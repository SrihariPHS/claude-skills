# When the goal is a bug

_Read this when the goal is a bug, a regression or a performance problem._

**No fix without a confirmed root cause.** Fixing the symptom is whack-a-mole.

- **The feedback loop is the skill.** Everything else is mechanical. With a
  tight pass/fail signal that goes red on this bug, you will find the cause.
  Without one, staring at code will not save you. Spend disproportionate
  effort here, be creative, refuse to give up. Reading code to build a theory
  before a red command exists is the exact failure.
- **Tighten it.** Faster (narrow the scope, cache setup), sharper (assert the
  specific symptom, not "did not crash"), more deterministic (pin time, seed
  RNG, freeze network). A 30-second flaky loop is barely better than none.
- **Flaky bug:** the goal is a higher reproduction rate, not a clean repro.
  Loop the trigger 100 times, parallelise, add stress, narrow the timing
  window. A 50% flake is debuggable. A 1% flake is not, so raise it.
- **No loop possible?** Stop and say so. List what you tried and ask for
  access to an environment that reproduces it, a redacted artifact (HAR, log,
  core dump), or permission to add temporary instrumentation. Do not
  hypothesise without a loop.
- **Check it shows the user's symptom**, not a neighbour. Wrong bug, wrong fix.
  Then **minimise**: cut inputs, callers, config and steps one at a time,
  re-running after each cut, until every remaining element is load-bearing.
- **Three to five ranked hypotheses before testing any.** Each falsifiable:
  "if X is the cause, changing Y makes it vanish". No prediction means it is
  a vibe, so discard or sharpen it. Single-hypothesis generation anchors on
  the first plausible idea. Change one variable at a time. A debugger beats
  ten logs. Never "log everything and grep".
- **Tag every debug log** `[DEBUG-xxxx]`. Cleanup is one grep. Untagged logs
  survive.
- **Perf bugs:** logs lie. Baseline first (timing harness, profiler, query
  plan), then bisect. Measure first, fix second.
- **Regression test before the fix**, at a seam that exercises the real
  call-site pattern. A shallow seam gives false confidence. If no correct
  seam exists, that is itself a finding: report it.
- **Cleanup:** the original repro is green, the test passes, no tagged logs
  left, throwaways deleted, and the winning hypothesis is stated in the PR so
  the next debugger learns.
- A fix that touches more than five files: stop and write a ruling on the
  blast radius, and put it in front of the critic.
