import logging
import time

logger = logging.getLogger('request')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        elapsed = int((time.time() - start) * 1000)
        logger.info(
            '%s %s -> %s (%dms)',
            request.method, request.path, response.status_code, elapsed,
        )
        return response
