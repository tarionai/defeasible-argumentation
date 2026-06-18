"""End-to-end build: curated seed -> frozen, hash-stamped JSON artifact.

This is fully deterministic. It calls no model: the LLM population happened once,
offline, and its curated output is the seed. So `python -m argkit.build`
regenerates byte-identical output, and its SHA-256 matches `SHA256SUMS` — the
property the CI deploy guard depends on. The browser never recomputes anything;
it renders this file.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from argkit import __version__
from argkit.aaf import SEMANTICS, extensions, grounded_extension, grounded_labelling
from argkit.export import deterministic_briefing, grounded_summary
from argkit.qc import blocking_issues, run_deterministic_checks
from argkit.schema import ArgumentGraph
from argkit.seed import build_seed_graph
from argkit.structured import live_attacks, to_af

ARTIFACT_DIR = Path(__file__).resolve().parent.parent / "artifact"
ARTIFACT_PATH = ARTIFACT_DIR / "argument_graph.v1.json"
SUMS_PATH = ARTIFACT_DIR / "SHA256SUMS"
ORACLE = "python-argumentation==2.0.2"


def _serialize_extensions(extension_set) -> list[list[str]]:
    return sorted([sorted(extension) for extension in extension_set])


def _abstract_attacks_payload(graph: ArgumentGraph) -> list[dict]:
    """Live defeat edges, each enriched with the attack type of the conflict it
    came from so the renderer can label edges without re-joining."""
    attack_type = {c.conflict_id: c.attack_type.value for c in graph.conflicts}
    payload = []
    for attack in live_attacks(graph):
        entry = attack.model_dump(mode="json")
        entry["attack_type"] = attack_type.get(attack.origin_conflict_id)
        payload.append(entry)
    return payload


def _preference_demonstration(graph: ArgumentGraph) -> dict:
    with_preferences = grounded_extension(to_af(graph, use_preferences=True))
    without_preferences = grounded_extension(to_af(graph, use_preferences=False))
    return {
        "with_preferences": sorted(with_preferences),
        "without_preferences": sorted(without_preferences),
        "note": "Dropping the one curated preference (D1 > B3) turns B3<->D1 into a 2-cycle; "
                "grounded semantics then leaves the claim undecided. The preference is "
                "load-bearing, and the engine shows it.",
    }


def build_artifact(graph: ArgumentGraph | None = None) -> dict:
    """Assemble the artifact. Raises if any blocking QC issue remains — a graph
    that fails the deterministic checks must never be frozen."""
    graph = graph or build_seed_graph()
    blocking = blocking_issues(graph)
    if blocking:
        raise ValueError(f"blocking QC issues: {[issue.message for issue in blocking]}")
    af = to_af(graph, use_preferences=True)
    return {
        "schema_version": "1.0",
        "engine_version": __version__,
        "title": graph.title,
        "root_claim_id": graph.root_claim_id,
        "generated_by": {"build": "deterministic; no model call at build time", "oracle": ORACLE},
        "graph": graph.model_dump(mode="json"),
        "abstract_attacks": _abstract_attacks_payload(graph),
        "extensions": {name: _serialize_extensions(extensions(af, name)) for name in SEMANTICS},
        "grounded_labelling": grounded_labelling(af),
        "preference_demonstration": _preference_demonstration(graph),
        "briefing": {
            "deterministic": deterministic_briefing(graph),
            "structured": grounded_summary(graph),
        },
        "qc": {"issues": [issue.model_dump(mode="json") for issue in run_deterministic_checks(graph)]},
    }


def render_json(artifact: dict) -> str:
    """Stable serialization — sorted keys, trailing newline — so the bytes (and
    therefore the hash) are reproducible."""
    return json.dumps(artifact, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def write_artifact(artifact: dict | None = None) -> Path:
    # Write raw UTF-8 bytes with LF newlines so the on-disk bytes (and the hash)
    # are identical on Windows and Linux — no platform newline translation.
    artifact = artifact if artifact is not None else build_artifact()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    payload = render_json(artifact).encode("utf-8")
    ARTIFACT_PATH.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    SUMS_PATH.write_bytes(f"{digest}  {ARTIFACT_PATH.name}\n".encode("utf-8"))
    return ARTIFACT_PATH


def main() -> None:
    path = write_artifact()
    print(f"wrote {path}")
    print(SUMS_PATH.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    main()
