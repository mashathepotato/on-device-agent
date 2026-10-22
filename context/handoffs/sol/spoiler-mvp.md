# Sol — spoiler MVP

- Status: implemented; parent review pending. Draft PR: https://github.com/mashathepotato/on-device-agent/pull/2.
- Branch: `agent/sol/spoiler-mvp` (sole app/data/eval/training owner).
- Scope: `spoiler/`, `web/`, `extension/`, `tools/`, `training/`, tests and setup docs.
- Run: `python3 -m spoiler.server`; model already pulled locally. See `docs/SPOILER.md` for extension origin/token pairing and all commands.
- Validation: 12 unit tests passed; both JavaScript syntax checks passed. Local UI real inference inspected by implementer and parent. Malicious Origin denied with HTTP 403; non-object/missing text requests return HTTP 400; offline selector serves 30 validation articles. Extension installation itself untested.
- Actual baseline: 30 official validation rows on M4 24 GiB / Ollama 0.32.5 / LFM2.5-1.2B-Instruct Q4_K_M. Revised prompt diagnostic median 1076 ms, p95 2210 ms; quote acceptance 10/30, token F1 .0487, single-reviewer displayed hook resolution 3/30. First model load request 8628 ms (7422 ms loading). Raw reports/data ignored; durable summary in `docs/notes/sol/baseline-summary.json`.
- Data: original 3200/800/1000; 21 exact article cross-split collisions; raw splits preserved, SFT train removes heldout article collisions (2504 examples). Validation SFT 631, final test excluded from Halo export.
- Remaining: organizer-approved exact checkpoint, H100/H200 access, Halo dense LFM smoke/backward check, actual training + same-quantization GGUF export, fair tuned comparison, untouched test evaluation. GPU recipe is proposed and untested. No tuned weights or improvement claimed.
- Parent reviewer should independently rerun tests and inspect final diff. Do not merge or introduce CI.
