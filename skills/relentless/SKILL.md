---
name: Relentless
description: Drive one measurable goal to a hard target with a real gate, a floor of measured runs, and a self-contained loop. Use for /relentless, "run until 99/100", "keep looping", "2x faster", "24/7 agents", "relentless", "run until done", or any goal where agents must measure, change, verify, and repeat.
---

# Relentless

You own the predicate, the gate, and the verdict. Workers change code. You accept or revert. A change counts only when a command you ran proves it on the real surface, at one commit SHA, with an artifact you opened.

## Qualify

Run these five checks before Phase 0. Each is binary. Any `no` stops the loop before it starts and the reason goes in the reply.

| Check | Pass condition |
| --- | --- |
| Number | The goal reduces to one number with a direction and a target the operator accepted. |
| Gate feasibility | A command can produce that number from the real surface without a human in the loop. |
| Repetition | The gate can run the baseline count in the `Numbers` table inside the available budget without changing the artifact. |
| Bar | A comparison artifact opens in under 5 minutes. |
| Authority | The branch, worktrees, and test methods the loop needs are permitted without a new approval per iteration. |

If `Repetition` fails because one run exceeds the iteration budget in the `Numbers` table, reduce the gate's scope to the checks the metric depends on. If `Gate feasibility` fails because a human must judge, replace the metric with a measurable proxy the human check correlates to, state the correlation method in `goal.md`, and add the human check as a Critic lane.

### Numbers

Every quantity in this skill, in one place. Use these values. Do not invent others.

| Quantity | Value | Why |
| --- | --- | --- |
| Baseline runs before Phase 3 | 5 | Distinguishes real movement from noise on a fresh tree. |
| `floor_attempts` | 3, or 5 when noisy or device-bound | Stops one lucky run from ending the loop. |
| Runs per iteration | 2 at the head | One run cannot separate a delta from drift. |
| Interleave order when the metric drifts | baseline, head, baseline, head | Cancels time-correlated drift. |
| Keep threshold | max(2 percent of baseline, 2 times the baseline spread) | A smaller delta is noise. |
| Baseline spread | p90 minus p10 of the 5 baseline runs | Robust to one outlier. |
| Plateau | 3 iterations below the keep threshold | Ends a dead hypothesis family. |
| Pivots before stop | 3 | Ends a dead direction. |
| Iteration budget | 90 minutes wall clock | Longer means the gate or the hypothesis is wrong. |
| Wake interval when unattended | 30 to 60 minutes | Below 30 wastes runs, above 60 lets a branch sit. |
| Lanes | 3 minimum, 5 default, 10 maximum | Below 3 has no independent check. |
| Critic runs per kept iteration | 1 maximum | More is re-litigating taste. |
| Respawns after an incomplete lane report | 1, then record a gap | A gap never counts as a pass. |
| Bar open time | under 5 minutes | A bar nobody opens is not a bar. |

## State

Three state files in `.relentless/`, committed with the work, plus a generated `resume-prompt.md` that points at them. Any cold agent resumes from the state files. Nothing else is authoritative.

### `.relentless/goal.md`

A fenced block first, prose after. The scorer reads the block. Nine required fields plus one optional:

```
<!-- relentless:begin -->
metric: <stable name>
direction: <up|down>
baseline: <measured number>
target: <number that ends the loop>
floor_attempts: <integer, at least 3>
gate: <one shell command, run from the repo root>
evidence: <comma separated paths the gate writes>
bar: <one real artifact you can open>
lanes: <integer 3 to 10>
report_fail_keys: <dotted.path:label, ...>
<!-- relentless:end -->
```

`metric` moves in the `direction` given. `up` means higher is better, `down` means lower is better. `baseline` is never a guess. `floor_attempts` is the number of measured runs required before a pass counts, so one lucky run cannot end the loop. Use the `Numbers` table values: 3 by default, 5 when the metric is noisy or depends on a device.

`gate` exits 0 only on pass, and prints these lines to stdout:

```
SCORE <earned>/<possible>
METRIC <name> <value>
GUARD <text>
EVIDENCE <path>
```

`report_fail_keys` is optional. Each entry is a dotted path into the gate's JSON report plus a label. A truthy value at that path becomes a failing guard. Populate it when a run can earn the target score while violating a surface condition that `goal.md` or the operator names as required. Leave it empty when every required surface condition already fails a check.

`GUARD` lines carry checks that must not regress. Any line containing `fail`, `failed`, `error`, `errors`, `failing`, `dirty`, or `missing` is red unless negated by a preceding `0`, `no`, `zero`, or `none`. `evidence` lists paths that must exist and be newer than the run that claims them.

### `.relentless/score.tsv`

One row per gate run, tab separated. Columns in this order: `ts`, `kind`, `attempt`, `sha`, `metric`, `value`, `percent`, `guards`, `evidence`, `stop`, `note`. `kind` is `baseline` or `iteration`. `stop` is `yes` or `no`. Append only. Never edit a row.

### `.relentless/ledger.tsv`

One row per iteration. Columns: `ts`, `phase`, `decision`, `why`, `evidence`, `result`. `evidence` is a path, a SHA, or a PR number, never a paragraph. `result` is `kept`, `reverted`, `inconclusive`, or the predicate state.

## Scripts

This skill ships two commands in its `scripts/` directory: `init.py` and `score.py`. Run them from the target repo, passing the full path to the script, because the skill directory is not the working directory. The rule text below is authoritative if a script is unavailable.

`init.py` writes the three state files and the resume prompt. It takes `--metric`, `--direction`, `--baseline`, `--target`, `--floor-attempts`, `--gate`, `--evidence`, `--bar`, `--lanes`, and `--report-fail-keys`, matching the `goal.md` block one-for-one, plus `--dir` for the repo root, `--body` for the prose section, and `--upgrade-block` to prepend the block to an existing prose goal without losing it. It refuses to run with any required value empty, `--floor-attempts` below 3, or `--lanes` outside 3 to 10, and writes nothing in that case. Run it once per repo, after the baseline is measured.

`score.py` takes `--dir`, `--tag` of `baseline` or `iteration`, `--note`, `--sha` to pin a measurement to a commit, `--timeout` in seconds, `--dry-run`, `--from-report`, `--record`, `--record-max-age` in minutes, and repeatable `--guard`. Use `--from-report` when the gate is slower than one tool call. Use `--record` only when the gate writes no JSON; it accepts `EARNED/TOTAL` or a bare value for a metric with a direction.

`score.py` runs the gate, streams its output, appends the row, writes the raw log to `.relentless/runs/`, and ends with `STOP yes` or `STOP no`. It exits 0 when the gate passed and 1 when it failed. It refuses to run while another scorer holds `.relentless/.score.lock`.

Every stop decision requires a complete `goal.md`: baseline, target, direction of `up` or `down`, a non-empty evidence list, a bar, a gate command, and `floor_attempts` of at least 3. A gate that passes against an incomplete goal still prints `STOP no` and the missing fields appear in the row's note.

When a gate takes longer than one tool call, run the gate yourself and log the result from its artifacts. `--from-report <json>` reads `score` or `passed` or `value`, plus `total` or `possible` when present, and compares against the target using the goal's `direction`. It derives red guards from the report: any check whose `status` is not `pass`, a score below `threshold`, and every truthy key named in `report_fail_keys`. `--record` works without JSON but then you supply each failing `GUARD` line through `--guard`. Both reject evidence older than `--record-max-age` minutes, default 120, and both apply the floor.

## Phase 0. Contract

1. State the goal in one sentence: who it serves and what changes for them.
2. Name the bar. A bar qualifies only if it is an artifact you can open or execute in this session and compare against the candidate in under 5 minutes. State its path or URL and the exact command or action that opens it. If you cannot open it, it is not a bar. If the operator named none, write three candidates, each with its open method, and stop for the pick. Do not proceed on an assumed bar.
3. Run the gate on the untouched tree the number of times the `Numbers` table gives. `baseline` is the median of those runs. Record the spread as p90 minus p10 of the same runs. Tag those rows `baseline`; they are calibration, not iterations.
4. Write `goal.md` with all nine required fields, plus `report_fail_keys` when a surface condition can pass every check yet still violate the goal. Take `floor_attempts` and `lanes` from the `Numbers` table.
5. Freeze it. Any later change to `metric`, `direction`, `target`, `gate`, or fixtures is a ledger row that names the old value, the new value, the reason, and the evidence, followed by a fresh baseline at the count in the `Numbers` table.

Do not write product code before the gate exists. The gate is the deliverable of Phase 0.

## Phase 1. Gate

The gate is the only thing that ends the loop, so it is the most dangerous code in the repo. Treat it that way.

1. Drive the surface the metric is defined on. When `goal.md`, the operator, or the bar names a surface, hardware, input method, or network condition, the gate uses exactly that and nothing weaker. Mock only at a boundary the product itself isolates, and print the boundary as a `GUARD` line so it appears in every run.
2. Print the four line types above, one value per line, with no prose around them.
3. Write at least one artifact that opens without the repo and lives at a path listed in `evidence`. The artifact contains the score, the declared total, and one status per executed check. A run with no artifact cannot stop the loop.
4. Prove sensitivity in both directions, 2 consecutive runs each. Break the build on purpose; the gate must exit non-zero on both runs. Restore it; the gate must exit 0 on both runs. Any other outcome stops Phase 1.
5. Prove it counts the work. The number of executed checks must equal the number reported, and the reported denominator must equal the declared total. Any shortfall fails the gate even when the ratio passes.
6. Prove the artifact under test is the artifact built. The SHA-256 in the report must equal the SHA-256 of the file the gate ran, computed in the same run. A mismatch fails the gate.

Freeze the gate, the fixtures, the thresholds, and the expected outputs. A worker may read them, never edit them. A gate change is its own iteration, with the old baseline re-measured afterwards.

## Phase 2. Lanes

Five lanes by default. Each is a fresh agent with a self-contained brief. Lanes never message each other. They exchange artifacts and commit SHAs only.

| Lane | Job | Write scope |
| --- | --- | --- |
| Conductor | contract, gate, verdicts, ledger, ship | `.relentless/` and PR state |
| Builder | one hypothesis per launch | one worktree, one branch |
| Verifier | rerun the gate at one SHA, audit the diff | a report file only |
| Critic | blind comparison against the bar | a report file only |
| Device or environment | physical run or clean checkout | artifacts, tags |

Lane rules:

- One writer per worktree. Two writers on one file invalidates both measurements.
- The Verifier runs on a different model family from the Builder. The Critic runs on a different family from both when a third exists.
- The Verifier never sees the Builder's reasoning. The Critic never sees the score, the diff, or the Builder's reasoning.
- Size the lane count by the `Numbers` table. Two lanes that always agree are one lane.
- A brief has exactly these eight fields: goal line, repo path, base SHA, worktree path, write scope, forbidden paths, exact commands, report format. A brief missing any of them is rejected before it runs.
- Reject a report with no SHA, no artifact, or a claim the artifact does not show. Ask once. On the second miss, respawn the lane with the same brief and the missing field called out.

Builder brief format: hypothesis with a mechanism, reproduction of the current number, the change, `git diff --stat`, fast checks, the SHA.

Verifier report format: `VERDICT: VERIFIED | NOT VERIFIED | INCONCLUSIVE`, the SHA, each gate run's exit code and numbers, the baseline comparison, each guard, the evidence paths and what they showed, the diff risk, and a gate integrity line. `INCONCLUSIVE` is not a pass. A verdict covers exactly one SHA.

Critic report format: `WINNER: A | B`, the single biggest gap as a change a builder can make, why a user would notice, the second gap, confidence, and the artifact paths captured for each side.

## Phase 3. Loop

Each iteration is one experiment, bounded by the iteration budget in the `Numbers` table, measured from the Builder launch to the ledger row. If a single iteration exceeds it, split the gate into a fast gate for iterations and a full gate for stops, or reduce the hypothesis to the smallest change that can move the metric. Never extend the budget to finish a hypothesis.

1. Read `goal.md`, the last 5 ledger rows, and the newest 2 run logs.
2. State one hypothesis in this exact shape, all four parts required: (a) the observed number, (b) the mechanism that produces it, (c) the change that alters the mechanism, (d) the predicted new number. A statement missing any part is rejected before launch.
3. Launch the Builder in its own worktree with the brief above. The change is the smallest one that tests the hypothesis.
4. Run the gate twice at the head. Same device, same inputs, same order. If the metric drifts with time, interleave: baseline, head, baseline, head.
5. Compute the keep threshold by the `Numbers` table. Keep only when the delta in the target direction meets it and every guard is green.
6. On a keep, launch the Verifier at the exact SHA. On `NOT VERIFIED` or `INCONCLUSIVE`, revert.
7. On a revert, `git revert --no-edit` or reset the worktree. Never hand-edit a partial revert.
8. Run the Critic when the goal includes a quality judgement a number cannot capture. At most one Critic run per kept iteration.
9. Append one ledger row, push the branch, and check the PR. Then run `score.py` once more only if the previous step changed code.

Keep rules:

- One change, one measurement. Never stack two untested hypotheses and attribute the result.
- Revert a win that breaks behavior, a guard, or simplicity for a number a user cannot feel.
- A change with no predicted number is reverted, not tested. A change whose prediction was not checked is reverted, not kept.
- One commit per kept change, staged by path.
- A number belongs to a SHA. If HEAD moved, the number is stale.

Plateau rule: when the number of consecutive iterations from the `Numbers` table falls below the keep threshold, that family of hypotheses is dead. Re-read the source or profile, combine near misses into one hypothesis, then pivot category. After the pivot count from the `Numbers` table with no movement, write the dead-end report: what was tried, the numbers, where the limit is, and the best remaining idea. Stop.

## Phase 4. Ship

1. Open the PR before the first keep, non-draft, so required checks and any automated review run alongside the work.
2. Merge only when all of these hold at the head SHA: a Verifier `VERIFIED`, required checks green on the base it lands on, every bot finding either fixed or dismissed in writing with a reason, and no human review requesting changes.
3. A new push resets the verdict. Re-verify the new SHA; do not reuse the old one.
4. Rebase onto the base branch, wait for green, then merge. Never merge while behind or conflicted.
5. Rerun the gate on the merged commit. A merge can change behavior. Fix forward if it does.
6. A tag, public release, or signed artifact needs the operator's standing grant, recorded in the ledger. Without it, stop at a merge-ready branch. The first release in any repo always stops for a checkpoint.
7. Release notes carry: the score, the target, the artifact SHA-256, the commit, the device or environment the gate ran on, and links to the artifacts.

## Phase 5. Continuity

An agent turn ends. The loop survives because every wake reads state, not history.

- Schedule an unattended wake at the interval in the `Numbers` table.
- Every wake runs the same resume sequence: read `goal.md`, the last 5 ledger rows, `score.tsv`, and the newest 2 run logs. Then continue at the next iteration. Never re-plan from scratch.
- One conductor per repo. The scorer holds `.relentless/.score.lock`. A stale lock is cleared only after confirming no scorer process is alive.
- A wake that finds uncommitted changes with no ledger row explaining them stops and inspects. Do not build on unknown work.
- A wake that finds the gate artifact older than the head SHA re-runs the gate before trusting any number.

## Stop rules

The loop stops on the first true condition.

1. `score.py` prints `STOP yes`, and a Verifier `VERIFIED` exists for the same SHA. The scorer alone is not enough, because it cannot read the diff. If the scorer says `STOP yes` and no verdict exists, launch the Verifier and wait for it before treating the loop as done. The scorer's `STOP yes` requires: gate exit 0, metric met in the named direction, all guards green, at least `floor_attempts` measured runs, and every evidence path present and fresh.
2. The pivot count in the `Numbers` table is reached with no movement, and the dead-end report is written.
3. The operator says stop.
4. The next step needs a decision only the operator can make, or needs an ingredient that cannot be built: hardware, key, model, permission.

Never stop because a check is green, because CI passed, because a PR merged, or because one lane said so. Never relax the gate, raise the floor, or widen the tolerance to make a pass.

## Reply

Open with the goal in one line and the predicate. Then: baseline to final with the delta and the number of runs, iterations kept and reverted, each lane's verdict with its SHA or artifact, the ledger path, the PR or release link, and the next hypothesis you would try. Name every number as measured, inferred, or guessed.
