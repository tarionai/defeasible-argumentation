"""Deploy guard — the hard invariant that makes a subtly-wrong live site
structurally impossible.

It recomputes the *shipped* artifact's extensions with the published library and
asserts they equal the values the site will render. It also asserts the
committed artifact is byte-identical to a fresh build and that its hash matches
SHA256SUMS. If any of these fail, CI fails and nothing deploys.
"""

from __future__ import annotations

import hashlib
import json

from argkit.aaf import SEMANTICS, Af
from argkit.build import ARTIFACT_PATH, SUMS_PATH, build_artifact, render_json
from _oracle import oracle_extensions


def _load_artifact() -> dict:
    return json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))


def _af_from_artifact(artifact: dict) -> Af:
    accepted = [a["argument_id"] for a in artifact["graph"]["arguments"]
                if a["provenance"]["status"] == "curated_accepted"]
    edges = [(x["attacker_argument_id"], x["attacked_argument_id"])
             for x in artifact["abstract_attacks"]]
    return Af.of(accepted, edges)


def _as_extension_set(serialized) -> set:
    return {frozenset(extension) for extension in serialized}


def test_committed_artifact_is_a_fresh_deterministic_build():
    assert ARTIFACT_PATH.read_text(encoding="utf-8") == render_json(build_artifact())


def test_artifact_hash_matches_sums_file():
    digest = hashlib.sha256(ARTIFACT_PATH.read_bytes()).hexdigest()
    recorded = SUMS_PATH.read_text(encoding="utf-8").split()[0]
    assert digest == recorded


def test_shipped_extensions_equal_pyarg_recompute():
    artifact = _load_artifact()
    af = _af_from_artifact(artifact)
    for semantics in SEMANTICS:
        shipped = _as_extension_set(artifact["extensions"][semantics])
        assert oracle_extensions(af, semantics) == shipped, semantics


def test_build_is_byte_reproducible():
    assert render_json(build_artifact()) == render_json(build_artifact())
