"""Textbook canon — small frameworks with extensions stated in the published
literature. Every expected value below is sourced so a reviewer can check the
provenance of each answer, not just that two implementations agree.

Sources:
  Dung (1995), "On the acceptability of arguments...", Artificial Intelligence 77.
  Baroni, Caminada & Giacomin (2011), "An introduction to argumentation
  semantics", The Knowledge Engineering Review 26(4):365-410.

Attack convention: the pair (x, y) means "x attacks y".
"""

from __future__ import annotations

import pytest

from argkit.aaf import Af, extensions
from _oracle import oracle_extensions


def _fs(*names) -> frozenset:
    return frozenset(names)


# name -> (Af, {semantics: expected set-of-extensions})
CANON = {
    # A single unattacked argument is accepted under every semantics.
    "unattacked": (
        Af.of(["a"], []),
        {
            "grounded": {_fs("a")},
            "complete": {_fs("a")},
            "preferred": {_fs("a")},
            "stable": {_fs("a")},
        },
    ),
    # A self-attacking argument is never acceptable; no stable extension exists
    # (the empty set fails to attack `a`). Dung (1995), self-defeat.
    "self_attacker": (
        Af.of(["a"], [("a", "a")]),
        {
            "grounded": {_fs()},
            "complete": {_fs()},
            "preferred": {_fs()},
            "stable": set(),
        },
    ),
    # Two mutually attacking arguments: grounded is empty (skeptical), but there
    # are two preferred/stable extensions. Separates complete from preferred:
    # the empty set is complete but not preferred. Dung (1995), Example.
    "two_cycle": (
        Af.of(["a", "b"], [("a", "b"), ("b", "a")]),
        {
            "grounded": {_fs()},
            "complete": {_fs(), _fs("a"), _fs("b")},
            "preferred": {_fs("a"), _fs("b")},
            "stable": {_fs("a"), _fs("b")},
        },
    ),
    # Odd-length cycle: the canonical no-stable-extension case; grounded empty,
    # the only complete extension is empty. Baroni/Caminada/Giacomin (2011).
    "odd_three_cycle": (
        Af.of(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]),
        {
            "grounded": {_fs()},
            "complete": {_fs()},
            "preferred": {_fs()},
            "stable": set(),
        },
    ),
    # Reinstatement: a attacks b, b attacks c. `a` defends `c` by defeating its
    # attacker, so grounded is {a, c}. The payoff structure of the demo.
    "reinstatement_chain": (
        Af.of(["a", "b", "c"], [("a", "b"), ("b", "c")]),
        {
            "grounded": {_fs("a", "c")},
            "complete": {_fs("a", "c")},
            "preferred": {_fs("a", "c")},
            "stable": {_fs("a", "c")},
        },
    ),
    # Even-length cycle: grounded empty, two stable extensions {a,c} and {b,d}.
    # Baroni/Caminada/Giacomin (2011).
    "even_four_cycle": (
        Af.of(["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")]),
        {
            "grounded": {_fs()},
            "complete": {_fs(), _fs("a", "c"), _fs("b", "d")},
            "preferred": {_fs("a", "c"), _fs("b", "d")},
            "stable": {_fs("a", "c"), _fs("b", "d")},
        },
    ),
}

CASES = [
    (name, semantics, expected)
    for name, (_, table) in CANON.items()
    for semantics, expected in table.items()
]


@pytest.mark.parametrize("name,semantics,expected", CASES)
def test_engine_matches_published_extensions(name, semantics, expected):
    af, _ = CANON[name]
    assert extensions(af, semantics) == expected


@pytest.mark.parametrize("name,semantics,expected", CASES)
def test_oracle_also_matches_published_extensions(name, semantics, expected):
    # The published values are independently confirmed by PyArg, so the canon
    # itself is double-locked, not just internally consistent.
    af, _ = CANON[name]
    assert oracle_extensions(af, semantics) == expected
