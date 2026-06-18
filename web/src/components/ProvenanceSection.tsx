import type { Argument } from "../model/artifact";

interface ProvenanceSectionProps {
  arguments: Argument[];
}

function statusLabel(status: Argument["provenance"]["status"]): string {
  return status === "curated_accepted" ? "accepted" : "rejected";
}

export function ProvenanceSection({ arguments: args }: ProvenanceSectionProps) {
  return (
    <section className="section" id="provenance">
      <p className="eyebrow">Section 05 — curation trail</p>
      <h2>Provenance &amp; human-in-the-loop gate</h2>
      <p className="section-note">
        Every argument the generator proposed is recorded with its model, confidence, and the
        curator&apos;s note. One candidate (R1) was rejected before it could enter the graph: its
        citation was a hallucination. The gate is auditable, not implicit.
      </p>

      <div className="table-wrap">
        <table className="prov">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Status</th>
              <th>Generator</th>
              <th>Conf.</th>
              <th>Curator note</th>
            </tr>
          </thead>
          <tbody>
            {args.map((arg) => {
              const rejected = arg.provenance.status === "curated_rejected";
              return (
                <tr key={arg.argument_id} className={rejected ? "rejected-row" : undefined}>
                  <td className="id">{arg.argument_id}</td>
                  <td className="title">{arg.title}</td>
                  <td>
                    <span className={`status-pill ${statusLabel(arg.provenance.status)}`}>
                      {statusLabel(arg.provenance.status)}
                    </span>
                  </td>
                  <td className="mono">{arg.provenance.generator_model}</td>
                  <td className="mono">{arg.provenance.confidence.toFixed(2)}</td>
                  <td className={rejected ? "note" : undefined}>{arg.provenance.curator_note}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
