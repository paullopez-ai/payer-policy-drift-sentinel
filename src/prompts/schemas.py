from __future__ import annotations

EVIDENCE_PACKET_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "root_cause_hypothesis": {"type": "string"},
        "recommended_review_path": {"type": "string"},
        "citations_used": {
            "type": "array",
            "items": {"type": "string"},
        },
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "limitations": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "summary",
        "root_cause_hypothesis",
        "recommended_review_path",
        "citations_used",
        "confidence",
        "limitations",
    ],
}
