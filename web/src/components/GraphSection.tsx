import { useState } from "react";
import type { ArgumentGraphArtifact } from "../model/artifact";
import { ArtifactView } from "../model/selectors";
import { ArgumentGraph } from "./ArgumentGraph";
import { ArgumentDetailPanel } from "./ArgumentDetailPanel";
import { EDGE_COLOR } from "./graphLayout";

interface GraphSectionProps {
  artifact: ArgumentGraphArtifact;
  view: ArtifactView;
}

const ATTACK_TYPES = ["undermine", "undercut", "rebut"] as const;

export function GraphSection({ artifact, view }: GraphSectionProps) {
  const accepted = view.acceptedArguments();
  const [selectedId, setSelectedId] = useState<string | null>(accepted[0]?.argument_id ?? null);
  const rejected = view.rejectedCandidates();

  const detail = selectedId !== null ? view.detailFor(selectedId) : undefined;
  const label = selectedId !== null ? view.labelFor(selectedId) : undefined;

  return (
    <section className="section" id="graph">
      <p className="eyebrow">Section 02 — argument graph</p>
      <h2>Directed defeat graph</h2>
      <p className="section-note">
        Seven arguments survive curation and enter abstract argumentation. Edges are the
        engine-computed <strong>defeats</strong> (attack that succeeds), drawn with arrowheads
        from attacker to attacked. Node colour is the precomputed grounded label — the browser
        renders it, it never recomputes the semantics. Click a node for its premises, inference,
        conclusion, and citations.
      </p>

      <div className="graph-wrap">
        <div className="graph-canvas">
          <ArgumentGraph
            view={view}
            attacks={artifact.abstract_attacks}
            arguments={accepted}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
          <div className="legend">
            {ATTACK_TYPES.map((type) => (
              <span className="legend-item" key={type}>
                <span className="legend-swatch" style={{ borderTopColor: EDGE_COLOR[type] }} />
                {type}
              </span>
            ))}
            <span className="legend-item">
              <span className="dot accepted" /> accepted
            </span>
            <span className="legend-item">
              <span className="dot rejected" /> rejected
            </span>
          </div>
        </div>

        <ArgumentDetailPanel detail={detail} label={label} />
      </div>

      {rejected.map((arg) => (
        <div className="rejected-card" key={arg.argument_id}>
          <div className="rc-head">
            <span className="rc-id">{arg.argument_id}</span>
            <span className="rc-title">{arg.title}</span>
            <span className="badge rejected">curated out</span>
          </div>
          <p className="rc-reason">{arg.provenance.curator_note}</p>
          {arg.provenance.source_citation !== null ? (
            <p className="rc-citation">cited: {arg.provenance.source_citation}</p>
          ) : null}
          <p className="rc-citation">
            Outside the live graph: this candidate never reaches the engine. The human-in-the-loop
            gate removed it before semantics were computed.
          </p>
        </div>
      ))}
    </section>
  );
}
