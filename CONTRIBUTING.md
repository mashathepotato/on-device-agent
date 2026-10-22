# Contributing

Read [AGENTS.md](AGENTS.md) and the [project context](docs/PROJECT.md). The same ownership and review workflow applies to humans and agents.

## First-time setup

Clone this repository and agree on the project brief in `docs/PROJECT.md`. The starter requires only Git and Python 3.9+; your application can use any stack.

CI is intentionally disabled for the hackathon to avoid automated notification emails. Run the starter tests locally with `python3 -m unittest discover -s tests -v`.

The repository administrator should configure a ruleset for the default branch: require PRs and a reviewer; block force pushes and deletion. Review the available protection options for your GitHub plan. Template copies do not automatically inherit repository settings, secrets, or permissions. Enable issues if unavailable. This starter does not configure these controls for you.

## Take a task

Create a **Team task** issue. Agree on one owner, a reviewer, scope, and acceptance criteria before starting. If you cannot use issues, keep the equivalent assignment in a human-approved shared document. For outside contributors, fork first and open the PR against the upstream repository.

```sh
python3 scripts/start-task.py YOUR-NAME TASK-SLUG
```

The helper fetches `origin`, detects its default branch (or uses `--base`), and creates a fresh branch and worktree. In a repo without a remote it uses local `main`. It does not edit, stash, or clean your current checkout. It refuses existing branch or directory names. Open the printed path in your harness; each agent should have a separate harness session in its own checkout.

If the default branch cannot be detected, specify the intended base explicitly:

```sh
python3 scripts/start-task.py alex api --base origin/develop
```

For dependent tasks, agree on the dependency and pass its branch as `--base`. On a fork, `origin` is your fork: sync it with upstream before starting, or fetch upstream and explicitly use `--base upstream/main`.

## Keep context useful

Copy `context/handoffs/_template.md` to `context/handoffs/<owner>/<task>.md`. Keep it current and brief; put detailed plans and supporting metadata under `docs/`, following `docs/README.md`. Each task owner edits their own note. Other worktrees see updates only after you push and they fetch; share the branch/path in the task or PR. Read `context/README.md` for the handoff workflow.

## Ship a change

Run the commands in `docs/PROJECT.md`. Inspect `git diff` and stage only your task’s files. Commit, then push your task branch:

```sh
git push -u origin HEAD
```

Open a PR using the included template. Report what passed and what could not run. A reviewer checks scope, behavior, and interactions with other PRs. Only an authorized integrator merges, and overlapping changes are integrated one at a time. Rerun affected checks after resolving conflicts.

After merging, return to the main clone. Remove your own clean worktree with `git worktree remove PATH`; do not use `--force`. Delete your own merged local branch with `git branch -d BRANCH`. Squash merges may require manual verification before branch removal; never force-delete work without checking it is preserved.

## Improve this starter

Keep it small, stack-neutral, and usable without installing dependencies. Include a regression test for changes to the worktree helper. Add application-specific tooling in your own project, not in this generic template.
