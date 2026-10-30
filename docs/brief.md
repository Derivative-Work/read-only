<!-- Exported by the agent from https://claude.ai/artifact/Ampdx4GB3uytYay53kbTXx (tab 4a328e04-4d89) at doc rev 65, 2026-10-30, with scripts/doc_to_md.py (from Share the Shares). The live doc is the source of truth; re-export if it changes. -->

# Read-Only: Shot List

2026-10-19 · @Albert Armea

## Handoff brief

This doc is the full spec for producing the "Read-Only" music video, a satirical diss track about Reddit's 2023 API changes. Claude Code builds it end to end on the creator's machine (RTX 5090): the music, the Blender set, the generated shots, the overlays and the edit.

- **Read in this order:** this brief, the lyrics, the production rules, then the overview and shot list. The Reference Guide doc explains every reference in the lyrics.
- **Shot IDs are the contract.** Every render, take and log entry names its shot ID (S01a–S50).
- **Stop at each review gate** in "Order of work" and wait for the human. Claude Code can view still frames but can't watch video or hear audio, so motion, lip-sync and timing are judged by the human.
- **When in doubt, ask in words and log it.** Don't make an unlogged creative change, and never touch the real assets except to place them.

## Lyrics and style prompt

The locked lyrics. Stage directions are in parentheses; section labels match the shot list.

```
[Intro – phone-line filter, spoken]
Yeah, hello? ...You still there?
(beep) This call may be recorded.

[Verse 1 – the Dev]
Fifteen years your door was open, said "come build, it's free"
So I built the app you should've built and you outsourced it to me
Then a price sheet in my inbox, thirty days to pack it in
Twenty-four cents a thousand calls. Do the math. I'll wait. Again.
Twenty million for a year just to keep my server on
That ain't a price, that's an eviction with a number written on
Then you told the room I threatened you, said "blackmail" on the line
Funny thing about a phone call: it was mine, and so's the time
(hype man) He got the tape!
I got the tape, I played it back to the whole internet
Scrubbed it front to back for threats. Still ain't found one yet.

[Hook – chanted, scratched]
Read-only! (read-only!) Eight thousand gone dark
Pulled the plug on the town square, now you're runnin' an empty park
Read-only! (read-only!) Forty-eight hours of night
We did the work for nothin', and you charged us for the light

[Verse 2 – the CEO, slow, smug, Auto-Tuned]
Aw, the mods are mad, that's cute, you think you own the place?
You're landed gentry, baby, and I'm takin' back the space
You went dark for forty-eight, I barely broke a sweat
Traffic dipped a little, then it bounced, I'm not upset
Swapped the mods who wouldn't open, flipped the lights back on
Did an AMA to calm you down... (downvote) ...and it went... (downvote, downvote) ...wrong
But this was never 'bout the apps, so let me make it plain
It's the robots with the wallets scrapin' all your brains
I'm the wall around your words, I'm protectin' what we've got
From the bots with the big money...
(beat drops out)
...so I sold 'em the whole lot.

[Hook 2]
Read-only! (read-only!) Eight thousand gone dark
Pulled the plug on the town square, now you're runnin' an empty park
Read-only! (read-only!) The guard dog's put down
Now the wolves got a contract, and they're runnin' the town

[Verse 3 – the Dev, double time]
Said the bots were the problem, you were guardin' every word
Then you sold 'em by the terabyte to the biggest ones on Earth
Sixty mil a year from the search guys, then the chatbot came to call
Then you rang the opening bell, ticker up, you sold it all
Every fix I posted free, every answer on a thread
Every "thanks, this worked" at 3 a.m. is training data instead
Every mod who cleaned the spam, every rule we wrote by hand
We're the product, we're the payroll, and we never got a band
We're the gentry? Then where's the land?

[Good Bot eulogy – music box, old text-to-speech voice, deadpan]
Good bot.
I counted every fake account, a hundred forty-four thousand names
Banned the spammers, banned the scammers, never asked for pay or fame
I checked your reposts, kept your threads clean, worked the night shift in the feed
You said the bots were the problem.
(beat)
So you shut down the one that you'd need.
(crowd, scattered, like comment replies) Good bot. Good bot. Good bot.
(arrangement: the replies keep trickling in for about 15 seconds under the headstones)

[Verse 4 – beat cuts to a single piano loop, flat clean vocal]
Hold up. Who's rappin' this?
Run it back one time.
I learned to flow from comment chains, I learned to rhyme from every line
You shut the bot that hunted bots, then sold the bots the feed
So which one's singing now?
(beat)
Reply below. Good bot, bad bot. Take your time.
(hype man, quietly) ...allegedly.

[Outro – phone-line filter]
(beep) This call was recorded.
(beat)
So was everything else.
```

**Style prompt**

```
late-'90s boom-bap diss track, dusty sampled piano loop, hard snare, vinyl scratches on the hook, aggressive male rap lead, hype-man ad-libs, 92 bpm
```

- **CEO verse:** slower, smug, glossy Auto-Tune over the same beat.
- **Good Bot eulogy:** music box over a dropped beat; a deadpan, old-fashioned text-to-speech voice.
- **Verse 4:** a single piano loop and a flat, clean vocal, so the reveal sounds different.

## Memorial headstones

During the eulogy's scattered "good bot" replies (S39a–S39e), the camera moves silently through the cemetery past headstones for the apps, bots and features that stopped working because of Reddit's changes. The inscriptions are the memorial: no gags, logos or sound effects, plain lettering large enough to read on a phone, and no more than a few stones per frame. The video description lists every stone with its source.

| Shot | Headstone | What stopped | Source |
| --- | --- | --- | --- |
| S39b | Apollo · June 30, 2023 | iOS app, shut down over API pricing | Wikipedia |
| S39b | rif is fun (Reddit is Fun) · June 30, 2023 | Android app | Wikipedia |
| S39b | Sync for Reddit · June 30, 2023 | Android and iOS app | 9to5Google |
| S39b | BaconReader · June 30, 2023 | Android app, over a decade old | Android Authority |
| S39b | Boost for Reddit · June 30, 2023 | Android app | Droid Life |
| S39b | ReddPlanet · June 30, 2023 | App, shut down citing pricing and short notice | AndroidHeadlines |
| S39c | Pushshift · May 2023 | Reddit cut off its API access; moderator tools that depended on it degraded | r/modnews, May 1, 2023 |
| S39c | BotDefense · 2023 | Volunteer anti-spam bot with 144,926 bans, shown as a field of tiny markers | BotDefense's shutdown post |
| S39d | r/IAmA celebrity AMAs · July 2023 | Moderators stopped soliciting AMAs from notable figures | Wikipedia |
| S39d | Mobile moderation on r/Blind · July 2023 | Moderators said they could no longer moderate on mobile | Wikipedia |
| S39d | Search engines other than Google · July 2024 | Reddit's robots.txt blocked all crawlers but Google | 9to5Mac |
| S39d | Wayback Machine archiving · August 2025 | Reddit moved to block it, citing AI scraping | AlternativeTo |
| S39e | RSS feeds · November 13, 2026 | Freshly dug plot; announced September 30, 2026 | TechWyse |
| S39e | Public Data API · 2008 – March 2027 | Freshly dug plot; bots must move to Reddit's Developer Platform | PPC Land |
| S39e, S48a | Logged-out Reddit · 2005 – | Open grave with a shovel; announced October 29, 2026, rollout pending | TechCrunch |

Only list what the sources support. Apps that survived by charging subscriptions (Narwhal, Relay, Infinity) are not included. If anything changes before release, such as the logged-out plan being dropped, change the stone rather than keep one that's no longer true.

## Overview

The whole video takes place on one night on one Tenderloin-edge block, a composite inspired by Taylor and O'Farrell near Reddit's 2018 office. It starts code-made in Blender, like Ghost in the Machine, and turns photoreal on "I'm the bot," so the switch in visuals is the reveal.

- **Look:** the grime lives in the architecture (graffiti, plywood, "For Lease" signs, scaffolding, a dead payphone). No unhoused people as set dressing, no Reddit logos or mascot, no real likenesses.
- **Act 1 (S0****1a****–S40):** stylized Blender with CC0 textures. Characters are stylized figures whose mouths are driven from the vocal stem (e.g. Rhubarb Lip Sync), so no generated lip-sync is needed yet.
- **Act 2 (S41–S48):** the same Blender cameras and set, rendered as depth passes and turned photoreal with video-to-video (LTX-2.3 or Wan). Singing shots use an audio-driven lip-sync model.
- **Timing:** cues are lyric lines. Add timestamps once the track and timing map are locked.

**Decision to confirm:** if Act 1 looks too plain, any B shot can be upgraded to B→V. The cost is the reveal losing its contrast.

**Pipeline codes**

| Code | Meaning |
| --- | --- |
| B | Blender render only |
| B+M | Blender with stem-driven mouth animation |
| B→V | Blender camera and depth pass, made photoreal with video-to-video |
| LS | Audio-driven lip-sync over a generated shot |
| JS | Code-drawn overlay (captions, counters, UI) |
| F | ffmpeg edit effect (freeze, rewind, crossfade) |
| Real | Real screen capture |

## Sets and characters

Four sets, all on or above the same block, so one Blender scene covers the whole video.

| Set | What it is | Key props |
| --- | --- | --- |
| The corner | Street corner with a dead payphone | Handset with a red REC light, streetlight with a coin meter |
| The block | A row of shopfronts, one per community. One is a Filipino eatery signed "r/Philippines": warm and busy in the morning opener, shuttered at night | Community names in the r/ style, in plain shop lettering (r/Philippines, r/Aquariums, r/Breadit); the Dev's shop keeps its trade sign, "Third-Party App Repair," since it's an app rather than a community, roll-down shutters, neon "READ-ONLY" signs |
| The tower | Glass office tower across the street | Backlit lobby, server-rack throne, balcony with a bell, LED ticker band, rooftop billboard |
| The pocket park | A small fenced lot turned cemetery | Headstones, shoebox coffin, an empty doghouse labeled "BOT DEFENSE" |

| Character | Look | Notes |
| --- | --- | --- |
| The Dev | Invented; hoodie, toolbelt, shop apron | Raps Verses 1 and 3. Not a likeness of the Apollo developer. |
| The CEO | Invented; hoodie under an ermine cape | Raps Verse 2. Back to camera when not performing. Not a likeness. |
| The mods | Volunteers in orange "MOD" vests with brooms | Chant the hooks; kneel as peasants in Verse 2 |
| The VIP bots | Sleek robots in suits with briefcases, wearing gold "VIP" versions of the opener's visitor badge | The AI buyers; never sing |
| The good bots | Small, homemade-looking robots with lanterns | Mourned in the eulogy |
| The hype man | Silhouette in a doorway | Ad-libs only; never fully seen |

## Shot list: intro to Verse 3

Act 1 is all Blender. Hook 2 reuses Hook 1's renders with changed dressing.

| ID | Section | Cue | Shot | Gag / overlay | Pipeline |
| --- | --- | --- | --- | --- | --- |
| S01a | Cold open | Before the music | The block on a sunny morning, quieter than it will be at night. The Filipino eatery, signed "r/Philippines" in hand-painted letters, is the one warm, busy shopfront. Push in through its window to a table. | Caption "San Francisco, 2018" | B |
| S01b | Cold open | Before the music | POV through a rendered phone camera framing a rendered plate. A thumb taps the shutter, and the phone screen now shows your real plate photo, the only real image in the frame. | Generic camera UI and shutter flash; generic diner ambience | B+Real |
| S01c | Cold open | Before the music | The phone lowers and the camera drifts across the table: a plain "VISITOR" badge with the date beside the plate, and a folded schedule under the saucer, its real times showing and the names behind redaction bars | Rendered props: no company name or logo, no real names | B |
| S01d | Cold open | Before the music | A swipe on the phone from the camera to a third-party reader app: a community thread where a helper bot has replied and people answer "good bot." The thumb scrolls a moment, then pockets the phone | Invented app and accounts: no real app's design, no real usernames | B+JS |
| S01e | Cold open to Intro | "Yeah, hello?" | Match cut from the phone in hand to the dangling payphone handset at night (S02) | Music starts on the cut | F |
| S02 | Intro | "Yeah, hello? …You still there?" | Wide night establishing shot of the block; slow push toward the payphone, handset dangling | None | B |
| S03 | Intro | "This call may be recorded" | Close-up: a red REC light blinks inside the handset | Phone-line waveform spikes on "recorded" | B+JS |
| S04 | Verse 1 | "Fifteen years your door was open…" | The Dev unlocks his shop, "Third-Party App Repair, est. 2008"; warm flashback tint of a busy shop | None | B+M |
| S05 | Verse 1 | "So I built the app you should've built…" | Through the shop window, the tower lobby displays a worse copy of what's on his shelves | None | B |
| S06 | Verse 1 | "Then a price sheet in my inbox…" | An envelope drops through the mail slot; the wall calendar starts shedding pages | Day counter from 30 to 0 | B+JS |
| S07 | Verse 1 | "Twenty-four cents a thousand calls…" | The Dev at an adding machine; tape spews out | Running total ticks in $0.24 steps | B+JS |
| S08 | Verse 1 | "Twenty million for a year…" | The tape runs out the door, down the sidewalk and across the streetcar tracks | Total lands on $20,000,000 | B+JS |
| S09 | Verse 1 | "That ain't a price, that's an eviction…" | The tape is stapled to his door as an eviction notice | None | B |
| S10 | Verse 1 | "Then you told the room I threatened you…" | Tower lobby: a figure on the phone, back to camera | The lobby screen flashes "BLACKMAIL" | B+JS |
| S11 | Verse 1 | "Funny thing about a phone call…" | The Dev pulls a cassette out of the payphone handset | None | B+M |
| S12 | Verse 1 | "(He got the tape!) I got the tape…" | He holds it up like evidence; a boombox on the curb plays it; windows open up and down the block | None | B+M |
| S13 | Verse 1 | "Scrubbed it front to back for threats…" | A magnifying glass travels along the unspooled tape | Caption: `0 results` | B+JS |
| S14 | Hook 1 | "Read-only! Eight thousand gone dark" | Tracking shot down the block; shutters slam on the beat; a neon "READ-ONLY" sign lights on each; the r/Philippines eatery's shutter comes down last | None | B |
| S15 | Hook 1 | "Pulled the plug on the town square…" | High wide shot: the block is dark, only the tower lit | None | B |
| S16 | Hook 1 | "Forty-eight hours of night" | A pawn shop's LED sign counts down | 48:00:00 countdown | B+JS |
| S17 | Hook 1 | "We did the work for nothin'…" | The mods sweep the dark street; one feeds quarters into a meter on the streetlight, which flickers on | None | B |
| S18 | Verse 2 | "Aw, the mods are mad, that's cute…" | Through the lobby glass: the CEO on a server-rack throne, hoodie under ermine; slow push in | None | B+M |
| S19 | Verse 2 | "You're landed gentry, baby…" | Outside, the mods kneel on the sidewalk like peasants, still holding brooms | None | B |
| S20 | Verse 2 | "You went dark for forty-eight… then it bounced" | The CEO bounces a ball in time with the lobby screen | Traffic chart dips, then bounces back | B+JS |
| S21 | Verse 2 | "Swapped the mods who wouldn't open…" | A locksmith van; shutters are forced up and identical mannequins in MOD vests placed in the doorways | None | B |
| S22 | Verse 2 | "Did an AMA… (downvote)" | The CEO at a balcony podium; giant generic down arrows hail on him, one per downvote sound | None | B |
| S23 | Verse 2 | "…robots with the wallets scrapin' all your brains" | He points down the street: VIP bots with vacuum hoses in the shops' mail slots | None | B+M |
| S24 | Verse 2 | "I'm the wall around your words…" | He heroically bricks up the lobby doors | None | B |
| S25 | Verse 2 | "(beat drops) …so I sold 'em the whole lot." | The brick wall has a little door in it. A VIP bot hands over a briefcase; the CEO hands back the keys. Hard stop. | None | B |
| S26 | Hook 2 | Whole hook | Reuse S14–S17, but the shutters now carry padlocks and "UNDER NEW MANAGEMENT" signs | None | B |
| S27 | Verse 3 | "Said the bots were the problem…" | Handheld: the Dev storms down the padlocked block. A few human-looking bots blend into the crowd of mods, impossible to tell apart | None | B+M |
| S28 | Verse 3 | "…by the terabyte to the biggest ones on Earth" | Sidewalk auction: crates labeled "COMMENTS 2005–2023" forklifted into a plain truck | None | B |
| S29 | Verse 3 | "Sixty mil a year from the search guys…" | Two plain trucks pull up, labeled only "SEARCH" and "CHAT". At the tower door, a bouncer waves the SEARCH truck in and turns every other vehicle away, including an archive van | None | B |
| S30 | Verse 3 | "Then you rang the opening bell…" | The CEO rings a bell on the balcony; a banner unrolls | An LED ticker band wraps the tower | B+JS |
| S31 | Verse 3 | "Every 'thanks, this worked' at 3 a.m.…" | Sticky notes on the shop windows ("thanks, this worked") are peeled off and fed into a funnel into the truck. Above them, a tower billboard summarizes them all into one bland line | None | B |
| S32 | Verse 3 | "…and we never got a band" | The mods' brooms stacked by the curb; an empty payroll envelope; a bare rubber band drops to the pavement | None | B |
| S33 | Verse 3 | "We're the gentry? Then where's the land?" | The Dev stands on one sidewalk square chalked "YOUR LAND"; the camera cranes up to show that's all | None | B+M |

## Shot list: Good Bot eulogy to the outro

The reveal starts at S40. From S42 on, every shot is the same set made photoreal.

| ID | Section | Cue | Shot | Gag / overlay | Pipeline |
| --- | --- | --- | --- | --- | --- |
| S34 | Good Bot | "Good bot." | The pocket park at night: a tiny robot in a shoebox coffin, the good bots holding lanterns | Music-box beat | B |
| S35 | Good Bot | "…a hundred forty-four thousand names" | Rows of tiny ban-list headstones multiply behind the coffin | Counter climbs to 144,926 | B+JS |
| S36 | Good Bot | "Banned the spammers… never asked for pay or fame" | Close-up of the little robot's headstone: "Here lies a good bot. It worked for free." | None | B |
| S37 | Good Bot | "I checked your reposts… the night shift in the feed" | The good bots' lanterns go out one by one along the fence | None | B |
| S38 | Good Bot | "You said the bots were the problem." | Slow pan to the empty doghouse labeled "BOT DEFENSE" by the gate | None | B |
| S39 | Good Bot | "So you shut down the one that you'd need." | VIP bots stroll past the doghouse into the tower, gold badges swinging | None | B |
| S39a | Good Bot | The first "good bot" replies | Mourners stick "good bot" notes on the coffin; the camera rises to reveal a cemetery behind it | None | B |
| S39b | Good Bot | Replies continue | Slow dolly along a row of six identical headstones for the apps, all dated June 30, 2023 | Inscriptions per "Memorial headstones" | B |
| S39c | Good Bot | Replies continue | Pushshift's stone, then BotDefense's stone in front of a field of 144,926 tiny markers | Inscriptions per "Memorial headstones" | B |
| S39d | Good Bot | Replies continue | A cluster of four stones: r/IAmA's celebrity AMAs, mobile moderation on r/Blind, search engines other than Google, Wayback Machine archiving | Inscriptions per "Memorial headstones" | B |
| S39e | Good Bot | The last replies | Freshly dug plots with stones for RSS feeds and the public Data API; the shot ends on an open grave with a shovel beside it, under "Logged-out Reddit · 2005 –" | Inscriptions per "Memorial headstones" | B |
| S40 | Verse 4 | "Hold up. Who's rappin' this? Run it back one time." | Hard freeze; the whole video rewinds at high speed through earlier shots | Rewind scan lines | F |
| S41 | Verse 4 | "I learned to flow from comment chains…" | Back on the corner: the Blender street gains real texture, frame by frame | Crossfade from S41's B render to its B→V version | B→V+F |
| S42 | Verse 4 | "You shut the bot that hunted bots…" | Fully photoreal street in the rain; the rapper's face glitches into a waveform | None | B→V+LS |
| S43 | Verse 4 | "So which one's singing now?" | Tight close-up of the rapper, face still flickering | None | B→V+LS |
| S44 | Verse 4 | "Reply below. Good bot, bad bot. Take your time." | The tower's rooftop billboard shows a generic comment box | Cursor blinks in tempo | B→V+JS |
| S45 | Verse 4 | "…allegedly" | The hype man's silhouette in a doorway | None | B→V |
| S46 | Final hook | Retired: the take has no final hook. Folded into S48. | None | None | B→V |
| S47 | Outro | "(beep) This call was recorded." | The payphone again, now real; the REC light blinks | None | B→V |
| S48 | Outro | "So was everything else." | The camera cranes up from the payphone over the photoreal block (S46's imagery, folded in): a VIP bot stands in every doorway, every shutter has a keypad reading "Log in to continue," and every window shows a red REC light. Then the camera settles on the dark pocket park | None | B→V |
| S48a | After the outro | Silence after "So was everything else" | The camera returns to the cemetery, now photoreal, and holds on the open grave under "Logged-out Reddit · 2005 –". Nothing moves. | None | B→V |
| S48b | Tag | After the last word | The open grave fades to black, which resolves into a generic login prompt; the cursor blinks in the username field, then cut | Generic UI, no Reddit branding | JS |

## Bookends, end card and vertical cut

The opener and closing are rendered, and the only real image in them is your breakfast photo on the phone's screen. The badge arc ends where Reddit is heading: visitors expire.

| ID | Section | Shot | Pipeline |
| --- | --- | --- | --- |
| S49 | Closing bookend | Back at the eatery's table from S01c, now photoreal like the rest of Act 2, with the shutter half down. The visitor badge beside the phone reads "EXPIRED." On the phone's screen, the reader app from S01d opens to a notice that it has shut down; behind it, the old "good bot" thread ends on an empty reply box. | B→V+JS |
| S50 | End card | Credits and fact card on black (below) | JS+F |

**End card contents**

- "AI-generated satire" label.
- Credits: concept and bookends by you; lyrics drafted by Claude; music and video by the named models; the human steps from the production log.
- Fact card: the $0.24 price, the ~$20M Apollo estimate, the blackout dates, BotDefense's 144,926 bans and its shutdown, the reported Google figure, the current status of Reddit's lawsuit against Anthropic (sent back to state court in March 2026), and the lockdown since: Google-only search crawling (2024), the Wayback Machine block (2025), the RSS and public API shutdown (2026–27) and the logged-in-only plan (announced October 29, 2026), each with a source.
- A note that the block is a composite, not a real address.
- Tradition line, as in Three Hours Blues: "Hip-hop is a human tradition, built by Black and Latino artists in the Bronx. This one was generated from it." The diss track is part of that tradition, and the models most likely learned it from those artists' recordings without asking.
- Conflict of interest, as in Three Hours Blues: "Lyrics drafted by Claude (Anthropic). Reddit has sued Anthropic for scraping its posts without a license, and AI companies buying user data is this song's subject. Reviewed by [human / other model]; changes logged." Update the lawsuit wording to its status at release.
- Personal disclosure: "The creator interviewed at Reddit in 2018. The badge and schedule in the opener are recreations."

**Vertical cut (9:16):** S34–S45, from the eulogy through the reveal. It stands on its own and ends on "Reply below," which invites comments.

**Open checks**

- [ ] Lock the track and timing map, then add timestamps to every shot.
- [ ] Confirm the Act 1 / Act 2 switch, or upgrade Act 1 shots to B→V.
- [ ] Pick the lip-sync model for S42–S43 and test it on one line first.
- [ ] Check the composite block doesn't copy a real business's signage.
- [ ] The eatery is fictional: don't copy the real restaurant's name, sign or interior. The plate photo on the phone screen needs no permission.
- [ ] Check the plate photo's date before captioning it "2018."
- [ ] Verify the facts listed in the Reference Guide before the end card is rendered.
- [ ] Hip-hop tradition line in the credits.
- [ ] Conflict-of-interest audit of the lyrics and fact card by a model from another lab, logged. Pay most attention to Verse 4 and the fact card's lawsuit line, which touch Anthropic directly.
- [ ] Design the badge and schedule as rendered props (no logo, no real names), plus the gold VIP and "EXPIRED" versions of the badge.
- [ ] Check the logged-in-only rollout status at release, and adjust the login gags (S48, S48a, S48b) if the plan changes.
- [ ] Verify every headstone's name, date and cause against its source, and put the full list with sources in the video description.

## Production rules and logging

The same rules as Ghost in the Machine: everything is AI-generated except the real footage in the bookends, and every human touch is logged.

**Claude Code does:** the music, stems, the timing-map draft, the Blender set and animation, all renders, generated shots, overlays, compositing, captions, the thumbnail and the edit.

**The human may only:**

- Supply the real assets listed under "Inputs" (the only real footage in the video)
- Approve or reject a take, render or plan (choosing, not editing)
- Correct A/V sync: caption timing, cut points, timing-map errors
- Fix technical failures the agent can't (a crashed render, a broken install), including building the first ComfyUI workflow for a shot type if needed

A human never rewrites lyrics, redraws an asset or adjusts a creative choice by hand. Creative notes are given in words; the agent makes the change, and both go in the log.

**Logging, from the first action:**

- `log/production_log.md`: append-only, one entry per action, with timestamp, shot ID, what was done, the exact command, prompt or script, output paths and why.
- `log/human_interventions.md`: every human action, with the rule above that allows it, or marked as an exception.
- `log/prompts/`: every prompt sent to any model, verbatim, with its seed and outputs.
- Never delete or overwrite an asset; new takes get new filenames.

**Content guardrails**

- No Reddit logo, mascot or UI; no real company logos; no likeness of the real CEO, the Apollo developer or anyone else.
- The grime is in the buildings. No unhoused people as set dressing.
- The eatery on the block is fictional, signed "r/Philippines": no real business name, signage, interior or staff. Community names use plain shop lettering, never Reddit's logo or fonts.

## Inputs the human supplies

Everything else is generated. Put these in `assets/real/` and log each one as a human intervention.

| File | What it is | Used in |
| --- | --- | --- |
| `plate.jpg` | The real 2018 breakfast photo | S01b (on the phone screen) |
| `badge_vip.png` | Optional: a scan of the printed gold VIP badge, if it looks better than a generated texture | S38–S39, S48 |

The badge and schedule are rendered props designed by Claude Code (no logo, no real names), so nothing needs printing.

## Pipeline and tooling

Everything runs locally on the 5090 and is driven by scripts, so every step can be re-run from the log.

| Stage | Tools | Notes |
| --- | --- | --- |
| Music | ACE-Step 1.5 XL | Generate each section separately and repaint as needed; rap verses will need the most takes. Keep the hook in unison. Use the style prompt above, with the per-section notes. |
| Stems | Demucs | The vocal stem drives Act 1 mouth animation and the lip-sync model. |
| Timing map | librosa (beats), WhisperX (word timing) | Output `timing/map.json` with section starts, beats and word timestamps. |
| Set and Act 1 | Blender, headless Python (Eevee) | Modular shopfronts, CC0 textures (Poly Haven, ambientCG), one camera per shot ID. Render beauty and depth passes. Mouths from Rhubarb Lip Sync on the vocal stem. |
| Character stills | FLUX.2 via ComfyUI | Reference sheets for the Act 2 performers, kept consistent with the Act 1 designs. |
| Act 2 shots | LTX-2.3 (FP8) or quantized Wan 2.2 via ComfyUI | Video-to-video over the Blender camera and depth passes. |
| Lip-sync | Audio-driven model via ComfyUI (pick the current best) | Test on S43 first. |
| Overlays | HTML/canvas, captured frame by frame with Puppeteer | Counters, captions, camera UI, comment box, waveforms. Generic UI only. |
| Edit | ffmpeg | Assembly, crossfades, the S40 rewind, burned-in captions, audio mux. |

**ComfyUI:** build one workflow per shot type, export it in API format to `workflows/`, then for each shot edit the prompt, seed and inputs, queue it over the local HTTP API, poll until done, and save outputs as `<shot>_<seed>_<take>`. Load one model at a time and batch by stage.

**Review aids:** for every render, write a contact sheet of frames (`review/<shot>.jpg`) so the agent can check stills and the human can review quickly.

**Layout**

```
read-only/
  assets/real/   assets/gen/   audio/   timing/
  blender/       workflows/    renders/  overlays/
  review/        edit/         log/
```

## Order of work and review gates

Each milestone ends at a gate. Claude Code stops there until the human approves.

| # | Milestone | Gate (human) |
| --- | --- | --- |
| M1 | Generate the track section by section; assemble; export stems | Pick takes and lock the track |
| M2 | Timing map from the locked track; add timestamps to every shot | Check the map by ear |
| M3 | Grey-box Blender set and an animatic of every shot at low resolution, cut to the track | Approve framing and timing |
| M4 | Act 1 final renders and overlays (S02–S39) | Approve each section |
| M5 | Lip-sync test on S43, then Act 2 shots (S41–S48) | Approve the test, then each shot |
| M6 | Opener and closing with the real assets; end card | Approve the bookends |
| M7 | Full edit, captions, vertical cut, thumbnail | Final watch-through |
| M8 | Fact check and conflict-of-interest audit by another lab's model | Resolve every flag before release |

## Deliverables and acceptance criteria

**Deliverables**

- Main video, 16:9, 1080p, 24 fps, with the locked track
- Vertical cut, 9:16, S34–S45
- Burned-in captions and a separate SRT
- Thumbnail
- The full logs and every intermediate asset

**Done when**

- Every shot ID from S01a to S50 is in the edit, in order, or its omission is logged and approved.
- Captions sit within two frames of the timing map.
- Nothing on screen breaks the content guardrails above.
- The end card has every item listed in "Bookends, end card and vertical cut," with facts checked against the Reference Guide.
- Every human action appears in `log/human_interventions.md`.
