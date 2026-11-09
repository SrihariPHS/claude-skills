# claude-skills

My Claude Code skills.

| Skill | Say | What it does |
|---|---|---|
| `godgoal` | "/godgoal" | Drives a long goal to a verified end while I am away: locks the goal, sweeps edge cases, tests rival theories, reviews with a fresh critic, files and babysits the PR. |
| `go` | "/go" | The light version for one task: research real examples first, build properly, prove it, never hand back an unfinished result. |
| `relentless` | "/relentless" | Drives one measured goal to a hard target: a gate that must be proved sensitive, a floor of measured runs, five lanes, and a stop predicate that never relaxes. |

## Install

```bash
git clone git@github.com:SrihariPHS/claude-skills.git
cp -R claude-skills/skills/* ~/.claude/skills/
```

`godgoal` keeps its detail in `references/`, read only when needed. Copy the whole folder.
`godgoal` expects `gh` and, for its council review, a `delegate` CLI that runs DeepSeek.
`relentless` needs `python3` and nothing else.
