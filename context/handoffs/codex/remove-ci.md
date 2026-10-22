# Remove CI

- **Owner:** codex
- **Updated:** 2026-10-22
- **Status:** done
- **Task / PR:** User requested removal of CI as a follow-up to bootstrap.
- **Branch:** main (bootstrap follow-up)
- **Scope:** Workflow and example removal; CI references in team docs.

## Current state

Removed the GitHub Actions pipeline and its example. Updated team docs to use local checks and recorded the decision.

## For the next agent

- **Next action and owner:** Team continues with local checks; keep CI disabled unless requested.
- **Dependencies / blockers:** None.
- **Checks and results:** Staged diff reviewed; `git diff --cached --check` passed. Tests were not rerun because only CI configuration and documentation were removed or edited.
- **Relevant context:** [Decision](../../../docs/DECISIONS.md).
