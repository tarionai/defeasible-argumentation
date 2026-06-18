"""Thin ASPIC+-flavored structured layer.

This is deliberately *not* full ASPIC+: there is no strict-rule closure, no
multi-step rule chaining, and no rationality-postulate guarantee. It implements
exactly one thing correctly — turning typed conflicts into Dung defeat edges via
a stated preference rule — and stops there. The honesty boundary is the point.

Defeat rule (stated verbatim, kept simple):
  * An attack from A onto B succeeds as a *defeat* unless B is strictly
    preferred to A.
  * An *undercut* always defeats, regardless of preference: you cannot
    out-prefer an attack on the inference rule itself (standard ASPIC+).

Preferences are explicit, curator-asserted `PreferenceNode`s — not silently
derived from a confidence number. Argument `strength` is recorded for curation
rationale and display; promoting it to an automated preference policy is a
documented future option, kept out of the shipped mapping on purpose
(deterministic, inspectable, curator-owned).
"""

from __future__ import annotations

from argkit.aaf import Af
from argkit.schema import AbstractAttack, ArgumentGraph, AttackType, ConflictNode


def is_strictly_preferred(graph: ArgumentGraph, stronger: str, weaker: str,
                          *, use_preferences: bool = True) -> bool:
    """True when `stronger` is strictly preferred to `weaker` by an explicit,
    one-directional `PreferenceNode`."""
    if not use_preferences:
        return False
    asserted = {(p.preferred_argument_id, p.dispreferred_argument_id)
                for p in graph.preferences}
    return (stronger, weaker) in asserted and (weaker, stronger) not in asserted


def _is_defeat(graph: ArgumentGraph, conflict: ConflictNode,
               *, use_preferences: bool) -> bool:
    if conflict.attack_type == AttackType.UNDERCUT:
        return True
    target_preferred = is_strictly_preferred(
        graph, conflict.target_argument_id, conflict.source_argument_id,
        use_preferences=use_preferences,
    )
    return not target_preferred


def derive_attacks(graph: ArgumentGraph, *, use_preferences: bool = True) -> list[AbstractAttack]:
    """Map every conflict that succeeds as a defeat to an abstract attack edge.
    Order follows the conflict list, so the result is deterministic."""
    attacks: list[AbstractAttack] = []
    for conflict in graph.conflicts:
        if not _is_defeat(graph, conflict, use_preferences=use_preferences):
            continue
        attacks.append(AbstractAttack(
            attacker_argument_id=conflict.source_argument_id,
            attacked_argument_id=conflict.target_argument_id,
            origin_conflict_id=conflict.conflict_id,
            note=f"{conflict.attack_type.value} succeeds as defeat",
        ))
    return attacks


def live_attacks(graph: ArgumentGraph, *, use_preferences: bool = True) -> list[AbstractAttack]:
    """Derived attacks restricted to curator-accepted arguments — the edges that
    actually enter the framework. Rejected candidates never attack the graph."""
    accepted = {a.argument_id for a in graph.accepted_arguments()}
    return [a for a in derive_attacks(graph, use_preferences=use_preferences)
            if a.attacker_argument_id in accepted and a.attacked_argument_id in accepted]


def to_af(graph: ArgumentGraph, *, use_preferences: bool = True) -> Af:
    """Collapse the curated graph to the abstract framework the engine runs on:
    accepted arguments as atomic nodes, their defeats as attack edges."""
    accepted = {a.argument_id for a in graph.accepted_arguments()}
    edges = [(a.attacker_argument_id, a.attacked_argument_id)
             for a in live_attacks(graph, use_preferences=use_preferences)]
    return Af.of(accepted, edges)
