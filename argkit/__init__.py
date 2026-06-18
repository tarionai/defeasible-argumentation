"""argkit — a verified miniature of a defeasible-argumentation pipeline.

Layers, in dependency order (each depends only on those above it):

  aaf         Dung abstract argumentation: the verified semantics core.
  schema      AIF-aligned typed nodes + Provenance (the knowledge graph).
  structured  Thin ASPIC+-flavored layer: attack types -> defeat -> abstract edges.
  qc          Deterministic checks + two-model cross-check + adversarial probe.
  curate      Human-in-the-loop curation pass.
  pipeline    LLM population stages (candidates only; never auto-promoted).
  export      Deterministic briefing (+ optional LLM-polished prose).
  build       End-to-end: curated seed -> frozen, hash-stamped artifact.

The semantics core never trusts the LLM, and the LLM never touches the semantics.
"""

__version__ = "1.0.0"
