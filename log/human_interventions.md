# Human interventions

Every human action: timestamp, what, why, and which production rule allows it. Rules (brief, "Production rules and logging"):
(R1) approve/reject a take, render or plan; (R2) correct A/V sync; (R3) fix technical failures the agent cannot; (R4) run an interface the agent has no access to (Suno, the mastering post-filter). The brief also lets the human supply the real assets under "Inputs" (`assets/real/`). Anything else is an EXCEPTION.

## 2026-10-17T14:26Z (from Suno's tag) — Track generated in Suno — R4 (choice of take: R1)

- **What:** A human ran Suno and chose take `0ee4eab0-dcf6-4572-86b6-765d2efc36c9` (https://suno.com/s/mQzQ0Dqkj7QCFTx9, 196.16 s). The brief's planned generator was ACE-Step 1.5 XL. Version, style prompt and submitted lyrics are logged from Suno's page in step 2.
- **Why:** The agent has no access to Suno.
- **Rule:** R4 to run Suno; R1 to choose the take.

## 2026-10-18T14:47 (from the files' mtimes) — Master run through the post-filter — R4

- **What:** A human ran music-deslop M6f 10k (release chain, with and without fallback) over the Suno mix as part of a batch of eight songs (`audio/master/REPORT.md`).
- **Rule:** R4 (the mastering post-filter).

## 2026-10-29T23:20 (from the files' mtimes) — Source files supplied; the agent pointed at the brief

- **What:** A human exported the 10-stem archive from Suno (2026-10-29 23:18) and placed it in `~/Downloads` beside the mix and the post-filter batch. They pointed the agent at the brief, the planning chat's share link, the Suno take and the sibling projects. They named Not Yet as the latest published video.
- **Why:** Inputs listed in the brief.
- **Rule:** R4 for the Suno stem export; supplying inputs is not a touch on the work. Logged for completeness.
