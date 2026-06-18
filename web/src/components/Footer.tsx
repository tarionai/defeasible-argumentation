import type { ArgumentGraphArtifact } from "../model/artifact";

interface FooterProps {
  artifact: ArgumentGraphArtifact;
}

const REPO_URL = "https://github.com/tarionai/defeasible-argumentation";
const ENGINE_CLAIM_URL =
  "https://github.com/tarionai/defeasible-argumentation/blob/main/tests/test_aaf_differential.py";

export function Footer({ artifact }: FooterProps) {
  const oracle = artifact.generated_by["oracle"] ?? "unknown";
  return (
    <footer className="footer">
      <p className="scope">
        <strong>Honest scope.</strong> Grounded semantics is shown here; complete, preferred, and
        stable extensions are also computed and differential-tested against PyArg. This is a thin
        ASPIC+ layer (defeasible rules, three attack types, and curated preferences) — not full
        ASPIC+ — applied to one curated worked example. The point is the method and its auditability,
        not a coverage claim.
      </p>
      <div className="links">
        <a href={REPO_URL} target="_blank" rel="noopener noreferrer">Public GitHub repository →</a>
        <a href={ENGINE_CLAIM_URL} target="_blank" rel="noopener noreferrer">
          Verified-engine claim (PyArg differential test) →
        </a>
      </div>
      <p className="engine-line">
        schema {artifact.schema_version} · engine {artifact.engine_version} · oracle {oracle} ·{" "}
        {artifact.qc.issues.length === 0 ? "QC: 0 open issues" : `QC: ${artifact.qc.issues.length} issues`}
      </p>
    </footer>
  );
}
