from __future__ import annotations

import hashlib
import json
from typing import Any


def compute_input_hash(data: dict[str, Any]) -> str:
    """Compute a deterministic SHA-256 hash of the input data."""
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()
