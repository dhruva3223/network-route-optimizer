"""DRF exception handler for consistent API error responses."""
from rest_framework.views import exception_handler
from rest_framework.response import Response


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(response.data, dict):
        detail = response.data.get("detail", response.data)
    else:
        detail = response.data
    response.data = {"error": detail}
    return Response(response.data, status=response.status_code)
