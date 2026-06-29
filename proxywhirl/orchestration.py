"""
Request orchestration with optional multi-proxy failover.

Coordinates an outer proxy rotation loop with the inner ``RetryExecutor``
retry loop. Failover is opt-in via ``FailoverPolicy.enabled`` (default False)
for backward compatibility with single-proxy + inner-retry behavior.
"""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import httpx
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.exceptions import (
    ProxyAuthenticationError,
    ProxyConnectionError,
    ProxyPoolEmptyError,
)
from proxywhirl.models import Proxy, ProxyPool, SelectionContext
from proxywhirl.retry import NonRetryableError, RetryExecutor, RetryPolicy
from proxywhirl.strategies import RotationStrategy


class FailoverPolicy(BaseModel):
    """Configuration for multi-proxy failover behavior."""

    enabled: bool = Field(
        default=False,
        description="Enable outer proxy rotation when inner retries are exhausted",
    )
    max_proxy_attempts: int | None = Field(
        default=None,
        ge=1,
        description="Maximum distinct proxies to try; None tries all available proxies",
    )
    use_intelligent_selection: bool = Field(
        default=True,
        description="Use RetryExecutor.select_retry_proxy for rotation when True",
    )

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_env(cls, *, enabled: bool | None = None) -> FailoverPolicy:
        """Build policy from environment, honoring explicit override when provided."""
        if enabled is not None:
            return cls(enabled=enabled)
        env_val = os.environ.get("PROXYWHIRL_FAILOVER_ENABLED", "").lower()
        return cls(enabled=env_val in ("1", "true", "yes", "on"))


class ProxyRotationContext(BaseModel):
    """Mutable context for a single request's proxy rotation lifecycle."""

    request_id: str
    method: str
    url: str
    failed_proxy_ids: list[str] = Field(default_factory=list)
    failover_round: int = 0
    selection_context: SelectionContext | None = None
    current_proxy_id: str | None = None

    model_config = ConfigDict(extra="forbid")


ProxyRotationCallback = Callable[[ProxyRotationContext, Proxy, Proxy], None]
SelectProxyFn = Callable[[SelectionContext | None], Proxy]
ProxySelectedCallback = Callable[[Proxy], None]
GetProxiesFn = Callable[[], list[Proxy]]
SyncRequestFnFactory = Callable[[Proxy], Callable[[], httpx.Response]]
AsyncRequestFnFactory = Callable[[Proxy], Callable[[], Awaitable[httpx.Response]]]


@dataclass(frozen=True)
class OrchestrationResult:
    """Outcome of a single orchestrated request."""

    response: httpx.Response
    proxy: Proxy
    response_time_ms: float


class RequestOrchestration:
    """
    Orchestrates proxy selection, inner retries, and optional outer failover.

    When failover is disabled, behavior matches the legacy path: select one proxy
    and delegate to ``RetryExecutor`` for inner retries only.
    """

    def __init__(
        self,
        *,
        failover_policy: FailoverPolicy,
        retry_executor: RetryExecutor,
        strategy: RotationStrategy,
        pool: ProxyPool,
        circuit_breakers: dict[str, CircuitBreaker],
        select_proxy: SelectProxyFn,
        get_all_proxies: GetProxiesFn,
        proxy_rotation_callback: ProxyRotationCallback | None = None,
    ) -> None:
        self.failover_policy = failover_policy
        self.retry_executor = retry_executor
        self.strategy = strategy
        self.pool = pool
        self.circuit_breakers = circuit_breakers
        self.select_proxy = select_proxy
        self.get_all_proxies = get_all_proxies
        self.proxy_rotation_callback = proxy_rotation_callback

    def execute_sync(
        self,
        *,
        method: str,
        url: str,
        request_fn_factory: SyncRequestFnFactory,
        retry_policy: RetryPolicy | None = None,
        selection_context: SelectionContext | None = None,
        on_proxy_selected: ProxySelectedCallback | None = None,
    ) -> OrchestrationResult:
        """Execute a synchronous request with optional failover."""
        request_id = str(uuid.uuid4())
        executor = self._resolve_executor(retry_policy)
        rotation_ctx = ProxyRotationContext(
            request_id=request_id,
            method=method,
            url=url,
            selection_context=selection_context,
        )

        if not self.failover_policy.enabled:
            return self._execute_single_proxy_sync(
                rotation_ctx=rotation_ctx,
                executor=executor,
                method=method,
                url=url,
                request_fn_factory=request_fn_factory,
                failover_round=0,
                on_proxy_selected=on_proxy_selected,
            )

        return self._execute_failover_sync(
            rotation_ctx=rotation_ctx,
            executor=executor,
            method=method,
            url=url,
            request_fn_factory=request_fn_factory,
            on_proxy_selected=on_proxy_selected,
        )

    async def execute_async(
        self,
        *,
        method: str,
        url: str,
        request_fn_factory: AsyncRequestFnFactory,
        retry_policy: RetryPolicy | None = None,
        selection_context: SelectionContext | None = None,
        on_proxy_selected: ProxySelectedCallback | None = None,
    ) -> OrchestrationResult:
        """Execute an asynchronous request with optional failover."""
        request_id = str(uuid.uuid4())
        executor = self._resolve_executor(retry_policy)
        rotation_ctx = ProxyRotationContext(
            request_id=request_id,
            method=method,
            url=url,
            selection_context=selection_context,
        )

        if not self.failover_policy.enabled:
            return await self._execute_single_proxy_async(
                rotation_ctx=rotation_ctx,
                executor=executor,
                method=method,
                url=url,
                request_fn_factory=request_fn_factory,
                failover_round=0,
                on_proxy_selected=on_proxy_selected,
            )

        return await self._execute_failover_async(
            rotation_ctx=rotation_ctx,
            executor=executor,
            method=method,
            url=url,
            request_fn_factory=request_fn_factory,
            on_proxy_selected=on_proxy_selected,
        )

    def _execute_single_proxy_sync(
        self,
        *,
        rotation_ctx: ProxyRotationContext,
        executor: RetryExecutor,
        method: str,
        url: str,
        request_fn_factory: SyncRequestFnFactory,
        failover_round: int,
        on_proxy_selected: ProxySelectedCallback | None = None,
    ) -> OrchestrationResult:
        proxy = self._select_initial_proxy(rotation_ctx)
        if on_proxy_selected is not None:
            on_proxy_selected(proxy)
        rotation_ctx.current_proxy_id = str(proxy.id)
        start_time = time.time()
        response = executor.execute_with_retry(
            request_fn_factory(proxy),
            proxy,
            method,
            url,
            request_id=rotation_ctx.request_id,
            failover_round=failover_round,
        )
        return OrchestrationResult(
            response=response,
            proxy=proxy,
            response_time_ms=(time.time() - start_time) * 1000,
        )

    async def _execute_single_proxy_async(
        self,
        *,
        rotation_ctx: ProxyRotationContext,
        executor: RetryExecutor,
        method: str,
        url: str,
        request_fn_factory: AsyncRequestFnFactory,
        failover_round: int,
        on_proxy_selected: ProxySelectedCallback | None = None,
    ) -> OrchestrationResult:
        proxy = self._select_initial_proxy(rotation_ctx)
        if on_proxy_selected is not None:
            on_proxy_selected(proxy)
        rotation_ctx.current_proxy_id = str(proxy.id)
        start_time = time.time()
        response = await executor.execute_with_retry_async(
            request_fn_factory(proxy),
            proxy,
            method,
            url,
            request_id=rotation_ctx.request_id,
            failover_round=failover_round,
        )
        return OrchestrationResult(
            response=response,
            proxy=proxy,
            response_time_ms=(time.time() - start_time) * 1000,
        )

    def _execute_failover_sync(
        self,
        *,
        rotation_ctx: ProxyRotationContext,
        executor: RetryExecutor,
        method: str,
        url: str,
        request_fn_factory: SyncRequestFnFactory,
        on_proxy_selected: ProxySelectedCallback | None = None,
    ) -> OrchestrationResult:
        max_rounds = self._max_failover_rounds()
        last_error: Exception | None = None
        previous_proxy: Proxy | None = None

        for failover_round in range(max_rounds):
            rotation_ctx.failover_round = failover_round
            try:
                if failover_round == 0:
                    proxy = self._select_initial_proxy(rotation_ctx)
                else:
                    assert previous_proxy is not None
                    proxy = self._rotate_proxy(rotation_ctx, previous_proxy)
                    if proxy is None:
                        break
                    self._notify_rotation(rotation_ctx, previous_proxy, proxy)
            except ProxyPoolEmptyError as exc:
                last_error = exc
                break

            if on_proxy_selected is not None:
                on_proxy_selected(proxy)
            rotation_ctx.current_proxy_id = str(proxy.id)
            start_time = time.time()
            try:
                response = executor.execute_with_retry(
                    request_fn_factory(proxy),
                    proxy,
                    method,
                    url,
                    request_id=rotation_ctx.request_id,
                    failover_round=failover_round,
                )
                return OrchestrationResult(
                    response=response,
                    proxy=proxy,
                    response_time_ms=(time.time() - start_time) * 1000,
                )
            except (NonRetryableError, ProxyAuthenticationError):
                raise
            except ProxyConnectionError as exc:
                last_error = exc
                rotation_ctx.failed_proxy_ids.append(str(proxy.id))
                previous_proxy = proxy
                logger.warning(
                    "Proxy exhausted inner retries, attempting failover",
                    proxy_id=str(proxy.id),
                    failover_round=failover_round,
                    failed_proxy_count=len(rotation_ctx.failed_proxy_ids),
                )
                continue

        if last_error:
            raise ProxyConnectionError(
                f"Request failed after {len(rotation_ctx.failed_proxy_ids)} proxy failover round(s)"
            ) from last_error
        raise ProxyConnectionError("Request failed: no proxies available for failover")

    async def _execute_failover_async(
        self,
        *,
        rotation_ctx: ProxyRotationContext,
        executor: RetryExecutor,
        method: str,
        url: str,
        request_fn_factory: AsyncRequestFnFactory,
        on_proxy_selected: ProxySelectedCallback | None = None,
    ) -> OrchestrationResult:
        max_rounds = self._max_failover_rounds()
        last_error: Exception | None = None
        previous_proxy: Proxy | None = None

        for failover_round in range(max_rounds):
            rotation_ctx.failover_round = failover_round
            try:
                if failover_round == 0:
                    proxy = self._select_initial_proxy(rotation_ctx)
                else:
                    assert previous_proxy is not None
                    proxy = self._rotate_proxy(rotation_ctx, previous_proxy)
                    if proxy is None:
                        break
                    self._notify_rotation(rotation_ctx, previous_proxy, proxy)
            except ProxyPoolEmptyError as exc:
                last_error = exc
                break

            if on_proxy_selected is not None:
                on_proxy_selected(proxy)
            rotation_ctx.current_proxy_id = str(proxy.id)
            start_time = time.time()
            try:
                response = await executor.execute_with_retry_async(
                    request_fn_factory(proxy),
                    proxy,
                    method,
                    url,
                    request_id=rotation_ctx.request_id,
                    failover_round=failover_round,
                )
                return OrchestrationResult(
                    response=response,
                    proxy=proxy,
                    response_time_ms=(time.time() - start_time) * 1000,
                )
            except (NonRetryableError, ProxyAuthenticationError):
                raise
            except ProxyConnectionError as exc:
                last_error = exc
                rotation_ctx.failed_proxy_ids.append(str(proxy.id))
                previous_proxy = proxy
                logger.warning(
                    "Proxy exhausted inner retries, attempting failover",
                    proxy_id=str(proxy.id),
                    failover_round=failover_round,
                    failed_proxy_count=len(rotation_ctx.failed_proxy_ids),
                )
                continue

        if last_error:
            raise ProxyConnectionError(
                f"Request failed after {len(rotation_ctx.failed_proxy_ids)} proxy failover round(s)"
            ) from last_error
        raise ProxyConnectionError("Request failed: no proxies available for failover")

    def _select_initial_proxy(self, rotation_ctx: ProxyRotationContext) -> Proxy:
        """Select the first proxy respecting circuit breakers and selection context."""
        selection_context = self._build_selection_context(rotation_ctx)
        return self.select_proxy(selection_context)

    def _rotate_proxy(
        self,
        rotation_ctx: ProxyRotationContext,
        failed_proxy: Proxy,
    ) -> Proxy | None:
        """Select the next proxy after inner retries are exhausted."""
        available_proxies = self._get_available_proxies(rotation_ctx.failed_proxy_ids)
        if not available_proxies:
            return None

        if self.failover_policy.use_intelligent_selection:
            target_region = None
            if rotation_ctx.selection_context is not None:
                target_region = rotation_ctx.selection_context.target_region
            selected = self.retry_executor.select_retry_proxy(
                available_proxies,
                failed_proxy,
                target_region=target_region,
            )
            if selected is not None:
                return selected

        selection_context = self._build_selection_context(rotation_ctx)
        temp_pool = ProxyPool(name="failover-temp", proxies=available_proxies)
        return self.strategy.select(temp_pool, selection_context)

    def _get_available_proxies(self, failed_proxy_ids: list[str]) -> list[Proxy]:
        """Return non-expired proxies with closed/half-open circuits, excluding failures."""
        available: list[Proxy] = []
        for proxy in self.get_all_proxies():
            if proxy.is_expired:
                continue
            if str(proxy.id) in failed_proxy_ids:
                continue

            circuit_breaker = self.circuit_breakers.get(str(proxy.id))
            if circuit_breaker is None or circuit_breaker.should_attempt_request():
                available.append(proxy)
        return available

    def _build_selection_context(
        self,
        rotation_ctx: ProxyRotationContext,
    ) -> SelectionContext | None:
        """Merge rotation state into a strategy selection context."""
        if rotation_ctx.selection_context is None and not rotation_ctx.failed_proxy_ids:
            return None

        if rotation_ctx.selection_context is None:
            return SelectionContext(failed_proxy_ids=list(rotation_ctx.failed_proxy_ids))

        return rotation_ctx.selection_context.model_copy(
            update={"failed_proxy_ids": list(rotation_ctx.failed_proxy_ids)}
        )

    def _max_failover_rounds(self) -> int:
        """Compute how many distinct proxies to attempt in the outer loop."""
        if self.failover_policy.max_proxy_attempts is not None:
            return self.failover_policy.max_proxy_attempts
        return max(len(self.get_all_proxies()), 1)

    def _notify_rotation(
        self,
        rotation_ctx: ProxyRotationContext,
        previous_proxy: Proxy,
        new_proxy: Proxy,
    ) -> None:
        if self.proxy_rotation_callback is None:
            return
        self.proxy_rotation_callback(rotation_ctx, previous_proxy, new_proxy)

    def _resolve_executor(self, retry_policy: RetryPolicy | None) -> RetryExecutor:
        if retry_policy is None:
            return self.retry_executor
        return RetryExecutor(
            retry_policy,
            self.circuit_breakers,
            self.retry_executor.retry_metrics,
        )
