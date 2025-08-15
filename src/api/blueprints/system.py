from flask import Blueprint, jsonify, current_app

bp = Blueprint('system', __name__)


@bp.route('/')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'VisaT - Visa Consulting Automation',
        'version': '1.0.0'
    })


@bp.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        sheets_client = current_app.extensions['services']['sheets_client']
        # Provide a basic statistics computation using SheetsClientFixed
        stats = {}
        try:
            # Fallback approach: compute stats from sheet data
            data = sheets_client.get_sheet_data("Form Responses 1", "A:L")
            data_rows = data[1:] if len(data) > 1 else []
            total = len(data_rows)
            qualified = 0
            booked = 0
            for row in data_rows:
                if len(row) > 9 and str(row[9]).lower() == 'true':
                    qualified += 1
                if len(row) > 10 and 'booked' in str(row[10]).lower():
                    booked += 1
            stats = {
                'total_leads': total,
                'qualified_leads': qualified,
                'appointments_booked': booked,
                'conversion_rate': round((qualified / total * 100) if total else 0.0, 2)
            }
        except Exception:
            stats = {
                'total_leads': 0,
                'qualified_leads': 0,
                'appointments_booked': 0,
                'conversion_rate': 0.0
            }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': 'Stats unavailable', 'message': str(e)}), 200


@bp.route('/api/system/metrics', methods=['GET'])
def get_metrics():
    return jsonify(current_app.extensions['metrics'])
