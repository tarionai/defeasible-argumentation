"""Export: a deterministic briefing that is the source of truth, plus an optional
LLM-polished prose layer that is explicitly *not* the authority.

The deterministic briefing is templated from the curated graph and the computed
grounded extension. No model can change its verdict. The polish step only
rewrites that text for a lay reader; the structured version is always shown
alongside it as ground truth.
"""

from __future__ import annotations

from argkit.aaf import Af, grounded_extension, grounded_labelling
from argkit.schema import ArgumentGraph
from argkit.structured import to_af


def _title(graph: ArgumentGraph, argument_id: str) -> str:
    argument = graph.argument(argument_id)
    return argument.title if argument else argument_id


def root_claim_status(graph: ArgumentGraph, labels: dict[str, str]) -> str:
    """Status of the root claim: accepted if any accepted argument concluding it
    is in the grounded extension; rejected if all are out; otherwise undecided."""
    carriers = [a.argument_id for a in graph.accepted_arguments()
                if a.conclusion_id == graph.root_claim_id]
    statuses = {labels.get(a, "undecided") for a in carriers}
    if "accepted" in statuses:
        return "accepted"
    if "undecided" in statuses:
        return "undecided"
    return "rejected"


def grounded_summary(graph: ArgumentGraph, *, use_preferences: bool = True) -> dict:
    """Structured grounded verdict over the live framework."""
    af = to_af(graph, use_preferences=use_preferences)
    labels = grounded_labelling(af)
    buckets: dict[str, list[str]] = {"accepted": [], "rejected": [], "undecided": []}
    for argument_id in sorted(af.arguments):
        buckets[labels[argument_id]].append(argument_id)
    return {
        "root_claim_id": graph.root_claim_id,
        "root_status": root_claim_status(graph, labels),
        "accepted": buckets["accepted"],
        "rejected": buckets["rejected"],
        "undecided": buckets["undecided"],
    }


def _defeater_lines(graph: ArgumentGraph, af: Af, labels: dict[str, str]) -> list[str]:
    root_arguments = [a.argument_id for a in graph.accepted_arguments()
                      if a.conclusion_id == graph.root_claim_id]
    lines = []
    for root in root_arguments:
        for attacker in sorted(x for (x, y) in af.attacks if y == root):
            verdict = "defeated" if labels[attacker] == "rejected" else "standing"
            lines.append(f"  - {attacker} ({_title(graph, attacker)}): {verdict}")
    return lines


def deterministic_briefing(graph: ArgumentGraph, *, use_preferences: bool = True) -> str:
    """The authoritative briefing, rendered from structure — never from a model."""
    af = to_af(graph, use_preferences=use_preferences)
    labels = grounded_labelling(af)
    summary = grounded_summary(graph, use_preferences=use_preferences)
    lines = [
        f"Claim ({graph.root_claim_id}): {root_claim_text(graph)}",
        "",
        f"Under grounded (skeptical) semantics, the claim is: {summary['root_status'].upper()}.",
        f"Accepted arguments: {', '.join(summary['accepted']) or '(none)'}.",
        f"Rejected arguments: {', '.join(summary['rejected']) or '(none)'}.",
        f"Undecided arguments: {', '.join(summary['undecided']) or '(none)'}.",
        "",
        "Attacks on the claim's supporting argument, and whether each is itself defeated:",
        *_defeater_lines(graph, af, labels),
    ]
    return "\n".join(lines)


def root_claim_text(graph: ArgumentGraph) -> str:
    claim = next((c for c in graph.claims if c.node_id == graph.root_claim_id), None)
    return claim.text if claim else graph.root_claim_id


def polish_briefing(client, briefing: str) -> str:
    """Optional readability layer (keyed). The structured briefing remains the
    authority; this is shown only as a lay-reader rewrite."""
    prompt = ("Rewrite the following structured argument briefing in plain language for a "
              "non-technical reader. Do not change any verdict or add new claims.\n\n" + briefing)
    return client.complete(prompt)
