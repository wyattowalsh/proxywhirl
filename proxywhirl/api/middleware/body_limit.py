"""ASGI request-body byte limit enforced while the body is received."""

from __future__ import annotations

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from proxywhirl.api.models import APIResponse, ErrorCode

# Allow a 1 MiB proxied body plus a bounded amount of JSON envelope overhead.
DEFAULT_MAX_API_REQUEST_BYTES = 1_048_576 + 65_536
_BODY_LIMIT_EXCEEDED_STATE_KEY = "proxywhirl_request_body_too_large"


class _RequestBodyTooLargeError(Exception):
    """Internal signal raised as soon as a streamed request exceeds its cap."""


class RequestBodyLimitMiddleware:
    """Reject request bodies that exceed a configured byte limit while streaming."""

    def __init__(
        self,
        app: ASGIApp,
        max_body_bytes: int = DEFAULT_MAX_API_REQUEST_BYTES,
    ) -> None:
        if max_body_bytes <= 0:
            raise ValueError("max_body_bytes must be positive")
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def _reject(self, scope: Scope, receive: Receive, send: Send) -> None:
        response: APIResponse[None] = APIResponse.error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="Request body is too large",
            details={"max_bytes": self.max_body_bytes},
        )
        await JSONResponse(
            status_code=413,
            content=response.model_dump(mode="json"),
        )(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        for name, value in scope.get("headers", []):
            if name.lower() != b"content-length":
                continue
            try:
                content_length = int(value.decode("ascii"))
            except (UnicodeDecodeError, ValueError):
                break
            if content_length > self.max_body_bytes:
                await self._reject(scope, receive, send)
                return
            break

        received_bytes = 0
        limit_exceeded = False
        response_started = False
        replacement_sent = False

        async def limited_receive() -> Message:
            nonlocal limit_exceeded, received_bytes
            if limit_exceeded:
                raise _RequestBodyTooLargeError
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self.max_body_bytes:
                    limit_exceeded = True
                    scope.setdefault("state", {})[_BODY_LIMIT_EXCEEDED_STATE_KEY] = True
                    raise _RequestBodyTooLargeError
            return message

        async def tracked_send(message: Message) -> None:
            nonlocal replacement_sent, response_started
            if limit_exceeded and not response_started:
                if not replacement_sent:
                    replacement_sent = True
                    await self._reject(scope, receive, send)
                return
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)
        except Exception:
            if not limit_exceeded:
                raise
            if response_started:
                raise
            if not replacement_sent:
                replacement_sent = True
                await self._reject(scope, receive, send)

        if limit_exceeded and not response_started and not replacement_sent:
            await self._reject(scope, receive, send)
