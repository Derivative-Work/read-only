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

## 2026-10-29T23:41 (by the agent's commit) — Answers on the take; track locked; reference photos supplied — R1, inputs

- **What:** The human answered step 2's open questions and supplied reference photos.
- **Note from the human:** "\"good bot\" is from 2:20 to 2:33 -- Suno repeated it more than requested; that's where I got the idea from. The final hook was removed -- some of those lines got moved to the previous hook. Track is locked, and music-deslop has not changed since I started making any of these videos. Reference photos are in ~/Downloads/read-only-references. I included photos of the restaurant for reference but in case it isn't clear: it is *extremely* informal, a hole-in-the-wall, with a cafeteria-style layout of food (a Filipino would call it a \"turo-turo\"), and a line of tables. It is as clean as one might expect of the area without being out-of-place, and very much not polished."
- **Rule:**
  - **R1:** locking the track closes gate M1.
  - **Inputs:** the plate photo is the brief's listed input. SHA-256 73a0d5f5…, `assets/real/plate.jpg`.
  - **Not a touch on the work:** the other six files are reference material, and the restaurant description is a creative note given in words.
  - **AI change, logged:** the extra "good bot" repeats are Suno's.
  - **Human change before generation (logged):** removing the final hook. It's the human's lyric edit to what Suno was given, made before the take existed. The brief's lyric block was never updated to match.

## 2026-10-29T23:44 (by the agent's commit) — S46 folded into S48; go-ahead for M2 — R1

- **Note from the human:** "fold S46 into S48 and go ahead with M2"
- **Rule:** R1 (approving a plan the agent proposed). The agent made the brief edit (production log, 23:44).

## 2026-10-29T23:57 (by the agent's commit) — S01e on the first piano chord; sung stage directions kept for now — R2, R1

- **Note from the human:** "cut S01e on the first piano chord. I'm good with the stage directions landing in here for now -- we can revisit replacing them using the stems later"
- **Rule:**
  - **R2:** placing a cut point. The agent proposed it and made the change.
  - **R1:** accepting Suno's sung stage directions ("hype man", "downvote") as they are, for now.

## 2026-10-30T00:02 (by the agent's commit) — M2 approved — R1, R2

- **Note from the human:** "clicks are good, go ahead with M3"
- **Rule:**
  - **R2:** checking the timing map by ear (the M2 gate).
  - **R1:** the go-ahead for M3.
- **Not answered:** whether the eulogy has a music box and a text-to-speech voice, and whether Verse 4 is piano-only (`timing/m2_review.md` section 3). The stem levels stand as the record: drums under both. Logged as Suno's change pending the human's ear.

## 2026-10-30T00:46 (approx., the human's message) — M3 review: the four proposals taken; more subreddits on the block — R1, R2

- **Note from the human:** "go with your proposals for all four. I think we also need more subreddits to fill in the block more"
- **Rule:**
  - **R2:** the timing of S39a–S39e, S48 and S03 (cut points and shot lengths).
  - **R1:** S26's staging and the fuller block, as creative notes given in words. The agent made every change (production log, 00:55).

## 2026-10-30T00:58 (approx., the human's message) — The block's communities swapped for confirmed blackout participants — R1

- **Notes from the human:** "did these subreddits participate in the blackout"; then "go with your swaps, Sourdough for Breadit, Cooking for Aquariums".
- **Rule:** R1 (choosing between the agent's proposals). r/Aquariums and r/Breadit were the brief's own examples; the human chose their replacements. The agent made the change (production log, 00:58).

## 2026-10-30T01:33 — M3 approved; go-ahead for M4 — R1, R2

- **Note from the human:** "this is great, keep going"
- **Rule:**
  - **R2:** framing and timing (the M3 gate).
  - **R1:** the go-ahead for M4.

## 2026-10-30T06:29 — M4 look test approved, with a note — R1

- **Note from the human:** "Go ahead, just make sure it's grungy"
- **Rule:** R1 (approval of the look test, with a creative note given in words). The agent makes the grunge pass itself (production log, same time).

## 2026-10-30T08:22 — Rhubarb allowed; "more detail" note on the scenes — R3, R1

- **Note from the human:** "Yes, use real Rhubarb. It seems that pretty much all of the scenes need more detail"
- **Rule:**
  - **R3:** this session's permissions had blocked fetching Rhubarb Lip Sync's binary (a technical failure the agent couldn't fix itself); the human allowed it. The agent fetched and ran it (production log, same time).
  - **R1:** a creative note on the M4 look, given in words. The agent makes the detail pass itself.

## 2026-10-30T09:40 — Render size for now — R1

- **Note from the human:** "oh and for the renders just stick with 720p for now so it's faster -- we can go to 4k at the end"
- **Rule:** R1 (a production choice, given in words).
- **Effect:**
  - Review renders use the `draft720` profile (1280×720) until the end.
  - The final render then goes to 4K, not the 1080p that `config/render_profiles.json` notes from the brief. That profile changes when we get there.

## 2026-10-30T11:05 — Headstones: overflowing, polygonal, painted-on text — R1

- **Note from the human:** "not quite: there is text going over the edge of the gravestones, and they are polygonal rather than round. they should also probably be engraved into the stones rather than black text"
- **Rule:** R1 (a creative note on the detail pass, given in words). The agent made the change (production log, same time).
