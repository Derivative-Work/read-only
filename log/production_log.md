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

## 2026-10-29T23:40:00-04:00 — Step 2: Suno take and planning chat logged; the Reference Guide found

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

## 2026-10-29T23:55:00-04:00 — The human's answers (M1 locked); reference photos filed

- **What:** Logged the human's answers to step 2's open questions (human_interventions, 23:50). Copied the seven reference files from `~/Downloads/read-only-references/` to `reference/private/` (git-ignored, not in the manifest) and the plate photo to `assets/real/plate.jpg`. Checked all against their sources by SHA-256 (7/7, plus the plate copy). Viewed each one (previews in the session scratchpad only). Wrote `reference/README.md`: what each file is, what it's used for, and the eatery's and the props' look, without the private details.
- **Commands:** `cp -p ~/Downloads/read-only-references/* reference/private/`; `cp -p …/breakfast-plate.jpg assets/real/plate.jpg`; `sha256sum` + `cmp`; EXIF via Pillow; `pdftoppm -r 60` for a preview of the scan; `.gitignore` gains `reference/private/`; `scripts/manifest.sh` (still 16 files)
- **Outputs:** `reference/README.md`; `reference/private/` (local only); `assets/real/plate.jpg` (local only, SHA-256 73a0d5f5…)
- **Findings:**
  - **The plate photo is from 2018:** EXIF 2018-03-27 10:35:24 (Pixel). The badge in the scan reads 10:51 AM the same day, and the office photo 16:24:52. That closes the brief's open check "Check the plate photo's date before captioning it '2018'". S01a's caption "San Francisco, 2018" stands.
  - **Private details:** the scan names eight real interviewers and a meeting room, and carries Reddit's logo and mascot. The office photo shows the logo and the human's face. The four restaurant photos are a map service's (other people's photos, some showing staff). None of these go on screen, in git, or in the manifest; the brief's props are recreations.
  - **The eulogy timing works:** the human says the take's "good bot" replies run 2:20–2:33 (about 13 s). Suno repeated them more than the lyrics asked, and that's what led to the brief's ~15 s note. The S39a–S39e headstones fit there; M2 times them.
  - **No final hook:** the human removed it before generating; its "guard dog" lines moved into Hook 2. The brief's lyric block (rev 57) still shows a `[Final hook]`, and S46 is cued to it. Open question for the human: retire S46 or re-cue it.
  - **The master stands:** music-deslop hasn't changed since the first of these videos (the human), so the 2026-10-18 batch is the current chain. Step 1's open question is closed.
- **Why:** Brief, "Inputs the human supplies" (`assets/real/`), "Content guardrails" and "Open checks"; the human's answers.

## 2026-10-30T00:05:00-04:00 — Brief: S46 retired into S48; lyric block matches the take

- **What:** On the human's decision ("fold S46 into S48"), edited the brief (Claude Doc rev 57 → 65). S46's cue now reads "Retired: the take has no final hook. Folded into S48." and its shot is "None"; the ID stays (retired, not removed). S48's shot gains S46's imagery: the crane rises over the photoreal block with a VIP bot in every doorway and "Log in to continue" keypads on the shutters, as well as the red REC lights. The lyric block now matches what the human gave Suno: `[Hook]` became `[Hook 2]` written out with the "guard dog" lines, and the `[Final hook]` block is gone (the human, 23:50). S46's other two mentions (the login-gags open check, the `badge_vip.png` input row) now name S48. Re-exported `docs/brief.md`; lyric block saved as `lyrics/locked_brief_rev65.txt`.
- **Commands:** Docs connector `update` on node `a990c55c-da10` (find-targeted text ops: one `delete`, six `replace`; then one fix-up `replace`, because "S46, S48" → "S48" had dropped the S48 entry from the open check); `python3 -I scripts/doc_to_md.py <read result> docs/brief.md`
- **Findings:**
  - `lyrics/locked_brief_rev65.txt` now differs from Suno's page lyrics only in curly quotes, section-tag wording, "(downvote)" vs "(downvote sound)", and the eulogy's arrangement note.
  - **For M3:** S26 ("Hook 2: reuse S14–S17") reuses S16's 48-hour countdown and S17's meter, which are cued to Hook 1's last two lines. Hook 2 ends on the "guard dog" lines instead, so those two reuses need new cues or new dressing.
  - Not changed: the Reference Guide's "Final hook" row (it explains the lines, which are still sung in Hook 2).
- **Why:** The human's decision (human_interventions, 00:00).
