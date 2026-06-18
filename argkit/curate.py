"""Human-in-the-loop curation.

A curator reviews the borderline candidates — those that failed a deterministic
check, drew a cross-check disagreement, or carry low confidence — and accepts,
edits, or rejects each. The decision and its note are written into provenance,
moving the argument to a terminal `curated_accepted` / `curated_rejected` state.

Rejected candidates are kept, not deleted: the demo renders them with the
curator's reason, which both demonstrates the value of the gate and keeps the
audit trail honest about what the LLM proposed and what a human threw out.
"""

from __future__ import annotations

from pydantic import BaseModel

from argkit.schema import Argument, ArgumentGraph, CurationStatus


class CurationDecision(BaseModel):
    model_config = {"frozen": True}
    argument_id: str
    accept: bool
    note: str


def review_queue(graph: ArgumentGraph) -> list[str]:
    """Argument ids still awaiting a human decision (not yet curated)."""
    pending = {CurationStatus.CANDIDATE, CurationStatus.CROSS_CHECKED}
    return [a.argument_id for a in graph.arguments if a.provenance.status in pending]


def _apply(argument: Argument, decision: CurationDecision) -> Argument:
    status = (CurationStatus.CURATED_ACCEPTED if decision.accept
              else CurationStatus.CURATED_REJECTED)
    provenance = argument.provenance.model_copy(
        update={"status": status, "curator_note": decision.note})
    return argument.model_copy(update={"provenance": provenance})


def apply_decisions(graph: ArgumentGraph, decisions: list[CurationDecision]) -> ArgumentGraph:
    """Return a new graph with the curator's decisions written into provenance.
    Arguments without a decision are left untouched."""
    by_id = {d.argument_id: d for d in decisions}
    updated = [_apply(a, by_id[a.argument_id]) if a.argument_id in by_id else a
               for a in graph.arguments]
    return graph.model_copy(update={"arguments": updated})
