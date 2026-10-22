# Agent coordination

Short notes for the next agent. Keep plans and background material in `docs/`.

## Leave a handoff

Copy [`handoffs/_template.md`](handoffs/_template.md) to `handoffs/<owner>/<task>.md`. Use the same owner and task names as your branch. Each task owner edits their own note; do not overwrite another agent’s handoff. Link related notes when work depends on another task.

Update the note when a decision, blocker, or next step changes, and before handing off. Keep it short: current state, affected files, checks, and what the next person needs to do. Link to detailed plans, logs, and PRs instead of pasting them here. Never include secrets or private chat transcripts.

## Read only what you need

Start with `AGENTS.md` and `docs/PROJECT.md`, then read your task’s handoff and notes for its direct dependencies. Open supporting docs only when relevant. Do not load the whole folder into every agent session.

## Share deliberately

Worktrees have separate files. A note in your checkout is not instantly visible to other agents. Commit and push it on your task branch, then link its branch/path in the task issue or PR when posting is authorized. A reader can fetch and inspect it without switching checkouts:

```sh
git fetch origin
git show origin/agent/alex/add-login:context/handoffs/alex/add-login.md
```

Replace the example branch and path with the actual handoff. Unmerged notes stay on their task branches; merged notes are available on the default branch. Check the date, branch, and linked task before relying on a note. The task issue (or human-approved shared assignment) remains the source of truth for ownership; handoff files are not locks or a live message bus.

Mark completed notes `done` with the PR or commit that contains the work. Read completed notes only when you need their history. New work gets a new note.
