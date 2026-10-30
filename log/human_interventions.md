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

## 2026-10-29T23:50 — Answers on the take; track locked; reference photos supplied — R1, inputs

- **What:** The human answered step 2's open questions and supplied reference photos.
- **Note from the human:** "\"good bot\" is from 2:20 to 2:33 -- Suno repeated it more than requested; that's where I got the idea from. The final hook was removed -- some of those lines got moved to the previous hook. Track is locked, and music-deslop has not changed since I started making any of these videos. Reference photos are in ~/Downloads/read-only-references. I included photos of the restaurant for reference but in case it isn't clear: it is *extremely* informal, a hole-in-the-wall, with a cafeteria-style layout of food (a Filipino would call it a \"turo-turo\"), and a line of tables. It is as clean as one might expect of the area without being out-of-place, and very much not polished."
- **Rule:**
  - **R1:** locking the track closes gate M1.
  - **Inputs:** the plate photo is the brief's listed input. SHA-256 73a0d5f5…, `assets/real/plate.jpg`.
  - **Not a touch on the work:** the other six files are reference material, and the restaurant description is a creative note given in words.
  - **AI change, logged:** the extra "good bot" repeats are Suno's.
  - **Human change before generation (logged):** removing the final hook. It's the human's lyric edit to what Suno was given, made before the take existed. The brief's lyric block was never updated to match.

## 2026-10-30T00:00 — S46 folded into S48; go-ahead for M2 — R1

- **Note from the human:** "fold S46 into S48 and go ahead with M2"
- **Rule:** R1 (approving a plan the agent proposed). The agent made the brief edit (production log, 00:05).
