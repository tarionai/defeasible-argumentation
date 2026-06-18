import type { GroundedLabel } from "../model/artifact";

const LABEL_TEXT: Record<GroundedLabel, string> = {
  accepted: "Accepted",
  rejected: "Rejected",
  undecided: "Undecided",
};

interface BadgeProps {
  label: GroundedLabel;
}

export function Badge({ label }: BadgeProps) {
  return (
    <span className={`badge ${label}`}>
      <span className={`dot ${label}`} />
      {LABEL_TEXT[label]}
    </span>
  );
}
