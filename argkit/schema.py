"""Typed knowledge-graph schema (Pydantic v2), with vocabulary borrowed from the
Argument Interchange Format (AIF) so the structure reads as literate to the
field:

  ClaimNode      AIF I-node   a proposition (incl. the root claim).
  EvidenceNode   AIF I-node   a premise / supporting datum, with a citation.
  InferenceNode  AIF RA-node  a defeasible rule application (evidence -> claim).
  ConflictNode   AIF CA-node  a typed attack instance (undermine/undercut/rebut).
  PreferenceNode AIF PA-node  a stated preference between two arguments.
  Argument                    the abstract unit for Dung: premises+inference+conclusion.
  AbstractAttack              a derived defeat edge — the only input to the engine.

Every node and edge carries `Provenance`. The status field is a deterministic
state machine; only a human curation step may write `curated_*`. Timestamps are
supplied by data (never `now()`), so the assembled artifact is byte-reproducible
and therefore hash-stampable.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AttackType(str, Enum):
    """The three ASPIC+ attack types, by what they target."""

    UNDERMINE = "undermine"  # targets a premise (an EvidenceNode)
    UNDERCUT = "undercut"    # targets the defeasible inference (an InferenceNode)
    REBUT = "rebut"          # targets the conclusion (a ClaimNode)


class CurationStatus(str, Enum):
    """Promotion state machine. candidate -> cross_checked -> curated_*.
    Only the human curation pass writes the curated_* terminal states."""

    CANDIDATE = "candidate"
    CROSS_CHECKED = "cross_checked"
    CURATED_ACCEPTED = "curated_accepted"
    CURATED_REJECTED = "curated_rejected"


class Stance(str, Enum):
    """Display-only: an argument's stance toward the root claim."""

    PRO = "pro"
    CON = "con"
    NEUTRAL = "neutral"


class Provenance(BaseModel):
    """Embedded on every node and edge. The audit trail of where each piece of
    the graph came from and whether a human has signed off on it."""

    model_config = ConfigDict(frozen=True)

    generator_model: str = Field(description="e.g. claude-opus-4-8, gpt-*, or 'human-curated'")
    prompt_id: str | None = Field(default=None)
    prompt_sha256: str | None = Field(default=None)
    created_at: datetime
    source_citation: str | None = Field(default=None)
    confidence: float = Field(ge=0.0, le=1.0)
    status: CurationStatus = CurationStatus.CANDIDATE
    curator_note: str | None = Field(default=None)


class _Node(BaseModel):
    model_config = ConfigDict(frozen=True)
    node_id: str
    text: str
    provenance: Provenance


class ClaimNode(_Node):
    """A proposition. The root claim and every argument conclusion is one."""


class EvidenceNode(_Node):
    """A premise / supporting datum. `source_citation` lives on its provenance."""


class InferenceNode(_Node):
    """A defeasible rule application linking premises to a conclusion."""

    premise_ids: list[str]
    conclusion_id: str


class Argument(BaseModel):
    """The abstract unit Dung semantics runs over: premises + one defeasible
    inference + a conclusion, collapsed to an atomic id with a strength used by
    the preference -> defeat rule."""

    model_config = ConfigDict(frozen=True)
    argument_id: str
    title: str
    premise_ids: list[str]
    inference_id: str
    conclusion_id: str
    strength: float = Field(ge=0.0, le=1.0)
    stance: Stance = Stance.NEUTRAL
    provenance: Provenance


class ConflictNode(BaseModel):
    """A typed attack from one argument onto a specific node of another. The
    deterministic QC check enforces that `attack_type` matches the targeted
    node's kind (undermine->evidence, undercut->inference, rebut->claim)."""

    model_config = ConfigDict(frozen=True)
    conflict_id: str
    attack_type: AttackType
    source_argument_id: str
    target_argument_id: str
    target_node_id: str
    provenance: Provenance


class PreferenceNode(BaseModel):
    """A stated preference: `preferred_argument_id` is at least as strong as
    `dispreferred_argument_id`. Curatorial judgment, not a derived fact."""

    model_config = ConfigDict(frozen=True)
    preference_id: str
    preferred_argument_id: str
    dispreferred_argument_id: str
    rationale: str
    provenance: Provenance


class AbstractAttack(BaseModel):
    """A derived defeat edge: the only input to the semantics engine. Carries the
    conflict it came from so the abstract graph stays traceable to the structure."""

    model_config = ConfigDict(frozen=True)
    attacker_argument_id: str
    attacked_argument_id: str
    origin_conflict_id: str
    note: str | None = None


class ArgumentGraph(BaseModel):
    """The whole curated graph — the single source of truth that serializes to
    the frozen artifact."""

    model_config = ConfigDict(frozen=True)
    title: str
    root_claim_id: str
    claims: list[ClaimNode]
    evidence: list[EvidenceNode]
    inferences: list[InferenceNode]
    arguments: list[Argument]
    conflicts: list[ConflictNode]
    preferences: list[PreferenceNode] = Field(default_factory=list)

    def node_kind(self, node_id: str) -> str | None:
        """The kind of a node id: 'claim' | 'evidence' | 'inference' | None."""
        if any(c.node_id == node_id for c in self.claims):
            return "claim"
        if any(e.node_id == node_id for e in self.evidence):
            return "evidence"
        if any(i.node_id == node_id for i in self.inferences):
            return "inference"
        return None

    def argument(self, argument_id: str) -> Argument | None:
        return next((a for a in self.arguments if a.argument_id == argument_id), None)

    def accepted_arguments(self) -> list[Argument]:
        """Arguments a curator accepted — the ones that compose the live graph."""
        return [a for a in self.arguments
                if a.provenance.status == CurationStatus.CURATED_ACCEPTED]
