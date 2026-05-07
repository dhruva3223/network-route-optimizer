"""DRF exception handler for consistent API error responses."""


def api_exception_handler(exc, context):
    try:
        from rest_framework.views import exception_handler
        from rest_framework.response import Response
    except Exception:
        return None

    response = exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data.get("detail", response.data)
    response.data = {"error": detail}
    return Response(response.data, status=response.status_code)
