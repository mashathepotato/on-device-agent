# Publisher error handling and visible-article fallback

- Owner: codex
- Updated: 2026-10-22
- Status: ready for review
- Branch: agent/codex/publisher-errors
- Scope: article error metadata, extension errors/source link, popup visible-article reader, tests and docs.

Publisher HTTP failures are no longer labelled local-server failures. Local transport errors alone give server-start guidance. Added explicit Open source normally link and Read this open article popup action using existing activeTab/scripting permissions. No automatic blocked-site retry or access-control bypass.

Validation: 20 Python tests passed; Node extension error tests passed; all changed extension scripts pass syntax checks and whitespace checks. Popup installation/UI test requires reloading the unpacked extension. The user's exact failing publisher URL is still requested; generic error distinction is verified with a simulated HTTP 403, not claimed as a reproduced live publisher fix.

## Follow-up: automatic metadata-only estimate

User requested URL/title/Google snippet fallback instead of opening blocked articles. Implemented local LFM preview score on fetch failure, clearly labelled preview-only; no spoiler/evidence generated. Added no-fetch `/api/preview` path, card-scoped snippet capture, actual field provenance and failed-fetch timing. 25 Python tests and Node error tests passed. Actual Harvard ADS HTTP 405 automatically fell back to a 40/100 estimate, 381 ms local inference (3.92 seconds including failed request). Reload the extension to enable new snippet capture; exact user-reported 403 publisher still unspecified. Current response schema/metadata match the extension's existing score display even before reload, but then only URL/title are available.

## Follow-up: concise result panels

User requested only the existing colored score and a one-sentence summary. Removed success-panel disclaimers, reasons, evidence paragraphs, source links, timings, and status text from extension, popup, and demo. Preview inference now returns a short topic summary alongside its estimate; grounding/provenance fields remain in the API. Full-article results still use the selected source sentence. Preview protocol bumped to v2 for cache invalidation.

Validation: 26 Python tests, Node extension error tests, JS syntax and whitespace checks passed. Two real local LFM preview calls produced short topic summaries in 418–539 ms. Scores remain an uncalibrated baseline. Installed extension files synced; Chrome must reload the extension and refresh existing tabs to load new content scripts.
