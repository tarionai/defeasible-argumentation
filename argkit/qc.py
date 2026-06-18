"""Quality control over the unreliable population step.

Two layers, deterministic first:

  1. Deterministic checks (no model, run first). Rules that catch the failure
     modes an LLM produces: a mis-typed attack, a dangling edge, a self-attack,
     a duplicate, a missing citation. Anything that fails is demoted to a
     candidate and routed to human review — the engine never sees it.
  2. Two-model cross-check (optional, keyed). A second model independently
     verifies each candidate. Agreement promotes to `cross_checked`;
     disagreement routes to the review queue.

This module owns only the deterministic layer plus the *interface* for the
cross-check; the model adapters live in `pipeline.py`. The deterministic layer
is the load-bearing one and needs no API key, so it always runs.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from argkit.schema import ArgumentGraph, AttackType, ConflictNode

# Which node kind each attack type must target (ASPIC+).
_REQUIRED_TARGET_KIND = {
    AttackType.UNDERMINE: "evidence",
    AttackType.UNDERCUT: "inference",
    AttackType.REBUT: "claim",
}


class Severity(str, Enum):
    BLOCKING = "blocking"   # cannot enter the framework
    WARNING = "warning"     # enters, but flagged for the curator


class CheckIssue(BaseModel):
    model_config = {"frozen": True}
    kind: str
    severity: Severity
    target_id: str
    message: str


def _argument_node_ids(graph: ArgumentGraph, argument_id: str) -> set[str]:
    argument = graph.argument(argument_id)
    if argument is None:
        return set()
    return {*argument.premise_ids, argument.inference_id, argument.conclusion_id}


def _check_conflict(graph: ArgumentGraph, conflict: ConflictNode) -> list[CheckIssue]:
    issues: list[CheckIssue] = []
    if graph.argument(conflict.source_argument_id) is None:
        issues.append(CheckIssue(kind="dangling_source", severity=Severity.BLOCKING,
                                 target_id=conflict.conflict_id,
                                 message=f"unknown source argument {conflict.source_argument_id}"))
    if graph.argument(conflict.target_argument_id) is None:
        issues.append(CheckIssue(kind="dangling_target", severity=Severity.BLOCKING,
                                 target_id=conflict.conflict_id,
                                 message=f"unknown target argument {conflict.target_argument_id}"))
    if conflict.source_argument_id == conflict.target_argument_id:
        issues.append(CheckIssue(kind="self_attack", severity=Severity.BLOCKING,
                                 target_id=conflict.conflict_id,
                                 message="an argument may not attack itself"))
    issues.extend(_check_attack_typing(graph, conflict))
    return issues


def _check_attack_typing(graph: ArgumentGraph, conflict: ConflictNode) -> list[CheckIssue]:
    required = _REQUIRED_TARGET_KIND[conflict.attack_type]
    kind = graph.node_kind(conflict.target_node_id)
    if kind != required:
        return [CheckIssue(kind="attack_type_mismatch", severity=Severity.BLOCKING,
                           target_id=conflict.conflict_id,
                           message=f"{conflict.attack_type.value} must target a {required} "
                                   f"node, but {conflict.target_node_id} is {kind}")]
    if conflict.target_node_id not in _argument_node_ids(graph, conflict.target_argument_id):
        return [CheckIssue(kind="target_node_not_in_argument", severity=Severity.BLOCKING,
                           target_id=conflict.conflict_id,
                           message=f"{conflict.target_node_id} is not part of "
                                   f"{conflict.target_argument_id}")]
    return []


def _check_duplicates(graph: ArgumentGraph) -> list[CheckIssue]:
    seen: set[tuple] = set()
    issues: list[CheckIssue] = []
    for conflict in graph.conflicts:
        key = (conflict.source_argument_id, conflict.target_argument_id,
               conflict.attack_type, conflict.target_node_id)
        if key in seen:
            issues.append(CheckIssue(kind="duplicate_conflict", severity=Severity.WARNING,
                                     target_id=conflict.conflict_id,
                                     message="duplicate of an earlier conflict"))
        seen.add(key)
    return issues


def _check_citations(graph: ArgumentGraph) -> list[CheckIssue]:
    return [CheckIssue(kind="missing_citation", severity=Severity.WARNING,
                       target_id=node.node_id,
                       message="evidence node has no source citation")
            for node in graph.evidence if not node.provenance.source_citation]


def run_deterministic_checks(graph: ArgumentGraph) -> list[CheckIssue]:
    """Every rule that needs no model. Blocking issues must be cleared before the
    graph can be safely reduced to a framework."""
    issues: list[CheckIssue] = []
    for conflict in graph.conflicts:
        issues.extend(_check_conflict(graph, conflict))
    issues.extend(_check_duplicates(graph))
    issues.extend(_check_citations(graph))
    return issues


def blocking_issues(graph: ArgumentGraph) -> list[CheckIssue]:
    return [issue for issue in run_deterministic_checks(graph)
            if issue.severity == Severity.BLOCKING]
