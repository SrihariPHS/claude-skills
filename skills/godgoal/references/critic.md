# Critic, council and arguing

_Read this before you write the first review brief._

Two fresh contexts, two axes. The critic never gets your reasoning or your
confidence. It gets GOAL.md, the diff, and the raw evidence. It defaults to
`NOT-SOUND`, approval is earned, and it should try to break the result at the
edges, the empty and max cases, the reload and the degraded state, and any
open or excluded rows in COVERAGE.md.

- **Spec**: did we build what the goal asked? Missing or partial requirements,
  scope creep, implemented-but-wrong, open cases presented as closed.
- **Standards**: is it built the way this repo builds things? Documented
  standards first, then smells the tooling does not already catch.

Each returns `SOUND` or `NOT-SOUND` and the single biggest gap on its axis.
Do not merge the reports. A clean style cannot excuse a wrong spec.

The critic is the council, run as two reviews, one after the other:

```bash
delegate deepseek --effort xhigh -f .godgoal/review-spec.md
delegate deepseek --effort xhigh -f .godgoal/review-standards.md
```

DeepSeek V4.1 Flash, max effort, read-only. If `delegate` is missing or
fails, say so in the report. Do not swap in another model silently, and do
not call your own self-review a critic. With no independent critic the best
outcome is `PARTIAL`, naming the self-assessment.

- The brief is self-contained, the worker has no memory of this chat:
  GOAL.md, the base sha and diff command, the check results, the axis, and
  the reply format `VERDICT: APPROVE|CHANGES`, then each finding as
  `[blocker|should|nit] file:line claim. Fix: ...`.
- Run `git status --short` first. Never stash, discard or include unrelated
  changes. Do not edit scoped files while a review runs.
- One model has blind spots. Cover them with your own checks. An APPROVE is
  never proof.
- Severity: blocker = the intended case is wrong. should = a real bug in the
  intended case that callers will hit. nit = everything else, including rare
  cases, other paths, small perf, extra compat. Re-grade severities yourself.
- Budget: 3 rounds. Round 1 full, later rounds only changed code and open
  findings. Extend to 5 only for security, auth, data loss or concurrency,
  with a blocker still open and evidenced. Stop early on nits only. A
  timeout or no answer is not approval.
- Keep a ledger in LOG.md: finding id, severity, outcome.

**Argue.** You are not a stenographer.

- Verify every finding against the code before touching anything: restate the
  requirement, check it against reality, ask whether it is right for THIS
  codebase, whether it breaks something, whether the reviewer had the full
  context. Do not implement before you have verified.
- **No performative agreement.** Never "you're absolutely right", "great
  catch" or thanks, in replies or in comments. State the fix or the
  requirement. Actions show you heard it.
- If any item is unclear, clarify all of them before implementing any. Items
  are often related, and partial understanding gives the wrong fix.
- **YAGNI check.** When a reviewer wants it "implemented properly", grep for
  real usage first. Unused: propose removing it. Used: do it properly.
- Agree: smallest fix, prefer deleting or narrowing code over a new lock,
  cache, helper or option. Add one focused test that fails without the fix if
  the goal needs it. Order: blocking issues, then simple fixes, then complex
  ones, one at a time, testing each. Disagree: say why, with file:line, a
  test, or output. Out of scope: decline in one line, add to Follow-ups.
- Pushed back and turned out wrong? State it flat ("checked X, it does Y,
  fixing") and move on. No apology, no defence.
- Cannot verify a finding? Say so and say what you would need.
- After fixes, re-run checks and check diff size. If review grew it, cut first.
- Never agree just to end the loop. Never accept a finding that widens the
  diff past the goal. Defending scope is your job.
- A dispute still open after two replies: both sides in 2-3 lines each, to the
  user. Budget running out is not agreement.
