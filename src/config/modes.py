from __future__ import annotations

from src.config.settings import settings


def require_mock_for_tests() -> None:
    """Call at test collection time to guarantee no live calls."""
    if not settings.is_mock:
        raise RuntimeError(
            "Tests must run with MOCK_LLM=true and EXTERNAL_CLIENT_MODE=mock. "
            "Live cloud calls are not allowed in the test suite."
        )
