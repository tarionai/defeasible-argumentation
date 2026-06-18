"""Differential testing against PyArg — the headline correctness claim.

The argkit engine and the published library must return *identical* extension
sets for grounded, complete, preferred, and stable, on:

  - the full textbook canon, and
  - 1,000 randomly generated small frameworks (a fixed seed makes the corpus
    reproducible).

If a single framework disagrees, the misunderstanding is in the core and
everything built on top of it is suspect — so this test gates the build.
"""

from __future__ import annotations

import random

import pytest

from argkit.aaf import Af, SEMANTICS, extensions
from _oracle import oracle_extensions
from test_aaf_textbook import CANON

NUM_RANDOM_FRAMEWORKS = 1000
MAX_ARGUMENTS = 12
EDGE_PROBABILITY = 0.3
SEED = 20260618


def _random_af(rng: random.Random) -> Af:
    size = rng.randint(1, MAX_ARGUMENTS)
    names = [f"x{i}" for i in range(size)]
    attacks = [
        (a, b)
        for a in names
        for b in names
        if rng.random() < EDGE_PROBABILITY  # self-attacks included on purpose
    ]
    return Af.of(names, attacks)


def _random_corpus() -> list[Af]:
    rng = random.Random(SEED)
    return [_random_af(rng) for _ in range(NUM_RANDOM_FRAMEWORKS)]


@pytest.mark.parametrize("semantics", SEMANTICS)
def test_engine_agrees_with_pyarg_on_textbook_canon(semantics):
    for name, (af, _) in CANON.items():
        assert extensions(af, semantics) == oracle_extensions(af, semantics), name


@pytest.mark.parametrize("semantics", SEMANTICS)
def test_engine_agrees_with_pyarg_on_random_corpus(semantics):
    for index, af in enumerate(_random_corpus()):
        mine = extensions(af, semantics)
        theirs = oracle_extensions(af, semantics)
        assert mine == theirs, (
            f"divergence on framework {index} under {semantics}\n"
            f"  arguments={sorted(af.arguments)}\n"
            f"  attacks={sorted(af.attacks)}\n"
            f"  argkit={sorted(map(sorted, mine))}\n"
            f"  pyarg={sorted(map(sorted, theirs))}"
        )
