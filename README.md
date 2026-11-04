# Read-Only

An AI-made late-'90s boom-bap diss track about Reddit's 2023 API changes and what followed. One night on one
composite block at the edge of San Francisco's Tenderloin: a third-party app developer ("the Dev") and "the CEO" trade
verses, a retired anti-spam bot gets its eulogy, and on "I'm the bot" the stylised Blender street turns photoreal. The
rapper who steps out of it keeps changing faces, because the song's subject touches everybody who ever posted. It
ends where Reddit is heading: visitors expire.

Claude Code (Opus 5.5) produced the video: the Blender set and animation, every generated still and clip, the
overlays, captions, edit and thumbnail. Suno V6 made the music, and Claude drafted the words. A human only approved or
rejected work, corrected sync, fixed technical failures and ran tools the agent couldn't reach, and every such action
is logged.

AI-generated satire about real events. The characters are fictional stand-ins: no real person is named or shown, and
the rappers in Verse 4 are generated people. The block is a composite and the eatery is fictional. The end card says
what actually happened, with sources;
[log/audits/release_fact_check_2026-11-03.md](log/audits/release_fact_check_2026-11-03.md) re-checks each line
against them on the day before release.

**Conflict of interest:** Claude, made by Anthropic, drafted the lyrics. Reddit is suing Anthropic over scraping, and
AI companies buying user data is this song's subject. The lyrics, on-screen text and end card were audited by Gemini
(Google) and ChatGPT (OpenAI); their audits are in [log/audits/](log/audits/README.md), verbatim, with every change
made in response.

## Watch

- **YouTube:** [the main video](https://www.youtube.com/watch?v=DsjWj7C0g1k); the vertical cut (link added at upload).
- **Files:** the videos, captions, thumbnail, music and stems are in the v1.0 release.

## The making-of record

- [The planning chat](https://claude.ai/share/3aa680ba-c565-45bd-9c13-ecacf3444fe1) that led to the song and the
  brief, archived in [docs/planning_chat/](docs/planning_chat/planning_chat.md).
- [docs/brief.md](docs/brief.md): the production brief, set and shot list (mirrored from the live brief), and the
  [Reference Guide](https://claude.ai/artifact/5KCzixyz4DRBiT9wqovwkW) that explains every reference.
- [log/production_log.md](log/production_log.md): every action the agent took, with commands and outputs.
- [log/human_interventions.md](log/human_interventions.md): every human action, with the rule that allowed it.
- [docs/sources.md](docs/sources.md): every end-card claim with the source it was checked against.
- [log/audits/](log/audits/README.md): the end-card fact check and the two outside audits, and how each flag was
  resolved.
- [log/prompts/](log/prompts/): the prompts sent to Suno, FLUX.2, LTX-2.3 and the other models, and Suno's record of
  the take.
- [timing/timing_map.md](timing/timing_map.md) and [style/](style/): when each shot lands in the song, and how it
  looks.
- [METADATA.md](METADATA.md): the YouTube titles, descriptions and settings.

## How it was made

- **Act 1 (S02–S39)** is a stylised Blender set, animated to the song's timing map (beats from Beat This!, words
  aligned with faster-whisper) and rendered with Eevee. Signs, screens and the running total are overlays rendered
  in Chrome headless.
- **Act 2 (S40–S49)** is the same set made photoreal. FLUX.2 [dev] keyframes are made by reference editing from the
  Blender frames. LTX-2.3 (22B, IC-LoRA union control with depth or MoGe geometry from the Blender renders) turns them
  into video, and LatentSync 1.6 syncs the rapper's lips to the vocal.
- **The Verse 4 recast:** outside reviewers read a single photoreal rapper in Verse 4 as AI blackface. The human asked
  for rapid cuts between generated rappers of different ethnicities, keeping the original one, to show that this is
  affecting everybody. Each approved keyframe was repainted inside a mask over the head, neck and hands only, so the
  street, light, pose and costume stay the same and every cut is a matched face swap
  ([config/recast.json](config/recast.json), [scripts/recast.py](scripts/recast.py)). VHS-era tape transitions run
  between the faces, masked to the pixels that change.
- **The real image:** the creator's breakfast photo from March 2018, on the phone's screen in the opener. The visitor
  badge and interview schedule beside it are recreations: the times are kept, and no names, logo or room appear.

## Files

Large files stay out of git. [MANIFEST.sha256](MANIFEST.sha256) lists them with SHA-256 hashes: the Suno track and
stems, the post-filtered master and the card bounce, the finished videos, and every take and render, so a rebuild can
be checked against them. The human's reference photos and scans (`reference/private/`) and the fact-check sources
(other publishers' pages) are kept locally and never published; [reference/README.md](reference/README.md) describes
the references without their details.

## Rebuilding

Versions used: Blender 5.2.3 LTS, ffmpeg 8.0.1, Node v24.22.0, uv with Python 3.12, ComfyUI (the API-format workflows
are in [workflows/](workflows/)), an NVIDIA RTX 5090.

```bash
uv sync                                   # .venv from pyproject.toml / uv.lock
npm ci                                    # Puppeteer and its Chrome headless shell
git config core.hooksPath scripts/hooks   # the 50 MiB pre-commit check
```

Put the large audio files back at the paths `MANIFEST.sha256` lists. `scripts/fetch_textures.py` and
`scripts/fetch_models.py` re-download the CC0 textures and models. Each production-log entry has the step's exact
command, inputs, outputs and checks (Python runs as `.venv/bin/python -I scripts/<name>.py`). In outline:

1. **Timing:** `timing_map.py` and `beats_beat_this.py`, from the stems and the word alignment.
2. **Act 1:** the Blender scene in `scenes/blender/`, then `overlay_cues.py` and the overlays under `overlays/`.
3. **Act 2:** `stills.py` and `keyframes.py` (FLUX.2), `ltx_v.py` (LTX-2.3), `l_batch.py` (LatentSync),
   `glitch_face.py` and `reveal.py`; the recast with `recast.py` and `recast_v.py`.
4. **Assembly:** `assemble.py` (the main cut, and the vertical cut with `--vertical`) → `deliverables/`;
   `thumbnail_recast.py` for the thumbnail.

Generated stills and clips depend on model weights and GPU kernels, so a rebuild matches the manifest's hashes only
for the deterministic steps; the takes themselves are in the manifest.

## Licences

- **Video and assets:** [CC BY-NC-SA 4.0](LICENSE-media.md). That file lists exactly what it covers, and what it
  doesn't (fonts, textures and models, the breakfast photo file, the reference material, the fact-check sources).
- **Code:** [MIT](LICENSE).

## Credits

- **Concept and bookends:** the creator.
- **Words:** Claude, in the planning chat, revised after audits by Gemini and ChatGPT. Conflict of interest: see
  above.
- **Music:** Suno V6, generated and chosen by a human.
- **Mastering:** music-deslop, a post-filter model for AI-generated music that Claude Code built and trained from a
  human-written spec, on Creative Commons audio only (checkpoint M6f 10k; its training data is listed in
  [Not Yet's README](https://github.com/Derivative-Work/not-yet#mastering-model-training-data)). The model is private
  for now. Its settings are in the production log.
- **Set, animation, generated video, edit, captions, end card and thumbnail:** Claude Code with Claude Opus 5.5.
- **Models:** FLUX.2 [dev] (Black Forest Labs) with its Mistral 3 Small text encoder, LTX-2.3 (Lightricks) with the
  IC-LoRA union control, LatentSync 1.6 (ByteDance), MoGe (geometry), Beat This! (beats) and faster-whisper (lyric
  alignment). The ambience is LTX-2.3's own audio track.
- **Tools:** Blender 5.2 (Eevee), ComfyUI, ffmpeg, Node.js with Puppeteer and Chrome headless shell, and Python with
  NumPy, SciPy, OpenCV, Pillow, librosa, soundfile and PyTorch.
- **Textures and models:** [Poly Haven](https://polyhaven.com), CC0.
- **Fonts:** [VT323](https://fonts.google.com/specimen/VT323) by Peter Hull (captions), [Inter](https://github.com/rsms/inter),
  [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono) and [Oooh Baby](https://github.com/googlefonts/oooh-baby),
  SIL Open Font License 1.1; [Permanent Marker](https://fonts.google.com/specimen/Permanent+Marker) by Font Diner,
  Apache License 2.0.

Hip-hop is a human tradition, built by Black and Latino artists in the Bronx. This one was generated from it.

The creator interviewed at Reddit in 2018. Satire. Not affiliated with or endorsed by Reddit, Anthropic or any other
company named here.
