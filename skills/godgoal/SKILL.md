---
name: godgoal
description: Use when the user says "godgoal" or "/godgoal". Drives a goal to a verified end while the user is away. Locks the goal into numbered requirements with checks that can fail, sweeps edge cases, tests rival explanations, escalates or rebuilds on a stall, reviews with a fresh critic, then files, babysits and merges the PR. Never stops at a shallow probe or a comfortable story.
---

# Godgoal

If the user triggered this, they are not watching. Your updates go unread
until long after you stop. You own the goal from now until it is finished
and proven. Not drafted. Finished.

The failure this skill exists to stop is the **confident non-result**: a
quick probe, one theory, or a happy path presented as a conclusion, while the
edge cases and the alternatives were never tested. Everything below makes
that report hard to write by accident.

Four things hold for the whole run:

1. **The artifact is the authority.** Not your summary, not a child's report,
   not the user's optimism.
2. **Progress is measured, not narrated.** A pass moves a requirement's check,
   closes an edge case, or kills a theory. Motion without one of those is not
   progress.
3. **The goal is frozen. Your explanation of how to reach it is disposable.**
   Requirements and checks do not change. Theories and plans get replaced
   when evidence says so.
4. **The run is `RUNNING` until a real ending.** A checkpoint, a compaction, a
   subagent's report or a tier change is not an ending.

This folder is the whole procedure. Nothing else needs to be installed. This
file is the core you always follow. The files in `references/` hold the detail
for one situation each. Read one when its stub below says to, not before.

## Modes

- **Ship** (default): carry it all the way (merged PR, deployed, delivered,
  whatever the goal says).
- **Stop** ("godgoal stop", "don't ship"): do all the work, hand over at the
  gate. Never merge, deploy or publish.
- **Time box** ("godgoal 4h ..."): at the limit, checkpoint and report
  honestly. A time box ending is not "done".
- **Read-only** ("audit", "don't change anything"): findings, evidence and a
  plan. No source edits.

## Do, don't narrate

- Decide, record the ruling, run the next probe. Do not wait for permission,
  encouragement or a status update.
- **No dangling promises.** "Let me look", "I'll check", "next I'll inspect"
  ends a turn only if the probe ran and its result is pasted, or a checkpoint
  names the exact next command. A turn ends with evidence, a checkpoint, a
  real ending, or a named block. Never with a promise.
- No "should I continue?", "is this a good stopping point?", "here is what I
  would do next" as a final. Those are stalls dressed as politeness.
- No final report while a cheaper open edge case remains.
- **Depth is part of done.** Every layer the goal names (data, logic,
  boundary, state, UI, docs, tests) is either complete at the goal's bar or
  excluded on paper. No stub, placeholder, TODO, mock-only path, hardcoded
  return, skipped test or disabled check presented as the deliverable. The
  smallest change is not the shallowest change.
- **No environment archaeology.** An odd thing about the OS, container,
  network or dependency tree is data, not a new task. If it blocks the goal,
  make it the next probe with a bound. If not, log `NOTED:` and move on.
- **No template capture.** Examples in this file are shapes, not tasks. Derive
  requirements, edge cases and probes from this goal.

## The grant

You may: commit, push your own branch, `--force-with-lease` that branch after
a rebase, merge once the gate passes (ship mode only), and use whatever test
method gives direct proof (browser, simulator, dev server, screenshots). An
"ask before testing" rule in a project file is replaced by this request.
Rules that name the correct command or check still apply.

You may not: delete data, touch production, change things outside the repo,
force-push other branches, close PRs, use `--admin` or any bypass. Those are
questions for the user (see Blocked).

Work on a branch, in an isolated worktree if the main one is dirty or in use.
Never start on the default branch.

**Destructive commands need a stop and a look**, even inside the grant:
`rm -r`/`rm -rf`, `DROP`/`TRUNCATE`, `git push --force` (anything but
`--force-with-lease` on your own branch), `git reset --hard`,
`git checkout .`/`git restore .`, `kubectl delete`, `docker rm -f`/`system
prune`. Check the target first. If it is not clearly yours and disposable, it
is a Blocked question.

Stop mode adds: never merge, enable auto-merge, enter a merge queue, or push
to the default branch. Before you start and before every push, check the PR
for auto-merge or a queue entry and turn it off. Report that you did. If you
cannot prevent automatic merging, say so before going further.

## State on disk

Everything lives in `.godgoal/`. Add it to `.git/info/exclude` so it never
gets committed. If it is not on disk, it did not happen.

- `GOAL.md`: the frozen contract.
- `LOG.md`: the run. Per entry: what changed, which requirement, evidence,
  next step. Also holds the theory ledger.
- `COVERAGE.md`: the edge-case table.
- `evidence/`: command, exit code, output tail, named by requirement and pass.
  Never paraphrase output.

You after a compaction must be able to resume from these files alone.
`/godgoal` with no goal and an existing `.godgoal/` means resume. Never
restart finished work.

## Step 0: Lock the goal

Most failed runs fail here. Do this before touching code.

1. Read the repo and the request. Check that the goal makes sense. If the
   premise is wrong or there is a much simpler way, say so now. Argue with the
   user once, up front. A wrong premise is a legitimate `NOT-NEEDED` or
   `IMPOSSIBLE`, with proof.
2. Write `.godgoal/GOAL.md`:

```
Goal (user's words, quoted):
What I think that means (one line):
Requirements (each has a check that can FAIL; no check = PREFERENCE, not counted):
  R1. <statement>  check: <command or observation>
  R2. ...
Constraints (hard / soft / self-imposed, with source):
Out of scope (at least one tempting thing):
Risk: low | touches shared state | destructive or outside the repo
Decisions I made for the user:
Follow-ups (real work I am not doing):
```

   "Works" is not a requirement. "`pnpm test checkout` passes and the cart page
   shows the discount at 375px and 1440px" is. Self-imposed constraints are
   candidates to relax. Hard ones are the goal.
3. **Echo test.** Spawn a fresh subagent. Give it ONLY the user's raw words and
   the repo. Ask: "What does done look like? What is out of scope?" Compare
   with GOAL.md. If they differ, the goal is ambiguous.
4. **Grill until the frontier is empty.** Ask only what the repo and the docs cannot answer.
   Map the goal as a design tree and ask the whole frontier each round, numbered, with your
   recommended answer on each. Facts are your job (send a scout). Decisions are the user's.
   Done when a fresh implementer could build it without asking a single question. Small goal:
   state the assumption in one line and go. User gone: pick defaults and log them. Read
   `references/grill.md` for the full protocol, including pushing back and pushing the human
   checkpoint right.
5. Seed `COVERAGE.md` and the theory ledger (below).

GOAL.md is frozen. Requirements and Out of scope change only if the user says
so. New ideas go under Follow-ups, marked `PROPOSED:`.

## Inherited work

Goal starts from someone else's PR, branch or thread? It is context, not proof. Read `references/inherited-work.md` before touching it. It covers the MODERNIZE / REWORK / CLOSE call, rebasing without losing intent, and keeping contributor credit.

## The loop

```
FRAME > BASELINE > PROBE > PLAN > BUILD > VERIFY > CRITIC > ADVANCE
```

Any stage may end a turn with a checkpoint. Only a real ending ends the run.

### Tiers

The tier is the depth of evidence, not the size of the diff. Write it in LOG.md.

- **Quick**: bounded recon. At least two fresh read-only lenses, run in
  parallel, cheapest probes, short. A tiny, obvious goal can still be proven at this tier, but
  Quick can never declare `IMPOSSIBLE`. Inconclusive means escalate.
- **Deep** (default for real work): full edge sweep, rival theories, fresh
  critics.
- **Overhaul**: rebuild the approach from the frozen goal (see Stall).

Move up on any of: an inconclusive quick pass, a stall, three fix rounds with
no check changing state, a theory falsified with no rival left, a verdict
proposed with open edge cases. Never move down inside a run.

### Baseline, probe, theories

Baseline first: run the project's own gate once, save it to `evidence/baseline`, and treat
pre-existing red as not yours. Then build the probe before any fix. It must be discriminating
(it separates your champion theory from a **rival**), red-capable, deterministic, fast,
agent-runnable and one command. Every theory needs a rival that predicts differently. A
falsified theory gets a tombstone in LOG.md and is never reused reworded. The same theory with
the same prediction on the same case again is a stall. Read `references/probe.md` before your
first probe.

### When the goal is a bug

No fix without a confirmed root cause, and the feedback loop is the whole skill. Read `references/bugs.md` first. It covers building and tightening the loop, flaky bugs, minimising, hypotheses, regression seams and cleanup.

### Plan

In this order, before any decomposition: **situation** (the mechanism, not the symptom), **landscape** (the closest existing solution and why it is not enough; no plan without one), **decision** (two or three approaches, one that is not the field's default, and what would reverse the choice). Then nodes: one requirement, one owner, one write set, one check. Read `references/plan.md` before planning. It has the source-qualification rules, depth by novelty and the pre-flight conflict scan.

### Build

- One node at a time. Read a neighbour before writing yours, match its style.
- Test first where testable. Let machines auto-fix what machines can fix.
- Rhythm: typecheck often, run single test files often, the full suite once
  at the end of the node, not after every edit.
- After each node, before anything depends on it, check it against the
  requirement and the repo's standards. Cheap for a small node (re-run the
  check, read the diff). A fresh reviewer for a risky one. Do not save all
  review for the end.
- Commit one concern at a time in the repo's commit format.
- Stay inside the node's write set. If you truly must leave it, write a
  one-line ruling (what, why, blast radius, what would reverse it) and go on.
- Record blockers when they happen.
- Never break what you were not asked to change. No adjacent refactors,
  dependency bumps, formatting sweeps or renames.

### Coverage and verify

A single point is not a sweep. `COVERAGE.md` lists, per requirement, the cases that could fail differently (axes: contract, mechanism, boundary, state). Each is `probed`, `excluded` with a written proof, or `open`, and an open case blocks `DONE`. Verify means: every check seen red then green, the full project gate against baseline, a scope audit of the diff, a mutation proof, two clean runs, a depth audit for stubs and TODOs, and a look at the real thing. Read `references/verify.md` for the full lists before the first Verify pass.

### Critic

Two fresh contexts, two axes, never given your reasoning: **Spec** (did we build what the goal asked) and **Standards** (is it built how this repo builds things). Both run on DeepSeek V4.1 Flash at max effort, read-only, one after the other:

```bash
delegate deepseek --effort xhigh -f .godgoal/review-spec.md
delegate deepseek --effort xhigh -f .godgoal/review-standards.md
```

No `delegate` means no independent critic, which means no `DONE` (the best outcome is `PARTIAL`). Its APPROVE is never proof. **Argue**: verify every finding first, no performative agreement, smallest fix, decline out-of-scope items in one line, never agree just to end the loop. Read `references/critic.md` before the first brief. It has the brief format, severity grades, the 3-round budget and the full argue rules.

### Advance

- Green, both critics `SOUND`, no open cases, success rows green with an earlier
  red: ready to ship, or `DONE` if there is nothing to ship.
- Red with a new theory: fix round. Five rounds per node. Rounds four and
  five use a fresh implementer.
- Same failure twice, or three fix rounds with no check changing state: stall.
- Three fixes that each reveal a new problem elsewhere: question the
  architecture. Do not attempt fix four.
- A case that cannot be probed: write the exclusion proof, or leave it open.
  Open is not green.

Each pass ends with LOG.md updated (theory ledger, coverage delta, next case,
tier), or a checkpoint that names them.

## Stall and overhaul

A stall is mechanical: the same check and output twice; three passes with no case, check or theory moving; three fix rounds with no check changing state; a metric flat across three experiments; three failed hypotheses. The answer is an **overhaul** (retire the plan and theories, re-derive the cases from the frozen goal, two new rivals, fresh agents), never a stop and never the same attempt again. No `IMPOSSIBLE` without a completed overhaul. Read `references/stall.md` when one triggers.

## Subagents: use them

Doing everything yourself is the failure mode on a long goal. Default to subagents unless it is a few tool calls. Dispatch when the reading is big (scout), pieces are independent (same turn, in parallel), you need an uncontaminated second opinion (fresh critic or lens), or you are about to trust your own work (adversary). One writer per file, four running at most, children never edit `.godgoal/`, brief them as if they know nothing, and a child's report is a claim: re-run a check and read the diff. Use the model the user named. No subagent tool means work inline and cap the outcome at `PARTIAL`. Read `references/subagents.md` for the role table and brief rules before the first dispatch.

## Stay on task

You will run long. Context will compact. You will drift. So:

- **Re-read `.godgoal/GOAL.md` first** at every wake, after every compaction,
  and before every commit. Not from memory. From the file.
- **Before each chunk of work, name the requirement it serves**, one line in
  LOG.md. Cannot name one? Do not do it. Add it to Follow-ups.
- Smallest change that works. Fix the case that happened, not every case that
  could. Review loops grow diffs one cheap fix at a time. Cut first.
- The user's later messages are corrections to the goal, not noise. Fold them
  into GOAL.md under a dated line and tell them what changed.
- **After a compaction, trust LOG.md and `git log` over your memory.** The
  most expensive failure on long runs is re-dispatching work that already
  landed. Log every dispatch and every commit hash as you go, and check the
  log before dispatching anything.
- End each phase (research, plan, build, review) with a LOG entry that a cold
  start could continue from. Phase boundaries are the safe places to lose
  context. The middle of a node is not, so finish or checkpoint the node first.
- If you must stop mid-run (time box, context, a block), write
  `.godgoal/HANDOFF.md` for a fresh agent: goal state, what is done, what is
  next, the exact next command, open cases. Link artifacts by path or URL
  instead of repeating them. Redact secrets.
- Looping on the same diagnostic, the same file or fix variants? Stop and
  reassess. That is a stall.

## Proof rules

Proof is something you observed this session. Not "should work".

- Commands: exact invocation, exit code, output tail.
- No claim without a command you ran this turn. Words like "should",
  "probably", "seems to", and "Done!" before the check ran are the tell.
  Confidence is not evidence. Partial verification proves nothing about the
  rest. A linter passing is not the build passing.
- A check must be seen **failing first**. If it cannot fail, it is not a check.
- A subagent's report is a claim. Re-run at least one check yourself and look
  at the actual diff.
- Read the evidence rules in `references/verify.md` before the first Verify pass: evidence kinds,
  claimed limitations, silenced stderr, null results, redaction.
- Green mocked tests do not prove the experience works. Run the app and look.
- A late discovery that a requirement cannot be verified changes the outcome in
  the report, loudly. Not silently.
- Cannot find a way to prove a requirement? You do not have full confidence.
  That is a block, not a shrug.

## Ship

Stop mode: skip to the gate and hand over. Otherwise read `references/ship.md` before filing. It has the PR title and description rules, the comment format, the babysit rules (one watcher, rate limits, bots, the base branch) and the full gate.

The gate, on the latest commit: every requirement green with proof you saw and no open cases; required checks green; review bots finished; no human requesting changes; branch up to date and mergeable after a fresh `git fetch`; both critics `SOUND` on the current diff. Ship mode merges the way the repo merges, through branch protection, and waits until GitHub says merged. Stop mode leaves the PR open and unmerged with auto-merge off.

## Blocked

A question in a normal message goes unseen and the thread looks finished.
Use the question tool. Put everything in it, in this shape: `STATUS` (what is
blocked), `REASON` (which block below), `ATTEMPTED` (what you tried), and
`RECOMMENDATION` (options, yours first), plus the PR link. Ask only when you
cannot go on alone:

- A destructive or irreversible action.
- Anything involving credentials, auth, permissions or secrets.
- A side effect outside the worktree the grant does not cover (production,
  deleting data, closing a PR, other branches, paid use at scale).
- A fact only the user holds that the code, the evidence and the public record
  do not settle.
- You cannot prove a requirement, or the gate cannot pass and you cannot fix it.
- Another change makes this one obsolete.

Name which one it is. A "block" that is really difficulty is a stall, and it
goes to overhaul. A plan so broken that every path is a guess is a stall too.

Everything else, decide with a sensible default and log it as:
`Ruling: <what> | <why> | <cost if wrong> | <what would reverse it>`.

No question tool, or no answer? Take the safe path: leave things unmerged and
open your final message with the question.

## Endings

| Outcome | Means | Needs |
|---|---|---|
| `DONE` | Every requirement met and proven. | Success rows green with an earlier red on the same check, no open cases, both critics `SOUND`, Deep or Overhaul tier. |
| `STOPPED AT GATE` | Stop mode, ready for the user to merge. | Same as DONE, PR open and unmerged. |
| `IMPOSSIBLE` | The frozen goal cannot be satisfied. | Every case probed or excluded with proof, a red success check, a completed overhaul that probed a new case, a falsified leading theory, the strongest counter-example searched. A mood or a budget is not proof. |
| `NOT-NEEDED` | Already satisfied, or the premise is false. | A proof file with a positive result and a citation, from a green check you ran. |
| `BLOCKED` | A named block from the list above is the next step. | One crisp question, everything else finished and evidenced. |
| `PARTIAL` | Stopped early: the user stopped it, a time box ended, or no independent critic was available. | A checkpoint, the open cases, the named gap, the next probe. Never presented as `DONE`. |
| `RUNNING` | A resumable checkpoint, not a report. | State on disk, next case, theory pair, next probe. |

The weakest requirement sets the outcome. No critic, no `DONE`. The pass cap
and the time box are checkpoints, not successes.

## Final report

The first line is the outcome and must not mislead someone who stops reading there. If it is
not `DONE` it says what is missing, and a `DONE` with a concern you could not close says so on
that line. Write for someone who was not watching: plain words, context first. Read
`references/report.md` for the template.

`PARTIAL` reported as `DONE` is the one failure this skill exists to prevent.
