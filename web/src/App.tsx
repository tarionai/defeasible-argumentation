import { useEffect, useMemo, useState } from "react";
import type { ArgumentGraphArtifact } from "./model/artifact";
import { loadArtifact } from "./model/loadArtifact";
import { ArtifactView } from "./model/selectors";
import { Header } from "./components/Header";
import { GraphSection } from "./components/GraphSection";
import { PreferenceSection } from "./components/PreferenceSection";
import { BriefingSection } from "./components/BriefingSection";
import { ProvenanceSection } from "./components/ProvenanceSection";
import { Footer } from "./components/Footer";

type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; artifact: ArgumentGraphArtifact };

export function App() {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    loadArtifact()
      .then((artifact) => {
        if (!cancelled) {
          setState({ status: "ready", artifact });
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          const message = error instanceof Error ? error.message : "Unknown error.";
          setState({ status: "error", message });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const view = useMemo(
    () => (state.status === "ready" ? new ArtifactView(state.artifact) : null),
    [state],
  );

  if (state.status === "loading") {
    return <div className="status-screen">Loading artifact…</div>;
  }
  if (state.status === "error") {
    return <div className="status-screen error">Could not load artifact: {state.message}</div>;
  }

  const { artifact } = state;
  if (view === null) {
    return <div className="status-screen error">Artifact view unavailable.</div>;
  }

  const preference = artifact.graph.preferences[0];

  return (
    <div className="page">
      <Header artifact={artifact} view={view} />
      <GraphSection artifact={artifact} view={view} />
      <PreferenceSection
        demonstration={artifact.preference_demonstration}
        preference={preference}
      />
      <BriefingSection briefing={artifact.briefing} />
      <ProvenanceSection arguments={artifact.graph.arguments} />
      <Footer artifact={artifact} />
    </div>
  );
}
