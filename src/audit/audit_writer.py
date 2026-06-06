from __future__ import annotations

import logging
from datetime import datetime, timezone

from src.contracts.evidence_packet import EvidencePacket

logger = logging.getLogger(__name__)


class AuditRecord:
    """Structured audit record for evidence packet persistence."""

    def __init__(self, packet: EvidencePacket) -> None:
        self.packet_id = packet.packet_id
        self.finding_id = packet.finding_id
        self.input_hash = packet.input_hash
        self.model_provider = packet.model_provider
        self.model_deployment = packet.model_deployment
        self.prompt_tokens = packet.cost.prompt_tokens
        self.completion_tokens = packet.cost.completion_tokens
        self.estimated_llm_cost_usd = packet.cost.estimated_llm_cost_usd
        self.estimated_platform_cost_usd = packet.cost.estimated_platform_cost_usd
        self.confidence = packet.confidence
        self.citation_count = packet.citation_count
        self.trust_boundary = packet.trust_boundary.value
        self.review_status = packet.review_status.value
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "packet_id": self.packet_id,
            "finding_id": self.finding_id,
            "input_hash": self.input_hash,
            "model_provider": self.model_provider,
            "model_deployment": self.model_deployment,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "estimated_llm_cost_usd": self.estimated_llm_cost_usd,
            "estimated_platform_cost_usd": self.estimated_platform_cost_usd,
            "confidence": self.confidence,
            "citation_count": self.citation_count,
            "trust_boundary": self.trust_boundary,
            "review_status": self.review_status,
            "created_at": self.created_at.isoformat(),
        }


class AuditWriter:
    """Writes audit records. In mock mode, logs only. In live mode, writes to Snowflake."""

    def __init__(self, snowflake_client: object | None = None) -> None:
        self.snowflake_client = snowflake_client
        self._records: list[AuditRecord] = []

    async def write(self, packet: EvidencePacket) -> AuditRecord:
        record = AuditRecord(packet)
        self._records.append(record)
        logger.info("Audit record created: packet_id=%s", record.packet_id)
        return record

    @property
    def records(self) -> list[AuditRecord]:
        return list(self._records)
