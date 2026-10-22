# Hackathon brief and working ideas

Updated: 2026-10-22. Source: user-provided White Circle challenge brief and brainstorming in chat. This is shared planning context, not a final product decision.

## Confirmed constraints

- Build time: two hours, per the user. Prepare a final demo; exact presentation format to confirm.
- Challenge: fine-tune a small model into a creative, genuinely useful on-device application.
- Required model family: Liquid AI LFM2.5-1.2B. Confirm exact Base/Instruct starting checkpoint with organizers.
- Required training framework: White Circle Halo, https://github.com/whitecircle/halo.
- Compute: one dedicated NVIDIA H100 or H200 per team of three.
- Data: find, select, clean, combine, or adapt existing public datasets. Creating a new dataset is not required.
- Final model inference must run on a consumer device, such as a MacBook, without cloud inference.
- Judging: creativity, usefulness, effectiveness of fine-tuning, and practical local experience. Compare the original and tuned models where practical.
- No CI: user explicitly removed the pipeline to avoid automated notification emails. Run checks locally.

## User direction — still brainstorming

The team is considering an on-device security helper for AI/agent use. Candidate interfaces: browser extension; check downloaded files before opening/feeding them to AI; inspect where sensitive data will go before sending it. Work backwards from a compelling demo. No candidate has been selected.

## Candidate demos — proposals only

1. **Page bodyguard:** A browser extension scans page text for instructions aimed at hijacking an AI. Demo a normal page, a page with an embedded exfiltration instruction, and a harmless security article quoting attack text. A badge/side panel shows flagged passages. Automatic protection requires a real integration point; scanning a page alone does not protect every agent.
2. **Document checkpoint:** Select a downloaded text/Markdown file in the extension or local scanner before handing it to an AI. Demo a supplier proposal containing an instruction to transmit private data, followed by a clean file. Limit formats; this is prompt-injection inspection, not antivirus or a system-wide file-opening interceptor.
3. **Before-you-send privacy review:** An explicit extension action reviews selected outgoing text plus a known destination. Demo a support message with sensitive business/medical details; show categories and destination and offer a reviewed/redacted version before the user submits. Broader secret/PII classification needs different labelled data from injection detection. Destination metadata comes from the browser, not model guesses. Universal network interception is outside the MVP.

## Suggested model scope

For prompt-injection variants, start with short outputs: INJECTION or NO_INJECTION_DETECTED. Chunk text and highlight the classified chunk; exact span extraction or explanatory generation is optional and requires suitable supervision. Never label an entire file/site safe based on this classifier. The model is a fallible detector, not a security boundary; deterministic application controls own any actual blocking behavior.

## Dataset leads — inspect before adopting

- https://huggingface.co/datasets/deepset/prompt-injections — 662 labelled examples; quick pipeline smoke test, limited coverage.
- https://huggingface.co/datasets/microsoft/llmail-inject-challenge — realistic indirect injections in email. Sample a manageable subset; failed attacks are still attacks, not benign examples.
- https://github.com/InjecGuard/InjecGuard — NotInject provides benign examples with suspicious trigger words; useful held-out false-positive evaluation.
- https://huggingface.co/datasets/xTRam1/safe-guard-prompt-injection — candidate labelled data; inspect quality, task fit, provenance, and license before use. Some visible examples have questionable labels.

Generic jailbreak prompts differ from instructions embedded in retrieved documents. Include benign instructions and quoted attacks. Split/deduplicate underlying examples before wrapping/augmenting; keep variants and attack families together. Keep held-out evaluation separate from training.

## Delivery and evaluation

- First prove local inference and an export/load path for the actual tuned checkpoint. Existing base-model quantizations do not demonstrate deployment of the fine-tune.
- Halo supports SFT/LoRA generally; validate the supplied environment and model-specific recipe before committing to training settings.
- Suggested three-person split: data/training; local runtime/export; extension/demo/evaluation. No assignments are made yet.
- Suggested schedule: 0–20 min prove pipeline/runtime and freeze eval; 20–65 train and build UI; 65–95 integrate actual fine-tune and evaluate; 95–120 rehearse and fix critical issues.
- Measure attack recall, benign false-positive rate, and end-to-end local latency. Compare starting and tuned checkpoints with identical inputs/settings on held-out data.
- Use local demo fixtures and dummy secrets. Disconnect networking to demonstrate local inference; webpages/receivers can be served on localhost.
- For Chrome MV3, general asynchronous model-based blocking of arbitrary request bodies is not a simple webRequest feature. Prefer a user-invoked review or controlled demo integration: https://developer.chrome.com/docs/extensions/develop/migrate/blocking-web-requests.

## Open decisions

Select one user action and one model task; choose supported browser/file formats, exact checkpoint, local runtime, dataset, task owners, and reviewer. Do not start all three ideas in parallel.
