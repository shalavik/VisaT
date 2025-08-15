from flask import Blueprint, jsonify, current_app, request
from ...utils.errors import error_response

bp = Blueprint('sheets', __name__)


def _register_sheets_job(interval: int = 30):
    scheduler = current_app.extensions['scheduler']
    services = current_app.extensions['services']
    monitor = services['sheets_monitor']

    def tick():
        try:
            # Use internal method to preserve behavior
            monitor._check_for_new_submissions()
        except Exception:
            pass

    scheduler.remove_job('sheets_monitor')
    scheduler.register_interval_job('sheets_monitor', tick, seconds=interval)


@bp.route('/api/sheets-monitor/start', methods=['POST'])
def start_sheets_monitoring():
    try:
        data = request.get_json() or {}
        interval = int(data.get('interval', 30))
        _register_sheets_job(interval)
        return jsonify({'status': 'success', 'message': 'Google Sheets monitoring scheduled'})
    except Exception as e:
        return error_response('SHEETS_MONITOR_START_ERROR', f'Failed to start sheets monitoring: {e}', 500)


@bp.route('/api/sheets-monitor/stop', methods=['POST'])
def stop_sheets_monitoring():
    try:
        scheduler = current_app.extensions['scheduler']
        scheduler.remove_job('sheets_monitor')
        return jsonify({'status': 'success', 'message': 'Google Sheets monitoring stopped'})
    except Exception as e:
        return error_response('SHEETS_MONITOR_STOP_ERROR', f'Failed to stop sheets monitoring: {e}', 500)


@bp.route('/api/sheets-monitor/status', methods=['GET'])
def sheets_monitoring_status():
    try:
        scheduler = current_app.extensions['scheduler']
        services = current_app.extensions['services']
        monitor = services['sheets_monitor']
        status = monitor.get_monitoring_status()
        sched = scheduler.get_status()
        return jsonify({'monitor': status, 'scheduler': sched})
    except Exception as e:
        return error_response('SHEETS_MONITOR_STATUS_ERROR', f'Failed to get monitoring status: {e}', 500)


@bp.route('/api/sheets-monitor/process', methods=['POST'])
def process_new_sheets_rows():
    try:
        services = current_app.extensions['services']
        monitor = services['sheets_monitor']
        ok = monitor.manual_process_new_rows()
        return jsonify({'status': 'success' if ok else 'failed'})
    except Exception as e:
        return error_response('SHEETS_MONITOR_PROCESS_ERROR', f'Failed to process rows: {e}', 500)


@bp.route('/api/sheets-monitor/process-row', methods=['POST'])
def process_specific_row():
    try:
        services = current_app.extensions['services']
        monitor = services['sheets_monitor']
        data = request.get_json() or {}
        row_number = data.get('row_number')
        if not row_number:
            return error_response('VALIDATION_ERROR', 'Row number required', 400)
        sheet_data = monitor._get_sheet_data()
        if row_number > len(sheet_data) or row_number < 1:
            return error_response('VALIDATION_ERROR', f'Invalid row number. Sheet has {len(sheet_data)} rows', 400)
        row_data = sheet_data[row_number - 1]
        result = monitor._process_form_submission(row_data, row_number)
        return jsonify({'status': 'processed', 'row_number': row_number, 'row_data': row_data, 'result': result})
    except Exception as e:
        return error_response('SHEETS_MONITOR_PROCESS_ROW_ERROR', f'Row processing failed: {e}', 500)


@bp.route('/api/sheets-monitor/reset', methods=['POST'])
def reset_sheets_monitoring():
    try:
        services = current_app.extensions['services']
        monitor = services['sheets_monitor']
        data = request.get_json() or {}
        reprocess_last_n = data.get('reprocess_last_n', 5)
        sheet_data = monitor._get_sheet_data()
        current_rows = len(sheet_data)
        if current_rows == 0:
            return error_response('VALIDATION_ERROR', 'No data in sheet', 400)
        new_processed_row = max(0, current_rows - int(reprocess_last_n))
        monitor.last_processed_row = new_processed_row
        monitor._check_for_new_submissions()
        return jsonify({
            'status': 'reset',
            'previous_processed_row': current_rows,
            'new_processed_row': new_processed_row,
            'will_reprocess_rows': list(range(new_processed_row + 1, current_rows + 1))
        })
    except Exception as e:
        return error_response('SHEETS_MONITOR_RESET_ERROR', f'Reset failed: {e}', 500)
