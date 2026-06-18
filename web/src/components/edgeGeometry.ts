import {
  NODE_WIDTH,
  NODE_HEIGHT,
  type NodeBox,
} from "./graphLayout";

export interface Point {
  x: number;
  y: number;
}

export interface EdgePath {
  start: Point;
  end: Point;
  mid: Point;
}

function center(box: NodeBox): Point {
  return { x: box.x + NODE_WIDTH / 2, y: box.y + NODE_HEIGHT / 2 };
}

/** Clip a ray from the box centre to the box's rectangular border. */
function borderPoint(box: NodeBox, toward: Point): Point {
  const c = center(box);
  const dx = toward.x - c.x;
  const dy = toward.y - c.y;
  if (dx === 0 && dy === 0) {
    return c;
  }
  const halfW = NODE_WIDTH / 2;
  const halfH = NODE_HEIGHT / 2;
  const scaleX = dx === 0 ? Infinity : halfW / Math.abs(dx);
  const scaleY = dy === 0 ? Infinity : halfH / Math.abs(dy);
  const scale = Math.min(scaleX, scaleY);
  return { x: c.x + dx * scale, y: c.y + dy * scale };
}

/**
 * Compute the visible segment between two node boxes, clipped to both borders.
 * `offset` shifts the line perpendicular to its direction so antiparallel edges
 * (a mutual rebut) do not overlap.
 */
export function computeEdgePath(
  from: NodeBox,
  to: NodeBox,
  offset: number,
): EdgePath {
  const fromCenter = center(from);
  const toCenter = center(to);

  let perpX = 0;
  let perpY = 0;
  if (offset !== 0) {
    const dx = toCenter.x - fromCenter.x;
    const dy = toCenter.y - fromCenter.y;
    const len = Math.hypot(dx, dy) || 1;
    perpX = (-dy / len) * offset;
    perpY = (dx / len) * offset;
  }

  const shiftedTo: Point = { x: toCenter.x + perpX, y: toCenter.y + perpY };
  const shiftedFrom: Point = { x: fromCenter.x + perpX, y: fromCenter.y + perpY };

  const start = borderPoint(from, shiftedTo);
  const end = borderPoint(to, shiftedFrom);
  const startShifted: Point = { x: start.x + perpX, y: start.y + perpY };
  const endShifted: Point = { x: end.x + perpX, y: end.y + perpY };

  return {
    start: startShifted,
    end: endShifted,
    mid: {
      x: (startShifted.x + endShifted.x) / 2,
      y: (startShifted.y + endShifted.y) / 2,
    },
  };
}
