"""
Consumer contract testing framework for proxy rotation API.

This module provides contract definitions and validation for consumer
contracts ensuring API stability across versions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class ContractType(str, Enum):
    """Types of contracts."""

    REQUEST = "request"
    RESPONSE = "response"
    STATE = "state"
    ERROR = "error"


@dataclass
class ContractTerm:
    """Represents a single contract term."""

    name: str
    expected_value: Any
    actual_value: Any | None = None
    satisfied: bool = False
    message: str = ""

    def validate(self) -> bool:
        """Validate contract term."""
        self.satisfied = self.actual_value == self.expected_value
        if not self.satisfied:
            self.message = f"Expected {self.expected_value}, got {self.actual_value}"
        return self.satisfied


@dataclass
class Contract:
    """Represents a consumer contract."""

    name: str
    version: str
    contract_type: ContractType
    terms: list[ContractTerm]
    description: str = ""
    created_at: str = ""

    def validate_all(self) -> bool:
        """Validate all contract terms."""
        return all(term.validate() for term in self.terms)

    def get_failures(self) -> list[ContractTerm]:
        """Get failed contract terms."""
        return [term for term in self.terms if not term.satisfied]


class ContractValidator:
    """Validates consumer contracts."""

    def __init__(self):
        """Initialize validator."""
        self.contracts: dict[str, Contract] = {}
        self.validators: dict[str, Callable] = {}

    def register_contract(self, contract: Contract) -> None:
        """Register a contract."""
        key = f"{contract.name}:{contract.version}"
        self.contracts[key] = contract

    def register_validator(
        self,
        name: str,
        validator_func: Callable[[Any], bool],
    ) -> None:
        """Register custom validator function."""
        self.validators[name] = validator_func

    def validate_response(
        self,
        response: dict,
        contract_name: str,
        version: str = "1.0",
    ) -> bool:
        """Validate response against contract."""
        key = f"{contract_name}:{version}"
        if key not in self.contracts:
            raise ValueError(f"Contract not found: {key}")

        contract = self.contracts[key]
        for term in contract.terms:
            term.actual_value = response.get(term.name)

        return contract.validate_all()

    def validate_request(
        self,
        request: dict,
        contract_name: str,
        version: str = "1.0",
    ) -> bool:
        """Validate request against contract."""
        return self.validate_response(request, contract_name, version)

    def get_violations(
        self,
        contract_name: str,
        version: str = "1.0",
    ) -> list[str]:
        """Get contract violations."""
        key = f"{contract_name}:{version}"
        if key not in self.contracts:
            return []

        contract = self.contracts[key]
        contract.validate_all()
        return [f"{term.name}: {term.message}" for term in contract.get_failures()]


__all__ = [
    "Contract",
    "ContractTerm",
    "ContractValidator",
    "ContractType",
]
