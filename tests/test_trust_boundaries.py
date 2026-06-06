"""Trust boundary classification tests."""

from __future__ import annotations

from datetime import date

from src.contracts.findings import DriftFinding, FindingType, Severity
from src.contracts.review import ReviewStatus, TrustBoundary
from src.security.trust_boundaries import classify_trust_boundary, determine_review_status


def _make_finding(
    finding_type: FindingType = FindingType.DENIAL_SPIKE,
    severity: Severity = Severity.HIGH,
    confidence: float = 0.85,
) -> DriftFinding:
    return DriftFinding(
        finding_id="test",
        scenario_id="test",
        finding_type=finding_type,
        detection_date=date(2024, 9, 15),
        procedure_group="advanced_imaging",
        baseline_rate=0.08,
        observed_rate=0.23,
        delta=0.15,
        severity=severity,
        confidence=confidence,
        policy_version_id="PV-001",
    )


def test_provider_outlier_is_restricted():
    finding = _make_finding(finding_type=FindingType.PROVIDER_OUTLIER)
    assert classify_trust_boundary(finding) == TrustBoundary.RESTRICTED


def test_policy_version_drift_is_restricted():
    finding = _make_finding(finding_type=FindingType.POLICY_VERSION_DRIFT)
    assert classify_trust_boundary(finding) == TrustBoundary.RESTRICTED


def test_critical_severity_is_restricted():
    finding = _make_finding(severity=Severity.CRITICAL)
    assert classify_trust_boundary(finding) == TrustBoundary.RESTRICTED


def test_high_severity_is_supervised():
    finding = _make_finding(severity=Severity.HIGH, finding_type=FindingType.DENIAL_SPIKE)
    assert classify_trust_boundary(finding) == TrustBoundary.SUPERVISED


def test_low_confidence_is_restricted():
    finding = _make_finding(confidence=0.4, severity=Severity.LOW)
    assert classify_trust_boundary(finding) == TrustBoundary.RESTRICTED


def test_low_severity_high_confidence_is_autonomous():
    finding = _make_finding(severity=Severity.LOW, confidence=0.9, finding_type=FindingType.DENIAL_SPIKE)
    assert classify_trust_boundary(finding) == TrustBoundary.AUTONOMOUS


def test_restricted_requires_review():
    assert determine_review_status(TrustBoundary.RESTRICTED) == ReviewStatus.REQUIRED


def test_supervised_requires_review():
    assert determine_review_status(TrustBoundary.SUPERVISED) == ReviewStatus.REQUIRED


def test_autonomous_no_review():
    assert determine_review_status(TrustBoundary.AUTONOMOUS) == ReviewStatus.NOT_REQUIRED
