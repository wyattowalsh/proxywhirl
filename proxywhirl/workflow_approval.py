"""Workflow approval system for changes.

Implements approval workflow for proxy configurations,
deployments, and policy changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class ApprovalStatus(str, Enum):
    """Status of approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"


@dataclass
class ApprovalRequest:
    """Represents an approval request."""

    request_id: str
    requester: str
    change_description: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    approvers: list[str] | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: list[str] | None = None
    approval_date: datetime | None = None
    rejection_reason: str | None = None


class WorkflowApprovalManager:
    """Manages approval workflows."""

    def __init__(self) -> None:
        """Initialize workflow approval manager."""
        self._requests: dict[str, ApprovalRequest] = {}
        logger.debug("WorkflowApprovalManager initialized")

    def create_request(
        self,
        request_id: str,
        requester: str,
        change_description: str,
        approvers: list[str] | None = None,
    ) -> bool:
        """Create approval request.

        Args:
            request_id: Request ID
            requester: Requester name
            change_description: Description of changes
            approvers: List of required approvers

        Returns:
            True if created
        """
        if request_id in self._requests:
            logger.warning(f"Request already exists: {request_id}")
            return False

        request = ApprovalRequest(
            request_id=request_id,
            requester=requester,
            change_description=change_description,
            approvers=approvers or [],
            approved_by=[],
        )
        self._requests[request_id] = request
        logger.info(f"Approval request created: {request_id}")
        return True

    def approve_request(self, request_id: str, approver: str) -> bool:
        """Approve request.

        Args:
            request_id: Request ID
            approver: Approver name

        Returns:
            True if approved
        """
        if request_id not in self._requests:
            return False

        request = self._requests[request_id]

        if request.status != ApprovalStatus.PENDING:
            logger.warning(f"Request not pending: {request_id}")
            return False

        if request.approved_by is None:
            request.approved_by = []

        if approver not in request.approved_by:
            request.approved_by.append(approver)

        if request.approvers and all(a in request.approved_by for a in request.approvers):
            request.status = ApprovalStatus.APPROVED
            request.approval_date = datetime.now(timezone.utc)
            logger.info(f"Request fully approved: {request_id}")
        else:
            logger.info(f"Request partially approved by {approver}: {request_id}")

        return True

    def reject_request(self, request_id: str, reason: str = "") -> bool:
        """Reject request.

        Args:
            request_id: Request ID
            reason: Rejection reason

        Returns:
            True if rejected
        """
        if request_id not in self._requests:
            return False

        request = self._requests[request_id]

        if request.status != ApprovalStatus.PENDING:
            logger.warning(f"Request not pending: {request_id}")
            return False

        request.status = ApprovalStatus.REJECTED
        request.rejection_reason = reason
        logger.info(f"Request rejected: {request_id}")
        return True

    def revoke_request(self, request_id: str) -> bool:
        """Revoke approved request.

        Args:
            request_id: Request ID

        Returns:
            True if revoked
        """
        if request_id not in self._requests:
            return False

        request = self._requests[request_id]

        if request.status == ApprovalStatus.APPROVED:
            request.status = ApprovalStatus.REVOKED
            logger.info(f"Request revoked: {request_id}")
            return True

        return False

    def get_pending_requests(self) -> list[ApprovalRequest]:
        """Get pending approval requests.

        Returns:
            List of pending requests
        """
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]

    def export_metrics(self) -> dict[str, Any]:
        """Export approval metrics.

        Returns:
            Dictionary of metrics
        """
        approved = sum(1 for r in self._requests.values() if r.status == ApprovalStatus.APPROVED)
        rejected = sum(1 for r in self._requests.values() if r.status == ApprovalStatus.REJECTED)
        pending = len(self.get_pending_requests())

        return {
            "total_requests": len(self._requests),
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
        }
