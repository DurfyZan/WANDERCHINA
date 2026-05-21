import structlog
from datetime import datetime
import logging

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


def get_logger(name: str):
    return structlog.get_logger(name)


class LoggerMiddleware:
    def __init__(self):
        self.logger = get_logger("middleware")
    
    async def log_request(self, request, response_time: float):
        self.logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response_time,
            client_ip=request.client.host if request.client else None,
        )
    
    async def log_error(self, request, error: Exception):
        self.logger.error(
            "request_error",
            method=request.method,
            path=request.url.path,
            error=str(error),
            error_type=type(error).__name__,
            client_ip=request.client.host if request.client else None,
        )


logger_middleware = LoggerMiddleware()
