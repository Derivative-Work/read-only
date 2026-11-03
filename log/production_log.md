# Production log

Append-only. One entry per action: timestamp, step (shot ID where relevant), what, exact command/prompt/script, outputs, why.

## 2026-10-29T23:27:00-04:00 — Step 1: repo scaffolding, the brief and supplied audio

- **What:** Read the brief ("Read-Only: Shot List", Claude Doc rev 57) in full. Unlike Share the Shares, it carries its own production rules, guardrails, inputs, pipeline and gates (M1–M8). Setup follows Not Yet, the latest published video (the human: "the latest *published* video is not-yet"). Created Not Yet's directory layout plus the brief's `assets/real/`, `assets/gen/` and `workflows/`. Copied in `.gitignore`, the 50 MiB pre-commit hook, `scripts/manifest.sh`, the Suno and share-page scripts, `package.json` and `pyproject.toml` with their lock files. Wrote `CLAUDE.md`, the logs and `config/render_profiles.json`. Mirrored the brief to `docs/brief.md`. Copied in the Suno mix, the stems and the post-filtered master from `~/Downloads` (originals left in place), and checked each copy's SHA-256 against its source (8/8 OK) and each unzipped stem against the archive (10/10).
- **Commands:**
  - `mkdir -p log/prompts/{suno,other} log/audits scripts/hooks docs lyrics archive style timing shots config scenes/blender/{lib,sets} overlays assets/real assets/gen workflows renders deliverables reference audio/{track,stems,master}`
  - `cp ../not-yet/{.gitignore,package.json,package-lock.json,pyproject.toml,uv.lock}`, `cp ../not-yet/scripts/{hooks/pre-commit,manifest.sh,fetch_share.mjs,chat_snapshot_to_md.py,fetch_suno.mjs,suno_meta.py}`; `cp ../share-the-shares/scripts/doc_to_md.py` (it keeps hard breaks and italics; Not Yet's drops them); names changed to `read-only`; `git config core.hooksPath scripts/hooks`
  - `.gitignore`: Not Yet's N33 screen-capture rule dropped; `assets/real/*` added (the human's photos stay local until the human says what may be published)
  - `npm ci`; `uv sync` (PyTorch 2.8.0+cu128, CUDA available)
  - `cp -p ~/Downloads/Read-Only.{wav,mp3} audio/track/`; `cp -p ~/Downloads/"Read-Only Stems.zip" audio/`; `unzip -q … -d audio/stems`; `cp -p ~/Downloads/music-deslop-m6f-10k-2026-10-18/with-fallback/read-only.wav "audio/master/Read-Only (postfilter m6f).wav"` and that folder's `REPORT.md`, `fallback.json` to `audio/master/`; `sha256sum` sources against copies
  - Brief: docs `read` of project `4f2454c9-705f-4e76-a4a9-f84654576aeb`, node `a990c55c-da10` (rev 57), then `python3 -I scripts/doc_to_md.py <read result> docs/brief.md`; the lyric block to `lyrics/locked_brief_rev57.txt`
  - `ffprobe -v error -show_entries format_tags=lyrics-eng -of default=nw=1:nk=1 audio/track/Read-Only.mp3 > log/prompts/suno/lyrics_submitted.txt`
  - Loudness: `ffmpeg -nostats -i <file> -af ebur128=peak=true -f null -`
- **Outputs:** the files above; `audio/track/Read-Only.{wav,mp3}`, `audio/stems/` (10 WAV stems), `audio/master/Read-Only (postfilter m6f).wav`; `docs/brief.md`; `lyrics/locked_brief_rev57.txt`; `log/prompts/suno/lyrics_submitted.txt`
- **Findings:**
  - **The track is Suno, not ACE-Step.** The brief's pipeline plans ACE-Step 1.5 XL, generated section by section, with Demucs stems. The MP3's comment tag reads `made with suno; created=2026-10-17T14:26:40Z; id=0ee4eab0-dcf6-4572-86b6-765d2efc36c9`. It's one full-song take, PCM s16le, 48 kHz stereo, **196.16 s** (3:16), −16.3 LUFS integrated, peak −3.8 dBFS.
  - **The take predates the brief's date.** It was made 2026-10-17; the brief is dated 2026-10-19 and is now at rev 57. Step 2 checks Suno's page for the submitted lyrics.
  - **Stems:** Suno's 10-stem export, made 2026-10-29 23:18 (today): Lead Vocals, Backing Vocals, Drums, Bass, Guitar, Keyboard, Percussion, Strings, Synth, Other. Each is 196.16 s, 16-bit, 48 kHz. **No MIDI**, unlike Not Yet's export. Note-driven animation would need transcription. Integrated loudness: lead vocals −19.0 LUFS, drums −19.3, guitar −25.3, backing vocals −27.0, bass −27.4, other −30.0, keyboard −30.6, synth −31.0, percussion −35.7, strings −43.7.
  - **The master:** music-deslop M6f 10k, release chain, batch of 2026-10-18 (`audio/master/REPORT.md`). Read-Only has no fallback passages (0.0% faded), so the `with-fallback` default and `no-fallback` files differ only by rounding; the default was taken. 24-bit 48 kHz, 196.16 s, −16.3 LUFS, peak −3.6 dBFS. This batch predates the post-filter commit Not Yet's master used (68441e2, 2026-10-23). Open question for the human: keep it, or re-run with the current chain. Its offset against the mix still gets a cross-correlation check (expected 0 samples).
  - **The MP3's lyrics tag is not the brief's lyrics.** It runs 127 lines. Its first 50 lines are a different arrangement: a "Bridge" eulogy after verse 2 and a hook ending on "guard dog". Verse 1 through Hook 2 then repeat, and the eulogy's last lines and the outro are doubled. Its final section order (Verse 3, eulogy, Verse 4, outro) matches the brief, but it has no final hook. It says "(downvote sound)" and lacks the eulogy's "(arrangement: …)" note. Not Yet found this tag can carry export artifacts, so Suno's page is the check (step 2). What is actually sung gets settled at M2.
  - **Brief vs the setup:** The brief's layout (`blender/`, `review/`, `edit/`) maps onto Not Yet's folders, as `CLAUDE.md` records. The brief's deliverable is 1080p at 24 fps, so `final` is 1920×1080 at 24 fps, not Not Yet's 4K/30.
- **Why:** Brief, "Production rules and logging" (log from the first action) and "Inputs the human supplies"; Not Yet's step 1 (layout, the 50 MiB check before the first commit, mirrored brief).
- **Environment:** Claude Code (Opus 5.5) on the RTX 5090 box (32 GB, driver 595.99.02); Blender 5.2.3 LTS; ffmpeg 8.0.1; Python 3.14.4 (system), 3.12 venv via uv 0.13.0; Node v24.22.0; git. Disk: 130 GB free.

## 2026-10-29T23:29:41-04:00 — Step 2: Suno take and planning chat logged; the Reference Guide found

- **What:** Fetched Suno's share page and the planning chat's share page with Not Yet's scripts. Extracted the take's metadata and submitted lyrics, and wrote `log/prompts/suno/takes.md`. Converted the chat to Markdown. Read the chat in full. It links the brief's companion doc, the Reference Guide ("Read-Only / We Hear You: Reference Guide", https://claude.ai/artifact/5KCzixyz4DRBiT9wqovwkW, project `22ef55b7-1ab8-421a-84d2-cadb2c12121b`, rev 10), which I read with the docs tools.
- **Commands:**
  - `node scripts/fetch_share.mjs https://claude.ai/share/3aa680ba-c565-45bd-9c13-ecacf3444fe1 docs/planning_chat/planning_chat`; `.venv/bin/python -I scripts/chat_snapshot_to_md.py docs/planning_chat/planning_chat.json <url> > docs/planning_chat/planning_chat.md`
  - `node scripts/fetch_suno.mjs https://suno.com/s/mQzQ0Dqkj7QCFTx9 log/prompts/suno/fetch_accepted`; `.venv/bin/python -I scripts/suno_meta.py log/prompts/suno/fetch_accepted`
  - Docs `read` of project `22ef55b7-1ab8-421a-84d2-cadb2c12121b`, node `e1dfb341-e43b` (rev 10)
- **Outputs:** `docs/planning_chat/planning_chat.{json,html,txt,md}`, `log/prompts/suno/fetch_accepted/{clip.json,lyrics.txt,page.html,page.txt,resp_*.json}`, `log/prompts/suno/takes.md`
- **Script changes (`scripts/suno_meta.py`):**
  - The lyric bounds were Not Yet's (`[Verse 1]` … `Goodnight.`). They are now `[Intro` … `So was everything else.`.
  - String fields came out mojibaked ("Late-â90s"), because `unicode_escape` reads the page's UTF-8 as Latin-1. The script now re-decodes them.
- **Findings:**
  - **Take:** Suno V6 (`chirp-hawk`), `aug_creativity` 1, created 2026-10-17T00:20:23Z, 196.16 s. The stored style prompt is an expanded version of the brief's (`takes.md`).
  - **The take predates the brief's later lyric edits.** Suno's page lyrics (78 lines) match the brief's except in these places (`takes.md`):
    - **Hook 2** carries the "guard dog" lines.
    - **No final hook** comes after Verse 4. The brief's S46 ("Read-only! The guard dog's put down…") is cued to a section the take may not have; M2 checks what is sung.
    - **The eulogy's replies:** the brief's ~15 s of trickling "good bot" replies (added 2026-10-30, planning chat message 52) aren't in the submitted lyrics. The take has the original "Good bot. Good bot. Good bot." Message 50 puts that at about four seconds. The S39a–S39e headstone sequence was planned for the ~15 s. **Open question for the human** (a creative call: an extended take, an edit of the replies, or fewer stones).
    - The MP3's lyrics tag (step 1) is an export artifact, as in Not Yet: its repeats aren't on Suno's page.
  - **Planning chat:** "Song: Read-Only (Reddit API)", snapshot 2026-10-30T03:20:57Z. It has 52 messages, 2026-10-16 to 2026-10-30. Messages 3–4 aren't in the share (probably an edited branch); archived as shared. It holds no lyric audit. The brief's conflict-of-interest audit by another lab's model is M8. The shot list's last edits (headstones, u/alternate-source-bot removed) are from 2026-10-30 02:35–03:01Z, after the take and the post-filter batch.
  - **Reference Guide:** a background timeline, a lyric-by-lyric reference table for both songs (Read-Only and the unmade boy-band version "We Hear You"), the visual references by shot, facts to verify, and sources. It says "other dates and figures here are from memory and approximate". The brief makes it the fact source for the end card, so it gets checked at M8. Not mirrored yet; it gets mirrored to `docs/` when the end card starts.
- **Why:** Brief, "Production rules and logging": every prompt sent to any model, verbatim, with its outputs (the Suno prompt and lyrics). Not Yet's step 2: log the audio retroactively and archive the planning chat.

## 2026-10-29T23:41:56-04:00 — The human's answers (M1 locked); reference photos filed

- **What:** Logged the human's answers to step 2's open questions (human_interventions, 23:41). Copied the seven reference files from `~/Downloads/read-only-references/` to `reference/private/` (git-ignored, not in the manifest) and the plate photo to `assets/real/plate.jpg`. Checked all against their sources by SHA-256 (7/7, plus the plate copy). Viewed each one (previews in the session scratchpad only). Wrote `reference/README.md`: what each file is, what it's used for, and the eatery's and the props' look, without the private details.
- **Commands:** `cp -p ~/Downloads/read-only-references/* reference/private/`; `cp -p …/breakfast-plate.jpg assets/real/plate.jpg`; `sha256sum` + `cmp`; EXIF via Pillow; `pdftoppm -r 60` for a preview of the scan; `.gitignore` gains `reference/private/`; `scripts/manifest.sh` (still 16 files)
- **Outputs:** `reference/README.md`; `reference/private/` (local only); `assets/real/plate.jpg` (local only, SHA-256 73a0d5f5…)
- **Findings:**
  - **The plate photo is from 2018:** EXIF 2018-03-27 10:35:24 (Pixel). The badge in the scan reads 10:51 AM the same day, and the office photo 16:24:52. That closes the brief's open check "Check the plate photo's date before captioning it '2018'". S01a's caption "San Francisco, 2018" stands.
  - **Private details:** the scan names eight real interviewers and a meeting room, and carries Reddit's logo and mascot. The office photo shows the logo and the human's face. The four restaurant photos are a map service's (other people's photos, some showing staff). None of these go on screen, in git, or in the manifest; the brief's props are recreations.
  - **The eulogy timing works:** the human says the take's "good bot" replies run 2:20–2:33 (about 13 s). Suno repeated them more than the lyrics asked, and that's what led to the brief's ~15 s note. The S39a–S39e headstones fit there; M2 times them.
  - **No final hook:** the human removed it before generating; its "guard dog" lines moved into Hook 2. The brief's lyric block (rev 57) still shows a `[Final hook]`, and S46 is cued to it. Open question for the human: retire S46 or re-cue it.
  - **The master stands:** music-deslop hasn't changed since the first of these videos (the human), so the 2026-10-18 batch is the current chain. Step 1's open question is closed.
- **Why:** Brief, "Inputs the human supplies" (`assets/real/`), "Content guardrails" and "Open checks"; the human's answers.

## 2026-10-29T23:44:35-04:00 — Brief: S46 retired into S48; lyric block matches the take

- **What:** On the human's decision ("fold S46 into S48"), edited the brief (Claude Doc rev 57 → 65). S46's cue now reads "Retired: the take has no final hook. Folded into S48." and its shot is "None"; the ID stays (retired, not removed). S48's shot gains S46's imagery: the crane rises over the photoreal block with a VIP bot in every doorway and "Log in to continue" keypads on the shutters, as well as the red REC lights. The lyric block now matches what the human gave Suno: `[Hook]` became `[Hook 2]` written out with the "guard dog" lines, and the `[Final hook]` block is gone (the human, 23:50). S46's other two mentions (the login-gags open check, the `badge_vip.png` input row) now name S48. Re-exported `docs/brief.md`; lyric block saved as `lyrics/locked_brief_rev65.txt`.
- **Commands:** Docs connector `update` on node `a990c55c-da10` (find-targeted text ops: one `delete`, six `replace`; then one fix-up `replace`, because "S46, S48" → "S48" had dropped the S48 entry from the open check); `python3 -I scripts/doc_to_md.py <read result> docs/brief.md`
- **Findings:**
  - `lyrics/locked_brief_rev65.txt` now differs from Suno's page lyrics only in curly quotes, section-tag wording, "(downvote)" vs "(downvote sound)", and the eulogy's arrangement note.
  - **For M3:** S26 ("Hook 2: reuse S14–S17") reuses S16's 48-hour countdown and S17's meter, which are cued to Hook 1's last two lines. Hook 2 ends on the "guard dog" lines instead, so those two reuses need new cues or new dressing.
  - Not changed: the Reference Guide's "Final hook" row (it explains the lines, which are still sung in Hook 2).
- **Why:** The human's decision (human_interventions, 23:44).

## 2026-10-29T23:51:35-04:00 — M2: as-sung lyrics, word alignment, beats and bars, the timing map and its ear check

- **What:**
  - Transcribed both vocal stems. Drafted the as-sung lyrics and aligned every word.
  - Built the beat grid and 4/4 bars, the vocal envelopes and the drum drop-outs.
  - Built the timing map with all 61 shot IDs resolved: 51 timed, 4 pre-roll, 3 after the audio, 1 retired (S46).
  - Built a click-track ear check (Share the Shares' review format, which the human approved there) and checked the master's offset.
- **Commands** (all `.venv/bin/python -I`, in order):
  - `scripts/first_pass.py`: faster-whisper large-v3, float16, on the RTX 5090. The pip wheels' cuBLAS and cuDNN aren't on the loader path, so the script preloads them.
  - Windowed re-runs (4–6 s windows, same model; a scratch script, outputs quoted in `lyrics/as_sung_draft.txt`'s notes): 0–20 s, 40–62 s and 138–196 s of the lead stem, and 0–12 s and 162–196 s of the backing stem.
  - `scripts/align_words.py` (torchaudio MMS_FA, from Share the Shares; per-line windows for Hook 1 and the outro)
  - `scripts/beats_beat_this.py`, then `scripts/meter.py` (both from Share the Shares, run on CUDA)
  - `scripts/stem_envelopes.py` (adds the drum drop-outs)
  - `scripts/timing_map.py` (rewritten for this brief's six-column shot tables and cue wording)
  - `scripts/m2_clicks.py` (from Share the Shares' `c3_clicks.py`, with this song's sync points)
  - Master offset: an inline cross-correlation of 60–80 s, mix against master
- **Outputs:** `lyrics/as_sung_draft.txt`; `timing/{first_pass_lead,first_pass_backing,words,beat_this,beats,drum_onsets,timing_map}.json`, `timing/envelopes/{lead,backing}.npy`, `timing/timing_map.md`, `timing/m2_review.md`; `config/{meter,shot_anchors}.json`; `scripts/{song,first_pass,align_words,beats_beat_this,meter,stem_envelopes,timing_map,m2_clicks}.py`; `renders/m2/m2_clicks.{wav,mp3,md}`
- **Findings:**
  - **Tempo and bars:** 90.9 bpm, rigidly steady (p5–p95 90.9–90.9), against the prompt's 92. 76 bars, all 4 beats except two 2-beat bars at 2:17.54 and 2:42.60. Both fall on a lyric "(beat)" pause, so they are probably real. Bar phase checked on the drum stem: the kick is on beat 1, the snare on beats 2 and 4.
  - **Intro:** piano and synth from 0:00.14, a drum hit at 2.46 s, a fill from 7.1 s, the full beat from 9.70 s. The first word ("Yeah, hello?") is at 3.08 s. So the music doesn't start on "Yeah, hello?", as the brief's S01e has it.
  - **Sections:**

    | Section | Start | End |
    | --- | --- | --- |
    | Intro | 0:03.08 | 0:09.60 |
    | Verse 1 | 0:20.62 | 0:47.90 |
    | Hook 1 | 0:47.70 | 1:00.46 |
    | Verse 2 | 1:00.62 | 1:28.96 |
    | Hook 2 | 1:29.64 | 1:39.88 |
    | Verse 3 | 1:40.18 | 2:03.89 |
    | Eulogy | 2:04.00 | 2:20.94 |
    | Replies | 2:20.92 | 2:33.10 |
    | Verse 4 | 2:33.68 | 2:48.96 |
    | Outro | 2:52.12 | 3:06.38 |

    The piano tail runs to 3:16.16.
  - **Suno's changes to the sung words** (for the ear check, `timing/m2_review.md`), logged as AI changes:
    - stage directions sung as words: "hype man" twice, and "downvote" for the sound effects;
    - a stutter on "This, this call";
    - six "yeah"s before Hook 1, and no "(read-only!)" echo;
    - about 18 "good bot"s, one per beat (the human: 2:20–2:33);
    - the outro line sung three times, stuttered and scratched;
    - vocal chops under the intro beat.
  - **Suno's arrangement changes** (by stem energy, to confirm by ear): drums under the eulogy (the prompt asked for the beat to drop to a music box), and the full band under Verse 4 (it asked for a single piano loop).
  - **Alignment:** all 62 lines aligned. Low-confidence words are listed in `timing/timing_map.md`; most are in the Auto-Tuned Verse 2, the double-time Verse 3 and the replies. The whole-stem pass looped on "good bot" from 2:22 to 2:46 and dropped Verse 4, so that stretch was re-transcribed in windows.
  - **Shots:**
    - All cues resolve. S20 and S40 match on their first phrase (each cue spans two lines).
    - S39b–S39e split the replies into equal runs of beats: about 2.5 s a shot.
    - Timing issues for M3 are in `timing/m2_review.md` section 4: S03 runs 12.9 s; S48 gets 1.06 s, against S47's 13.2 s; S48a holds over a 9.8 s piano tail, not silence.
  - **Master offset:** 0 samples against the mix (normalised correlation 1.000), as expected.
- **Why:** Brief M2: "Timing map from the locked track; add timestamps to every shot". The brief names librosa and WhisperX; this uses beat_this and MMS_FA instead, as the sibling projects did. Adding the timestamps to the brief's shot tables waits for the human's ear check, so the doc changes once, not twice.
- **Fix after the commit:** the ported script still wrote `renders/m2/c3_clicks.*`; renamed in the script and re-run. The misnamed copies (same content) are archived as `archive/renders/m2/m2_clicks_superseded_misnamed-c3.*`.
- **Status:** **M2 is ready for review.** The agent stops here.

## 2026-10-29T23:57:57-04:00 — S01e cut on the first piano chord; stage directions kept for now

- **What:** On the human's decision, S01e (the match cut) and S02 now start on the first piano chord, 0:00.14. `config/shot_holds.json` (new) holds both, and "Yeah, hello?" falls 2.9 s into S02. In the brief, S01e's cue now reads "The first piano chord, 2.9 s before "Yeah, hello?"" (doc rev 65 → 66); its overlay note "Music starts on the cut" stands. Re-exported `docs/brief.md`, and rebuilt the timing map and the click track. The click track's first two tones are now the cut (0:00.14) and "Yeah, hello?" (0:03.08).
- **Commands:** Docs connector `update` on node `a990c55c-da10` (a find within table `mh1vfytf976.2893`, row 5, col 2); `python3 -I scripts/doc_to_md.py …`; `.venv/bin/python -I scripts/timing_map.py`; `.venv/bin/python -I scripts/m2_clicks.py`
- **Findings:** S02 now runs 7.61 s (0:00.14–0:07.75).
- **Stage directions:** the sung "hype man" (twice) and "downvote" stay in the track for now. The human may revisit replacing them from the stems later. That would be an audio edit, made by the agent and logged. Open item.
- **Why:** The human's decisions (human_interventions, 23:57).

## 2026-10-30T00:02:55-04:00 — M2 approved; timestamps written into the brief

- **What:** The human approved the click track (M2 gate). In the brief's two shot tables, added a "Start" column after "Cue" with each shot's start from `timing/timing_map.json` (m:ss.ss of the Suno mix): "Pre-roll" for S01a–S01d, "Retired" for S46, "After the audio" for S48b. The bookends table (S49, S50) has no cue column and is left alone; both come after the audio. Ticked two open checks: "Lock the track and timing map, then add timestamps to every shot" and "Check the plate photo's date" (EXIF, logged 2026-10-29). Doc rev 66 → 129. Re-exported `docs/brief.md`. `scripts/timing_map.py` reads the new seven-column rows; re-running it changes no time, and every brief Start matches the map.
- **Commands:** Docs connector `update` on node `a990c55c-da10`: an `insert` with `each` (a "TBD" cell after the Cue cell of all 61 rows), then 61 cell-scoped find/replace ops, then two `set checked` ops. `python3 -I scripts/doc_to_md.py …`; `.venv/bin/python -I scripts/timing_map.py`, and a check that the brief's Start column equals the map.
- **Why:** Brief M2 ("add timestamps to every shot") and its gate; the human's approval (human_interventions, 00:02).

## 2026-10-30T00:20:00-04:00 — Correction: log timestamps

- **What:** The headings of the six entries from step 2 through "M2 approved" carried guessed times, 10 to 98 minutes late. They are now the times of each step's commit (`git log --date=iso-strict`), and the cross-references to human_interventions now match. Content unchanged. From here on, every heading takes `date -Iseconds` at the time of writing.

## 2026-10-30T00:44:00-04:00 — M3: the grey-box set and the animatic

- **What:** Built the brief's four sets in one grey-box Blender scene, staged every shot ID with its own camera, rendered the whole edit at 640×360 and assembled it with the post-filtered master and burned-in review captions.
- **The set** (`scenes/blender/sets/block.py`, flat colours only):
  - **The block:** ten shopfronts with roll-down shutters, neon "READ-ONLY" signs, padlocks, "UNDER NEW MANAGEMENT" and "Log in to continue" keypads. Upper windows each carry a REC light.
  - **The eatery:** a turo-turo interior after the human's note and `reference/README.md` (steam table, menu board, one line of tables). It copies nothing from the real restaurant.
  - **The Dev's shop:** its interior; the trade sign "Third-Party App Repair est. 2008".
  - **The corner:** the payphone with its REC light, and the streetlight with its coin meter.
  - **The tower:** lobby, throne, screen, brick wall, balcony with bell and podium, ticker band, rooftop billboard.
  - **The pocket park:** the coffin, the doghouse, good bots with lanterns, all 15 headstones from the brief's table with their inscriptions, and one mesh of 144,926 markers.
  - **Stand-ins:** the Dev, the CEO, mods, VIP bots and good bots as coloured primitives; their mouths follow the lead stem's envelope.
- **The shots** (`scenes/blender/shots.py`):
  - 62 cameras on timeline markers: every timed ID, plus one camera per line of S26.
  - Staging and gags are keyed from `timing/timing_map.json`:
    - shutters slam east to west across S14, the eatery last, with each neon on as its shutter lands;
    - the block goes dark at S15, the corner lamp flickers back at S17;
    - one arrow per sung "downvote";
    - the bell swings on the beat;
    - the ban stones multiply through S35, and the lanterns go out one by one in S37;
    - notes land on the coffin in S39a.
  - Morning light in the pre-roll, night from the S01e cut.
- **Assembly** (`scripts/animatic_assemble.py`):
  - an 18 s pre-roll (`config/bookends.json`, a proposal), then the master;
  - S40's freeze (0.4 s) and rewind, built from the rendered frames;
  - captions: the lyrics word by word, shot ID and pipeline code, the brief's overlay note for JS/F/Real/LS shots, an "Act 2 at M5" note, and placeholder cards for S01b's photo, S48b, S49 and S50.
- **Iterations:**
  - Anchor stills v1–v4 and their contact sheets found about 15 bad frames. Cameras sat inside a building (S15, S30), a coffin stand (S36), a headstone (S39c) or behind a figure (S05, S11). The lobby doors were opaque (S10, S18, S20). The S05 view to the lobby needed a glass shop door. The hype man stood behind a closed door and shutter (S45). Trucks' lettering showed outside their shot (a child-visibility bug).
  - Cameras now track keyed target empties, so long moves don't flip.
  - Superseded stills and sheets are archived in `archive/renders/m3/`.
- **Commands:**
  - `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m3/anchors_v5 --anchors` (62 stills, 17 s)
  - `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m3/frames_v1` (5,669 frames in 25 min, 0.26 s/frame, Eevee at 8 samples on the RTX 5090)
  - `.venv/bin/python -I scripts/animatic_assemble.py renders/m3/frames_v1 renders/m3/m3_animatic.mp4`
  - `.venv/bin/python -I scripts/contact_sheet.py renders/m3/anchors_v5 renders/m3/m3_sheet_{a,b,c}.jpg 4 <IDs>`
- **Outputs:**
  - Code and config: `scenes/blender/{animatic,shots}.py`, `scenes/blender/lib/gb.py`, `scenes/blender/sets/block.py`, `scripts/{animatic_assemble,contact_sheet}.py`, `config/bookends.json`
  - Fonts: `assets/fonts/` (Inter and JetBrains Mono, OFL, from Not Yet with their checksums)
  - Renders: `renders/m3/m3_animatic.mp4` (3:56.17, 640×360, 24 fps, H.264 + AAC), `renders/m3/m3_sheet_{a,b,c}.jpg`, `renders/m3/anchors_v5/`, `renders/m3/frames_v1/` (not in the manifest)
  - Review notes: `shots/m3_review.md`
- **Findings for the review** (`shots/m3_review.md`):
  - S39a–S39e get about 2.5 s each;
  - S48's crane has 1.06 s against S47's 13.2 s;
  - S03 holds the REC light for 12.9 s;
  - Hook 2's last two lines don't match S16 and S17's reused gags.
  - Each comes with a proposal.
- **Not in M3:** overlays (M4), the real photo (M6), the photoreal Act 2 and lip-sync (M5), and proper Act 1 lip-sync (Rhubarb, M4).
- **Why:** Brief M3: "Grey-box Blender set and an animatic of every shot at low resolution, cut to the track"; gate: "Approve framing and timing". The anchor-sheet loop is Not Yet's C4.
- **Status:** **M3 is ready for review.** The agent stops here.

## 2026-10-30T00:55:00-04:00 — M3 v2: the four timing changes, a fuller block; brief rev 134

- **What:**
  1. **S39a–S39e** (`config/replies_split.json`, new):
     - The replies, S39a to "Hold up", are now split by beats in proportions 2 : 6 : 4 : 4 : 4. `scripts/timing_map.py` reads the weights.
     - New lengths: S39a 1.9 s (coffin notes), S39b 4.0 s (the six app stones, was 2.6), S39c 2.0 s, S39d 2.6 s, S39e 2.3 s.
  2. **S48:** a hold in `config/shot_holds.json` starts it on the second "This call was recorded" (L60, 2:56.74), so the crane over the block has 9.64 s, up from 1.06 s; S47 now runs 4.62 s. The crane is re-keyed in five stages: payphone → over the shopfronts → high over the block's doorways and windows → toward the park → settling on the dark park.
  3. **S03:** the close-up holds on the REC light until the beat comes in (0:09.70), then pulls back from the payphone to the Dev's shop and the eatery by Verse 1.
  4. **S26** (Hook 2): the cameras for its last two lines are now S38's (the doghouse) and S39's, with three VIP bots strolling past the doghouse on "Now the wolves got a contract".
  5. **More subreddits:**
     - two more south-row shops east of FOR LEASE: r/AskHistorians and r/Coffee;
     - a north-side row east of the tower: r/Houseplants, r/BoardGames and r/Birding, the same shopfront turned to face the street;
     - painted signs in six upper windows: r/Bonsai, r/MechanicalKeyboards, r/Sewing, r/HomeImprovement, r/Fishing, r/Books.

     Several of these names were replaced at 00:58 (next entry).

     The block now shows 17 communities, up from 7. All 15 shops take part in the shutter slams, the padlocks, the keypads and the S48 doormen.
- **Fixes found on the way:**
  - `shopfront()` now builds in local coordinates around a root, so a shop can face either way.
  - S14's slam wave trailed its tracking camera, so the shutters came down out of frame. Each shop now slams as the camera's aim passes it; the eatery is still last. S26's first line does the same.
  - The VIP bots in S39 walked outside the frame; their path is now in front of the camera.
  - The VIP bots' grey is lighter, so they read at night.
- **Brief** (docs `update` on node `a990c55c-da10`, rev 129 → 134):
  - S03's and S26's shot text;
  - S48's cue: "The second "This call was recorded" through "So was everything else."";
  - Start column: S48 2:56.74, S39b 2:22.82.

  `docs/brief.md` is re-exported, and the Start column matches the timing map (0 mismatches).
- **Commands:**
  - `.venv/bin/python -I scripts/timing_map.py`
  - `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m3/anchors_v6 --anchors`, plus a scratch script for stills at chosen moments (S03 late, S14 mid, S26 lines 3–4, S48 mid)
  - `blender … --out renders/m3/frames_v2` (in progress)
- **Housekeeping:** the v1 frame sequence moved out of the repo to the session scratchpad. Frame sequences are never archived; `frames_v1` regenerates from commit 64fd4b7.
- **Why:** The human's decisions (human_interventions, 00:46).

## 2026-10-30T00:58:00-04:00 — The block's communities checked against the blackout list; eight swapped

- **What:**
  - The human asked whether the block's subreddits took part in the blackout. I had chosen them as recognisable hobby communities without checking.
  - Downloaded the list of 5,351 subreddits that announced they would join (r/ModCoord's posts, as collected by github.com/bpettis/reddit-blackout-announcements; also published on Dryad, doi:10.5061/dryad.qfttdz0qd).
  - Of the 18 communities on the block, 12 are on it. r/Aquariums, r/Breadit, r/bicycling, r/birding, r/Bonsai, r/sewing, r/Fishing and r/books aren't.
  - The list records announced participants, not who actually went private, and it's incomplete (over 7,000 went private), so "not listed" means unconfirmed.
- **Swaps** (the human: "go with your swaps, Sourdough for Breadit, Cooking for Aquariums"). Every name on the block is now on the list:

  | Was | Now |
  | --- | --- |
  | r/Aquariums | r/Cooking |
  | r/Breadit | r/Sourdough |
  | r/Bicycling | r/Running |
  | r/Birding | r/Crochet |
  | r/Bonsai | r/Embroidery |
  | r/Sewing | r/Quilting |
  | r/Fishing | r/Chess |
  | r/Books | r/Photography |

- **Files:**
  - `scenes/blender/sets/block.py`: the names, and a comment naming the source.
  - `reference/sources/blackout_list/subreddits.txt`: the list, kept locally (another publisher's file, like Not Yet's evidence pages).
  - `reference/sources/blackout_list.tsv` (in git): the list's URL, retrieval time and SHA-256 (cc74ed9e…).
- **Docs:**
  - **Brief**, rev 134 → 135: the sets table's example names now read "(r/Philippines, r/Cooking, r/Sourdough), each one a community that announced it would join the June 2023 blackout (r/ModCoord's list)". `docs/brief.md` re-exported.
  - **Reference Guide**, rev 10 → 11: its visual-references row now names r/Cooking and r/Sourdough.
- **Render:**
  - The v2 render in progress still had the old names. It was stopped at frame 954, its partial frames deleted (a regenerable frame sequence), and restarted.
  - Stopping it with `pkill -f` also ended the two background wait loops; nothing else was affected.
- **Why:** The hook is "Eight thousand gone dark", and every shop's shutter slams on it, so the block shows only communities that took part. The human's decision (human_interventions, 00:58).

## 2026-10-30T01:27:00-04:00 — M3 v2 rendered and assembled

- **What:** Rendered v2 with the four timing changes, the fuller block and the swapped names. Assembled it, re-rendered the anchor stills and rebuilt the contact sheets. Spot-checked frames: S02, S14 (r/Running's shutter and neon land in frame), S26's last line (the VIP bots past the doghouse), S39d and S42.
- **Commands:**
  - `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m3/frames_v2` (5,669 frames, about 25 min)
  - `.venv/bin/python -I scripts/animatic_assemble.py renders/m3/frames_v2 renders/m3/m3_animatic_v2.mp4`
  - `… --anchors` → `renders/m3/anchors_v7`, then `scripts/contact_sheet.py` → `renders/m3/m3_sheet_{a,b,c}.jpg`
- **Outputs:** `renders/m3/m3_animatic_v2.mp4` (3:56.17, 640×360), `renders/m3/m3_sheet_{a,b,c}.jpg`, `renders/m3/anchors_v7/`
- **Archived:**
  - `archive/renders/m3/m3_animatic_v1_superseded_m3-review.mp4`
  - `archive/renders/m3/anchors_v5_superseded/`
  - `archive/renders/m3/m3_sheet_{a,b,c}_v1_superseded.jpg`
  - `renders/m3/anchors_v6` (check stills of a state that was never rendered) deleted, as were the v1 frames in the scratchpad: both regenerable.
- **Status:** **M3 v2 is ready for review.**

## 2026-10-30T01:33:03-04:00 — M3 approved

- **What:** The human approved M3 v2 (`renders/m3/m3_animatic_v2.mp4`) and said to continue (human_interventions, same time). The grey-box framing and timing, `config/bookends.json` and `config/replies_split.json` stand. Next: M4, starting with a look test for approval before the Act 1 renders, as in the sibling projects' C1.

## 2026-10-30T01:39:36-04:00 — M4 (first step): the style spec, CC0 textures, stylized figures, and a look test

- **What:** Before the Act 1 renders, a look test for approval, as the sibling projects' C1:
  - **The spec** (`style/style_spec.md`):
    - the palette: sodium street light, a blue night, the cold corporate tower, red reserved for REC and READ-ONLY, warm community windows;
    - materials, lettering, characters and light.
  - **The numbers:** `config/look.json`.
  - **Textures:** 12 CC0 textures from Poly Haven, fetched by `scripts/fetch_textures.py` and checked against Poly Haven's MD5s. Sources and licence are in `assets/textures/sources.tsv`; the files are git-ignored and re-fetchable. They're box-projected in object space at real-world scale (`gb.tex_mat`).
  - **Figures** (`scenes/blender/sets/chars.py`): stylized and toy-like, with big heads, dot eyes and a driven mouth: the Dev (teal hoodie, apron, tool belt), the CEO (ermine cape with spots, red lining), the mods (MOD vests, brooms), the VIP bots (gunmetal suits, gold VIP badges, cyan eye slits, briefcases), the good bots (small, homemade, screws and antenna) and the hype man (a black silhouette with a cap).
  - **The switch:** `--look final` in `scenes/blender/animatic.py` turns all of this on. The grey-box stays the default, so M3 still reproduces.
- **Iterations** (stills at draft720: S01a, S02, S12, S14, S18, S27, S34, S39b; v1–v4 in `archive/renders/m4/`):
  - **v1:** the park and cemetery were black, the night uniformly orange, the windows and lobby blown out.
  - **v2:** the payphone gets a backlit PHONE sign and its own light; the lobby light is cold and dimmer.
  - **v3:**
    - the windows' unlit glass is now dark (they read as cream slabs before);
    - a stronger blue moon and night sky;
    - a soft cool moonlight fill over the park.
  - **v4:** the unlit neon is dark, so READ-ONLY doesn't show before S14.
  - **v5:** the headstones are plain pale stone (textured concrete was too dark to read), with lettering about 0.15 m high, "large enough to read on a phone" (brief). S39b's dolly is slower (3 m in 4 s), so the inscriptions don't smear.
- **Commands:**
  - `.venv/bin/python -I scripts/fetch_textures.py`
  - `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m4/look_v5 --profile draft720 --look final --times -15.5 3.5 43.6 51.6 61.8 101.5 125.0 144.5`
  - Sheet: an inline PIL script → `renders/m4/m4_look_v5.jpg`
- **Known weak spots, for after the look is approved:**
  - the upper windows are plain lit panes, with no frames or curtains;
  - the lobby is bare;
  - the S01a morning shows no daylight outside;
  - the sign bands are plain boards.
- **Status:** **The look test is ready for review**, before the Act 1 renders.

## 2026-10-30T06:29:44-04:00 — M4 look test approved; grunge pass next

- **What:** The human approved the look test (`renders/m4/m4_look_v5.jpg`, `style/style_spec.md`) with one note: "make sure it's grungy" (human_interventions, same time). Next, before the Act 1 renders: a grunge pass on the set (stains, grime, litter, tags, worn signs), then the known weak spots, then Rhubarb lip sync.

## 2026-10-30T06:40:44-04:00 — M4: the grunge pass

- **What:** The human's note on the look test, "make sure it's grungy", is applied to the whole block. The final look only; the grey-box is unchanged.
  - **The materials** (`gb.grime`, amounts in `config/look.json` → `grime`):
    - procedural dirt blotches, run-off streaks and rising damp on the facades, shutters, signs, trim, curbs, plywood and payphone;
    - gum spots and cracks in the sidewalks;
    - puddles in the asphalt;
    - weathered headstones, which stay readable.
  - **The set dressing** (`scenes/blender/sets/grunge.py`):
    - **Windows:** frames and sills, plus blinds, curtains, foil and AC units. The coverings dim with their window's light at S15.
    - **Fire escapes** on four brick buildings.
    - **Decals:** tags on the shutters, which roll down with them and are kept clear of "UNDER NEW MANAGEMENT", and layered torn posters on the party-wall piers, the FOR LEASE plywood, the corner wall and the payphone post.
    - **The street:** litter, bag piles, cardboard and weeds.
    - **Overhead:** the trolley wire, span wires, facade cables and two utility poles.
    - **The park:** leaves.
  - **Kept clean:** the tower and its sidewalk, and the people. No tents, bedrolls or carts, per the guardrail on unhoused people.
- **Decals:** `scripts/gen_grunge_decals.py` (PIL, fixed seed) makes 12 tags and throw-ups and 10 posters. They're shapes only: no letters, no real tags, no text on the posters, and no REC red or Reddit orange-red. `assets/gen/grunge/` is git-ignored and regenerable.
- **Iterations** (draft720 stills; v1–v3 in `archive/renders/m4/`):
  - **v1:** too clean on the shutters, signs and stones.
  - **v2:** more grime and more tags; the stones lean. But a tag covered "UNDER NEW MANAGEMENT" (S27), the puddles flooded the street (S28), and a payphone flyer sat in S03's close-up.
  - **v3:** weathered stones; tags placed clear of the sign.
  - **v4:** smaller puddles; the payphone flyers moved low.
- **Commands:**
  - `.venv/bin/python -I scripts/gen_grunge_decals.py`
  - `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m4/grunge_v4 --profile draft720 --look final --times -15.5 3.5 43.6 51.6 61.8 101.5 125.0 144.5 58.5 104.0`
  - `.venv/bin/python -I scripts/look_sheet.py renders/m4/grunge_v4 renders/m4/m4_grunge_v4.jpg <labels>`
- **Status:** the grunge pass is done. Next: the weak spots (lobby, S01a daylight), Rhubarb lip sync, then the Act 1 renders by section.

## 2026-10-30T06:50:59-04:00 — M4: lip sync (mouth shapes from the aligner; Rhubarb blocked)

- **What:** Act 1's singing mouths now take shapes: Rhubarb Lip Sync's mouth set, A–H and X.
  - **Rhubarb wasn't run.** The session's permission check blocked downloading and running its release binary (v1.14.0 from GitHub), so it's left for the human to allow (R3) if wanted.
  - **The shapes:** `scripts/visemes.py` re-aligns each sung line with the M2 aligner (torchaudio MMS_FA), keeps every letter's span, and maps letters and digraphs onto Rhubarb's shapes, resting where the stem is quiet. The result is `timing/visemes.json`, with 62 lines.
  - **On the figures:** `gb.mouth` keys the jaw's width and opening per shape in the final look. The grey-box keeps the loudness drive.
- **Command:** `.venv/bin/python -I scripts/visemes.py`
- **Checked:** S04 stills 0.2 s apart show closed, round and open mouths in time with the line.

## 2026-10-30T06:51:20-04:00 — M4: weak spots: the lobby, the little door, interior grime

- **The lobby** (final look only), still clean and cold:
  - fins on the back wall around the screen, and light strips in the ceiling;
  - clipped topiary in white planters either side of the throne;
  - an unstaffed reception desk, and glass security gates.
- **The little door (S25)** stood in front of the lobby all night as a black box. It's now hidden until the wall goes up in S24, since it belongs to the wall. This is a bug fix; S24 and S25's framing are unchanged.
- **The grey-box's flat graffiti squares** (shops 2 and 6) are left out of the final look; the grunge pass's tags replace them.
- **Stucco grime** is at 0.7: the Dev's back wall read as mould at 0.85.
- **Checked:** S05, S10, S18 and S20 stills.
- **Still open:**
  - S01a shows no daylight (the eatery's door is solid);
  - the sign bands are boards, now grimy.

  Both are left for M6, when the pre-roll and bookends are made.

## 2026-10-30T06:52:14-04:00 — M4: Act 1's overlays and in-world screens (JS)

- **What:** every Act 1 JS overlay in the brief, drawn in HTML/canvas and captured with Puppeteer (brief, "Overlays"). Generic UI only, in Inter and JetBrains Mono, as the set's lettering. The cues come from the timing map and word alignment (`scripts/overlay_cues.py` → `overlays/cues.json`).
  - **Over the picture** (`overlays/overlay.html`, `overlays/render.mjs`, 443 frames → `renders/overlays/act1/`), composited in the edit:
    - **S03:** the phone line's waveform from the lead stem, spiking red on "recorded", with a blinking REC.
    - **S06:** DAYS LEFT, 30 to 0 on sixteenth notes.
    - **S07–S08:** the RUNNING TOTAL in $0.24 steps, then faster, landing on $20,000,000.00.
    - **S13:** a find bar typing "threat", then "0 results".
    - **S35:** ACCOUNTS BANNED climbing to 144,926.
  - **On the set** (`overlays/screens.html`, `overlays/screens.mjs` → `renders/screens/<name>/`), mapped as image sequences by `scenes/blender/screens.py` in place of the grey-box's static text:
    - **S10:** the lobby screen flashes BLACKMAIL on the eighth notes, red and white.
    - **S16:** the pawn shop's LED counts down from 48:00:00.
    - **S20:** the lobby's traffic chart dips on "dark" and bounces back past where it was on "bounced"; its head hops on each beat with the CEO's ball.
    - **S30:** a green dot-matrix ticker on the band's street face: "IPO ▲ OPENING BELL ▲ UP UP UP ▲ NEW MANAGEMENT ▲ USER CONTENT NOT INCLUDED". It has no figures or ticker symbol, so it makes no factual claim for M8 to check. It's a 24 s loop, slow enough that motion blur doesn't double the dots.
- **The edit:** `scripts/animatic_assemble.py` gains `--overlay DIR` (composites the overlay; drops the bracketed notes for drawn overlays) and `--from/--to` (section cuts with matching audio and captions).
- **Commands:**
  - `.venv/bin/python -I scripts/overlay_cues.py`
  - `node overlays/screens.mjs`
  - `node overlays/render.mjs`
- **Checked:** stills of each overlay, and S10, S16, S20 and S30 rendered with their screens.
- **Next:** the Act 1 render (final profile, S02–S39e, frames 435–4120), running.

## 2026-10-30T08:31:00-04:00 — M4 lip sync: Rhubarb Lip Sync itself

- **Why:** the human allowed Rhubarb (human_interventions, 08:22, R3).
- **What:** `scripts/rhubarb_visemes.py` cuts each of the 62 sung lines from its stem (padded 0.25 s, 16 kHz mono), runs Rhubarb 1.14.0 on it with the line's text as the dialog file (PocketSphinx, extended shapes GHX), and writes the cues in song seconds to `timing/visemes.json`. Same format, so `gb.mouth()` is unchanged.
- **Rhubarb:** https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Linux.zip, SHA-256 a9a9074862cff47b2d59b8bf399a678a3b0b74f9452ad6ad94cb292913dd8667, unpacked to `tools/` (git-ignored, never archived).
- **Superseded:** the MMS_FA mapping's output → `archive/timing/visemes_mms_superseded.json`. `scripts/visemes.py` stays as the record of how it was made.
- **Command:** `.venv/bin/python -I scripts/rhubarb_visemes.py` (7 min).
- **Act 1 render** (`renders/m4/act1/frames`, 3,686 frames) finished with the old mouths and before the detail note; it serves as the survey for the detail pass and will be re-rendered after it.

## 2026-10-30T09:05:00-04:00 — M4 detail pass: survey, CC0 models, hooks

- **Why:** the human's note: "pretty much all of the scenes need more detail" (human_interventions, 08:22, R1).
- **Survey:** one frame from the middle of every Act 1 shot of the finished render (`renders/m4/survey/page_1..5.jpg`). What's thin:
  - **Around the block:** a black void. There is nothing across the cross street but two plain boxes, and nothing behind the rows, the tower or the park; the aerials (S15, S23, S26) show the block floating in black. The sky is flat.
  - **The street:** lamps and litter only. No cars, hydrants, meters, bins, markings or trees.
  - **The interiors:** the Dev's shop is shelves of blank boxes; the eatery's steam table and menu cards are blank; the other shops are empty rooms; the lobby is boxes and spheres.
  - **The gags' props are the grey-box's boxes:** the adding machine, cassette, boombox, magnifier, van, trucks, crates, briefcase, arrows, hoses, bell, funnel, coffin, doghouse, lanterns.
  - **The park and cemetery:** flat grass in front of a black wall.
  - **The figures:** no hair, ears or noses, and plain clothes.
- **Plan:** a detail pass in five areas (`scenes/blender/sets/detail.py`): `city`, `street`, `interiors`, `parkdress` (set dressing, the end of `block.build()`) and `props` (after `shots.stage()`, dressing the gags' objects in place so every shot's keys and visibility stay as approved). The figures get their detail in `chars.py`. Then look-test stills of every shot, for review before Act 1 is rendered again.
- **CC0 models:** 72 Poly Haven models (1k glTF), the same source as the textures. `scripts/fetch_models.py` → `assets/models/` (git-ignored, 273 MB); `assets/models/sources.tsv` records every file's URL, MD5 and licence. `decorative_book_set_01` has no glTF and was skipped.
  - **Checked** in a contact render (`renders/m4/kit_contact.jpg`). `plastic_crate_01` ("GALLER" moulded in its side) and `gaming_console` (a wordmark) read as brands, so they are fetched but never placed.
- **Kit:** `scenes/blender/lib/kit.py` imports each model once as one mesh, which all its copies share. `swap()` gives a grey-box object a model's mesh but keeps its keys.
- **Commands:**
  - `.venv/bin/python -I scripts/fetch_models.py`
  - contact render: an inline Blender script (`kit.place` per model).

## 2026-10-30T10:20:00-04:00 — M4 detail pass: the gags' props and the figures

- **Props** (`scenes/blender/sets/props.py`, called after `shots.stage()`). Each grey-box object keeps its name, keys and visibility and takes a modelled mesh (`scenes/blender/lib/mk.py`, a procedural builder) or a CC0 one (`kit.swap`):
  - **Verse 1:**
    - the adding machine (keys, crank, paper roll);
    - the tear-off calendar, JUNE 1 to 28, over a board with the 30th ringed;
    - the envelope ("IMPORTANT: NEW PRICING");
    - S09's notice, as strips of tape: "0.24 +" down the columns, 20,000,000.00 at the foot, stapled;
    - the cassette, labelled "phone call / do not tape over";
    - the boombox and the magnifying glass (CC0).
  - **Verse 2:**
    - the locksmith van;
    - generic down arrows, pale grey, not the site's colours;
    - ribbed vacuum hoses from the VIP bots' backs into the mail slots;
    - S24's brick wall, laid in ten bands, not a stretched box;
    - the briefcase, with gold latches.
  - **Verse 3:**
    - box trucks and the archive van, lettered on both sides (the cameras see some from the far side);
    - slatted crates;
    - a cast bell on an iron yoke;
    - a white lectern with a mic;
    - the banner's rods;
    - sticky notes reading "thanks, this worked";
    - a steel funnel;
    - the brooms (CC0) standing in a crate;
    - the PAYROLL envelope;
    - the rubber band;
    - a chalk outline round YOUR LAND.
  - **The eulogy:**
    - the shoebox coffin with tissue, its lid propped, on two slatted crates, and the tiny robot with its eyes closed;
    - the "good bot" notes;
    - a gabled doghouse with an empty bowl;
    - frames round the lanterns;
    - the shovel (CC0).
  - **The balcony** (S22, S23, S30 were near black):
    - its opaque rail is now clear glass between steel posts;
    - a cold spot from the tower lights it, all night.
- **Printed and handwritten surfaces:** `scripts/gen_detail_props.py` → `assets/gen/detail/props/` (git-ignored). The handwriting is Oooh Baby (OFL), vendored from Not Yet into `assets/fonts/` and added to `SHA256SUMS`.
- **The figures** (`scenes/blender/sets/chars.py`). The lip-sync mouths are unchanged.
  - **On everyone:** a neck, ears, a nose, brows, catchlights in the eyes, hair (crop, bun, beanie, curls, cap or bald, seeded by name) and white soles.
  - **The Dev:** curls, the hoodie's drawstrings, a canvas apron with a pocket and neck strap (it read as a box).
  - **The CEO:** in S10, on the phone.
  - **The mods:** reflective tape on the vests; real brooms (CC0).
  - **S21's mannequins:** faceless, in plastic white.
  - **The bouncer:** shaved head, dark glasses.
  - **The VIP bots:** shoulder pads, lapels, ear bolts, a mouth grille, latches on the briefcases.
  - **The good bots:** each one different (a claw arm, a patch, wheels).
- **Checked:** stills of S06–S13, S21–S25, S28–S39a and S04–S27's figures, built alone (`DETAIL_ONLY=props`) in `renders/m4/detail_props/v1..v5`.
- **Fixed on the way:** the doghouse roof's slopes ran the wrong way.
- **Commands:**
  - `.venv/bin/python -I scripts/gen_detail_props.py`
  - `DETAIL_ONLY=props blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m4/detail_props/vN --profile draft720 --look final --times …`

## 2026-10-30T10:55:00-04:00 — M4 detail pass: the park and the cemetery

- **What** (`scenes/blender/sets/parkdress.py`; built by a sub-agent of this session, and checked here):
  - **Ground:** a lumpy lawn with worn paths, a trampled ring round the coffin and bare patches; about 50k grass tufts, longer at the edges; pebbles; leaves drifted against the walls.
  - **Iron:** pickets with spear finials on the fence, and an open double gate. Pickets are lost in front of the doghouse, so S38 reads BOT DEFENSE. An old railing with a gate stands by the plots.
  - **Planting:** hedges, bushes, weed clumps, and three thinned late-autumn trees (CC0 `tree_small_02`, with 22% of their leaves kept).
  - **Furniture:** two iron benches, a bin, and one sodium park lamp (160 W).
  - **The cemetery:**
    - an old brick wall with piers on three sides;
    - 16 weathered blank stones, an obelisk, an urn, a kerbed grave and a ledger;
    - real earth mounds on the plots;
    - the open grave dark and edged with a board, with a spoil heap.
  - **Kept readable:** every inscribed stone, and nothing new carries text.
- **Here:**
  - **The 144,926 markers** (`block.py`, final look) read as one pale slab. They are now laid in blocks with narrow aisles, each a little taller or shorter and leaning, so the field reads as rows of tiny markers.
  - **The shovel** stands in the spoil heap.
- **Timing (measured by the sub-agent):** about +0.45 s/frame at the final profile, the trees most of it.
- **Checked:**
  - the sub-agent's `renders/m4/detail_park/v9`, `v10`;
  - with the props: `renders/m4/detail_park/mine1..3` (S35, S39a, S39c, S39e).

## 2026-10-30T11:05:00-04:00 — Headstones: one arched solid, inscriptions engraved and fitted

- **Why:** the human's note (human_interventions, 11:05, R1).
- **What** (`block.headstone()`, final look only; the grey-box is unchanged):
  - **The shape:** each stone is one solid, a slab with a smooth 48-segment arched top. Before, it was a box plus a 16-sided cylinder, which read as a polygon. The cylinder's face also covered the upper letters, so the first engraving tests lost words.
  - **The inscriptions:**
    - Each is shrunk to fit within the stone's margins: 76% of its width and 62% of its height.
    - Each is cut into the face 5 mm deep (a Boolean, applied once at build time), and the cut takes a darker, rougher stone.
    - There is no black lettering any more.
- **Cost:** about 40 s more to build, and none per frame. Evaluating the Boolean every frame had quadrupled the time per still.
- **Checked:** S36, S39b, S39d and S39e (`renders/m4/detail_park/stones5`; sheet `renders/m4/stones_engraved.jpg`).

## 2026-10-30T11:40:00-04:00 — M4 detail pass: the interiors

- **What** (`scenes/blender/sets/interiors.py`, `scripts/gen_detail_interiors.py` → `assets/gen/detail/interiors/`; built by a sub-agent of this session, and checked here). Each room is merged into one mesh. Its fluorescents, cooler, TV, case lights and backlit window signs are driven from the shop's own light, so they go dark with it at S15.
  - **The Dev's shop:**
    - stocked steel shelving, with his six boxed apps (made-up names), repair kits, parts bins, tablets and cables;
    - a workbench under a pegboard;
    - the register, a phone case, the price list and the framed first dollar (June 2008);
    - "WE FIX APPS" and "SCREEN REPAIR" in the window, and an OPEN sign.
  - **The eatery:**
    - six pans of food in the steam table;
    - stockpots, the rice cooker and trays;
    - a chalk menu (a made-up turo-turo list) with numbered dish cards;
    - real ladder-back chairs and tables, with condiment caddies (the breakfast table stays clear);
    - a cooler, a water dispenser, the TV, ceiling fans, a calendar, a rice-terrace print, paper-star garlands and a parol;
    - nothing taken from the real restaurant.
  - **The pawn shop:** lit jewellery cases, guitars, TVs, cameras, clocks, and bars inside the window.
  - **The other shops** are each themed to their name. FOR LEASE stays empty.
  - **The lobby:**
    - server racks with bezels, vents, blinking blue, white and green LEDs, and draped cables;
    - a white display of blank "OFFICIAL" boxes (the Dev's apps with the names taken off), with the placard "Now with fewer features.";
    - real plants, two lounge groups, and monitors on the desk.
- **Here:**
  - `props.build()` calls `interiors.staged()`, which hides the grey-box display that `shots.stage()` makes by the glass.
  - **S18:** the CEO now sits on the throne. He had stood on its seat. He sits with thighs forward and shins down, and his root is lowered (`chars.py`).
- **Left as they are:**
  - small red parts on the CC0 pliers and desk lamp, and a fictional maker's plate on the register;
  - the S05 Dev standing out of frame. That's as it was at M3.
- **Timing:** not yet measured, because the GPU was shared by the sub-agents. To be measured on the combined build.
- **Checked:** the sub-agent's `renders/m4/detail_interiors/v1..v7`, and `renders/m4/detail_interiors/mine1` (S01a, S04, S05, S07, S18, S20).

## 2026-10-30T12:30:00-04:00 — M4 detail pass: the city and the street; the haze bounded, so the moon lights

- **What** (`scenes/blender/sets/city.py`, `street.py`; built by a sub-agent of this session, and checked here):
  - **The sky:** a night-only city glow (warm haze at the horizon fading to night blue), keyed off by day.
  - **The city:**
    - streets, cross streets, the alley and outer rings;
    - about 30 merged building objects with one procedural facade shader: window grids lit warm or a few cool, brick or paint, cornices and roofs, storefronts on street faces;
    - about 80 skyline towers, mostly north-east;
    - far lamps.
  - **The corner:** the two plain `corner.far` boxes are hidden, not deleted. Six generic storefronts take their place (LAUNDRY, GROCERY · DELI, DONUTS…), with awnings, a HOTEL blade sign and fire escapes.
  - **The block's roofs:** parapets, cornices, water tanks, HVAC units, vents, bulkheads and antennas.
  - **The street:**
    - about 110 modelled cars, unbadged and in muted colours, kept out of every gag's path;
    - hydrants (the CC0 model repainted white);
    - bins, utility boxes, manholes, drains, meters, nameless newspaper boxes and a bike rack;
    - ONE WAY and SPEED LIMIT 25 signs. There are no stop signs or signals, since red is reserved.
    - worn crosswalks and lane paint;
    - two street trees, thinned.
  - **The tower's frontage:** a clean granite plaza, steel bollards, and six security cameras with tiny REC lights. They're red because they record, which the style spec allows.
- **Found by the sub-agent:** the world-volume haze (`shots.light()`) absorbed the sun and the moon entirely, because Eevee treats a world volume as infinite. Since M3, nothing has been lit by the moon fill, or by the pre-roll's sun.
  - **Fixed:** the haze is now a 300 × 300 × 60 m box with a Principled Volume at the same density.
  - `city.FAKE_MOON` (the sub-agent's stand-in moonlight) is set to 0.
  - **Effect:** the night now has the cool moon fill the style spec describes. Walls and roofs read as shapes under a blue night, not black, so the night is a little brighter than the approved look test.
- **Timing (measured by the sub-agent):** city and street add +0.45 to 0.6 s/frame at the final profile.
- **Checked:**
  - the sub-agent's `renders/m4/detail_city/v4..v8`;
  - the full build in `renders/m4/detail_all/v1` (S01a, S02, S03, S14, S15, S23, S27, S39).

## 2026-10-30T12:50:00-04:00 — M4 detail pass: look test of every Act 1 shot, for review

- **What:** one 720p still from the middle of every shot, S01a and S01e–S40 (46 stills), with all five areas built. Contact sheets: `renders/m4/m4_detail_1..4.jpg`.
- **Command:** `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m4/detail_all/survey --profile draft720 --look final --times -15.5 <each shot's middle>`
- **Timing:** the build takes about 56 s, and each 720p still about 3 s, including motion blur.
- **Weak spots seen:**
  - **S22:** the CEO is still hidden at mid-shot behind a falling arrow and the balcony's underside.
  - **S39e:** the engraving is low-contrast in the open.
  - **S01a:** the parol's streamers cross the frame.
- **Next:** the human's review of the sheets, then Act 1 re-rendered at 720p (about 3 h), then the section clips for the M4 gate.

## 2026-10-30T13:30:00-04:00 — The figures rebuilt: continuous bodies

- **Why:** the human's note (human_interventions, 13:30, R1).
- **What was wrong:** a lineup (`renders/m4/lineup_v1.png`) showed the bodies as separate blobs. The arms floated with no shoulders, the torso was an egg on two tubes, the vests were boxes, and the CEO's cape and lining wrapped his front like a red sack.
- **What** (`scenes/blender/sets/chars.py`). Same names, the same `jaw` for the lip sync, the same calls from `shots.py`:
  - **Bodies:** each body is a skeleton of joints with radii (Blender's Skin modifier, subdivided, applied once at build), so shoulders, elbows and knees join.
    - The top runs from hem to neck with both arms in one piece.
    - Each leg is its own chain under the hem. A branched pelvis had folded into flaps.
  - **Poses** (`POSES`): stand, sit (S18 on the throne; this replaces the earlier fix) and phone (S10).
  - **Hands, feet and faces:** mitten hands with thumbs; rounded shoes with white soles; whites to the eyes with dark pupils and catchlights; the head slightly egg-shaped.
  - **The mods' vests** are shaped to the body. The reflective tape runs round them, and the lettering sits on the vest's surface.
  - **The Dev:** his apron wraps round the body from chest to thigh, with a pocket, a neck strap and a round tool belt.
  - **The CEO's cape** hangs from the shoulders behind him. It is open at the front, with the red lining inside, and has an ermine collar with spots.
  - **Unchanged:** the VIP bots and good bots, which are boxy robots on purpose.
- **Checked:**
  - a lineup of the cast (`renders/m4/lineup_v7.png`);
  - S04, S09, S10, S17, S18, S19, S25 and S27 in their shots (`renders/m4/figures/v1`, `v2`);
  - sheet: `renders/m4/m4_figures.jpg`.

## 2026-10-30T13:45:00-04:00 — M4: Act 1 render v2 (720p, detail pass), started

- **Why:** the human approved the detail pass and the figures (human_interventions, 13:45, R1). Review renders stay at 720p (human_interventions, 09:40).
- **What:** S02–S39e (song 0.14–153.68), `draft720` profile, final look, into `renders/m4/act1_v2/frames`. The first Act 1 render (`renders/m4/act1/frames`, before the detail pass) is superseded. Frame sequences are never archived; it stays where it is until it's cleaned up.
- **Command:** `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m4/act1_v2/frames --profile draft720 --look final --from 0.14 --to 153.68 --resume`

## 2026-10-30T13:26:00-04:00 — M4: Act 1 render v2 done; section clips cut for the gate

- **Render:** 3,686 frames (f_00435–f_04119), 1280×720, about 3.0 s a frame, 10:11–13:17. Two "Failed to create GPU texture from Blender image" errors in the log (before the first frame, and at f_01769). The frames either side match and nothing visible is missing; watch for a blank texture in review.
- **Correction:** the two 13:45 stamps above (production_log and human_interventions, "detail pass approved") should read about 10:10. The commit ed29777 is 10:10:26 and the first frame was written 10:11:58. They're left as written; this entry corrects them.
- **Assembler fix (`scripts/animatic_assemble.py`):** the full-act cut failed about 47 s in with ffmpeg error -28 ("No space left on device"); /tmp and the disk both had space. The cause: overlay composites were saved as RGB and the renders are RGBA, so every switch between them rebuilt the filter graph and restarted libass, and the ninth restart failed. Composites are now saved as RGBA. The section clips, which were shorter, hadn't hit it.
- **Caption fonts:** the ASS styles named "Inter" and "JetBrains Mono", but the vendored files are "Inter Medium Flat" and "JetBrains Mono SemiBold Flat", so libass fell back to Noto Sans (since M3). The styles now name the vendored families. These are review captions only.
- **Clips:** `renders/m4/sections/1_intro … 7_goodbot.mp4` (the shots/m4_review.md table) and `renders/m4/m4_act1.mp4` (153.5 s), each `--overlay renders/overlays/act1` (1080p overlays scaled to 720p).
- **Also committed:** `shots/m4_review.md` (720p, the detail pass, Rhubarb) and `archive/timing/visemes_mms_superseded.json` (the MMS visemes, superseded by Rhubarb).
- **QC:** stills at 10, 35, 55, 75, 95, 112, 128 and 145 s. The overlays and the karaoke captions are present. S22's CEO still reads small on the balcony (a known weak spot).

## 2026-10-30T15:05:44-04:00 — M4: flicker fixed (z-fighting); S06, S11–S12 and S31 re-staged

- **Why:** the human's notes on the Act 1 clips (human_interventions, same time, R1).
- **Diagnosis:**
  - Freezing the camera at each flicker hotspot (one-frame brightness jumps on a 16×9 grid) made the frames identical. So the flicker came from camera movement, not the scene: coplanar surfaces swapped depth order as the camera moved (brick and stucco at 0:11, for one).
  - A ray-cast survey (every 12th frame, a 64×36 grid, a second surface within 2 mm of the first) found 207 surface pairs and 2,366 hits. The largest groups: the park's ground under the lawn, layered posters 2 mm apart, the shop piers against the side walls, the headstones' old cylinder tops (their hide_render was undone by the inherited visibility keys), the lobby ceiling against the tower, and the chalk squares.
  - The underlying cause: the cameras' near clip of 0.02 m (far 800 m) gave about 1 mm of depth precision at 20 m.
- **Fixes:**
  - The near clip is now 0.1 m (`lib/gb.py`).
  - The park's base ground sits 12 mm under the lawn.
  - Posters and flyers are 5 mm apart.
  - The shop side walls are 5 mm inside the piers.
  - The chalk squares are raised.
  - The lobby ceiling is inset.
  - The headstones' tops are given an empty mesh.
  - A second survey: 166 pairs and 672 hits, almost all of them intended intersections (grass roots in the lawn, eyes in heads, aprons on bodies).
- **S06** (the calendar was inside the wall: the plaster at x −18.11 was in front of the whole stack, and the pages showed only through depth fighting):
  - The calendar is now 3 cm off the plaster.
  - One camera sees both the mail slot and the calendar, then pushes in.
  - The pages go two at a time, 0.3 s apart (JUNE 1, 7, 13, 19, 25), and fall to the door side.
  - The ringed 30 holds about 0.9 s.
- **S11–S12** (the cassette):
  - It's rebuilt as a compact cassette at 1.5× scale: a shell, five screws, a smoked window with two tape packs and toothed hubs, the trapezoid with the head openings, and a label with its window cut out ("A · PHONE CALL / do not tape over!", C-60). `scripts/gen_detail_props.py` regenerated `assets/gen/detail/props/*` (git-ignored and regenerable). The old cassette.png was overwritten, not archived; it regenerates from the previous commit's script.
  - The Dev has new "reach" and "hold" poses (`sets/chars.py`).
  - S11: he reaches into the handset for 1.3 s, then turns and holds the tape up; the camera pushes from 40 to 50 mm.
  - S12: it opens close on the tape in his raised hand (50 mm), then pulls back to 24 mm as it goes into the boombox and the windows open (from 1.8 s).
  - It no longer flies 9 m across the cut.
- **S31** (the notes were behind the shutter: at FRONT+0.03, with the shutter at +0.12):
  - Ten notes, 0.3 m, on PAWN's shutter at eye height, lit by a spot (the streetlight's spill).
  - They hold 1.0 s, then peel 0.16 s apart and arc 1.8 s into the funnel. The funnel is over the roof hatch of a truck in the near lane, about 5 m away.
  - The camera holds on the wall to 2.4 s, cranes up to look into the funnel, then tilts to the billboard and zooms from 32 to 110 mm.
  - The billboard has moved to the roof's front edge (from 2 m back, where the roof hid it from the street), and S31's line is 3.0 m text.
- **Tests:** `renders/m4/gags_v1`…`gags_v6`, stills every 3–6 frames. The S03 close-up now shows the bigger cassette under the REC light.

## 2026-10-30T15:07:10-04:00 — M4: Act 1 render v3 started

- **What:** S02–S39e at 720p with the flicker fixes and the re-staged gags (the commit before this one), into `renders/m4/act1_v3/frames`. v2 is superseded; frame sequences are never archived.
- **Command:** `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m4/act1_v3/frames --profile draft720 --look final --from 0.14 --to 153.68 --resume`

## 2026-10-30T16:16:37-04:00 — M4: the adding-machine tape made real; S07, S08, S09 and S13 re-staged

- **Why:** the human's go-ahead (human_interventions, same time, R1). In the v2 render there was no tape: in S07 none came off the machine, in S08 nothing ran out the door, and in S13 the 8 cm grey-box strip read as a painted curb line. The S09 notice was hidden behind the Dev, and the magnifying glass crossed 7 m in 3 s with a black lens.
- **The tape (`sets/props.py` tape_run):**
  - One printed paper ribbon, 8.5 cm wide, about 27 m long: from the roll, over the counter edge, across the floor, out the door, along the sidewalk at y −7.6 (at −7.0 it lay against the curb's painted line), round the corner and over the tracks.
  - Each stretch is draped by ray-casting onto the highest upward-facing surface below a height limit (counter, floor, threshold, sidewalk, street), 3 mm up.
  - It's revealed by arc length through the material (a driven value against an "arc" UV, dithered alpha), keyed from `shots.tape_staging`: 0 to 2.6 m in S07, the rest by the end of S08. It lies there through S13.
  - The grey-box's stretched boxes are replaced or blanked.
- **The tape texture (`scripts/gen_detail_props.py` tape_strip):**
  - "0.24+" printed along the tape, large: a real machine prints across it, but S13 sees it from the side and it has to read.
  - The receipt texture (S09) now has the total in bold red marker, "$20,000,000", ringed, with "due June 30".
  - The notice gets three staples and sits flat on the door's face (found by ray cast; it floated 10 cm off).
- **Staging:**
  - S07: closer on the machine; the tape spews over the counter edge to the floor.
  - S08: a crane from the doorstep, up and back to 6 m, until the whole run shows. A first try chased the tape's end at 1.4 m and blurred it into nothing.
  - S09: the notice slaps on (scale 0 → 1.1 → 1); the Dev stands aside; framed to read.
  - S13: the glass moves 2.5 m in the shot, 0.24 m up over the tape; the camera is on the shop side (the curb's posts blocked the street side), at 40 mm. The lens is clear blended glass at alpha 0.12; with transmission it rendered black, and raytraced refraction didn't help.
- **Tests:** `renders/m4/gags_v7`…`gags_v9`.
- **The v3 render:** stopped at f_01659. Its 544 frames from S07 (f_01116) on were deleted, since they had the old staging (frame sequences are regenerable and never archived), and it resumes from there with --resume.

## 2026-10-30T18:57:10-04:00 — M4: Act 1 v3 rendered and cut; S09's notice text fitted

- **Render:** finished, 3,686 frames (f_00435–f_04120). Two "Failed to create GPU texture" warnings, as in v2; nothing visible.
- **QC, flicker:** the 16×9 grid brightness check gives 871 cell events against v2's 954. The windows that remain high (about 50–52 s, 90–92 s, 96 s and 137–140 s) were checked by eye: fast pans over the facades, the fence passing the doghouse, the robots' eye lights. None of them is a surface fighting another. The sharpness at 50–51 s varies about ±15% frame to frame, normal for a pan over changing detail.
- **QC, gags:** stills of S06, S07–S09, S11–S12 and S31 checked. One fault: S09's "$20,000,000" at size 190 was wider than the 1000 px receipt texture and ran off both edges ("20,000,00").
- **Fix:** `scripts/gen_detail_props.py` receipt() now takes the largest size up to 190 that fits inside the ring. The textures were regenerated (git-ignored and regenerable; the others are the same, from the same seed), and S09 (34.03–36.81 s, 67 frames) was re-rendered over its old frames (log `renders/m4/act1_v3/render_s09.log`).
- **Cut:** the seven section clips in `renders/m4/sections_v3/` and the full act in `renders/m4/m4_act1_v3.mp4` (153.54 s). The v2 clips stay where they were. The first 2_verse1 cut, with the clipped notice, is archived as `archive/renders/m4/sections_v3_superseded/2_verse1_notice_clipped.mp4`.

## 2026-10-30T19:54:40-04:00 — M4: the human's v3 notes fixed (S03, S07–S08, S19, S20, S28, S29, S31, building flicker)

- **Why:** the human's notes on the v3 section clips (human_interventions, same day, R1).
- **Building flicker:** the first survey skipped overlaps within one object. An extended survey (it counts faces of the same object too, near-parallel faces only, with a gap that grows with distance: 2 mm, or 0.02% of the distance) found these, now spaced apart:
  - **Shop side walls** ran forward inside the piers and lintel, 5 mm under their faces. They now start behind them (`block.py`).
  - **Interior paint layers** were 5 mm off the shell walls; now 1.5 cm (`interiors.paint`).
  - **The Dev's window signs** were 3 mm in front of their plastic backing; now 9 mm.
  - **Graffiti tags** on the shutters were 2 mm apart from each other; now 6 mm (`grunge.decals`).
  - **City storefront sign faces** were 5 mm off the sign band; now 15 mm, and the lettering 15 mm more (`city.py`).
  - **Street paint** is raised from 5 mm to 1 cm; **plaza paving** from 6 mm to 1 cm over the sidewalk; **sidewalk joint lines** from 3 mm to 6 mm.
  - **The lobby ceiling's** top no longer runs 1 cm into the tower.
- **S03:** the cassette rested where the handset hangs (the 1.5× cassette was inside the handset). It is now on the post's street face beside the handset (`block.CASS_REST`); S11's grab path and opening framing start from there.
- **S07–S08, the tape:**
  - It now leaves the top of the roll, lies on the counter, goes over the edge and hangs down the counter's front to the floor. The first draped point had been past the counter's edge, so the ribbon cut a diagonal through the counter.
  - Vertical stretches keep the last heading for their width; a straight-down stretch would otherwise be zero-width.
  - Draping accepts horizontal faces that point down. The road's and the shop floor's do, and the tape went under them.
  - The haze volume's floor is the road's (z 0): stepping past it skipped the road too, and the tape landed on the far ground 1 cm under. Draped points are now clamped to z ≥ 0.
  - The tape is built last, after the interiors, so it drapes onto the shop's interior floor.
- **S19:** the mods were whole standing figures sunk 45 cm into the sidewalk. There's now a real kneel (`chars.POSES["kneel"]`: on both knees, shins flat behind, soles up, brooms planted). The camera moves low and to the side along the row: from behind they read as short people standing.
- **S20:** the ball bounced 0.7 m from the CEO with nothing touching it. He now dribbles it (`"dribble"` pose: palm down over the ball). It hits the floor on each beat and comes back to his palm between beats. The camera moves in from 11 m to about 6 m. The ball is a basketball with seams (`props.ball`).
- **S28:** the brief's forklift was never built; the crates flew 6 m through the air into a truck in the far lane. Now:
  - the truck parks at the near curb, with its side door to the sidewalk;
  - a forklift (`props.forklift`) lifts a pallet of four crates (two on two) and drives it into the hold, then backs off;
  - every crate has a white plate, "COMMENTS 2005–2023", on all four sides;
  - an A-frame reads "SIDEWALK AUCTION / all data must go" (the last line is the agent's wording), and a second lot waits beside it;
  - the camera is close to the shopfronts on the west: further out, the lamp post at x −5 stood in front of everything; from the east, the truck hid the pallet.
- **S29:** the trucks drove through at 9 m/s and the blur took their names. SEARCH and CHAT now pull up and stop, SEARCH at the door. Their names are larger, 0.85 m, on the cargo box.
- **S31:** "UNDER NEW MANAGEMENT" (x −4.33..−3.28, z 1.73..2.07) covered note 1 and the edge of note 0. Note 1 is now above the text and note 0 is 12 cm aside.
- **Tests:** `renders/m4/notes_v1`…`notes_v6`.

## 2026-10-30T20:25:33-04:00 — M4: the tape laid like paper; Act 1 render v4 started

- **Why:** the human's note that the tape still clipped into the counter and the floor (human_interventions, same time, R1).
- **What was wrong** (found with close-up debug renders, `renders/m4/tape_look_v1`, and probes of the tape against the set):
  - **Through the counter:** the placed points over the counter's edge cut its corner with a straight segment, 3 mm into the counter.
  - **Under the shop floor:** the step from the last placed point to the first laid one used that point's placeholder height of 0, so the tape sloped into the ground for 15 cm.
  - **Under narrow things:** one ray down the middle every 2 cm missed the sidewalk's joint lines (6 mm high since the flicker fix), the streetcar rails and bits of litter, so the tape ran under them.
  - **Through the door:** the Dev's door is a closed glass slab down to the floor; the tape went through it. The draping also took the door's underside for a floor.
  - **A stray scrap:** the grey-box's stub of tape at the roll (`dev.tape`) was still drawn.
- **Fix** (`sets/props.py` tape_points):
  - **Sampling:** every centimetre, with five rays across the tape's width; the highest surface wins. Litter is no longer skipped, so the tape lies over it, being newer.
  - **Stiffness:** a 1-D relaxation stands in for a cloth simulation. The paper can't bend sharper than a slope of 0.5 from anything it rests on, then it's smoothed upward only, so it rides over a joint line or a rail in a short ramp and never goes into what it lies on. A full cloth sim over the 27 m run, colliding with half the block, would be slow; this gives the same shape for paper lying on surfaces.
  - **The counter:** an arc round the front edge (1.3 mm clear of the corner), then plumb down the face, then an arc onto the floor.
  - **The door:** the Dev's door stops 18.5 cm up (`block.py`), a gap the tape runs under. Doors' undersides are skipped when draping.
  - **The scrap:** blanked.
- **Checked:**
  - no tape vertex lies inside any object;
  - nothing visible lies over the tape except things above it (the ceiling, the door leaf, the slot, the notice);
  - close-ups at the roll, the edge, the counter, the floor, the door, the curb and the rails, and stills of S07–S08 (`renders/m4/tape_look_v2`).
- **Also:** the extended flicker survey after the building fixes: 82 pairs and 1,978 hits, down from 118 and 3,432; shop12's pier against its side wall went from 50 to 2. The largest left, `int.dev` at 114, is the two faces of a 2 mm sign backing, not a fight.
- **Render v4:** all of Act 1 again (the building fixes touch nearly every shot), into `renders/m4/act1_v4/frames`.
  - Command: `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m4/act1_v4/frames --profile draft720 --look final --from 0.14 --to 153.68 --resume`

## 2026-10-31T00:00:00-04:00 — M4: Act 1 v4 cut; QC found a regression (the Dev's pegboard flickering) and fixed it

- **Render v4:** all 3,686 frames (f_00435–f_04120), exit 0. One "Failed to create GPU texture" warning, as in v3; the frames saved normally.
- **Cut:** seven section clips in `renders/m4/sections_v4/` and the full act, `renders/m4/m4_act1_v4.mp4` (153.54 s). The assembler's ffmpeg read the shell loop's stdin and clipped the start of six output names; the files were renamed to their section names (frame ranges checked from the logs).
- **Stills:** `renders/m4/review/v4_fixes_contact.jpg` (S03, S07–S09, S11, S13, S19, S20, S28, S29, S31). S28 reads as crates labelled COMMENTS 2005–2023 forklifted into the truck. In S31 no resting note touches "UNDER NEW MANAGEMENT"; the one crossing it at 115 s is flying off to the funnel.
- **Flicker QC:** a new per-pixel check for a spot that keeps jumping for one frame and coming back, shot by shot (320×180, a 4×4 block's share of the shot's frames).
  - Clean everywhere except: S16 (the countdown ticking, meant), S14, S38, S39 and S39e (camera moves past thin fence bars; aliasing, not surfaces fighting), and **S04: the Dev's pegboard**, appearing and vanishing frame to frame.
  - **Cause, a regression of the last round's fix:** `interiors.paint()` moved the side walls' paint 1.5 cm out to 2.5 cm off the shell, exactly where the pegboard quad sat (`w.p(4.0, 0.025, …)`). The survey's 64×36 grid every 12th frame never landed on it.
  - **Same cause, hidden:** the running shop's race bibs and the crochet shop's granny squares (2 cm off the wall) were now inside the paint; the price cards (3 cm) and the pawn shop's board were 5 mm off it.
- **Fix** (`sets/interiors.py`): everything flat on a painted wall now sits at least 1 cm in front of the paint: the pegboard (4.5 cm), its tools (6 cm) and cable coils (7 cm); shelving back panels (3.5–5.5 cm); the Dev's and the eatery's sign cards and the shop poster (4.5 cm); the pawn board (3.5–5.5 cm); bibs (4.5 cm); granny squares (4.5 cm); the SINCE 2008 card and the hardware shop's tool board (back wall, 2–4 cm).
- **Survey re-run** with a gap probe at each flagged pair. Truly coincident faces (gap ≤ 0.003 mm): inside the CC0 kit models (magnifier, spade, chair, fire escape), where the chalk lines cross (same colour), the park pit's floor. None shows in the pixel check. The rest are 0.3–20 mm apart.
- **Next:** re-render S03–S10 (7.75–39.25 s, the shots that see into the Dev's shop) into `renders/m4/act1_v4b/frames`, and cut v4 again from v4 plus those frames.

## 2026-10-31T00:48:45-04:00 — M4: S03–S10 re-rendered; Act 1 v5 cut and sent for the M4 gate

- **Render:** S03–S10 (7.75–39.25 s, f_00618–f_01374, 757 frames) into `renders/m4/act1_v4b/frames`, exit 0. The pegboard holds steady in the crops that flickered in v4.
- **v5 frames:** `renders/m4/act1_v5/frames` holds symlinks, v4b where it exists and v4 elsewhere (no frame copied or overwritten). Both splice frames are pixel-identical between v4 and v4b; the jumps there are the S03 and S11 camera cuts.
- **Flicker check on v5:** S04's worst spot went from 0.25 to 0.11 of frames, with no block over 0.15; S03–S13 clean.
- **Cut:** `renders/m4/sections_v5/*.mp4` and `renders/m4/m4_act1_v5.mp4` (153.54 s), with stdin closed to the assembler this time.
- **Archived:** the v4 cuts to `archive/renders/m4/v4_superseded/` (superseded by v5).
- **Review notes:** `shots/m4_review.md` points at v5 and lists the fixes for the v3 notes. Stopped at the M4 gate.

## 2026-10-31T03:21:26-04:00 — Log: M4 v5 notes from the human (R1)

- Eight notes on S02, S22, S25, S28, S29, S31, S33, S36, verbatim in human_interventions. Working through them next.

## 2026-10-31T03:48:00-04:00 — M4: the human's v5 notes (S02, S22, S25, S28, S29, S31, S33, S36); Act 1 render v6 started

- **Why:** the human's notes on v5 (human_interventions, previous entry, R1).
- **S02, flicker by the subreddit signs:** a dark wedge came and went where each shop's lintel met its piers. The lintel ran across the piers' tops and the two faces were one plane, brick against trim. It now fits between them (`block.py`). The ray survey and the single-frame pixel check both missed it; even/odd frame crops found it.
  - **New check:** `coplanar.py` (scratchpad) buckets every axis-aligned face in the scene by plane (0.5 mm) and reports same-facing overlaps between objects or materials. From it, also fixed:
    - the city's curbs, flush with their slabs' sides block-wide (now 6 mm proud);
    - the LED ticker's back on the tower's glass bands (now 3 cm off);
    - the lobby glass into its side walls;
    - posters and wall tags of neighbouring shops on a shared pier (now at different depths);
    - street-tree soil level with the sidewalk;
    - the cars' wheel arches on their sides, and their plates on their bumpers;
    - the city storefronts' awnings on their frames.
- **S02, the payphone was grey box:** modelled in `props.payphone()` into the existing objects, so the cassette's rest and the handset's swing are unchanged.
  - **Post:** square steel on a bolted base plate.
  - **Housing:** blue enamel, with the instruction card, coin slot, a 12-key keypad, coin return, the empty hook and the cord boot.
  - **Canopy:** with side panels.
  - **Handset:** earpiece, grip and mouthpiece, on a coiled cord.
  - **REC light:** moved into the grip, with its own softer glow (5, not the windows' 40, which blew it out to white at 0.5 m in S03).
- **S22, the downvotes:**
  - **Before:** both arrows fell down one line past the balcony and out of frame within a second, and read as one blur. The arrows were white because I had kept clear of the site's colours.
  - **Now:** each "downvote" (two, at 75.12 s and 76.09 s) drives a 1.3× arrow tip-first into the balcony floor, one either side of the CEO, where it shudders and stays.
  - **Colour:** blue-purple (#8f8fff), lit slightly from within, on the human's note; the shape stays generic.
  - **Camera:** at balcony level, so the CEO is larger.
- **S25, the exchange:** re-staged to the brief ("The brick wall has a little door in it. A VIP bot hands over a briefcase; the CEO hands back the keys").
  - **The door:** the little door is hinged and stands open on a dark opening behind the CEO.
  - **The handover:** the bot holds the case out on its raised arm, and the CEO takes it in his left hand (new pose, "give"). He holds out an oversized brass key ring (`props.keys25`), which goes to the bot's hand as the arm lowers.
  - **Camera:** side-on two-shot. The bot's own case at its side is hidden.
- **S28, too fast:**
  - **Timing:** it starts 1.0 s early (102.2 s, `config/shot_holds.json` and timing_map.py; S27 is now 2.02 s, S28 3.08 s), the human having allowed it to eat into the previous shot. The forklift's beats are fractions of the shot, so they slow with it. This moves S28 off the brief's 1:43.20 cue.
  - **Light:** a work light on the hold, so the lot reads in the truck's shadow.
- **S29, CHAT off frame:** CHAT stops 1 m behind SEARCH (x −2.5); the camera aims 17° further west; the archive van starts 2 m closer. CHAT, SEARCH and the bouncer are all in.
- **S31:**
  - **The notes:** ten different thank-yous ("you saved my thesis", "edit: solved, thanks!", "worked in 2015. still works"…). They're in Permanent Marker (Apache 2.0, google/fonts, vendored with its licence and checksum in `assets/fonts`), as large as fits in three lines. "came from google" was changed to "found it by search": no real company names.
  - **"People found this helpful.":** now two lines across 70% of the board.
  - **Clearance:** note 0 is 24 cm clear of the text.
- **S33:** "YOUR LAND" is in the square's front half, turned to read from the camera; the Dev stands in the back half. The opening camera was pulled back so words, feet and head are all in frame.
- **S36:**
  - **Headstones:** Poly Haven's concrete (diffuse, normal and roughness at a 0.9 m tile, roughness ×0.6 for a worn sheen), in place of the plain pale stone.
  - **Engraving:** darker (#1d1b19) so it still reads; grime on stone 0.25.
  - **Grass:** the lawn's density goes from 3% of cells to about 30% with 7 blades a tuft, and there is short grass (≤ 5 cm) among the markers, which had none.
- **Stills:** `renders/m4/notes5_v1`, `notes5_v2`.
- **Render v6:** all of Act 1 (the curb, lintel, stone and grass changes touch nearly every shot), into `renders/m4/act1_v6/frames`.

## 2026-10-31T06:14:31-04:00 — M4: the headstones vary stone to stone and read again; Act 1 v6 resumed with them
- **The human's note (R1):** the stones were hard to read and all had the same texture. Every stone shared one material, box-projected in object space with each stone's origin in the same place, so each showed the identical pattern. The concrete's formwork lines and the grime's vertical run-off fought the lettering.
- **Fix (`gb.tex_mat`: new `vary`, `flat`, `bump` options; `block.TEXOPT` sets them for "stone"):**
  - **Per stone (Object Info: Random):** its own texture offset, a tilt in the face's plane (±0.6 rad), a scale (±35%) and a tone (value ±18%, a little warmer or cooler), so no two stones match.
  - **Calmer face:** the diffuse is pulled 55% toward plain grey (#8e897f), and the normal map is at half strength.
  - **Grime:** the run-off streaks on stone are down from 0.9 to 0.4 (`config/look.json`).
- **Stills:** `renders/m4/stones_v1`, `stones_v2`. "Here lies a good bot", the S39b row, Pushshift and the S39d/e stones read clearly; each stone has a different tone and pattern.
- **Render:** v6 was stopped at f_03146 (113.0 s, before the first stone shot) and resumed with --resume, so every shot from S34 on has the new stones. Earlier frames show the cemetery only in the hook's aerial wides.

## 2026-10-31T07:08:45-04:00 — M4: Act 1 v6 cut for the M4 gate
- **Render:** `renders/m4/act1_v6/frames`, all 3,686 frames (f_00435–f_04120), draft720. It was stopped and resumed once for the headstone fix (previous entry).
- **QC:**
  - **Flicker:** the per-shot hot-spot check (flick_hot) finds no lasting flicker in S02 (worst 0.03) or anywhere in S02–S37. The moderate flags are motion: the pan in S14, the countdown's changing digits in S16, and the iron fence bars aliasing as the camera passes in S38–S39e (worst in S39e, 0.28). No coplanar surfaces. The fence is left for the 4K final's higher sample count.
  - **Stills:** S02 (payphone), S03 (REC light), S22, S25, S28, S29 (CHAT and SEARCH in frame through the shot), S31, S33, S36 and S39b–S39e (inscriptions) checked.
- **Cut:** `renders/m4/sections_v6/` (seven clips) and `renders/m4/m4_act1_v6.mp4` (153.5 s), with the overlays and the master.
- **Archive:** the v5 cuts (`sections_v5`, `m4_act1_v5.mp4` and its log) moved to `archive/renders/m4/v5_superseded/`, superseded by v6.
- **Review notes:** `shots/m4_review.md` now points to v6, with a "Since v5: your notes" section.
- **Manifest:** updated.

## 2026-10-31T07:29:43-04:00 — M4: the human's v6 notes (S26 doghouse, S28 hold, S30 banner); re-render v6b started
- **S26, the doghouse (`props.doghouse`):**
  - **Roof:** the two slopes were shorter than the slope itself and left a gap at the ridge. Each is now the slope's full length plus an eave, and they meet under a ridge cap.
  - **Doorway:** a true round arch (25 points) on straight sides; the old one had three straight segments.
  - **Sign:** found in QC: "BOT DEFENSE" stood 4.5 cm off its board and cast a ghost copy below. It now sits on the board.
- **S28, the crates vanish in the truck (`props.vehicle`, open_side):** the truck was a solid box with a black panel for its door, so the lot disappeared into the solid. It's now hollow: walls round a real 1.8 m opening down to the hold's floor, a grey lining, a dark floor and the rolled-up door's drum. The crates stay in sight, in shadow, lit a little by the work light. The forklift's lift (`HOLD_Z` 0.86 → 0.64) matches the new floor.
- **S30, "IPO" before the banner:** the text wasn't attached to the banner and hung in the air while it unrolled. It's now parented to the banner (inverse taken at full size) and unrolls with it.
- **Stills:** `renders/m4/notes6_v1`, `notes6_v2`.
- **Render v6b:** S26, S28, S30 and S34–S39 (the doghouse's shots), into `renders/m4/act1_v6b/frames`; the cut will merge them over v6.

## 2026-10-31T08:27:57-04:00 — M4: Act 1 v7 cut for the M4 gate
- **Frames:** `renders/m4/act1_v7/frames`: symlinks to v6b where re-rendered (S26, S28, S30, S34–S39; 870 frames), else v6.
- **QC:**
  - **Flicker:** flick_hot shows S26 0.07, S28 0.04 and S30 0.03. S34–S39 match v6; the fence bars still alias as the camera passes.
  - **Stills:** the doghouse (S26, S37–S38), the crates in the hold (S28) and the banner unrolling (S30) checked.
- **Cut:** `renders/m4/sections_v7/` and `renders/m4/m4_act1_v7.mp4` (153.5 s).
- **Archive:** the v6 cuts moved to `archive/renders/m4/v6_superseded/`, superseded by v7.
- **Review notes:** `shots/m4_review.md` now points to v7 and has a "Since v6: your notes" section.
- **Manifest:** updated.

## 2026-10-31T09:16:17-04:00 — M4: the human's v7 notes (the payphone's handset and a tape recorder; S18 throne; S20 dribble); re-render v7b started
- **S02–S03, the handset:**
  - **Before:** it hung from the middle of the housing's underside, its cord running up into the housing.
  - **Now:** it hangs on its coiled cord from the cord's boot under the housing's left side, and sways from there (block.HANDSET_PIVOT). The sway is gentler (0.04 rad), since a lead runs to it.
- **S02–S03, the tape (`props.recorder`):**
  - **Before:** the cassette was taped flat on the post.
  - **The recorder:** a portable cassette recorder (generic, no maker's name), 1.5x scale like the tape, taped to the post beside the handset with two bands of grey tape. The tape sits behind a smoked window in a door hinged at its bottom edge.
  - **Details:** piano keys on top (REC in red) and a speaker grille. The REC light moved from the handset to the recorder, clear of the tape. A thin lead runs from its mic jack to a suction-cup pickup on the handset's back, the way calls were taped.
  - **S03:** the camera frames the recorder and the handset, then pushes in on the REC light as the beat comes in.
  - **S11:** the Dev flips the door down, then lifts the tape out (CASS_REST is now in the recorder's well).
  - **S47:** its camera now aims at the recorder.
- **S18, the CEO through his chair:** the seat floated at knee height (0.7 m) on nothing, so his shins and cape went through it.
  - **Throne:** the seat is at sitting height (top 0.93) on a plinth set back from his shins.
  - **The CEO:** he sits on the floor's level (root 0.17), 25 cm forward, his cape's back clear of the racks. Seated, his cape ends on the seat.
- **S20, a real dribble:**
  - **The arm:** the dribbling arm is its own object (`chars.arm_chain`). A shape key blends it from "dribble" to DRIBBLE_LOW, the wrist down 18 cm. The low pose bends the same mesh at the shoulder and elbow, because a second skin of the low pose had more vertices.
  - **Timing:** the ball hits the floor on each beat. On the way up it slows into his palm; the palm rides it down and pushes it off; the hand rises to meet the next bounce. The mitten, thumb and ball are keyed every frame from one phase function, so the hand and ball stay in contact.
- **Stills:** `renders/m4/notes7_v1`–`v3`; a 2.2 s S20 clip, `renders/m4/notes7_clip`.
- **Render v7b:** 0.14–20.62, 23.38–25.88, 36.81–50.01 and 57.78–73.60 s (the payphone, the throne in the lobby shots, the CEO), into `renders/m4/act1_v7b/frames`.

## 2026-10-31T10:35:00-04:00 — M4: Act 1 v8 cut for the M4 gate
- **Frames:** `renders/m4/act1_v8/frames`: symlinks to v7b where re-rendered (1,252 frames: 0.14–20.62, 23.38–25.88, 36.81–50.01, 57.78–73.60 s), else v7's targets.
- **Render log:** three "Failed to create GPU texture" lines, one per Blender process; the same intermittent message has appeared since the first Act 1 render with no visible effect.
- **QC:**
  - **Flicker:** flick_hot matches v7 everywhere except S20, 0.07 → 0.08, which is the moving arm.
  - **Stills:** the recorder and REC light (S03), the tape out (S11), the seated CEO (S18) and the dribble (S20) checked.
- **Cut:** `renders/m4/sections_v8/` and `renders/m4/m4_act1_v8.mp4`.
- **Archive:** the v7 cuts moved to `archive/renders/m4/v7_superseded/`, superseded by v8.
- **Review notes:** `shots/m4_review.md` now points to v8 and has a "Since v7: your notes" section.
- **Manifest:** updated.

## 2026-11-01 — M4 gate passed; M5 starts
- **M4:** the human approved Act 1 v8 (human interventions, same date). Approved cut: `renders/m4/sections_v8/`, `renders/m4/m4_act1_v8.mp4`.
- **Open for the 4K render:** the fence bars' shimmer in S38–S39e.
- **Next:** M5, the lip-sync test on S43, then Act 2 (S40–S48b).

## 2026-11-01T08:37:14-05:00 — M5: reference sheets (rapper)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, text encoder `mistral_3_small_flux2_fp4_mixed.safetensors`, VAE `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0; ComfyUI (`scripts/stills.py`, graph as the `image_flux2_fp8` template, text-to-image).
- **Prompts:** `log/prompts/stills/<item>.txt`. **Inputs:** none (text only).
- **Command:** `.venv/bin/python scripts/stills.py rapper`

| Item | Seed | Output | Seconds | Status |
| --- | --- | --- | --- | --- |
| rapper | 1001 | `takes/stills/rapper/rapper_s1001.png` | 62.5 | pending (R1) |
| rapper | 1002 | `takes/stills/rapper/rapper_s1002.png` | 50.1 | kept (R1, 2026-11-01) |
| rapper | 1003 | `takes/stills/rapper/rapper_s1003.png` | 50.1 | pending (R1) |
| rapper | 1004 | `takes/stills/rapper/rapper_s1004.png` | 50.1 | pending (R1) |

## 2026-11-01T08:41:17-05:00 — M5: keyframes (S43)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S43`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S43 | 2001 | 0.92 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png | `takes/keyframes/S43/S43_s2001.png` | 108.2 | pending (R1) |
| S43 | 2002 | 0.92 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png | `takes/keyframes/S43/S43_s2002.png` | 106.1 | pending (R1) |

## 2026-11-01T08:45:06-05:00 — M5: keyframes (S43)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S43`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S43_v2 | 2001 | 1.0 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png | `takes/keyframes/S43/S43_v2_s2001.png` | 115.1 | pending (R1) |
| S43_v2 | 2002 | 1.0 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png | `takes/keyframes/S43/S43_v2_s2002.png` | 114.3 | pending (R1) |

## 2026-11-01T08:51:04-05:00 — M5: lip sync with LatentSync 1.6 (S43)

- **Model:** LatentSync 1.6 (`ByteDance/LatentSync-1.6` `latentsync_unet.pt`, code `bytedance/LatentSync` a229c39), 20 steps, guidance 2.5, DeepCache.
- **Inputs:** the V take (`config/l.json`), `audio/stems/0 Lead Vocals.wav`; a face crop of 2.6 face heights from `takes/l/<shot>/faces.json` (`scripts/l_faces.py`), 512 px, 24 fps frames labelled 25 fps with the vocal sped up 25/24. Pasted back through a feathered ellipse around the face. **Command:** `.venv/bin/python scripts/l_batch.py S43`

| Shot | Seed | Frames | Synced | Input | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S43 | 1 | 39 | 41 | `takes/v/S43/S43_moge_s2.mp4` | `takes/l/S43/S43_s1.mp4` | 22.4 | pending (R1) |
| S43 | 2 | 39 | 41 | `takes/v/S43/S43_moge_s2.mp4` | `takes/l/S43/S43_s2.mp4` | 19.5 | approved (R1, 2026-11-01): lip sync method and seed |

## 2026-11-01T08:58:00-05:00 — M5: the S43 lip-sync test (pipeline, plates, sheet, keyframe, V, lip sync)
- **Pipeline (from Folks Like Us, which built it 2026-10-19/20 on this machine):** `scripts/comfy_client.py`, `stills.py`, `keyframes.py`, `ltx_v.py`, `l_faces.py`, `l_batch.py`, and ComfyUI's FLUX.2 and LTX-2.3 templates with their API conversions in `workflows/` (brief: "export it in API format to `workflows/`"). Adapted: Read-Only's paths, no building-mask sentences, `config/l.json` lists each take with its song time. Outputs go in `takes/` (git-ignored, in the manifest).
- **Plates:** `scenes/blender/plates.py` renders a shot's own frames from the animatic build (look final) at the V size, 1280×704: beauty, 16-bit inverse depth and EXR, into `renders/m5/plates/<shot>/`. No handles past a shot's end, since its cast is hidden there; a clip is padded by holding the last frame. First frames of S41–S43 rendered.
- **The rapper faces his cameras** (`shots.py`): at rot_z 200° he looked 50° off S42's and S43's cameras, in profile for a lip-synced close-up. Now S41 147°, S42 151°, S43 154°. The first layouts are in `archive/renders/m5/plates_first_v1/`, superseded.
- **Sheet:** `rapper`, the Dev's Act 1 design made real (config/stills.json), four seeds (entry above). Seed 1002 used for the test (consistent face across the four views); the human picks at the gate.
- **Keyframe:** v1 (denoise 0.92 from the layout) kept the stand-in's cartoon head and eyes. v2 starts from noise with the layout as a reference only and asks for natural proportions: photoreal, but its background is its own (the payphone is wall-mounted, the street runs away to the right). v2 seed 2002 used.
- **V (deviation for S43):** v2's geometry doesn't match the Blender depth, which would pull the face back to the stand-in's. S43 is a near-static close-up, so its control is the template's MoGe depth estimate of the keyframe itself, with the shot's slow pull-back made by ffmpeg (zoom 1.06 → 1.0 over 41 frames, `takes/v/S43/S43_s1_c0_control.mp4`). Wider shots keep the Blender depth.
  - **Command:** `.venv/bin/python scripts/ltx_v.py takes/v/S43/S43_s1_c0_control.mp4 takes/v/S43/S43_s1_c0_first.png takes/v/S43/S43_moge_s<seed>.mp4 --prompt "$(cat log/prompts/v/S43_moge.txt)" --seed <seed> --control moge --guide 0.6`
  - **Model:** LTX-2.3 22B distilled fp8 + IC-LoRA union control (ref0.5), `workflows/video_ltx2_3_ic_lora.api.json`, 1280×704, 41 frames, 24 fps.

  | Seed | Output | Seconds | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S43/S43_moge_s1.mp4` | 36.9 | 32.0 GB | pending (R1) |
  | 2 | `takes/v/S43/S43_moge_s2.mp4` | 17.4 | 31.6 GB | pending (R1); used for the lip sync (a car passes behind him) |
- **Lip sync:** LatentSync 1.6 on V seed 2 (entry above), the brief's "pick the current best": the tool Folks Like Us settled on after LTX-2.3's audio-video model failed there. It runs outside ComfyUI, which the brief names; the reason is in `config/l.json`. Both seeds replace the V take's hanging-open mouth with the words' shapes; no seam at the paste.
- **Not in the test:** the brief's "face still flickering" glitch for S43, an effect pass after the lip sync is approved.

## 2026-11-01T08:59:44-05:00 — M5: keyframes (S43)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S43 --seeds 2001,2002,2003,2004`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S43_v3 | 2001 | 1.0 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S43/S43_v3_s2001.png` | 169.3 | pending (R1) |
| S43_v3 | 2002 | 1.0 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S43/S43_v3_s2002.png` | 157.2 | pending (R1) |
| S43_v3 | 2003 | 1.0 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S43/S43_v3_s2003.png` | 156.6 | pending (R1) |
| S43_v3 | 2004 | 1.0 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S43/S43_v3_s2004.png` | 157.2 | pending (R1) |

## 2026-11-01T09:11:53-05:00 — M5: lip sync with LatentSync 1.6 (S43 --seeds 2)

- **Model:** LatentSync 1.6 (`ByteDance/LatentSync-1.6` `latentsync_unet.pt`, code `bytedance/LatentSync` a229c39), 20 steps, guidance 2.5, DeepCache.
- **Inputs:** the V take (`config/l.json`), `audio/stems/0 Lead Vocals.wav`; a face crop of 2.6 face heights from `takes/l/<shot>/faces.json` (`scripts/l_faces.py`), 512 px, 24 fps frames labelled 25 fps with the vocal sped up 25/24. Pasted back through a feathered ellipse around the face. **Command:** `.venv/bin/python scripts/l_batch.py S43 --seeds 2`

| Shot | Seed | Frames | Synced | Input | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S43 | 2 | 39 | 41 | `takes/v/S43/S43_v3_moge_s2.mp4` | `takes/l/S43/S43_s2.mp4` | 22.5 | pending (R1) |

## 2026-11-01T09:40:00-05:00 — M5: S43 with the set's payphone (the human's note)
- **Keyframe v3** (`config/keyframes.json`; four seeds, auto-logged above): the set's payphone, a crop of S42's layout (`takes/stills/props/payphone_layout.png`), is reference image 3, placed at the frame's right edge as in the layout: a blue housing on a square post with a lit blank sign box. All four seeds have it; seed 2002 is closest to the layout and used.
- **V:** as the approved test (MoGe depth of the keyframe, pull-back 1.06 → 1.0, guide 0.6, `log/prompts/v/S43_moge.txt`): `takes/v/S43/S43_v3_control.mp4`, `S43_v3_first.png`.

  | Seed | Output | Seconds | Status |
  | --- | --- | --- | --- |
  | 1 | `takes/v/S43/S43_v3_moge_s1.mp4` | 45.8 | not used |
  | 2 | `takes/v/S43/S43_v3_moge_s2.mp4` | 20.0 | used (as the test) |
- **Lip sync:** seed 2 (approved) on V seed 2 (row above): `takes/l/S43/S43_s2.mp4`. The test's lip-sync outputs moved to `archive/takes/l/S43_keyframe_v2/`, superseded (their working frame folders not archived).
- **Review:** `renders/m5/review/S43_v3.mp4` (played three times with the master).

## 2026-11-01T09:26:08-05:00 — M5: keyframes (S43)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S43 --seeds 2001,2002,2003,2004`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S43_v4 | 2004 | 1.0 | renders/m5/plates/S43/beauty/04323.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S43/S43_v4_s2004.png` | 50.1 | pending (R1) |

## 2026-11-01T09:27:56-05:00 — M5: lip sync with LatentSync 1.6 (S43 --seeds 2)

- **Model:** LatentSync 1.6 (`ByteDance/LatentSync-1.6` `latentsync_unet.pt`, code `bytedance/LatentSync` a229c39), 20 steps, guidance 2.5, DeepCache.
- **Inputs:** the V take (`config/l.json`), `audio/stems/0 Lead Vocals.wav`; a face crop of 2.6 face heights from `takes/l/<shot>/faces.json` (`scripts/l_faces.py`), 512 px, 24 fps frames labelled 25 fps with the vocal sped up 25/24. Pasted back through a feathered ellipse around the face. **Command:** `.venv/bin/python scripts/l_batch.py S43 --seeds 2`

| Shot | Seed | Frames | Synced | Input | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S43 | 2 | 39 | 41 | `takes/v/S43/S43_v4_moge_s2.mp4` | `takes/l/S43/S43_s2.mp4` | 22.5 | pending (R1) |

## 2026-11-01T10:20:00-05:00 — M5: S43 v4, the Tenderloin (the human's note)
- **Why it read as Queens:** red brick walk-ups down a long flat street, under orange sodium light.
- **Keyframe v4** (`config/keyframes.json`): a "tenderloin" sentence for every street shot: six- and seven-story early-1900s apartment hotels in pale stucco and terracotta, ornate cornices, stacked bay windows, fire escapes on the fronts, vertical neon blade signs, scissor gates and roll-down shutters, a parking meter, Muni trolley-bus wires overhead and a steep hill in the distance. The style's light is now San Francisco's white LED streetlights. The set's brick corner wall stays beside him. Checked against the street photo in `reference/private/` (mood only; nothing from it used as an input).
  - **Seeds:** 2001–2004. The first run hit the tool's 10-minute limit after three seeds and was stopped before writing its log rows; the rerun made 2004 and logged only that one (row above). Seeds 2001–2003 were made with the same command and prompt (`log/prompts/keyframes/S43_v4.txt`).
  - **Pick:** seed 2002: an ornate cornice, the hill, trolley wires, the payphone at the right edge with the recorder on its post. The neon across the street is blurred and has no legible text.
- **V:** as approved, with "Tenderloin" and white LED light in the prompt (`log/prompts/v/S43_moge_v4.txt`), seed 2: `takes/v/S43/S43_v4_moge_s2.mp4` (35.7 s), control `S43_v4_control.mp4`.
- **Lip sync:** seed 2 on it: `takes/l/S43/S43_s2.mp4` (auto-logged row above). v3's outputs moved to `archive/takes/l/S43_keyframe_v3/`, superseded (working frames not archived).
- **Review:** `renders/m5/review/S43_v4.mp4`.

## 2026-11-01T10:40:00-05:00 — Log: S43 v4 approved (R1)
- S43 is done for the V and lip-sync passes: `takes/l/S43/S43_s2.mp4`. Still open for S43: the face flicker (brief: "face still flickering"), to be added with S42's glitch so the two match. Next: S42.

## 2026-11-01T11:47:06-05:00 — M5: keyframes (S42)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S42 --seeds 2001,2002,2003,2004`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S42 | 2001 | 1.0 | renders/m5/plates/S42/beauty/04261.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S42/S42_s2001.png` | 171.4 | pending (R1) |
| S42 | 2002 | 1.0 | renders/m5/plates/S42/beauty/04261.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S42/S42_s2002.png` | 158.2 | pending (R1) |
| S42 | 2003 | 1.0 | renders/m5/plates/S42/beauty/04261.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S42/S42_s2003.png` | 157.5 | pending (R1) |
| S42 | 2004 | 1.0 | renders/m5/plates/S42/beauty/04261.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S42/S42_s2004.png` | 158.2 | pending (R1) |

## 2026-11-01T11:59:44-05:00 — M5: lip sync with LatentSync 1.6 (S42 --seeds 2)

- **Model:** LatentSync 1.6 (`ByteDance/LatentSync-1.6` `latentsync_unet.pt`, code `bytedance/LatentSync` a229c39), 20 steps, guidance 2.5, DeepCache.
- **Inputs:** the V take (`config/l.json`), `audio/stems/0 Lead Vocals.wav`; a face crop of 2.6 face heights from `takes/l/<shot>/faces.json` (`scripts/l_faces.py`), 512 px, 24 fps frames labelled 25 fps with the vocal sped up 25/24. Pasted back through a feathered ellipse around the face. **Command:** `.venv/bin/python scripts/l_batch.py S42 --seeds 2`

| Shot | Seed | Frames | Synced | Input | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S42 | 2 | 62 | 64 | `takes/v/S42/S42_moge_s2.mp4` | `takes/l/S42/S42_s2.mp4` | 28.2 | pending (R1) |

## 2026-11-01T12:15:00-05:00 — M5: S42 (keyframe, V, lip sync) and the face glitch (S42, S43)
- **Keyframe** (`config/keyframes.json` S42; four seeds, auto-logged above): the S43 recipe (layout as reference only, denoise 1.0, sheet 1002, the payphone crop, the Tenderloin sentence), as a medium shot in steady rain. **Pick: seed 2003**, closest to the layout (brick corner and shutter on the left, him centred, the payphone with the recorder on its post, a newspaper box); cornices, bay windows, fire escapes, trolley wires. The neon blade sign across the street has nonsense letters; blurred and not a real name.
- **V:** as S43: MoGe depth of the keyframe with the shot's camera made by ffmpeg (S42's Blender camera is static, so a slow push-in, zoom 1.0 → 1.04 over 65 frames, the plan's clip), guide 0.6, `log/prompts/v/S42_moge.txt`. Control `takes/v/S42/S42_control.mp4`, first frame `S42_first.png`.
  - **Command:** `.venv/bin/python scripts/ltx_v.py takes/v/S42/S42_control.mp4 takes/v/S42/S42_first.png takes/v/S42/S42_moge_s<seed>.mp4 --prompt "$(cat log/prompts/v/S42_moge.txt)" --seed <seed> --control moge --guide 0.6`

  | Seed | Output | Seconds | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S42/S42_moge_s1.mp4` | 46.3 | 31.1 GB | not used |
  | 2 | `takes/v/S42/S42_moge_s2.mp4` | 31.1 | 31.2 GB | used (a car passes behind him, as in S43) |
- **Lip sync:** the approved seed 2 (auto-logged above): `takes/l/S42/S42_s2.mp4`.
- **Face glitch (new, `scripts/glitch_face.py`, `config/glitch.json`):** an effect pass inside the tracked face ellipse, driven by the lead vocal stem: rows tear sideways by the voice's samples, the colour channels split, and above strength 0.5 the face goes dark and becomes the vocal's waveform (a teal trace, 12 ms of the voice per frame). Timed to the words (`timing/words.json`): S42 flickers on "bot" and "bots," and turns into the waveform on "the bots to the feed"; S43 keeps flickering ("face still flickering") with a waveform flash on its first frame. Outputs `takes/fx/S42/S42_glitch.mp4`, `takes/fx/S43/S43_glitch.mp4`.
- **Config:** `config/v.json` style: white LED light instead of sodium (unused by the scripts so far; kept in step with the approved look).
- **Review:** `renders/m5/review/S42_S43_v1.mp4` (S42 into S43 with the master, three times).

## 2026-11-01T12:21:17-05:00 — M5: keyframes (S41)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S41 --seeds 2001,2002 --denoise 0.85`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S41_d85 | 2001 | 0.85 | renders/m5/plates/S41/beauty/04198.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S41/S41_d85_s2001.png` | 149.7 | pending (R1) |
| S41_d85 | 2002 | 0.85 | renders/m5/plates/S41/beauty/04198.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S41/S41_d85_s2002.png` | 135.3 | pending (R1) |

## 2026-11-01T12:26:02-05:00 — M5: keyframes (S41)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S41 --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S41_d92 | 2001 | 0.92 | renders/m5/plates/S41/beauty/04198.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S41/S41_d92_s2001.png` | 146.4 | pending (R1) |
| S41_d92 | 2002 | 0.92 | renders/m5/plates/S41/beauty/04198.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S41/S41_d92_s2002.png` | 146.6 | pending (R1) |

## 2026-11-01T12:31:11-05:00 — M5: keyframes (S41)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S41 --seeds 2001,2002 --denoise 0.96`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S41_d96 | 2001 | 0.96 | renders/m5/plates/S41/beauty/04198.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S41/S41_d96_s2001.png` | 152.2 | pending (R1) |
| S41_d96 | 2002 | 0.96 | renders/m5/plates/S41/beauty/04198.png, takes/stills/rapper/rapper_s1002.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S41/S41_d96_s2002.png` | 152.2 | pending (R1) |

## 2026-11-01T13:05:00-05:00 — M5: S41, the reveal (plates, keyframe, V, the patchy crossfade)
- **Plates:** all 63 frames of S41 (4198–4260), `blender -b --factory-startup --python scenes/blender/plates.py -- S41`, `renders/m5/plates/S41/`.
- **Keyframe** (`config/keyframes.json` S41; six rows auto-logged above): unlike S42–S43, S41 must keep the layout's geometry, since it dissolves from the Blender render. From the layout at denoise 0.85 (still CG; the rapper keeps the stand-in's head), 0.92 (the far street turns real, the corner stays CG) and 0.96. **Pick: 0.96, seed 2002** (`takes/keyframes/S41/S41_d96_s2002.png`): the pole, wall, payphone, van, crosswalk and one-way sign in place; apartment hotels with bay windows and fire escapes, a hill, rain. The eatery's sign band comes out blank (the style asks for blank signs).
- **V:** the Blender depth pass this time (63 frames, last held to the 65-frame clip: `takes/v/S41/S41_depth.mp4`), guide 0.8 so the man can move a little off the stand-in's shape, `log/prompts/v/S41_depth.txt`.
  - **Command:** `.venv/bin/python scripts/ltx_v.py takes/v/S41/S41_depth.mp4 takes/v/S41/S41_first.png takes/v/S41/S41_depth_s<seed>.mp4 --prompt "$(cat log/prompts/v/S41_depth.txt)" --seed <seed> --control depth --guide 0.8`

  | Seed | Output | Seconds | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S41/S41_depth_s1.mp4` | 36.5 | 31.1 GB | not used |
  | 2 | `takes/v/S41/S41_depth_s2.mp4` | 18.0 | 31.1 GB | used (cleaner around him) |
- **Reveal (new, `scripts/reveal.py`):** the brief's crossfade from the B render (the plates' beauty) to the V take, done in patches: each pixel turns at its own moment from a soft noise field plus the depth pass, so the far street goes real first and the corner nearest the camera last. 0.25 s to 2.0 s into the shot, smoothstep. **Command:** `.venv/bin/python scripts/reveal.py S41 takes/v/S41/S41_depth_s2.mp4` → `takes/fx/S41/S41_reveal.mp4`.
- **Review:** `renders/m5/review/S41_S43_v1.mp4` (S41 → S42 → S43 with the master, three times).
- **Open:** the "r/Philippines" sign on the eatery dissolves to a blank band, and S42–S43's corner has no sign either. If it should read in Act 2, it goes on as an overlay in the edit (signs are overlays, `config/v.json`).

## 2026-11-01T13:40:00-05:00 — M5: S41, the eatery sign back on (the human's note)
- **Sign matte (new, `scenes/blender/sign_matte.py`):** the sign's lettering alone (`shop0.sign`) from S41's camera, every other object a holdout so the pole still hides it, fog off (it put haze in the alpha; first try discarded, not an asset): `renders/m5/plates/S41/sign/`. **Command:** `blender -b --factory-startup --python scenes/blender/sign_matte.py -- S41`
- **Reveal:** `scripts/reveal.py` prints the lettering onto the V take's blank band as ink (darkens the band by 85% under the matte, blurred 0.6 px) before the dissolve, so the text carries through and takes the real light. Same command; `takes/fx/S41/S41_reveal.mp4`. The first reveal moved to `archive/takes/fx/S41_v1/`, superseded.
- S42–S43 frame the corner below the sign band, so they need no sign.
- **Review:** `renders/m5/review/S41_S43_v2.mp4`.

## 2026-11-01T12:58:33-05:00 — M5: keyframes (S44)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S44 --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S44_d90 | 2001 | 0.9 | renders/m5/plates/S44/beauty/04362.png | `takes/keyframes/S44/S44_d90_s2001.png` | 104.6 | pending (R1) |
| S44_d90 | 2002 | 0.9 | renders/m5/plates/S44/beauty/04362.png | `takes/keyframes/S44/S44_d90_s2002.png` | 73.1 | pending (R1) |

## 2026-11-01T13:01:31-05:00 — M5: keyframes (S44)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S44 --seeds 2001,2002 --denoise 0.96`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S44_d96 | 2001 | 0.96 | renders/m5/plates/S44/beauty/04362.png | `takes/keyframes/S44/S44_d96_s2001.png` | 79.1 | pending (R1) |
| S44_d96 | 2002 | 0.96 | renders/m5/plates/S44/beauty/04362.png | `takes/keyframes/S44/S44_d96_s2002.png` | 79.1 | pending (R1) |

## 2026-11-01T14:30:00-05:00 — M5: S44, the rooftop billboard's comment box
- **Plates:** all 112 frames of S44 (4362–4473), `renders/m5/plates/S44/`.
- **Screen (`overlays/screens.html` "billboard_reply", cue in `scripts/overlay_cues.py`):** a generic comment box (a white field holding "Reply below.", plain Cancel and Reply buttons, Inter), the cursor on for the first half of every beat (brief: "Cursor blinks in tempo"). Cues regenerated; Act 1's entries unchanged (checked). `node overlays/screens.mjs --only billboard_reply` → `renders/screens/billboard_reply/` (113 frames from 4362). Blender doesn't map it (scenes/blender/screens.py lists its own), so Act 1 is untouched.
- **Keyframe** (`config/keyframes.json` S44, no sheets; four rows auto-logged above): the tower's crown from below with a blank glowing billboard. Denoise 0.9 and 0.96, seeds 2001–2002. **Pick: 0.9, seed 2001**: the billboard and the tower's edge where the layout has them; the others drift or tilt.
- **V:** the Blender depth, guide 1.0, chained (the plan's 97 + 17: clip 1 starts from clip 0's last frame, one frame of overlap dropped), `log/prompts/v/S44_depth.txt`. Per-clip depth and first frames kept in `takes/v/S44/`.
  - **Command (per clip):** `.venv/bin/python scripts/ltx_v.py takes/v/S44/S44_c<k>_depth.mp4 <first> takes/v/S44/S44_s<seed>_c<k>.mp4 --prompt "$(cat log/prompts/v/S44_depth.txt)" --seed <seed> --control depth`

  | Seed | Output | Seconds (c0 + c1) | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S44/S44_s1.mp4` | 63.0 + 8.0 | 31.1 GB | used: clean across the join |
  | 2 | `takes/v/S44/S44_s2.mp4` | 28.1 + 7.0 | 31.3 GB | not used: the billboard's corners darken in clip 1 |
- **Pin (new, `scripts/billboard.py`):** finds the billboard's lit face in the take each frame (largest bright four-cornered region), smooths the corners over 5 frames, warps the screen onto it, multiplied by the take's light there so rain and falloff carry over. **Command:** `.venv/bin/python scripts/billboard.py S44 takes/v/S44/S44_s1.mp4` → `takes/fx/S44/S44_billboard.mp4`, `corners.json`.
- **Review:** `renders/m5/review/S43_S44_v1.mp4` (S43 into S44 with the master, three times).

## 2026-11-01T14:00:59-05:00 — M5: keyframes (S45)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S45 --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S45_d90 | 2001 | 0.9 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_d90_s2001.png` | 116.8 | pending (R1) |
| S45_d90 | 2002 | 0.9 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_d90_s2002.png` | 75.4 | pending (R1) |

## 2026-11-01T14:04:12-05:00 — M5: keyframes (S45)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S45 --seeds 2001,2002 --denoise 0.96`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S45_d96 | 2001 | 0.96 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_d96_s2001.png` | 79.4 | pending (R1) |
| S45_d96 | 2002 | 0.96 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_d96_s2002.png` | 80.1 | pending (R1) |

## 2026-11-01T14:07:07-05:00 — M5: keyframes (S45)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S45 --seeds 2001,2002,2003 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S45_v2_d92 | 2001 | 0.92 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_v2_d92_s2001.png` | 82.4 | pending (R1) |
| S45_v2_d92 | 2002 | 0.92 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_v2_d92_s2002.png` | 81.5 | pending (R1) |
| S45_v2_d92 | 2003 | 0.92 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_v2_d92_s2003.png` | 78.3 | pending (R1) |

## 2026-11-01T16:10:00-05:00 — M5: S45, the hype man in the doorway
- **Camera (`shots.py`):** S45's first plate showed a sidewalk fixture (`street.furniture`, found by ray cast) 0.85 m in front of the lens, over the doorway: S45 is Act 2, so its final-look layout was never reviewed at M4. The camera moves a metre east (x + 1.5 → x + 2.6), still aimed at the doorway; Act 1 is untouched. The stopped first render's layout is in `archive/renders/m5/plates_S45_v1/`, superseded.
- **Plates:** 89 frames (4474–4562). The first frame at 16 samples (the keyframe layout), the rest at 4 (`--samples 4`: V uses only their depth; 32 samples ran at ~50 s a frame with the doorway's backlight). The shutter slams down over him in the last three frames, as built at M3.
- **Keyframe** (`config/keyframes.json` S45; seven rows auto-logged above): v1 at 0.9 and 0.96 (seeds 2001–2002): one kept the stand-in's cartoon legs, one put a sports-team-style logo on his cap (rejected under the guardrails), the others lit his face (brief: "never fully seen"). v2 asks for a pitch-black front with a thin rim light and a plain cap, 0.92, seeds 2001–2003. **Pick: v2 seed 2001** (`takes/keyframes/S45/S45_v2_d92_s2001.png`): a solid silhouette with human proportions; 2002 and 2003 kept the stand-in's shape.
- **V:** the Blender depth at guide 0.7 (his shape stays human), 89 frames, `log/prompts/v/S45_depth.txt`.
  - **Command:** `.venv/bin/python scripts/ltx_v.py takes/v/S45/S45_depth.mp4 takes/v/S45/S45_first.png takes/v/S45/S45_s<seed>.mp4 --prompt "$(cat log/prompts/v/S45_depth.txt)" --seed <seed> --control depth --guide 0.7`

  | Seed | Output | Seconds | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S45/S45_s1.mp4` | 61.9 | 31.3 GB | used: the shutter slams in the last frames, as in Blender |
  | 2 | `takes/v/S45/S45_s2.mp4` | 30.0 | 31.0 GB | not used: the shutter starts early and hangs half down |
- **The STITCH NIGHT notice** (continuity, as the human asked for S41's sign): the take's notice came out garbled. `scenes/blender/sign_matte.py` gains `--materials` (keep faces of a material, by name prefix, showing their own texture; glass clear; all else holdout), since the notice is a quad in the interior's merged mesh: `blender -b --factory-startup --python scenes/blender/sign_matte.py -- S45 --materials int.atlas.shops` → `renders/m5/plates/S45/sign/`. New `scripts/sign_paste.py` replaces the take's notice with it, lit by the take's light there (blurred so the garbled letters don't show), and with `--shutter 650 1250` gives way to the take's own shutter as it comes down (its bottom edge found row by row; a first try by pixel difference let the notice ghost on the blue shutter). **Command:** `.venv/bin/python scripts/sign_paste.py S45 takes/v/S45/S45_s1.mp4 --shutter 650 1250` → `takes/fx/S45/S45_sign.mp4`.
- **Review:** `renders/m5/review/S44_S45_v1.mp4` (S44 into S45 with the master, three times).

## 2026-11-01T14:49:57-05:00 — M5: keyframes (S45)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S45 --seeds 2001,2002,2003 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S45_v3_d92 | 2001 | 0.92 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_v3_d92_s2001.png` | 113.8 | pending (R1) |
| S45_v3_d92 | 2002 | 0.92 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_v3_d92_s2002.png` | 76.2 | pending (R1) |
| S45_v3_d92 | 2003 | 0.92 | renders/m5/plates/S45/beauty/04474.png | `takes/keyframes/S45/S45_v3_d92_s2003.png` | 76.3 | pending (R1) |

## 2026-11-01T17:20:00-05:00 — M5: S45 v3, the hype man inside the shop (the human's note)
- **Why:** he stood 0.3 m behind the shopfront, on the same floor height as the sidewalk, so the photoreal take put his feet on the sidewalk and the shutter seemed to come down in front of a man outside it.
- **Set (`shots.py`):** he stands 1.2 m inside on the shop floor; his backlight moves back to match (FRONT − 3.4). Plates and the notice matte re-rendered (89 frames; first frame 16 samples, the rest 4). The previous layout is in `archive/renders/m5/plates_S45_v2/`, superseded.
- **Archived, superseded:** the v1–v2 keyframes, V takes and the notice pass, in `archive/takes/S45_hypeman_at_door/` (the V prompt they used stays as `log/prompts/v/S45_depth.txt`).
- **Keyframe v3** (`config/keyframes.json` S45; three rows auto-logged above): "a few steps inside the shop, on its floor and well behind the doorway's threshold … framed by the open doorway"; the threshold and the sidewalk between him and the camera. 0.92, seeds 2001–2003. **Pick: seed 2003**: a real man inside on the shop floor, the threshold in front of his feet; 2001 and 2002 kept the stand-in's shape.
- **V:** as before (depth, guide 0.7), prompt `log/prompts/v/S45_depth_v3.txt` (he stands inside behind the threshold; the shutter comes down across the shopfront, between him and the camera).

  | Seed | Output | Seconds | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S45/S45_v3_s1.mp4` | 51.6 | 31.1 GB | used: the shutter slams across the shopfront in the last four frames |
  | 2 | `takes/v/S45/S45_v3_s2.mp4` | 28.1 | 31.2 GB | not used: the shutter starts early |
- **Notice:** `scripts/sign_paste.py S45 takes/v/S45/S45_v3_s1.mp4 --shutter 450 1200` → `takes/fx/S45/S45_sign.mp4`. The shutter's edge detection now takes the first tall run of changed rows near the top (the trim above the shutter doesn't change; gaps of up to 8 rows bridged; under 60 rows is a flickering neon tube, not the shutter).
- **Review:** `renders/m5/review/S44_S45_v2.mp4`.

## 2026-11-01T15:01:31-05:00 — M5: keyframes (S47)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S47 --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S47_d90 | 2001 | 0.9 | renders/m5/plates/S47/beauty/04563.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S47/S47_d90_s2001.png` | 136.8 | pending (R1) |
| S47_d90 | 2002 | 0.9 | renders/m5/plates/S47/beauty/04563.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S47/S47_d90_s2002.png` | 115.4 | pending (R1) |

## 2026-11-01T15:05:56-05:00 — M5: keyframes (S47)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S47 --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S47_v2_d90 | 2001 | 0.9 | renders/m5/plates/S47/beauty/04563.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S47/S47_v2_d90_s2001.png` | 110.3 | pending (R1) |
| S47_v2_d90 | 2002 | 0.9 | renders/m5/plates/S47/beauty/04563.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S47/S47_v2_d90_s2002.png` | 102.2 | pending (R1) |

## 2026-11-01T15:09:29-05:00 — M5: keyframes (S47)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S47 --seeds 2001,2002 --denoise 0.95`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S47_v2_d95 | 2001 | 0.95 | renders/m5/plates/S47/beauty/04563.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S47/S47_v2_d95_s2001.png` | 128.1 | pending (R1) |
| S47_v2_d95 | 2002 | 0.95 | renders/m5/plates/S47/beauty/04563.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S47/S47_v2_d95_s2002.png` | 125.2 | pending (R1) |

## 2026-11-01T18:30:00-05:00 — M5: S47, the real payphone and its REC light
- **Plates:** 111 frames (4563–4673): the first at 16 samples (the keyframe layout), the rest at 4 (depth only). The REC LED's matte from the shot's camera: `blender -b --factory-startup --python scenes/blender/sign_matte.py -- S47 --objects recorder.rec` → `renders/m5/plates/S47/sign/`.
- **Keyframe** (`config/keyframes.json` S47, the payphone crop as reference 2; six rows auto-logged above): v1 asked for "piano-key buttons" and got a toy keyboard on the recorder; v2 describes a row of six chunky push buttons, the speaker grille and the open cassette door. 0.9 and 0.95, seeds 2001–2002. **Pick: v2 0.95 seed 2001** (`takes/keyframes/S47/S47_v2_d95_s2001.png`): the post, the duct-taped recorder with a cassette in its open door, the handset on its coiled cord, the van and the newspaper box where the layout has them.
- **V:** the Blender depth, guide 1.0, chained 97 + 17 like S44, `log/prompts/v/S47_depth.txt`.

  | Seed | Output | Seconds (c0 + c1) | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S47/S47_s1.mp4` | 52.1 + 7.0 | 31.3 GB | used |
  | 2 | `takes/v/S47/S47_s2.mp4` | 28.1 + 7.0 | 31.3 GB | not used (much the same; seed 1 a little cleaner) |
- **REC blink (new, `scripts/rec_blink.py`):** the take has a lit red LED a few pixels from the Blender one; it is found each frame (the reddest blob within 40 px of the matte's position), smoothed, and blinked on the Blender timing (on 0.25 s every 0.5 s from the shot's start): dimmed to a dark red lens when off, a bright lens with a soft red glow when on. **Command:** `.venv/bin/python scripts/rec_blink.py S47 takes/v/S47/S47_s1.mp4` → `takes/fx/S47/S47_rec.mp4`.
- **Review:** `renders/m5/review/S45_S47_v1.mp4` (S45 into S47 with the master, three times; S46 is retired).

## 2026-11-01T16:14:06-05:00 — M5: keyframes (S48)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48 --seeds 2001,2002 --denoise 0.95`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48_d95 | 2001 | 0.95 | renders/m5/plates/S48/beauty/04674.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S48/S48_d95_s2001.png` | 127.1 | pending (R1) |
| S48_d95 | 2002 | 0.95 | renders/m5/plates/S48/beauty/04674.png, takes/stills/props/payphone_layout.png | `takes/keyframes/S48/S48_d95_s2002.png` | 110.1 | pending (R1) |

## 2026-11-01T16:18:04-05:00 — M5: keyframes (S48_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48_end --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48_end_d92 | 2001 | 0.92 | renders/m5/plates/S48/beauty/04904.png | `takes/keyframes/S48_end/S48_end_d92_s2001.png` | 77.2 | pending (R1) |
| S48_end_d92 | 2002 | 0.92 | renders/m5/plates/S48/beauty/04904.png | `takes/keyframes/S48_end/S48_end_d92_s2002.png` | 76.1 | pending (R1) |

## 2026-11-01T16:25:14-05:00 — M5: keyframes (S48_mid)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48_mid --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48_mid_d92 | 2001 | 0.92 | renders/m5/plates/S48/beauty/04770.png | `takes/keyframes/S48_mid/S48_mid_d92_s2001.png` | 92.7 | pending (R1) |
| S48_mid_d92 | 2002 | 0.92 | renders/m5/plates/S48/beauty/04770.png | `takes/keyframes/S48_mid/S48_mid_d92_s2002.png` | 77.1 | pending (R1) |

## 2026-11-01T16:30:58-05:00 — M5: keyframes (S48_q)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48_q --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48_q_d92 | 2001 | 0.92 | renders/m5/plates/S48/beauty/04722.png | `takes/keyframes/S48_q/S48_q_d92_s2001.png` | 91.2 | pending (R1) |
| S48_q_d92 | 2002 | 0.92 | renders/m5/plates/S48/beauty/04722.png | `takes/keyframes/S48_q/S48_q_d92_s2002.png` | 76.3 | pending (R1) |

## 2026-11-01T21:30:00-05:00 — M5: S48, the crane over the block
- **Plates:** 231 frames (4674–4904): the first at 16 samples, the rest at 4. The first run was stopped by Claude Code at 119 frames (the machine ran low on memory, ComfyUI holding its models in RAM); after the human restarted the session with the reaper off, ComfyUI's models were freed (`POST /free`) and the render resumed from frame 120 (plates.py skips finished frames).
- **The whip:** between 0.55 and 0.8 of the shot the crane swings round almost 180° (frame 4850 is all motion blur) and settles on the pocket park. So the take is two parts cut inside the blur: **A**, frames 0–175, forward from a keyframe of the first frame; **B**, frames 176–230, generated backwards from a keyframe of the last frame (as Folks Like Us's v_batch "reverse"), so the park is designed, not invented from a blur.
- **Keyframes** (`config/keyframes.json`; rows auto-logged above). `scripts/keyframes.py` gains a per-entry `"frame"` (a plate frame other than the first). **S48** (the corner; payphone crop as reference 2), 0.95: **seed 2001**. **S48_end** (frame 4904, the park), 0.92: **seed 2001** (keeps the layout's marker grid, headstones, paths, fence and doghouse). **S48_mid** (frame 4770), 0.92: **seed 2001** (night, lit windows with a red light in each, the doormen; the Blender lettering survived too). **S48_q** (frame 4722), 0.92: **seed 2001** (dark robot doormen with gold ties).
- **V:** the Blender depth, guide 1.0. Part A chained 97 + 81 (clip 1 from clip 0's last frame), part B one 57-frame clip from the depth reversed (2 frames of hold), joined as A[0:176] + reversed B.
  - **v1** (anchor: the first frame only): the facades went to overcast daylight with unlit windows once the camera left the corner, and the doormen came out as white bin-shaped robots. Moved to `archive/takes/v/S48_no_mid_guide/`, superseded.
  - **`scripts/ltx_v.py` gains `--key IDX:IMAGE` and `--end IMAGE`:** keyframes for other frames of a clip, as more LTXVAddGuide nodes chained after the control's.
  - **v2** (+ S48_mid as clip 0's end): night from frame 96 on, but still dusky with white robots around frame 46. Moved to `archive/takes/v/S48_mid_guide_only/`, superseded.
  - **v3** (+ S48_q at frame 48): night throughout, dark doormen. Prompts `log/prompts/v/S48_a_depth_v3.txt` (part A) and `log/prompts/v/S48_b_depth.txt` (part B).
  - **Command (part A clip 0):** `.venv/bin/python scripts/ltx_v.py takes/v/S48/S48_a_c0_depth.mp4 takes/v/S48/S48_a_c0_first.png takes/v/S48/S48_v3_s<seed>_a_c0.mp4 --prompt "$(cat log/prompts/v/S48_a_depth_v3.txt)" --seed <seed> --control depth --key 48:takes/v/S48/S48_a_c0_key48.png --end takes/v/S48/S48_a_c0_end.png`; clip 1 and part B as before without keys.

  | Seed | Output | Seconds (A c0 + A c1 + B) | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S48/S48_v3_s1.mp4` | 44.2 + 24.1 + 16.0 | 31.3 GB | used |
  | 2 | `takes/v/S48/S48_v3_s2.mp4` | 31.1 + 23.0 + 16.0 | 31.2 GB | not used (much the same) |
- **Overlay (new, `scripts/overlay_add.py`):** the set's shop signs, READ-ONLY neon, keypad screens, window REC lights, the doormen's eye slits and the pawn clock, rendered alone in their own colours: `scenes/blender/sign_matte.py` gains `--own` (keep materials and the look), glob `--objects` and `--subdir`. `blender -b --factory-startup --python scenes/blender/sign_matte.py -- S48 --own --subdir overlay --objects 'shop*.rec[0-9]*' 'shop*.neon' 'shop*.keypad.txt' 'shop*.sign' 'shop*.unm' 'shop*.win*.sign' 'vip*.eye' 'screen.pawn_led.face'` → `renders/m5/plates/S48/overlay/`; laid over the take with a glow from its lights: `.venv/bin/python scripts/overlay_add.py S48 takes/v/S48/S48_v3_s1.mp4` → `takes/fx/S48/S48_overlay.mp4`.
- **Open:** the keypads' "Log in to continue" barely reads: each doorman stands in front of his keypad (as built at M3). For the human.
- **Review:** `renders/m5/review/S47_S48_v1.mp4` (S47 into S48 with the master, three times).

## 2026-11-01T17:55:00-05:00 — M5: keyframes (S48_q)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48_q --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48_q_v2_d92 | 2001 | 0.92 | renders/m5/plates/S48/beauty/04722.png, takes/keyframes/S48/S48_d95_s2001.png | `takes/keyframes/S48_q/S48_q_v2_d92_s2001.png` | 137.3 | pending (R1) |
| S48_q_v2_d92 | 2002 | 0.92 | renders/m5/plates/S48/beauty/04722.png, takes/keyframes/S48/S48_d95_s2001.png | `takes/keyframes/S48_q/S48_q_v2_d92_s2002.png` | 106.1 | pending (R1) |

## 2026-11-01T17:59:16-05:00 — M5: keyframes (S48_mid)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48_mid --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48_mid_v2_d92 | 2001 | 0.92 | renders/m5/plates/S48/beauty/04770.png, takes/keyframes/S48_q/S48_q_v2_d92_s2002.png | `takes/keyframes/S48_mid/S48_mid_v2_d92_s2001.png` | 108.2 | pending (R1) |
| S48_mid_v2_d92 | 2002 | 0.92 | renders/m5/plates/S48/beauty/04770.png, takes/keyframes/S48_q/S48_q_v2_d92_s2002.png | `takes/keyframes/S48_mid/S48_mid_v2_d92_s2002.png` | 106.2 | pending (R1) |

## 2026-11-01T18:03:03-05:00 — M5: keyframes (S48_k144)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48_k144 --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48_k144_d92 | 2001 | 0.92 | renders/m5/plates/S48/beauty/04818.png, takes/keyframes/S48_mid/S48_mid_v2_d92_s2001.png | `takes/keyframes/S48_k144/S48_k144_d92_s2001.png` | 108.1 | pending (R1) |
| S48_k144_d92 | 2002 | 0.92 | renders/m5/plates/S48/beauty/04818.png, takes/keyframes/S48_mid/S48_mid_v2_d92_s2001.png | `takes/keyframes/S48_k144/S48_k144_d92_s2002.png` | 106.2 | pending (R1) |

## 2026-11-01T18:06:38-05:00 — M5: keyframes (S48_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48_end --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48_end_v2_d92 | 2001 | 0.92 | renders/m5/plates/S48/beauty/04904.png, takes/keyframes/S48_mid/S48_mid_v2_d92_s2001.png | `takes/keyframes/S48_end/S48_end_v2_d92_s2001.png` | 107.4 | pending (R1) |
| S48_end_v2_d92 | 2002 | 0.92 | renders/m5/plates/S48/beauty/04904.png, takes/keyframes/S48_mid/S48_mid_v2_d92_s2001.png | `takes/keyframes/S48_end/S48_end_v2_d92_s2002.png` | 106.3 | pending (R1) |

## 2026-11-01T23:55:00-05:00 — M5: S48 v4 (the human's notes)
- **Keypads (`sets/block.py`):** moved from the doorway (where each doorman stood in front of his) onto the shutter beside the door (x + 0.75), larger (0.75 × 0.6 m), lettering 0.08 → 0.11 m at emission 5. Plates and the overlay pass re-rendered (231 frames, same settings). The previous first frame is in `archive/renders/m5/plates_S48_v1/`.
- **Tried, not used: video-to-video.** `scripts/ltx_v.py` gains `--init beauty.mp4 --denoise D` (the beauty pass VAE-encoded as the starting latent). On part A clip 0: at 0.6 and 0.75 the distilled model's schedule lost the init (grey daylight again); at 0.3 it follows the Blender render; at 0.45–0.5 with the anchors it keeps the night but looks CG and soft, and jumps from the photoreal opening keyframe within a dozen frames. Kept as an option; test takes in `archive/takes/v/S48_v3_keypads_in_door/test/`.
- **The fix: a chain of anchors, each referencing the one before** (`config/keyframes.json` refs `s48_k0/k48/k96`): frame 48 (S48_q v2, the corner as style reference: **seed 2002**; 2001 copied the reference and ignored the layout), frame 96 (S48_mid v2, referencing 48: **seed 2001**), **new frame 144** (S48_k144, looking down at the street just before the whip: "wet black asphalt at ground level with painted white lane lines and a double yellow center line", referencing 96: **seed 2002**), and the park (S48_end v2, referencing 96: **seed 2002**; 2001 scattered markers over the grass). Rows auto-logged above.
- **V v4:** part A clip 0 `--key 48:S48_a_key48.png --end S48_a_key96.png`, clip 1 (from clip 0's last frame) `--key 48:S48_a_key144.png`, part B reversed from the new park keyframe; prompts as v3. The road through the whip now reads as asphalt with its lane lines; the corner, block and park share one look.

  | Seed | Output | Seconds (A c0 + A c1 + B) | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S48/S48_v4_s1.mp4` | 66.6 + 29.1 + 16.0 | 31.3 GB | used |
  | 2 | `takes/v/S48/S48_v4_s2.mp4` | 31.2 + 25.1 + 16.1 | 31.3 GB | not used (near identical) |
- **Overlay:** `scripts/overlay_add.py` gains `--clean R`: the keyframes kept the Blender lettering a little off, so the take had its own copy and "r/Philippines" doubled; under the overlay's ink (dilated 5 px) the take is blurred out first. `.venv/bin/python scripts/overlay_add.py S48 takes/v/S48/S48_v4_s1.mp4 --clean 5` → `takes/fx/S48/S48_overlay.mp4`.
- **Archived, superseded:** the v3 takes, controls and anchors in `archive/takes/v/S48_v3_keypads_in_door/`, the v3 overlay in `archive/takes/fx/S48_v3/`.
- **Still open:** the early rise is soft from the speed of the move; the keypads read for about a second as the crane passes the corner.
- **Review:** `renders/m5/review/S47_S48_v2.mp4`.

## 2026-11-02T01:10:00-05:00 — M5: S48 v5 (the human's notes)
- **Login panels (`sets/block.py`):** the keypad is now a login panel, 1.0 × 0.62 m, reading "LOG IN TO / CONTINUE" in capitals at 0.16 m, emission 8. Only the overlay pass was re-rendered (it now includes the panels, `shop*.keypad`, so they have a clean dark backing over whatever the take drew): `blender -b --factory-startup --python scenes/blender/sign_matte.py -- S48 --own --subdir overlay --objects 'shop*.rec[0-9]*' 'shop*.neon' 'shop*.keypad' 'shop*.keypad.txt' 'shop*.sign' 'shop*.unm' 'shop*.win*.sign' 'vip*.eye' 'screen.pawn_led.face'`. The beauty and depth plates (and the V take made from them) have the previous 0.75 × 0.6 m panel; the depth difference is a 6 cm-deep box on a shutter, so they were not re-rendered.
- **The seam:** part B was regenerated longer, reversed from the park keyframe back to plate frame 4834 (73 frames: `takes/v/S48/S48_b5_depth_rev.mp4`, seed 1 → `S48_v5_s1_b_rev.mp4`, 36.4 s, peak VRAM 31.1 GB), so A (0–176) and B (160–230) overlap through the whip. Over the overlap B was 2.5× A's brightness (Lab L 131 vs 53). New `scripts/join_blend.py` grades B to A over the overlap (per-channel Lab mean and spread), crossfades it in with a smoothstep across frames 160–176, and eases the grade off over the next 24 frames: `.venv/bin/python scripts/join_blend.py takes/v/S48/S48_v5_s1_a.mp4 takes/v/S48/S48_v5_s1_b.mp4 --b-start 160 --length 231 --out takes/v/S48/S48_v5_s1.mp4`.
- **Overlay:** `.venv/bin/python scripts/overlay_add.py S48 takes/v/S48/S48_v5_s1.mp4 --clean 5` → `takes/fx/S48/S48_overlay.mp4`; the v4 overlay moved to `archive/takes/fx/S48_v4/`, superseded.
- **Review:** `renders/m5/review/S47_S48_v3.mp4`.

## 2026-11-01T18:36:06-05:00 — M5: keyframes (S48a)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48a --seeds 2001,2002 --denoise 0.85`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48a_d85 | 2001 | 0.85 | renders/m5/plates/S48a/beauty/04905.png | `takes/keyframes/S48a/S48a_d85_s2001.png` | 96.6 | pending (R1) |
| S48a_d85 | 2002 | 0.85 | renders/m5/plates/S48a/beauty/04905.png | `takes/keyframes/S48a/S48a_d85_s2002.png` | 71.1 | pending (R1) |

## 2026-11-01T18:38:54-05:00 — M5: keyframes (S48a)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S48a --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S48a_d92 | 2001 | 0.92 | renders/m5/plates/S48a/beauty/04905.png | `takes/keyframes/S48a/S48a_d92_s2001.png` | 76.3 | pending (R1) |
| S48a_d92 | 2002 | 0.92 | renders/m5/plates/S48a/beauty/04905.png | `takes/keyframes/S48a/S48a_d92_s2002.png` | 76.4 | pending (R1) |

## 2026-11-02T02:10:00-05:00 — M5: S48a, the open grave
- **Plate:** the first frame only (`plates.py S48a --first --samples 16`): the camera is locked off and nothing in the set moves, so that frame's depth serves for every frame (`takes/v/S48a/S48a_depth.mp4`, the frame held 97 frames). 235 frames, 186.38–196.16.
- **Keyframe** (`config/keyframes.json` S48a; four rows auto-logged above): 0.85 and 0.92, seeds 2001–2002; all four keep the inscription ("Logged-out Reddit / 2005 –") as carved. **Pick: 0.92 seed 2002** (`takes/keyframes/S48a/S48a_d92_s2002.png`): wet granite, the grave dark, a little street neon on the railing.
- **V:** three 97-frame clips from the same keyframe (seeds 1–3, the depth guide, `log/prompts/v/S48a_depth.txt`), joined with 24-frame dissolves (offsets 3.04 s and 6.08 s) and trimmed to 235 frames: `takes/v/S48a/S48a_joined.mp4`. Largest frame-to-frame change 1.1 grey levels (at the first dissolve): the joins don't show.
  - **Command:** `.venv/bin/python scripts/ltx_v.py takes/v/S48a/S48a_depth.mp4 takes/v/S48a/S48a_first.png takes/v/S48a/S48a_s<seed>.mp4 --prompt "$(cat log/prompts/v/S48a_depth.txt)" --seed <seed> --control depth`

  | Seed | Output | Seconds | Peak VRAM | Status |
  | --- | --- | --- | --- | --- |
  | 1 | `takes/v/S48a/S48a_s1.mp4` | 56.0 | 31.1 GB | used, frames 0–96 |
  | 2 | `takes/v/S48a/S48a_s2.mp4` | 27.4 | 30.9 GB | used, from frame 73 |
  | 3 | `takes/v/S48a/S48a_s3.mp4` | 25.1 | 31.0 GB | used, from frame 146 |
- **Review:** `renders/m5/review/S48_S48a_v1.mp4` (S48 into S48a with the master, twice).

## 2026-11-02T03:00:00-05:00 — M5: S40, S48b and the Act 2 cut (the M5 gate)
- **S48b (new screen, `overlays/screens.html` "login_prompt", cue in `scripts/overlay_cues.py`):** a generic login prompt, full frame: a white card on light grey with "Log in to continue", Username and Password fields, a plain Log in button and "Forgot your password?", Inter; black until 0.8 s into S48b, fading in by 1.6 s; the cursor blinks in the username field twice a second. No site's layout, colours, logo or fonts. Cues regenerated (the other entries unchanged, checked); `node overlays/screens.mjs --only login_prompt` → `renders/screens/login_prompt/` (97 frames). S48b runs 196.16–200.16 (`config/bookends.json` post-roll).
- **Act 2 cut (new, `scripts/act2_assemble.py`):** 2 s of S39e from the approved Act 1 frames (`renders/m4/act1_v8/frames`), then S40, the approved M5 takes S41–S48a (scaled to cover 1280×720), and S48b; the master to its end, S48b silent. **Command:** `.venv/bin/python -I scripts/act2_assemble.py renders/m5/act2_v1.mp4` → `renders/m5/act2_v1.mp4` (48.5 s).
  - **S40:** the M3 assembler's rewind (0.4 s hard freeze on S39e's last frame, then every Act 1 frame back to S02 in reverse), with the brief's "rewind scan lines" over the rewind: scan lines, a rolling tracking band of noise, the colour channels pulled apart, line jitter, crushed and desaturated. The freeze stays clean.
  - **S48b:** S48a's last frame fades to black over 0.8 s, then the login prompt.

## 2026-11-02T03:40:00-05:00 — M5: the tag on the scratches (the human's note)
- **The scratches:** the track ends with vinyl scratches, in the Other stem from 194.65 to 195.75 s (measured in 50 ms windows; drums and percussion hit there too), in S48a's last seconds; the piano plays out from 187 s before them.
- **Login prompt:** its cue (`scripts/overlay_cues.py`, "login_prompt") now starts at 194.65, drawn in full (no fade from black), with `"scratch": [194.65, 195.75]`; re-rendered (133 frames from timeline frame 5104). The other cues are unchanged (checked).
- **`scripts/act2_assemble.py`:** from the first scratch the grave fades straight into the prompt, its opacity following the Other stem's energy accumulated over the scratches, so it moves with each stroke; the prompt then holds, cursor blinking, to the cut at 200.16. No fade to black. → `renders/m5/act2_v2.mp4` (48.5 s). v1 moved to `archive/renders/m5/act2_v1.mp4`, superseded.

## 2026-11-02T03:50:00-05:00 — Log: M5 approved (R1); M6 starts
- Approved cut: `renders/m5/act2_v2.mp4`. Next, M6: the bookends (S01a–S01d, S49), the end card (S50) and the badge props.

## 2026-11-02T05:10:00-05:00 — M6: the bookend props and the opener's staging
- **Printed props (new, `scripts/gen_bookend_props.py`):** the visitor badge, its EXPIRED version (red stripes bled through, stamped) and the gold VIP version; the day schedule, folded in thirds → `assets/gen/props/`. From the human's real schedule and badge (`reference/private/`, read only for this) only the eight time slots with each meeting's kind and the badge's date and time (Mar 27, 2018 · 10:51 AM) are used; every name, title and the room are redaction bars; no company, logo or mascot. `.venv/bin/python -I scripts/gen_bookend_props.py`
- **The breakfast (`sets/props.py` `breakfast`):** modelled after the human's plate photo (`assets/real/plate.jpg`, the phone's photo in S01b): bangsilog on a paper plate (garlic rice of 700 grains with toasted garlic, two fried eggs with broken runny yolks, a butterflied fried milkfish with its backbone and tail), a white plastic fork and spoon, the black textured tray, a paper napkin and cup; the printed badge (VISITOR to S49, EXPIRED from S49) and schedule replace the grey-box boxes and lettering.
- **Fixes (`shots.py`):** S49's phone keys had replaced the opener's (`gb.keys` rewrites an F-curve), so the phone lay in its S49 pose through S01a–S01d; both sets of keys are now written together. The phone is hidden in S01b (the phone camera's own view). S01d's camera looks down the screen's normal from 0.42 m, so the phone fills about 70% of the frame.

## 2026-11-02T07:30:00-05:00 — M6: the phone's screens, the end card, the fact check
- **Phone screens (`overlays/screens.html`, cues in `scripts/overlay_cues.py`):** an invented third-party reader app, never named (a neutral list UI; no site's layout, colours, icons or fonts), an invented community ("SF Breakfast") and accounts. `phone_s01d`: the photo just taken (the human's plate photo, "Just now"), a swipe to the app, the thread "Best silog near the Tenderloin?" scrolling past a helper bot's reply ("LunchMapBot") to its "good bot"s. `phone_s49`: the thread's end on an empty reply box, under the notice "This app has shut down. It stopped working on June 30, 2023, when access to the API ended." `node overlays/screens.mjs --only phone_s01d,phone_s49` → `renders/screens/phone_s01d/` (124 frames), `phone_s49/` (193). Mapped onto the phone in `scenes/blender/screens.py` (two faces, the opener's until S49, S49's after; keyed directly, since `show_between` assumes t ≥ 0). S49's phone now lies on the table by the badge (it lay across the tray's edge).
- **Fact check:** a research subagent checked the brief's fact-card items against sources it opened; its report is in `log/audits/m6_end_card_fact_check.md`. Corrections taken: the $0.24 price was revealed May 31, 2023 by Apollo's developer (Reddit announced paid access in April); the blackout was 48 hours from June 12; the lawsuit's status is the September 2026 ruling (Judge Kahn let the contract and unfair-competition claims proceed); "primarily logged-in", not "logged-in only". It found no source for the Reference Guide's "Aug 2026: judge signals doubt" line. Reddit-hosted originals were unreachable for it.
- **End card (new, `overlays/cards.json`; `end_card` in `overlays/screens.html`):** four pages on black: "AI-generated satire" and the credits (the intervention count from `log/human_interventions.md`); "2023" (4 facts); "Since then" (6 facts), each with its source; the notes (the composite block, the tradition line, the conflict-of-interest line, the creator's disclosure). The COI line's reviewer is a placeholder until M8. `config/bookends.json`: S50 is now 42 s (8 + 10 + 12 + 12), from the M3 proposal's 10 s. `node overlays/screens.mjs --only end_card` → `renders/screens/end_card/` (1009 frames).
- **`scripts/bookends_assemble.py` (new):** the M6 review cut: the opener (S01a with its caption "San Francisco, 2018"; S01b's camera UI, toy thumb, flash and the photo; S01c; S01d) with the diner ambience, the match cut into S02 with the music, then S49 and S50.

## 2026-11-01T20:46:49-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_d90 | 2001 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_d90_s2001.png` | 111.0 | pending (R1) |
| S49_d90 | 2002 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_d90_s2002.png` | 73.3 | pending (R1) |

## 2026-11-01T20:49:55-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002 --denoise 0.95`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_d95 | 2001 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_d95_s2001.png` | 79.3 | pending (R1) |
| S49_d95 | 2002 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_d95_s2002.png` | 80.1 | pending (R1) |

## 2026-11-01T20:52:50-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002,2003 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_v2_d90 | 2001 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v2_d90_s2001.png` | 75.1 | pending (R1) |
| S49_v2_d90 | 2002 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v2_d90_s2002.png` | 74.1 | pending (R1) |
| S49_v2_d90 | 2003 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v2_d90_s2003.png` | 74.1 | pending (R1) |

## 2026-11-01T21:18:43-05:00 — M5: keyframes (S49_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_end --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_end_d90 | 2001 | 0.9 | renders/m5/plates/S49/beauty/05427.png, takes/keyframes/S49/S49_v2_d90_s2001.png | `takes/keyframes/S49_end/S49_end_d90_s2001.png` | 131.5 | pending (R1) |
| S49_end_d90 | 2002 | 0.9 | renders/m5/plates/S49/beauty/05427.png, takes/keyframes/S49/S49_v2_d90_s2001.png | `takes/keyframes/S49_end/S49_end_d90_s2002.png` | 102.1 | pending (R1) |

## 2026-11-01T21:25:23-05:00 — M5: keyframes (S49_mid)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_mid --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_mid_d90 | 2001 | 0.9 | renders/m5/plates/S49/beauty/05332.png, takes/keyframes/S49/S49_v2_d90_s2001.png | `takes/keyframes/S49_mid/S49_mid_d90_s2001.png` | 123.5 | pending (R1) |
| S49_mid_d90 | 2002 | 0.9 | renders/m5/plates/S49/beauty/05332.png, takes/keyframes/S49/S49_v2_d90_s2001.png | `takes/keyframes/S49_mid/S49_mid_d90_s2002.png` | 102.1 | pending (R1) |

## 2026-11-02T12:30:00-05:00 — M6: the opener, S49 and the bookends cut (the M6 gate)
- **Ambience (new, `audio/sfx/diner_ambience.wav`, 18.65 s):** LTX-2.3's own audio track: six 97-frame takes over the S01a push-in (`--control moge --guide 0.5`, prompt `log/prompts/v/diner_ambience.txt`: a busy little eatery's room sound, no music, no close speech) → `takes/sfx/amb_s<seed>.mp4`, their audio extracted. Checked for clear speech with faster-whisper large-v3 (CPU): seeds 1, 2, 3, 4, 6 produced only its stock phantom phrases (no-speech 0.5–0.83); seed 5 ("Hello!", no-speech 0.31) left out. The five, each loudness-normalised to −26 LUFS, joined with 0.35 s crossfades. Not listened to: the human's ear is the check.
- **Opener render:** `renders/m6/preroll_v1/` (436 frames, draft720, look final), S01a–S01d. Fixes found on the way: the phone's screen face showed Blender's missing-texture magenta before its sequence began (the `phone_s01d` cue now starts at S01a's start, dark until the photo is taken) and in S01b (hidden there with the phone); the VISITOR badge was hidden through the whole opener (`show_between` from −1e5 keys a hide before frame 0) and sat under the tray's edge — now keyed directly and moved clear, where S01c's drift ends. Superseded assemblies in `archive/renders/m6/`.
- **S01b overlay (`scripts/bookends_assemble.py`):** a generic camera UI (thirds grid, a drawn flash icon, a dot menu, the last-photo square, "Photo", the shutter button), the focus box settling on the plate, a toy thumb tapping the shutter, a white flash, then the human's plate photo in a plain viewer ("Just now"). S01a's caption "San Francisco, 2018".
- **S49 (B→V+JS):** `shots.py`: the camera now pushes in from the M3 framing to end close over the phone and the badge (the notice was 70 px wide, unreadable). Plates `renders/m5/plates/S49/` (192 frames). Keyframes (`config/keyframes.json`; rows auto-logged above): S49 v1 drew a whole fish with its head, so v2 asks for it butterflied: **v2 0.9 seed 2001**; anchors referencing it: **S49_mid seed 2002** (frame 5332) and **S49_end seed 2002** (frame 5427; seeds 2001 drifted to a wider view with the window). V: two 97-frame clips on the depth, clip 0 `--end` the mid anchor, clip 1 from clip 0's last frame `--end` the end anchor, prompt `log/prompts/v/S49_depth.txt`: **seed 1** `takes/v/S49/S49_v3_s1.mp4` (seed 2 much the same). Earlier takes (unanchored, exposure creeping up; one ending on the wrong anchor) in `archive/takes/S49_v1/`, `archive/takes/S49_v2_wrong_end/`.
  - **Overlay:** the phone's screen (`phone_s49`, its glow cut 2.0 → 0.35: at night it blew out to white) and the EXPIRED badge rendered in their own colours (`sign_matte.py -- S49 --own --subdir overlay --objects 'screen.phone_s49.face' 'eat.badge.exp'`), laid over with no bloom (`overlay_add.py` gains `--bloom`; at 0.8 the glow washed out the notice's text): `takes/fx/S49/S49_overlay.mp4`. The notice reads at the end of the push.
- **Bookends cut:** `.venv/bin/python -I scripts/bookends_assemble.py renders/m6/bookends_v1.mp4 --preroll renders/m6/preroll_v1 --s49 takes/fx/S49/S49_overlay.mp4 --s50 renders/screens/end_card` → `renders/m6/bookends_v1.mp4` (71.2 s: the opener with ambience to the match cut and 3 s of S02 with the music; S49; the end card).

## 2026-11-01T22:41:28-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_v3_d90 | 2001 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v3_d90_s2001.png` | 103.4 | pending (R1) |
| S49_v3_d90 | 2002 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v3_d90_s2002.png` | 73.1 | pending (R1) |

## 2026-11-01T22:44:35-05:00 — M5: keyframes (S49_mid)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_mid --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_mid_v2 | 2001 | 0.97 | renders/m5/plates/S49/beauty/05332.png, takes/keyframes/S49/S49_v3_d90_s2001.png | `takes/keyframes/S49_mid/S49_mid_v2_s2001.png` | 115.5 | pending (R1) |
| S49_mid_v2 | 2002 | 0.97 | renders/m5/plates/S49/beauty/05332.png, takes/keyframes/S49/S49_v3_d90_s2001.png | `takes/keyframes/S49_mid/S49_mid_v2_s2002.png` | 110.2 | pending (R1) |

## 2026-11-01T22:48:21-05:00 — M5: keyframes (S49_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_end --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_end_v2 | 2001 | 0.97 | renders/m5/plates/S49/beauty/05427.png, takes/keyframes/S49/S49_v3_d90_s2001.png | `takes/keyframes/S49_end/S49_end_v2_s2001.png` | 111.4 | pending (R1) |
| S49_end_v2 | 2002 | 0.97 | renders/m5/plates/S49/beauty/05427.png, takes/keyframes/S49/S49_v3_d90_s2001.png | `takes/keyframes/S49_end/S49_end_v2_s2002.png` | 110.3 | pending (R1) |

## 2026-11-01T22:52:28-05:00 — M5: keyframes (S49_mid)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_mid --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_mid_v3 | 2001 | 0.95 | renders/m5/plates/S49/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v3_s2001.png` | 80.1 | pending (R1) |
| S49_mid_v3 | 2002 | 0.95 | renders/m5/plates/S49/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v3_s2002.png` | 79.2 | pending (R1) |

## 2026-11-01T22:55:08-05:00 — M5: keyframes (S49_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_end --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_end_v3 | 2001 | 0.95 | renders/m5/plates/S49/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v3_s2001.png` | 80.2 | pending (R1) |
| S49_end_v3 | 2002 | 0.95 | renders/m5/plates/S49/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v3_s2002.png` | 79.2 | pending (R1) |

## 2026-11-01T22:58:05-05:00 — M5: keyframes (S49_mid)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_mid --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_mid_v4 | 2001 | 0.95 | renders/m5/plates/S49/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v4_s2001.png` | 80.1 | pending (R1) |
| S49_mid_v4 | 2002 | 0.95 | renders/m5/plates/S49/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v4_s2002.png` | 79.2 | pending (R1) |

## 2026-11-01T23:00:45-05:00 — M5: keyframes (S49_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_end --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_end_v4 | 2001 | 0.95 | renders/m5/plates/S49/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v4_s2001.png` | 80.2 | pending (R1) |
| S49_end_v4 | 2002 | 0.95 | renders/m5/plates/S49/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v4_s2002.png` | 79.2 | pending (R1) |

## 2026-11-01T23:05:22-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002,2003`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_v4 | 2001 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v4_s2001.png` | 105.5 | pending (R1) |
| S49_v4 | 2002 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v4_s2002.png` | 79.2 | pending (R1) |
| S49_v4 | 2003 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v4_s2003.png` | 79.3 | pending (R1) |

## 2026-11-02T17:00:00-05:00 — M6: bookends v2 (the human's notes)
- **Ambience:** the distilled model's audio was "synthetic or garbled". `scripts/ltx_v.py` gains `--dev` (the full LTX-2.3 model, `ltx-2.3-22b-dev-fp8`, 30 steps, cfg 3.5, euler/simple): three clips, seeds 1–3 (`takes/sfx/amb_dev_s<seed>.mp4`, ~190 s each), sent as an A/B with the old one. The human picked seed 2. It is 4.0 s, so `audio/sfx/diner_ambience.wav` is now that clip loudness-normalised (−26 LUFS) and looped six times with 1 s crossfades (19.06 s). The distilled bed moved to `archive/audio/sfx/diner_ambience_distilled_v1.wav`, superseded.
- **The schedule:** the saucer on it "is not reading correctly": it is gone (hidden), and the schedule is a three-panel page (folded in thirds and opened out, its creases riding up a few millimetres), one corner tucked under the tray. S01b–S01d re-rendered (`renders/m6/preroll_v1/`, frames 120–435) and S49's plates.
- **S49 "too CG":** the anchors at 0.9 from the Blender frames stayed CG. v3–v4: the close-up anchors at 0.95 with no style reference (with S49's opening keyframe as reference they copied its whole composition), the prompt saying "indoors … the eatery's yellow-painted wall … no window, no street" (without it they put the table outdoors) and "real worn wooden table, real paper, real plastic"; the opening keyframe the same way at 0.95 so all three agree. **Picks:** `S49_v4_s2002` (opening; every seed added a stray sheet at the table's front edge, which leaves frame in the push), `S49_mid_v4_s2002`, `S49_end_v4_s2002`. V v5 seed 1 (`takes/v/S49/S49_v5_s1.mp4`), prompt `log/prompts/v/S49_depth_v4.txt`. The EXPIRED badge is now pasted lit by the take (`sign_matte.py --materials prop.img.badge_expired` → `sign_paste.py S49 … --blur 10`), the phone screen over it (`overlay_add.py --bloom 0`) → `takes/fx/S49/S49_overlay.mp4`. Superseded takes in `archive/takes/S49_v3_saucer/`, `archive/takes/S49_v4_mismatched_open/`.
- **Cut:** `renders/m6/bookends_v2.mp4`; v1 moved to `archive/renders/m6/`.

## 2026-11-02T06:08:45-05:00 — M5: keyframes (S49_mid, S49_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_mid S49_end --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_mid_v5 | 2001 | 0.6 | renders/m6/s49_reproj/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v5_s2001.png` | 86.2 | pending (R1) |
| S49_mid_v5 | 2002 | 0.6 | renders/m6/s49_reproj/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v5_s2002.png` | 60.3 | pending (R1) |
| S49_end_v5 | 2001 | 0.6 | renders/m6/s49_reproj/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v5_s2001.png` | 61.1 | pending (R1) |
| S49_end_v5 | 2002 | 0.6 | renders/m6/s49_reproj/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v5_s2002.png` | 58.1 | pending (R1) |

## 2026-11-02T06:13:26-05:00 — M5: keyframes (S49_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_end --seeds 2001,2002 --denoise 0.75`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_end_v5_d75 | 2001 | 0.75 | renders/m6/s49_reproj/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v5_d75_s2001.png` | 73.1 | pending (R1) |
| S49_end_v5_d75 | 2002 | 0.75 | renders/m6/s49_reproj/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v5_d75_s2002.png` | 73.2 | pending (R1) |

## 2026-11-02T06:16:00-05:00 — M5: keyframes (S49_end)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_end --seeds 2001,2002 --denoise 0.88`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_end_v5_d88 | 2001 | 0.88 | renders/m6/s49_reproj/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v5_d88_s2001.png` | 88.1 | pending (R1) |
| S49_end_v5_d88 | 2002 | 0.88 | renders/m6/s49_reproj/beauty/05427.png | `takes/keyframes/S49_end/S49_end_v5_d88_s2002.png` | 98.1 | pending (R1) |

## 2026-11-02T20:30:00-05:00 — M6: bookends v3 (the human's notes on v2)
- **"The intro is a little washed out":** the pre-roll's daylight was a flat blue sky fill at strength 1.0 with a sun of 4.0, the night haze volume stayed on by day (lit by the sun it lifted every black), and the shop glass (`glass_a`, alpha 0.18) laid a pale sheet over S01a's push through the eatery window. `scenes/blender/shots.py`: by day (before the song) the haze density is keyed to 0, the sky fill to 0.4 and the sun to 5.5 (`DAY_SKY`, `DAY_SUN`), and the glass alpha to 0.06 (`DAY_GLASS`); from the song on everything is as approved. Opener stills: the 5th-percentile luminance went from ~60 to ~40 (Act 1 sits at 13–28); the colour came back. Re-rendered: `renders/m6/preroll_v3/` (436 frames; `preroll_v2` was the same without the glass change).
- **S49 "wall appears to travel":** the three FLUX anchors (opening, middle, end) were each painted at 0.95 from the Blender frames, and each put the eatery's wall corner and a window in a different place, so the take morphed between them. New `scenes/blender/cams.py` dumps the shot's camera per frame and its planar depth (`renders/m5/plates/S49/cams.json`, `depth_z/`); new `scripts/reproject.py` carries an image from one frame into another's camera through that depth (checked on the plates: frame 5236's beauty reprojected onto 5427 lines up with 5427's own). The opening anchor `S49_v4_s2002` reprojected to frame 5332 (holes 0.7%, Telea-filled) → `renders/m6/s49_reproj/`, then FLUX at 0.6 only re-details it (`config/keyframes.json` S49_mid v5, layout `renders/m6/s49_reproj`): pick `S49_mid_v5_s2001` (2002 put a dark patch on the screen). The end frame (5427) reprojected has the tray rim doubled (the anchor painted the tray a few cm larger than the set's) — at 0.6/0.75 it stays doubled and soft, at 0.88 it invents keychains — so S49 v6 has no end anchor: clip 0 from the opening anchor to the middle anchor, clip 1 chained from clip 0's last frame on the depth guide alone. `takes/v/S49/S49_v6_s{1,2}.mp4`; **pick seed 1** (seed 2's second half goes grey). The wall corner and window now stay put through the push. v5 and its anchors → `archive/takes/S49_v5_travelling_wall/`; the end-anchor attempts (`takes/keyframes/S49_end/S49_end_v5*`) are unused.
- **"EXPIRED" hard to read:** the badge texture v2 (`scripts/gen_bookend_props.py`): a full-width white band across the badge with "EXPIRED" in heavy red capitals filling it; v1 → `archive/assets/gen/props/badge_expired_v1.png`. Matte re-rendered (`sign_matte.py -- S49 --materials prop.img.badge_expired`), pasted on v6 (`sign_paste.py S49 takes/v/S49/S49_v6_s1.mp4 --blur 10`).
- **Phone screen's white border:** the take's own lit screen is a little larger than the rendered one, and its edge showed round the overlay. `scripts/overlay_add.py` gains `--bezel R`: a ring R px round the overlay is painted the phone's black glass before the screen goes on. `overlay_add.py S49 takes/fx/S49/S49_sign.mp4 --bloom 0 --bezel 6` → `takes/fx/S49/S49_overlay.mp4`. The v5 fx → `archive/takes/S49_v5_fx/`.

## 2026-11-02T07:17:36-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002,2003,2004`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_v5 | 2001 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v5_s2001.png` | 109.2 | pending (R1) |
| S49_v5 | 2002 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v5_s2002.png` | 102.2 | pending (R1) |
| S49_v5 | 2003 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v5_s2003.png` | 104.1 | pending (R1) |
| S49_v5 | 2004 | 0.95 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v5_s2004.png` | 108.1 | pending (R1) |

## 2026-11-02T07:25:04-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_v5_d90 | 2001 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v5_d90_s2001.png` | 97.1 | pending (R1) |
| S49_v5_d90 | 2002 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v5_d90_s2002.png` | 92.1 | pending (R1) |

## 2026-11-02T07:28:14-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002 --denoise 0.92`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_v5_d92 | 2001 | 0.92 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v5_d92_s2001.png` | 91.4 | pending (R1) |
| S49_v5_d92 | 2002 | 0.92 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v5_d92_s2002.png` | 91.3 | pending (R1) |

## 2026-11-02T07:31:43-05:00 — M5: keyframes (S49_mid)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_mid --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_mid_v6 | 2001 | 0.6 | renders/m6/s49_reproj_v2/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v6_s2001.png` | 63.1 | pending (R1) |
| S49_mid_v6 | 2002 | 0.6 | renders/m6/s49_reproj_v2/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v6_s2002.png` | 60.1 | pending (R1) |

## 2026-11-02T23:30:00-05:00 — M6: bookends v4 (the human's notes on v3)
- **The fish clipping into the plate:** the fillets were one rigid flat shape tilted over a dished plate, a rice mound and an egg. `props.drape()` lays a flat object onto what's under it the way the receipt tape is laid (in place of a cloth simulation): the surface under its footprint sampled on a 2 mm grid (rays onto the plate, the rice and eggs, the plasticware), stiffened by a cone dilation (it can't bend sharper than a 0.25 rise per run, and it's only ever smoothed upward, so it never goes into what it lies on), each vertex set on that surface at its own height above the fish's underside. The fish is also 15% smaller and 1.2 cm further back, and the spoon moved to the front of the rice, so it crowds the plate less; its flesh sits 4 mm over the skin (at 2.5 mm the bends let the skin show through). (A mis-placed comment briefly turned the flesh into a 1 m sphere in a test still; caught and fixed before any render.)
- **"All of the chairs appear to be facing the wrong way":** the eatery's side chairs (`interiors.eatery`) were turned +90°, which faced the chair's front (-Y) away from its table; now -90°. The end chair (180°) was right. This changes the eatery interior in Act 1 too (its approved frames were rendered before the fix); the final render picks it up.
- **The opener render:** `renders/m6/preroll_v5/` (436 frames, draft720); `preroll_v3`/`v4` were the same without these fixes.
- **S49 "the table and the road warp together":** the opening anchor `S49_v4_s2002` painted the back half of the table as the wet street (the Blender table runs back to the window sill), so in the take the street was on the table's plane and moved with it. New opening anchor: the prompt pins the table ("its whole top is dry, dark worn wood all the way back to the window sill … the street is only ever seen through the glass, never on the table"; and one page only, nothing at the table's front edge). At 0.95 the composition drifted from the layout (seeds 2001–2004); at 0.92 the window spilled over the table; at 0.9 seed 2002 follows the set's outline: **pick `S49_v5_d90_s2002`**. Reprojected to frame 5332 (`renders/m6/s49_reproj_v2/`) → `S49_mid_v6_s2001` (FLUX 0.6). V v7 (clip 0 first → middle anchor, clip 1 on the depth alone): seeds 1–2, **pick seed 1** (seed 2 greys in its second half) → `takes/v/S49/S49_v7_s1.mp4`. v6 and its anchors → `archive/takes/S49_v6_road_on_table/`, its fx → `archive/takes/S49_v6_fx/`.
- **S49 phone:** in v7 the take's screen glows past the phone: `overlay_add.py` gains `--halo R` (past the bezel, out to R px, each pixel kept no brighter than the table round about, the take blurred with the phone region left out). `sign_paste.py S49 takes/v/S49/S49_v7_s1.mp4 --blur 10` → `overlay_add.py S49 takes/fx/S49/S49_sign.mp4 --bloom 0 --bezel 9 --halo 30` → `takes/fx/S49/S49_overlay.mp4` (the first v7 overlay, bezel 6 and no halo, → `archive/takes/S49_v7_fx_halo/`).
- **The foley repeating; "use seed 3 and mix them together":** new `scripts/ambience_bed.py`: two layers, each a chain of 1.5–2.6 s pieces from random places in `takes/sfx/amb_dev_s2.wav` and `amb_dev_s3.wav` (level-matched; never the same clip and place twice running), 0.5 s equal-power crossfades, the second layer offset 1 s; summed at −3 dB each, loudness-normalised to −26 LUFS → `audio/sfx/diner_ambience.wav` (19.5 s). Its envelope's autocorrelation is ≤ 0.09 at every lag from 2 to 8 s (no period). The seed-2 loop → `archive/audio/sfx/diner_ambience_s2_loop_v2.wav`.

## 2026-11-03T01:00:00-05:00 — M6: bookends v5 (the human's note on v4)
- **The SF Breakfast screen (S01d):** its header was crisp but the thread's text came out faint and doubled: the scroll ran steadily for 2.5 s, so every frame was mid-motion and the render's motion blur averaged several scroll positions into grey. `overlays/screens.html` `phone_s01d`: the scroll is now two flicks (0.3 s each, ease-out; 55% then 45% of the 420 px) with a 0.95 s reading pause after the first and a hold after the second; re-rendered `renders/screens/phone_s01d/` (a frame sequence, regenerated). `scenes/blender/screens.py`, both phone faces: anti-glare glass (specular 0.08, roughness 0.45; tested: not the cause, kept as a phone's glass) and a gamma of 1.6 on the screen texture, since its thin strokes shrunk to ~40% averaged to mid-grey (white stays white). The S49 overlay frames already rendered are unchanged.
- **The opener overall:** `scripts/bookends_assemble.py` grades the opener's render frames (not the real photo or the camera UI): black point down 6%, a gentle S round the middle, saturation +8%. The 5th-percentile luminance goes from ~45 to ~25 (Act 1: 13–28); highlights unchanged.
- **Opener render:** `renders/m6/preroll_v6/` (`preroll_v5` was the same before the screen changes).

## 2026-11-03T03:00:00-05:00 — M6: bookends v6 (S49 foley, the end card's instrumental)
- **Chairs (the human's question):** yes: the fix is in `interiors.eatery`, which every render builds; Act 1's approved frames (`renders/m4/act1_v8`) predate it, and the M7 render and the final render pick it up.
- **S49's foley:** LTX-2.3's own audio from the full model (`--dev`) over S49's depth and opening keyframe, prompt `log/prompts/v/s49_foley.txt` (the empty eatery after closing: rain on the street, the window and the shutter, the fridge hum, a neon sign's buzz, a distant car; no people, speech or music): seeds 1–3 → `takes/sfx/s49_dev_s<seed>.{mp4,wav}` (4.0 s each; faster-whisper large-v3 hears only its stock phantom phrases, no-speech 0.68–0.75). `scripts/ambience_bed.py` (gains `--sources`) mixes all three into `audio/sfx/s49_room.wav` (9.5 s, −26 LUFS). Not listened to: sent to the human as an A/B with the bed.
- **The end card's instrumental:** new `scripts/cards_audio.py` (after Not Yet's): Drums, Bass, Guitar, Keyboard, Percussion, Strings, Synth from Verse 4's first downbeat (154.68 s) to the stems' end (196.16 s) = 41.48 s, the end card's 42 s less half a second; muted: both vocal stems (an instrumental) and Other (the record scratches, already S48b's cue). 4 s pre-roll for the model, trimmed. Limiter at −1 dBFS (the stem sum peaks at +0.5 dBFS; 0.18 s of gain reduction in all). **Post-filter:** music-deslop M6f 10k at 68441e2, `--source suno` with the release chain's defaults (the master's chain: with the fallback). → `audio/post/cards_audio.wav` (24-bit 48 kHz, −16.3 LUFS, peak −0.95 dBFS); `timing/cards_audio.json`. faster-whisper: no vocal bleed (one stock phantom phrase in the last window, no-speech 0.7).
- **Assembly:** `scripts/bookends_assemble.py`: under S49 its room sound (1 s fade-in, out over the end card's first second), under S50 the instrumental at −4 dB (about −20 LUFS, for reading) from the card's first frame. `renders/m6/bookends_v6.mp4`. Levels along it (0.5 s RMS): opener ambience ≈ −30 dB, S49 ≈ −30 dB, the instrumental −20 dB from 29.2 s, the piano tail −31 dB at the end.

## 2026-11-03T04:00:00-05:00 — M6: bookends v7 (S49: tape hiss and crackle)
- **Rejected:** the generated room sound ("far too noisy"): `takes/sfx/s49_dev_s{1,2,3}` → `archive/takes/sfx_s49_room/`, the bed → `archive/audio/sfx/s49_room_rejected.wav`.
- **New `scripts/tape_hiss.py`** (synthesised, seeded): cassette hiss (white noise, 70% correlated L/R, a high shelf from ~2 kHz, 150 Hz–12 kHz), breathing with wow (0.55 Hz) and flutter (6.5 Hz) ±0.6 dB; 60 Hz hum with its 3rd and 5th harmonics 30 dB under; crackle: Poisson clicks (~5/s, 0.2–1.5 ms bursts band-passed 1–7 kHz, log-normal sizes) and a duller pop about every 2 s; a 0.25 s fade-in; −30 LUFS. `audio/sfx/s49_tape.wav` (9.5 s, seed 49; band energy peaks at 4–12 kHz, peak −22 dBFS). The assembler (`S49_FOLEY`) puts it under S49 as before (1 s in, out under the card's first second).
- **Cut:** `renders/m6/bookends_v7.mp4` (v6 → `archive/renders/m6/`).

## 2026-11-03T05:00:00-05:00 — M6: the tape hiss from S47 (bookends v8, Act 2 v3, the ending review cut)
- **The bed:** `scripts/tape_hiss.py` gains `--ease T:dB,...` (a gain envelope, linear in dB, applied after the loudness normalisation, so 0 dB is −30 LUFS). `audio/sfx/tape_bed_s47_s49.wav` (37.04 s, seed 49) starts at S47 (172.12 s: the payphone, the recorder taped beside it, its cassette in view): `--ease "0:-60,1.5:-18,28.04:-8,29.04:0,37.04:0"`: in over 1.5 s to −18 dB under "This call was recorded", rising in dB through S48, S48a's silence and S48b's login screen to −8 dB, then up to full over S49's first second (the cut back to the eatery). The 9.5 s `s49_tape.wav` → `archive/audio/sfx/s49_tape_v1.wav`.
- **Assemblers:** `scripts/act2_assemble.py` mixes the bed from S47 under the master → `renders/m5/act2_v3.mp4` (the approved `act2_v2` stays; it differs only by the bed). `scripts/bookends_assemble.py` takes the same file from S49's offset (28.04 s; no fade-in, it is already up) → `renders/m6/bookends_v8.mp4`.
- **Review cut:** `renders/m6/ending_v1.mp4` (80.1 s): `act2_v3` from 2 s before S47 to its end, then the bookends' closing (S49, S50) (`ffmpeg -ss 18.44` + concat). The hiss band (> 6 kHz, 0.5 s RMS) along it: about −48 dB through the silence and the login screen, −46 dB at S48b's end, −36 dB from the eatery.

## 2026-11-02T11:40:00-05:00 — M6 gate passed; M7 starts (captions, full-edit assembler, vertical cut, thumbnail options)
- **M6:** approved by the human (human interventions, same date): `renders/m6/bookends_v8.mp4`, `renders/m5/act2_v3.mp4`, `renders/m6/ending_v1.mp4`.
- **Housekeeping:** four stale background waiters from M6 (their `pgrep -f` pattern matched their own command line, so they never ended) killed; nothing else was running.
- **Act 1 re-render (the chairs, M6 note):** `blender -b --factory-startup --python scenes/blender/animatic.py -- --out renders/m7/act1/frames --profile draft720 --look final --from 0.14 --to 153.68 --resume` (log `renders/m7/act1/render.log`), running; the whole act, so the edit has one consistent Act 1 with the eatery's chairs turned. To be diffed against the approved `renders/m4/act1_v8/frames` when done.
- **Caption face:** VT323 (Peter Hull, The VT323 Project Authors; SIL OFL 1.1), from `google/fonts` `ofl/vt323` into an isolated scratch folder; vendored as `assets/fonts/VT323-Regular.ttf` with `VT323-OFL.txt`, added to `SHA256SUMS`. A bitmap DEC VT320 terminal face: the nearest openly licensed match to a period caption decoder's lettering. It covers the captions' characters except the music note.
- **New `scripts/captions.py`** (the human: "a VHS/old-school closed caption font"): CEA-608 ("line 21") captions as a late-'90s VCR taped them:
  - roll-up, two rows (RU2), a 32-column grid, left-aligned; each word paints on at its `start_frame` in `timing/timing_map.json` (so every word is on its sung frame: the acceptance's "within two frames"); each sung line starts a row, long lines wrap balanced (the fewest rows, the longest as short as possible: no orphan words); a new row rolls the others up over 0.125 s; a run is erased 2 s after its last word or when the next starts;
  - 608's conventions: `>>` at a change of speaker, a music note at the start of each sung line, `♪♪` over the opening piano, capitals; sound tags: [INDISTINCT CHATTER] (S01a, lower right, clear of the location caption and the eatery's sign), [TAPE HISSES] (S48a's silence), [RECORD SCRATCH] (into the login prompt);
  - VT323 stretched 1.5× wide to the 608 cell (0.6 of the row), white on black boxes (alpha 0.92) with a cell before and after the text, rows stacked without gaps; the music note drawn as a bitmap on VT323's pixel grid (608 has it as a special character; VT323 has none); the layer softened across and its red and blue pulled a pixel apart (tape);
  - `srt`: one cue per sung line (the timing map's text, from its first word's frame to the next line or 1 s after its last word) plus the tags.
- **New `scripts/assemble.py`** (M7's full edit, after Not Yet's): every frame from its source in one pass (no re-encode of the M4–M6 cuts): the opener render graded with S01a's caption and S01b's camera (`bookends_assemble.opener_frame`, factored out), Act 1's frames with their overlays (`renders/overlays/act1`), Act 2 (`act2_assemble.Act2`, factored out; both scripts' CLIs unchanged, `act2_assemble.py` gains `--act1`), S49's take (now scaled to cover, as Act 2's takes: the M6 cut had stretched 1280×704 to 720 high), the end card; captions over everything but the end card. Sound on one timeline: the ambience under the opener, the master from video 18 s, the tape bed from S47 (out over the card's first 1.2 s), the card's instrumental at −4 dB from S50. Review encode x264 CRF 16. Tested on two sections (0–30 s; 186–222 s) over the v8 frames: captions on time, the tags placed.
  - `--vertical`: the vertical cut, 1080×1920, `config/reframe.json` (new): a 9:16 window per shot, keyed from contact sheets of each shot's start, middle and end; S36 "fit" (its epitaph is wider than any 9:16 window: the whole frame across the width over a blurred, darkened fill); captions re-set to 22 columns and higher (clear of a phone app's controls); the master over the span, in over 0.4 s, picture and music out over the last 2 s. It runs S34–S45 as the brief's range says (48.1 s); S44's "Reply below" line runs into S45's "…allegedly", so the cut ends after it rather than cutting mid-line. A test over the v8 frames: S39b's window fell between two stones; re-keyed to follow the names.
- **New `scripts/thumbnail.py`:** three options for the human (R1), the captions' type as the headline: **a** the photoreal open grave, "READ-ONLY"; **b** the Dev's face glitching into a waveform (S42), "WHO'S RAPPIN' THIS?"; **c** the toy Dev and the photoreal Dev from S41 split on a diagonal, zoomed 1.7× about a point either side of him so each is whole, "I'M THE BOT".

## 2026-11-02T14:15:00-05:00 — M7: Act 1 re-rendered (the chairs), the full cut v1, the vertical cut v1, thumbnail options
- **Act 1 re-render done:** `renders/m7/act1/frames` (3686 frames, 435–4120). Diffed every 4th frame against the approved `renders/m4/act1_v8/frames` (pixels off by more than 12/255): only S03's and S05's eatery passages differ (frames 571–615 up to 0.7%, 707–807 up to 5.5%: the chairs turned to their tables), plus the cut frame below; everything else identical. The log's two "Failed to create GPU texture from Blender image" errors (frames ~1768) changed no frame.
- **The cut frame's daylight flash:** frame 435 (song 0.14 s, the cut on the first piano chord) averaged 81.9 (v8: 99.8) against 64.4 for the frames after it: the centred motion-blur shutter sampled the pre-roll's daylight keys half a frame earlier. `scenes/blender/animatic.py` gains `--mb-start` (the shutter opens on the frame); frame 435 alone re-rendered with it (`--from 0.14 --to 0.16 --mb-start` → `renders/m7/act1_cutframe/`): 64.4, 0.01% off frame 436. Put into the sequence; the centred-shutter frame kept as `renders/m7/act1/f_00435_centred_shutter.png`.
- **Full cut:** `scripts/assemble.py renders/m7/m7_full_v1.mp4 --preroll renders/m6/preroll_v6 --act1 renders/m7/act1/frames --srt deliverables/read_only.srt`: 268.21 s, 6437 frames, 1280×720 (the draft720 tier; the final render's resolution is for the M7 gate), −16.8 LUFS integrated. Contact sheet checked: captions on every section, none over the end card.
- **Vertical cut:** `--vertical` → `renders/m7/vertical_v1.mp4` (48.12 s, 1080×1920, S34–S45) and `deliverables/read_only_vertical.srt`.
- **Thumbnails:** `scripts/thumbnail.py renders/m7/thumbs --act1 renders/m7/act1/frames` → `thumb_{a,b,c}.jpg` for the human to choose (R1).
- **Review copies:** `renders/review/m7_full_v1_review.mp4` (CRF 25, 41 MB; over the 30 MiB send limit, so also `m7_full_v1_review_small.mp4`, two-pass 750 kb/s, 28 MiB, the one sent), `renders/review/m7_vertical_v1_review.mp4` (540×960, 6 MB).
- **Found for the final render:** the end card's intervention count was drawn at 40; `log/human_interventions.md` now has 49 entries (and M7/M8 will add more): re-render `end_card` from the final count.
- **`scripts/manifest.sh`:** its filter loop returned 1 when the last file it checked was tracked (under `pipefail` the script stopped before its summary line; the manifest itself was complete). The loop now uses `if … then … fi`; the manifest is byte-identical.

## 2026-11-02T15:00:00-05:00 — M7: full cut v2 (the "Five years later" timecard; a VHS tracking transition into the login prompt)
- **Why:** the human's notes on full cut v1 (human interventions, same date, R1).
- **Timecard:** `scripts/assemble.py` `TIMECARD`: "Five years later" over S02's start (the opener is 2018, the song 2023), set as S01a's "San Francisco, 2018" is (`bookends_assemble.caption`: lower left, 0.6 s fades), from song 0.5 s to 3.05 s, so it is gone before "Yeah, hello?" paints on its row (3.08 s). The `♪♪` tag under the piano moves to the lower right (`captions.py` TAGS, "right"), clear of it, as 608 captioners moved captions off on-screen text.
- **Tracking:** `scripts/act2_assemble.py` `tracking()` replaces M6's fade from the grave (S48a) to the login prompt (S48b). A VHS tracking bar (a 76-line band of snow) rolls up the frame as the scratches go by: its height is the scratch stem's accumulated energy over 194.65–195.75 s (the same curve the fade used), the grave above it and the login prompt below, as a tape switching between two recordings. Each stroke (`scratch_energy()`: the Other stem's energy per frame over its loudest) tears the lines sideways (block wobble, a hard skew at the bar), rolls the picture a few lines, pulls red and blue apart, drains the colour and lifts the snow; a little remains on the login prompt while the last strokes sound. Seeded per frame (repeatable).
- **Cut:** `renders/m7/m7_full_v2.mp4` (268.21 s, the same 6437 frames); review copy `renders/review/m7_full_v2_review_small.mp4` (28 MiB). Test sections checked frame by frame (video 16.5–22.5 s and 211.5–215 s). `deliverables/read_only.srt` regenerated: identical. The vertical cut (S34–S45) is unaffected. v1 and its review copies → `archive/renders/m7/`, `archive/renders/review/`, superseded.

## 2026-11-02T17:21:23-05:00 — M5: keyframes (S49)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49 --seeds 2001,2002 --denoise 0.9`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_v6_d90 | 2001 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v6_d90_s2001.png` | 89.3 | pending (R1) |
| S49_v6_d90 | 2002 | 0.9 | renders/m5/plates/S49/beauty/05236.png | `takes/keyframes/S49/S49_v6_d90_s2002.png` | 74.1 | pending (R1) |

## 2026-11-02T17:24:46-05:00 — M5: keyframes (S49_plate)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_plate --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_plate | 2001 | 0.65 | renders/m7/s49_v8/layout/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_s2001.png` | 54.4 | pending (R1) |
| S49_plate | 2002 | 0.65 | renders/m7/s49_v8/layout/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_s2002.png` | 53.1 | pending (R1) |

## 2026-11-02T17:31:25-05:00 — M5: keyframes (S49_plate)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_plate --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_plate_v2 | 2001 | 0.5 | renders/m7/s49_v8/layout2/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_v2_s2001.png` | 51.2 | pending (R1) |
| S49_plate_v2 | 2002 | 0.5 | renders/m7/s49_v8/layout2/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_v2_s2002.png` | 41.2 | pending (R1) |

## 2026-11-02T17:33:34-05:00 — M5: keyframes (S49_plate)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_plate --seeds 2001,2002,2003`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_plate_v3 | 2001 | 0.8 | renders/m7/s49_v8/layout3/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_v3_s2001.png` | 65.2 | pending (R1) |
| S49_plate_v3 | 2002 | 0.8 | renders/m7/s49_v8/layout3/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_v3_s2002.png` | 65.1 | pending (R1) |
| S49_plate_v3 | 2003 | 0.8 | renders/m7/s49_v8/layout3/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_v3_s2003.png` | 65.1 | pending (R1) |

## 2026-11-02T17:37:15-05:00 — M5: keyframes (S49_plate)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_plate --seeds 2001,2002,2003`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_plate_v4 | 2001 | 0.8 | renders/m7/s49_v8/layout4/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_v4_s2001.png` | 65.1 | pending (R1) |
| S49_plate_v4 | 2002 | 0.8 | renders/m7/s49_v8/layout4/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_v4_s2002.png` | 65.1 | pending (R1) |
| S49_plate_v4 | 2003 | 0.8 | renders/m7/s49_v8/layout4/beauty/05236.png | `takes/keyframes/S49_plate/S49_plate_v4_s2003.png` | 65.1 | pending (R1) |

## 2026-11-02T17:40:42-05:00 — M5: keyframes (S49_mid)

- **Model:** FLUX.2 [dev] `flux2_dev_fp8mixed.safetensors`, `mistral_3_small_flux2_fp4_mixed.safetensors`, `flux2-vae.safetensors`; 28 steps, euler, guidance 4.0, denoise from the layout per row (1.0 = none); reference editing (ReferenceLatent, 1 MP per reference), 1920×1056.
- **Prompts:** `log/prompts/keyframes/<shot>.txt`. **Command:** `.venv/bin/python scripts/keyframes.py S49_mid --seeds 2001,2002`

| Shot | Seed | Denoise | Inputs (reference 1 = layout) | Output | Seconds | Status |
| --- | --- | --- | --- | --- | --- | --- |
| S49_mid_v7 | 2001 | 0.6 | renders/m6/s49_reproj_v3/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v7_s2001.png` | 52.1 | pending (R1) |
| S49_mid_v7 | 2002 | 0.6 | renders/m6/s49_reproj_v3/beauty/05332.png | `takes/keyframes/S49_mid/S49_mid_v7_s2002.png` | 50.2 | pending (R1) |

## 2026-11-02T17:55:00-05:00 — M7: full cut v3 (the fork, spoon and chairs remodelled; S49 regenerated with them)
- **Why:** the human's notes (human interventions, same date, R1): the fork, spoon and chair "prominently missing some detail and have parts floating"; then S49's cutlery "also visibly wrong -- regenerate it".
- **Fork and spoon (`sets/props.py`):** they were flat boxes, the fork's tines four loose slivers, the spoon's bowl a flattened sphere beside its handle, set at fixed heights over the food. New `utensil()`: each one moulded piece, a closed shell over stations along its length (UTENSIL: a rounded handle end, the handle's edges raised 0.5 mm, the neck dipping the head 4–4.5 mm; the spoon's bowl dished 4.5 mm; the fork's four tapered tines with gaps, grown out of the head, their tips curling up 2 mm). New `rest()`: sets a rigid piece down on what's under it (rays down onto the plate, the food, the tray and the table top, sampled along its length and across its width against its own underside; it lies on the upper hull of those heights where the hull spans its middle: on its two highest contacts, through nothing). The tray is built before them; the fish drapes over them as before.
- **Chair (`sets/interiors.ladder_chair`):** its "side stretchers" ran crosswise through the middle of the seat, touching no leg (floating); now stretchers run between the legs on every side (front and sides doubled, one at the back). Turned legs (round, the front ones swelling to the seat, feet), back posts with finials and a turned ring at the seat, an apron under the seat, a rush seat woven in from its four edges (strands twisted in short alternating lengths, three shades), three back slats bowed back 2 cm. The pans' serving spoons: the handle swung with its random angle while the bowl stayed put, so on most pans it stood in the air beside the bowl; it now starts at the bowl's back edge, with a neck.
- **Renders:** the opener `renders/m7/preroll_v7/` (436 frames). Act 1: a survey of stills every 2 s against `renders/m7/act1` found changes only in the eatery shots at song 0.2–16.2 s (largest 2.7% of pixels at 12.2 s), none after; re-rendered song 0.14–20.62 s (`renders/m7/act1_eatery/`, 493 frames) and the cut frame with `--mb-start` (`renders/m7/act1_eatery_cut/`); `renders/m7/act1_v2/frames` links them over `renders/m7/act1/frames` (3686 frames).
- **S49 v8:** plates re-rendered (`renders/m5/plates/S49/`; the M6 plates kept as `renders/m5/plates/S49_m6/` for comparison; the overlay and sign mattes copied, those objects unchanged; `cams.py` re-run). The approved anchors are kept and only the cutlery changed in them:
  - New `scenes/blender/cutlery_matte.py`: mattes of the new fork and spoon (and the old plasticware, rebuilt) from S49's camera. The approved anchor `S49_v5_d90_s2002` had painted the old cutlery a few cm off the set's (its spoon across the napkin), so the old cutlery's area there is traced by hand (`renders/m7/s49_v8/mask_old_painted_05236.png`).
  - New FLUX run on the new plate (`S49_v6_d90_s2001/2002`, config S49 v6, the prompt now describing the cutlery's lie); `S49_v6_d90_s2002` fills the old and new cutlery's areas in the approved anchor; `scripts/keyframes.py` gains a shot `mask` (SetLatentNoiseMask) and repaints only there at 0.8 (`S49_plate` v4; v1–v3 tried a whole-plate paste, which brought back a CG fish, and an inpainted fill, whose smears FLUX copied from its reference): **pick `S49_plate_v4_s2003`**, pasted back inside the mask → `renders/m7/s49_v8/S49_open_v8.png`. The approved fish, eggs and rice stay.
  - Reprojected to frame 5332 (`renders/m6/s49_reproj_v3/`) → `S49_mid_v7_s2001` (FLUX 0.6), pasted into the approved `S49_mid_v6_s2001` where the two reprojections differ → `renders/m7/s49_v8/S49_mid_v8.png`.
  - V v8 as v7 (clip 0 first → middle anchor, clip 1 on the depth alone), prompt `log/prompts/v/S49_depth_v5.txt` (adds "a white plastic fork and spoon resting still on the plate"): seeds 1–2 near identical, the cutlery steady through the push; **pick seed 1** → `sign_paste.py --blur 10`, `overlay_add.py --bloom 0 --bezel 9 --halo 30` → `takes/fx/S49/S49_overlay.mp4`. v7's inputs → `archive/takes/S49_v7_inputs/`, its fx → `archive/takes/S49_v7_fx_final/`.
- **Cut:** `scripts/assemble.py renders/m7/m7_full_v3.mp4 --preroll renders/m7/preroll_v7 --act1 renders/m7/act1_v2/frames` (268.21 s); review copy `renders/review/m7_full_v3_review_small.mp4`. v2 and its review copy → `archive/renders/m7/`, `archive/renders/review/`. The vertical cut and thumbnails don't include the eatery: unchanged.

## 2026-11-02T18:55:00-05:00 — M7: full cut v4 (the downvotes shake the camera; S32's pile, envelope and band on the ground; the IPO banner unrolls)
- **Why:** the human's notes on full cut v3 (human interventions, same date, R1).
- **Camera shake (S22, `shots.py`):** on each downvote's first frame (75.125 s, 76.083 s: the arrow's tip into the balcony floor) the camera and its look-at target take a jolt and a decaying shudder (nine keys 1.5 frames apart, amplitudes 1 → 0, alternating; camera 3.5 cm, target 11 cm, seeded), as `delta_location` on top of their keys, so the frame bumps and tips; settled within about half a second.
- **S32 (`sets/props.py`):**
  - **The check and the band:** set at 0.17 m, they hovered 1–2 cm over the paving (0.150 m, its joint strips 0.156). New `paving()` (the sidewalk, curb and joint strips under a footprint) and `ground_at()` (rays down onto them): the payroll envelope lies with its underside on the highest point under it (moved clear of the pile, to (-7.15, -6.45), turned 0.25); the band's landing key is set to the paving under it (moved to (-6.8, -6.62)).
  - **The brooms:** five 1.45 m brooms with 49 cm heads stood in a 40 cm crate, their heads through its sides. Now the brief's "the mods' brooms stacked by the curb": laid down on the heads' broad faces, heads together and staggered, handles fanned, each set down rigid on the paving and the brooms already placed (`rest()`; `bvh()` builds the ray tree from the mesh data when an object is hidden at the current frame). The crate is gone. (Head-to-tail first: it read as a ladder.)
- **The IPO banner (S30):** the banner was one mesh scaled 0 → 1 in height, its bottom rod and the IPO lettering (parented) squashed with it: a blind stretching. Now (`props.banner_roll`): the top rod and the sheet hang as before; a roll of paper at the sheet's foot (in front of it, toward the camera below), 0.26 m in radius, furled under the rod before the bell, runs down with the sheet's edge, turning as the paper comes off (the length out over its mean radius) and slimming to its 3 cm gold core, which is the bottom rod once it's out; its ends show the turns of paper, and a line along it (the paper's free edge) shows it turning. The lettering is printed at full size and cut off below the roll's axis (a non-turning marker), so it appears as the roll passes. The unroll takes 1.5 s (was 1.2 s).
- **Renders:** S22 `renders/m7/act1_s22/` (153 frames), S30–S32 `renders/m7/act1_s30_s32/` (323 frames). A survey every 2 s from 122 s to 152 s: unchanged. `renders/m7/act1_v3/frames` links them over `act1_v2`.
- **Cut:** `renders/m7/m7_full_v4.mp4` (268.21 s), review copy `renders/review/m7_full_v4_review_small.mp4`; v3 and its copy → `archive/renders/m7/`, `archive/renders/review/`.

## 2026-11-02T19:20:00-05:00 — M7: full cut v4 approved; vertical cut v2 (the pan follows every gravestone); final render at 1080p
- **Approved (human interventions, same date, R1):** the full cut `renders/m7/m7_full_v4.mp4`. The final render is 1080p (the brief's; 4K, raised earlier, is off: Act 2's takes are 1280×704).
- **Vertical cut:** the 9:16 window missed names, Apollo above all (S39b opened on "rif is fun", with Apollo at the frame's left edge); S39c sat between stones as the camera whipped to BotDefense and then cut it in half; S39e lagged Public Data API and Logged-out Reddit. `config/reframe.json`: S39b, S39c, S39e re-keyed from strips every 0.25–0.3 s with a ruler over the frame: the window follows each name as it crosses (S39b: Apollo at the left edge 142.82–143.25 s, rif is fun, Sync for Reddit, BaconReader, Boost for Reddit; S39c: Pushshift, then with the whip to BotDefense; S39e: RSS feeds, Public Data API, Logged-out Reddit). `renders/m7/vertical_v2.mp4` (48.12 s; over `act1_v3`), review copy `renders/review/m7_vertical_v2_review.mp4`; v1 and its copy → `archive/renders/m7/`, `archive/renders/review/`. Checked at 2 frames a second through S39b–S39e: every name in the window.

## 2026-11-02T19:40:00-05:00 — M7 gate passed; M8 starts (the audit packet); the final render's timing
- **M7:** approved (human interventions, same date, R1): full cut v4, vertical cut v2, thumbnail B.
- **M8 (brief: "Fact check and conflict-of-interest audit by another lab's model", "Pay most attention to Verse 4 and the fact card's lawsuit line"):** no audit was run in the planning chat (searched), so it is run now, as Not Yet's were: the human pastes one self-contained prompt into other labs' models (R4: the agent has no access to them) and saves each full response. `log/prompts/audit/m8_audit_prompt.md`: what the video is and the conflict of interest; what can still change (the recording is locked; on-screen text, the end card and the description can change); the lyrics as sung (`lyrics/as_sung_draft.txt` without the alignment notes); every claim on screen (the counters, the lobby screens, the trucks and crates, the banner and ticker, the billboard, the bot's counter and epitaph, all fifteen headstones from `block.TONES`, the login prompt, the S49 notice); the end card verbatim (`overlays/cards.json`); and what to return (model and version, a claim-by-claim fact table with sources, the conflict-of-interest review, harms to real people, a concrete fix per flag). It warns against guessing at events past the model's training (several are from late 2026) and recalls GLM's lesson from Not Yet's audit.
- **Waiting on the audit before the final render:** a flag could change a headstone, a screen or the end card; the final render (1080p, `config/render_profiles.json` "final") picks up the fixes. Its per-frame time is being measured.
- **Final render timing:** the "final" profile (1920×1080, 64 samples, 4 motion-blur steps) renders a frame in about 5–6 s (stills at 60, 100 and 140 s after a 107 s scene build): Act 1 (3686 frames) about 5.5–6 h, the opener (436 frames) about 40 min.

## 2026-11-02T23:05:00-05:00 — M8: the audits are in (Gemini, ChatGPT)
- **Inputs (human interventions, same date, R4):** the human ran `log/prompts/audit/m8_audit_prompt.md` in Gemini and ChatGPT. Copied byte for byte to `log/audits/01_gemini_raw.md` and `log/audits/02_chatgpt_raw.md`; `log/audits/README.md` records each auditor and version. Gemini 4 Argon was selected in the UI, but the response calls itself "Gemini 3.1 Pro" (no fallback notice in the UI); both are recorded.
- **Next:** check each flag against primary sources (the two disagree on BotDefense's count, Boost's date, the September 2026 ruling and the "blackmail" wording), then propose fixes for the human's approval (R1). The final render waits.

## 2026-11-02T23:55:00-05:00 — M8: the audit flags checked; fixes proposed
- **Checked** every flag from the two audits against reporting and mirrors (Reddit-hosted originals unreachable; an archive-API fetch of the BotDefense post was refused as bot-check circumvention and not retried). Results, sources and the proposed fixes are in `log/audits/m8_resolution.md`.
- **Where they disagreed:**
  - The September 2026 ruling: ChatGPT is right; Gemini has unjust enrichment and interference swapped. The end card's line stands.
  - BotDefense's 144,926: it is in the July 5, 2023 shutdown post, worded ambiguously ("In January… our ban list which now stands at 144,926"). The card will attribute it to the post rather than date it.
  - Who ended BotDefense: its volunteers (ChatGPT).
  - Boost's June 30 date is unsupported (Gemini).
  - Huffman's documented words were "threatening" and "coercing"; "blackmail" is Selig's report of what Huffman told staff (both auditors).
- **Proposed (R1 pending):**
  - On screen: S10's BLACKMAIL → "HE'S THREATENING US"; Boost's headstone → 2023; r/IAmA → "celebrity bookings"; the $20M total labelled as Apollo's estimate; S49's notice "free access"; a disclosure after "allegedly".
  - End card: BotDefense reworded; the IPO (with the directed share program) and the OpenAI deal added; the lawsuit line with Reddit's allegations, Anthropic's denial and no ruling on the merits; the conflict-of-interest note with Reddit's anti-scraping rationale and the reviewers.
  - The description; the declined flags, with reasons.

## 2026-11-03T00:40:00-05:00 — M8: the audit fixes applied (text); the repository link
- **Approved (human interventions, 2026-11-03, R1)**; the fixes from `log/audits/m8_resolution.md`:
  - **S10's lobby screen** (`overlays/screens.html` `lobby_blackmail`): BLACKMAIL → "HE'S / THREATENING US" in two lines, sized to fit, flashing as before; the grey-box's text (`shots.py`) matches. Re-rendered `renders/screens/lobby_blackmail/` (60 frames).
  - **Headstones** (`sets/block.py` TONES): "Boost for Reddit / 2023"; "r/IAmA celebrity / bookings / July 2023". Renders with Act 1.
  - **The running total** (`overlays/overlay.html`): the panel 30 px taller, "APOLLO'S ESTIMATE, PER YEAR" under the figure. `renders/overlays/act1/` re-rendered (443 frames, 1080p).
  - **S49's notice** (`phone_s49`): "when free access to the API ended." Re-rendered `renders/screens/phone_s49/`; the S49 overlay pass follows.
  - **The disclosure** (`scripts/captions.py` NOTICES): at the top of the frame in the captions' boxes, 169.1–176.4 s (after "allegedly" to before the second "This call was recorded"): "CLAUDE (ANTHROPIC) WROTE THESE LYRICS. REDDIT IS SUING ANTHROPIC, ALLEGING IT SCRAPED REDDIT WITHOUT A LICENSE. ANTHROPIC DISPUTES IT. NO RULING YET." It is six rows in the main cut and eight in the vertical. It is burned in, not in the SRT.
  - **The vertical cut** (`config/reframe.json`): it runs on through S47 (176.74 s, whole frame over the blurred fill), so the disclosure holds 7 s; S45's end gave it 3.
  - **End card** (`overlays/cards.json`): five pages in the same 42 s (the card's music is fixed at 41.48 s), timed 6/8/9/9/10 s:
    - credits, plus the repository link (the human: "the end cards also need the link to where this repository will be hosted (https://github.com/Derivative-Work/read-only)"), as "Full production log: …", as in Not Yet;
    - 2023, with BotDefense reworded;
    - 2024 (new): Google; the IPO and the directed share program; OpenAI; robots.txt;
    - since then, with the lawsuit line rewritten;
    - notes: the conflict-of-interest line with Reddit's rationale and "Reviewed by Gemini and ChatGPT".
    The card is now drawn at 1920×1080 (laid out at 1280×720, scaled; `overlay_cues.py` size); a long source narrows its fact's column (TechCrunch; Bloomberg Law overlapped). Re-rendered `renders/screens/end_card/` (1009 frames). The intervention count, 59 now, is regenerated before the final assembly.

## 2026-11-03T01:30:00-05:00 — M8: S49's notice; the final render started; the assembly at 1080p
- **S49:** the overlay pass re-rendered with the new notice (`sign_matte.py -- S49 --own --subdir overlay --objects 'screen.phone_s49.face' 'eat.badge.exp'`, 192 frames), then `overlay_add.py S49 takes/fx/S49/S49_sign.mp4 --bloom 0 --bezel 9 --halo 30` → `takes/fx/S49/S49_overlay.mp4` ("when free access to the API ended" reads at the push's end). The M7 overlay and its audio copy → `archive/takes/S49_v8_fx_m7/`.
- **Final render (running, background):** `animatic.py --profile final --look final`: the cut frame with `--mb-start` → `renders/final/act1_cut/` (done); the opener (frames 0–434) → `renders/final/preroll/`; Act 1 (436–4120) → `renders/final/act1/`; log `renders/final/render.log`.
- **Assembly at the render's size:**
  - `scripts/assemble.py` sizes the edit from the Act 1 frames (`sizes()`: 1920×1080 for the final; the M7 review frames still give 1280×720).
  - `bookends_assemble.set_size()`: the camera UI, the photo viewer and the captions are drawn at 720-line measures scaled by `u()`.
  - `act2_assemble.set_size()`: the rewind's and the tracking's pixel measures are scaled; scan lines are every third 720-line row; Act 2's takes, the login prompt and S49 are scaled to cover the frame (1280×704 and 1280×720 sources).
  - End card frames are 1920×1080 (`overlay_cues.py`).
- **Tested** over the M7 frames plus the new 1080p cut frame: 1080p sections at video 184–196 s (the disclosure over S45, above the lyric captions) and 211–232 s (the tracking into the login prompt, S49, the end card's credits with the link), and the vertical cut (52.75 s, S34–S47; the disclosure over S47's fitted frame and "THIS CALL WAS RECORDED."). All as intended.

## 2026-11-03T01:45:00-05:00 — M8: the description drafted
- `deliverables/description.md` (fix 12–14 in `log/audits/m8_resolution.md`): what made what; the repository link; the conflict-of-interest disclosure (Reddit's allegations as allegations, Anthropic's dispute, the September 2026 ruling, no ruling on the merits, Reddit's anti-scraping rationale, nothing implied about Claude's training data, Suno's open question, the audits); a note on "blackmail" (what was said on the June 7, 2023 call, the recording and the apology on it); every headstone with what stopped and its source (Boost, BotDefense and r/IAmA as corrected); the tradition line; the creator's disclosure. The lawsuit's status is marked for re-checking on the release date.

## 2026-11-03T02:00:00-05:00 — The repository pushed (private)
- The human created https://github.com/Derivative-Work/read-only (private) and gave access (human interventions, same date, R4). Checked before pushing:
  - nothing from `reference/private/` or `assets/real/` in any commit (only `assets/real/README.md`);
  - no blob over 2 MB in the history;
  - the user's email address appears nowhere in the tracked files.
  `origin` set over HTTPS, as Not Yet's (SSH had no key); `main` pushed. A clean-up for release comes later (the human).

## 2026-11-03T05:50:00-05:00 — M8: the final render done; S10's screen re-laid out
- **Final render finished** (exit 0): the opener (0–434), the cut frame, and Act 1 (436–4120, 3,685 frames, none missing) at 1080p. A contact sheet of every 100th frame matches the approved look.
- **S10, found in the survey:** the two-row "HE'S / THREATENING US" fell behind the server racks ("THREAT▮▮NG US"). `overlays/screens.html` `lobby_blackmail`: both rows now sit in the screen's top half (0.21 H text from 0.17 H). `renders/screens/lobby_blackmail/` re-rendered (60 frames); S10 re-rendered at final (frames 1315–1373, `--from 36.79 --to 39.21`, log `renders/final/render_s10.log`). Readable from the first to the last frame, in both flash states. The headstones (Boost "2023"; r/IAmA "celebrity bookings") read correctly.

## 2026-11-03T06:00:00-05:00 — M8: the final cuts assembled
- **End card:** `overlay_cues.py` (interventions: 60), `renders/screens/end_card/` re-rendered (1009 frames).
- **Act 1 frames:** `renders/final/act1_frames/` links the cut frame (`act1_cut/f_00435.png`) and `renders/final/act1/` (3686 frames, with S10's re-render).
- **Main:** `scripts/assemble.py renders/final/out/read_only_main.mp4 --preroll renders/final/preroll --act1 renders/final/act1_frames --srt …` → `deliverables/read_only.mp4`: 268.21 s, 1920×1080, 24 fps, −16.8 LUFS integrated (as M7). The SRT is unchanged from `deliverables/read_only.srt`.
- **Vertical:** `--vertical` → `deliverables/read_only_vertical.mp4`: 52.75 s (S34–S47), 1080×1920. Its SRT (now through S47) → `deliverables/read_only_vertical.srt`; the M7 one → `archive/deliverables/read_only_vertical_m7.srt`.
- **Checked:** contact sheets of both (every 7.5 s and 5 s): the opener's caption and camera, the lobby screen, the total's label, the headstones, the disclosure over S45 (main) and S47 (vertical), the login prompt, S49, all five end card pages (60 interventions; the repository link). Logs `renders/final/assemble_{main,vertical}.log`.
- **Review copies** (two-pass x264, 750 kb/s): `renders/review/m8_final_review_small.mp4`, `renders/review/m8_final_vertical_review_small.mp4`. Manifest updated.
- **The M8 gate:** awaiting the human's approval (R1). Approving logs a 61st intervention; the end card would then read 60, one behind (re-render the card and re-assemble if wanted).
