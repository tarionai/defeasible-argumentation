import type { GroundedLabel } from "../model/artifact";
import type { ArgumentDetail } from "../model/selectors";
import { Badge } from "./Badge";

interface ArgumentDetailPanelProps {
  detail: ArgumentDetail | undefined;
  label: GroundedLabel | undefined;
}

export function ArgumentDetailPanel({ detail, label }: ArgumentDetailPanelProps) {
  if (detail === undefined) {
    return (
      <aside className="detail">
        <p className="placeholder">Select a node in the graph to inspect its premises, inference, conclusion, and provenance.</p>
      </aside>
    );
  }

  const { argument, premises, inference, conclusion } = detail;
  const citations = premises
    .map((node) => node.provenance.source_citation)
    .filter((citation): citation is string => citation !== null);

  return (
    <aside className="detail">
      <div className="detail-head">
        <span className="detail-id">{argument.argument_id}</span>
        {label !== undefined ? <Badge label={label} /> : null}
      </div>
      <h3>{argument.title}</h3>

      <div className="detail-field">
        <div className="k">Premises</div>
        <ul>
          {premises.map((node) => (
            <li key={node.node_id} className="v">
              {node.text}
            </li>
          ))}
        </ul>
      </div>

      {inference !== undefined ? (
        <div className="detail-field">
          <div className="k">Inference</div>
          <div className="v">{inference.text}</div>
        </div>
      ) : null}

      {conclusion !== undefined ? (
        <div className="detail-field">
          <div className="k">Conclusion</div>
          <div className="v">{conclusion.text}</div>
        </div>
      ) : null}

      {citations.length > 0 ? (
        <div className="detail-field">
          <div className="k">Source citations</div>
          {citations.map((citation, index) => (
            <div key={index} className="v citation">
              {citation}
            </div>
          ))}
        </div>
      ) : null}

      <div className="detail-field">
        <div className="k">Provenance</div>
        <div className="meta-row">
          <span className="chip">{argument.provenance.status}</span>
          <span className="chip">conf {argument.provenance.confidence.toFixed(2)}</span>
          <span className="chip">strength {argument.strength.toFixed(2)}</span>
          <span className="chip">{argument.stance}</span>
        </div>
      </div>
    </aside>
  );
}
