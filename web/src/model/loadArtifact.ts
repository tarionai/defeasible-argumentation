import type { ArgumentGraphArtifact } from "./artifact";

const ARTIFACT_URL = "/argument_graph.v1.json";

const REQUIRED_KEYS: ReadonlyArray<keyof ArgumentGraphArtifact> = [
  "title",
  "root_claim_id",
  "graph",
  "abstract_attacks",
  "extensions",
  "grounded_labelling",
  "preference_demonstration",
  "briefing",
  "qc",
];

function assertShape(value: unknown): asserts value is ArgumentGraphArtifact {
  if (typeof value !== "object" || value === null) {
    throw new Error("Artifact is not an object.");
  }
  const record = value as Record<string, unknown>;
  for (const key of REQUIRED_KEYS) {
    if (!(key in record)) {
      throw new Error(`Artifact is missing required key: ${String(key)}`);
    }
  }
}

export async function loadArtifact(): Promise<ArgumentGraphArtifact> {
  const response = await fetch(ARTIFACT_URL, { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`Failed to fetch artifact (${response.status} ${response.statusText}).`);
  }
  const data: unknown = await response.json();
  assertShape(data);
  return data;
}
