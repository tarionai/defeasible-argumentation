export type AttackType = "undermine" | "undercut" | "rebut";
export type Stance = "pro" | "con" | "neutral";
export type GroundedLabel = "accepted" | "rejected" | "undecided";
export type CurationStatus = "curated_accepted" | "curated_rejected";

export interface Provenance {
  status: CurationStatus;
  curator_note: string;
  source_citation: string | null;
  confidence: number;
  generator_model: string;
  created_at: string;
  prompt_id: string;
  prompt_sha256: string;
}

export interface Argument {
  argument_id: string;
  title: string;
  premise_ids: string[];
  inference_id: string;
  conclusion_id: string;
  strength: number;
  stance: Stance;
  provenance: Provenance;
}

export interface GraphNode {
  node_id: string;
  text: string;
  provenance: Provenance;
}

export interface Inference {
  node_id: string;
  text: string;
  conclusion_id: string;
  premise_ids: string[];
  provenance: Provenance;
}

export interface Conflict {
  conflict_id: string;
  attack_type: AttackType;
  source_argument_id: string;
  target_argument_id: string;
  target_node_id: string;
  provenance: Provenance;
}

export interface Preference {
  preference_id: string;
  preferred_argument_id: string;
  dispreferred_argument_id: string;
  rationale: string;
  provenance: Provenance;
}

export interface Graph {
  title: string;
  root_claim_id: string;
  arguments: Argument[];
  claims: GraphNode[];
  evidence: GraphNode[];
  inferences: Inference[];
  conflicts: Conflict[];
  preferences: Preference[];
}

export interface AbstractAttack {
  attacker_argument_id: string;
  attacked_argument_id: string;
  attack_type: AttackType;
  origin_conflict_id: string;
  note: string;
}

export type GroundedLabelling = Record<string, GroundedLabel>;

export interface Extensions {
  grounded: string[][];
  complete: string[][];
  preferred: string[][];
  stable: string[][];
}

export interface PreferenceDemonstration {
  with_preferences: string[];
  without_preferences: string[];
  note: string;
}

export interface StructuredBriefing {
  root_claim_id: string;
  root_status: GroundedLabel;
  accepted: string[];
  rejected: string[];
  undecided: string[];
}

export interface Briefing {
  deterministic: string;
  structured: StructuredBriefing;
}

export interface QcIssue {
  kind: string;
  severity: string;
  target_id: string;
  message: string;
}

export interface Qc {
  issues: QcIssue[];
}

export interface ArgumentGraphArtifact {
  title: string;
  root_claim_id: string;
  graph: Graph;
  abstract_attacks: AbstractAttack[];
  extensions: Extensions;
  grounded_labelling: GroundedLabelling;
  preference_demonstration: PreferenceDemonstration;
  briefing: Briefing;
  qc: Qc;
  schema_version: string;
  engine_version: string;
  generated_by: Record<string, string>;
}
