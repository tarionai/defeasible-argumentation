import type {
  ArgumentGraphArtifact,
  Argument,
  GraphNode,
  Inference,
  GroundedLabel,
} from "./artifact";

export interface ArgumentDetail {
  argument: Argument;
  premises: GraphNode[];
  inference: Inference | undefined;
  conclusion: GraphNode | undefined;
}

function indexBy<T>(items: T[], key: (item: T) => string): Map<string, T> {
  const map = new Map<string, T>();
  for (const item of items) {
    map.set(key(item), item);
  }
  return map;
}

export class ArtifactView {
  private readonly evidenceById: Map<string, GraphNode>;
  private readonly claimsById: Map<string, GraphNode>;
  private readonly inferencesById: Map<string, Inference>;

  constructor(private readonly artifact: ArgumentGraphArtifact) {
    this.evidenceById = indexBy(artifact.graph.evidence, (node) => node.node_id);
    this.claimsById = indexBy(artifact.graph.claims, (node) => node.node_id);
    this.inferencesById = indexBy(artifact.graph.inferences, (node) => node.node_id);
  }

  rootClaim(): GraphNode | undefined {
    return this.claimsById.get(this.artifact.root_claim_id);
  }

  acceptedArguments(): Argument[] {
    const labelled = this.artifact.grounded_labelling;
    return this.artifact.graph.arguments.filter((arg) => arg.argument_id in labelled);
  }

  rejectedCandidates(): Argument[] {
    return this.artifact.graph.arguments.filter(
      (arg) => arg.provenance.status === "curated_rejected",
    );
  }

  labelFor(argumentId: string): GroundedLabel | undefined {
    return this.artifact.grounded_labelling[argumentId];
  }

  detailFor(argumentId: string): ArgumentDetail | undefined {
    const argument = this.artifact.graph.arguments.find(
      (arg) => arg.argument_id === argumentId,
    );
    if (argument === undefined) {
      return undefined;
    }
    const premises = argument.premise_ids
      .map((id) => this.evidenceById.get(id))
      .filter((node): node is GraphNode => node !== undefined);
    const conclusion =
      this.claimsById.get(argument.conclusion_id) ??
      this.evidenceById.get(argument.conclusion_id);
    return {
      argument,
      premises,
      inference: this.inferencesById.get(argument.inference_id),
      conclusion,
    };
  }
}
