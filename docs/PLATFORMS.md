# Platforms: content strategy per social network

Researched 2026-11-05. Data lives in `library/platforms/<platform>.json` (one file per network) and `library/hooks.json`
(hook catalogue, retention patterns, CTAs, comment questions). This guide says how the app should use them. Anything
marked **unverified** comes from third-party sources only, or was not re-checked this session: confirm it in the app or
the platform's help center before relying on it. Platforms change these rules often; re-check every ~6 months.

## 1. How the app chooses

### Platform first, then length
1. The user picks one primary platform (it drives length, hook and CTA) and any number of secondary ones (they get an
   adapted cut from the same master, section 4).
2. Length comes from the goal, inside the platform's `specs.ideal_s`:

| Goal | TikTok | Reels | Shorts | Facebook | LinkedIn |
|---|---|---|---|---|---|
| Reach test / new topic | 20-45 s | 20-45 s | 20-40 s | 30-60 s | 30-45 s |
| Educational episode (default) | 61-90 s | 45-90 s | 40-60 s | 60-90 s | 45-90 s |
| Monetised / deep | 61-180 s | up to 180 s | 60-180 s* | 90 s+ | up to 120 s |

All ranges are heuristics, since no platform publishes an ideal length. The hard facts behind them:
- TikTok's Creator Rewards Program only pays for original videos **over 1 minute**.
- YouTube: Shorts can run up to 3 minutes, but *a Short **over 1 minute** with any active Content ID claim is blocked
  worldwide until the claim is resolved*. Only go past 60 s with own or Audio Library music.
- Instagram caps Reels at 3 minutes. Facebook has had no cap since June 2025, when every video became a reel.
  LinkedIn allows up to 15 minutes.
- Length is not a stated ranking factor anywhere. Watch time and full watches are, so the shortest cut that delivers the
  payoff wins.

The `artist_short` template (55-70 s) fits Shorts, Reels and Facebook as is. For TikTok it should be stretched to at
least 61 s if monetisation matters. For LinkedIn it should be cut to one idea (30-60 s).

### Hook
Pick from `hooks_preferidos` of the primary platform, matched to the episode. Use `curiosity_gap`, `secret_reveal` or
`find_it_challenge` for a detail, `cold_open` or `story_character` for a story, `myth_bust` or `contrarian` for a myth,
and `numbered_list` for a list. Rules:
- The spoken line, the on-screen text and the first 5 words of the caption are three versions of **one** promise.
- A visual change in the first second (`visual_pattern_interrupt`) goes under every spoken hook.
- Never start with a greeting or the channel name. `series_callback` only goes alongside a content hook.
- Measure with YouTube's *Viewed vs. swiped away* and TikTok's retention. Change the hook line on the next episode
  before changing the topic.

### Retention structure (all platforms)
1. Hook and open loop (L01): a specific, closable question.
2. Context fast (L02).
3. Mini payoffs every 8-12 s, with a re-hook at 35-50% (template L05, "the turn").
4. Main payoff at 70-85% of the runtime, before any CTA.
5. Close: the two-option question, a CTA after the payoff, and an optional loop back into the first line.

Note on evidence: open loops are justified by information-gap theory (curiosity needs a closable gap). The often-quoted
Zeigarnik "unfinished tasks are remembered better" effect did not hold up in a 2025 meta-analysis.

### CTA
- One CTA, after the payoff, in the last 2-3 s.
- Per platform: TikTok gets "part 2" (only if it exists). Instagram gets a **send** prompt (sends per reach is a named
  signal). YouTube points to the Related video link. Facebook and LinkedIn get an opinion or advice question.
- Never "like/comment/share if..." or "comment YES". Facebook demotes engagement bait, including when it is spoken in
  the audio. Asking for advice or recommendations is explicitly fine.
- The comment question is a balanced two-option **opinion** question ("Genius or fraud: which was he?"), never
  "comment 1 or 2".

## 2. What each algorithm rewards (platform statements first)

| | Strongest stated signals | Demoted |
|---|---|---|
| TikTok | Interactions (likes, shares, follows, comments). A full watch of a longer video weighs more than weak signals. Then captions, sounds, hashtags. Device and locale weigh least. Follower count and past hits are **not** direct factors. | Unlabeled realistic AI (may be removed or restricted). Misleading content even when labeled. |
| Instagram Reels | Predicted reshare, full watch, like, audio-page visit. In January 2025 the head of Instagram named watch time, likes per reach and **sends per reach** (secondary sources). | Low-res, watermarked, muted, bordered, mostly-text reels, and reposts. Aggregators lose reach to originals (2024, extended 2026). |
| YouTube Shorts | Personalised by viewer behaviour and satisfaction. A system separate from long-form. Public views count every start or replay (since March 2025); revenue uses *engaged views*. | Re-uploads and aggregators (2026 originality update). Mass-produced or repetitive "inauthentic content" loses YPP monetisation (since July 2025, channel-wide). |
| Facebook Reels | Same personalisation; the 2025 merge did not change recommendations. | Engagement bait (posts, comments, audio). Pages that repeat it get Page-level demotion. |
| LinkedIn | No official video ranking statement found (unverified). Video uploads up 36% year over year, and there is a vertical video feed. | unverified |

**For a templated, AI-presented series the biggest risk is YouTube's inauthentic-content policy and Meta's
originality push, not the hook.** Every episode needs its own script, argument, sources and visuals. The same voice and
character are fine; near-identical episodes are not.

## 3. Specs and safe areas (1080x1920, 30 fps)

| Platform | Max | Top | Bottom | Left | Right | Caption text | Hashtags |
|---|---|---|---|---|---|---|---|
| TikTok | 10 min safe (up to 60 for some accounts, unverified) | 130 | 380 | 60 | 140 | 4000 (in app) | 3-5 |
| Instagram Reels | 3 min | 270 | 670 | 65 | 65 | 2200 (unverified) | max 5 (since Dec 2025) |
| YouTube Shorts | 3 min | 288 | 672 | 48 | 192 | title 100 / description 5000 (unverified) | 2-3 |
| Facebook Reels | none | 270 | 670 | 65 | 65 | very long; first line matters | 1-3 |
| LinkedIn | 15 min | 240 | 480 | 60 | 140 | 3000 (unverified) | 0-3 |

All safe-area pixel values are **unverified**. Platforms publish safe zones for ads only, so these numbers come from
third-party templates; LinkedIn's are an estimate. **Master safe box** (the union of all of them): x 65-888,
y 288-1248, which is 823x960 px. Keep subtitles, names and key text inside it and every platform is covered.

**Conflict with the current style:** `library/styles/collage_v10c.json` puts subtitles at `y_subtitulos: 1400`. That is
inside the bottom UI band on YouTube Shorts (title, channel, Subscribe from y≈1248) and on Instagram/Facebook (caption
from y≈1250). On TikTok it is clear (the band starts at y≈1540). Either move the subtitles to ~1150-1230 for a
cross-platform master, or render per platform. Check this in the app preview before changing the style.

Covers: TikTok and Instagram grids crop the cover toward 3:4 (unverified), so cover text goes in the centre 1080x1440
band. YouTube lets you pick a Shorts frame in the app; custom uploads were reported rolling out in 2025-2026
(unverified). Make the hook frame double as the cover.

## 4. Repurposing one 9:16 master

Render one clean master (no watermark, no burned platform UI, subtitles inside the master safe box), then:

| Change | TikTok | Instagram Reels | YouTube Shorts | Facebook Reels | LinkedIn |
|---|---|---|---|---|---|
| Length | ≥61 s if monetising | tightest cut, ≤180 s | ≤60 s unless music is own/Audio Library | as is, or a longer story cut | 30-60 s, one idea |
| Hook | keep; caption starts with keyword | keep; first caption line = hook | title = searchable phrase + hook | keep | professional angle (`modern_parallel`, `contrarian`) |
| CTA | part 2 / opinion question | send prompt | Related video link | opinion or advice question, no bait | perspective question |
| Text | caption 1-2 sentences + 3-5 tags | hook line + ≤5 tags + alt text | title + description with sources + 2-3 tags | first line hook | insight above video, sources below |
| Music | business account: Commercial Music Library or own | business: Meta Sound Collection or own; IG audio is not cleared off-platform | Audio Library or own | as Instagram | own only |
| Subtitles | above y=1540 | above y=1250 | above y=1248 | above y=1250 | centre band, everything readable muted |
| Watermarks | none from other apps | none (demoted) | none (originality) | none | none |
| AI label | toggle | toggle | Studio: AI use = Yes | toggle | say it in the text |
| Extra | reply-with-video to comments | trial reel to test the hook; carousel twin for saves | Related video link to long-form; SRT upload | | optional 4:5 crop for the main feed |

Always export each platform's file from the master project, never re-upload a file downloaded from another platform.
Downloaded files carry watermarks and lose quality, and both get demoted.

## 5. AI disclosure (synthetic presenter and voice)

| Platform | Required when | How | If you don't |
|---|---|---|---|
| YouTube | Realistic content made or meaningfully altered with AI: real people doing or saying things they didn't, altered real events or places, realistic scenes that didn't happen, music as the main focus. Not required for clearly unrealistic content, minor edits, captions, or AI used for scripts, ideas or thumbnails. | Studio upload: altered/synthetic content = Yes. The label shows in the description, or in the player for photoreal or AI music. YouTube may auto-label from C2PA. | Forced label, removal, YPP suspension. Disclosing does **not** reduce reach or monetisation (YouTube's statement). |
| TikTok | AI-generated or significantly edited content showing realistic-looking scenes or people. | "AI-generated content" toggle. Auto-label from C2PA Content Credentials (since May 2024). Invisible watermark on TikTok-tool content. | May be removed, restricted, or labeled by TikTok. |
| Instagram / Facebook | Organic photorealistic video or realistic-sounding audio that was digitally created or altered. | AI label toggle ("AI info"). Auto-label from industry signals. AI-edited-only content shows the label in the menu. | Meta "may apply penalties" (unspecified). Fact-checked altered content is shown lower. |
| LinkedIn | No creator toggle found (unverified). Deceptive content is against policy. | State it in the post text; keep C2PA metadata (LinkedIn is reported to show Content Credentials, unverified). | unverified |

**App rule:** a photoreal generated presenter with a synthetic voice is a realistic-looking person who does not exist,
so **always** turn on the AI label on every platform and say it in the description ("Presenter and voice are
AI-generated; facts and artworks are real, sources below"). Keep C2PA or Content Credentials metadata if the generators
write it, since it triggers the label automatically. Labels never make a misleading claim acceptable, and each fact
still needs its source (already a repo rule).

Also unverified: the EU AI Act's transparency duties for deepfakes (Art. 50) are scheduled to apply from August 2026.
Check the current status if the channel targets the EU.

## 6. Content strategy for an educational faceless or avatar channel

**Pillars** (3-4, rotate weekly):
1. *Hidden details*: one artwork, one detail. Hooks: `curiosity_gap`, `find_it_challenge`.
2. *Artist files*: biographies (the `artist_short` template). Hooks: `story_character`, `cold_open`.
3. *Myths and debates*: attribution, restoration, famous myths. Hooks: `myth_bust`, `contrarian`, `versus`.
4. *Art and science/money*: pigments, X-rays, prices, forgeries. Hooks: `bold_number`, `secret_reveal`, `stakes`. The
   pigment and X-ray side may fit TikTok's STEM feed (unverified for art topics).

**Series formats.** Use a numbered series name in the title or on-screen text ("Hidden details #12"), a playlist or
collection per series, and the same opening sound and title card for recognition. Never the same script shape twice in
a row: vary the hook type and the structure (list, story, versus) inside a series, which also covers the
inauthentic-content risk.

**Cadence.** No platform publishes a required cadence; consistency beats volume. Heuristics, unverified:
- TikTok: 4-7 per week. TikTok's often-quoted "1-4 per day" figure has no primary page.
- Instagram: about 3 per week. The creator FAQ reportedly says the fastest-growing creators post 10+ reels a month.
- YouTube: 3-5 Shorts per week, plus a long-form when available.
- LinkedIn: 1-2 per week.

For this pipeline, one produced episode per weekday cross-posted, plus cheap reply videos on TikTok, is the realistic
ceiling. Publish times come from each platform's audience-activity insights after 2-3 weeks of data.

**Feedback loop.** After 7 days, record per episode and platform: viewed vs swiped (YouTube), average watch % (all),
sends and saves (Instagram), comments. Keep the hook that wins per platform as the default `hooks_preferidos[0]` for
the next pillar episode.

## 7. Conflicts between sources (as found 2026-11-05)
- **YouTube 3-minute Shorts date:** the help article says 15 Oct 2024 for standard channels and 8 Dec 2025 for Official
  Artist Channels. Some regional copies show only one of the dates.
- **Instagram max length:** 3 min (most sources and Meta coverage of Facebook) versus one 2026 claim of 20 min
  (unverified).
- **Instagram hashtag cap:** 5 per post since Dec 2025, but sources disagree on whether comments count; an earlier test
  used 3.
- **TikTok max upload:** 10 / 30 / 60 minutes across guides; caption limit 4000 in the app versus 2200 via the API.
- **Safe areas:** TikTok bottom 250-380 px and right 100-140 px depending on the template. YouTube 288/672/48/192 versus
  a percentage set (~380 px bottom, ~200 px right). Meta 14%/35%/6% from a single secondary source versus checkers
  with a 280 px bottom.
- **Instagram's third signal:** "sends per reach" versus "shares per reach" in the coverage.
- **YouTube Shorts custom thumbnails:** available (desktop, rolling out) versus frame-only, depending on the guide.
- **LinkedIn vertical feed:** mobile only versus mobile and desktop.
- **Business-account music on Instagram:** restricted to the Meta Sound Collection, versus creators reporting full
  access; Instagram says "certain" business accounts.
- **Open loops:** marketing sources lean on the Zeigarnik effect, which the 2025 meta-analysis did not support.

## Sources
Platform (primary):
- https://support.google.com/youtube/answer/15424877?hl=en (three-minute Shorts, Content ID over 1 minute, music limits)
- https://support.google.com/youtube/answer/14328491?hl=en (YouTube altered/synthetic content disclosure)
- https://support.google.com/youtube/thread/470890423/prioritizing-original-content-on-shorts?hl=en (Shorts originality)
- https://blog.youtube/creator-and-artist-stories/youtube-related-videos-traffic-guide/ (Related video link)
- https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you (TikTok recommendation factors)
- https://www.tiktok.com/community-guidelines/en/integrity-authenticity (TikTok AI labeling rule)
- https://ads.tiktok.com/business/en-US/blog/9-creative-tips-to-drive-auction-ad-performance (3 s / 6 s hook guidance, 63% figure)
- https://newsroom.tiktok.com/tiktok-launches-dedicated-feed-for-stem-content-across-europe (STEM feed)
- https://about.instagram.com/blog/announcements/instagram-ranking-explained (Reels ranking and demotions)
- https://creators.instagram.com/blog/best-practices-for-creators (Best Practices hub)
- https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/ (Meta AI labels)
- https://about.fb.com/news/2017/12/news-feed-fyi-fighting-engagement-bait-on-facebook/ (engagement bait)
- https://www.facebook.com/business/help/980593475366490 (Meta Stories/Reels safe zone, ads)
- https://www.linkedin.com/help/linkedin/answer/a548372 (LinkedIn video limits)

Press and analyses (secondary):
- https://ppc.land/youtube-changes-how-shorts-views-are-counted-from-march-31/
- https://www.searchenginejournal.com/youtube-targets-mass-produced-content-in-monetization-update/550337/
- https://www.searchenginejournal.com/youtube-shorts-algorithm-explained-in-qa-format/459513
- https://www.digitalmusicnews.com/2026/10/02/youtube-shorts-prioritize-original-content/
- https://www.tubefilter.com/2025/06/17/meta-facebook-reels-all-videos-update/
- https://www.businesstoday.in/technology/news/story/no-more-hashtag-stuffing-instagram-limits-hashtag-usage-to-just-5-per-reel-and-post-507444-2025-12-19
- https://petapixel.com/2024/12/13/instagram-launches-trial-reels-so-you-can-test-content-with-non-followers
- https://petapixel.com/2026/04/30/new-instagram-policies-target-reposted-content/
- https://www.engadget.com/instagrams-algorithm-overhaul-will-reward-original-content-and-penalize-aggregators-130018977.html
- https://siliconangle.com/2024/05/09/tiktok-announces-new-tools-automatically-flag-ai-generated-content/
- https://www.socialmediatoday.com/news/tiktok-announces-revamped-creator-rewards-program-to-incentivize-longer-u/710639/
- https://techcrunch.com/2025/02/04/linkedin-amps-up-vertical-video-tools-as-uploads-jump-36
- https://www.socialync.io/tools/safe-zones/youtube-shorts and https://www.trymypost.com/blog/tiktok-ad-specs-2026-safe-zones (safe-area templates)

Research:
- https://doi.org/10.1037/0033-2909.116.1.75 (Loewenstein 1994, information-gap theory; DOI not opened this session)
- https://ideas.repec.org/a/pal/palcom/v12y2025i1d10.1057_s41599-025-05000-w.html (2025 Zeigarnik/Ovsiankina meta-analysis)

Each JSON file lists its own full source set in `fuentes`.
