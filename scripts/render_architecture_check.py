"""Confirms Mermaid file exists and parses."""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    path = Path("docs/architecture.mermaid")
    if not path.exists():
        print("FAIL: docs/architecture.mermaid not found")
        return

    content = path.read_text()
    if "graph TD" not in content:
        print("FAIL: Mermaid file does not contain 'graph TD'")
        return

    required_nodes = ["UI", "API", "GRAPH", "SNOW", "DBX", "AOAI", "OBS", "TEST"]
    missing = [n for n in required_nodes if n + "[" not in content]
    if missing:
        print(f"FAIL: Missing nodes: {missing}")
        return

    print("PASS: docs/architecture.mermaid exists and contains all expected nodes")
    print(f"  File size: {len(content)} bytes")
    print(f"  Lines: {content.count(chr(10)) + 1}")


if __name__ == "__main__":
    main()
