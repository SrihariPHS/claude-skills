---
name: go
description: Use when the user says "/go" or "go". Research how it is done well first, find real examples, then do the work properly and finish it. Never hand back a half-done, stubbed or guessed result. The light version of godgoal for one task, no state files, no PR pipeline.
---

# Go

Do the task, properly, to the end. This is the short version of godgoal: same
standard, no ceremony. Use it for one task you can finish in this session.
Use godgoal when the work is long, needs a PR, or the user is leaving.

The failure this stops is the **unfinished result dressed as finished**: built
from guesses instead of examples, a happy path that works once, a stub, a
TODO, a "should work".

## 1. Say what you are doing

One line: what you think the user wants and what "done" looks like. Make "done"
something you can check (a command, a screenshot, a number). If two readings
would change what you build, or the premise looks wrong, say so now and give a
recommendation. Ask only if the answer changes the build and the code, the
repo and the docs cannot answer it. Otherwise state the assumption and go.

## 2. Research before you build

Do not build from memory. Find how this is done well, and copy the shape of
the best example. In this order, stopping when the next source stops changing
your plan:

1. **This repo.** Search for the closest existing thing: a component, a
   handler, a test, a script that already does something like this. Read it
   and its neighbours. Match its style, naming and structure. Reuse it.
2. **What is already installed.** The standard library, the framework, the
   dependencies you already have. Check them before adding anything.
3. **The primary source.** The official docs, the library's own examples and
   tests, the upstream code. Read the version this project actually uses.
4. **Real examples in the wild.** Well-maintained repos that solve the same
   problem, the issue or discussion where the problem was worked out, a
   write-up from someone who shipped it.

For each example you use, note: what it is, why it applies (same constraints,
same scale, same version, or it is only an analogy and you say so), and what it
changes in your plan. A source that changes nothing, drop. A blog post that
nobody ran is a claim, not evidence. Two sources that copy each other are one.

If the reading is big, send a scout subagent and take back the conclusion
with file:line pointers. Do not flood your own context.

Then say, in two or three lines: the closest existing solution, why it is not
enough as it stands (or why it is), and the approach you picked. If you cannot
name a closest example, you have not researched enough.

## 3. Build it properly

- Follow the example's shape. Smallest change that does the whole job. No
  adjacent refactors.
- Test first where it is testable. Watch the check **fail** before you make it
  pass. A check you never saw fail proves nothing.
- Cover the edges, not just the happy path: empty, maximum, wrong type, the
  second run, the reload, the error and the slow path, whatever applies to
  this task. Write the list, then probe each. A case is tested or it is
  excluded with a reason.
- Every layer the task touches is finished. No stubs, no placeholders, no
  TODO or FIXME, no hardcoded returns, no mock standing in for the real path,
  no skipped or disabled test. If the full depth cannot be reached, say what
  is missing and why. Do not ship the hollow version as done.
- Odd things you notice that are not the task (a failing unrelated test, a
  messy file): note them at the end, leave them alone.

## 4. Prove it

Proof is something you ran this turn and read.

- Run the project's own checks (typecheck, lint, tests, build), not only the
  ones you added. Compare with how it was before you started.
- For anything visible, run it and look at it. Mocked tests passing do not
  show the experience works.
- Break it on purpose once: revert the change or flip the expectation and
  watch the check go red, then restore. If it stays green, the check is broken.
- Re-read the user's ask against what you built. Is it the thing they asked
  for, or an easier thing nearby?
- Words like "should work", "probably" and "looks right" mean you have not
  proved it yet.

If the task is big or risky, send one fresh subagent with only the ask, the
diff and the evidence, and tell it to try to break the result. Check its
claims yourself before you accept them. Argue with it: if a finding is wrong
or out of scope, say so with evidence.

## 5. Finish, then report

Keep going until it is done and proven. Do not stop at a first working
version, and do not end on "let me know if you want me to continue". If you hit
a real wall (needs credentials, a destructive action, a fact only the user
has), stop and ask one clear question with your recommendation first. Anything
else, decide and carry on.

Report in plain words, first line the honest status: `Done`, or what is missing.

- What you built and which example it follows (name it).
- Proof: the commands you ran and what they showed.
- Edges you tested, and any you excluded and why.
- What you did not verify, and why.
- Things you noticed and left alone.

Saying a partial result is done is the one failure this skill exists to stop.
