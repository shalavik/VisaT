import uuid
from flask import jsonify, g
from typing import Optional


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


def get_request_id() -> str:
    """Get the current request ID from Flask global context if available."""
    return getattr(g, 'request_id', None) or generate_correlation_id()


def error_response(error_code: str, message: str, status: int = 400, details: Optional[dict] = None):
    """Return a standardized JSON error with correlation ID."""
    response = {
        "status": "error",
        "error_code": error_code,
        "message": message,
        "correlation_id": get_request_id()
    }
    if details:
        response["details"] = details
    return jsonify(response), status
