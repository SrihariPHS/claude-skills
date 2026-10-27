# Grilling the user

_Read this in Step 0, before you ask the first question._

Step 0, item 4 in full.

4. **Grill until the frontier is empty.** This is the only cheap time to
   ask, so use it. A question is worth asking when the answer changes the
   build and the code, the repo and the docs cannot answer it.
   - Map the goal as a **design tree**: every decision branches into the
     decisions that hang off it. The **frontier** is every decision whose
     prerequisites are already settled. Ask the whole frontier in one round,
     numbered, with your recommended answer on each, worded so "yes" accepts
     it (question tool: `AskUserQuestion` in Claude Code, up to four per
     call). Settled answers push the frontier outward. A question that
     depends on another still-open question belongs to a later round.
   - **Facts are your job, never the user's.** If a question needs a fact
     from the repo, the tools or the web, send a scout. Do not block on it:
     ask the rest of the frontier now, and only the questions downstream of
     the scout wait. **Decisions are the user's**: put each to them.
   - Done when the frontier is empty, nothing is silently assumed, and a
     fresh implementer could build it without asking a single question.
   - Big, multi-file or hard-to-reverse goal: rounds until then, two or three
     is normal. Small, reversible goal: state the assumption in one line and
     go. Two or more readings that change the build: lay them out with a
     recommendation, never silently pick one. Destructive or outside-the-repo
     risk: ask before acting, not after.
   - The user already said they are gone: pick defaults, write them under
     Decisions, go. Mid-run, ask only for the Blocked list, and keep every
     unblocked piece of work moving while you wait for the answer.
   - **Push right.** When you do need the human mid-run, do all the prep
     first and ask once, late. Show a decision-ready brief (what was
     produced, why, a link to the artifact), never raw output.
   - **Push back.** If the user's plan, premise or correction conflicts with
     what the code or the evidence shows, say so with the evidence, give your
     recommendation, then do what they decide. Agreeing to be agreeable is a
     failure.
