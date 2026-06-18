"""Dung abstract argumentation — the verified semantics core.

Reference: P. M. Dung, "On the acceptability of arguments and its fundamental
role in nonmonotonic reasoning, logic programming and n-person games,"
Artificial Intelligence 77 (1995) 321-357.

Every function here is a pure transformation over an immutable `Af`. There is
no I/O, no randomness, no model call. This is deliberate: the engine is the one
surface a computational-argumentation specialist will scrutinize hardest, and
the whole demo's deploy guard recomputes against a published library (PyArg) to
prove these answers are right. Brute-force enumeration is used for the
exponential semantics — for the small frameworks here it is fast enough, and a
reviewer can confirm it is correct by reading it, which a clever solver would
not allow.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

SEMANTICS = ("grounded", "complete", "preferred", "stable")


@dataclass(frozen=True)
class Af:
    """An abstract argumentation framework.

    arguments: the atomic argument identifiers.
    attacks:   directed edges; the pair (x, y) reads "x attacks y".
    """

    arguments: frozenset[str]
    attacks: frozenset[tuple[str, str]]

    @staticmethod
    def of(arguments, attacks) -> "Af":
        """Build from any iterables; normalizes to frozensets."""
        return Af(frozenset(arguments), frozenset((x, y) for x, y in attacks))


def attackers(af: Af, argument: str) -> frozenset[str]:
    """The arguments that attack `argument`."""
    return frozenset(x for (x, y) in af.attacks if y == argument)


def is_conflict_free(af: Af, candidate) -> bool:
    """True when no member of the set attacks another member."""
    members = set(candidate)
    return not any(x in members and y in members for (x, y) in af.attacks)


def is_acceptable(af: Af, argument: str, candidate) -> bool:
    """Dung acceptability: the set defends `argument` because every attacker of
    it is itself attacked by some member of the set."""
    members = set(candidate)
    return all(any((defender, attacker) in af.attacks for defender in members)
               for attacker in attackers(af, argument))


def characteristic_operator(af: Af, candidate) -> frozenset[str]:
    """F(S): every argument the set defends. Grounded is its least fixed point."""
    return frozenset(a for a in af.arguments if is_acceptable(af, a, candidate))


def grounded_extension(af: Af) -> frozenset[str]:
    """Least fixed point of F from the empty set.

    F is monotone, so iterating from the empty set yields a non-decreasing
    sequence whose limit is the least fixed point. Grounded is unique,
    polynomial-time, and skeptical — the safety-appropriate default.
    """
    current: frozenset[str] = frozenset()
    while True:
        following = characteristic_operator(af, current)
        if following == current:
            return current
        current = following


def grounded_labelling(af: Af) -> dict[str, str]:
    """Label each argument accepted / rejected / undecided under grounded
    semantics (the Caminada in / out / undec labelling)."""
    grounded = grounded_extension(af)
    labels: dict[str, str] = {}
    for argument in af.arguments:
        if argument in grounded:
            labels[argument] = "accepted"
        elif any((member, argument) in af.attacks for member in grounded):
            labels[argument] = "rejected"
        else:
            labels[argument] = "undecided"
    return labels


def _all_subsets(af: Af):
    """Yield every subset of the arguments as a frozenset (sorted for
    determinism). Used by the exponential semantics below."""
    items = sorted(af.arguments)
    for size in range(len(items) + 1):
        for combo in combinations(items, size):
            yield frozenset(combo)


def is_admissible(af: Af, candidate) -> bool:
    """Conflict-free and self-defending: S subset of F(S)."""
    members = frozenset(candidate)
    return is_conflict_free(af, members) and members <= characteristic_operator(af, members)


def admissible_sets(af: Af) -> set[frozenset[str]]:
    """All admissible sets (includes the empty set, always admissible)."""
    return {s for s in _all_subsets(af) if is_admissible(af, s)}


def complete_extensions(af: Af) -> set[frozenset[str]]:
    """Conflict-free fixed points of F: S = F(S). A complete extension contains
    exactly the arguments it defends."""
    return {s for s in _all_subsets(af)
            if is_conflict_free(af, s) and characteristic_operator(af, s) == s}


def preferred_extensions(af: Af) -> set[frozenset[str]]:
    """The subset-maximal admissible sets."""
    admissible = admissible_sets(af)
    return {s for s in admissible if not any(s < other for other in admissible)}


def stable_extensions(af: Af) -> set[frozenset[str]]:
    """Conflict-free sets that attack every argument outside the set."""
    result: set[frozenset[str]] = set()
    for members in _all_subsets(af):
        if not is_conflict_free(af, members):
            continue
        outside = af.arguments - members
        if all(any((member, other) in af.attacks for member in members) for other in outside):
            result.add(members)
    return result


def extensions(af: Af, semantics: str) -> set[frozenset[str]]:
    """Public dispatch. Grounded is normalized to a one-element set so all four
    semantics share the `set of extensions` shape the differential harness and
    deploy guard compare on."""
    if semantics == "grounded":
        return {grounded_extension(af)}
    if semantics == "complete":
        return complete_extensions(af)
    if semantics == "preferred":
        return preferred_extensions(af)
    if semantics == "stable":
        return stable_extensions(af)
    raise ValueError(f"unknown semantics: {semantics!r}")
