# Release fact check (a Claude research subagent, 2026-11-03, the day before release)

Research only; the subagent opened every source it cites. Recorded verbatim below. The agent then checked the key new
source itself: the Reddit passages in Anthropic's S-1/A (SEC, filed 2026-11-02) read as quoted. What changed in
response is listed at the end.

---

## Release fact check of Read-Only's end card and description (as of 2026-11-03)

Nothing on the end card is wrong or out of date. One stated fact on the description's headstone list is wrong (ReddPlanet), and two optional changes would make the lawsuit wording more precise. No files were edited.

The best new source is Anthropic's own S-1/A, filed with the SEC on **Nov 2, 2026**: https://www.sec.gov/Archives/edgar/data/2130357/000162828026068676/anthropicpbc-sx1ax1.htm. I downloaded and read it. Its legal-proceedings note says:

> "In June 2025, Reddit, Inc. filed suit against the Company in California state court alleging various claims, including breach of contract and trespass to chattels… In September 2026, the state court narrowed the case to Reddit's breach of contract, interference with contract, and unfair competition claims. The Company disputes the allegations…"

Its risk factors add: "The case was remanded to state court on March 30, 2026. The lawsuit is currently pending." As of Nov 2, Anthropic's own filing reports:
- the case still pending;
- no settlement or license;
- no trial date;
- no ruling on the merits;
- only the three surviving claims.

That implies the unjust enrichment and trespass claims had not been reinstated after the Oct 16 deadline. No press report of an amended complaint exists either, though I couldn't open the state docket (PlainSite refused the connection).

| # | Verdict | Wording suggestion | Sources opened (date) |
|---|---|---|---|
| 1 | Unchanged | — | TechCrunch, Jun 8 2023 (Selig: "50 million requests costs $12,000"; "20 million US dollars per year"). The April 2023 announcement was confirmed at M6 (TechCrunch, Apr 18 2023). |
| 2 | Unchanged | — | TechCrunch, Jun 12 2023 ("Over 8,000 subreddits went dark or read-only"; "will last for 48 hours") |
| 3 | Unchanged | — | lemmy.world mirror of the Jul 5 2023 r/BotDefense post (quote "now stands at an incredible 144,926 accounts"; reasons include Reddit's hostility toward moderators and developers). Ars Technica is blocked for me. |
| 4 | Unchanged, with a note for #5 | — | Reuters via The Star, Feb 22 2024 ("about $60 million per year, according to one of the sources"); Variety via Yahoo, Feb 22 2024 ("at the IPO price"); CNBC, Feb 22 2024; TechCrunch, Mar 11 2024 (8% of shares, 75,000 eligible); Engadget, May 16 2024 (OpenAI partnership; openai.com returned 403). |
| 5 | Unchanged, but watch it | Optional: "Google, which pays Reddit for its data, stays…". This is accurate as of July 2024, and no other engine has a deal. | 9to5Mac, Jul 25 2024; PPC Land, Sep 2 2026 (SerpApi's Aug 28 2026 counterclaims still describe Bing, DDG, Mojeek and Qwant as locked out; no other engine has a deal); CNBC, Jul 22 2026 (the WSJ reported the $60M Google deal "ending soon"; Reddit weighed cutting off Google's AI access); CNBC, Oct 29 2026 (Huffman: still "in negotiations" with Google). Google still has fresh results and no lapse has been reported. If the deal lapses before release, "pays Reddit" would be stale. |
| 6 | Unchanged (confirmed by Anthropic's Nov 2 filing) | — | Anthropic S-1/A, Nov 2 2026 (above); Mashable via Yahoo, Sep 19 2026; Bloomberg Law, Sep 21 2026 (Judge Harold E. Kahn, "largely denied"). No amended complaint, settlement, Reddit–Anthropic license, appeal, trial date or new ruling turned up in any search. One caution: the only source for the IPO-filing context is a ZeroHedge item I couldn't date. |
| 7 | Unchanged | — | Engadget, Aug 11 2025 ("will only be able to crawl Reddit's homepage"; AI companies scraping via Wayback). No reversal found. Forbes (Apr 14 2026) and a 2026 guide still treat the block as in place. |
| 8 | Unchanged | — | Decrypt, Oct 1 2026; PPC Land, Oct 4 2026 (Nov 13 RSS end; no new requests from Oct 31; Jan 12 2027; "March 2027" with no day). I found no delay or reversal. Wikipedia wrongly says the API closes "November 2026", so don't use it. RSS ends 9 days after release. |
| 9 | Unchanged | — | TechCrunch, Oct 29 2026 (tests "in select markets outside the U.S. in the fourth quarter"; "doesn't yet have a timeline" worldwide; no update note); TechCrunch, Nov 3 2026 ("will make the transition gradually, initially in markets outside the U.S."); TechTimes, Oct 30 2026; PPC Land, Oct 29 2026 (Huffman: "a primarily logged-in experience"). No report says tests have started, no markets are named, there is no US date, and nothing has been walked back. |
| Desc: lawsuit | Unchanged; two optional precision fixes | (a) Reuters says Anthropic "accessed or tried to access" Reddit "more than 100,000 times". (b) The deleted-posts point is an allegation that Anthropic doesn't honour deletions through Reddit's Compliance API; NatLawReview summarises it as "including deleted posts". Both are acceptable if written as allegations. | Reuters via The Star, Jun 5 2025 (filed in San Francisco Superior Court; 100,000); The Decoder, Jun 4 2025; NatLawReview, Jun 17 2025; S-1/A for the three surviving claims |
| Desc: headstones | Apollo, rif, Sync, BaconReader, Pushshift, r/IAmA and r/Blind unchanged. **ReddPlanet is wrong (see below).** | Fix ReddPlanet as below. On r/IAmA, keep the July 2023 framing of mods stopping celebrity coordination (M8 fix 3). | AndroidHeadlines, Jun 9 2023 (Apollo June 30; rif and Sync "end of this month"); 9to5Google, Jul 1 2023 (BaconReader killed); Droid Life, Jun 30 2023; Wikipedia, "Reddit API controversy" (BaconReader June 30 per The Verge; r/Blind "could no longer moderate on mobile", Jul 1 2023 report); TheWrap, Jul 3 2023 (r/IAmA); r/modnews May 1 2023 via search snippets only (Pushshift) |

**ReddPlanet:** the only sources I opened say it was shutting down "at the end of this month" (AndroidHeadlines, Jun 9 2023). Wikipedia lists it only as announcing a shutdown around Jun 8 2023, not among the apps that went dark June 30. Use "June 2023", or leave its date as it was announced.

### Must change before release
1. **ReddPlanet's headstone date in the description:** change "June 30 2023" to "June 2023", or leave its date as it was announced. Not on the end card.

Everything else can ship as written. There are three soft items:
- **Lawsuit wording (optional):** "accessed or tried to access", and describing the deleted-posts claim as an allegation about honouring deletions, are slightly more exact.
- **#5 Google deal:** if a lapse is reported before tomorrow, revisit "pays".
- **The lawsuit:** with Anthropic mid-IPO, anything could be filed after Nov 2; a last check of news on the morning of release costs little.

### Sources list for the description (each opened by me)
- **Selig/Apollo pricing:** https://techcrunch.com/2023/06/08/popular-third-party-reddit-app-apollo-is-shutting-down-as-a-result-of-reddits-new-api-pricing/ (Jun 8 2023)
- **Blackout:** https://techcrunch.com/2023/06/12/reddit-blackout-8000-subreddits-went-dark-protest-api/ (Jun 12 2023)
- **"Blackmail"/"threatened" and the call recording:** https://techcrunch.com/2023/06/09/reddit-ceo-doubles-down-on-attack-on-apollo-developer-in-drama-filled-ama/ (Jun 9 2023). Covers the rep's "threat" reading and later apology, Huffman's "threatening", and "recording and leaking a private phone call". The "blackmail" wording appears in this piece only as a user's question.
- **BotDefense:** https://lemmy.world/comment/942001 (mirror of r/BotDefense 14riw76, Jul 5 2023). Ars Technica is blocked for me (it 400s in search), so I couldn't open it; the M8 citation went through Slashdot.
- **Google deal:** https://www.thestar.com.my/tech/tech-news/2024/02/22/exclusive-reddit-in-ai-content-licensing-deal-with-google-sources-say (Reuters copy, Feb 22 2024)
- **IPO directed share program:** https://www.cnbc.com/2024/02/22/reddit-will-let-users-buy-its-ipo-but-warns-that-they-could-make-the-stock-riskier.html (Feb 22 2024). It doesn't state the price; for "at the IPO price" use https://ca.news.yahoo.com/reddit-discloses-finances-ipo-filing-213842947.html (Variety, Feb 22 2024).
- **OpenAI partnership:** https://www.engadget.com/openai-strikes-deal-to-put-reddit-posts-in-chatgpt-224133045.html (May 16 2024). The openai.com post returned 403.
- **robots.txt:** https://9to5mac.com/2024/07/25/reddit-blocking-search-engines/ (Jul 25 2024)
- **Lawsuit filing:** https://www.thestar.com.my/tech/tech-news/2025/06/05/reddit-sues-ai-startup-anthropic-for-allegedly-using-data-without-permission (Reuters, Jun 5 2025: SF Superior Court, 100,000+). TechCrunch https://techcrunch.com/2025/06/04/reddit-sues-anthropic-for-allegedly-not-paying-for-training-data/ (Jun 4 2025) has the 100,000 figure but not the court or deleted posts. The Decoder https://the-decoder.com/reddit-sues-anthropic-for-scraping-site-content-to-train-claude/ (Jun 4 2025) covers deleted posts and the Compliance API.
- **Sept 2026 ruling:** https://www.yahoo.com/news/us/articles/judge-allows-most-reddits-lawsuit-155921694.html (Mashable, Sep 19 2026). Bloomberg Law https://news.bloomberglaw.com/ip-law/anthropic-loses-bid-to-dismiss-reddit-ai-scraping-privacy-suit (Sep 21 2026) is paywalled past the first lines.
- **Case status today:** Anthropic S-1/A, https://www.sec.gov/Archives/edgar/data/2130357/000162828026068676/anthropicpbc-sx1ax1.htm (Nov 2 2026)
- **Wayback block:** https://www.engadget.com/social-media/reddit-is-restricting-its-availability-to-the-internet-archives-wayback-machine-170035482.html (Aug 11 2025). The Nieman Lab piece I could open (https://www.niemanlab.org/2025/08/it-just-got-easier-to-make-an-archival-copy-of-that-website-youre-digging-into/, Aug 13 2025) mentions the block but not the homepage exception or the AI reason, so Engadget is the better cite.
- **RSS/API:** https://decrypt.co/379892/reddit-killing-rss-feeds-public-api-access-ai-scrapers (Oct 1 2026); https://ppc.land/reddit-to-halt-public-data-api-access-in-march-2027-as-14-000-apps-register/ (Oct 4 2026)
- **Logged-in:** https://techcrunch.com/2026/10/29/as-search-traffic-dries-up-reddit-announces-its-shifting-to-a-logged-in-experience/ (Oct 29 2026)

Blocked or unreachable for me: Reddit itself, Ars Technica, Reuters direct, openai.com, Courthouse News, Daily Journal, TechRepublic, PlainSite and Techdirt. The Pushshift line rests on search snippets of the r/modnews post, not an opened page.

---

## What changed in response (the agent)

- **The end card and both cuts:** no change. Every line holds as of 2026-11-03.
- **The description (`deliverables/description.md`, `METADATA.md`):** ReddPlanet's headstone is dated "June 2023" with "announced its shutdown". The lawsuit paragraph says "accessed or tried to access the site more than 100,000 times" and describes the deleted-posts claim as an allegation that Anthropic didn't honour deletions. It adds the case's status as of Anthropic's November 2 filing, and a SOURCES list with these URLs.
- **The Reference Guide** (the human's doc, which the README links to): its lines that this check and the M6/M8 checks found wrong are corrected (see the production log).
- **Morning of release:** search once more for news on the lawsuit and on the Google deal before publishing.
