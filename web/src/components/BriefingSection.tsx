import type { Briefing } from "../model/artifact";

interface BriefingSectionProps {
  briefing: Briefing;
}

export function BriefingSection({ briefing }: BriefingSectionProps) {
  return (
    <section className="section" id="briefing">
      <p className="eyebrow">Section 04 — deterministic briefing</p>
      <h2>The briefing is computed, not written</h2>
      <p className="section-note">
        This text is emitted directly from the engine&apos;s labelling of the frozen graph. No language
        model produces it at render time; the wording is a deterministic function of the structure
        above.
      </p>

      <div className="source-of-truth">
        <span className="dot accepted" /> source of truth — computed, not generated
      </div>
      <pre className="briefing-block">{briefing.deterministic}</pre>

      <p className="caption">
        An optional LLM-polished prose layer exists in the pipeline for human-readable summaries, but
        it is downstream and advisory: this structured briefing remains the authority, and any prose
        layer must agree with it.
      </p>
    </section>
  );
}
