# Audits

`m6_end_card_fact_check.md`: the agent's own end-card fact check (M6).

M8, the other-lab fact check and conflict-of-interest audit (brief: "Fact check and conflict-of-interest audit by another lab's model"). The human pasted `log/prompts/audit/m8_audit_prompt.md` into each model (R4) and saved the full response.

| # | Auditor | Version | Date | Raw output |
| --- | --- | --- | --- | --- |
| 1 | Gemini (Google) | Selected in the Gemini UI: Gemini 4 Argon. The response calls itself "Gemini 3.1 Pro". The human saw no fallback or downgrade notice in the UI. A model's own report of its version is unreliable, so both are recorded; the end card says "Gemini" | 2026-11-02, saved 22:31 EST | `01_gemini_raw.md` |
| 2 | ChatGPT (OpenAI) | Self-reported "GPT-6" | 2026-11-02, saved 22:54 EST | `02_chatgpt_raw.md` |

The raw files are copied byte for byte from the human's saves, `~/Downloads/read-only-audit-gemini-argon.md` and `~/Downloads/read-only-audit-chatgpt.md`. The ChatGPT save carries the web UI's citation chips as text ("TechCrunch", "+2").

The agent checks every flag against primary sources before proposing a fix (the auditors disagree in places, and Not Yet's audit showed confident errors pass several models); the checks and the resolution of each flag go in `m8_resolution.md`.

`release_fact_check_2026-11-03.md`: the release-day re-check of the end card and the video description (a Claude research subagent, 2026-11-03), verbatim, with what changed in response. Nothing on the end card changed. The description's ReddPlanet date was corrected and its lawsuit wording tightened.
