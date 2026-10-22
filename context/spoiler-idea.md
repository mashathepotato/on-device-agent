# Clickbait spoiler — shared MVP brief

Updated: 2026-10-22. User explicitly requested a new branch, shared context, and a Sol agent to implement this idea as an MVP and report results. This branch is the isolated spoiler experiment; security remains an alternative discussed in chat.

## Assignment and ownership

- Branch: `agent/sol/spoiler-mvp`.
- Sole implementation owner: Sol subagent. Parent Codex reviews/tests; Masha is final decision maker.
- Scope: all MVP application, browser extension, local inference integration, dataset adaptation/evaluation tools, tests, and related docs on this branch. No CI, cloud inference, deployment, or merge to main.
- Acceptance: runnable local MVP; one article at a time; headline plus actual article text produces a brief spoiler; fair original/tuned comparison; real elapsed timings; dataset preparation path; useful setup/run docs; report all missing weights/training/hardware honestly.

## Hackathon and organizer guidance

- Two-hour hackathon, team of three, one H100 or H200 for training supplied by organizers. No GPU credentials have been supplied in this chat.
- Required model: Liquid AI LFM2.5-1.2B; training framework: White Circle Halo (https://github.com/whitecircle/halo). Confirm exact Base/Instruct checkpoint with organizers rather than silently switching models.
- Final inference must run locally on a consumer device, without cloud inference.
- Organizers emphasized fine-tuning, speed, local productivity, and a comparison against the original checkpoint that demonstrates improvement.
- CI was explicitly removed by the user because it sends notification emails. Do not reintroduce pipelines.

## Product

Working name: Get to the Point / Saved You a Click (not finalized).
Given a clickbait headline and its article, reveal the specific information withheld by the headline in a short phrase or at most one sentence. A generic article summary is not enough. Title-only guesses are unacceptable; article text or video transcript is necessary.
Browser extension is desired. Minimal interface: explicit user action on the current article, spoiler, evidence/source passage, latency. A local comparison page/CLI may support training evaluation and demo. Prioritize working model/data flow over UI polish.
Articles first; YouTube is optional and deferred because transcript retrieval and domain transfer add risk. Whole-feed prefetching and arbitrary-site perfection are out of scope.

## Data and training

- Exact task dataset: Webis Clickbait Spoiling Corpus 2022: https://zenodo.org/records/8136637 and https://pan.webis.de/semeval23/pan23-web/clickbait-challenge.html.
- 5,000 examples: 3,200 training, 800 validation, 1,000 test. Includes clickbait post, cleaned article paragraphs, spoiler text/positions, spoiler types (phrase/passage/multipart).
- HF mirror https://huggingface.co/datasets/Tugay/clickbait-spoiling lists only 4,000 examples. Prefer original source; verify availability/license/fields.
- Train headline + article -> short grounded spoiler. Start with phrase/passage labels; do not invent full-sentence rewritten targets or human evidence labels.
- Preserve official splits and check duplicate leakage. Freeze evaluation before training. Output a Halo-compatible preparation/training path grounded in actual Halo docs; do not present an untested config as verified.
- Benchmark the original model on 30–50 held-out examples early. If it is already excellent, report limited improvement headroom honestly.

## Fair comparison and evaluation

Original and tuned checkpoints use identical input, prompt, generation limits/settings, preprocessing, hardware, and inference runtime. Never silently compare different model sizes or substitute cached/mock outputs for real inference.
Measure whether output resolves the hook, is supported by article, and is brief. Include suitable automatic metrics and manual inspection, with honest limits. Report original/tuned results only when both are actually run.
No trained checkpoint is supplied. MVP can expose configurable checkpoint paths and a runnable baseline; tuned mode must clearly indicate unavailable until actual weights exist. Do not fabricate a training run or success.
Evidence: use original dataset positions when available for examples; for arbitrary articles validate any claimed supporting quote against source. Show fallback/uncertainty rather than invented evidence.

## Speed

Likely bottlenecks: article fetch/extraction and input prefill, not a ten-word answer. Fine-tuning does not inherently increase token throughput; shorter output may reduce total time.
Keep model loaded, process one article at a time, cache repeat inputs. Measure cold/warm inference separately from network/extraction.
Proposed go/no-go target: under 2 seconds for a cached ~500-word article on demo hardware. This is an unverified target, not a promise. Long inputs should be bounded transparently; never silently drop the answer and claim article-wide coverage.
Offline demo uses cached article text and actual locally loaded fine-tuned weights. Fetching a live article requires internet; local inference does not.

## Demo

A feed of cached held-out clickbait articles; reveal the withheld answer and source evidence. Side-by-side Original/Specialist outputs, elapsed time, and output length. Let a judge select another unseen example. Disconnect Wi-Fi and repeat locally. Show aggregate held-out results, not only cherry-picked successes.

## Prior art and positioning

- https://ironmedia.com/baitbuster/ — close YouTube caption-grounded spoiler product; documented hosted inference/OpenRouter.
- https://github.com/av/unhype — neutralizes headlines, supports local Ollama; does not establish novelty for generic local clickbait rewriting.
- https://github.com/n4ze3m/page-assist — general local webpage assistant.
- https://dearrow.ajay.app/ — crowdsourced YouTube titles/thumbnails.
Do not claim first-ever local clickbait tool. Distinction to prove: a tiny model specifically fine-tuned to resolve the headline's missing answer with evidence and low latency.

## Other idea discussed

Browser security bodyguard detects indirect prompt injections in page/file text. More integration and security-validation burden. Candidate datasets BrowseSafe++, BrowseSafe-Bench, InjecAgent, NotInject. Do not mix security detection into this spoiler MVP.
