# Plan

_Read this before you plan: situation, landscape, decision, decomposition._

Three things, in this order, before any decomposition. Write them in LOG.md.

- **Situation.** What exists at the seam and what its consumers assume. The
  **mechanism** by which it misses the goal (a symptom just restates the
  complaint). Each constraint marked hard, soft or self-imposed. Unknowns,
  ranked by what would change the plan if answered the other way. Every
  premise the approach needs, marked untested / supported / falsified, with
  the probe that would settle it. An untested premise reaches Build only
  with a probe attached.
- **Landscape.** Read the field before choosing. Name the closest existing
  solution (in this repo, in a dependency, in the wild) and the best-known
  alternative, and why each is insufficient. Prior art: read upstream code,
  docs, issues and papers. Qualify a source before it moves the plan: is it
  primary, how current, does it match your constraints and scale (otherwise it
  is an analogy, say so), can you re-run it. A finding is a change, not a
  link: claim, source, and what it changes in the plan. A finding that changes
  nothing is `NOTED`. Research is read-only, bounded, dated, and informs the
  goal without widening it. A borrowed design is a candidate, never the task.
  Depth follows novelty, not diff size: an in-repo precedent needs the
  precedent and its differences. No precedent anywhere needs two independent
  sources and a stated gap. A claim that the ask is impossible, or that the
  current approach is optimal, needs the strongest counter-example searched
  for and the search recorded.
- **Decision.** Two or three approaches with their trades, at least one that
  is not the field's default so the field does not own your frame. The chosen
  one, why the closest existing solution is not enough, the rival it must
  beat, what evidence would reverse the choice, the blast radius, the
  rollback.

Then decompose. A **node** is one requirement, one owner, one write set, one
check, a set of edge cases. Right-sized means a fresh builder can do it without
asking. One writer per file at a time. Sequence real dependencies. Schedule a
probe for each top risk before anything depends on it.

**Pre-flight conflict scan** before the first builder starts. Read the plan
against GOAL.md and the constraints. Where two nodes claim the same file, or a
node contradicts a requirement or a hard constraint, or the plan assumes
something the baseline disproved, settle it now with a ruling in LOG.md. Plan
defects found mid-build cost a rebuild.
