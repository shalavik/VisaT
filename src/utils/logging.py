import logging
from flask import g, request


class RequestContextFilter(logging.Filter):
    """Inject request context information into log records if available."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Set safe defaults
        record.request_id = '-'
        record.path = '-'
        record.method = '-'
        
        # Try to enrich with Flask context if available
        try:
            record.request_id = getattr(g, 'request_id', '-')
            try:
                record.path = request.path
                record.method = request.method
            except Exception:
                # Request object may not be available
                pass
        except Exception:
            # No application/request context
            pass
        
        return True


def setup_request_id(app):
    """Register before/after request handlers to manage request IDs."""
    @app.before_request
    def _attach_request_id():
        if not hasattr(g, 'request_id'):
            # Simple request ID, could also accept X-Request-ID header
            g.request_id = request.headers.get('X-Request-ID') or _generate_simple_request_id()

    @app.after_request
    def _propagate_request_id(response):
        try:
            response.headers['X-Request-ID'] = getattr(g, 'request_id', '-')
        except Exception:
            pass
        return response


def _generate_simple_request_id() -> str:
    import uuid
    return str(uuid.uuid4())
