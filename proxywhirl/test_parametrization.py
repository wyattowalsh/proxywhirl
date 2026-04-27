"""Parametrization helpers for comprehensive test coverage.

Provides utilities for systematic parametrization of test cases
across different parameter combinations and edge cases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class ParameterSet:
    """Represents a set of test parameters."""

    name: str
    parameters: dict[str, Any]
    expected_result: Any | None = None
    should_raise: type[Exception] | None = None


class ParametrizationMatrix:
    """Creates parametrization matrices for comprehensive testing."""

    def __init__(self) -> None:
        """Initialize parametrization matrix."""
        self._test_sets: dict[str, list[ParameterSet]] = {}
        logger.debug("ParametrizationMatrix initialized")

    def register_parameter_set(
        self,
        test_name: str,
        param_set: ParameterSet,
    ) -> bool:
        """Register parameter set.

        Args:
            test_name: Name of test
            param_set: Parameter set

        Returns:
            True if registered
        """
        if test_name not in self._test_sets:
            self._test_sets[test_name] = []

        self._test_sets[test_name].append(param_set)
        logger.debug(f"Parameter set registered: {test_name} - {param_set.name}")
        return True

    def create_combination_matrix(self, param_lists: dict[str, list[Any]]) -> list[dict[str, Any]]:
        """Create cartesian product of parameters.

        Args:
            param_lists: Dictionary of parameter names to lists

        Returns:
            List of parameter dictionaries
        """
        if not param_lists:
            return [{}]

        import itertools

        keys = list(param_lists.keys())
        values = list(param_lists.values())

        combinations = []
        for combo in itertools.product(*values):
            combinations.append(dict(zip(keys, combo)))

        logger.debug(f"Combinations created: {len(combinations)}")
        return combinations

    def create_edge_cases(
        self,
        param_type: str,
    ) -> list[Any]:
        """Generate edge cases for parameter type.

        Args:
            param_type: Type of parameter (int, str, list, dict)

        Returns:
            List of edge case values
        """
        edge_cases: dict[str, list[Any]] = {
            "int": [0, 1, -1, 2147483647, -2147483648],
            "str": ["", " ", "\n", "a" * 1000, "\x00"],
            "list": [[], [1], [None], [1, 2, 3]],
            "dict": [{}, {"a": 1}, {"a": None}],
            "float": [0.0, 1.0, -1.0, float("inf"), float("-inf")],
        }

        return edge_cases.get(param_type, [])

    def get_parameter_sets(self, test_name: str) -> list[ParameterSet]:
        """Get parameter sets for test.

        Args:
            test_name: Test name

        Returns:
            List of parameter sets
        """
        return self._test_sets.get(test_name, [])

    def create_boundary_cases(
        self,
        min_val: int,
        max_val: int,
    ) -> list[int]:
        """Create boundary test cases.

        Args:
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            List of boundary values
        """
        return [
            min_val,
            max_val,
            min_val + 1,
            max_val - 1,
            (min_val + max_val) // 2,
        ]

    def export_matrix(self) -> dict[str, list[dict[str, Any]]]:
        """Export parameter matrix.

        Returns:
            Dictionary of test matrices
        """
        return {
            test_name: [
                {
                    "name": param_set.name,
                    "parameters": param_set.parameters,
                    "expected_result": param_set.expected_result,
                    "should_raise": (
                        param_set.should_raise.__name__ if param_set.should_raise else None
                    ),
                }
                for param_set in param_sets
            ]
            for test_name, param_sets in self._test_sets.items()
        }

    def get_total_test_cases(self) -> int:
        """Get total test cases.

        Returns:
            Total count
        """
        return sum(len(sets) for sets in self._test_sets.values())


class ParametrizationHelper:
    """Helper for parameter generation."""

    @staticmethod
    def scale_test(
        base_value: int,
        scales: list[int] | None = None,
    ) -> list[int]:
        """Generate scaled test values.

        Args:
            base_value: Base value
            scales: Scale factors

        Returns:
            List of scaled values
        """
        if scales is None:
            scales = [1, 10, 100, 1000]

        return [base_value * scale for scale in scales]

    @staticmethod
    def range_test(
        start: int,
        end: int,
        step: int = 1,
    ) -> list[int]:
        """Generate range test values.

        Args:
            start: Start value
            end: End value
            step: Step size

        Returns:
            List of values
        """
        return list(range(start, end + 1, step))
