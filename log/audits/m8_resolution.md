# M8: checking the audits' flags, and the fixes proposed

Auditors: Gemini (`01_gemini_raw.md`) and ChatGPT (`02_chatgpt_raw.md`); see `README.md`. Checked by the agent on 2026-11-02 against the sources below, which include the M6 fact check (`m6_end_card_fact_check.md`). Reddit-hosted originals were unreachable from here (old.reddit.com is blocked for the agent's fetcher; an archive API fetch was refused as bot-check circumvention and not retried), so Reddit posts are read through mirrors and press quotes, as at M6.

Status: **proposed; awaiting the human's approval (R1).** Nothing on screen or on the end card has changed yet.

## 1. Where the auditors disagreed

| Flag | Gemini | ChatGPT | Finding | Sources |
| --- | --- | --- | --- | --- |
| BotDefense's 144,926 | A January 2023 figure, stale by July | Reported by the creator; accurate | **Neither is quite right.** The July 5, 2023 shutdown post itself says: "In January of 2023, we added an incredible 10,070 bots to our ban list which now stands at an incredible 144,926 accounts." Ars Technica (July 2023) reports the same total. Whether "now" means January or July is unclear (the post also says only 5,517 were banned in May), so the card should attribute the figure to the shutdown post rather than date it. | lemmy.world/post/1142959 (mirror of r/BotDefense 14riw76); M6 check #4; Slashdot summary of Ars Technica, Jul 9 2023 |
| Who ended BotDefense | Reddit's changes (fine as is) | Its volunteers chose to stop; "Reddit shut it down" is misleading | **ChatGPT is right.** Its creator told Ars Technica that Reddit's "antagonistic actions" toward moderators and developers were "the only reason". The post also cites the API terms, the loss of Pushshift and distrust of Reddit. The end card's "shuts down over the changes" is accurate but doesn't say who chose. | Ars Technica via Slashdot; the shutdown post |
| Boost for Reddit, June 30, 2023 | Wrong: it ran into July | Accurate | **Gemini is right that the date isn't solid.** Boost was due to stop with the June 30 deadline, but its API key kept working into July, and no exact end date is documented. Gemini's quote ("will stop working after July 1st") couldn't be found. | 9to5Google Jun 13 2023; r/redditdev Jun 30 2023 thread (mirror); forum reports |
| The September 2026 ruling | Sept 19; contract, unfair competition and unjust enrichment survive; trespass and interference get leave to amend | Sept 18; contract, interference and unfair competition survive | **ChatGPT is right; Gemini has two claims swapped.** Judge Harold Kahn (San Francisco Superior Court) signed on Sept 17 and filed on Sept 18. Breach of contract, interference with contract and the UCL survive; unjust enrichment and trespass to chattels were dismissed with leave to amend by Oct 16. No report of an amended complaint was found as of today. The end card's line is accurate. | Mashable via Yahoo, Sep 19 2026; Bloomberg Law, Sep 21 2026 (M6 #6); Sigma Law Group, Sep 22 2026 |
| Did Huffman say "blackmail"? | No: he said "threatened" and "coercing" | It's Reddit's accusation, not a finding | **Both are right.** On the June 7, 2023 moderator call (per Selig's transcript): "Apollo threatened us, said they'll 'make it easy' if Reddit gave them $10 million. This guy behind the scenes is coercing us. He's threatening us." "Blackmail" is Selig's account of what Huffman told employees (The Verge, Jun 8 2023, via Wikipedia) and the press's summary. In the AMA Huffman kept up the accusation and complained of Selig "recording and leaking a private phone call". The Reddit employee on the recorded call said: "That's a complete misinterpretation on my end. I apologize." | TechCrunch, Jun 9 2023; Wikipedia, "Reddit API controversy" (citing The Verge, Jun 8 2023); Selig's posted transcript (mirrors) |
| Reddit's complaint against Anthropic | Alleges 100,000+ accesses after Anthropic said it had stopped, and use of deleted posts | Not raised | **Confirmed as allegations.** The complaint says Anthropic's bots accessed Reddit more than 100,000 times after Anthropic said (July 2024) it had stopped, that Claude reproduced posts users had deleted, and that, unlike other AI companies, Anthropic didn't license the data or agree to honour deletions. Anthropic: "we disagree with Reddit's claims, and we will defend ourselves vigorously." | TechCrunch, Jun 4 2025; Telco Magazine; The Decoder; NBC News |
| "Fifteen years" (2008–2023) | Accurate | Misleading (Reddit began in 2005) | **Gemini is right.** The API dates from 2008; the lyric is about the open API. | Wikipedia, "Reddit API controversy" ("In 2008, Reddit introduced its application programming interface") |

## 2. The other flags, checked

| Flag | Raised by | Finding | Sources |
| --- | --- | --- | --- |
| Verse 3's order: Google, then "the chatbot", then the IPO | Gemini | **Accurate flag.** The IPO was March 21, 2024; the OpenAI partnership was May 16, 2024. The lyric can't change, and the end card currently mentions neither. | Reddit IR; OpenAI, May 16 2024 |
| "We never got a band" / "USER CONTENT NOT INCLUDED" | Gemini (and ChatGPT on the ticker) | **Fair satire, but the card should be fair to Reddit.** Reddit's directed share program offered 8% of the IPO's shares to about 75,000 eligible users and moderators (by karma and moderator actions) to buy at the IPO price. | CNBC, Feb 22 2024; 9to5Mac, Feb 26 2024 |
| r/IAmA celebrity AMAs, July 2023 | Both | **Overstated.** On July 1, 2023 the mods said they would stop soliciting and coordinating AMAs with notable figures and run the sub "like your average subreddit". Celebrity AMAs didn't end. | Social Media Today; TheWrap; Quartz (July 2023) |
| Mobile moderation on r/Blind, July 2023 | ChatGPT | **Accurate as their statement.** Its moderators said they could no longer moderate on mobile. | The Verge, Jul 1 2023 (via Wikipedia); Quartz |
| Search engines other than Google, July 2024 | ChatGPT | **Accurate, and still current.** Bing, DuckDuckGo, Mojeek and Qwant lost new Reddit content from July 2024. An August 28, 2026 SerpApi filing alleges Reddit still serves Google a different robots.txt, and no deal with another engine has been reported. Reddit denies a link to the Google deal. | 9to5Mac, Jul 25 2024; PPC Land (SerpApi counterclaims, 2026) |
| Pushshift, May 2023 | ChatGPT | **Accurate.** Reddit cut its access on May 1, 2023; it came back later for moderators only. | r/modnews, May 1 2023 (brief's source) |
| Logged-out Reddit, 2005 – / "Log in to continue" | Both | **Accurate as staged.** The open-ended date says it isn't dead yet, and the end card says tests start outside the US. | TechCrunch, Oct 29 2026 |
| RSS feeds Nov 13, 2026 / Public Data API to March 2027 | Both (future dates) | **Accurate as announced dates.** The end card says "Reddit says". | PPC Land; Decrypt (M6 #9) |
| The $20M total | ChatGPT | **Accurate, but the on-screen total isn't labelled as an estimate.** The end card already attributes it to Selig. | TechCrunch, Jun 8 2023 |
| The S49 app notice, "when access to the API ended" | ChatGPT | **Loose.** The API didn't end; free access did. | — |
| "Selig recorded the call" (Intro/Outro) | Gemini | **No change needed.** He recorded it lawfully in Canada (one-party consent), and nothing in the video suggests otherwise. | TechCrunch; Selig's post |
| Verse 4 and the conflict of interest | Both | **A real gap.** Verse 4 plays as a wink. Reddit alleges that Anthropic, unlike its licensed buyers, didn't pay and didn't honour deletions, and that Reddit's lockdowns since 2024 (Wayback, RSS, logged-out pages) are aimed at unlicensed scrapers. The video never says this, and it's the context most damaging to the lyricist's maker. | As above |

## 3. Proposed fixes (for R1)

### On screen (Act 1; carried into the final 1080p render, no extra render)
1. **S10, the lobby screen:** `BLACKMAIL` → `"HE'S THREATENING US"`, Huffman's documented words on the June 7 call. The sung line stays; the screen then shows what was actually said.
2. **S39b, Boost's headstone:** `Boost for Reddit / June 30, 2023` → `Boost for Reddit / 2023`.
3. **S39d, r/IAmA's headstone:** `r/IAmA celebrity AMAs / July 2023` → `r/IAmA celebrity bookings / July 2023`.
4. **S07–S08, the running total:** a small label under $20,000,000.00: `APOLLO'S ESTIMATE, PER YEAR`.

### On screen (Act 2 and S49)
5. **S49, the app notice:** "when access to the API ended" → "when free access to the API ended". This means re-running `overlay_add.py` only; the take doesn't change.
6. **New, after "allegedly" (S45 on, about 168.5–176 s, also in the vertical cut):** a disclosure at the top of the frame in the closed-caption style, about 5 s: `Claude (Anthropic) wrote these lyrics. Reddit is suing Anthropic, alleging it scraped Reddit without a license. Anthropic disputes it. No ruling yet.`

### The end card (`overlays/cards.json`)
7. **BotDefense:** "July 2023: BotDefense's volunteers shut it down, blaming the API changes and Reddit's treatment of moderators and developers. Their shutdown post put its ban list at 144,926 accounts." (BotDefense; Ars Technica)
8. **New, after the Google line:** "Mar 2024: Reddit goes public. It lets some users and moderators buy shares at the offering price." (CNBC) and "May 2024: Reddit announces a data partnership with OpenAI." (OpenAI)
9. **The lawsuit:** "June 2025: Reddit sues Anthropic, alleging it scraped Reddit without a license, kept accessing the site after saying it had stopped, and used posts users had deleted. Anthropic disputes the claims. In September 2026 a San Francisco judge lets the contract and unfair-competition claims proceed; there is no ruling on the merits." (TechCrunch; Bloomberg Law)
10. **The conflict-of-interest note:** "...and AI companies buying user data is this song's subject. Reddit says its lockdowns since 2024 target AI companies that scrape without paying, as it alleges Anthropic did. Reviewed by Gemini and ChatGPT; changes logged."
11. **The interventions count:** recounted from `log/human_interventions.md` at render time.

The "Since then" page grows from 6 to 8 lines. Its page time, and the card's 42 s, need checking against the card music.

### The video's description (draft at release)
12. The full disclosure, adapted from ChatGPT's: who made what; the lawsuit's status at release; that Claude drafting the lyrics doesn't establish what Claude was trained on; that Suno's training data is its own open question; and that this is satire, with the facts documented separately.
13. A note on the "blackmail" line: what Huffman said on the June 7 call, Selig's recording, and the employee's apology on it.
14. The gravestones with their sources (already a release check).

### Declined, with reasons
- **"Fifteen years" (ChatGPT):** the API is from 2008.
- **The literal readings of "the whole lot", "by the terabyte" and "every answer… is training data" (ChatGPT):** read as satire, and the end card gives the documented deals.
- **Gemini's ticker rewrite and its "as of Jan 2023" label:** the January date isn't established (see §1).
- **Gemini's lawsuit list including unjust enrichment:** wrong (§1).
- **ChatGPT's longer headstone wordings** (Pushshift, r/Blind, search engines, Wayback, the API, logged-out): the short ones check out, and the stones have little room.
- **"NEW MANAGEMENT" on the ticker:** the Hook 2 "under new management" running gag, not a claim about Reddit's leadership.
- **ChatGPT's "Log in to continue" qualifier:** it's the video's staged future, which the end card dates.
- **Gemini's suggested disclosure "Unlike Google and OpenAI, Anthropic didn't buy a Reddit license":** stated as fact, it's Reddit's allegation. Fix 10 attributes it.
