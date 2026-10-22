# Preview score rubric fix

The original LFM preview prompt repeatedly returned numeric zero for ordinary news, even after the fine-tuned deployment was reverted. The preview now asks the original model for a named reading-value category and a short topic summary. The badge uses the category's fixed ordinal score:

| Model category | Displayed score |
|---|---:|
| Skip | 10 |
| Low | 30 |
| Uncertain | 50 |
| Useful | 70 |
| High value | 90 |

These are coarse preview judgments from URL/title/snippet, not calibrated click probabilities. No unseen article contents are assumed. A narrow headline rule overrides vague sensational promises without supporting snippet detail; API metadata retains both model and final categories. Category validity is enforced; malformed outputs become an error rather than a zero. `search-preview-value-v3` invalidates old cached ratings. Full-article selection and its existing heuristic score are unchanged; the fine-tuned model remains disabled and saved.

Verified with 30 unit tests, extension error tests, four real local API calls and the installed extension's existing Google news result. API smoke scores: supply-chain warning 70, severe-weather warning 90, practical energy guide 70, vague sensational secret 10. These examples verify functional behavior, not predictive accuracy. Current API runs from `agent/codex/lfm-score-training` at http://127.0.0.1:8765. Previously rendered zero badges must be recomputed with Spoil again or cleared by refreshing the page.
