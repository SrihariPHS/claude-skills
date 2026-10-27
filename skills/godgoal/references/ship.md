# Ship

_Read this before you file the PR._

Stop mode: skip to the gate and hand over.

### File the PR

- First check whether a PR for this branch already exists. Review the diff
  against the base branch yourself and make sure it matches the goal.
- Rebase onto the latest default branch first.
- The title usually becomes the commit message. Follow the repo's
  conventions (look at recent merged PRs and the history). Say why it
  matters, not what mechanism you touched.
  Bad: `perf(server): negotiate permessage-deflate on the websocket`.
  Good: `perf(server): cut websocket frame size by 70%+ with gzipping`.
- The description opens with the problem in plain words, taken from the
  user's request, then the solution in a line or two. Never lead with an
  inventory of what you changed.
  Bad: "Removed implicit workspace carry-over from every new-thread entry
  point and deleted three helpers..."
  Good: "My 'new worktree' default was ignored when starting threads on
  existing worktrees. Now your preferences always apply."
- Add one short line on how you proved it. End with the public model name
  and harness that made the change, e.g. `Created with <model> in <harness>.`
  Include subagent models that wrote part of it. Use the name the harness
  reports. If you do not know the model, name the harness and do not guess.
- Check the title, description, quotes and attachments for secrets and
  private details before you submit.
- Open a real PR, not a draft, so review bots run. If `gh pr create` fails on
  the GraphQL rate limit, open it through REST:
  `gh api repos/<owner>/<repo>/pulls -f title=... -f head=... -f base=... -F body=@<file>`.
- Do not post extra PR comments unless they serve the goal.

### Comments you post

Every comment you leave on the user's behalf (top-level, inline, replies to
bots or humans, written reasons before resolving or dismissing) starts with:

```md
> [!NOTE]
> 🤖 **<model> responding on behalf of <user>**

Actual comment starts here.
```

Use the verified model name and the user's name or GitHub login. If you do
not know the model, use the harness name. Attribution goes inside the note,
the reply goes outside it. No rule, heading, signature or second attribution.
Not for PR descriptions or commit messages.

Write it direct: lead with the conclusion, cite the code, check or
reproduction, no filler, no canned thanks, no status narration. Separate
verified fact from judgment. Reply to an inline review comment inside its
thread (`gh api repos/<o>/<r>/pulls/<pr>/comments/<id>/replies`), not as a
new top-level comment. Check for secrets first. Preview the Markdown,
post it, and confirm GitHub returned a URL. Resolve a thread only after the
reply posted.

### Babysit

Many repos have review bots. They help, and they are not always right.

- **Waiting:** never write your own `sleep` or polling loop. Run one
  blocking command under the Monitor tool (`gh pr checks <pr> --watch`),
  then end your turn so it wakes you. One watcher per PR, never two. If you
  end a turn with checks pending and nothing watching, the work dies. When a
  wake needs no action, say nothing. No "still waiting" filler.
- **Rate limits:** `gh pr view`, `gh pr checks` and `gh pr create` use
  GraphQL. When it runs out, REST is separate: `gh api repos/<o>/<r>/pulls/<n>`
  for the PR and `gh api repos/<o>/<r>/commits/<sha>/check-runs` for checks.
  Check `gh api rate_limit --jq .resources.graphql`. If remaining is near 0,
  wait for the reset with one background command. Never retry in a tight
  loop.
- **Checks green is not ready.** If the repo has review bots, ready means
  they reviewed the current head and no threads are unresolved.
- **Only act on checks and comments newer than your latest push.** Verify
  every bot finding against the source before changing code. Fix real
  findings and CI failures. Tell repo failures from infra flakes. If a bot
  finding is not worth doing, reply with a written reason and resolve it.
  If the repo has rules files for a bot (for example
  `.macroscope/check-run-agents/*.md`), read them before replying to that
  bot. CodeRabbit is advisory: treat findings like any other, never wait for
  it, never hold a merge for it.
- **Keep the PR the size the goal needs.** Fix real bugs in the intended
  case. Decline and list as follow-ups: unneeded tests, guards for edge cases
  that do not matter, extra compat, small perf costs. Prefer the fix that
  deletes or narrows code. Re-prove after every fix, before you push it.
- **Watch the base.** Rebase when main moves under you. If the PR goes BEHIND
  or DIRTY, or commits that landed after your last green run touch your
  files, rebase, push, wait for green again. If an overlapping PR makes this
  one obsolete, stop, report it, and ask before closing anything.
- Ignore automated reviews that only say "needs human review" if you are
  confident in the change.

### Gate

All true on the latest commit, or you do not ship:

- Every requirement green with proof you saw, no open cases in COVERAGE.md.
- Required checks green. Review bots finished, each finding fixed or
  dismissed with a reason. No human still requesting changes.
- Branch is up to date and GitHub says mergeable. Run `git fetch` and look
  again right before merging.
- Both critics `SOUND` on the current diff, not an old one.

**Ship mode:** merge the way the repo merges (check the allowed methods and
recent merged PRs), through branch protection as configured. If the repo uses
a merge queue or auto-merge, wait until GitHub says merged.

**Stop mode:** fetch the target, check the live PR's head, base, checks,
reviews and mergeability. Confirm it is open, not a draft, not set to merge
without the user. Then it is one of: ready to merge (leave it open and
unmerged), waiting on required human approval (confirm that is the real
blocker), or blocked (say what, what you tried, what you need). If someone
else merged it, report that instead.
