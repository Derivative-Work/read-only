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

## 2026-10-30T13:30 — The figures — R1

- **Note from the human:** "much better, but the people don't look quite right"
- **Rule:** R1 (a creative note on the detail look test, given in words). The agent rebuilt the figures (production log, same time).

## 2026-10-30T13:45 — The detail pass and figures approved; go-ahead for the Act 1 render — R1

- **Note from the human:** "much better, go ahead"
- **Rule:** R1 (approval of the detail look test and the rebuilt figures).

## 2026-10-30T15:05:44-04 — M4 Act 1 clips: flicker, and gags too fast — R1

- **Note from the human:** "Check for flicker - it's present in a bunch of places. There's also places where jokes aren't landing because they're too fast, like the calendar countdown and the post its"
- **Then:** "The cassette joke is also too fast, and also doesn't look like a cassette"
- **Rule:** R1 (a creative note on the M4 section clips, given in words; not yet a section-by-section verdict). The agent fixed the flicker and re-staged S06, S11–S12 and S31 (production log, same time).

## 2026-10-30T16:16:37-04 — Fix the other fast gags too — R1

- **Note from the human:** "yes, fix those too" (the agent had offered S07's running total, S09's eviction notice and S13's magnifying glass).
- **Rule:** R1 (a creative go-ahead). The agent re-staged S07–S09 and S13 (production log, same time).

## 2026-10-30T19:15:53-04:00 — M4 v3 section clips: notes — R1

- **Notes from the human:**
  - "S03: the tape is colliding with the phone"
  - "still seeing flicker due to overlapping surfaces on the buildings"
  - "S07: the receipt is not flowing out of the register correctly,  it clips into the table, it goes under the road"
  - "S19: the mods are clipping into the sidewalk"
  - "S20: is the CEO supposed to be dribbling the ball? it's bouncing for no visible reason"
  - "S28: it's not clear what the crates are or where they're going"
  - "S29: the truck labels are barely visible"
  - "S31: \"UNDER NEW MANAGEMENT\" is incorrectly on top of the post-its -- just move one so that they're not on top of each other"
- **Rule:** R1 (creative and technical notes on the M4 clips; not a section-by-section verdict). The agent fixes them (production log, following entries).

## 2026-10-30T19:59:54-04:00 — The receipt tape still clips — R1

- **Note from the human:** "Look closer at the receipt tape. It's still clipping into the table and floor. It may help to use a cloth simulation or similar"
- **Rule:** R1 (a creative and technical note). The agent re-checks the tape's draping (production log, following entries).

## 2026-10-31T03:21:26-04:00 — M4 v5 notes — R1

- **Notes from the human** (verbatim):
  - "S02: the phone booth and phone are still gray box and I'm still seeing flicker by the subreddit titles"
  - "S22: the downvotes are not convincing enough -- give them some more separation and make them the correct blue/purple"
  - "S25: the exchange is not reading correctly"
  - "S28: still too fast to see what's going on; it can eat slightly into the previous shot if necessary"
  - "S29: CHAT truck text stays off frame for the entire shot"
  - "S31: add a few more variations on this so it's not all the same text, also it's too small to be legible -- use a marker font instead. make \"People found this helpful\" have some more space on the sides so it's not so stretched out"
  - "S33: \"YOUR LAND\" is occluded by the dev"
  - "S36: the gravestones could use some concrete texturing and reflection maps and the grass can use more detail"
- **Rule:** R1 (notes on the M4 clips; not yet a section-by-section verdict). The agent fixes them (production log, following entries).

## 2026-10-31T06:14:31-04:00 — The headstones in the v6 stills — R1
- **What:** from the test stills: "the gravestones are now hard to read and too clearly have the same texture".
- **Rule:** R1. The agent fixes it (production log, next entry).

## 2026-10-31T07:24:51-04:00 — M4 v6 notes — R1
- **What:** notes on the v6 clips:
  - "S26: the \"BOT DEFENSE\" doghouse's roof has a hole, and its entrance is not rounded"
  - "S28: much better, but the comments crates disappear completely once they're in the truck (rather than being in shadow)"
  - "S30: the \"IPO\" text is visible before the thing that it's on"
- **Rule:** R1 (notes on the M4 clips). The agent fixes them (production log, next entry).

## 2026-10-31T08:54:26-04:00 — M4 v7 notes — R1
- **What:** notes on the v7 clips:
  - "S02 into S03: the handset isn't hanging off the phone booth quite right, and the tape should be in a tape recorder next to the handset"
  - "S18: the CEO is clipping through his chair"
  - "S20: let's make it so it looks like he's actually dribbling the ball"
- **Rule:** R1 (notes on the M4 clips). The agent fixes them (production log, following entries).

## 2026-11-01 — M4 approved — R1
- **What:** after the v8 clips: "approved, go ahead with M5". Act 1 (S02–S39e, sections 1–7 in `renders/m4/sections_v8/`) approved.
- **Rule:** R1 (the M4 gate). The fence shimmer in S38–S39e stays an open item for the 4K render.

## 2026-11-01 — M5: the S43 lip-sync test — R1
- **What:** "lip sync is good, use seed 2. use whichever reference sheet was used on the demo. yes, fix the payphone"
  - **Lip sync:** approved; `takes/l/S43/S43_s2.mp4` (LatentSync 1.6) is the pick.
  - **Sheet:** `takes/stills/rapper/rapper_s1002.png` kept.
  - **Note:** the S43 keyframe's wall-mounted payphone doesn't match the set's post-mounted one; fix it.
- **Rule:** R1 (approve or reject; the note is a rejection of that detail). The agent fixes it (production log, next entries).

## 2026-11-01 — M5: S43 v3 — R1
- **What:** "better, but this is still reading more like Queens than it is Tenderloin"
- **Rule:** R1 (a rejection of the take's look). The agent fixes it (production log, next entry).

## 2026-11-01 — M5: S43 v4 approved — R1
- **What:** "Much better, keep going". S43 v4 (`takes/l/S43/S43_s2.mp4`, keyframe seed 2002) approved, and with it the Tenderloin description and white LED light for every Act 2 street shot.
- **Rule:** R1. The agent moves on to S42.

## 2026-11-01 — M5: S42 and the face glitch approved — R1
- **What:** "This is great, keep going". S42 (`takes/l/S42/S42_s2.mp4`, keyframe seed 2003) and the face glitch on S42 and S43 (`takes/fx/`, `config/glitch.json`) approved; the neon sign's made-up letters accepted as they are.
- **Rule:** R1. The agent moves on to S41.

## 2026-11-01 — M5: S41 approved, sign back — R1
- **What:** "This is great. Put the text back for continuity". S41's reveal approved; the eatery's "r/Philippines" sign goes back on in Act 2.
- **Rule:** R1 (approval, and a rejection of the blank sign). The agent fixes it (production log, next entry).

## 2026-11-01 — M5: S44 approved — R1
- **What:** "Good, keep going". S44 (`takes/fx/S44/S44_billboard.mp4`: V seed 1, the comment box pinned on) approved.
- **Rule:** R1. The agent moves on to S45.

## 2026-11-01 — M5: S45 rejected (the hype man outside the shutter) — R1
- **What:** "the problem is escherian: the hype man is outside of the shop (per his feet) and but the shop's door appears to close in front of him"
- **Rule:** R1 (a rejection of the take). The agent fixes it (production log, next entry).

## 2026-11-01 — M5: S45 v3 approved — R1
- **What:** "Good, keep going". S45 v3 (`takes/fx/S45/S45_sign.mp4`) approved.
- **Rule:** R1. The agent moves on to S47.

## 2026-11-01 — M5: S47 approved — R1
- **What:** "Good, keep going". S47 (`takes/fx/S47/S47_rec.mp4`) approved.
- **Rule:** R1. The agent moves on to S48.

## 2026-11-01 — M5: S48 v3 notes — R1
- **What:** "move the keypads beside the doors. is there supposed to be anything that actually says "log in to continue"? the reference isn't quite clear from the video. for a bit, parts of the road read as a roof atop it, almost like an elevated subway. the continuity is also not great, and there seem to be warp artifacts from the generation"
- **Rule:** R1 (a rejection of the take, and a layout change the human chose between the two offered). The agent fixes it (production log, next entry).

## 2026-11-02 — M5: S48 v4 notes — R1
- **What:** "the text is still not very clear -- most importantly, the "LOG IN TO CONTINUE". also see about blending or color-matching together the shots from the sidewalk to the graveyard -- there's a visible seam between the two"
- **Rule:** R1 (a rejection of the take). The agent fixes it (production log, next entry).

## 2026-11-02 — M5: S48 v5 approved — R1
- **What:** "Good, keep going". S48 v5 (`takes/fx/S48/S48_overlay.mp4`) approved.
- **Rule:** R1. The agent moves on to S48a.

## 2026-11-02 — M5: S48a approved — R1
- **What:** "Good, keep going". S48a (`takes/v/S48a/S48a_joined.mp4`) approved. The agent builds S40 and S48b and assembles Act 2 for the M5 gate.
- **Rule:** R1.

## 2026-11-02 — M5: the Act 2 cut, the tag — R1
- **What:** "this is great, just use the record scratches at the end to fade directly to the login screen (skip the fade to black first)". The Act 2 cut approved but for the S48a → S48b transition.
- **Rule:** R1. The agent changes the transition (production log, next entry).

## 2026-11-02 — M5 approved — R1
- **What:** "approved, go ahead with M6". Act 2 (`renders/m5/act2_v2.mp4`: S40–S48b) approved; M5 closed.
- **Rule:** R1 (the M5 gate).

## 2026-11-02 — M6: bookends v1 notes — R1
- **What:** "the foley at the beginning doesn't sound quite right, and neither does the generated video at the end. The plate (?) on top of the interview schedule is not reading correctly either". Asked to narrow it down: the ambience is "Synthetic or garbled"; S49 is "Too CG".
- **Rule:** R1 (rejections). The agent fixes them (production log, next entries).

## 2026-11-02 — M6: the ambience pick — R1
- **What:** after an A/B file (the distilled model's clip, then three from the full LTX-2.3 model): "for the audio, go with seed 2" (`takes/sfx/amb_dev_s2.wav`).
- **Rule:** R1 (picking a take).

## 2026-11-02 — M6: bookends v2 notes — R1
- **What:** "the intro is a little washed out", "the ending's phone screen has a white border on the edges -- it's probably not masked correctly", "the ending's wall appears to travel"; then, mid-fix, "also, \"EXPIRED\" is very hard to read".
- **Rule:** R1 (rejections). The agent fixes them (production log, next entry).

## 2026-11-02 — M6: bookends v3 notes — R1
- **What:** "the fish is clipping into the plate -- it may be useful to simulate it much like the paper. at the end, the table and the road warp together slightly. I am hearing the foley repeat -- also use seed 3 and mix them together"; then, mid-fix, "I unfortunately just noticed now that all of the chairs appear to be facing the wrong way".
- **Rule:** R1 (rejections; seed 3 is a pick of an existing take). The agent fixes them (production log, next entry).

## 2026-11-03 — M6: bookends v4 notes — R1
- **What:** "much better, but it's still a little washed out in the beginning, particularly in the SF Breakfast screencast".
- **Rule:** R1 (a rejection). The agent fixes it (production log, next entry).

## 2026-11-03 — M6: bookends v5 notes — R1
- **What:** "Much better. I assume the chairs will be fixed in the other scenes in the subsequent render, right? This could use some foley at the end scene that shows the app being shut down, then make an instrumental bounce for the text afterwards (please make sure to run it through the post filter)".
- **Rule:** R1 (notes on the cut). The agent runs the post-filter itself (it is installed locally, as in Not Yet's C6 bounce); no R4 needed.

## 2026-11-03 — M6: S49 foley rejected; tape hiss instead — R1
- **What:** "None of the generated end foley is good (far too noisy for what it was going for). But that gave me a better idea: make tape hiss and crackle".
- **Rule:** R1 (a rejection, with the direction). The agent makes it (production log, next entry).

## 2026-11-03 — M6: the tape hiss's entrance — R1
- **What:** "Make it ease in from the previous scene as the tape recorder is visible, but don't have it go to full volume until we're back at the eatery".
- **Rule:** R1 (a note on the cut). The agent changes it (production log, next entry).

## 2026-11-02 — M6 approved; caption direction — R1
- **What:** "This is great, keep going. For the captions I think a VHS/old-school closed caption font would work best".
- **Rule:** R1 (the M6 gate approved: bookends v8, Act 2 v3, the ending cut; and a creative note given in words). The agent makes the captions to it (production log, next entry).

## 2026-11-02 — M7: full cut v1 notes — R1
- **What:** The human, on `renders/m7/m7_full_v1.mp4`: "This needs a \"five years later\" or similar at the cut to the start of the music. Also instead of fading from the gravestone, do a VHS tracking effect between it and the login screen, still synced to the record scratches".
- **Why:** Review notes on the M7 cut.
- **Rule:** R1.

## 2026-11-02 — M7: the cutlery and the chairs — R1
- **What:** The human, on the M7 cut: "take another look at the fork, spoon, and chair -- they are prominently missing some detail and have parts floating".
- **Why:** Review notes on the M7 cut.
- **Rule:** R1.

## 2026-11-02 — M7: S49's cutlery — R1
- **What:** The human, while the cutlery fix was rendering: "hm, the S49 cutlery is also visibly wrong -- regenerate it once that's done".
- **Why:** Review note on the M7 cut.
- **Rule:** R1.

## 2026-11-02 — M7: full cut v3 notes — R1
- **What:** The human, on `renders/m7/m7_full_v3.mp4`: "add camera shake timed with the downvotes landing"; "the band and the check are not laying on the ground, and the brooms and crate next to them are not reading right"; "the \"IPO\" doesn't look like it's rolling out".
- **Why:** Review notes on the M7 cut.
- **Rule:** R1.

## 2026-11-02 — M7: full cut approved; the vertical cut's gravestones; 1080p — R1
- **What:** "Full cut is good. In the vertical cut, we're missing some of the gravestones -- most importantly Apollo. You'll have to drive the pan a bit more. 1080p is fine for this. What were the thumbnail options again".
- **Why:** Review of the M7 cut (`renders/m7/m7_full_v4.mp4`) and the vertical cut; the final render's resolution (the agent had raised 4K vs the brief's 1080p).
- **Rule:** R1.

## 2026-11-02 — M7 approved; thumbnail B — R1
- **What:** "vertical cut is good; let's go with B".
- **Why:** The M7 gate: with the full cut (approved earlier the same day), the vertical cut `renders/m7/vertical_v2.mp4` and thumbnail option B (`renders/m7/thumbs/thumb_b.jpg`, "WHO'S RAPPIN' THIS?") are approved.
- **Rule:** R1.

## 2026-11-02 — M8: the other-lab audits — R4
- **What:** The human ran the M8 audit prompt in Gemini (selected: Gemini 4 Argon; it reported itself as Gemini 3.1 Pro, with no fallback shown in the UI) and ChatGPT, and saved both responses to `~/Downloads/`.
- **Why:** The agent has no access to other labs' models.
- **Rule:** R4.

## 2026-11-02 — M8: go-ahead to check the flags — R1
- **What:** "okay go ahead", on the agent's plan: archive the audits, verify every flag against primary sources, then bring a fix list for approval before changing any text.
- **Why:** The human had asked for a summary before any changes.
- **Rule:** R1.

## 2026-11-03 — M8: the audit fixes approved — R1
- **What:** "these are all good to me, go ahead", on the fixes proposed in `log/audits/m8_resolution.md` (on screen: S10's lobby screen, Boost's and r/IAmA's headstones, the $20M label, S49's notice, the disclosure after "allegedly"; the end card's BotDefense, IPO, OpenAI, lawsuit and conflict-of-interest lines; the description; the declined flags).
- **Why:** The M8 gate.
- **Rule:** R1.

## 2026-11-03 — M8: the repository link on the end card — R1
- **What:** "oh the end cards also need the link to where this repository will be hosted (https://github.com/Derivative-Work/read-only)".
- **Why:** The end card's credits; Not Yet's ended on its repository link.
- **Rule:** R1.

## 2026-11-03 — The GitHub repository — R4
- **What:** "I created the repository and gave you access -- go ahead and push what you currently have there (we'll clean it up for release later)". https://github.com/Derivative-Work/read-only, private.
- **Why:** The agent can't create repositories under the organization.
- **Rule:** R4.

## 2026-11-03 — M8: a notice at the beginning — R1
- **What:** On the final cut: "This is great, but it needs something along the lines of "AI generated satire. Not investment advice." at the beginning, likely in the same closed caption style".
- **Why:** The M8 gate: the video opens with no disclaimer, and its subject includes Reddit's IPO and shares.
- **Rule:** R1.

## 2026-11-03 — M8: the counter's source — R1
- **What:** "Put the source in the "ACCOUNTS BANNED" counter".
- **Why:** The M8 gate: the figure 144,926 appears on screen without its source.
- **Rule:** R1.

## 2026-11-03 — M8: the disclaimer over the tape recorder; the trucks' names — R1
- **What:** "The Claude disclaimer at the end is occluding the tape recorder, and the "SEARCH" and "CHAT" trucks need to be brighter to read on mobile".
- **Why:** The M8 gate.
- **Rule:** R1.

## 2026-11-03 — M8: flicker in the repair shop — R1
- **What:** "There's visible flicker in the repair shop scene, likely z fighting".
- **Why:** The M8 gate.
- **Rule:** R1.

## 2026-11-03 — M8: the Verse 4 rapper recast — R1
- **What:** "After human review by others, the photoreal rapper at the end is being interpreted by some as AI blackface. Let's try a version where it cuts rapidly between a number of different generated rappers of different ethnicities to emphasize the point that this is affecting everybody", and then: "Make sure to keep the Black rapper in there as one of the faces that is swapped in".
- **Why:** The M8 gate, after outside reviewers' reading of S41–S43.
- **Rule:** R1.

## 2026-11-03 — M8: VHS transitions between the faces — R1
- **What:** "Hm add VHS and similar era appropriate glitch transitions between the faces (masked to just the parts that change)".
- **Why:** The M8 gate, on the recast v1 cuts.
- **Rule:** R1.

## 2026-11-03 — M8: the recast approved — R1
- **What:** "*Much* better, and it passes human review. Suggest new thumbnails with the edit in mind".
- **Why:** The M8 gate, on the recast v2 cuts (VHS transitions between the faces), after outside review.
- **Rule:** R1. The recast v2 cuts become the deliverables.

## 2026-11-03 — M8: thumbnail D; the release — R1
- **What:** "Let's do D. I'm planning on publishing this tomorrow morning, so check the facts and prepare the repo much like the others".
- **Why:** The M8 gate: the thumbnail options for the recast (D, the lineup; E, the splice; F, the index; or the earlier A). Release planned for the morning of 2026-11-04.
- **Rule:** R1.

## 2026-11-03 — Release: the IPO banner and S25's exchange — R1
- **What:** "hm two last things: * the "IPO" banner is covered by the closed captions * the key exchange is not reading correctly -- face them towards the camera".
- **Why:** Review of the final v7 cut: in S30 the banner's "IPO" sat in the frame's bottom fifth, under the captions; in S25 the exchange was seen side-on, with the bot cut off at the frame's edge.
- **Rule:** R1 (reject, with notes).

## 2026-11-03 — Release: S25's mood — R1
- **What:** "that shot of S25 doesn't convey "shady night deal" quite as well as the previous version though".
- **Why:** On the agent's first restaging of S25 (a frontal camera facing the wall).
- **Rule:** R1 (reject, with notes).

## 2026-11-03 — Release: notes on v8 — R1
- **What:** "* the keys are disjoint * the trucks have rectangles on top of the wheels * the "good bot" in the box needs more detail (and so does the box) * the bookends need to zoom in and hold on the phone and schedule more so that they are legible on mobile -- it's okay if the camera moves to get there are faster so that there is more time to read".
- **Why:** Review of the final v8 cut.
- **Rule:** R1 (reject, with notes).

## 2026-11-04 — Release: S49's notice — R1
- **What:** ""when free access to the API ended" is *far* too nice to Reddit. Let's go with something like "when Reddit made access to the API prohibitively expensive" instead".
- **Why:** Review of the final v9 cut: the S49 app notice's wording (from the M8 audit fix).
- **Rule:** R1 (reject, with notes).

## 2026-11-04 — Main video uploaded to YouTube — R4
- **What:** The human uploaded the main video (v10) to YouTube and shared the link: "here is the YouTube link https://www.youtube.com/watch?v=DsjWj7C0g1k".
- **Why:** The release; YouTube is an interface the agent has no access to.
- **Rule:** R4.

## 2026-11-04 — Vertical cut uploaded to YouTube — R4
- **What:** The human uploaded the vertical cut as a Short and shared the link: "here's the one for the vertical cut too https://youtube.com/shorts/YpuD6DVpeC4".
- **Why:** The release; YouTube is an interface the agent has no access to.
- **Rule:** R4.

## 2026-11-04 — Release: the main video underperforming; new thumbnails and titles asked for — R1
- **What:** "I uploaded early as an experiment to see if I could catch the SF evening commute window (as opposed to the NYC morning commute window, which is where my videos have historically performed the best), but it seems to be underperforming regardless. Suggest other thumbnails and titles (including the alternatives you've suggested before)".
- **Why:** After release (the main video was published early, on 2026-11-03 Pacific evening).
- **Rule:** R1 (a correction after release, as Not Yet's 2026-10-28 thumbnail note).

## 2026-11-04 — Release: thumbnail G and title #4 — R1
- **What:** "Let's go with G and #4".
- **Why:** The options after the underperforming upload: thumbnail G (the "Logged-out Reddit" grave, "LOG IN TO CONTINUE") and title #4 ("Reddit sold your posts to AI, so AI wrote a diss track back").
- **Rule:** R1.
