import type { PreferenceDemonstration, Preference } from "../model/artifact";

interface PreferenceSectionProps {
  demonstration: PreferenceDemonstration;
  preference: Preference | undefined;
}

interface ExtensionCardProps {
  label: string;
  set: string[];
  verdict: "ACCEPTED" | "UNDECIDED";
  mechanism: string;
  flip?: boolean;
}

function ExtensionCard({ label, set, verdict, mechanism, flip }: ExtensionCardProps) {
  const verdictClass = verdict === "ACCEPTED" ? "accepted" : "undecided";
  return (
    <div className={`pref-card${flip === true ? " flip" : ""}`}>
      <div className="pc-head">
        <span className="pc-label">{label}</span>
        <span className={`badge ${verdictClass}`}>
          <span className={`dot ${verdictClass}`} /> C0 {verdict}
        </span>
      </div>
      <div className="ext-set">
        {set.map((id) => (
          <span className="ext-token" key={id}>
            {id}
          </span>
        ))}
      </div>
      <p className="pref-mechanism">grounded extension = {`{ ${set.join(", ")} }`}</p>
      <p className="pref-mechanism">{mechanism}</p>
    </div>
  );
}

export function PreferenceSection({ demonstration, preference }: PreferenceSectionProps) {
  const prefLabel =
    preference !== undefined
      ? `${preference.preferred_argument_id} ≻ ${preference.dispreferred_argument_id}`
      : "the curated preference";

  return (
    <section className="section" id="preference">
      <p className="eyebrow">Section 03 — load-bearing preference</p>
      <h2>One curated preference flips the verdict</h2>
      <p className="section-note">
        ASPIC+ preferences decide which way a symmetric rebuttal resolves. Here exactly one curated
        preference ({prefLabel}) breaks the {preference?.dispreferred_argument_id ?? "B3"}{"↔"}
        {preference?.preferred_argument_id ?? "D1"} two-cycle. Remove it and grounded semantics can no
        longer accept the claim. This is the centrepiece: the engine makes the dependency explicit and
        testable, rather than burying it in prose.
      </p>

      <div className="pref-grid">
        <ExtensionCard
          label="With preference"
          set={demonstration.with_preferences}
          verdict="ACCEPTED"
          mechanism={`preference ${prefLabel} resolves the rebuttal; the defender survives.`}
        />
        <ExtensionCard
          label="Without preference"
          set={demonstration.without_preferences}
          verdict="UNDECIDED"
          mechanism="symmetric 2-cycle; grounded labelling leaves both endpoints undecided."
          flip
        />
      </div>

      {preference !== undefined ? (
        <div className="pref-note">
          <strong>Curator rationale.</strong> {preference.rationale}
        </div>
      ) : null}

      <div className="pref-note">{demonstration.note}</div>
    </section>
  );
}
