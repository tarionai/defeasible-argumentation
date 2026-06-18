import { useMemo } from "react";
import type { AbstractAttack, Argument, GroundedLabel } from "../model/artifact";
import type { ArtifactView } from "../model/selectors";
import {
  layoutNodes,
  layoutEdges,
  EDGE_COLOR,
  NODE_WIDTH,
  NODE_HEIGHT,
  CANVAS_WIDTH,
  CANVAS_HEIGHT,
  type NodeBox,
} from "./graphLayout";
import { computeEdgePath } from "./edgeGeometry";

const LABEL_FILL: Record<GroundedLabel, { fill: string; stroke: string; text: string }> = {
  accepted: { fill: "var(--accept-soft)", stroke: "var(--accept)", text: "var(--accept)" },
  rejected: { fill: "var(--reject-soft)", stroke: "var(--reject)", text: "var(--reject)" },
  undecided: { fill: "var(--undecided-soft)", stroke: "var(--undecided)", text: "var(--undecided)" },
};

interface ArgumentGraphProps {
  view: ArtifactView;
  attacks: AbstractAttack[];
  arguments: Argument[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

function wrapTitle(title: string, perLine = 22): string[] {
  const words = title.split(" ");
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const candidate = current === "" ? word : `${current} ${word}`;
    if (candidate.length > perLine && current !== "") {
      lines.push(current);
      current = word;
    } else {
      current = candidate;
    }
  }
  if (current !== "") {
    lines.push(current);
  }
  return lines.slice(0, 3);
}

export function ArgumentGraph({
  view,
  attacks,
  arguments: args,
  selectedId,
  onSelect,
}: ArgumentGraphProps) {
  const titleById = useMemo(() => {
    const map = new Map<string, string>();
    for (const arg of args) {
      map.set(arg.argument_id, arg.title);
    }
    return map;
  }, [args]);

  const nodes: NodeBox[] = useMemo(
    () => layoutNodes(args.map((arg) => arg.argument_id)),
    [args],
  );
  const nodeById = useMemo(() => {
    const map = new Map<string, NodeBox>();
    for (const node of nodes) {
      map.set(node.id, node);
    }
    return map;
  }, [nodes]);

  const edges = useMemo(() => layoutEdges(attacks), [attacks]);

  return (
    <svg
      viewBox={`0 0 ${CANVAS_WIDTH} ${CANVAS_HEIGHT}`}
      role="img"
      aria-label="Directed defeat graph over the seven accepted arguments"
    >
      <defs>
        {(["undermine", "undercut", "rebut"] as const).map((type) => (
          <marker
            key={type}
            id={`arrow-${type}`}
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill={EDGE_COLOR[type]} />
          </marker>
        ))}
      </defs>

      {edges.map((edge, index) => {
        const from = nodeById.get(edge.attacker);
        const to = nodeById.get(edge.attacked);
        if (from === undefined || to === undefined) {
          return null;
        }
        const offset = edge.isBidirectional ? 11 : 0;
        const path = computeEdgePath(from, to, offset);
        const color = EDGE_COLOR[edge.attackType];
        const dimmed =
          selectedId !== null &&
          edge.attacker !== selectedId &&
          edge.attacked !== selectedId;
        return (
          <g key={`${edge.attacker}-${edge.attacked}-${index}`} opacity={dimmed ? 0.22 : 1}>
            <line
              x1={path.start.x}
              y1={path.start.y}
              x2={path.end.x}
              y2={path.end.y}
              stroke={color}
              strokeWidth={1.6}
              markerEnd={`url(#arrow-${edge.attackType})`}
            />
            <text
              className="edge-label"
              x={path.mid.x}
              y={path.mid.y - 3}
              textAnchor="middle"
              fill={color}
            >
              {edge.attackType}
            </text>
          </g>
        );
      })}

      {nodes.map((node) => {
        const label = view.labelFor(node.id) ?? "undecided";
        const colors = LABEL_FILL[label];
        const title = titleById.get(node.id) ?? node.id;
        const lines = wrapTitle(title);
        const isSelected = node.id === selectedId;
        return (
          <g
            key={node.id}
            className={`gnode${isSelected ? " selected" : ""}`}
            onClick={() => onSelect(node.id)}
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onSelect(node.id);
              }
            }}
          >
            <rect
              x={node.x}
              y={node.y}
              width={NODE_WIDTH}
              height={NODE_HEIGHT}
              rx={6}
              fill={colors.fill}
              stroke={colors.stroke}
              strokeWidth={isSelected ? 2.5 : 1.4}
            />
            <text className="gnode-id" x={node.x + 10} y={node.y + 17} fill={colors.text}>
              {node.id}
            </text>
            {lines.map((line, lineIndex) => (
              <text
                key={lineIndex}
                className="gnode-title"
                x={node.x + NODE_WIDTH / 2}
                y={node.y + 32 + lineIndex * 13}
                textAnchor="middle"
              >
                {line}
              </text>
            ))}
          </g>
        );
      })}
    </svg>
  );
}
