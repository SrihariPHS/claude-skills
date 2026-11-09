#!/usr/bin/env python3
"""Run the gate, record the attempt, and decide whether the loop stops.

Reads .relentless/goal.md, runs its `gate` command from the repo root,
appends one row to .relentless/score.tsv, writes the raw output to
.relentless/runs/, and prints STOP yes or STOP no.

Three modes:

  score.py --dir .                        run the gate now
  score.py --dir . --from-report r.json   log a run from its JSON artifact
  score.py --dir . --record 95/100        log a run with no JSON artifact

--from-report and --record exist because a gate can take longer than one
tool call. --from-report also derives failing guards from the report: any
check whose status is not pass, a score below threshold, and every truthy
key named by report_fail_keys in goal.md.

Exit codes: 0 when the gate passed, 1 when it failed, 2 on setup error.
The STOP decision is printed, not encoded in the exit code.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

BEGIN = "<!-- relentless:begin -->"
END = "<!-- relentless:end -->"


def parse_goal(path: Path) -> dict[str, str]:
    text = path.read_text()
    if BEGIN not in text or END not in text:
        raise SystemExit(f"{path} has no {BEGIN} ... {END} block")
    block = text.split(BEGIN, 1)[1].split(END, 1)[0]
    fields: dict[str, str] = {}
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def number(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_output(text: str) -> dict[str, object]:
    found: dict[str, object] = {
        "score": None,
        "possible": None,
        "metric": None,
        "metric_value": None,
        "guards": [],
        "evidence": [],
    }
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^SCORE\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)$", line)
        if m:
            found["score"] = float(m.group(1))
            found["possible"] = float(m.group(2))
            continue
        m = re.match(r"^[*\s]*Score:?\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", line, re.IGNORECASE)
        if m:
            found["score"] = float(m.group(1))
            found["possible"] = float(m.group(2))
            continue
        m = re.match(r"^METRIC\s+(\S+)\s+(-?\d+(?:\.\d+)?)$", line)
        if m:
            found["metric"] = m.group(1)
            found["metric_value"] = float(m.group(2))
            continue
        m = re.match(r"^GUARD\s+(.+)$", line)
        if m:
            found["guards"].append(m.group(1).strip())
            continue
        m = re.match(r"^EVIDENCE\s+(.+)$", line)
        if m:
            found["evidence"].append(m.group(1).strip())
    return found


def guard_is_green(line: str) -> bool:
    """A guard line is green unless it names a failure.

    Words like "pass", "ok", "clean" mean green. "fail", "error", "dirty",
    "missing" mean red, unless negated by a preceding 0, no, zero or none.
    """
    good = ("pass", "passed", "passing", "ok", "green", "clean", "healthy")
    bad = (
        "fail", "failed", "failing", "failure", "failures",
        "error", "errors", "red", "dirty", "missing",
    )
    negations = ("0", "no", "zero", "none")
    state = None
    words = re.findall(r"[a-z0-9]+", line.lower())
    for index, word in enumerate(words):
        previous = words[index - 1] if index else ""
        if word in bad and previous not in negations:
            state = False
        elif word in good:
            state = True
    return state is not False


def percent_from_metric(
    value: float, baseline: float, target: float, direction: str
) -> float | None:
    if direction == "down":
        if baseline <= 0 or target <= 0:
            return None
        if value <= target:
            return 100.0
        # linear from baseline (0 percent progress) to target (100 percent)
        span = baseline - target
        if span <= 0:
            return None
        return max(0.0, min(100.0, (baseline - value) / span * 100.0))
    span = target - baseline
    if span == 0:
        return 100.0 if value >= target else 0.0
    return max(0.0, min(100.0, (value - baseline) / span * 100.0))


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    if len(lines) < 2:
        return []
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        cells = line.split("\t")
        cells += [""] * (len(header) - len(cells))
        rows.append(dict(zip(header, cells)))
    return rows


HEADER = "ts\tkind\tattempt\tsha\tmetric\tvalue\tpercent\tguards\tevidence\tstop\tnote\n"


def cell(value: object) -> str:
    text = str(value).replace("\t", " ").replace("\n", " ").replace("\r", " ")
    if text[:1] in ("=", "+", "-", "@"):
        text = "'" + text
    return text


def write_row(
    score_path: Path,
    kind: str,
    attempt: int,
    sha: str,
    metric_name: str,
    metric_value: object,
    pct: float | None,
    guards: list[str],
    evidence: list[str],
    stop_value: str,
    note: str,
) -> None:
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = "\t".join(
        cell(v)
        for v in (
            ts,
            kind,
            attempt,
            sha[:12],
            metric_name,
            "" if metric_value is None else metric_value,
            "" if pct is None else f"{pct:.1f}",
            "|".join(guards),
            ",".join(evidence),
            stop_value,
            note,
        )
    )
    with score_path.open("a") as handle:
        handle.write(row + "\n")


def key_value(document: object, dotted: str) -> object:
    """Read a dotted key path out of a parsed JSON document."""
    current = document
    for part in dotted.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def goal_gaps(goal: dict[str, str]) -> list[str]:
    """Return the missing or malformed goal fields that block a stop.

    A gate can pass while the contract is incomplete, because the gate only
    knows its own command. These gaps must block STOP regardless.
    """
    gaps: list[str] = []
    if number(goal.get("baseline", "")) is None:
        gaps.append("baseline missing")
    if number(goal.get("target", "")) is None:
        gaps.append("target missing")
    if goal.get("direction", "").strip() not in ("up", "down"):
        gaps.append("direction must be up or down")
    if not [p for p in goal.get("evidence", "").split(",") if p.strip()]:
        gaps.append("evidence list empty")
    if not goal.get("bar", "").strip():
        gaps.append("bar missing")
    if not goal.get("gate", "").strip():
        gaps.append("gate missing")
    try:
        floor = int(number(goal.get("floor_attempts", "")) or 0)
    except (TypeError, ValueError):
        floor = 0
    if floor < 3:
        gaps.append("floor_attempts below 3")
    return gaps


def surface_fail_keys(goal: dict[str, str]) -> list[tuple[str, str]]:
    """Read `report_fail_keys` from the goal block.

    Shape: comma separated `dotted.path:label`. A truthy value at the path
    is a failing guard. Surface rules live in the goal file, not the script,
    so the scorer stays generic across targets.
    """
    raw = goal.get("report_fail_keys", "").strip()
    if not raw:
        return []
    pairs = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        path, _, label = item.partition(":")
        pairs.append((path.strip(), (label.strip() or path.strip())))
    return pairs


def record_existing(
    root: Path,
    score_path: Path,
    goal: dict[str, str],
    rows: list[dict[str, str]],
    args: argparse.Namespace,
    sha: str,
    attempt: int,
) -> int:
    """Log a gate run that happened outside score.py, from its artifacts.

    A slow gate (one run longer than a tool call) is run by the conductor and
    recorded here. Evidence must exist and be recent, so a stale report cannot
    be logged as a new pass. The value is compared to the target using the
    goal's direction, so a down metric compares correctly against its ceiling.
    """
    gaps = goal_gaps(goal)
    if gaps:
        print("goal.md is incomplete, refusing to record: " + ", ".join(gaps), file=sys.stderr)
        return 2

    earned_text, _, total_text = args.record.partition("/")
    value = number(earned_text)
    possible = number(total_text) if total_text else None
    if value is None:
        print("--record needs a number, as EARNED/TOTAL or a bare value", file=sys.stderr)
        return 2
    if possible is not None and possible <= 0:
        print("--record total must be greater than zero", file=sys.stderr)
        return 2
    pct = (value / possible * 100.0) if possible else None

    target = number(goal.get("target", ""))
    direction = goal.get("direction", "up")
    floor = int(number(goal.get("floor_attempts", "3")) or 3)

    evidence = [p.strip() for p in goal.get("evidence", "").split(",") if p.strip()]
    evidence_missing = [item for item in evidence if not (root / item).exists()]
    if evidence_missing:
        print(
            "evidence is missing, refusing to record: " + ", ".join(evidence_missing),
            file=sys.stderr,
        )
        return 2

    newest = 0.0
    for item in evidence:
        path = root / item
        mtime = path.stat().st_mtime
        if path.is_dir():
            mtime = max((child.stat().st_mtime for child in path.rglob("*") if child.is_file()), default=mtime)
        newest = max(newest, mtime)
    age_minutes = (time.time() - newest) / 60.0
    if age_minutes > args.record_max_age:
        print(
            f"evidence is {age_minutes:.0f} minutes old, older than --record-max-age {args.record_max_age}",
            file=sys.stderr,
        )
        return 2

    guards = args.guard or []
    guards_ok = all(guard_is_green(line) for line in guards)
    if direction == "down":
        hit_target = value <= target
    else:
        hit_target = value >= target
    measured_runs = sum(1 for row in rows if row.get("kind") != "baseline") + 1
    floor_ok = measured_runs >= floor

    stop = hit_target and guards_ok and floor_ok
    reason = []
    if not hit_target:
        reason.append("target not met")
    if not guards_ok:
        reason.append("guard failed")
    if not floor_ok:
        reason.append(f"floor {measured_runs}/{floor} runs")

    stop_value = "yes" if stop else "no"
    note = args.note or ("target met" if stop else "; ".join(reason))

    write_row(
        score_path,
        args.tag,
        attempt,
        sha,
        goal.get("metric", "score"),
        value,
        pct,
        guards,
        evidence,
        stop_value,
        note,
    )

    shown = "n/a" if pct is None else f"{pct:.1f}"
    print("")
    print(
        f"recorded attempt={attempt} sha={sha[:12]} metric={goal.get('metric', 'score')} "
        f"value={value:g} percent={shown} evidence_age={age_minutes:.0f}m"
    )
    print(
        f"guards={'ok' if guards_ok else 'FAILED'} runs={measured_runs}/{floor} "
        f"source=--record ({args.record})"
    )
    print(f"STOP {stop_value}")
    return 0 if hit_target else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default=".")
    parser.add_argument("--tag", default="iteration")
    parser.add_argument("--note", default="")
    parser.add_argument("--sha", default="")
    parser.add_argument("--timeout", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--record",
        default="",
        help=(
            "Log a gate run that happened outside score.py, as 'EARNED/TOTAL'. "
            "Use when a slow gate (a 20 minute device suite) was run directly. "
            "Evidence must exist and be newer than --record-max-age minutes."
        ),
    )
    parser.add_argument(
        "--record-max-age",
        type=int,
        default=120,
        help="Minutes an evidence file may predate now in --record mode (default 120).",
    )
    parser.add_argument("--guard", action="append", default=[], help="Guard line for --record mode.")
    parser.add_argument(
        "--from-report",
        default="",
        help=(
            "With --record omitted, read earned/total from a JSON report "
            "(keys score+total, passed+total, or score+possible)."
        ),
    )
    args = parser.parse_args()

    root = Path(args.dir).resolve()
    rel = root / ".relentless"
    goal_path = rel / "goal.md"
    if not goal_path.exists():
        print(f"no goal at {goal_path}; run scripts/init.py first", file=sys.stderr)
        return 2
    goal = parse_goal(goal_path)

    gate = goal.get("gate", "")
    if not gate or gate.startswith("TODO"):
        print("goal.md has no gate command yet", file=sys.stderr)
        return 2
    metric = goal.get("metric", "score")
    direction = goal.get("direction", "up")
    baseline = number(goal.get("baseline", ""))
    target = number(goal.get("target", ""))
    floor = int(number(goal.get("floor_attempts", "3")) or 3)
    lanes = int(number(goal.get("lanes", "5")) or 5)
    completeness = goal_gaps(goal)

    rel.mkdir(parents=True, exist_ok=True)
    (rel / "runs").mkdir(exist_ok=True)
    score_path = rel / "score.tsv"
    if not score_path.exists():
        score_path.write_text(HEADER)

    lock_path = rel / ".score.lock"
    lock = lock_path.open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("another score run holds the lock; one conductor per repo", file=sys.stderr)
        return 2
    lock.write(str(os.getpid()))
    lock.flush()

    sha = args.sha
    if not sha:
        try:
            sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except Exception:
            sha = "unknown"

    rows = load_rows(score_path)
    attempt = len(rows) + 1
    out_path = rel / "runs" / f"{attempt:04d}-{args.tag}.log"

    if args.dry_run:
        print(f"would run: {gate}")
        print(f"would write: {out_path}")
        print("STOP no")
        return 0

    if args.from_report and not args.record:
        try:
            report = json.loads((root / args.from_report).read_text())
        except Exception as exc:  # noqa: BLE001 - report unreadable input
            print(f"could not read --from-report {args.from_report}: {exc}", file=sys.stderr)
            return 2
        earned = report.get("score", report.get("passed"))
        total = report.get("total", report.get("possible"))
        if earned is None and isinstance(report.get("value"), (int, float)):
            earned = report["value"]
        if earned is None or total is None:
            # A metric-shaped report carries only a value. Record it as the
            # value with no denominator; direction decides the pass.
            if earned is None:
                print(
                    f"--from-report needs score/passed/value, got {sorted(report)}",
                    file=sys.stderr,
                )
                return 2
            args.record = str(earned)
        else:
            args.record = f"{earned}/{total}"

        # Derive guards from the report itself. Omitting --guard must never
        # turn a failing run green, so the report's own failures are guards.
        # Only generic keys are read: checks with a status, a threshold, and
        # any surface key the goal names in `report_fail_keys`.
        derived: list[str] = []
        checks = report.get("checks") or []
        failed_checks = [str(c.get("id", "?")) for c in checks if c.get("status") != "pass"]
        if failed_checks:
            derived.append("checks FAILED: " + ",".join(failed_checks))
        threshold = report.get("threshold")
        if isinstance(threshold, (int, float)) and isinstance(earned, (int, float)) and earned < threshold:
            derived.append(f"threshold FAILED: {earned} below {threshold}")
        for key, label in surface_fail_keys(goal):
            value = key_value(report, key)
            if value:
                derived.append(f"{label} FAILED: report value {value!r}")
        if derived:
            args.guard = list(args.guard) + derived
            print("guards derived from the report:")
            for line in derived:
                print(f"  GUARD {line}")

    if args.record:
        return record_existing(
            root=root,
            score_path=score_path,
            goal=goal,
            rows=rows,
            args=args,
            sha=sha,
            attempt=attempt,
        )

    print(f"[attempt {attempt}] {gate}", flush=True)
    started = dt.datetime.now(dt.timezone.utc)
    captured: list[str] = []
    killed_for_timeout = False

    def pump(stream, log) -> None:
        for line in stream:
            captured.append(line)
            log.write(line)
            log.flush()
            print(line, end="", flush=True)

    with out_path.open("w") as log:
        try:
            proc = subprocess.Popen(
                gate,
                cwd=root,
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                start_new_session=True,
                env={**os.environ, "RELENTLESS_ATTEMPT": str(attempt)},
            )
            reader = threading.Thread(target=pump, args=(proc.stdout, log), daemon=True)
            reader.start()
            try:
                code = proc.wait(timeout=args.timeout or None)
            except subprocess.TimeoutExpired:
                killed_for_timeout = True
                # The gate is a shell that may have spawned a device suite.
                # Kill the whole group so no orphan keeps driving the phone.
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                code = proc.wait()
                note = f"\nTIMEOUT after {args.timeout}s; gate killed\n"
                log.write(note)
                captured.append(note)
                print(note, end="", flush=True)
            reader.join(timeout=5)
            if killed_for_timeout:
                code = 124
        except Exception as exc:  # noqa: BLE001 - report gate setup failures
            message = f"GATE ERROR: {type(exc).__name__}: {exc}\n"
            log.write(message)
            captured.append(message)
            print(message, end="", flush=True)
            code = 127

    elapsed = (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
    combined = "".join(captured)

    parsed = parse_output(combined)
    metric_name = parsed["metric"] or metric
    metric_value = parsed["metric_value"]
    if metric_value is None:
        metric_value = parsed["score"]
    pct: float | None = None
    if parsed["score"] is not None and parsed["possible"]:
        pct = parsed["score"] / parsed["possible"] * 100.0
    elif metric_value is not None and baseline is not None and target is not None:
        pct = percent_from_metric(float(metric_value), baseline, target, direction)

    guards_ok = all(guard_is_green(line) for line in parsed["guards"])

    evidence = parsed["evidence"]
    if not evidence and goal.get("evidence"):
        evidence = [p.strip() for p in goal["evidence"].split(",") if p.strip()]
    evidence_missing: list[str] = []
    stale_after = started.timestamp() - 2.0
    for item in evidence:
        path = root / item
        if not path.exists():
            evidence_missing.append(item)
            continue
        newest = path.stat().st_mtime
        if path.is_dir():
            newest = max((child.stat().st_mtime for child in path.rglob("*") if child.is_file()), default=newest)
        if newest < stale_after:
            evidence_missing.append(f"{item} (stale)")

    gate_pass = code == 0

    # A pass needs a numeric observation, green guards, and the floor.
    if metric_value is not None and target is not None:
        if direction == "down":
            hit_target = float(metric_value) <= target
        else:
            hit_target = float(metric_value) >= target
    elif pct is not None and target is not None:
        hit_target = pct >= target
    else:
        hit_target = code == 0

    measured_runs = sum(1 for row in rows if row.get("kind") != "baseline") + (0 if args.tag == "baseline" else 1)
    floor_ok = measured_runs >= floor

    stop = (
        gate_pass
        and hit_target
        and guards_ok
        and floor_ok
        and not evidence_missing
        and not completeness
    )
    reason = []
    if not gate_pass:
        reason.append(f"gate exit {code}")
    if not hit_target:
        reason.append("target not met")
    if not guards_ok:
        reason.append("guard failed")
    if not floor_ok:
        reason.append(f"floor {measured_runs}/{floor} runs")
    if evidence_missing:
        reason.append("missing evidence: " + ", ".join(evidence_missing[:3]))
    if completeness:
        reason.append("goal incomplete: " + ", ".join(completeness))

    stop_value = "yes" if stop else "no"
    note = args.note or ("target met" if stop else "; ".join(reason))

    write_row(
        score_path,
        args.tag,
        attempt,
        sha,
        metric_name,
        metric_value,
        pct,
        parsed["guards"],
        evidence,
        stop_value,
        note,
    )

    print("")
    print(f"attempt={attempt} sha={sha[:12]} gate={'pass' if gate_pass else 'fail'} "
          f"metric={metric_name} value={metric_value} percent={'n/a' if pct is None else f'{pct:.1f}'}")
    print(f"guards={'ok' if guards_ok else 'FAILED'} evidence={'ok' if not evidence_missing else 'MISSING'} "
          f"runs={measured_runs}/{floor} lanes={lanes} elapsed={elapsed:.0f}s")
    print(f"STOP {stop_value}")
    return 0 if gate_pass else 1


if __name__ == "__main__":
    sys.exit(main())
