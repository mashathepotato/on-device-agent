# Project context

Keep this brief current as the team agrees on the hackathon scope. Undecided items are explicit so contributors do not invent requirements.

## What we are building

- **Name:** On-device Agent
- **Problem and users:** Exploring local protection for people using AI agents: detect prompt injection in webpages/files or review sensitive data before sending. Final use case is not selected.
- **Success looks like:** A narrow, working offline demo on a consumer device, with a measured comparison between the original and fine-tuned model.
- **Out of scope:** Not decided
- **Deadline or demo:** Two-hour hackathon build; prepare a short final demonstration. Exact event deadline/presentation format to confirm.

## People and coordination

- **Human lead / final decision maker:** Masha (@mashathepotato)
- **Reviewer / integration owner:** Not assigned
- **Task board:** https://github.com/mashathepotato/on-device-agent/issues
- **Ownership:** One assigned owner per task; list files/areas in the issue. Resolve overlaps before editing. Shared files need explicit coordination.
- **Communication:** Task issues and PRs, with short handoffs in `context/handoffs/<owner>/<task>.md`. Notes become available to other worktrees through Git, not automatically. External messages require human authorization.
- **Supporting context:** `docs/plans.md` for the project plan; `docs/notes/` for detailed plans and metadata. Read only what the task needs.

## Technical context

- **Stack and architecture:** Application stack undecided. Required model: Liquid AI LFM2.5-1.2B; required training framework: White Circle Halo. Confirm the exact Base/Instruct checkpoint with organizers. Final inference must run locally on a consumer device; GPU training is provided.
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
- **App test / lint / build:** Not configured — add local commands when adding the app. CI is intentionally disabled to avoid automated notification emails.
- **Deploy:** Not configured; requires explicit authorization.

## Hackathon context

Read [the shared hackathon brief](notes/hackathon-brief.md) for constraints, candidate demos, dataset leads, and evaluation pitfalls. These are proposals, not an approved implementation scope.

## Current priorities

1. Agree on the project brief and choose the stack.
2. Define module boundaries and create scoped task issues.
3. Build the smallest useful end-to-end version.
