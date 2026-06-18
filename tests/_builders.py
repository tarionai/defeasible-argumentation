"""Compact constructors for typed graph objects, so tests can build small
frameworks without node boilerplate."""

from __future__ import annotations

from datetime import datetime, timezone

from argkit.schema import (
    Argument,
    ArgumentGraph,
    AttackType,
    ConflictNode,
    CurationStatus,
    PreferenceNode,
    Provenance,
    Stance,
)

_TS = datetime(2026, 6, 18, tzinfo=timezone.utc)


def prov(status: CurationStatus = CurationStatus.CURATED_ACCEPTED, **kwargs) -> Provenance:
    return Provenance(generator_model="human-curated", created_at=_TS,
                      confidence=0.9, status=status, **kwargs)


def make_arg(argument_id: str, *, strength: float = 0.7,
             status: CurationStatus = CurationStatus.CURATED_ACCEPTED,
             stance: Stance = Stance.NEUTRAL) -> Argument:
    return Argument(
        argument_id=argument_id, title=argument_id,
        premise_ids=[f"{argument_id}.e"], inference_id=f"{argument_id}.i",
        conclusion_id=f"{argument_id}.c", strength=strength, stance=stance,
        provenance=prov(status=status),
    )


def make_conflict(conflict_id: str, attack_type: AttackType, source: str, target: str,
                  target_node_id: str) -> ConflictNode:
    return ConflictNode(
        conflict_id=conflict_id, attack_type=attack_type,
        source_argument_id=source, target_argument_id=target,
        target_node_id=target_node_id, provenance=prov(),
    )


def make_pref(preference_id: str, preferred: str, dispreferred: str,
              rationale: str = "test") -> PreferenceNode:
    return PreferenceNode(
        preference_id=preference_id, preferred_argument_id=preferred,
        dispreferred_argument_id=dispreferred, rationale=rationale, provenance=prov(),
    )


def make_graph(arguments, conflicts, preferences=()) -> ArgumentGraph:
    return ArgumentGraph(
        title="test", root_claim_id="C0.c", claims=[], evidence=[], inferences=[],
        arguments=list(arguments), conflicts=list(conflicts),
        preferences=list(preferences),
    )
