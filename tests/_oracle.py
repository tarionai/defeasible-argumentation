"""Adapter wrapping PyArg (`python-argumentation`) — the independent oracle.

PyArg is dev/test-only. It never leaks into `argkit`: this module is the single
boundary where its API is touched, and it returns the same `set of frozensets of
names` shape that `argkit.aaf.extensions` returns, so callers compare like with
like.

Caveat handled here: PyArg mutates each `Argument` object's attack lists at
framework construction. Reusing argument objects across frameworks therefore
pollutes results, so fresh objects are built for every framework.
"""

from __future__ import annotations

from argkit.aaf import Af
from py_arg.abstract_argumentation_classes.argument import Argument
from py_arg.abstract_argumentation_classes.defeat import Defeat
from py_arg.abstract_argumentation_classes.abstract_argumentation_framework import (
    AbstractArgumentationFramework,
)
from py_arg.algorithms.semantics.get_grounded_extension import get_grounded_extension
from py_arg.algorithms.semantics.get_complete_extensions import get_complete_extensions
from py_arg.algorithms.semantics.get_preferred_extensions import get_preferred_extensions
from py_arg.algorithms.semantics.get_stable_extensions import get_stable_extensions


def _to_pyarg(af: Af) -> AbstractArgumentationFramework:
    arguments = {name: Argument(name) for name in af.arguments}
    defeats = [Defeat(arguments[x], arguments[y]) for (x, y) in af.attacks]
    return AbstractArgumentationFramework("oracle", list(arguments.values()), defeats)


def _names(extension) -> frozenset:
    return frozenset(argument.name for argument in extension)


def oracle_extensions(af: Af, semantics: str) -> set:
    """Extensions of `af` under `semantics`, computed by PyArg."""
    framework = _to_pyarg(af)
    if semantics == "grounded":
        return {_names(get_grounded_extension(framework))}
    if semantics == "complete":
        return {_names(e) for e in get_complete_extensions(framework)}
    if semantics == "preferred":
        return {_names(e) for e in get_preferred_extensions(framework)}
    if semantics == "stable":
        return {_names(e) for e in get_stable_extensions(framework)}
    raise ValueError(f"unknown semantics: {semantics!r}")
