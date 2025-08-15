import os
from flask import Blueprint, request, jsonify, current_app
from ...utils.errors import error_response

bp = Blueprint('calendly', __name__)


@bp.route('/api/calendly/webhook', methods=['POST'])
def calendly_webhook():
    try:
        from ...integrations.calendly_webhook import CalendlyWebhookProcessor
        raw_body = request.get_data()
        signature = request.headers.get('X-Calendly-Signature', '')
        payload = request.get_json()
        if not payload:
            return error_response('VALIDATION_ERROR', 'No JSON payload received', 400)
        result = CalendlyWebhookProcessor().process_webhook(payload, signature, raw_body)
        status_code = 200 if result.get('status') in ('success', 'ignored') else 400
        return jsonify(result), status_code
    except Exception as e:
        return error_response('CALENDLY_WEBHOOK_ERROR', f'Webhook processing failed: {e}', 500)


@bp.route('/api/calendly/status', methods=['GET'])
def calendly_status():
    try:
        from ...integrations.calendly_webhook import CalendlyWebhookProcessor
        result = CalendlyWebhookProcessor().test_webhook_processing()
        return jsonify(result), 200
    except Exception as e:
        return error_response('CALENDLY_STATUS_ERROR', f'Status check failed: {e}', 500)


@bp.route('/api/calendly/test', methods=['POST'])
def test_calendly():
    try:
        from ...integrations.calendly_webhook import CalendlyWebhookProcessor
        test_data = request.get_json() if request.is_json else None
        result = CalendlyWebhookProcessor().test_webhook_processing(test_data)
        return jsonify(result), 200
    except Exception as e:
        return error_response('CALENDLY_TEST_ERROR', f'Test failed: {e}', 500)


@bp.route('/api/calendly/bookings', methods=['GET'])
def get_calendly_bookings():
    try:
        from ...integrations.sheets_client_fixed import SheetsClientFixed
        sheet_id = os.getenv('CALENDLY_SHEET_ID')
        if not sheet_id:
            return error_response('CONFIG_ERROR', 'Calendly sheet ID not configured', 400)
        limit = request.args.get('limit', 50, type=int)
        bookings = SheetsClientFixed().get_booking_sheet_data(sheet_id, limit)
        return jsonify({'status': 'success', 'bookings': bookings, 'count': len(bookings)}), 200
    except Exception as e:
        return error_response('CALENDLY_BOOKINGS_ERROR', f'Failed to retrieve bookings: {e}', 500)


@bp.route('/api/calendly/setup-headers', methods=['POST'])
def setup_calendly_headers():
    try:
        from ...integrations.sheets_client_fixed import SheetsClientFixed
        sheet_id = os.getenv('CALENDLY_SHEET_ID')
        if not sheet_id:
            return error_response('CONFIG_ERROR', 'Calendly sheet ID not configured', 400)
        ok = SheetsClientFixed().create_booking_sheet_headers(sheet_id)
        if ok:
            return jsonify({'status': 'success', 'message': 'Booking sheet headers created successfully'}), 200
        return error_response('CALENDLY_HEADERS_ERROR', 'Failed to create booking sheet headers', 500)
    except Exception as e:
        return error_response('CALENDLY_HEADERS_ERROR', f'Failed to setup headers: {e}', 500)


@bp.route('/api/calendly/poll/start', methods=['POST'])
@bp.route('/api/calendly/poll/stop', methods=['POST'])
@bp.route('/api/calendly/poll/status', methods=['GET', 'POST'])
@bp.route('/api/calendly/poll', methods=['POST'])
def calendly_poll_control():
    try:
        poller = current_app.extensions['services']['calendly_poller']
        path = request.path
        if path.endswith('/start'):
            poller.start_polling()
            return jsonify({'status': 'success', 'message': 'Calendly polling started (every 5 minutes)'})
        if path.endswith('/stop'):
            poller.stop_polling()
            return jsonify({'status': 'success', 'message': 'Calendly polling stopped'})
        if path.endswith('/status'):
            status = poller.get_status()
            return jsonify({'status': 'success', 'data': status})
        # manual poll
        result = poller.manual_poll()
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return error_response('CALENDLY_POLL_ERROR', f'Calendly poll control failed: {e}', 500)
