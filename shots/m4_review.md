# M4 review: Act 1 final renders and overlays (S02–S39e)

The brief's gate is **"Approve each section"**. Each section is its own clip in `renders/m4/sections_v8/`, at 1280×720
(your call: 720p for review, 4K at the end) and 24 fps, with the post-filtered master. `renders/m4/m4_act1_v8.mp4` is all seven back to back.

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

## Since v7: your notes

- **S02–S03, the handset:** it hangs on its coiled cord from the cord's exit on the housing's left side (it hung from the housing's middle), and sways gently from there.
- **S02–S03, the tape:** it's now in a portable cassette recorder (generic, no maker's name) taped to the post beside the handset with grey duct tape, the tape behind its smoked window. A lead runs from it to a suction-cup pickup on the handset's back. The REC light is on the recorder. S03 frames the recorder and handset, then pushes in on the REC light.
- **S11:** the Dev flips the recorder's door down and lifts the tape out.
- **S18:** the throne's seat is at sitting height on a base set back from his legs; he sits on it, his cape ending on the seat.
- **S20:** he dribbles: the ball hits the floor on each beat, his palm meets it on the way up, rides it down and pushes it off.
- **Clips 1, 2, 3 and 4 changed** (clip 3 only because the payphone is in the background of S17). Clips 5–7 are the same frames as v7.

## Since v6: your notes

- **S26, the doghouse:** the roof's two panels now meet under a ridge cap (they stopped short of the peak), and the doorway is a round arch. "BOT DEFENSE" now sits on its board; it had floated 4 cm off it and cast a ghost copy below.
- **S28:** the truck has a real door opening and a hollow load area, so the crates stay in sight, in shadow, once they're loaded.
- **S30:** "IPO" is printed on the banner and unrolls with it.
- **Only clips 5, 6 and 7 changed.** Clips 1–4 are the same frames as v6.

## Since v5: your notes

- **S02:**
  - **Flicker:** each shop's lintel, the strip of wall above the shopfront, shared a plane with the tops of its brick side columns. It now fits between them. A new check that tests every surface in the scene found and fixed more overlaps: the curbs, the tower's ticker, the lobby glass, neighbouring posters, and the cars' trim and plates. No spot in S02 keeps flickering (per-pixel check, v6).
  - **Payphone:** modelled: a blue steel housing with a keypad, coin slot and return, a canopy with side panels, and a handset on a coiled cord. S03's REC light is now a soft red, not a white blob.
- **S22:** each "downvote" drives a large blue-purple arrow tip-first into the balcony floor, one either side of the CEO, and the arrows stay. The camera is at balcony level. The colour is your call; the shape stays generic.
- **S25:** re-staged to the brief, side-on, in front of the open little door. The bot holds out the briefcase and the CEO takes it. He hands over an oversized brass key ring, and the bot lowers its arm with the keys.
- **S28:** starts 1 s early (at 1:42.20, off the brief's 1:43.20 cue), so it runs 3.1 s and the forklift moves more slowly; S27 is 1 s shorter. A work light shows the crate labels.
- **S29:** CHAT stops just behind SEARCH and the camera swings left, so both names stay in frame.
- **S31:** ten different thank-you notes in a marker font (Permanent Marker, Apache 2.0), large enough to read. "People found this helpful." is on two lines with room on the sides.
- **S33:** "YOUR LAND" is in front of the Dev and reads the right way up from the camera.
- **S36 and the cemetery:**
  - **Stones:** concrete with a worn sheen. On your note about the stills, each stone now has its own pattern and tone, the face is calmer, and the dirt streaks are lighter, so the inscriptions read.
  - **Grass:** a denser lawn, with short grass among the small markers.
  - **Hook wides:** the stones in the aerial shots are the earlier, uniform ones (too small to tell).
- **Shimmer:** the iron fence bars still shimmer as the camera passes (S38–S39e, worst in S39e). It's aliasing on thin bars, not overlapping surfaces, and the 4K final's higher sample count should smooth it.

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
