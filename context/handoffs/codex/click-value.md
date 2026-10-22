# Worth-clicking score

- **Owner:** codex
- **Updated:** 2026-10-22
- **Status:** done
- **Branch:** main (user explicitly requested commit/push to main)
- **Scope:** Fast click-value heuristic, API response, extension and local-feed badges, tests/docs.

Added a 0–100 estimate with green/amber/red recommendation, short explanation, and explicit baseline/not-fine-tuned label. It evaluates scanned article substance, practical/explanatory detail, hype, repetition, and answer availability, without an extra inference call. It is not a confidence or credibility score. Existing spoiler training labels are not click-value supervision.

Checks: 19 unit tests, JavaScript syntax and whitespace checks passed. Local server restarted from main. Browser smoke verification is recorded in chat. The installed unpacked extension checkout will be synchronized to main; reload the extension and refresh pages to see the new badge. No CI or training added.
