# Read-Only

An AI-made late-'90s boom-bap diss track about Reddit's 2023 API changes. One night on one composite Tenderloin-edge block: Act 1 is stylized Blender, and on "I'm the bot" (Verse 4) the same set turns photoreal with video-to-video. The agent does the production; the human may only approve or reject (R1), correct A/V sync (R2), fix technical failures the agent can't (R3), and run interfaces the agent has no access to, such as Suno and the mastering post-filter (R4). The real assets (the breakfast plate photo, an optional badge scan) are inputs the brief plans for; log each one.

**Start here:** the brief is the Claude Doc https://claude.ai/artifact/Ampdx4GB3uytYay53kbTXx, "Read-Only: Shot List" (read it with the docs tools, not a web fetch; mirrored in `docs/brief.md`). It has its own production rules, guardrails and review gates (M1–M8). Setup and conventions come from Not Yet (`~/Projects/not-yet`), the latest published video. Then read the latest entries of `log/production_log.md` and `log/human_interventions.md`.

Rules that apply to every step:
- **Logs:** append to `log/production_log.md` for every action. Log every human action with its rule in `log/human_interventions.md`. Prompts go in `log/prompts/`; the planning chat is in `docs/planning_chat/` and audits go verbatim in `log/audits/`.
- **Commits:** one git commit per logged step.
- **Assets:** never delete or overwrite an asset. Superseded or rejected files go to `archive/` with a log note.
- **Large files** stay out of git; run `scripts/manifest.sh` after adding any. Frame sequences, caches, venvs and node_modules are never archived. `assets/real/` (the human's photos) stays local and out of the manifest until the human says otherwise.
- **Shot IDs** (S01a–S50) never change: inserts take a letter suffix, removals retire their ID.
- **Guardrails:** no Reddit logo, mascot, UI or fonts; no real company logos; no real likenesses; no unhoused people as set dressing; the eatery is fictional.
- **Layout:** the brief's folders map onto Not Yet's: `blender/` → `scenes/blender/`, `review/` → `renders/review/`, `edit/` → `deliverables/` (and the assembly scripts). `assets/real/`, `assets/gen/` and `workflows/` (ComfyUI, API format) are as the brief names them.
- **Render tiers:** `config/render_profiles.json`. Everything runs on the RTX 5090 box; final is 1080p at 24 fps.
