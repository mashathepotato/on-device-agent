# Project context

Keep this brief current as the team agrees on the hackathon scope. Undecided items are explicit so contributors do not invent requirements.

## What we are building

- **Name:** On-device Agent
- **Problem and users:** Spoiler MVP experiment: reveal the answer clickbait headlines withhold, using the actual article. See `context/spoiler-idea.md`.
- **Success looks like:** Fast local spoiler extraction, with a fair original-versus-fine-tuned comparison and grounded evidence. Improvement must be measured, not assumed.
- **Out of scope:** Not decided
- **Deadline or demo:** Two-hour hackathon; working offline demo on a consumer device.

## People and coordination

- **Human lead / final decision maker:** Masha (@mashathepotato)
- **Reviewer / integration owner:** Not assigned
- **Task board:** https://github.com/mashathepotato/on-device-agent/issues
- **Ownership:** One assigned owner per task; list files/areas in the issue. Resolve overlaps before editing. Shared files need explicit coordination.
- **Communication:** Task issues and PRs, with short handoffs in `context/handoffs/<owner>/<task>.md`. Notes become available to other worktrees through Git, not automatically. External messages require human authorization.
- **Supporting context:** `docs/plans.md` for the project plan; `docs/notes/` for detailed plans and metadata. Read only what the task needs.

## Technical context

- **Stack and architecture:** MVP implementation in progress by Sol on `agent/sol/spoiler-mvp`. Required model family LFM2.5-1.2B; required training framework Halo. See `context/spoiler-idea.md` for scope and evaluation constraints.
- **Source layout and module boundaries:** `spoiler/` Python API/inference, `web/` local demo, `extension/` MV3 popup, `tools/` data/evaluation, `training/` proposed Halo recipe. Sol owns these on the MVP branch.
- **Shared interfaces:** Record contracts and their owners here before parallel implementation.
- **External services / data:** None configured. Add only approved services and data sources.
- **Environment:** Copy `.env.example` to `.env` only if needed. Never commit real secrets.

## Commands

These check the starter tooling, not your future application:

```sh
python3 -m unittest discover -s tests -v
```

- **App install:** Python venv + `pip install -r requirements.txt`; install Ollama and pull official LFM weights (see `docs/SPOILER.md`).
- **App dev server:** `.venv/bin/python -m spoiler.server` → http://127.0.0.1:8765
- **App test / lint / build:** `python3 -m unittest discover -s tests -v`; `node --check web/app.js`; `node --check extension/popup.js`. CI remains disabled.
- **Deploy:** Not configured; requires explicit authorization.

## Current priorities

1. Agree on the project brief and choose the stack.
2. Define module boundaries and create scoped task issues.
3. Build the smallest useful end-to-end version.
