# Coverage and verify

_Read this before the first Verify pass, and when building COVERAGE.md._

A single point is not a sweep. For each requirement, in `COVERAGE.md`, list
the cases that could make it fail differently. Derive them from the goal along
four axes:

- **Contract**: the literal ask, the success condition, the actors.
- **Mechanism**: the approach and its assumptions.
- **Boundary**: interfaces, environments, layers above and below, external
  dependencies, trust boundaries.
- **State**: sequence, time, concurrency, empty and full, degraded,
  recovered, reloaded, hostile input.

Per axis, name the edges: the extremes, the boundary values, the case the
user meets first. Each case row: requirement, case, status, evidence file.

- **probed**: fresh evidence this pass.
- **excluded**: a proof or an equivalence shows it cannot differ, written
  down. A bare note is not coverage.
- **open**: unprobed, with a reason and the probe that would close it.

Each requirement needs at least two cases, including one success case that was
seen red before green. Visit the cheapest discriminating case first, then
edges, then uncovered cases, then high-blast and adversarial ones, then
re-check what was green. Every pass visits at least one case and updates the
file. An open case blocks `DONE` and `IMPOSSIBLE`, unless it is the one case
the named human block is about.

### Verify

Run all of this and save real output to `evidence/`:

1. Each requirement's check, with red before green proven.
2. The full project gate, not just touched files. No new failures vs baseline.
3. Scope audit: the diff against the declared write sets. Nothing outside it,
   no new dependencies without a reason.
4. Re-read the goal. Does the artifact satisfy the ask, or an adjacent thing
   that was easier to measure? Write the one sentence that connects them.
5. Mutation proof: revert the change or break the expectation, watch the
   check go red, restore. If it stays green, the check is broken.
6. Two consecutive clean runs with nothing changed between them.
7. Re-run the cases the change can affect, plus the ones that were green.
8. Depth audit: grep the diff for stubs, TODO/FIXME, mock-only paths,
   hardcoded returns, skipped tests, catch-all exception handling, disabled
   checks. Every layer complete or excluded.
9. For UI: look at it at every viewport, theme and state the goal names, and
   check console errors, overflow, tap targets and keyboard access. For
   anything with numbers: variance and a noise floor.

Any failure goes back to Build as a fix round. Never to the report with a
softer claim.

## Evidence rules

- **Name the evidence kind**: static read, unit test, fixture or replay, live
  run, production. Never pass one off as another. A mock is not a live check.
- A claimed limitation ("the API can't", "this needs a credential") needs the
  verbatim error, a documented statement or a live probe. Probe before you
  ask or block.
- Never cite a command whose stderr you silenced. Two agents agreeing, or
  one source read twice, is one datum.
- A checked null result ("ran X, found nothing") is a success. An unsupported
  positive claim is worse than silence.
- Redact secrets from anything you save or show: write `<REDACTED>`. Build
  loops against environment variables, so credentials stay out of evidence.
