from __future__ import annotations

from src.contracts.findings import DriftFinding, FindingType, Severity
from src.contracts.review import ReviewStatus, TrustBoundary


def classify_trust_boundary(finding: DriftFinding) -> TrustBoundary:
    """Classify a finding's trust boundary based on type, severity, and confidence."""
    # Provider outlier findings are always restricted
    if finding.finding_type == FindingType.PROVIDER_OUTLIER:
        return TrustBoundary.RESTRICTED

    # Policy version drift is always restricted
    if finding.finding_type == FindingType.POLICY_VERSION_DRIFT:
        return TrustBoundary.RESTRICTED

    # Critical severity is restricted
    if finding.severity == Severity.CRITICAL:
        return TrustBoundary.RESTRICTED

    # High severity is supervised
    if finding.severity == Severity.HIGH:
        return TrustBoundary.SUPERVISED

    # Low confidence is restricted
    if finding.confidence < 0.6:
        return TrustBoundary.RESTRICTED

    # Medium severity is supervised
    if finding.severity == Severity.MEDIUM:
        return TrustBoundary.SUPERVISED

    return TrustBoundary.AUTONOMOUS


def determine_review_status(trust_boundary: TrustBoundary) -> ReviewStatus:
    """Determine review requirement from trust boundary."""
    if trust_boundary == TrustBoundary.RESTRICTED:
        return ReviewStatus.REQUIRED
    if trust_boundary == TrustBoundary.SUPERVISED:
        return ReviewStatus.REQUIRED
    return ReviewStatus.NOT_REQUIRED
