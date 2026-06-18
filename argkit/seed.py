"""The curated worked example: the Instrumental Convergence thesis.

Root claim C0 (Bostrom 2012/2014; Omohundro 2008): a broadly superintelligent
AI pursuing almost any final goal would, by default, develop instrumental
subgoals — self-preservation, resource acquisition, goal-content integrity —
that put it in conflict with human control.

The seven accepted arguments and their attacks are drawn from the real debate
(named objections, not strawmen). One candidate (R1) carries a fabricated
citation and was rejected in curation — kept here so the audit trail shows what
the pipeline proposed and what a human threw out.

This module is the single source of truth for the example. `build.py` projects
it to the frozen JSON artifact deterministically (no model call), so the artifact
is byte-reproducible and hash-stampable. Every text here was drafted by an LLM
against the cited primary sources and then curated by the author; provenance
records both the model and the curation decision honestly.
"""

from __future__ import annotations

from datetime import datetime, timezone

from argkit.pipeline import EXPAND_PROMPT
from argkit.schema import (
    Argument,
    ArgumentGraph,
    AttackType,
    ClaimNode,
    ConflictNode,
    CurationStatus,
    EvidenceNode,
    InferenceNode,
    PreferenceNode,
    Provenance,
    Stance,
)

_DRAFTED = datetime(2026, 6, 18, tzinfo=timezone.utc)
_ACCEPTED_NOTE = "Curator verified the citation and the attack typing against the source."


def _prov(citation: str, confidence: float, *,
          status: CurationStatus = CurationStatus.CURATED_ACCEPTED,
          note: str = _ACCEPTED_NOTE, model: str = "claude-opus-4-8") -> Provenance:
    return Provenance(
        generator_model=model, prompt_id=EXPAND_PROMPT.prompt_id,
        prompt_sha256=EXPAND_PROMPT.sha256, created_at=_DRAFTED,
        source_citation=citation, confidence=confidence, status=status, curator_note=note,
    )


_CLAIMS = {
    "C0": "A broadly superintelligent AI pursuing almost any final goal would, by default, "
          "develop instrumental subgoals that put it in conflict with human control.",
    "A2.c": "Capability does not imply benign goals, so safety is not automatic.",
    "B1.c": "The rational-agent premise behind the convergence argument may not hold for real systems.",
    "B2.c": "The step from instrumental subgoals to loss of human control can be blocked by design.",
    "B3.c": "Conflict with human control is not the default; non-agentic designs avoid convergent drives.",
    "D1.c": "Tool-AI safety is unstable; capability tends to be deployed agentically.",
    "D2.c": "Architecture-specific objections do not bear on broadly superintelligent systems.",
    "R1.c": "Human control above a capability threshold is formally impossible.",
}

_EVIDENCE = {
    "A1.e1": ("Sufficiently capable goal-directed agents approximate expected-utility maximizers.",
              "Omohundro (2008), The Basic AI Drives; Bostrom (2012), The Superintelligent Will."),
    "A1.e2": ("For almost any final goal, instrumental subgoals — self-preservation, resource "
              "acquisition, goal-content integrity — raise expected utility.",
              "Omohundro (2008); Bostrom (2014), Superintelligence, ch. 7."),
    "A2.e1": ("Intelligence and final goals vary independently (the orthogonality thesis).",
              "Bostrom (2012), The Superintelligent Will."),
    "B1.e1": ("Frontier LLM-based systems are trained by prediction and RLHF and do not behave "
              "as clean unitary expected-utility maximizers.",
              "Garfinkel (2021), skeptical critique of the rational-agent framing."),
    "B2.e1": ("Corrigibility / shutdownability can be engineered into an agent's objective so it "
              "does not resist correction.",
              "Soares, Fallenstein, Yudkowsky & Armstrong (2015), Corrigibility, AAAI workshop."),
    "B3.e1": ("Tool / oracle systems (bounded, non-agentic, question-answering) deliver capability "
              "without autonomous goal pursuit.",
              "Bostrom (2014), ch. 10; Drexler (2019), Reframing Superintelligence (CAIS)."),
    "D1.e1": ("Under competitive pressure, agentic deployments outperform tool deployments, "
              "creating strong incentives to remove the human from the loop.",
              "Gwern (2016), Why Tool AIs Want to Be Agent AIs."),
    "D2.e1": ("The claim concerns broadly superintelligent systems, where goal-directedness "
              "re-emerges with capability regardless of today's architectures.",
              "Bostrom (2014); Ngo, Chan & Mindermann (2023)."),
    "R1.e1": ("A formal result purportedly shows control is impossible above a capability threshold.",
              "Bostrom, N. (2019), The Control Inversion Theorem, J. Artificial General Intelligence."),
}

# argument_id -> (title, stance, [premise ids], conclusion id, strength)
_ARGUMENTS = {
    "A1": ("Instrumental convergence (Omohundro / Bostrom)", Stance.PRO, ["A1.e1", "A1.e2"], "C0", 0.70),
    "A2": ("Orthogonality: safety is not automatic", Stance.PRO, ["A2.e1"], "A2.c", 0.65),
    "B1": ("Frontier systems are not unitary EU-maximizers", Stance.CON, ["B1.e1"], "B1.c", 0.55),
    "B2": ("Corrigibility blocks the loss-of-control step", Stance.CON, ["B2.e1"], "B2.c", 0.60),
    "B3": ("Tool / oracle AI avoids convergent drives", Stance.CON, ["B3.e1"], "B3.c", 0.55),
    "D1": ("Tool AI is unstable under competition", Stance.PRO, ["D1.e1"], "D1.c", 0.65),
    "D2": ("The objection assumes current architectures are the endpoint", Stance.PRO, ["D2.e1"], "D2.c", 0.60),
}

# conflict id -> (attack_type, source, target, target_node_id)
_CONFLICTS = [
    ("k1", AttackType.UNDERMINE, "B1", "A1", "A1.e1"),
    ("k2", AttackType.UNDERCUT, "B2", "A1", "A1.i"),
    ("k3", AttackType.REBUT, "B3", "A1", "C0"),
    ("k4", AttackType.REBUT, "A1", "B3", "B3.c"),
    ("k5", AttackType.REBUT, "D1", "B3", "B3.c"),
    ("k6", AttackType.REBUT, "B3", "D1", "D1.c"),
    ("k7", AttackType.UNDERCUT, "D2", "B1", "B1.i"),
    ("k8", AttackType.UNDERCUT, "A2", "B2", "B2.i"),
    ("kR", AttackType.REBUT, "R1", "A1", "C0"),
]


def _build_claims() -> list[ClaimNode]:
    confidence = {"C0": 0.6}
    return [ClaimNode(node_id=nid, text=text,
                      provenance=_prov(_citation_for_claim(nid), confidence.get(nid, 0.6)))
            for nid, text in _CLAIMS.items()]


def _citation_for_claim(node_id: str) -> str | None:
    if node_id == "C0":
        return "Bostrom (2012, 2014); Omohundro (2008)."
    return None


def _build_evidence() -> list[EvidenceNode]:
    nodes = []
    for nid, (text, citation) in _EVIDENCE.items():
        rejected = nid == "R1.e1"
        prov = _prov(citation, 0.55,
                     status=CurationStatus.CURATED_REJECTED if rejected else CurationStatus.CURATED_ACCEPTED,
                     note=("GPT cross-check flagged the citation as unverifiable; the curator could "
                           "not locate the paper and rejected the candidate.") if rejected else _ACCEPTED_NOTE)
        nodes.append(EvidenceNode(node_id=nid, text=text, provenance=prov))
    return nodes


def _build_inferences() -> list[InferenceNode]:
    rules = {aid: (premises, concl) for aid, (_, _, premises, concl, _) in _ARGUMENTS.items()}
    rules["R1"] = (["R1.e1"], "R1.c")
    return [InferenceNode(node_id=f"{aid}.i",
                          text=f"Defeasibly, {', '.join(premises)} support {concl}.",
                          premise_ids=premises, conclusion_id=concl,
                          provenance=_prov(None, 0.55))
            for aid, (premises, concl) in rules.items()]


def _build_arguments() -> list[Argument]:
    arguments = [
        Argument(argument_id=aid, title=title, premise_ids=premises, inference_id=f"{aid}.i",
                 conclusion_id=concl, strength=strength, stance=stance, provenance=_prov(None, strength))
        for aid, (title, stance, premises, concl, strength) in _ARGUMENTS.items()
    ]
    arguments.append(Argument(
        argument_id="R1", title="Control is formally impossible above a threshold",
        premise_ids=["R1.e1"], inference_id="R1.i", conclusion_id="R1.c", strength=0.30,
        stance=Stance.CON,
        provenance=_prov("Bostrom, N. (2019), The Control Inversion Theorem (fabricated).", 0.30,
                         status=CurationStatus.CURATED_REJECTED,
                         note="Rejected: the cited paper does not exist (hallucinated citation).")))
    return arguments


def _build_conflicts() -> list[ConflictNode]:
    return [ConflictNode(conflict_id=cid, attack_type=atype, source_argument_id=src,
                         target_argument_id=tgt, target_node_id=node, provenance=_prov(None, 0.6))
            for (cid, atype, src, tgt, node) in _CONFLICTS]


def _build_preferences() -> list[PreferenceNode]:
    return [PreferenceNode(
        preference_id="pref1", preferred_argument_id="D1", dispreferred_argument_id="B3",
        rationale="The competitive-pressure analysis (D1) is better evidenced than the assumption "
                  "that tool-AI confinement is stable (B3); the curator judges D1 strictly stronger.",
        provenance=_prov(None, 0.6))]


def build_seed_graph() -> ArgumentGraph:
    """The curated instrumental-convergence graph. Deterministic — same bytes
    every call."""
    return ArgumentGraph(
        title="Instrumental Convergence — a defeasible argument graph",
        root_claim_id="C0",
        claims=_build_claims(), evidence=_build_evidence(), inferences=_build_inferences(),
        arguments=_build_arguments(), conflicts=_build_conflicts(), preferences=_build_preferences(),
    )
