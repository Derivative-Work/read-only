# Upload metadata

YouTube metadata for the main video and the vertical cut, ready to paste at upload. Written by the agent (M8, release
prep, 2026-11-03); the human uploads (R4).

**Before uploading:**
- **The last news check (morning of release).** Search once for news on Reddit v. Anthropic and on Reddit's Google
  deal since 2026-11-03. If either has moved, the end card's lawsuit line or "Google, which pays Reddit" may need
  changing (`log/audits/release_fact_check_2026-11-03.md`).
- **Intervention count.** The main description gives the number logged at upload
  (`grep -c '^## ' log/human_interventions.md`). The end card gives the count when it was rendered.
- **The main video's link** goes in the vertical cut's footer once the main video is up. In YouTube Studio, also set
  the vertical cut's **Related video** to the main video.

**Release plan (human, 2026-11-03):** both on the morning of 2026-11-04. Licences: video and assets CC BY-NC-SA 4.0,
code MIT, as the earlier videos (`LICENSE`, `LICENSE-media.md`).

---

## Main video (16:9, 1920×1080, 24 fps)

**File:** `deliverables/read_only.mp4` (4:28.2). Captions `deliverables/read_only.srt`. Thumbnail
`deliverables/read_only_thumbnail.jpg`.

### Title

In use since 2026-11-04 (59 characters; the human, R1, after the first title underperformed):

```
Reddit sold your posts to AI, so AI wrote a diss track back
```

The title at upload: `Read-Only — an AI-made diss track about Reddit's API changes`.

Alternatives:
- `Read-Only (I'm the Bot) — AI-generated '90s boom-bap about Reddit`
- `Read-Only: good bot, bad bot — an AI diss track about Reddit`
- `Reddit is suing the company whose AI wrote this diss track`
- `Reddit wants you logged in. Here's a diss track about why.`
- `Remember Apollo? A '90s diss track about Reddit, made by AI`
- `Good bot: a '90s diss track about what Reddit did to its bots`

### Description

```
AI-generated satire about real events. Not investment advice.

A late-'90s boom-bap diss track about Reddit's 2023 API changes and what followed. One night on one block: an app developer and "the CEO" trade verses, a volunteer anti-spam bot gets its eulogy, and on "I'm the bot" the street turns photoreal and the rapper keeps changing faces. The characters are fictional stand-ins; the Verse 4 rappers are generated people. The block is a composite and the eatery is fictional. The only real image is the creator's breakfast photo, March 2018.

Lyrics drafted by Claude (Anthropic), music by Suno, video by Claude Code with Blender, FLUX.2 [dev], LTX-2.3 and LatentSync. A human only approved or rejected work, fixed sync and technical failures, and ran tools the agents couldn't reach. Each of those [N] interventions is logged, with every prompt and production step:
https://github.com/Derivative-Work/read-only

CONFLICT OF INTEREST
Claude, made by Anthropic, drafted these lyrics. Reddit is suing Anthropic (filed June 2025, San Francisco Superior Court), alleging it scraped Reddit without a license, accessed or tried to access the site more than 100,000 times after saying it had stopped, and, unlike the AI companies that license Reddit's data, didn't agree to honour deletions. Anthropic disputes the claims. In September 2026 the judge let the contract, interference and unfair-competition claims proceed. As of Anthropic's Nov 2, 2026 SEC filing the case is pending, with no ruling on the merits.

The song criticizes Reddit for selling its users' work to AI companies; the same criticism applies to the AI companies, including the one whose model wrote it. Reddit says its lockdowns since 2024 target AI companies that scrape without paying. Gemini (Google) and ChatGPT (OpenAI) fact-checked the lyrics, on-screen text and end card; their audits and our changes are in log/audits/.

CHAPTERS
0:00 Opener: San Francisco, 2018
0:21 Intro
0:38 Verse 1
1:05 Hook
1:18 Verse 2
1:47 Hook
1:58 Verse 3
2:22 Good bot
2:51 Verse 4: I'm the bot
3:10 Outro
3:46 Credits and the facts

"Blackmail" is the Dev's word. On the record, Reddit's CEO said the developer "threatened" Reddit; the lobby screen shows those words. More, with every source: https://github.com/Derivative-Work/read-only/blob/main/docs/sources.md

THE HEADSTONES
- Apollo, June 30, 2023: iOS app, shut down over API pricing (Wikipedia)
- rif is fun, June 30, 2023: Android app (Wikipedia)
- Sync for Reddit, June 30, 2023: Android and iOS app (9to5Google)
- BaconReader, June 30, 2023: Android app (Android Authority)
- Boost for Reddit, 2023: Android app, due to stop June 30; its key worked into July (9to5Google; Droid Life)
- ReddPlanet, June 2023: app, announced its shutdown citing pricing and short notice (AndroidHeadlines)
- Pushshift, May 2023: Reddit cut off its API access; moderator tools that relied on it degraded (r/modnews)
- BotDefense, 2023: volunteer anti-spam bot. Its volunteers stopped it in July 2023, blaming the API changes and Reddit's treatment of moderators and developers; their post put its ban list at 144,926 accounts (BotDefense; Ars Technica)
- r/IAmA celebrity bookings, July 2023: the mods stopped coordinating AMAs with notable figures (Social Media Today; The Verge)
- Mobile moderation on r/Blind, July 2023: its mods said they could no longer moderate on mobile (The Verge)
- Search engines other than Google, July 2024: robots.txt blocks crawlers except Google's (9to5Mac); Reddit denies a link to its Google deal
- Wayback Machine archiving, August 2025: most of the site blocked, citing AI scraping (Engadget)
- RSS feeds, November 13, 2026: announced September 30, 2026 (PPC Land; Decrypt)
- Public Data API, 2008 – March 2027: announced September 30, 2026 (PPC Land)
- Logged-out Reddit, 2005 –: on October 29, 2026 Reddit said it would shift to a primarily logged-in experience, testing first outside the US (TechCrunch)

CREDITS
Concept and bookends: the creator · Lyrics: Claude (Anthropic) · Music: Suno V6, post-filtered with music-deslop · Video: Claude Code with Opus 5.5 · Type: VT323, Inter, JetBrains Mono, Oooh Baby (OFL), Permanent Marker (Apache 2.0)

Hip-hop is a human tradition, built by Black and Latino artists in the Bronx. This one was generated from it.
The creator interviewed at Reddit in 2018. The badge and schedule in the opener are recreations.

Video and assets CC BY-NC-SA 4.0 · Code MIT. Satire; not affiliated with or endorsed by any company named.

#AIgenerated #hiphop #Reddit
```

### Tags

Paste as one comma-separated line:

```
Read-Only, AI music video, AI generated, AI satire, diss track, boom bap, 90s hip hop, Reddit, Reddit API, Apollo app, Reddit blackout, good bot, BotDefense, AI training data, data licensing, web scraping, Claude, Claude Code, Suno, Blender, FLUX.2, LTX-2.3
```

### Settings

| Setting | Value |
|---|---|
| Category | Music |
| Audience | Not made for kids. |
| Altered or synthetic content | **Yes.** Realistic generated people (the Verse 4 rappers) and an AI-generated singing voice. |
| Language / caption language | English / English |
| Captions | Upload `deliverables/read_only.srt` as English subtitles. The video also has burned-in captions; the SRT gives search text and lets viewers restyle them. |
| License | Standard YouTube License. YouTube's only Creative Commons option is CC BY, which would drop the NC-SA terms; the description states the licence instead. |
| Thumbnail | `deliverables/read_only_thumbnail.jpg` (1280×720, `scripts/thumbnail_release.py`): G, the photoreal "Logged-out Reddit 2005 –" grave with "LOG IN TO CONTINUE / a diss track for Reddit" (human, R1, 2026-11-04). It replaced D, the lineup (`archive/deliverables/read_only_thumbnail_d.jpg`), used at upload. |
| Chapters | From the description (first at 0:00; each over 10 s). |
| End screen | From 4:18 to the end (10 s), over the end card's last page, whose text sits in the top two-thirds: elements in the bottom corners (the vertical cut or another video bottom left, Subscribe bottom right). Earlier would cover the fact pages. |
| Comments | Open. |
| Visibility | Unlisted for a check pass, then public. |

---

## Vertical cut (9:16, 1080×1920, a Short)

**File:** `deliverables/read_only_vertical.mp4` (52.75 s), captions `deliverables/read_only_vertical.srt`. S34–S47:
from "Good bot" through the headstones, Verse 4's turn to photoreal and the recast, to "This call was recorded". It
opens with the "AI-generated satire" notice and carries the conflict-of-interest disclosure after "allegedly".

Settings as the main video: Music; not made for kids; altered/synthetic content: yes; English captions from its SRT;
Standard YouTube License; Related video: the main video. No chapters or end screen. YouTube takes a custom Short
thumbnail only through the mobile app's upload flow; otherwise pick a frame from Verse 4 in the frame picker.

**Title:**
```
"Good bot, bad bot… which one's singing now?" #Shorts
```

**Description:**
```
AI-generated satire about real events. In 2023 Reddit started charging for its API, and BotDefense, a volunteer bot that had banned 144,926 spam accounts, shut down. Reddit now licenses its users' posts to AI companies. The Verse 4 rappers are generated people; the lyrics were drafted by Claude, whose maker Reddit is suing over scraping (Anthropic disputes the claims; no ruling on the merits). From Read-Only, an AI-made music video.

Full video, facts and sources: https://www.youtube.com/watch?v=DsjWj7C0g1k
Production log, with every prompt and every human intervention: https://github.com/Derivative-Work/read-only
Music: Suno · Lyrics: Claude · Video: Claude Code
Video and assets CC BY-NC-SA 4.0. Satire; not affiliated with any company named.

#AIgenerated #Reddit #Shorts
```

**Tags:**
```
Read-Only, AI music video, AI generated, AI satire, Reddit, good bot, BotDefense, Reddit API, hip hop, Claude, Suno, shorts
```
