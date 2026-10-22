# Installed Chrome extension verification

- **Owner:** codex (parent reviewer)
- **Updated:** 2026-10-22
- **Status:** done
- **Branch / PR:** agent/sol/spoiler-mvp / https://github.com/mashathepotato/on-device-agent/pull/2
- **Scope:** Independent browser and test verification after user manually loaded/reloaded extension.

## Verified behavior

User installed the unpacked extension and reloaded the final Google placement fix. Parent used connected Chrome on `https://www.google.com/search?q=NASA+moon+illusion`, clicked the extension's inline Spoil button beside the actual NASA organic result, and verified an answer and exact source paragraph appeared under that result. Browser URL remained the same Google search URL; article was not opened. Correct answer preserves NASA's uncertainty: “Brace yourself: we don't really know.” Source paragraph explains there is no rock-solid scientific explanation.

First observed final extension request: 990.17 ms total; fetch/extract 0.01 ms (cached article), model 988.4 ms (new inference). Repeat: 1.41 ms total; both article and answer explicitly labelled cached. These are individual smoke observations, not benchmark claims.

Parent separately tested live NASA battery article through headline feed: 576.62 ms total, 380.49 ms fetch/extract and 195.49 ms model. It selected the source sentence identifying solid ceramic/polymer electrolyte. Earlier rejected freeform/exact-quote protocols are superseded by the source-sentence selector; no tuning/improvement claimed.

## Checks and limits

Parent independently ran all 16 unit tests successfully, plus syntax checks on content/background/web JavaScript and whitespace checks. Final Google organic button placement is now browser-verified; the prior pending-retest note in Sol's handoff is superseded by this note. Sources may block fetching; broad hook-resolution quality remains weak (see selector diagnostic). No CI, no training, no main merge.
