"""Interactive configuration wizard for the CLI.

Guides users through configuration setup with prompts and validation.
"""

from __future__ import annotations

from typing import Any

from loguru import logger


class ConfigWizard:
    """Interactive configuration wizard.

    Example:
        >>> wizard = ConfigWizard()
        >>> config = wizard.run()
    """

    def __init__(self) -> None:
        """Initialize configuration wizard."""
        self.config: dict[str, Any] = {}

    def run(self) -> dict[str, Any]:
        """Run the interactive wizard.

        Returns:
            Configuration dict
        """
        logger.info("Starting configuration wizard...")

        self._ask_pool_config()
        self._ask_rotation_config()
        self._ask_validation_config()
        self._ask_retry_config()
        self._ask_cache_config()
        self._ask_circuit_breaker_config()
        self._ask_rate_limiting_config()

        logger.info("Configuration wizard completed")
        return self.config

    def _ask_pool_config(self) -> None:
        """Configure pool settings."""
        logger.info("Configuring proxy pool...")

        self.config["pool"] = {
            "max_size": self._prompt_int(
                "Maximum pool size (10-1000)",
                default=100,
                min_val=10,
                max_val=1000,
            ),
            "timeout_seconds": self._prompt_int(
                "Pool timeout in seconds (5-60)",
                default=30,
                min_val=5,
                max_val=60,
            ),
        }

    def _ask_rotation_config(self) -> None:
        """Configure rotation strategy."""
        logger.info("Configuring rotation strategy...")

        strategies = [
            "round_robin",
            "weighted",
            "hash_based",
            "performance_based",
        ]
        strategy_choice = self._prompt_choice("Select rotation strategy", strategies)

        self.config["rotation"] = {"strategy": strategy_choice}

    def _ask_validation_config(self) -> None:
        """Configure validation settings."""
        logger.info("Configuring proxy validation...")

        enable_validation = self._prompt_yes_no(
            "Enable proxy validation?",
            default=True,
        )

        if enable_validation:
            self.config["validation"] = {
                "enabled": True,
                "timeout": self._prompt_int(
                    "Validation timeout in seconds (5-60)",
                    default=10,
                    min_val=5,
                    max_val=60,
                ),
                "max_concurrent": self._prompt_int(
                    "Max concurrent validations (10-200)",
                    default=50,
                    min_val=10,
                    max_val=200,
                ),
            }
        else:
            self.config["validation"] = {"enabled": False}

    def _ask_retry_config(self) -> None:
        """Configure retry settings."""
        logger.info("Configuring retry policy...")

        enable_retry = self._prompt_yes_no("Enable retry on failure?", default=True)

        if enable_retry:
            self.config["retry"] = {
                "enabled": True,
                "max_attempts": self._prompt_int(
                    "Max retry attempts (1-10)",
                    default=3,
                    min_val=1,
                    max_val=10,
                ),
                "backoff_factor": self._prompt_float(
                    "Backoff factor (1.0-3.0)",
                    default=1.5,
                    min_val=1.0,
                    max_val=3.0,
                ),
            }
        else:
            self.config["retry"] = {"enabled": False}

    def _ask_cache_config(self) -> None:
        """Configure caching settings."""
        logger.info("Configuring cache...")

        enable_cache = self._prompt_yes_no("Enable caching?", default=True)

        if enable_cache:
            self.config["cache"] = {
                "enabled": True,
                "ttl_seconds": self._prompt_int(
                    "Cache TTL in seconds (300-86400)",
                    default=3600,
                    min_val=300,
                    max_val=86400,
                ),
            }
        else:
            self.config["cache"] = {"enabled": False}

    def _ask_circuit_breaker_config(self) -> None:
        """Configure circuit breaker settings."""
        logger.info("Configuring circuit breaker...")

        enable_cb = self._prompt_yes_no(
            "Enable circuit breaker?",
            default=False,
        )

        if enable_cb:
            self.config["circuit_breaker"] = {
                "enabled": True,
                "failure_threshold": self._prompt_int(
                    "Failure threshold (1-10)",
                    default=5,
                    min_val=1,
                    max_val=10,
                ),
                "timeout_duration": self._prompt_int(
                    "Timeout duration in seconds (10-300)",
                    default=30,
                    min_val=10,
                    max_val=300,
                ),
            }
        else:
            self.config["circuit_breaker"] = {"enabled": False}

    def _ask_rate_limiting_config(self) -> None:
        """Configure rate limiting settings."""
        logger.info("Configuring rate limiting...")

        enable_rl = self._prompt_yes_no(
            "Enable rate limiting?",
            default=False,
        )

        if enable_rl:
            self.config["rate_limiting"] = {
                "enabled": True,
                "requests_per_minute": self._prompt_int(
                    "Requests per minute (100-10000)",
                    default=1000,
                    min_val=100,
                    max_val=10000,
                ),
            }
        else:
            self.config["rate_limiting"] = {"enabled": False}

    @staticmethod
    def _prompt_int(
        prompt: str,
        default: int,
        min_val: int | None = None,
        max_val: int | None = None,
    ) -> int:
        """Prompt for integer input with validation.

        Args:
            prompt: Prompt text
            default: Default value
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Validated integer
        """
        while True:
            try:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
                value = int(user_input)

                if min_val is not None and value < min_val:
                    logger.warning(f"Value must be >= {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    logger.warning(f"Value must be <= {max_val}")
                    continue

                return value
            except ValueError:
                logger.warning("Please enter a valid integer")

    @staticmethod
    def _prompt_float(
        prompt: str,
        default: float,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> float:
        """Prompt for float input with validation.

        Args:
            prompt: Prompt text
            default: Default value
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Validated float
        """
        while True:
            try:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
                value = float(user_input)

                if min_val is not None and value < min_val:
                    logger.warning(f"Value must be >= {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    logger.warning(f"Value must be <= {max_val}")
                    continue

                return value
            except ValueError:
                logger.warning("Please enter a valid number")

    @staticmethod
    def _prompt_yes_no(prompt: str, default: bool = True) -> bool:
        """Prompt for yes/no input.

        Args:
            prompt: Prompt text
            default: Default value

        Returns:
            Boolean result
        """
        default_str = "Y/n" if default else "y/N"
        while True:
            user_input = input(f"{prompt}? [{default_str}]: ").strip().lower()
            if not user_input:
                return default
            if user_input in ("y", "yes"):
                return True
            if user_input in ("n", "no"):
                return False
            logger.warning("Please enter 'y' or 'n'")

    @staticmethod
    def _prompt_choice(prompt: str, choices: list[str]) -> str:
        """Prompt for choice from list.

        Args:
            prompt: Prompt text
            choices: Available choices

        Returns:
            Selected choice
        """
        for i, choice in enumerate(choices, 1):
            print(f"  {i}) {choice}")

        while True:
            try:
                user_input = input(f"{prompt}: ").strip()
                choice_idx = int(user_input) - 1
                if 0 <= choice_idx < len(choices):
                    return choices[choice_idx]
                logger.warning(f"Please select 1-{len(choices)}")
            except ValueError:
                logger.warning("Please enter a valid number")
