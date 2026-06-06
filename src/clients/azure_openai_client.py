from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class AzureOpenAIClientBase(ABC):
    """Abstract base for Azure OpenAI interactions."""

    @abstractmethod
    async def generate_evidence(
        self, prompt: str, max_tokens: int = 1800
    ) -> dict[str, Any]:
        """Returns dict with keys: content, prompt_tokens, completion_tokens, model_deployment."""
        ...
