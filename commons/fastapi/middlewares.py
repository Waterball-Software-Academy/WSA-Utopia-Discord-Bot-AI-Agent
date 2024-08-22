__author__ = "Lauren (lauren@waterballsa.tw)"

import binascii
import os
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from commons.utils.logging import get_logger


def generate_trace_id():
    random_bytes = os.urandom(16)
    trace_id = binascii.hexlify(random_bytes).decode('ascii')
    return trace_id


class TraceIdToLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("TraceIdToLoggerMiddleware")

    async def dispatch(self, request, call_next):
        trace_id = generate_trace_id()
        with self.logger.contextualize(trace_id=trace_id):
            # Add the trace id to the request headers
            response = await call_next(request)
            return response
