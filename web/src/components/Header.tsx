import type { ArgumentGraphArtifact } from "../model/artifact";
import type { ArtifactView } from "../model/selectors";
import { Badge } from "./Badge";

interface HeaderProps {
  artifact: ArgumentGraphArtifact;
  view: ArtifactView;
}

export function Header({ artifact, view }: HeaderProps) {
  const rootClaim = view.rootClaim();
  const rootStatus = artifact.briefing.structured.root_status;

  return (
    <header className="header">
      <p className="eyebrow">Computational argumentation · frozen artifact</p>
      <h1>{artifact.title}</h1>
      <p className="what">
        A worked example in defeasible reasoning: a claim, its supporting and attacking arguments, and
        the verdict an argumentation engine computes under grounded semantics. Everything on this page
        is rendered from one frozen JSON artifact — the engine ran once; the browser only displays its
        output.
      </p>

      <div className="root-claim">
        <div className="claim-body">
          <p className="claim-label">Root claim · {artifact.root_claim_id}</p>
          <p className="claim-text">{rootClaim?.text ?? "(root claim text unavailable)"}</p>
        </div>
        <Badge label={rootStatus} />
      </div>
    </header>
  );
}
