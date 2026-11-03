# Read-Only: independent fact-check and conflict-of-interest audit

Model: GPT-6 Audit date: 2 November 2026 Scope: Historical accuracy, current-status claims, misleading implications, reputational risks and the financial/editorial conflict involving Anthropic.

I will distinguish between four things that are easy to conflate:

- Accurate: supported by evidence, allowing for reasonable rounding.
- Inaccurate: contradicted by evidence.
- Misleading: based on something real but omits context or implies something stronger than the evidence supports.
- Can't verify: insufficient independently checkable evidence. This is not the same as false.

One important limitation: a claim about what Reddit announced is not necessarily proof that the announced policy has actually taken effect. I will also distinguish allegations in litigation from judicial findings.

## 1. Executive findings

Several core historical figures check outThe central 2023 story is substantially grounded in documented events. In particular:

- Apollo's quoted API price of $12,000 per 50 million requests is supported by contemporaneous reporting. The $20 million annual figure was Apollo developer Christian Selig's projection, not an invoice or a charge actually paid.
  TechCrunch
  +2
- More than 8,000 subreddits participated in the June 2023 protest.
  TechCrunch
- BotDefense reported 144,926 banned accounts and announced that it was ceasing operations.
  Ars Technica
- Google's reported Reddit data deal was approximately $60 million annually, according to sources cited by Reuters. It was not a publicly disclosed, independently audited contract value.
  reuters.com
- Reddit did restrict the Internet Archive's access to most individual Reddit pages in August 2025.
  Nieman Journalism Lab
  +1
- The September 2026 litigation development is real: Anthropic's attempt to dismiss important state-law claims was largely unsuccessful. That is not a finding that Anthropic committed the alleged wrongdoing.
  news.bloomberglaw.com
  +1

Three particularly important corrections1. BotDefense was not simply switched off by Reddit. Its volunteer maintainers announced that they were stopping operations in response to Reddit's changes and what they described as antagonistic treatment. The distinction matters.
2. The Anthropic lawsuit has not been decided on its merits. Saying that a judge allowed claims to proceed is accurate; presenting that as proof of scraping or liability is not.
3. The AI-authorship conflict is under-addressed. The piece criticizes Reddit for monetizing user-generated material while giving Anthropic and the AI production process very little equivalent scrutiny.

The video is not simply anti-Reddit propaganda: there are legitimate, documented grievances about API pricing, accessibility and the loss of community tools. But its strongest accusations sometimes turn disputed causation or commercial arrangements into more definite claims than the evidence supports.

## 2. Fact-check table

The following is a claim-by-claim audit. Where multiple closely related words make one factual assertion, I group them into a single row rather than pretending that every adjective is independently verifiable.

### A. Verse 1 — Apollo and the API changes

| Claim | Location | Verdict | Evidence / explanation |
| --- | --- | --- | --- |
| Reddit had been open to third-party developers for 15 years | Verse 1 | Misleading | Reddit launched in 2005. The API and third-party development history are real, but the 15-year figure is not an accurate description of the entire period through 2023. |
| Reddit introduced API charges | Verse 1 | Accurate | Reddit announced the new charging policy in 2023. <br>TechCrunch |
| $12,000 per 50 million calls | Verse 1 | Accurate | This was the price Selig said Reddit quoted him. <br>TechCrunch |
| $0.24 per 1,000 calls | Verse 1 and screen | Accurate | The arithmetic is correct: $12,000 ÷ 50,000,000 × 1,000 = $0.24. |
| Thirty days to pack up | Verse 1 and countdown | Accurate, with qualification | The new pricing was announced at the beginning of June, with the new terms scheduled for July 1. The countdown is a reasonable shorthand for the transition period. |
| Apollo would cost $20 million a year | Verse 1 and counter | Accurate as an attributed estimate; misleading if presented as an actual bill | Selig calculated this from Apollo's reported usage and the quoted API price. It was a projection, not a sum Reddit invoiced or collected. <br>TechCrunch<br>+1 |
| The price amounted to eviction | Verse 1 | Fair satire | An evaluative metaphor, not a factual allegation. |
| Reddit accused Selig of threatening/blackmailing it | Verse 1 | Accurate in substance | Huffman publicly characterized Selig's conduct as threatening. The distinction between that characterization and what was actually said is important. <br>TechCrunch |
| Selig recorded the call | Verse 1 and hype-man exchange | Accurate | Contemporary reporting describes the recording and Selig's publication of it. <br>TechCrunch |
| The recording contains no threats | Verse 1 | Misleading / partly subjective | Selig disputed Reddit's characterization and published the recording. The assertion that no threat can be found is an interpretation of the recording, not a neutral legal finding. |
| The recording was played to the internet | Verse 1 | Accurate | The recording was made public and discussed during the dispute. <br>TechCrunch |

Important arithmetic distinction: the $20 million counter is defensible as a visualization of Selig's estimate. It should not look like a running total of money Reddit actually received. The distinction is especially important because the visual appears to calculate a definitive liability from a projected usage figure.

### B. Hook 1 and Verse 2 — the blackout and Reddit leadership

| Claim | Location | Verdict | Evidence / explanation |
| --- | --- | --- | --- |
| More than 8,000 communities went dark | Hook 1 | Accurate | TechCrunch reported more than 8,000 participating subreddits on June 12, 2023. <br>TechCrunch |
| The protest lasted 48 hours | Hook 1 | Accurate as the initial protest period | The protest was organized for June 12–14. Some communities remained private or restricted for longer. |
| Reddit's traffic dipped and recovered | Verse 2 and traffic graph | Can't fully verify as shown | The video needs to distinguish overall site traffic, individual community traffic and the CEO's description of the protest's business impact. A graph without a cited dataset is not independently auditable. |
| Reddit replaced moderators who refused to reopen | Verse 2 | Accurate in substance, but needs context | Reddit did remove or replace some moderators during the aftermath of the protest. This was not a universal replacement of every moderator who participated. |
| The CEO held an AMA | Verse 2 | Accurate | Huffman held an AMA during the June 2023 controversy. <br>TechCrunch<br>+1 |
| The AMA went badly | Verse 2 | Fair satire | The negative reception is a reasonable interpretation, not a measurable factual claim. |
| Reddit said bots were a reason for API changes | Verse 2 | Accurate | Reddit explicitly connected its policy changes to protecting its data and limiting large-scale automated access. <br>Upvoted<br>+1 |
| Reddit sold access to AI companies | Verse 2 | Accurate in substance | Reddit entered commercial data-licensing arrangements, including the reported Google deal. |
| Reddit sold the entire corpus to AI companies | Verse 2, "sold 'em the whole lot" | Misleading | Commercial licensing does not establish that every post, every comment or the entire archive was sold without restrictions. It also doesn't establish that every AI company received access. |

The CEO verse is intentionally voiced as an arrogant caricature. Lines such as "I barely broke a sweat" are clearly performative. The more serious issue is the implied sequence: Reddit opposed bots, then sold its users' content to AI companies. That is a legitimate criticism of its commercial policy, but it should not imply that Reddit's anti-scraping policies and its licensed data deals are necessarily identical forms of access.

### C. Hook 2, Verse 3 and the IPO

| Claim | Location | Verdict | Evidence / explanation |
| --- | --- | --- | --- |
| Reddit's third-party apps went dark | Hook 2 | Accurate | Several major clients ceased normal operation following the API changes. <br>Android Authority<br>+1 |
| Reddit eliminated all third-party apps | Hook 2, implied | Misleading if taken literally | Some clients continued under subscriptions, exemptions or special arrangements. |
| BotDefense was the guard dog | Hook 2 | Accurate metaphor | It was a volunteer anti-spam system. <br>Ars Technica |
| Reddit shut down the guard dog | Hook 2 | Misleading | BotDefense's maintainers decided to cease operations. Reddit's API changes and treatment of developers were important factors, but the bot was not simply switched off by Reddit. |
| Reddit sold data to search companies | Verse 3 | Accurate in substance | Google licensing is documented; the partnership with OpenAI was announced in May 2024. <br>Reuters<br>+1 |
| Reddit sold data by the terabyte | Verse 3 | Can't verify | I found evidence of licensing arrangements, but not evidence establishing that the relevant deals were priced or delivered by terabyte. |
| Google deal was worth $60 million a year | Verse 3 | Accurate with attribution | Reuters reported this estimate from a source familiar with the agreement. It was not a publicly confirmed payment figure. <br>reuters.com |
| A chatbot company subsequently made a deal | Verse 3 | Accurate | Reddit and OpenAI announced their partnership on May 16, 2024. <br>OpenAI |
| Every free answer and helpful comment became training data | Verse 3 | Misleading | Reddit content was licensed for AI-related uses, but the available evidence does not establish that every comment, every answer or every individual user's contribution was included in a particular model's training dataset. |
| Every moderator's rules and work became part of the product | Verse 3 | Partly accurate, partly rhetorical | Moderation activity and community-generated content contribute to Reddit's value. The lyric does not establish that all moderator-created material was included in licensed datasets. |
| Users are the product and the payroll | Verse 3 | Fair satire | This is an economic criticism of a platform business model, not a literal accounting statement. |
| Reddit's IPO happened | Verse 3 and IPO visuals | Accurate | Reddit priced its IPO on March 20, 2024, and began trading on March 21. <br>investor.redditinc.com<br>+1 |
| The stock went up at the opening | Verse 3 and ticker | Accurate | Shares opened above the $34 IPO price, at approximately $47. <br>CBS News<br>+1 |
| Reddit sold everything | Verse 3, "you sold it all" | Misleading | Reddit floated shares in an IPO. It did not sell the entire company. The IPO included both newly issued shares and shares sold by existing shareholders. |
| Users' content was not included in the IPO | Ticker | Misleading if read literally | The stock offering was a sale of equity, not a transfer of individual content ownership. User contributions were not individually sold as IPO shares, but the content and community are important components of the company's commercial value. |

The strongest factual distinction in this section is between selling access to content and selling ownership of content. Reddit's licensing agreements are real, but they do not prove that users' posts were individually sold or that every contribution was included in AI training.

### D. The eulogy — BotDefense

| Claim | Location | Verdict | Evidence / explanation |
| --- | --- | --- | --- |
| BotDefense was a volunteer project | Eulogy | Accurate | Ars Technica described it as a volunteer project established in 2019. <br>Ars Technica |
| It identified and banned spam accounts | Eulogy | Accurate | This was its central function. |
| It had banned 144,926 accounts | Eulogy and counter | Accurate, as a reported historical count | BotDefense's creator supplied this figure to Ars Technica. It should be attributed to BotDefense rather than presented as an independently audited Reddit statistic. <br>Ars Technica |
| It worked without payment | Eulogy | Accurate in the volunteer sense | The project was volunteer-operated. That does not prove nobody ever incurred expenses or received indirect benefits. |
| It checked reposts and kept threads clean | Eulogy | Broadly accurate | Consistent with the described moderation functions, though the exact extent of each task is not independently quantified. |
| Reddit shut it down | Eulogy | Misleading | The maintainers announced their own cessation of operations. Reddit's actions were part of the stated reason, not the same as a direct shutdown order. |
| Reddit lost a useful anti-spam resource | Eulogy | Accurate | The bot had helped moderate several very large communities. <br>Ars Technica |
| Reddit consequently had no bot protection | Eulogy, implied | Inaccurate if inferred | BotDefense was one volunteer tool, not Reddit's entire anti-spam infrastructure. |

This is the most important correction to the 2023 narrative after the $20 million qualification. The existing lyric says:

> You shut down the one that you'd need.

It makes a compelling dramatic line, but it attributes direct agency to Reddit. The evidence supports a more nuanced causal chain: Reddit changed the API and its relationship with third-party developers; BotDefense's maintainers then decided to stop operating.

Because the words are final, the correction belongs on screen.

### E. Verse 4 — the AI singer

| Claim | Location | Verdict | Evidence / explanation |
| --- | --- | --- | --- |
| The singer is an AI | Verse 4 | Accurate as the stated fictional premise | The credits describe AI-generated production. I cannot independently inspect the actual recording's generation provenance. |
| It learned to flow from comment chains | Verse 4 | Can't verify | The actual training data and training history of the particular models used are not established by the credits. |
| It learned to rhyme from every line | Verse 4 | Misleading if interpreted as a literal training claim | This is a poetic description, not evidence that every Reddit comment or every line of text was used. |
| Reddit shut down the bot that hunted bots | Verse 4 | Misleading | The BotDefense distinction above applies. |
| Reddit sold bots the feed | Verse 4 | Misleading | There are documented AI licensing deals, but this wording implies that the buyer category, scope and data access are uniform. |
| The singer asks viewers to judge whether it is a good or bad bot | Verse 4 | Fair satire | A rhetorical invitation, not a verifiable claim. |
| "Allegedly" | Verse 4 | Fair satire, but insufficient legal qualification | It does not clarify which allegations are contested, by whom, or what has actually been decided. |

There is an especially important distinction here: the video identifies Claude as the lyric drafter, but that does not establish that Claude was trained on Reddit data. Reddit's lawsuit alleges that Anthropic scraped Reddit material for training; Anthropic disputes the allegations. Those are not interchangeable propositions.

AP News

+1

Verse 4 also makes the AI singer appear to be a neutral observer that has simply learned from the material humans supplied. That is a convenient narrative for the company whose model drafted the lyrics.

The singer admits that it learned from comment chains, but it does not acknowledge the possibility that the AI industry has benefited from precisely the sort of unpaid public contributions that the song condemns Reddit for monetizing.

That is a genuine conflict-of-interest weakness, not just an artistic choice.

## 3. On-screen text: individual checks

### Countdown and API price

| Screen claim | Verdict | Reason |
| --- | --- | --- |
| DAYS LEFT, 30 to 0 | Accurate | Reasonable representation of the notice period. |
| $0.24 / 1,000 calls | Accurate | Correct arithmetic from the reported quote. |
| Total climbing to $20 million | Accurate with qualification | It represents Selig's projected annual cost, not actual money paid to Reddit. |
| BLACKMAIL | Misleading without context | It reproduces Reddit's characterization of the dispute, not an established finding that Selig committed blackmail. |

### Blackout and commercial imagery

| Screen claim | Verdict | Reason |
| --- | --- | --- |
| 48-hour blackout sign | Accurate | The initial protest was organized around 48 hours. |
| SEARCH and CHAT trucks | Accurate as symbolism | Google and OpenAI both announced commercial partnerships with Reddit. |
| COMMENTS 2005–2023 crates | Misleading | It suggests all comments from those years were transferred or sold. That is not established. |
| ARCHIVE van turned away | Accurate symbolism, with qualification | Reddit restricted the Internet Archive's access to most post-level pages in August 2025. |
| IPO bell | Accurate | Reddit's IPO and first trading day are documented. |
| IPO ▲ OPENING BELL ▲ UP UP UP | Accurate | The stock opened above the IPO price. |
| NEW MANAGEMENT | Can't verify as a factual change | It could be interpreted as a change of leadership. The IPO itself did not establish that Reddit's management changed. |
| USER CONTENT NOT INCLUDED | Misleading | User contributions were not individually included as shares, but they were central to the company's business and valuation. |

### Account counter, headstones and login screen

| Screen claim | Verdict | Reason |
| --- | --- | --- |
| ACCOUNTS BANNED: 144,926 | Accurate | Matches BotDefense's reported historical figure. |
| BotDefense epitaph: worked for free | Accurate with qualification | It was a volunteer project. |
| Apollo, June 30, 2023 | Accurate | Apollo announced its closure for that date. <br>MacRumors |
| rif is fun, June 30, 2023 | Accurate | The normal app service ended around the API transition. <br>9to5Google |
| Sync for Reddit, June 30, 2023 | Accurate | Its normal third-party Reddit service ended around the same transition. <br>Android Authority |
| BaconReader, June 30, 2023 | Accurate | The app discontinued normal Reddit operation. <br>Android Authority |
| Boost for Reddit, June 30, 2023 | Accurate | Normal operation ended around the transition. <br>9to5Google |
| ReddPlanet, June 30, 2023 | Broadly accurate | The app's developer announced closure following the API changes. <br>Ars Technica |
| Pushshift, May 2023 | Misleading | Reddit stopped Pushshift's access to new API data on May 1, 2023. This did not mean every historical archive or every service immediately ceased to exist. <br>Reddit<br>+1 |
| BotDefense, 2023 | Accurate | It announced cessation in July 2023. <br>Ars Technica |
| r/IAmA celebrity AMAs, July 2023 | Can't verify | I could not establish that celebrity AMAs as a category ended in July 2023. The protest and API changes affected community participation, but that does not prove the death of celebrity AMAs. |
| Mobile moderation on r/Blind, July 2023 | Misleading | Blind moderators reported that accessibility regressions made mobile moderation extremely difficult. That is not proof that all mobile moderation ceased. <br>Reddit |
| Search engines other than Google, July 2024 | Misleading | Non-Google engines lost many recent Reddit results, but the statement that every other major search engine was completely excluded is too broad. <br>Ars Technica<br>+1 |
| Wayback Machine archiving, August 2025 | Accurate with qualification | Reddit restricted access to most post details, comments and profiles, while allowing limited homepage archiving. <br>Nieman Journalism Lab<br>+1 |
| RSS feeds, November 13, 2026 | Accurate as an announced future date | Reddit officially announced this date. As of November 2, the shutdown has not happened yet. <br>October 8, 2026 – Reddit Help<br>+1 |
| Public Data API, 2008–March 2027 | Partly can't verify | March 2027 is the announced end of remaining public access. I could not establish 2008 as the precise beginning of the API in the sense implied by the tombstone. <br>October 8, 2026 – Reddit Help<br>+1 |
| Logged-out Reddit, 2005– | Misleading if read as already ended | Reddit has announced a move toward a primarily logged-in experience, but has not announced that all logged-out access has already ended. <br>TechCrunch<br>+1 |
| Log in to continue | Misleading without a location/date qualifier | As of November 2, the announced transition is being tested in selected markets outside the US; it is not yet a universal login requirement. <br>TechCrunch<br>+1 |

### The fictional reader app notice

> It stopped working on June 30, 2023, when access to the API ended.

Needs qualificationThe date is reasonable for an app that depended on the old API terms and could not continue under the new pricing. But it is not true that all Reddit API access ended on June 30. The changes affected different applications in different ways, and some continued operating under exemptions or revised commercial arrangements.

The wording also risks suggesting that Reddit's entire API was switched off on that date. It wasn't.

## 4. End-card historical timeline

This is where I would be particularly careful: the end card presents itself as a factual reference, so it should meet a higher standard than the lyrics.

### 2023

| End-card claim | Verdict | Evidence / correction |
| --- | --- | --- |
| April 2023: Reddit announces API charges | Accurate | Reddit announced the policy change in April. <br>Upvoted<br>+1 |
| May 31: Apollo developer reveals $12,000 per 50 million calls | Accurate | Contemporaneous reporting supports the date and amount. <br>TechCrunch<br>+1 |
| $20 million a year estimate | Accurate | Must remain attributed to Selig. <br>TechCrunch |
| June 12: more than 8,000 subreddits go private or read-only | Accurate | Supported by TechCrunch's contemporary reporting. <br>TechCrunch |
| 48-hour blackout | Accurate | This was the initial protest period; some communities continued afterwards. |
| July 2023: BotDefense shuts down | Misleading wording | It ceased operations by decision of its volunteer maintainers. <br>Ars Technica |
| BotDefense ban list: 144,926 | Accurate | Reported by its creator. <br>Ars Technica |

### Since then

| End-card claim | Verdict | Evidence / correction |
| --- | --- | --- |
| February 2024: Google data licence | Accurate | Reuters reported the deal. <br>reuters.com |
| Approximately $60 million annually | Accurate with attribution | Reuters' sources gave this estimate. It was not a confirmed public contract value. |
| July 2024: Reddit's robots.txt blocks crawlers | Accurate with qualification | Reddit changed its crawling rules and blocked or restricted crawlers that would not agree to its conditions. <br>Upvoted<br>+1 |
| Google remains the only major search engine with fresh Reddit results | Misleading | Google had a significant advantage, but the wording is too absolute. Reddit said it was discussing arrangements with other search engines, and some engines could surface results through other indexing arrangements. <br>9to5Google<br>+1 |
| June 2025: Reddit sues Anthropic | Accurate | The lawsuit was filed June 4, 2025. <br>PlainSite<br>+1 |
| Reddit alleges Anthropic scraped posts without a licence | Accurate as an allegation | This is the substance of Reddit's case. Anthropic disputes the allegations. <br>AP News<br>+1 |
| September 2026: judge lets contract and unfair-competition claims proceed | Accurate, but incomplete | The September proceedings allowed important claims to continue. Other claims faced dismissal or opportunities to amend. This is a procedural decision, not a judgment that Anthropic is liable. <br>Bloomberg Law<br>+1 |
| August 2025: Reddit blocks Wayback Machine from archiving most of the site | Accurate | The restriction covered most individual pages, comments and profiles, not every possible archive capture. <br>Nieman Journalism Lab<br>+1 |
| September 30, 2026: Reddit announces RSS ends November 13 | Accurate | Confirmed by Reddit's own October help-page update. <br>October 8, 2026 – Reddit Help |
| Public API ends in March 2027 | Accurate as an announced plan | Reddit says remaining public access ends in March 2027, with earlier restrictions beginning January 12. <br>October 8, 2026 – Reddit Help<br>+1 |
| October 29, 2026: Reddit announces primarily logged-in experience | Accurate | Announced during the Q3 earnings period. <br>TechCrunch<br>+1 |
| The experience is already being imposed everywhere | Inaccurate if implied | The initial tests are planned for selected markets outside the US, with no universal rollout date announced. <br>TechCrunch |

### Credits and explanatory notes

| Claim | Verdict | Reason |
| --- | --- | --- |
| Claude drafted the lyrics | Can't independently verify | This is a creator-provided production disclosure. |
| Suno generated the music | Can't independently verify | The production method is not independently inspectable from the text supplied. |
| Claude Code, Blender, FLUX.2, LTX-2.3 and LatentSync produced the video | Can't independently verify | These are production-process disclosures, not established by the historical sources. |
| music-deslop post-filtering | Can't independently verify | I cannot inspect the production chain. |
| Only real image is the creator's March 2018 breakfast photo | Can't verify | Requires inspection of the actual video and the image's provenance. |
| Fictional block and fictional eatery | Can't verify | The disclosure is sensible, but the actual visuals would need inspection. |
| Creator interviewed at Reddit in 2018 | Can't verify | No independent corroboration established here. |
| Badge and schedule are recreations | Can't verify | Requires comparison with the original materials. |
| Hip-hop originated in a Black and Latino cultural tradition in the Bronx | Accurate | This is an important and appropriate acknowledgement of the music's cultural origins. |

## 5. Conflict-of-interest assessment

Material conflict disclosed, but not fully addressedThere are two distinct interests here.

1. Anthropic has a commercial interest in how AI companies' collection and use of public material are perceived.
2. Anthropic is itself a defendant in Reddit's lawsuit, and Claude is credited as the lyric drafter.

That makes the conflict unusually direct: the company whose product helped write the criticism is also one of the companies implicated by the criticism.

### Where the piece is unfair to Reddit

A. It equates different kinds of data access.

Reddit's API pricing, its Google and OpenAI partnerships, its restrictions on crawlers, and its lawsuit against Anthropic are related, but not identical.

The song compresses them into one accusation:

- Reddit said it wanted to protect users from bots.
- Reddit then licensed data to AI companies.
- Therefore, Reddit was simply selling the same material it claimed to protect.

There is a real basis for questioning this policy. Reddit's commercial licensing creates a legitimate question about whether users should have greater control over their contributions and compensation.

But the argument needs to acknowledge that Reddit distinguishes between authorized commercial access and unauthorized scraping. Whether that distinction adequately protects users is a separate debate.

B. It understates Reddit's anti-abuse rationale.

Reddit has argued that uncontrolled scraping creates costs and risks, including automated abuse, privacy problems and the failure to honour content deletions.

Those concerns are not invented merely because Reddit also has a commercial interest in licensing its data.

The end card should give readers enough information to understand Reddit's stated rationale, even if the song disagrees with it.

C. It blames Reddit for BotDefense's closure too directly.

This is probably the clearest factual unfairness to Reddit's staff.

BotDefense's volunteers were angry about Reddit's changes and chose to stop. That is a legitimate criticism of Reddit's relationship with its developer and moderator communities. But the lyric changes a decision made by volunteers into an act directly performed by Reddit.

D. It flattens the moderator experience.

Reddit moderators are not one homogeneous group. Some supported the protest, some opposed it, and many were concerned about losing essential tools.

The protest did involve real harm to moderation workflows, particularly for accessibility-dependent moderators. The video should avoid suggesting that all moderators had the same motivations or that every moderation tool was eliminated.

### Where the piece is too easy on Anthropic and AI companies

A. It does not meaningfully interrogate the company that wrote the lyrics.

The lyrics repeatedly condemn Reddit for monetizing public contributions, but they do not directly examine Anthropic's own use of public internet material.

The end card mentions the lawsuit, which is good, but the main creative work gives Anthropic no comparable critical treatment.

The viewer hears the AI voice reveal itself and ask whether it is a good bot or a bad bot. That is charming, but it is not accountability.

B. It treats AI training as a natural consequence of public discussion.

"I learned to flow from comment chains" makes the process sound organic, almost as if the AI singer learned by participating in a community.

There are important distinctions between:

- Reading publicly available material.
- Scraping it at scale.
- Using it to train a commercial model.
- Licensing it.
- Respecting deletion requests.
- Respecting contractual restrictions.

The lyric collapses these into a vague idea of learning from comments.

C. It leaves Suno out of the conflict discussion.

The credits say Suno generated the music. Suno is another AI company with its own data-provenance and copyright controversies.

In September 2026, Suno announced a new v6 model family it said was trained using licensed music data, while distinguishing it from earlier model generations. That is a relevant contemporary example of why AI training provenance deserves disclosure.

TechCrunch

This does not prove anything about the training data for the particular Suno model used in this video. That remains unverified.

D. It makes the AI persona the final moral commentator.

The final verse has a structural advantage: the AI gets the last word, asks the audience to judge it, and turns the discussion into a playful engagement prompt.

The human creator and the AI company remain outside that judgment.

The AI is effectively asking the audience to decide whether it is a good bot or a bad bot without giving the audience the evidence necessary to decide.

### My assessment of Verse 4

The verse is artistically effective, but ethically incomplete.

It acknowledges that the singer is artificial, but does not disclose the particular conflict between its lyric-generating model's developer and the company being criticized.

The phrase "allegedly" is not enough. It is a wink, not an explanation.

I would not remove the verse or claim that it is inherently dishonest. I would add a short, direct disclosure immediately after it or on the end card.

### Is the lawsuit line accurate and current?

Substantially accurate as of November 2, 2026The lawsuit was filed in June 2025. Reddit alleges that Anthropic used automated access to obtain Reddit content for Claude's training without authorization.

Anthropic contests the allegations.

There have been important procedural developments in 2026:

- In March, a federal court remanded the case to California state court.
  Courthouse News
- In September, Bloomberg Law reported that a federal judge had rejected Anthropic's attempt to dismiss important state-law claims on copyright-preemption grounds.
  Bloomberg Law
- A separate September 18 state-court order addressed the pleadings, allowing the breach-of-contract, interference and unfair-competition claims to proceed while sustaining objections to other claims with leave to amend.
  Trellis Law

These are not necessarily contradictory reports: they describe different procedural stages and issues.

The lawsuit line is not false, but it needs a stronger qualification. It should explicitly state that the claims are allegations, that Anthropic disputes them, and that the court has not made a final finding of liability.

Also, avoid saying that the court found Anthropic had scraped Reddit. It has not established that conclusion merely by allowing claims to proceed.

## 6. Reputational and legal risks

These are the issues I would prioritize before publication.

| Risk | Severity | Why |
| --- | --- | --- |
| "BLACKMAIL" graphic | High | Could be read as an accusation that a named real person committed a crime or misconduct. |
| "You shut down the one that you'd need" | Medium–high | Assigns direct responsibility for a volunteer project's closure. |
| "Sold 'em the whole lot" | Medium | Implies a wider transfer of content than the evidence establishes. |
| "Every answer ... is training data" | Medium–high | Makes a sweeping factual assertion about data use. |
| $20 million counter | Medium | Could be mistaken for actual revenue or an actual invoice. |
| Anthropic lawsuit presentation | High | The company that wrote the lyrics is a party to the litigation, creating an unusually direct conflict. |
| Logged-in prompt | Medium | Could suggest a universal login restriction already in effect. |
| Search-engine tombstone | Medium | Overstates the July 2024 change. |
| Pushshift tombstone | Medium | Confuses loss of new ingestion with total shutdown. |
| r/IAmA tombstone | Medium | Historical claim has not been established. |

### The blackmail exchange deserves special attention

The video refers to a real and identifiable controversy involving Reddit CEO Steve Huffman and Apollo developer Christian Selig.

The underlying facts are:

- Selig recorded his call with Reddit representatives.
- The recording was made public.
- Reddit's leadership characterized Selig's behaviour as threatening.
- Selig disputed that interpretation.
- The recording became central to the public dispute.

Contemporary reporting supports this sequence.

TechCrunch

What it does not establish is that Selig committed blackmail.

The screen flashing BLACKMAIL is especially risky because it can look like a factual label rather than a depiction of Reddit's accusation.

My recommendation is to change the screen, not the lyric.

## 7. Concrete publication fixes

These are the changes I recommend. They preserve the recording and most of the creative concept.

### Priority 1: Correct the potentially defamatory or misleading material

| Existing text | Recommended replacement |
| --- | --- |
| `BLACKMAIL` | `REDDIT'S ACCUSATION: BLACKMAIL` |
| `ACCOUNTS BANNED 144,926` | `BOTDEFENSE-REPORTED BAN LIST: 144,926` |
| `Here lies a good bot. It worked for free.` | `Here lies BotDefense. Volunteer-run. Ceased operations in July 2023.` |
| `You shut down the one that you'd need.` (supporting screen text) | `API CHANGES. VOLUNTEERS WALKED AWAY.` |
| `$20,000,000.00` | `$20,000,000.00 / PROJECTED ANNUAL API COST, PER APOLLO'S DEVELOPER` |
| `COMMENTS 2005–2023` | `REDDIT PUBLIC DISCUSSIONS / LICENSED DATA ACCESS` |
| `USER CONTENT NOT INCLUDED` | `USERS CREATED THE VALUE. USERS DIDN'T GET IPO SHARES.` |
| `NEW MANAGEMENT` | `PUBLIC COMPANY / NEW SHAREHOLDERS` |

The replacement for the BotDefense text is particularly important. It preserves the criticism without falsely suggesting Reddit directly ordered the bot to stop operating.

### Priority 2: Correct the historical tombstones

| Existing headstone | Recommended replacement |
| --- | --- |
| `Pushshift, May 2023` | `Pushshift: Reddit API ingestion stopped, May 1, 2023` |
| `r/IAmA celebrity AMAs, July 2023` | Remove unless the creator can produce a specific source documenting the claimed cessation. |
| `Mobile moderation on r/Blind, July 2023` | `r/Blind: Mobile moderation accessibility severely impaired, July 2023` |
| `Search engines other than Google, July 2024` | `Non-Google search: Recent Reddit results sharply restricted, July 2024` |
| `Wayback Machine archiving, August 2025` | `Wayback Machine: Most Reddit post pages and comments blocked, August 2025` |
| `Public Data API, 2008–March 2027` | `Reddit public Data API: Remaining access scheduled to end March 2027` |
| `Logged-out Reddit, 2005–` | `Open logged-out Reddit: Under transition, announced October 2026` |

For the login screen, use:

`LOGGED-IN EXPERIENCE: TESTING IN SELECT MARKETS`

That is more accurate than implying a universal login requirement.

### Priority 3: Correct the end card

I would replace the relevant portions of the end card with the following.

Writing

## 2023

- **April 2023:** Reddit announces plans to charge for API access.
- **May 31, 2023:** Apollo developer Christian Selig reports a proposed price of $12,000 per 50 million requests ($0.24 per 1,000).
- Selig estimates that Apollo's usage would translate to approximately $20 million annually. This is his projection, not an invoice or payment.
- **June 12–14, 2023:** More than 8,000 subreddits participate in the coordinated API protest. Some remain restricted beyond the initial 48-hour period.
- **July 2023:** Volunteer-run BotDefense announces that it is ceasing operations amid Reddit's API changes and deteriorating relations with moderators and developers. Its reported ban list stood at 144,926 accounts.

## Since then

- **February 2024:** Reuters reports that Reddit has agreed to license data to Google for AI-related purposes, with the deal estimated at approximately $60 million annually. This figure was reported by sources familiar with the agreement, not publicly confirmed as a contract value.
- **May 2024:** Reddit and OpenAI announce a data-access partnership.
- **July 2024:** Reddit changes its crawler policies. Non-Google search engines lose access to many recent Reddit results; the impact is not identical across all search engines.
- **August 2025:** Reddit restricts the Internet Archive's access to most individual posts, comments and profiles, citing unauthorized AI scraping. Limited homepage archiving remains.
- **June 4, 2025:** Reddit files suit against Anthropic, alleging unauthorized scraping of Reddit content for AI training.
- **September 2026:** Courts allow important contract and unfair-competition claims to proceed. These are procedural developments, not a finding that Anthropic is liable. Anthropic disputes Reddit's allegations.
- **September 30, 2026:** Reddit announces that RSS support will end November 13, 2026, and that remaining public Data API access is scheduled to end in March 2027.
- **October 29, 2026:** Reddit announces a transition toward a primarily logged-in experience, beginning with tests in selected markets outside the United States.

## Important qualifications

The $20 million Apollo figure is a developer's projected annual cost, not money paid to Reddit.

BotDefense ceased operations by decision of its volunteer maintainers; it was not directly shut down by Reddit.

Reddit's licensing agreements with AI companies and its restrictions on unauthorized scraping are different policies. Whether that distinction adequately protects contributors is an open question.

The Anthropic litigation concerns allegations that have not been finally adjudicated.

### Priority 4: Add a direct conflict-of-interest disclosure

This is the most important new material I would add to the description or end card.

Writing

## AI authorship and conflict-of-interest disclosure

This video was produced using generative AI tools. Claude, made by Anthropic, drafted the lyrics. Suno generated the music.

There is a material conflict of interest: Anthropic is currently being sued by Reddit over allegations that it scraped Reddit content without authorization to train its AI models. Anthropic disputes those allegations. As of November 2, 2026, the case has not produced a final finding of liability.

The video criticizes Reddit's API changes, commercial licensing of user-generated content, and treatment of third-party developers and volunteer moderators. Those criticisms should also be applied to AI companies that collect, process, license and monetize public contributions.

The fact that Claude drafted these lyrics does not establish that Claude was trained on Reddit content. The training-data provenance of the particular models used in this production has not been independently verified.

This is satire, not a neutral account of the dispute. Claims in the lyrics are not all literal factual assertions. Historical claims and legal developments are documented separately, with allegations distinguished from established findings.

I would put a shortened version on the actual end card and the full version in the description.

### Priority 5: Give Verse 4 a better ending on screen

I would retain every sung word.

However, immediately after:

> Hype man: allegedly.

Add a short silent text sequence:

## WHO TRAINED THE SINGER?

# Anthropic made Claude.

Claude drafted these lyrics.

## Reddit sued Anthropic.

Reddit alleges unauthorized scraping for AI training. Anthropic disputes the allegations.

## No final finding of liability.

Legal status checked November 2, 2026.

This changes the final effect from an AI asking the audience to judge everyone else into an AI acknowledging that its own maker is implicated.

## 8\. Final editorial verdict

Historical foundation

Generally sound

The central 2023 API controversy, blackout, Apollo pricing estimate, BotDefense count, Google licensing report and later policy changes have substantial documentary support.Precision of claims

Needs revision

The BotDefense attribution, $20 million presentation, search-engine claims, Pushshift tombstone and logged-out access claims need qualification.Fairness to Reddit

Somewhat unfair

The piece compresses complicated business decisions into a single narrative of hypocrisy and sometimes attributes decisions to Reddit that were made by volunteers.Fairness to Anthropic

Insufficient scrutiny

The company is disclosed in the credits and lawsuit note, but the AI singer's self-examination is largely theatrical. The conflict deserves more direct acknowledgement.Ready to publish

After corrections

I would not require re-recording. The identified problems can be addressed through overlays, end-card amendments and the description.

### My five non-negotiable changes

If production time is limited, I would insist on these five:

1. Change `BLACKMAIL` to `REDDIT'S ACCUSATION: BLACKMAIL`.
2. Correct the BotDefense account so it says the volunteer maintainers ceased operations.
3. Attribute the $20 million to Selig's projected annual cost.
4. Correct the logged-out Reddit, RSS and March 2027 API claims to distinguish announced future changes from completed events.
5. Add the Anthropic litigation and training-data disclosure immediately after Verse 4.

One final point: the video's cultural acknowledgement of hip-hop's Black and Latino Bronx origins is worthwhile. Keep it. The fact that the production is AI-generated does not make the artistic tradition it draws from ownerless or culturally neutral. The credits should preserve that distinction.

My overall judgment: the song has a defensible historical and satirical foundation, but its most serious editorial weakness is that it applies a much tougher standard to Reddit's monetization of user contributions than to Anthropic's and the wider AI industry's monetization of public material. Fixing the factual attribution errors and explicitly confronting that conflict would make the piece considerably more credible without sacrificing its bite.
