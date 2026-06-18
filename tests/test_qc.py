"""Deterministic QC checks — the layer that catches LLM population errors before
the engine ever sees them."""

from __future__ import annotations

from datetime import datetime, timezone

from argkit.qc import Severity, blocking_issues, run_deterministic_checks
from argkit.schema import (
    Argument,
    ArgumentGraph,
    AttackType,
    ClaimNode,
    ConflictNode,
    CurationStatus,
    EvidenceNode,
    InferenceNode,
    Provenance,
    Stance,
)

_TS = datetime(2026, 6, 18, tzinfo=timezone.utc)


def _prov(citation="src", status=CurationStatus.CURATED_ACCEPTED):
    return Provenance(generator_model="human-curated", created_at=_TS, confidence=0.9,
                      source_citation=citation, status=status)


def _well_typed_graph(conflicts) -> ArgumentGraph:
    # Argument A: premise A.e (evidence) -> inference A.i -> conclusion A.c (claim).
    arg = Argument(argument_id="A", title="A", premise_ids=["A.e"], inference_id="A.i",
                   conclusion_id="A.c", strength=0.7, stance=Stance.PRO, provenance=_prov())
    other = Argument(argument_id="B", title="B", premise_ids=["B.e"], inference_id="B.i",
                     conclusion_id="B.c", strength=0.7, stance=Stance.CON, provenance=_prov())
    claims = [ClaimNode(node_id="A.c", text="A", provenance=_prov()),
              ClaimNode(node_id="B.c", text="B", provenance=_prov())]
    evidence = [EvidenceNode(node_id="A.e", text="A premise", provenance=_prov()),
                EvidenceNode(node_id="B.e", text="B premise", provenance=_prov())]
    inferences = [InferenceNode(node_id="A.i", text="A rule", premise_ids=["A.e"],
                                conclusion_id="A.c", provenance=_prov()),
                  InferenceNode(node_id="B.i", text="B rule", premise_ids=["B.e"],
                                conclusion_id="B.c", provenance=_prov())]
    return ArgumentGraph(title="t", root_claim_id="A.c", claims=claims, evidence=evidence,
                         inferences=inferences, arguments=[arg, other], conflicts=conflicts)


def _conflict(attack_type, target_node_id, source="B", target="A"):
    return ConflictNode(conflict_id="k", attack_type=attack_type, source_argument_id=source,
                        target_argument_id=target, target_node_id=target_node_id,
                        provenance=_prov())


def test_correctly_typed_conflicts_have_no_blocking_issues():
    graph = _well_typed_graph([
        _conflict(AttackType.UNDERMINE, "A.e"),
        _conflict(AttackType.UNDERCUT, "A.i"),
        _conflict(AttackType.REBUT, "A.c"),
    ])
    assert blocking_issues(graph) == []


def test_mistyped_attack_is_flagged():
    # Undercut must hit an inference node, not a claim.
    graph = _well_typed_graph([_conflict(AttackType.UNDERCUT, "A.c")])
    kinds = {i.kind for i in run_deterministic_checks(graph)}
    assert "attack_type_mismatch" in kinds


def test_self_attack_is_flagged():
    graph = _well_typed_graph([_conflict(AttackType.REBUT, "A.c", source="A", target="A")])
    assert any(i.kind == "self_attack" for i in blocking_issues(graph))


def test_dangling_target_is_flagged():
    graph = _well_typed_graph([_conflict(AttackType.REBUT, "A.c", target="ZZZ")])
    assert any(i.kind == "dangling_target" for i in blocking_issues(graph))


def test_target_node_must_belong_to_target_argument():
    # B.c is a claim, but it is not part of argument A.
    graph = _well_typed_graph([_conflict(AttackType.REBUT, "B.c")])
    assert any(i.kind == "target_node_not_in_argument" for i in blocking_issues(graph))


def test_duplicate_conflict_is_a_warning():
    graph = _well_typed_graph([
        _conflict(AttackType.REBUT, "A.c"),
        _conflict(AttackType.REBUT, "A.c"),
    ])
    issues = run_deterministic_checks(graph)
    assert any(i.kind == "duplicate_conflict" and i.severity == Severity.WARNING for i in issues)
