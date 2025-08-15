import logging
import os
from flask import Flask
from ..utils.logging import RequestContextFilter, setup_request_id
from ..integrations.gmail_client import GmailClient
from ..integrations.whatsapp_client import WhatsAppClient
from ..integrations.sheets_client_fixed import SheetsClientFixed
from ..integrations.calendly_client import CalendlyClient
from ..integrations.sheets_monitor import SheetsMonitor
from ..integrations.calendly_poller import CalendlyPoller
from ..handlers.contact_handler import ContactHandler
from ..handlers.form_processor import FormProcessor
from ..engines.qualification_engine import QualificationEngine
from ..jobs.scheduler import SchedulerManager


def create_app() -> Flask:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

    # Logging + request IDs
    setup_request_id(app)
    for handler in logging.getLogger().handlers:
        handler.addFilter(RequestContextFilter())

    # Metrics (very simple in-memory counters)
    app.extensions['metrics'] = {
        'requests_total': 0,
        'requests_error': 0,
    }

    @app.before_request
    def _inc_requests():
        app.extensions['metrics']['requests_total'] += 1

    @app.errorhandler(Exception)
    def _on_error(e):
        app.extensions['metrics']['requests_error'] += 1
        # Let blueprint handlers format; default to JSON minimal to avoid import cycle
        from flask import jsonify
        return jsonify({'status': 'error', 'message': str(e)}), 500

    # Services (DI container)
    services = {
        'gmail_client': GmailClient(),
        'whatsapp_client': WhatsAppClient(),
        'sheets_client': SheetsClientFixed(),
        'calendly_client': CalendlyClient() if os.getenv('CALENDLY_PAT') or os.getenv('CALENDLY_ACCESS_TOKEN') else None,
        'sheets_monitor': SheetsMonitor(),
        'calendly_poller': CalendlyPoller(),
        'contact_handler': ContactHandler(),
        'form_processor': FormProcessor(),
        'qualification_engine': QualificationEngine(),
    }
    app.extensions['services'] = services

    # Scheduler
    scheduler = SchedulerManager.instance()
    scheduler.start()
    app.extensions['scheduler'] = scheduler

    # Auto-start Calendly poller if configured
    try:
        if os.getenv('CALENDLY_POLL_ON_START', 'true').lower() == 'true':
            services['calendly_poller'].start_polling()
    except Exception:
        pass

    # Auto-register Sheets monitoring job at startup with baseline
    try:
        monitor = services['sheets_monitor']
        interval = int(os.getenv('SHEETS_MONITOR_INTERVAL', '30'))

        # Establish baseline to avoid reprocessing historical rows
        try:
            current_data = monitor._get_sheet_data()
            if current_data:
                monitor.last_processed_row = len(current_data)
        except Exception:
            pass

        def _sheets_tick():
            try:
                monitor._check_for_new_submissions()
            except Exception:
                pass

        scheduler.remove_job('sheets_monitor')
        scheduler.register_interval_job('sheets_monitor', _sheets_tick, seconds=interval)
        # No immediate tick here to prevent processing historical rows
    except Exception:
        # Do not block app startup if scheduling fails
        pass

    # Auto-start WhatsApp personal session and monitoring if configured
    try:
        if services['whatsapp_client'].get_mode() == 'personal' and os.getenv('WHATSAPP_AUTOSTART', 'true').lower() == 'true':
            ok = services['whatsapp_client'].start_personal_session()
            if ok:
                services['whatsapp_client'].start_monitoring(force=True)
    except Exception:
        pass

    # Register blueprints
    from .blueprints.system import bp as system_bp
    from .blueprints.whatsapp import bp as whatsapp_bp
    from .blueprints.sheets import bp as sheets_bp
    from .blueprints.calendly import bp as calendly_bp

    app.register_blueprint(system_bp)
    app.register_blueprint(whatsapp_bp)
    app.register_blueprint(sheets_bp)
    app.register_blueprint(calendly_bp)

    return app
