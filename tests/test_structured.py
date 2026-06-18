"""Unit tests for the structured -> abstract mapping (the ASPIC+-flavored defeat
rule). The semantics engine is verified elsewhere; here we verify only that
conflicts become the *right* defeat edges."""

from __future__ import annotations

from argkit.aaf import grounded_extension
from argkit.schema import AttackType
from argkit.structured import derive_attacks, is_strictly_preferred, to_af
from _builders import make_arg, make_conflict, make_graph, make_pref


def _edges(attacks) -> set:
    return {(a.attacker_argument_id, a.attacked_argument_id) for a in attacks}


def test_undercut_always_defeats_even_when_target_is_preferred():
    # Even with an explicit preference protecting the target, an undercut on the
    # inference rule still defeats — you cannot out-prefer it.
    graph = make_graph(
        arguments=[make_arg("A"), make_arg("B")],
        conflicts=[make_conflict("k1", AttackType.UNDERCUT, "B", "A", "A.i")],
        preferences=[make_pref("p1", "A", "B")],
    )
    assert _edges(derive_attacks(graph)) == {("B", "A")}


def test_rebut_is_suppressed_when_target_strictly_preferred():
    graph = make_graph(
        arguments=[make_arg("A"), make_arg("B")],
        conflicts=[make_conflict("k1", AttackType.REBUT, "B", "A", "A.c")],
        preferences=[make_pref("p1", "A", "B")],  # A preferred over its attacker B
    )
    assert _edges(derive_attacks(graph)) == set()  # B's rebut fails as a defeat


def test_rebut_succeeds_without_a_protecting_preference():
    graph = make_graph(
        arguments=[make_arg("A"), make_arg("B")],
        conflicts=[make_conflict("k1", AttackType.REBUT, "B", "A", "A.c")],
    )
    assert _edges(derive_attacks(graph)) == {("B", "A")}


def test_use_preferences_false_ignores_the_relation():
    graph = make_graph(
        arguments=[make_arg("A"), make_arg("B")],
        conflicts=[make_conflict("k1", AttackType.REBUT, "B", "A", "A.c")],
        preferences=[make_pref("p1", "A", "B")],
    )
    assert _edges(derive_attacks(graph, use_preferences=False)) == {("B", "A")}


def test_preference_is_load_bearing_on_a_two_cycle():
    # p and c mutually rebut (contradictory conclusions). With the preference,
    # only p->c is a defeat, so grounded accepts p. Without it, p<->c is a
    # 2-cycle and grounded accepts neither. The preference changes the verdict.
    arguments = [make_arg("p"), make_arg("c")]
    conflicts = [
        make_conflict("k1", AttackType.REBUT, "p", "c", "c.c"),
        make_conflict("k2", AttackType.REBUT, "c", "p", "p.c"),
    ]
    preferences = [make_pref("p1", "p", "c")]

    with_pref = make_graph(arguments, conflicts, preferences)
    without_pref = make_graph(arguments, conflicts)

    assert grounded_extension(to_af(with_pref)) == frozenset({"p"})
    assert grounded_extension(to_af(without_pref)) == frozenset()


def test_strict_preference_requires_one_directional_assertion():
    graph = make_graph(
        arguments=[make_arg("A"), make_arg("B")],
        conflicts=[],
        preferences=[make_pref("p1", "A", "B"), make_pref("p2", "B", "A")],
    )
    # Mutually asserted preference is not strict in either direction.
    assert not is_strictly_preferred(graph, "A", "B")
    assert not is_strictly_preferred(graph, "B", "A")
