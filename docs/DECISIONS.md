# Decisions

## 2026-10-22 — Bootstrap team collaboration

- **Status:** Accepted
- **Context:** The empty hackathon repository needs shared team instructions and onboarding.
- **Decision:** Adopt `mashathepotato/agent-team-starter` at revision `ba2f2fcee3e0c929164284bfbedbb54adeaccff3`, retain its MIT license, and enable its test workflow.
- **Consequences:** Future tasks use scoped ownership, isolated branches and worktrees, handoffs, and reviewed PRs. The application stack and product scope remain undecided.
- **Owner and reference:** Masha requested the initial setup, commit, and push directly to `main`. This authorization applies to the bootstrap; the normal team workflow applies afterward.

## 2026-10-22 — Remove CI for the hackathon

- **Status:** Accepted; supersedes the bootstrap decision to enable CI.
- **Decision:** Remove the GitHub Actions workflow and CI example. Run checks locally instead.
- **Reason:** Masha requested removal to avoid automated email notifications.
- **Owner and reference:** Masha’s follow-up to the initial setup; commit and push the cleanup to `main`.
