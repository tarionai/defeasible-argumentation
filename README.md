# Defeasible Argument Graphs — a verified miniature

[![tests](https://github.com/tarionai/defeasible-argumentation/actions/workflows/tests.yml/badge.svg)](https://github.com/tarionai/defeasible-argumentation/actions/workflows/tests.yml)

**Live demo:** [tarion-argue.netlify.app](https://tarion-argue.netlify.app)

A small, honest, end-to-end model of the machinery an evidentiary-argumentation
system needs: a **typed knowledge graph** of claims/evidence/inferences, a
**thin ASPIC+-flavored structured layer** that turns typed attacks into defeats,
a **Dung abstract-argumentation engine** that computes what survives, an
**LLM population pipeline** wrapped in a **deterministic QC + two-model
cross-check + human-in-the-loop** scaffold, and a **frozen, hash-stamped
artifact** rendered by a static site.

The worked example is the **Instrumental Convergence** thesis from AI safety
(Bostrom 2012/2014; Omohundro 2008), with real, named objections.

> **The spine is correctness, made provable.** The semantics engine is
> differential-tested against a published library — [PyArg](https://pypi.org/project/python-argumentation/)
> — on the textbook canon **and 1,000 randomly generated frameworks**, for
> grounded, complete, preferred, and stable semantics. A CI deploy guard
> recomputes the *shipped* artifact's extensions with PyArg and refuses to
> deploy if they ever diverge. A subtly-wrong extension reaching the live site
> is therefore structurally impossible, not merely unlikely.

## What it is — and what it deliberately is not

This is a **miniature, not a research contribution.** The honesty boundary is a
first-class deliverable:

- **Dung abstract argumentation** is implemented in full and verified:
  grounded (the foregrounded default — unique, polynomial, skeptical), plus
  complete, preferred, and stable.
- The **structured layer is ASPIC+-*flavored*, not ASPIC+.** It implements
  exactly three attack types (undermine → a premise, undercut → an inference,
  rebut → a conclusion) and one stated preference→defeat rule. There is **no**
  strict-rule closure, **no** multi-step rule chaining, and **no**
  rationality-postulate guarantee. Those are out of scope and named as such.
- One curated **worked example**, not a corpus. Depth over breadth.

## The payoff: a preference that changes the verdict

Under grounded (skeptical) semantics, the claim C0 is **accepted** — each of the
three attacks on the pro-argument (an undermine, an undercut, and a rebut) is
itself defeated by a counter-argument, so the pro-argument is *reinstated*.

But the verdict hinges on **one curated preference** (`D1 ≻ B3`). Drop it and the
mutual rebut `B3 ↔ D1` becomes a 2-cycle; grounded semantics then leaves the
claim **undecided**. The engine shows both. This is the point of a structured
layer: it makes the load-bearing disagreement explicit and lets you see exactly
which curatorial judgment the conclusion depends on. The artifact ships both
results (`preference_demonstration`).

## Architecture

```
argkit/
  aaf.py          Dung engine — the verified core (pure functions, no I/O)
  schema.py       AIF-aligned typed nodes + Provenance (Pydantic v2)
  structured.py   thin ASPIC+ layer: attack types -> defeat -> abstract edges
  qc.py           deterministic checks + two-model cross-check interface
  curate.py       human-in-the-loop curation pass (writes curated_* status)
  pipeline.py     LLM population stages (candidates only; never auto-promoted)
  llm_adapters.py Anthropic / OpenAI adapters (lazy-imported; optional)
  export.py       deterministic briefing (+ optional LLM-polished prose)
  seed.py         the curated Instrumental Convergence graph (single source)
  build.py        seed -> frozen, hash-stamped JSON artifact
tests/            textbook canon, 1000-AF differential vs PyArg, QC, deploy guard
artifact/         argument_graph.v1.json + SHA256SUMS  (the frozen output)
web/              Vite + React + TS static site that renders the artifact
```

Dependency direction is one-way (`build` → `export`/`structured`/`qc` →
`schema`/`aaf`). The semantics core never trusts the LLM; the LLM never touches
the semantics. PyArg is a **dev/test-only** oracle and is wrapped at a single
boundary (`tests/_oracle.py`) — it does not leak into `argkit`.

### Candidate → promotion gates

Nothing the LLM emits enters the framework unchecked. Every node/edge carries
`Provenance` with a status state machine:

```
candidate → cross_checked → curated_accepted | curated_rejected
```

- **Deterministic checks (no model, first):** attack-type-vs-target validity,
  dangling edges, self-attacks, duplicates, missing citations. A failure demotes
  to `candidate` and routes to review.
- **Two-model cross-check:** one model generates, a second independently
  verifies; only agreement promotes to `cross_checked`.
- **Human curation:** the curator accepts/edits/rejects; the decision and note
  are written to provenance. **Rejected candidates are kept, not deleted** — the
  artifact renders them (one argument, `R1`, was rejected for a hallucinated
  citation) so the audit trail is honest about what was thrown out and why.

## Reproduce from a clean checkout

Requires Python 3.10+.

```bash
python -m venv .venv && . .venv/Scripts/activate      # or .venv/bin/activate
pip install -e ".[dev]"
pytest                                                # textbook canon + 1000-AF differential + deploy guard
python -m argkit.build                                # regenerates artifact/argument_graph.v1.json
(cd artifact && sha256sum -c SHA256SUMS)               # hash matches -> byte-reproducible
```

The build calls **no model** — the LLM population happened once, offline, and
its curated output is `seed.py`. So `python -m argkit.build` is byte-identical
every run, and its SHA-256 matches `SHA256SUMS`. That reproducibility is exactly
what the deploy guard depends on.

### Running the LLM pipeline (optional)

The population pipeline is in-repo as runnable, inspectable evidence of the
capability. It is **not** on the build path and needs no key to build or test
(a deterministic fake stands in for the model in the tests). To run it for real:

```bash
pip install -e ".[dev,llm]"
export ANTHROPIC_API_KEY=...   # generator
export OPENAI_API_KEY=...       # independent cross-check
```

## Web

```bash
cd web && npm install && npm run build      # prebuild copies the artifact into public/
```

The browser never recomputes semantics — it renders the precomputed,
PyArg-verified values from the frozen artifact. Single engine, single
verification surface.

## Correctness references

- P. M. Dung (1995), *On the acceptability of arguments…*, Artificial Intelligence 77.
- P. Baroni, M. Caminada, M. Giacomin (2011), *An introduction to argumentation semantics*, KER 26(4).
- Oracle: **PyArg** (`python-argumentation`), Utrecht University, MIT. Backup oracles in the same space: `pygarg` (SAT-based), Tweety (Java).

## License

MIT. See [LICENSE](LICENSE).
