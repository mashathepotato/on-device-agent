# Project context

Keep this brief current as the team agrees on the hackathon scope. Undecided items are explicit so contributors do not invent requirements.

## What we are building

- **Name:** On-device Agent
- **Problem and users:** Not decided
- **Success looks like:** Not decided
- **Out of scope:** Not decided
- **Deadline or demo:** Not decided

## People and coordination

- **Human lead / final decision maker:** Masha (@mashathepotato)
- **Reviewer / integration owner:** Not assigned
- **Task board:** https://github.com/mashathepotato/on-device-agent/issues
- **Ownership:** One assigned owner per task; list files/areas in the issue. Resolve overlaps before editing. Shared files need explicit coordination.
- **Communication:** Task issues and PRs, with short handoffs in `context/handoffs/<owner>/<task>.md`. Notes become available to other worktrees through Git, not automatically. External messages require human authorization.
- **Supporting context:** `docs/plans.md` for the project plan; `docs/notes/` for detailed plans and metadata. Read only what the task needs.

## Technical context

- **Stack and architecture:** Not chosen; this starter does not include an application.
- **Source layout and module boundaries:** Define when choosing the stack.
- **Shared interfaces:** Record contracts and their owners here before parallel implementation.
- **External services / data:** None configured. Add only approved services and data sources.
- **Environment:** Copy `.env.example` to `.env` only if needed. Never commit real secrets.

## Commands

These check the starter tooling, not your future application:

```sh
python3 -m unittest discover -s tests -v
```

- **App install:** Not configured
- **App dev server:** Not configured
- **App test / lint / build:** Not configured — replace these entries and enable/extend the CI example in `docs/checks.yml.example` when adding the app. The starter checks are already enabled in `.github/workflows/checks.yml`.
- **Deploy:** Not configured; requires explicit authorization.

## Current priorities

1. Agree on the project brief and choose the stack.
2. Define module boundaries and create scoped task issues.
3. Build the smallest useful end-to-end version.
