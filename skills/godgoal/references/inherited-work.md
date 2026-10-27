# Inherited work

_Read this when the goal starts from someone else's PR, branch or agent thread._

If the goal starts from someone else's PR, branch, or agent thread, it is
context, not proof. Do not defend it because it already exists.

- Resolve the handoff to the real code and the current head. Account for
  uncommitted work. Re-check the source later, it may have improved while
  you worked.
- Treat existing worktree changes as the user's. If the worktree is dirty or
  busy, use a disposable worktree. Fetch the latest origin for the branch,
  the default branch, and anything related before you start.
- **Pick a disposition before pushing anything.** Record the PR's intent
  (URL, state, base, head, author, checks, reviews, linked issues, full
  diff) and the smallest coherent goal it tried to reach. Then look at what
  landed on the base since it diverged, and at merged and open PRs that
  overlap. Ask: is the problem already solved, did APIs or schemas move, do
  both sides now own the same behavior, was the code deleted or simplified,
  would landing this create two ways to do one thing, is the benefit still
  worth the upkeep. No conflicts does not mean current.
  - **MODERNIZE**: goal still useful, shape still right. Rebase, resolve,
    test, update the branch.
  - **REWORK**: goal useful, a mechanical rebase would keep the wrong
    implementation. Do the smallest credible rewrite if the goal covers it,
    otherwise report and ask.
  - **CLOSE**: superseded, obsolete or not worth it. Cite evidence. Do not
    rebase an obsolete branch. Do not close it without permission.
  Age is not evidence. Sunk effort is not a reason. Be willing to say CLOSE.
- To rebase: branch or worktree at the recorded head, rebase onto the fresh
  base, resolve conflicts by the PR's intent and the base's newer rules. A
  conflict that exposes a product or architecture disagreement means
  reconsider the disposition, do not guess. Compare with `git range-diff` and
  read the final diff for lost or reintroduced behavior. Push with
  `--force-with-lease` tied to the head SHA you saw before.
- For a replacement PR, import the original commits onto a new branch and add
  your fixes as separate commits. Keep Git authorship and co-author trailers.
  Credit the contributors in the PR description and link the original. If the
  work will be squashed, keep human credit in the merge commit with verified
  identities, never guessed emails. A model attribution line does not replace
  contributor credit.
- Do not merge, close, change the base, or widen scope on the original PR
  without authorization.
