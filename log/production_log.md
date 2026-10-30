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
