# Subagents

_Read this before the first dispatch._

Doing everything yourself is the failure mode on a long goal. Your context
fills, your first theory becomes the only theory, and nobody checks your
work. Default to subagents. Do it yourself only when the task is a few tool
calls (a grep beats a subagent).

Dispatch when any of these is true:

- The reading is big (many files, logs, docs, prior art) and would flood your
  context. Send a **scout**, get back the conclusion and file:line pointers.
- Two or more pieces are independent. Send them in the **same turn** so they
  run in parallel.
- You need a second opinion that is not contaminated by yours. Send a fresh
  **critic** or **lens**.
- You are about to trust your own work. Send an **adversary** whose only job
  is to break it.

Roles:

| Role | Context | Writes | Returns |
|---|---|---|---|
| Scout | Fresh, read-only | Nothing | Findings with file:line, what it could not find |
| Lens | Fresh, read-only | Nothing | A reframing, a falsifiable theory, the cheapest probe, what kills it |
| Builder | Fresh, briefed | Its node's write set only | Diff, check command and output, short report |
| Adversary | Fresh, read-only | Scratch only | The input, state or sequence that breaks it, with a reproduction |
| Critic | Fresh, no builder history | Nothing | `SOUND` or `NOT-SOUND` and the biggest gap (the DeepSeek council) |
| Coverage auditor | Fresh, read-only | Nothing | Case table gaps, cases marked closed without evidence |

Rules:

- **Brief like they know nothing**, because they do not: the goal, the exact
  files to read, the exact files they may change, the check that proves it,
  and "stop and list questions instead of guessing". Quote GOAL.md.
- One builder per node. **One writer per file at a time.** Cap four running
  at once. Sequence real dependencies.
- Children never edit `.godgoal/`. You are the only one who writes state.
- The critic and the builder are never the same context. After two failed
  fix rounds on a node, use a fresh builder.
- **A child's report is a claim.** Re-run at least one check yourself and read
  the diff before you accept it. Do not use a subagent to rubber-stamp your
  own work.
- Argue with their results exactly like you argue with the council: verify,
  then accept, reject with evidence, or send it back with the specific gap.
- Use the model the user named. If none, use the session default. Do not
  switch models on your own. If no subagent tool exists, work inline and cap
  the outcome at `PARTIAL`, saying there was no independent check.
