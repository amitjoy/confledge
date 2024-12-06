from http import HTTPStatus

import time
from fastapi import HTTPException
from functools import wraps
from typing import Any, Type, Callable, Awaitable


class RateLimitException(Exception):
    """
    Exception raised when the rate limit is exceeded.
    """

    def __init__(self, message: str = "API Rate Limit Exceeded"):
        super().__init__(message)


class RateLimiter:
    """
    A class to handle rate limiting for API requests.
    """

    def __init__(
            self,
            limit: int,
            seconds: int,
            exception: Type[Exception] = RateLimitException,
            exception_status: int = HTTPStatus.TOO_MANY_REQUESTS,
            exception_message: Any = "API Rate Limit Exceeded"
    ):
        """
        Initializes the RateLimiter with the specified parameters.

        :param limit: The maximum number of requests allowed.
        :param seconds: The time window in seconds for the rate limit.
        :param exception: The exception to raise when the rate limit is exceeded.
        :param exception_status: The HTTP status code to use for the exception.
        :param exception_message: The message to include in the exception.
        """
        self.limit = limit
        self.seconds = seconds
        self.local_session = {}
        self.exception_cls = exception
        self.exception_status = exception_status
        self.exception_message = exception_message

    def __call__(self, func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        """
        Decorator to apply rate limiting to a function.

        :param func: The function to decorate.
        :return: The decorated function.
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request", None)
            key = self._get_key(request)
            await self._check_rate_limit(key)
            return await func(*args, **kwargs)

        return wrapper

    @staticmethod
    def _get_key(request) -> str:
        """
        Generates a unique key for the request based on the client's IP and request path.

        :param request: The request object.
        :return: A unique key as a string.
        """
        if request:
            return f"default:{request.client.host}:{request.url.path}"
        return ""

    def _raise_exception(self):
        """
        Raises the configured exception when the rate limit is exceeded.
        """
        if issubclass(self.exception_cls, HTTPException):
            raise self.exception_cls(
                status_code=self.exception_status, detail=self.exception_message
            )
        else:
            raise self.exception_cls(self.exception_message)

    async def _check_rate_limit(self, key: str):
        """
        Checks if the request exceeds the rate limit and updates the session data.

        :param key: The unique key for the request.
        """
        current_time = time.time()
        last_request_time, request_count = self.local_session.get(key, (0, 0))

        if (current_time - last_request_time) < self.seconds and request_count >= self.limit:
            self._raise_exception()
        else:
            new_count = 1 if (current_time - last_request_time) >= self.seconds else request_count + 1
            self.local_session[key] = (current_time, new_count)
