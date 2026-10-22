# Publisher error handling and visible-article fallback

- Owner: codex
- Updated: 2026-10-22
- Status: ready for review
- Branch: agent/codex/publisher-errors
- Scope: article error metadata, extension errors/source link, popup visible-article reader, tests and docs.

Publisher HTTP failures are no longer labelled local-server failures. Local transport errors alone give server-start guidance. Added explicit Open source normally link and Read this open article popup action using existing activeTab/scripting permissions. No automatic blocked-site retry or access-control bypass.

Validation: 20 Python tests passed; Node extension error tests passed; all changed extension scripts pass syntax checks and whitespace checks. Popup installation/UI test requires reloading the unpacked extension. The user's exact failing publisher URL is still requested; generic error distinction is verified with a simulated HTTP 403, not claimed as a reproduced live publisher fix.
