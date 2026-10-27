# Baseline, probe and theories

_Read this before your first probe, and whenever you write a theory._

### Baseline

Measure before changing, so change is attributable.

- Find the project's own gate (package scripts, build files, CI config,
  contributing docs). Do not invent a command when one exists. Run it once.
  Save exit codes and failing names to `evidence/baseline`.
- Record the commit and the working tree state.
- For measurements, record method, sample count and variance. One run is an
  anecdote. For visual work, capture every viewport, theme and state the goal
  names.
- Pre-existing red is not yours. Record it. Do not claim credit for it or
  take blame for it.

### Probe

Build the signal that decides the run **before** you fix anything. The probe is
the product. Spend disproportionate effort here. A good probe is:

- **discriminating**: its result differs between your leading theory and the
  rival, on the named case;
- **red-capable**: you have already seen it fail on the exact symptom, not a
  nearby one;
- **deterministic**: same verdict twice, or a stated rate if it is flaky;
- **fast** (seconds), **agent-runnable** (no "watch the screen"), and **one
  command or observation** another agent could re-run.

Cheapest mechanism that can fail on the goal's success condition: a failing
test at the seam, a live call against the running thing, a fixture diff against
known-good, a scripted real-browser interaction, a replayed trace, a
throwaway harness, a property or fuzz loop, a bisection, a differential
between two implementations or configs. Pick one that fits this goal.

### Theories: champion, rival, tombstone

For any bug, behavior or approach question:

- Write a **champion** theory and at least one **rival** that predicts a
  different result on the next probe. If you only have one explanation, or
  only a yes/no framing, split it into rivals first.
- Choose the probe because it separates them. A probe that cannot tell them
  apart is not a probe.
- A survivor is not proven, it is not yet falsified. A falsified theory gets a
  **tombstone** in LOG.md (what killed it) and is never reworded and reused
  without new evidence.
- Repeating the same theory with the same prediction on the same case is not
  persistence, it is a stall.
