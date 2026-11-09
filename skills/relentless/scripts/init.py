#!/usr/bin/env python3
"""Initialize .relentless/ for a relentless run.

Usage:
  python3 init.py [--dir .] [--metric NAME] [--direction up|down] [--gate CMD]
                  [--target N] [--baseline N] [--floor-attempts N]
                  [--evidence PATHS] [--bar TEXT] [--report-fail-keys KEYS]
                  [--upgrade-block]

Writes .relentless/goal.md, .relentless/score.tsv (header only),
.relentless/ledger.tsv (header only), and the directories lanes use.
Idempotent: an existing goal.md is never overwritten.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

BEGIN = "<!-- relentless:begin -->"
END = "<!-- relentless:end -->"

GOAL_TEMPLATE = """{begin}
metric: {metric}
direction: {direction}
baseline: {baseline}
target: {target}
floor_attempts: {floor_attempts}
gate: {gate}
evidence: {evidence}
bar: {bar}
lanes: {lanes}
report_fail_keys: {report_fail_keys}
{end}

# Goal

{body}

## Bar

{bar}

## Gate sensitivity

Record 2 consecutive failing runs on a deliberately broken build and 2
consecutive passing runs on the real build, with the command and output for
each. The loop does not start until all four exist.

- Broken build, run 1:
- Broken build, run 2:
- Real build, run 1:
- Real build, run 2:

## Qualification

Record the evidence for each Qualify check: the number and its direction, the
gate command, the measured minutes per run, the bar path and open method, and
the permission that covers branch and test work.
"""


RESUME_TEMPLATE = """You are resuming a relentless loop in {root}.

Read, in order:
1. .relentless/goal.md
2. the last 5 rows of .relentless/ledger.tsv
3. .relentless/score.tsv
4. the newest 2 files in .relentless/runs/

Then run the next iteration. One hypothesis, one builder, one gate run,
one verdict, one ledger row. Do not re-plan from scratch and do not repeat
a hypothesis the ledger marks reverted. Stop only on "STOP yes" from
scripts/score.py, three dead pivots, or a decision only the operator can make.
Reply with one short status line and nothing else.
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default=".")
    parser.add_argument("--metric", default="score")
    parser.add_argument("--direction", default="up", choices=["up", "down"])
    parser.add_argument("--gate", default="")
    parser.add_argument("--target", default="")
    parser.add_argument("--baseline", default="")
    parser.add_argument("--floor-attempts", default="3")
    parser.add_argument("--evidence", default="")
    parser.add_argument("--bar", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--lanes", default="5")
    parser.add_argument("--report-fail-keys", default="")
    parser.add_argument(
        "--upgrade-block",
        action="store_true",
        help="If goal.md exists without the machine block, add the block at the top and keep the prose.",
    )
    args = parser.parse_args()

    try:
        floor = int(args.floor_attempts)
    except (TypeError, ValueError):
        print("--floor-attempts must be an integer", file=sys.stderr)
        return 2
    if floor < 3:
        print("--floor-attempts must be at least 3", file=sys.stderr)
        return 2
    try:
        lanes = int(args.lanes)
    except (TypeError, ValueError):
        print("--lanes must be an integer", file=sys.stderr)
        return 2
    if lanes < 3 or lanes > 10:
        print("--lanes must be between 3 and 10", file=sys.stderr)
        return 2

    if not args.upgrade_block:
        missing = []
        for flag, value in (
            ("--gate", args.gate),
            ("--baseline", args.baseline),
            ("--target", args.target),
            ("--evidence", args.evidence),
            ("--bar", args.bar),
        ):
            if not str(value).strip():
                missing.append(flag)
        if missing:
            print(
                "missing required values: " + ", ".join(missing),
                file=sys.stderr,
            )
            print(
                "goal.md needs a measured baseline, a target, a gate command, "
                "at least one evidence path, and a bar. Run the gate first.",
                file=sys.stderr,
            )
            return 2

    root = Path(args.dir).resolve()
    rel = root / ".relentless"
    (rel / "runs").mkdir(parents=True, exist_ok=True)

    goal = rel / "goal.md"
    if goal.exists() and args.upgrade_block and BEGIN not in goal.read_text():
        block = GOAL_TEMPLATE.format(
            begin=BEGIN,
            end=END,
            metric=args.metric,
            direction=args.direction,
            baseline=args.baseline,
            target=args.target,
            floor_attempts=args.floor_attempts,
            gate=args.gate,
            evidence=args.evidence,
            bar=args.bar,
            body=args.body,
            lanes=args.lanes,
            report_fail_keys=args.report_fail_keys,
        ).split(END, 1)[0] + END + "\n\n"
        goal.write_text(block + goal.read_text())
        print(f"added the machine block to existing {goal}")
    elif goal.exists():
        print(f"goal.md already exists, leaving it untouched: {goal}")
        if BEGIN not in goal.read_text():
            print("  it has no relentless:begin block; score.py cannot read it.")
            print("  re-run with --upgrade-block to add the block above the prose, or add it by hand.")
    else:
        write(
            goal,
            GOAL_TEMPLATE.format(
                begin=BEGIN,
                end=END,
                metric=args.metric,
                direction=args.direction,
                baseline=args.baseline,
                target=args.target,
                floor_attempts=args.floor_attempts,
                gate=args.gate,
                evidence=args.evidence,
                bar=args.bar,
                body=args.body,
                lanes=args.lanes,
                report_fail_keys=args.report_fail_keys,
            ),
        )
        print(f"wrote {goal}")

    score = rel / "score.tsv"
    if not score.exists():
        write(
            score,
            "ts\tkind\tattempt\tsha\tmetric\tvalue\tpercent\tguards\tevidence\tstop\tnote\n",
        )
        print(f"wrote {score}")

    ledger = rel / "ledger.tsv"
    if not ledger.exists():
        write(ledger, "ts\tphase\tdecision\twhy\tevidence\tresult\n")
        print(f"wrote {ledger}")

    resume = rel / "resume-prompt.md"
    if not resume.exists():
        write(
            resume,
            RESUME_TEMPLATE.format(root=root),
        )
        print(f"wrote {resume}")

    ignore = root / ".gitignore"
    lines = [".relentless/runs/", ".relentless/.score.lock"]
    text = ignore.read_text() if ignore.exists() else ""
    added = [line for line in lines if line not in text]
    if added:
        with ignore.open("a") as handle:
            if text and not text.endswith("\n"):
                handle.write("\n")
            handle.write("# raw relentless run logs and the run lock; goal.md, score.tsv and ledger.tsv stay committed\n")
            for line in added:
                handle.write(line + "\n")
        print("added to " + str(ignore) + ": " + ", ".join(added))

    print("\nNext: fill goal.md, prove the gate is sensitive, run the baseline, then start the loop.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
