"""LLM population pipeline — candidates only, never auto-promoted.

Stages emit candidate nodes/edges stamped with provenance (`status=candidate`)
and a prompt fingerprint. Nothing here writes a `curated_*` status; promotion is
the curator's job (`curate.py`), and the semantics engine only ever sees what
survived QC and curation.

Models are reached through the `LlmClient` protocol, so neither `anthropic` nor
`openai` leaks into the rest of the package — the adapters import their SDK
lazily, so importing this module (and running the whole build + test suite)
needs no SDK and no API key. The committed artifact is built deterministically
from the curated seed; this pipeline is how that seed was *originally*
populated, kept in-repo as runnable, inspectable evidence of the capability.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Protocol

from pydantic import BaseModel

from argkit.schema import CurationStatus, Provenance


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LlmClient(Protocol):
    """Minimal text-in/text-out interface. Identity is declared by the client
    (`model_name`); callers never pick a model at the call site."""

    model_name: str

    def complete(self, prompt: str) -> str: ...


class PromptBundle(BaseModel):
    """A prompt plus the fingerprint that ties any generated node back to the
    exact instruction that produced it."""

    model_config = {"frozen": True}
    prompt_id: str
    text: str

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


def candidate_provenance(client: LlmClient, bundle: PromptBundle, confidence: float,
                         *, now: datetime | None = None) -> Provenance:
    """Provenance for a freshly generated candidate (un-curated)."""
    return Provenance(
        generator_model=client.model_name,
        prompt_id=bundle.prompt_id,
        prompt_sha256=bundle.sha256,
        created_at=now or _utcnow(),
        confidence=confidence,
        status=CurationStatus.CANDIDATE,
    )


def parse_json_candidates(raw: str) -> list[dict]:
    """Tolerantly extract the JSON array a stage prompt asks the model to emit.
    Raises if the model returned something unparseable — a parse failure is a QC
    signal, not something to paper over."""
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON array found in model output")
    return json.loads(raw[start:end + 1])


def reconcile_cross_check(generator_valid: bool, verifier_valid: bool) -> CurationStatus:
    """Two-model cross-check: agreement that a candidate is valid promotes it to
    `cross_checked`; any disagreement (or a rejection) keeps it a candidate for
    the human review queue."""
    if generator_valid and verifier_valid:
        return CurationStatus.CROSS_CHECKED
    return CurationStatus.CANDIDATE


EXPAND_PROMPT = PromptBundle(
    prompt_id="expand.v1",
    text=(
        "You are populating a defeasible argument graph for an AI-safety claim. "
        "Given the root claim, propose candidate arguments as a JSON array. Each "
        "object: {\"title\", \"stance\" (pro|con), \"premise\", \"inference\", "
        "\"conclusion\", \"source_citation\", \"confidence\" (0-1)}. Only output "
        "the JSON array."
    ),
)

PROBE_PROMPT = PromptBundle(
    prompt_id="adversarial_probe.v1",
    text=(
        "You are a devil's advocate. For the given currently-accepted argument, "
        "produce the single strongest defeater as a JSON array with one object: "
        "{\"attack_type\" (undermine|undercut|rebut), \"title\", \"rationale\", "
        "\"source_citation\", \"confidence\" (0-1)}. Only output the JSON array."
    ),
)


def expand_candidates(client: LlmClient, root_claim: str,
                      *, now: datetime | None = None) -> list[dict]:
    """Stage 1 — ask a model for candidate arguments for the root claim. Returns
    raw candidate dicts, each tagged with the provenance to stamp on promotion."""
    raw = client.complete(f"{EXPAND_PROMPT.text}\n\nROOT CLAIM:\n{root_claim}")
    candidates = parse_json_candidates(raw)
    stamp = candidate_provenance(client, EXPAND_PROMPT, confidence=0.5, now=now)
    return [{"candidate": c, "provenance": stamp.model_dump(mode="json")} for c in candidates]


def adversarial_probe(client: LlmClient, accepted_argument_title: str,
                      *, now: datetime | None = None) -> list[dict]:
    """Stage 3 — surface the strongest missing defeater against an accepted
    argument (Gate D's constrained slot-filling: the target is fixed by us)."""
    raw = client.complete(f"{PROBE_PROMPT.text}\n\nARGUMENT:\n{accepted_argument_title}")
    candidates = parse_json_candidates(raw)
    stamp = candidate_provenance(client, PROBE_PROMPT, confidence=0.4, now=now)
    return [{"candidate": c, "provenance": stamp.model_dump(mode="json")} for c in candidates]
