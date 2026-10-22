# LFM summary + click score training

- Owner: Codex. Reviewer/human lead: Masha.
- Branch: `agent/codex/lfm-score-training`.
- Status: data pilot and real baseline complete; GPU access missing; training/comparison pending.
- Scope: new `training/click_model/`, focused tests, own docs. Existing deployed application untouched.
- Added shared sentence+score v2 prompt, teacher labelling/resume/provenance, Halo export with overlength rejection, candidate single-GPU recipe and real collator preflight, matched uncached baseline/tuned benchmark with trivial controls.
- Real work: 64 train + 30 validation teacher-labelled using Claude Haiku 5.5 on public Webis data. Official test not labelled or inferred on; train articles duplicated in heldout excluded.
- Untuned model: local official LFM2.5-1.2B-Instruct Q4_K_M. Warm median 675 ms/p95 1578 ms; 30/30 valid JSON; sentence accuracy 10%; teacher-score MAE 29.67; click accuracy 50% vs always-skip 86.7%. Improvement not assumed.
- Checks: 21 unit tests pass; JS, shell syntax, compileall and diff checks pass. Halo export/backward/conversion not executed (CUDA GPU unavailable).
- Plan, commands, access-request draft: `docs/notes/codex/lfm-score-training-plan.md`. Durable baseline summary: `docs/notes/codex/lfm-score-baseline.json`.
- Ignored local artifacts: `data/click-v2/` labels, SFT and manifest; `results/click-v2-baseline.json` predictions. These must be explicitly transferred to organizer GPU with code; no credentials in Git.
- Next: obtain organizer SSH/portal endpoint; export and inspect masks, 2-step backward smoke, audit/scale training data, real Halo training, same-runtime/quantization baseline-vs-tuned validation, integrate only real checkpoint; final test once frozen. No contact messaged.
