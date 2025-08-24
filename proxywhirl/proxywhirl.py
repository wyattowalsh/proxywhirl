"""ProxyWhirl unified interface.

A high-level orchestrator for discovering, validating, rotating, and consuming
public/free proxies. Provides both synchronous wrappers and a first-class
asynchronous API. Designed around pluggable loaders, strict Pydantic models,
and a multi-backend cache.

Notes
-----
- Python: 3.13+ required.
- Validation leverages async concurrency and a circuit-breaker in the validator.
- Cache backends include in-memory (default), JSON, and SQLite.
- This module is intentionally lightweight and integrates with specialized
  components: loaders, rotator, validator, and cache.

Examples
--------
Basic usage (sync):
    >>> from proxywhirl.proxywhirl import ProxyWhirl
    >>> pw = ProxyWhirl(cache_type="memory", rotation_strategy="round_robin")
    >>> count = pw.fetch_proxies(validate=True)
    >>> proxy = pw.get_proxy()
    >>> print(count, proxy)

Async usage:
    >>> import asyncio
    >>> async def main():
    ...     pw = await ProxyWhirl.create(rotation_strategy="round_robin")
    ...     async with pw.session():
    ...         await pw.fetch_proxies_async(validate=True)
    ...         proxy = await pw.get_proxy_async()
    ...         print(proxy)
    >>> asyncio.run(main())

See Also
--------
proxywhirl.cache.ProxyCache
proxywhirl.rotator.ProxyRotator
proxywhirl.validator.ProxyValidator
proxywhirl.models.Proxy
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Coroutine,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    TypeVar,
    Union,
    cast,
)

from loguru import logger
from pandas import DataFrame

from proxywhirl.cache import ProxyCache
from proxywhirl.loaders.base import BaseLoader
from proxywhirl.loaders.clarketm_raw import ClarketmHttpLoader

# from proxywhirl.loaders.fresh_proxy_list import FreshProxyListLoader  # DISABLED: Domain dead
from proxywhirl.loaders.jetkai_proxy_list import JetkaiProxyListLoader
from proxywhirl.loaders.monosans import MonosansLoader

# from proxywhirl.loaders.openproxyspace import OpenProxySpaceLoader  # DISABLED: 521 errors
from proxywhirl.loaders.proxifly import ProxiflyLoader

# from proxywhirl.loaders.proxynova import ProxyNovaLoader  # DISABLED: Module missing
from proxywhirl.loaders.proxyscrape import ProxyScrapeLoader
from proxywhirl.loaders.the_speedx import (
    TheSpeedXHttpLoader,
    TheSpeedXSocksLoader,
)
from proxywhirl.loaders.user_provided import UserProvidedLoader
from proxywhirl.loaders.vakhov_fresh import VakhovFreshProxyLoader
from proxywhirl.models import (
    CacheType,
    Proxy,
    ProxyStatus,
    RotationStrategy,
    TargetDefinition,
    ValidationErrorType,
)
from proxywhirl.rotator import ProxyRotator
from proxywhirl.validator import ProxyValidator

if TYPE_CHECKING:
    from proxywhirl.export_models import ExportConfig

T = TypeVar("T")


class ProxyWhirl:
    """
    Unified ProxyWhirl interface with smart sync/async handling.

    Provides a single entry point to fetch, validate, rotate, and consume
    proxies from multiple sources while keeping a clean separation of concerns.

    Parameters
    ----------
    cache_type : CacheType or str, default="memory"
        Cache backend. Accepts enum or case-insensitive string alias.
        Options: "memory", "json", "sqlite".
    cache_path : str or pathlib.Path, optional
        Path required when using JSON/SQLite caches. Ignored by memory cache.
    rotation_strategy : RotationStrategy or str, default="round_robin"
        Strategy used by the rotator. Accepts enum or case-insensitive alias.
        Options include "round_robin", "least_latency", etc.
    health_check_interval : int, default=30
        Reserved for periodic health checks by higher-level schedulers.
    auto_validate : bool, default=True
        When True, fetched proxies are validated before caching.
    validator_timeout : float, default=10.0
        Per-request timeout used by the validator in seconds.
    validator_test_url : str, default="https://httpbin.org/ip"
        Test URL used by the validator. Wrapped internally as a single-item list.
    enable_metrics : bool, default=True
        Reserved flag to toggle metrics collection. Does not alter behavior here.
    max_concurrent_validations : int, default=10
        Upper bound for concurrent validation tasks.

    Attributes
    ----------
    cache : ProxyCache
        Backing cache for storing proxies.
    rotator : ProxyRotator
        Rotation strategy implementation.
    validator : ProxyValidator
        Async validator with concurrency and circuit-breaker.
    loaders : list[BaseLoader]
        Active loader instances used to fetch proxies.
    cache_type : CacheType
        Effective cache type after normalization.
    rotation_strategy : RotationStrategy
        Effective rotation strategy after normalization.

    Notes
    -----
    - String enum inputs are normalized via the corresponding enum constructors.
    - This class offers sync wrappers that are safe for non-async contexts only.
    """

    # Sensible default cap for validation during fetch to avoid huge runs by default
    DEFAULT_MAX_VALIDATE_ON_FETCH: int = 500

    def __init__(
        self,
        cache_type: Union[CacheType, str] = CacheType.MEMORY,
        cache_path: Optional[Union[str, Path]] = None,
        rotation_strategy: Union[RotationStrategy, str] = RotationStrategy.ROUND_ROBIN,
        health_check_interval: int = 30,
        auto_validate: bool = True,
        # Additional configuration options
        validator_timeout: float = 10.0,
        validator_test_url: str = "https://httpbin.org/ip",
        # Target-based validation support
        validation_targets: Optional[Dict[str, TargetDefinition]] = None,
        enable_metrics: bool = True,
        max_concurrent_validations: int = 10,
        # Optional cap on total number of proxies to collect during fetch across all loaders.
        # None disables the cap. Applied before validation to reduce fetch/parse cost.
        max_fetch_proxies: Optional[int] = None,
        # Maximum proxies to validate when validation is performed during fetch.
        # None disables the cap. Overrideable via CLI.
        max_validate_on_fetch: Optional[int] = DEFAULT_MAX_VALIDATE_ON_FETCH,
    ):
        """
        Initialize a ProxyWhirl instance.

        See class docstring for detailed parameter descriptions.
        """
        # Normalize any string-based enum inputs to their enum counterparts.
        if not isinstance(cache_type, CacheType):
            cache_type = CacheType(str(cache_type).lower())
        if not isinstance(rotation_strategy, RotationStrategy):
            rotation_strategy = RotationStrategy(str(rotation_strategy).lower())

        self.cache_type = cache_type
        self.rotation_strategy = rotation_strategy
        self.health_check_interval = health_check_interval
        self.auto_validate = auto_validate
        self.enable_metrics = enable_metrics
        self.max_concurrent_validations = max_concurrent_validations
        # Normalize caps (treat non-positive as no cap)
        if max_fetch_proxies is not None and max_fetch_proxies <= 0:
            max_fetch_proxies = None
        if max_validate_on_fetch is not None and max_validate_on_fetch <= 0:
            max_validate_on_fetch = None
        self.max_fetch_proxies: Optional[int] = max_fetch_proxies
        self.max_validate_on_fetch: Optional[int] = max_validate_on_fetch

        # Initialize cache (path is only meaningful for JSON/SQLite backends).
        cache_path_obj = Path(cache_path) if cache_path else None
        self.cache = ProxyCache(cache_type, cache_path_obj)

        # Initialize rotator and validator with custom settings.
        self.rotator = ProxyRotator(rotation_strategy)
        # Validator expects a list of test URLs; adapt single URL into a list.
        # Also pass validation targets if provided.
        self.validation_targets = validation_targets
        self.validator = ProxyValidator(
            timeout=validator_timeout,
            test_urls=[validator_test_url],
            targets=validation_targets,
            max_concurrent=max_concurrent_validations,
        )

        # Initialize default loaders. UserProvidedLoader is added on-demand.
        self._default_loaders: List[type] = [
            # FreshProxyListLoader,  # DISABLED: Domain is dead (404)
            TheSpeedXHttpLoader,
            TheSpeedXSocksLoader,
            ClarketmHttpLoader,
            MonosansLoader,
            ProxyScrapeLoader,
            # ProxyNovaLoader,  # DISABLED: Module missing
            # OpenProxySpaceLoader,  # DISABLED: Returns 521 errors
            # New working loaders based on research
            ProxiflyLoader,
            VakhovFreshProxyLoader,
            JetkaiProxyListLoader,
        ]
        self.loaders: List[BaseLoader] = self._create_loaders()

        logger.info(
            f"ProxyWhirl initialized with {cache_type} cache and {rotation_strategy} rotation"
        )

    def _create_loaders(self, enabled_loaders: Optional[List[str]] = None) -> List[BaseLoader]:
        """
        Instantiate default loader instances.

        Parameters
        ----------
        enabled_loaders : list[str], optional
            If provided, only loaders whose class names (case-insensitive)
            are in this list will be instantiated.

        Returns
        -------
        list[BaseLoader]
            The list of created loader instances.

        Notes
        -----
        - UserProvidedLoader is intentionally skipped here because it requires
          runtime-supplied proxies.
        - Failures are logged and skipped without failing the whole process.
        """
        loaders: List[BaseLoader] = []

        enabled_set: set[str] = (
            {name.lower() for name in enabled_loaders} if enabled_loaders else set()
        )

        for loader_class in self._default_loaders:
            try:
                # Skip UserProvidedLoader as it requires proxies parameter.
                if loader_class.__name__ == "UserProvidedLoader":
                    continue
                # Respect the allowlist when provided.
                if enabled_set and (loader_class.__name__.lower() not in enabled_set):
                    continue
                loader: BaseLoader = cast(BaseLoader, loader_class())
                loaders.append(loader)
            except Exception as e:  # noqa: BLE001
                # Loader failures should not prevent other loaders from being used.
                logger.warning(
                    "Failed to create loader %s: %s",
                    loader_class.__name__,
                    e,
                )

        logger.info(f"Created {len(loaders)} proxy loaders")
        return loaders

    def add_user_provided_loader(self, proxies: Iterable[Mapping[str, object]]) -> None:
        """
        Add a UserProvidedLoader with pre-supplied proxy data.

        Parameters
        ----------
        proxies : Iterable[Mapping[str, object]]
            Iterable of proxy-like mappings. Keys should align with the
            Proxy model (e.g., host/ip, port, schemes).

        Notes
        -----
        - Useful for injecting custom or premium proxies alongside free sources.
        """
        try:
            # Validate that proxies is actually an iterable of mappings
            proxy_list = list(proxies)
            if proxy_list and not isinstance(proxy_list[0], dict):
                raise ValueError("Expected iterable of dict-like mappings")

            user_loader = UserProvidedLoader(proxy_list)
            self.loaders.append(user_loader)
            logger.info("Added user-provided loader")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to add user-provided loader: {e}")

    def register_custom_loader(self, loader: BaseLoader) -> None:
        """
        Register an arbitrary loader instance.

        Parameters
        ----------
        loader : BaseLoader
            A ready-to-use loader implementing the BaseLoader interface.
        """
        self.loaders.append(loader)
        logger.info(f"Registered custom loader: {loader.name}")

    @asynccontextmanager
    async def session(self) -> AsyncIterator["ProxyWhirl"]:
        """
        Async context manager for resource lifecycle.

        Yields
        ------
        ProxyWhirl
            This instance, ready for async operations.

        Notes
        -----
        - Reserved for future resource acquisition/cleanup needs.
        """
        try:
            yield self
        finally:
            # Placeholder for cleanup of async resources if/when added.
            pass

    @classmethod
    async def create(
        cls,
        cache_type: Union[CacheType, str] = CacheType.MEMORY,
        cache_path: Optional[Union[str, Path]] = None,
        **kwargs: Union[str, int, float, bool],
    ) -> "ProxyWhirl":
        """
        Async factory for constructing a ProxyWhirl.

        Parameters
        ----------
        cache_type : CacheType or str, default="memory"
            See class parameters.
        cache_path : str or pathlib.Path, optional
            See class parameters.
        **kwargs
            Forwarded to the class initializer.

        Returns
        -------
        ProxyWhirl
            A fully initialized instance.
        """
        instance = cls(
            cache_type=cache_type,
            cache_path=cache_path,
            **kwargs,  # type: ignore
        )
        # No async init currently required.
        return instance

    def _is_async_context(self) -> bool:
        """
        Detect if a running event loop is present.

        Returns
        -------
        bool
            True if called within an async context (event loop running), else False.
        """
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False

    def _run_async(self, coro: Coroutine[Any, Any, T]) -> T:
        """
        Execute a coroutine from a synchronous context.

        Parameters
        ----------
        coro : Coroutine
            The coroutine to execute.

        Returns
        -------
        Any
            The coroutine result.

        Notes
        -----
        - Sync wrappers use this to provide blocking variants of async APIs.
        - In Jupyter notebooks and other environments with existing event loops,
          this will try to use nest_asyncio for compatibility.
        - For best performance, prefer using async methods directly in async contexts.
        """
        if self._is_async_context():
            logger.debug(
                "ProxyWhirl sync method called in async context (e.g., Jupyter). "
                "Attempting nest_asyncio compatibility."
            )
            try:
                # Try to use nest_asyncio for Jupyter compatibility
                import nest_asyncio  # type: ignore

                nest_asyncio.apply()
                return asyncio.run(coro)
            except ImportError:
                # Fallback: use the existing event loop with a workaround
                logger.debug("nest_asyncio not available, using event loop workaround")

                # Create a task and run it in the current event loop
                import concurrent.futures

                # Use a thread pool to run the coroutine in a new event loop
                def _run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(_run_in_thread)
                    return future.result()
            except Exception as e:
                logger.warning(f"Failed to run async in nested context: {e}")
                # Last resort: suggest async usage
                raise RuntimeError(
                    "Cannot run sync methods in this async context. "
                    "Please use the async version (e.g., get_proxy_async()) instead. "
                    "Alternatively, install nest_asyncio: pip install nest-asyncio"
                ) from e

        # Create and run a dedicated loop for the coroutine.
        return asyncio.run(coro)

    # === Async API ===

    async def fetch_proxies_async(self, validate: Optional[bool] = None) -> int:
        """
        Fetch proxies from all configured loaders and optionally validate.

        Parameters
        ----------
        validate : bool, optional
            Whether to run validation before caching. Defaults to `self.auto_validate`.

        Returns
        -------
        int
            Number of proxies added to the cache (post-validation when enabled).

        Notes
        -----
        - Loader outputs are expected as pandas.DataFrame; rows are converted to
          Proxy models with light field normalization (e.g., ip/host, protocol→schemes).
        - Duplicate host:port entries are deduplicated.
        - Validation occurs concurrently and may reduce the final count.
        """
        if validate is None:
            validate = self.auto_validate

        all_proxies: List[Proxy] = []
        seen: set[tuple[str, int]] = set()

        # Use asyncio.gather for parallel loading with resilient retry logic
        logger.info(f"Starting parallel load from {len(self.loaders)} loaders")
        tasks = [loader.load_with_retry() for loader in self.loaders]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for loader, result in zip(self.loaders, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to load from {loader.name}: {result}")
                continue

            try:
                # Type guard: result is now guaranteed to be a DataFrame
                df = cast(DataFrame, result)
                logger.info(f"Processing {len(df)} rows from {loader.name}")

                # Convert DataFrame to Proxy objects with minimal normalization.
                proxies: List[Proxy] = []
                for _, row in df.iterrows():
                    try:
                        proxy_data = cast(Dict[str, Any], dict(row))
                        # Normalize common aliases.
                        if "ip" not in proxy_data and "host" in proxy_data:
                            proxy_data["ip"] = proxy_data["host"]
                        if "protocol" in proxy_data:
                            proxy_data["schemes"] = [proxy_data["protocol"]]
                        proxy_data.setdefault("source", loader.name)

                        proxy = Proxy(**proxy_data)
                        key = (proxy.host, proxy.port)
                        if key in seen:
                            continue  # Drop duplicates eagerly.
                        seen.add(key)
                        proxies.append(proxy)
                    except Exception as e:  # noqa: BLE001
                        # Row-level failures are expected on noisy sources.
                        logger.debug(f"Failed to create proxy from row: {e}")
                        continue

                logger.info(f"Loaded {len(proxies)} proxies from {loader.name}")
                all_proxies.extend(proxies)

                # If a fetch cap is set, check if we need to truncate after all parallel loads
                if (
                    self.max_fetch_proxies is not None
                    and len(all_proxies) >= self.max_fetch_proxies
                ):
                    # Truncate to exact cap to avoid minor overrun
                    all_proxies = all_proxies[: self.max_fetch_proxies]
                    logger.info(
                        "Reached fetch cap of %d proxies after parallel loading",
                        self.max_fetch_proxies,
                    )
                    break

            except Exception as e:  # noqa: BLE001
                # Processing failures are logged and processing continues.
                logger.error(f"Failed to process results from {loader.name}: {e}")
                continue

        if validate and all_proxies:
            # Optionally cap validation count during fetch to keep runs fast by default
            proxies_to_validate = all_proxies
            if (
                self.max_validate_on_fetch is not None
                and len(all_proxies) > self.max_validate_on_fetch
            ):
                logger.info(
                    "Capping validation to first %d proxies out of %d during fetch",
                    self.max_validate_on_fetch,
                    len(all_proxies),
                )
                proxies_to_validate = all_proxies[: self.max_validate_on_fetch]

            logger.info("Validating %d loaded proxies...", len(proxies_to_validate))
            validation_result = await self.validator.validate_proxies(proxies_to_validate)
            # Replace with valid proxies only.
            all_proxies = validation_result.valid_proxies
            logger.info(
                "Validation complete: %.1f%% success rate",
                validation_result.success_rate * 100.0,
            )

        # Persist final set to cache.
        self.cache.add_proxies(all_proxies)

        logger.info(f"Total proxies loaded: {len(all_proxies)}")
        return len(all_proxies)

    async def get_proxy_async(
        self,
        target_id: Optional[str] = None,
        session_id: Optional[str] = None,
        custom_ttl: Optional[int] = None,
    ) -> Optional[Proxy]:
        """
        Retrieve a proxy according to the configured rotation strategy.

        If the cache is empty, automatically fetches and validates proxies
        from configured loaders before attempting to return a proxy.

        Parameters
        ----------
        target_id : str, optional
            Filter proxies that are healthy for a specific target.
            If provided, only returns proxies with good health for this target.
            If None, uses standard proxy selection without target filtering.
        session_id : str, optional
            Unique identifier for session-based proxy stickiness.
            If provided, maintains consistent proxy assignment for the same session.
        custom_ttl : int, optional
            Custom TTL in seconds for session-based assignments. Uses rotator's default if None.
            Only applies when session_id is provided.

        Returns
        -------
        Proxy or None
            A proxy instance or None if no proxies could be fetched/validated.

        Notes
        -----
        - Auto-fetches proxies when cache is empty for seamless user experience
        - Uses the configured auto_validate setting for fetched proxies
        - Target-based filtering requires validation_targets to be configured
        - Session stickiness maintains consistent proxy assignment with TTL-based expiration
        - Unhealthy session proxies are automatically reassigned

        Examples
        --------
        Basic usage:
            >>> proxy = await pw.get_proxy_async()

        With target filtering:
            >>> proxy = await pw.get_proxy_async(target_id="website1")

        With session stickiness:
            >>> proxy1 = await pw.get_proxy_async(session_id="user123")
            >>> proxy2 = await pw.get_proxy_async(session_id="user123")  # Same proxy as proxy1
        """
        proxies = self.cache.get_proxies()

        if not proxies:
            context = f"session {session_id}" if session_id else "proxy request"
            logger.info(f"Cache is empty, auto-fetching proxies for {context}...")
            try:
                # Auto-fetch proxies using the configured auto_validate setting
                fetched_count = await self.fetch_proxies_async(validate=self.auto_validate)
                if fetched_count > 0:
                    logger.info(f"Auto-fetched {fetched_count} proxies")
                    # Get proxies from the now-populated cache
                    proxies = self.cache.get_proxies()
                else:
                    logger.warning("No proxies could be fetched from any loader")
                    return None
            except Exception as e:
                logger.error(f"Failed to auto-fetch proxies: {e}")
                return None

        if not proxies:
            logger.warning("No proxies available after auto-fetch attempt")
            return None

        # Apply target-based filtering if requested
        if target_id is not None:
            if not self.validation_targets or target_id not in self.validation_targets:
                logger.warning(f"Target '{target_id}' not found in validation targets")
                return None

            # Filter proxies that are healthy for the specified target
            target_healthy_proxies = []
            for proxy in proxies:
                target_health = proxy.get_target_health(target_id)
                if target_health is not None:
                    # Consider proxy healthy if it has reasonable success rate and recent success
                    if target_health.success_rate >= 0.5 and target_health.consecutive_failures < 3:
                        target_healthy_proxies.append(proxy)

            if not target_healthy_proxies:
                context_msg = f" in session {session_id}" if session_id else ""
                logger.warning(f"No healthy proxies found for target '{target_id}'{context_msg}")
                return None

            context_msg = f" in session {session_id}" if session_id else ""
            logger.debug(
                f"Filtered {len(target_healthy_proxies)}/{len(proxies)} proxies for target '{target_id}'{context_msg}"
            )
            proxies = target_healthy_proxies

        # Use session-aware or regular proxy selection
        if session_id is not None:
            return self.rotator.get_proxy_for_session(session_id, proxies, target_id, custom_ttl)
        else:
            return self.rotator.get_proxy(proxies)

    async def export_proxies_async(self, config: "ExportConfig") -> str:
        """
        Export cached proxies asynchronously in specified format.

        Parameters
        ----------
        config : ExportConfig
            Export configuration including format, filters, and options.

        Returns
        -------
        str
            Formatted export string.

        Raises
        ------
        ProxyExportError
            If export operation fails.
        """
        from .exporter import ProxyExporter

        # Get cached proxies
        proxies = self.cache.get_proxies()
        if not proxies:
            logger.warning("No proxies available for export")
            return ""

        # Create exporter and export
        exporter = ProxyExporter()
        return exporter.export(proxies, config)

    async def export_to_file_async(self, config: "ExportConfig") -> tuple[str, int]:
        """
        Export cached proxies to file asynchronously.

        Parameters
        ----------
        config : ExportConfig
            Export configuration including file path.

        Returns
        -------
        tuple[str, int]
            File path and number of proxies exported.

        Raises
        ------
        ProxyExportError
            If file export operation fails.
        """
        from .exporter import ProxyExporter

        # Get cached proxies
        proxies = self.cache.get_proxies()
        if not proxies:
            logger.warning("No proxies available for export")
            return "", 0

        # Create exporter and export to file
        exporter = ProxyExporter()
        return exporter.export_to_file(proxies, config)

    async def validate_proxies_async(self, max_proxies: Optional[int] = None) -> int:
        """
        Validate all cached proxies with intelligent lifecycle management.

        Returns
        -------
        int
            Count of valid proxies remaining in the cache.

        Notes
        -----
        - Uses differentiated error handling instead of clearing entire cache.
        - Proxies are selectively removed, paused, or retained based on error types.
        """
        proxies = self.cache.get_proxies()

        if not proxies:
            logger.info("No proxies to validate")
            return 0

        # Normalize cap (non-positive treated as no cap)
        if max_proxies is not None and max_proxies <= 0:
            max_proxies = None

        proxies_to_validate = proxies
        if max_proxies is not None and len(proxies) > max_proxies:
            logger.info(
                "Validating up to %d proxies out of %d (explicit cap)",
                max_proxies,
                len(proxies),
            )
            proxies_to_validate = proxies[:max_proxies]

        validation_result = await self.validator.validate_proxies(proxies_to_validate)

        # Process results with differentiated error handling
        proxies_to_remove = []
        proxies_to_update = []

        for result in validation_result.failed_proxy_results:
            proxy = result.proxy

            # Update error state using the enhanced rotator method
            self.update_proxy_health(
                proxy=proxy,
                success=False,
                response_time=result.response_time,
                error_type=result.error_type,
                error_message=result.error_message,
                http_status=result.status_code,
            )

            # Check if proxy should be removed (inactive/blacklisted status)
            if proxy.status in [ProxyStatus.INACTIVE, ProxyStatus.BLACKLISTED]:
                proxies_to_remove.append(proxy)
                logger.debug(
                    "Removing proxy %s:%s (status: %s, error: %s)",
                    proxy.host,
                    proxy.port,
                    proxy.status,
                    result.error_type,
                )
            else:
                # Proxy is in cooldown but will be retained
                proxies_to_update.append(proxy)
                logger.debug(
                    "Retaining proxy %s:%s in cooldown until %s (error: %s)",
                    proxy.host,
                    proxy.port,
                    proxy.error_state.cooldown_until,
                    result.error_type,
                )

        # Update successful proxies
        for result in validation_result.valid_proxy_results:
            self.update_proxy_health(
                proxy=result.proxy,
                success=True,
                response_time=result.response_time,
            )
            proxies_to_update.append(result.proxy)

        # Apply selective removal instead of nuclear cache clear
        for proxy in proxies_to_remove:
            self.cache.remove_proxy(proxy)

        for proxy in proxies_to_update:
            self.cache.update_proxy(proxy)

        # Count currently available (non-cooldown) proxies
        remaining_proxies = self.cache.get_proxies()
        available_count = sum(1 for p in remaining_proxies if p.error_state.is_available())

        logger.info(
            "Validation complete: %d total proxies, %d available, %d in cooldown, %d removed",
            len(remaining_proxies),
            available_count,
            len(remaining_proxies) - available_count,
            len(proxies_to_remove),
        )

        return available_count

    # === Sync API with smart async detection ===

    def fetch_proxies(self, validate: Optional[bool] = None) -> int:
        """
        Synchronous wrapper for fetch_proxies_async.

        Parameters
        ----------
        validate : bool, optional
            See fetch_proxies_async.

        Returns
        -------
        int
            See fetch_proxies_async.

        Raises
        ------
        RuntimeError
            If invoked from an async context.
        """
        return self._run_async(self.fetch_proxies_async(validate))

    def get_proxy(self, target_id: Optional[str] = None) -> Optional[Proxy]:
        """
        Synchronous wrapper for get_proxy_async.

        Parameters
        ----------
        target_id : str, optional
            Filter proxies that are healthy for a specific target.

        Returns
        -------
        Proxy or None
            See get_proxy_async.

        Raises
        ------
        RuntimeError
            If invoked from an async context.
        """
        return self._run_async(self.get_proxy_async(target_id))

    def validate_proxies(self) -> int:
        """
        Synchronous wrapper for validate_proxies_async.

        Returns
        -------
        int
            See validate_proxies_async.

        Raises
        ------
        RuntimeError
            If invoked from an async context.
        """
        return self._run_async(self.validate_proxies_async())

    def export_proxies(self, config: "ExportConfig") -> str:
        """
        Synchronous wrapper for export_proxies_async.

        Parameters
        ----------
        config : ExportConfig
            Export configuration including format, filters, and options.

        Returns
        -------
        str
            Formatted export string.

        Raises
        ------
        RuntimeError
            If invoked from an async context.
        """
        return self._run_async(self.export_proxies_async(config))

    def export_to_file(self, config: "ExportConfig") -> tuple[str, int]:
        """
        Synchronous wrapper for export_to_file_async.

        Parameters
        ----------
        config : ExportConfig
            Export configuration including file path.

        Returns
        -------
        tuple[str, int]
            File path and number of proxies exported.

        Raises
        ------
        RuntimeError
            If invoked from an async context.
        """
        return self._run_async(self.export_to_file_async(config))

    # === Sync methods that don't require async ===

    def list_proxies(self) -> List[Proxy]:
        """
        List all cached proxies.

        Returns
        -------
        list[Proxy]
            Current snapshot of proxies in the cache.
        """
        return self.cache.get_proxies()

    def update_proxy_health(
        self,
        proxy: Proxy,
        success: bool,
        response_time: Optional[float] = None,
        error_type: Optional[ValidationErrorType] = None,
        error_message: Optional[str] = None,
        http_status: Optional[int] = None,
    ) -> None:
        """
        Update a proxy's health based on recent usage.

        Parameters
        ----------
        proxy : Proxy
            The proxy to update.
        success : bool
            Whether the last usage succeeded.
        response_time : float, optional
            Observed response time in seconds. If provided, persisted on the model.
        error_type : ValidationErrorType, optional
            Type of error if request failed.
        error_message : str, optional
            Error message if request failed.
        http_status : int, optional
            HTTP status code if available.

        Notes
        -----
        - Also updates the cache with timing metadata when available.
        - Applies differentiated error handling based on error type.
        """
        self.rotator.update_health_score(
            proxy, success, response_time, error_type, error_message, http_status
        )

        # Update proxy in cache with timing metadata.
        if response_time is not None:
            proxy.response_time = response_time
            proxy.last_checked = datetime.now(timezone.utc)
            self.cache.update_proxy(proxy)

    def get_proxy_count(self) -> int:
        """
        Get the number of proxies currently cached.

        Returns
        -------
        int
            Cache size.
        """
        return len(self.cache.get_proxies())

    def clear_cache(self) -> None:
        """
        Remove all proxies from the cache.

        Notes
        -----
        - This operation is irreversible for the current process lifetime.
        """
        self.cache.clear()
        logger.info("Proxy cache cleared")

    async def generate_health_report(self) -> str:
        """
        Generate a comprehensive Markdown health report.

        Combines loader status, validation metrics, validator health, and cache
        statistics into a single Markdown document suitable for logging or
        diagnostics.

        Returns
        -------
        str
            Markdown report.

        Notes
        -----
        - May perform limited sampling validation to estimate quality.
        - Integrates validator circuit-breaker state and test endpoint status.
        """
        # Collect data from all components.
        cache_stats = self.cache.get_stats() if hasattr(self.cache, "get_stats") else {}
        validator_stats = self.validator.get_validation_stats()
        validator_health = await self.validator.health_check()

        # Get current proxy status.
        proxies = self.list_proxies()
        total_proxies = len(proxies)

        # Generate validation summary if we have proxies (sampled for speed).
        validation_summary = None
        if proxies:
            validation_summary = await self.validator.validate_proxies(proxies[:20])  # Sample

        # Build the report (Markdown).
        report_lines = [
            "# ProxyWhirl Health Report",
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "## 📊 Overview",
            f"- **Total Proxies:** {total_proxies}",
            f"- **Cache Type:** {self.cache_type.value}",
            f"- **Rotation Strategy:** {self.rotation_strategy.value}",
            f"- **Auto Validation:** {'✅ Enabled' if self.auto_validate else '❌ Disabled'}",
            "",
        ]

        # Add loader status
        if self.loaders:
            report_lines.extend(
                [
                    "## 🔄 Loader Status",
                    "| Loader | Status | Last Update |",
                    "|--------|--------|-------------|",
                ]
            )

            for loader in self.loaders:
                status = "✅ Active" if hasattr(loader, "load") else "❌ Inactive"
                last_update = getattr(loader, "last_update", "Never")
                report_lines.append(f"| {loader.name} | {status} | {last_update} |")

            report_lines.append("")

        # Add validation metrics if available
        if validation_summary:
            report_lines.extend(
                [
                    "## ✅ Validation Metrics",
                    f"- **Success Rate:** {validation_summary.success_rate:.1%}",
                    f"- **Quality Tier:** {validation_summary.quality_tier}",
                    f"- **Valid Proxies:** {validation_summary.valid_proxy_count}/{validation_summary.total_proxies}",
                ]
            )

            if validation_summary.avg_response_time:
                report_lines.append(
                    f"- **Avg Response Time:** {validation_summary.avg_response_time:.2f}s"
                )

            # Add error breakdown if there are errors
            if validation_summary.error_breakdown:
                report_lines.extend(
                    [
                        "",
                        "### Error Breakdown",
                    ]
                )
                for error_type, count in validation_summary.error_breakdown.items():
                    report_lines.append(f"- **{error_type.value.title()}:** {count}")

            report_lines.append("")

        # Add validator health status
        report_lines.extend(
            [
                "## 🔧 Validator Health",
                f"- **Circuit Breaker:** {validator_health['circuit_breaker_state'].upper()}",
                f"- **Failure Count:** {validator_health['circuit_breaker_failures']}",
                f"- **Total Validations:** {validator_stats['total_validations']}",
                f"- **Overall Success Rate:** {validator_stats['success_rate']:.1%}",
                "",
            ]
        )

        # Add test endpoint status
        if validator_health.get("test_endpoints"):
            report_lines.extend(
                [
                    "### Test Endpoints",
                    "| Endpoint | Status | Response Time |",
                    "|----------|--------|---------------|",
                ]
            )

            for endpoint in validator_health["test_endpoints"]:
                status = "✅ Healthy" if endpoint["status"] == "healthy" else "❌ Unhealthy"
                response_time = (
                    f"{endpoint.get('response_time', 'N/A')}s"
                    if endpoint.get("response_time")
                    else "N/A"
                )
                report_lines.append(f"| {endpoint['url']} | {status} | {response_time} |")

            report_lines.append("")

        # Add cache statistics if available
        if cache_stats:
            report_lines.extend(
                [
                    "## 💾 Cache Statistics",
                    f"- **Cache Hits:** {cache_stats.get('hits', 'N/A')}",
                    f"- **Cache Misses:** {cache_stats.get('misses', 'N/A')}",
                    f"- **Cache Size:** {cache_stats.get('size', 'N/A')} items",
                    "",
                ]
            )

        # Add recommendations
        recommendations = []

        if validation_summary:
            if validation_summary.success_rate < 0.5:
                recommendations.append(
                    "⚠️ Low proxy success rate - consider refreshing proxy sources"
                )
            if validation_summary.avg_response_time and validation_summary.avg_response_time > 5.0:
                recommendations.append(
                    "🐌 High average response time - consider filtering slower proxies"
                )

        if validator_health["circuit_breaker_failures"] > 0:
            recommendations.append("🔧 Circuit breaker has failures - check test endpoints")

        if total_proxies < 10:
            recommendations.append("📊 Low proxy count - consider enabling more loader sources")

        if recommendations:
            report_lines.extend(
                [
                    "## 💡 Recommendations",
                ]
            )
            report_lines.extend(recommendations)
            report_lines.append("")

        # Add footer
        report_lines.extend(
            ["---", "*Report generated by ProxyWhirl - Rotating Proxy Management Library*"]
        )

        return "\n".join(report_lines)
