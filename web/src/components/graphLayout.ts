import type { AbstractAttack, AttackType } from "../model/artifact";

export interface NodeBox {
  id: string;
  x: number;
  y: number;
}

export interface PositionedEdge {
  attacker: string;
  attacked: string;
  attackType: AttackType;
  isBidirectional: boolean;
}

export const NODE_WIDTH = 158;
export const NODE_HEIGHT = 58;
export const CANVAS_WIDTH = 720;
export const CANVAS_HEIGHT = 460;

/**
 * Fixed preset layout. A1 (the root-supporting argument) sits centre-top as the
 * focus of attack; the three con-arguments (B1/B2/B3) form the attacking band;
 * the pro defenders (A2/D1/D2) sit on the flanks/bottom defeating them. Positions
 * are hand-tuned so every directed defeat edge reads cleanly with no dep on an
 * auto-layout engine.
 */
export const NODE_POSITIONS: Record<string, { x: number; y: number }> = {
  A1: { x: 281, y: 24 },
  B1: { x: 70, y: 170 },
  B2: { x: 281, y: 170 },
  B3: { x: 492, y: 170 },
  D2: { x: 70, y: 330 },
  A2: { x: 281, y: 330 },
  D1: { x: 492, y: 330 },
};

export const EDGE_COLOR: Record<AttackType, string> = {
  undermine: "var(--undermine)",
  undercut: "var(--undercut)",
  rebut: "var(--rebut)",
};

export function layoutNodes(argumentIds: string[]): NodeBox[] {
  return argumentIds
    .map((id) => {
      const pos = NODE_POSITIONS[id];
      if (pos === undefined) {
        return undefined;
      }
      return { id, x: pos.x, y: pos.y };
    })
    .filter((box): box is NodeBox => box !== undefined);
}

export function layoutEdges(attacks: AbstractAttack[]): PositionedEdge[] {
  const pairKey = (a: string, b: string): string => [a, b].sort().join("::");
  const counts = new Map<string, number>();
  for (const attack of attacks) {
    const key = pairKey(attack.attacker_argument_id, attack.attacked_argument_id);
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return attacks.map((attack) => {
    const key = pairKey(attack.attacker_argument_id, attack.attacked_argument_id);
    return {
      attacker: attack.attacker_argument_id,
      attacked: attack.attacked_argument_id,
      attackType: attack.attack_type,
      isBidirectional: (counts.get(key) ?? 0) > 1,
    };
  });
}
