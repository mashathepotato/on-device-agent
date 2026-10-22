# On-device Agent

Hackathon project for an on-device agent. The product brief, application stack, and demo scope are still to be agreed.

## Get started

```sh
git clone https://github.com/mashathepotato/on-device-agent.git
cd on-device-agent
python3 -m unittest discover -s tests -v
```

The team tooling requires Git and Python 3.9+. No application dependencies are configured yet.

Read [AGENTS.md](AGENTS.md) and [docs/PROJECT.md](docs/PROJECT.md) before making changes. Agree on a task owner, scope, acceptance criteria, and reviewer in a GitHub task issue, then create your own branch and checkout:

```sh
python3 scripts/start-task.py YOUR-NAME TASK-SLUG
```

Open the printed checkout in your coding harness. Keep a short handoff in `context/handoffs/<owner>/<task>.md`, run the project checks, and open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## Team context

- [Project brief and commands](docs/PROJECT.md)
- [Current plan](docs/plans.md)
- [Shared decisions](docs/DECISIONS.md)
- [Agent handoffs](context/README.md)
- [Supporting docs](docs/README.md)

Run checks locally. CI is intentionally disabled for the hackathon to avoid automated notification emails. Repository rules and review requirements must be configured separately by an administrator.

Bootstrapped from [Agent Team Starter](https://github.com/mashathepotato/agent-team-starter), revision `ba2f2fcee3e0c929164284bfbedbb54adeaccff3`. The starter's MIT license is retained in [LICENSE](LICENSE).

## Clickbait spoiler MVP

Run local LFM inference, browser extension, Webis preparation, and baseline evaluation: see [setup and limitations](docs/SPOILER.md). No tuned checkpoint has been trained yet.
