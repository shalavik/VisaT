import os
from flask import Blueprint, request, jsonify, current_app
from ...utils.errors import error_response

bp = Blueprint('whatsapp', __name__)


@bp.route('/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    try:
        services = current_app.extensions['services']
        contact_handler = services['contact_handler']

        if request.method == 'GET':
            verify_token = request.args.get('hub.verify_token')
            if verify_token == os.getenv('WHATSAPP_VERIFY_TOKEN'):
                return request.args.get('hub.challenge')
            return 'Verification failed', 403

        data = request.get_json()
        result = contact_handler.handle_whatsapp_message(data)
        return jsonify({'status': 'received', 'result': result})
    except Exception as e:
        return error_response('WHATSAPP_WEBHOOK_ERROR', f'Processing failed: {e}', 500)


@bp.route('/api/whatsapp/send', methods=['POST'])
def send_whatsapp_message():
    try:
        services = current_app.extensions['services']
        whatsapp_client = services['whatsapp_client']

        data = request.get_json() or {}
        if not all(k in data for k in ['to', 'template_name']):
            return error_response('VALIDATION_ERROR', 'Missing required fields: to, template_name', 400)

        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        if not access_token:
            return error_response('CONFIG_ERROR', 'WhatsApp access token not configured', 500)

        # This app currently supports personal send paths elsewhere; keep stub for business template
        result = whatsapp_client.send_message(data['to'], f"TEMPLATE:{data['template_name']}")
        return jsonify({'status': 'sent', 'result': result})
    except Exception as e:
        return error_response('WHATSAPP_SEND_ERROR', f'Sending failed: {e}', 500)


@bp.route('/api/whatsapp-status', methods=['GET'])
def whatsapp_status():
    try:
        whatsapp_client = current_app.extensions['services']['whatsapp_client']
        return jsonify(whatsapp_client.get_status())
    except Exception as e:
        return error_response('WHATSAPP_STATUS_ERROR', f'Failed to get WhatsApp status: {e}', 500)


@bp.route('/api/whatsapp-restart', methods=['POST'])
@bp.route('/api/whatsapp-start', methods=['POST'])
@bp.route('/api/whatsapp-stop', methods=['POST'])
def whatsapp_session_control():
    try:
        whatsapp_client = current_app.extensions['services']['whatsapp_client']
        path = request.path
        if whatsapp_client.get_mode() != 'personal':
            return error_response('INVALID_MODE', 'Operation only available in personal mode', 400)
        if path.endswith('restart'):
            success = whatsapp_client.restart_personal_session()
        elif path.endswith('start'):
            success = whatsapp_client.start_personal_session()
        else:
            success = whatsapp_client.stop_personal_session()
        return jsonify({'status': 'success' if success else 'failed'})
    except Exception as e:
        return error_response('WHATSAPP_SESSION_ERROR', f'Failed to control session: {e}', 500)


@bp.route('/api/whatsapp-force-monitoring', methods=['POST'])
def whatsapp_force_monitoring():
    try:
        whatsapp_client = current_app.extensions['services']['whatsapp_client']
        if whatsapp_client.get_mode() != 'personal':
            return error_response('INVALID_MODE', 'Only available in personal mode', 400)
        success = whatsapp_client.start_monitoring(force=True)
        return jsonify({'status': 'success' if success else 'failed'})
    except Exception as e:
        return error_response('WHATSAPP_MONITORING_ERROR', f'Failed to force start monitoring: {e}', 500)
