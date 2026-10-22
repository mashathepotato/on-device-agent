# Project docs

Keep the root tidy and the default agent context small.

| File or folder | Purpose | When to read |
| --- | --- | --- |
| [PROJECT.md](PROJECT.md) | Short project brief, boundaries, and commands | Every task |
| [DECISIONS.md](DECISIONS.md) | Agreed decisions and their reasons | When relevant to your scope |
| [plans.md](plans.md) | Project plan and links to detailed task plans | When planning or checking dependencies |
| [notes/](notes/) | Research, meeting notes, metadata, and detailed task plans | Only when linked from your task |
| [../context/](../context/) | Short agent handoffs and blockers | Your task and direct dependencies |
| [checks.yml.example](checks.yml.example) | Optional GitHub Actions workflow | When setting up CI |

Put supporting Markdown here instead of adding `PLAN.md`, scratch notes, or status files to the repository root. Keep one owner per task note, and coordinate changes to shared docs. Promote accepted decisions into `DECISIONS.md`; do not leave requirements buried in scratch notes. Local throwaway output belongs in ignored `.tmp/`, not committed documentation.
