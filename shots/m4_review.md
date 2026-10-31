# M4 review: Act 1 final renders and overlays (S02–S39e)

The brief's gate is **"Approve each section"**. Each section is its own clip in `renders/m4/sections_v5/`, at 1280×720
(your call: 720p for review, 4K at the end) and 24 fps, with the post-filtered master. `renders/m4/m4_act1_v5.mp4` is all seven back to back.

| Clip | Section | Shots | Song time |
| --- | --- | --- | --- |
| `1_intro.mp4` | Intro | S02–S03 | 0:00.14–0:20.62 |
| `2_verse1.mp4` | Verse 1 | S04–S13 | 0:20.62–0:50.01 |
| `3_hook1.mp4` | Hook 1 | S14–S17 | 0:50.01–1:00.62 |
| `4_verse2.mp4` | Verse 2 | S18–S25 | 1:00.62–1:29.64 |
| `5_hook2.mp4` | Hook 2 | S26 | 1:29.64–1:40.18 |
| `6_verse3.mp4` | Verse 3 | S27–S33 | 1:40.18–2:04.00 |
| `7_goodbot.mp4` | Good Bot | S34–S39e | 2:04.00–2:33.68 |

## What's new since M3

- **The look:** the approved look test, plus the grunge pass you asked for (`renders/m4/m4_grunge_v4.jpg`). The
  street, the walls and the shops are worn and dirty. The tower, its lobby and the people stay clean.
- **The detail pass** (your note, "pretty much all of the scenes need more detail"; look test
  `renders/m4/m4_detail_1..4.jpg`): a lit city round the block, street furniture and parked cars, stocked interiors,
  modelled gag props, the park and cemetery dressed, the headstones engraved, the figures rebuilt
  (`renders/m4/m4_figures.jpg`). The moon now actually lights the night (a haze bug had swallowed it since M3).
- **Lip sync:** Rhubarb Lip Sync 1.14.0 itself, per sung line on its stem, with the lyrics as dialog text.
- **The overlays (JS)**, drawn rather than noted in brackets:
  - **S03:** the waveform spikes on "recorded".
  - **S06:** the day counter.
  - **S07–S08:** the running total.
  - **S13:** "0 results".
  - **S35:** the ban counter.
- **The screens (JS)**, in the set:
  - **S10:** BLACKMAIL flashes.
  - **S16:** the pawn shop's LED countdown.
  - **S20:** the traffic chart.
  - **S30:** the ticker band.
- **The lobby** is furnished, still corporate-clean.

## Since v3: your notes

- **S03:** the cassette now sits on the payphone's post beside the handset, clear of the phone.
- **Flicker:**
  - Every overlapping surface on the buildings and shopfronts is spaced apart: side walls, paint, signs, tags, street paint, the plaza.
  - The shops' wall paint moved out as part of that, which caught the Dev's pegboard. QC found it, and everything on a painted wall now clears the paint.
  - A per-pixel check finds no spot that keeps flickering. Thin fence bars still shimmer as the camera moves (S38–S39e); that should smooth out in the 4K final.
- **S07–S08, the receipt tape:**
  - It comes off the roll and curves round the counter's edge.
  - It lies on the floor and passes under the Dev's door, which now has a gap.
  - It rides over the curb, the joint lines and the rails, and never goes through anything.
- **S19:** the mods kneel on the sidewalk, filmed low from the side.
- **S20:** the CEO dribbles: the ball meets the floor on the beat and his palm between beats.
- **S28:** a forklift loads a pallet of crates labelled COMMENTS 2005–2023 into the truck, with a SIDEWALK AUCTION sign.
- **S29:** the trucks pull up into frame, and their labels are bigger.
- **S31:** no note rests on "UNDER NEW MANAGEMENT". One crosses it briefly as it flies to the funnel.
- **S09:** the red total fits inside its ring.

## Still review aids, not the final edit

- **Burned in for review:** the lyric line at the bottom, and the shot ID and pipeline code at top right.
- **At M7:** the final captions.
- **S40, the rewind:** assembled in the edit at M7 from these frames.

## Not in M4 (by design)

- **M5:** Act 2 (S41 on): the photoreal pass and lip sync.
- **M6:** the pre-roll (S01a–S01d), with the real plate photo, and the end card.
- **Later:** the sung stage directions, which stay as they are for now (your call at M2).
