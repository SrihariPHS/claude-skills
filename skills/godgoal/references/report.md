# Final report

_Read this when you write the final report._


First line is the outcome, and it must not mislead someone who stops reading
there. If it is not `DONE`, the first line says what is missing. If it is
`DONE` with a concern you could not close (an intermittent bug, something that
needs staging), put the concern on that first line too: `DONE (concern: ...)`.

Write for someone who was not watching: plain words, a little context first,
jargon defined once. If a reader would say "wait, what?", re-pitch it.

```
Outcome: <one of the above> - one sentence
Changed: <files/areas, one-line why>
Evidence: R1 -> <check> -> pass (<file>)
          R2 -> ...
Coverage: <probed>/<excluded>/<open>; open cases and why, or none
Theories: leading -> survived/falsified; rival -> survived/falsified
Landscape: <closest existing solution and its gap; what changed the plan>
PR: <link, merge commit or open state, reviewer/critic outcome and rounds>
Decisions I made for you: <rulings>
Declined: <follow-ups>
Not verified: <what, and why>
Noted: <adjacent problems left alone>
```
