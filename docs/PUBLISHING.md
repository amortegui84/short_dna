# Publishing: from a finished cut to YouTube Shorts, Instagram Reels and TikTok

| Network | Route | Why this route |
|---|---|---|
| YouTube Shorts | Zapier MCP (YouTube actions + YouTube API requests) | free plan; private upload, then the AI label and public |
| Instagram Reels | Zapier MCP (Instagram for Business + Graph API requests) | free plan; Zapier's own Publish Video times out, the Graph API route does not |
| TikTok (**main route since 2026-11-18**) | TikTok Studio in the person's own Chrome, driven by Claude in Chrome (Part C) | no middleman and no quota: the account's own session and TikTok's own scheduler (up to 10 days ahead) |
| TikTok (fallback) | PostWire MCP (`postwire-mcp`) | Zapier has no TikTok action; PostWire is an audited TikTok app (public, private or draft, with TikTok's AI label), but its free plan is 10 posts a month and the video passes through a third party |

PostWire can also post to YouTube, Instagram, Facebook, LinkedIn, X, Bluesky and Mastodon. On its free plan (10 posts a
month, 2 networks per post) it is only a TikTok fallback. Zapier covers YouTube and Instagram. A brand that publishes
every day (docs/AUTOPILOT.md) uses Part C for TikTok.

The app's **Publish** view follows this guide. Part A is done once per brand (accounts and links). Part B is done for every
episode.

**Proven on 2026-11-06:** Cult Pixel Tapes 01–03 went live on all three networks this way: YouTube Shorts on
@cult_pixel, Instagram Reels on Cult_Pixel and TikTok on @cult_pixel, each with the AI label. The links and the copy are in
`brands/cult_pixel/posts.md` (local), and each episode's `publicado.json` holds its ids.

## Quick reference: one episode on the three networks
| # | What | Tool / call | Who | Cost |
|---|---|---|---|---|
| 1 | Check the final cut (QC, props popping in or out of hands) | `qc.json`, a contact sheet | Claude | — |
| 2 | Publish copy, ~50 MB | `python engine/publicar.py <project>` | Claude or the app | — |
| 3 | Title, captions (long for YouTube and Instagram, short for TikTok), hashtags, tags | brand's `posts.md` | Claude writes, the person reads | — |
| 4 | Direct download link | `python tools/publish_release.py --repo <brand>_media <file>` | the person (first time) | — |
| 5 | YouTube private + AI label | Zapier `upload_video`, then `PUT videos?part=status` with `containsSyntheticMedia` | Claude | 4 Zapier tasks |
| 6 | Review | YouTube Studio → Content → Shorts (brand channel selected) | the person | — |
| 7 | YouTube public | the same `PUT` with `privacyStatus: public` | Claude, after the OK | 2 tasks |
| 8 | Instagram Reel | Graph API: `POST /media` → wait ~4 min for `FINISHED` → `POST /media_publish` | Claude, after the OK | 6 tasks |
| 9 | TikTok | PostWire `post_to_social` with `PUBLIC_TO_EVERYONE`, `ai_generated: true` and an idempotency key; TikTok reviews it before it shows | Claude, after the OK | 1 of 10 PostWire posts |
| 10 | Record | `publicado.json` (+ the links in `posts.md`) | Claude | — |

On the free plans that is about 12 Zapier tasks (out of ~100 a month) and 1 PostWire post (out of 10) per episode. The
limit is PostWire: about 10 episodes a month on TikTok. A private TikTok test costs one more post, so skip it once the
route is trusted.

Rules that hold throughout:
- People create their own accounts and type their own logins. Claude never types passwords, codes or personal data into a site.
- YouTube uploads go **private first**. The person reviews them in YouTube Studio and only then are they made public.
- Instagram has no private mode, so nothing is posted there without an explicit "publish" from the person.
- Every video with AI-generated people or reconstructions carries the AI label (YouTube `containsSyntheticMedia`) and a
  line in the caption saying what is AI and what is real.

## Part A: connect once per brand

### A1. A YouTube channel for the brand
YouTube does not use Instagram or Facebook. It needs a **Google account**, and the channel lives inside it.
1. Sign in to youtube.com with the Google account that will own the channel. A separate Gmail just for the brand keeps it
   apart from personal mail.
2. Open the profile photo → **Settings** → **Add or manage your channels** (or go to `youtube.com/channel_switcher`) →
   **Create a channel**. Give it the brand's name. This makes a **brand channel**: it has its own name, doesn't show the
   person's name, and others can be given access later without sharing a password.
3. In **Customize channel → Basic info**, set the handle (e.g. `@cult_pixel`), the description, avatar and banner.
4. Optional but recommended: verify the channel with a phone at `youtube.com/verify`. It is required for custom
   thumbnails.
5. Switch between the personal and the brand channel with **Switch account** in the profile menu. A private video only
   shows up in YouTube Studio while that channel is selected.

### A2. An Instagram account Zapier can publish to
Instagram only allows publishing through its API to a **Business** account linked to a **Facebook Page**. Creator and
personal accounts are not supported.
1. In the Instagram app: **Settings → Account type and tools → Switch to professional account → Business**.
2. Link it to a Facebook Page that the person administers (Meta Business Suite or the Page's settings → Linked accounts →
   Instagram).

### A3. Zapier (the bridge Claude uses to post)
Zapier's free plan gives ~100 tasks a month, and every action Claude runs through it costs 2 tasks. One episode on both
networks costs about 10 tasks (upload, AI label, make public, Instagram create/check/publish).
1. Create a Zapier account at zapier.com (the person signs up).
2. Add the **Zapier MCP** connector to the Claude account (claude.ai → Settings → Connectors → Zapier) and sign in there.
3. In a Claude session, ask Claude to enable these Zapier actions. It does this with `discover_zapier_actions` and
   `enable_zapier_action`:
   - **YouTube** (`YouTubeV4CLIAPI`): Upload Video, Update Video Thumbnail, Add Video to Playlist, Find Video, and the
     API request actions.
   - **Instagram for Business** (`InstagramBusinessCLIAPI`): Publish Video, Publish Photo(s), New Media, and the API
     request actions.
4. Claude then gives one sign-in link per app (`manage_zapier_connections`). The person opens each one:
   - **YouTube:** choose the Google account, and when Google asks which channel, choose the **brand channel**, not the
     personal one.
   - **Instagram:** sign in with Facebook and allow the Page and the Instagram Business account.
5. Claude checks both connections and sets them as defaults (`list_zapier_connections`, then `manage_zapier_connections`
   with `default_connection_id`). It also confirms that the right accounts are connected:
   - YouTube: `GET https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true` must return the brand channel.
   - Instagram: the "Instagram Account to Use" list of Publish Video must show the brand's account. Write its id in
     `brand.json` → `publicar.instagram_id`.

### A4. TikTok through PostWire
1. The person creates the brand's TikTok account in the TikTok app and signs up at postwire.io with Google or email.
   The free plan covers 10 posts a month, 1 brand and 2 networks per post.
2. In PostWire → **Accounts**, connect TikTok. TikTok's own sign-in screen opens; the person logs in with the
   **brand's** TikTok and allows it.
3. In PostWire → **API & MCP**, copy the API key (`pw_live_...`). Treat it like a password: don't paste it in chats or
   commit it. If it leaks, create a new key there and revoke the old one.
4. Put it in the `.env` named by `config/local.json` → `env_file`, as `POSTWIRE_API_KEY=...` (template:
   `config/.env.example`). The app's Claude gets the `postwire` server from `config/local.json` → `mcp`, and the app
   passes it only the keys listed in its `env_keys`:
   ```json
   "postwire": { "command": "npx", "args": ["-y", "postwire-mcp@0.4.0"], "env_keys": ["POSTWIRE_API_KEY"] }
   ```
   For Claude Code outside the app, register it for your user (the key stays in `~/.claude.json`, never in the repo):
   ```
   claude mcp add --scope user postwire -e POSTWIRE_API_KEY=<key> -- npx -y postwire-mcp@0.4.0
   ```
   The version is pinned on purpose. 0.4.0 was read before use: a thin bridge to `https://postwire.io/api/mcp` that runs
   no commands and reads no files. Read a new version before raising the pin.
5. Check it: `GET https://postwire.io/api/me` (header `Authorization: Bearer <key>`), or the MCP tool `my_account`, must
   list the TikTok handle under `connections`. Write it in `brand.json` → `publicar.tiktok`.

### A5. A place the videos can be downloaded from
Zapier works in the cloud, so it needs a **direct download link** to each video, not a file on this PC.
- **Default: a GitHub release.** `tools/publish_release.py` creates a public repo `<your GitHub user>/<brand>_media` and a
  release `tapes`, uploads the files, and prints one direct link per file. It uses the GitHub login git already has
  (`git credential fill`) and never prints the token. The person runs it in their own terminal the first time, because it
  reads a credential and creates a public repository:
  ```
  python tools/publish_release.py --repo cult_pixel_media brands/cult_pixel/proyectos/ep01_gateway/ep01_gateway_pub.mp4
  ```
- **Claude runs it (proven 2026-11-06):** when Windows keeps several GitHub accounts, Git Credential Manager opens a
  picker window that a non-interactive terminal cannot answer; name the account: `--user <github user>` (Cult Pixel:
  `amortegui84`). The script never prints the token.
- **Unattended (Claude runs it every episode):** git's login lives in the person's own session, so Claude's terminal
  cannot read it. Create a GitHub fine-grained token (github.com › Settings › Developer settings › Fine-grained tokens):
  only the repository `<brand>_media`, permissions *Contents* and *Administration* read/write, an expiry date. Paste it
  yourself as `GITHUB_TOKEN=...` in the `.env` named by `config/local.json` › `env_file`. The script prefers it and never
  prints it.
- **Alternative: Google Drive.** Shared as "Anyone with the link". For large files Drive can answer with a "can't scan
  for viruses" page instead of the video, and then the upload fails. Test with a private YouTube upload first.

## Part B: every episode

1. **Final cut checked.** QC passed (`qc.json` ok), and someone watched the whole cut. Look out for objects that appear or
   vanish in the narrator's hands: a generated clip can invent props. The fix is one line in the clip's `accion` ("hands
   empty the whole time, never hold or reveal any object"), then regenerate only that clip
   (move `clips/Lxx.mp4` and `mates/Lxx.mov` aside, then `factory.py run <brand>/<slug> --only clips|mates|montaje|ae|render|qc --force`).
2. **Publish copy.** `python engine/publicar.py <project folder>` (or the **Make publish copy** button) writes
   `<slug>_pub.mp4`: H.264 high, CRF 21, at most 6 Mbps, AAC 160k, faststart, about 50 MB for 80 s. The 150 MB master
   is too big for the platforms' URL fetchers.
3. **Copy.** Write the post per episode (the format is in `brands/cult_pixel/posts.md`):
   - a title with the hook, under 100 characters, ending in `#shorts`;
   - a caption: a two-line story hook, the twist, the two-option comment question, the narrator's sign-off;
   - sources, and an AI line ("Narrator and reconstructions are AI-generated. The documents are real.");
   - 12–15 hashtags, niche first and broad last;
   - YouTube tags.
4. **Link.** Run `tools/publish_release.py` with the `_pub.mp4` files. Check each link answers 200 and the sizes match the
   local files.
5. **YouTube, private.** Zapier `upload_video` with `privacy_status: private`, `category_id: 24` (Entertainment),
   `made_for_kids: false`, `notify_subscribers: false`, language `en`, title, description and tags. Then set the AI label:
   `PUT https://www.googleapis.com/youtube/v3/videos?part=status` with `{"id": ..., "status": {"privacyStatus": "private",
   "selfDeclaredMadeForKids": false, "embeddable": true, "license": "youtube", "publicStatsViewable": true,
   "containsSyntheticMedia": true}}`. A `PUT` replaces the whole `status`, so send every field.
6. **Review.** The person opens YouTube Studio (with the brand channel selected) → Content → Shorts and watches it.
7. **YouTube, public.** The same `PUT` with `"privacyStatus": "public"`.
8. **Instagram Reel.** Zapier's *Publish Video* gives up after 180 s while Meta is still processing the video, so use the
   Graph API in three steps through the Instagram "API request" actions:
   1. `POST https://graph.facebook.com/v21.0/<instagram_id>/media` with `{"media_type": "REELS", "share_to_feed": true,
      "video_url": "<release link>", "caption": "..."}`. It returns a container id.
   2. Wait about 4 minutes, then `GET https://graph.facebook.com/v21.0/?ids=<container ids>&fields=status_code`. Continue
      when every container says `FINISHED`.
   3. `POST https://graph.facebook.com/v21.0/<instagram_id>/media_publish?creation_id=<container id>` for each one, in
      episode order. The last one published shows first on the grid.
   4. Read the permalinks: `GET https://graph.facebook.com/v21.0/?ids=<media ids>&fields=permalink`.
9. **TikTok.** Through PostWire (`post_to_social`, or `POST https://postwire.io/api/post`):
   ```json
   {"platforms": ["tiktok"], "text": "<caption>", "video_url": "<release link>",
    "options": {"tiktok": {"privacy_level": "SELF_ONLY", "ai_generated": true, "upload_method": "max"}},
    "idempotency_key": "<brand>-<slug>-tiktok"}
   ```
   - `SELF_ONLY` (only you) is the review step; `PUBLIC_TO_EVERYONE` once approved. `as_draft: true` sends it to the
     TikTok inbox instead, so the person can add a trending sound and post it from the app.
   - `ai_generated: true` adds TikTok's AI label.
   - The `idempotency_key` keeps a retry from posting twice.
   - Check it with `get_post_status` (`platform`, `id`). `publish_complete` with no public id means it is private, as
     intended.
   - TikTok captions are shorter than YouTube's: the hook in one line, the comment question, the AI line, and 8–10
     hashtags.
   - A private TikTok can't be made public through the API: post it again with `PUBLIC_TO_EVERYONE` and a new
     idempotency key, then delete the private one in the app. Each try counts as a post on the free plan.
10. **Record it.** Write `publicado.json` in the project folder (`{"youtube": {"id", "url", "privacy"}, "instagram":
   {"id", "url"}, "tiktok": {"id", "privacy"}, "video_url", "date"}`). The Publish view and the Projects gallery read it.

## What can go wrong
| Symptom | Cause | Fix |
|---|---|---|
| Nothing shows on YouTube after the upload | The videos are private, or YouTube is showing the personal channel | Switch account to the brand channel → YouTube Studio → Content |
| Zapier uploads to the wrong channel | The Google account has several channels and the personal one was chosen at sign-in | Reconnect YouTube in Zapier and choose the brand channel; check with `channels?mine=true` |
| Instagram account missing from "Instagram Account to Use" | The account is Creator or personal, or it isn't linked to a Page the person administers | Switch to Business and link the Page (A2), then reconnect |
| `Video is still processing` from Publish Video | Meta's processing takes longer than Zapier waits | Use the three-step Graph API route (B8) |
| Upload fails with an HTML or virus-scan error | The link is a Drive page, not the file | Use the GitHub release, or a direct-download link |
| Claude can't run `publish_release.py` | The permission system blocks reading a git credential and creating a public repo | The person runs it in their terminal, or approves it when the app asks |
| PostWire answers `no_api_key` | `POSTWIRE_API_KEY` is missing from the `.env` (or the user MCP config) | Add it (A4) and restart the app |
| TikTok post `publish_complete` but no link | It went out as `SELF_ONLY`: only the account sees it | Expected for the test. For the real post, send it again as `PUBLIC_TO_EVERYONE` |
| PostWire refuses a post with a monthly limit error | Free plan: 10 posts a month | Wait for the reset (1st of the month) or upgrade |
| Zapier stops working mid-month | The ~100 free tasks are used up | Wait for the reset or upgrade; each episode costs ~10 tasks |

## Part C: TikTok Studio in the person's own Chrome (no middleman)
**Proven 2026-11-18:** 20 Cult Pixel posts (Nov 19–28, two a day) scheduled in TikTok Studio this way, after PostWire's
free month ran out. Nothing passes through a third party: Claude drives the Chrome where the person is already signed in.

### C0. Connect once (each person who will schedule TikTok)
Nothing here needs an API key, a developer app or a paid plan. The video goes from this PC to TikTok through the
person's own browser session; no other company receives it.
1. **The brand's TikTok account.** Created in the TikTok app by the person who owns it. Settings → Account → switch to
   a **Business** or **Creator** account (both give TikTok Studio on desktop). Two-step verification on.
2. **Chrome on the PC that holds the videos.** Sign in at `tiktok.com` with the brand's account, typed by the person
   (or by QR from the phone). Open `tiktok.com/tiktokstudio/upload` once and accept any terms yourself. If the team
   shares one Chrome, use a Chrome profile just for the brand.
3. **Claude in Chrome.** Install the Claude extension from the Chrome Web Store in that same profile, sign in to Claude
   and allow it on `tiktok.com`. In Claude Code, the `claude-in-chrome` tools must show as connected
   (`tabs_context_mcp` lists the Chrome window).
4. **Test with one post scheduled for later.** Ask Claude to schedule one kit post (steps below), then open TikTok
   Studio → Posts and check its date, time, caption and the AI-generated label. Delete it there if it was only a test.
5. **Record it** in `brand.json` → `publicar.tiktok_via: "tiktok_studio_chrome"`, and tell whoever runs the kits which
   Chrome profile holds the session.

Who does what: the person signs in, accepts terms and answers any code, CAPTCHA or "is this you?" check; Claude only
uploads the file, writes the caption, sets the schedule and the AI label, and never touches the login, the password
or the account settings. If TikTok logs the session out, Claude stops and asks the person to sign in again.

Account health first: on 2026-11-19 every @cult_pixel post showed 0 views in Studio, with no violation notice. Before
scheduling a new batch, open TikTok Studio → **Account status** (and the inbox's System notifications) and check that
recent posts get views. Schedule a few days at a time (two posts a day at most), not weeks in bulk.

What it needs:
- The person opens `tiktok.com/tiktokstudio/upload` in **their own Chrome**, signed in to the brand's account, with the
  **Claude in Chrome** extension connected. Claude never types the login.
- A kit: `brands/<brand>/tiktok_kit/build_kit.py` writes `kit.json` (date, time, video, caption per post),
  `KIT_TIKTOK.html` (the same as cards with copy buttons, for doing it by hand) and `videos/` (the files in posting order,
  hard links to the -14 LUFS cuts).

Why the file goes in as parts: Claude in Chrome's `file_upload` takes at most ~10 MB per call, and TikTok's "Select video"
button opens a native file picker that never appears while Chrome is driven remotely. TikTok's page also blocks fetches
from localhost and GitHub, so the page cannot download the file itself.

Per post:
1. `python tools/browser_upload_chunks.py <video>` splits it into ≤9 MB parts and prints three page scripts.
2. Run script 1 (`javascript_tool`): it adds a hidden input labelled `kitin chunk input`.
3. `find "kitin chunk input"`, then `file_upload` each part into it, **one part per call**.
4. Run script 3: it joins the parts in order into one `File` and hands it to TikTok's own `<input type=file>` with a
   `DataTransfer` and a `change` event. TikTok then uploads it as if it had been picked.
5. Paste the caption into the description box (clear TikTok's prefilled file name first).
6. Under **When to post**, choose **Schedule**, set the date in the calendar and the time (hour and minute lists: click
   until the wanted value is selected; the minute list recentres after each click).
7. **Show more** → turn on **AI-generated content** (TikTok's AI label, mandatory for the brand).
8. Press **Schedule**, then check the post in TikTok Studio → Posts with its date and time.

Pitfalls:
- `ref_N` ids change after each upload: run `find` again before clicking.
- Videos over 60 s get an extra line ("Duet and Stitch not available") under **Show more**, which moves the AI
  toggle down; locate it with `find` and check it is on (zoom) before pressing Schedule.
- Quote cards: keep them off faces. A card's `y` sets its height; a long credit line is cut at the right edge, so keep
  `autor` short.
- Several `file_upload` calls in one `browser_batch` fail on the 10 MB total; send them one by one.
- Scheduling reaches 10 days ahead at most; schedule the rest later.
- If the person closes Chrome or the extension disconnects, the step in flight is lost: check the Posts list before
  retrying, so nothing is posted twice.

## Part D: a batch on autopilot (approved cuts only)
The whole daily cycle (night production, approval, publishing) is in docs/AUTOPILOT.md. This part is only the posting task.
For a run of episodes, a scheduled task posts one a day without anyone at the PC
(`cult-pixel-reacts-daily`, every day at 19:00):
- `proyectos/_gen/cola_publicacion.json` is the queue: one row per day with `fecha`, `slug`, `aprobado`, `youtube`,
  `instagram`. **Only the person flips `aprobado` to true**, after watching the cut. The task never posts an unapproved row.
- Step 1: today's approved row goes out as an Instagram Reel (Graph API, B8). Before posting it lists recent media, so a
  retry never posts twice.
- Step 2: tomorrow's approved row is uploaded to YouTube **private with `publishAt`** (15:00 UTC = 10:00 Bogota) and the
  AI label. YouTube makes it public on its own at that time.
- Step 3: it fills the row's ids, appends to `posts.md` and reports in 2–4 lines.
- TikTok is not in this task: approved cuts are scheduled in TikTok Studio a few days at a time (Part C).
- Best hours for this channel (Bogota time, from its own history): YouTube 10:00, Instagram ~19:00, TikTok 13:00 and
  20:00.

## Going direct: no middleman per network
Zapier and PostWire are only bridges. Every network can be reached without them; the trade-off is a one-time setup that
only the person can do (their accounts, their consent screens).

| Network | Direct route | One-time setup (the person) | Limits | Status |
|---|---|---|---|---|
| YouTube | YouTube Data API v3 with an own OAuth client: `videos.insert` (resumable upload of the local file, no public link needed), `status.publishAt`, `containsSyntheticMedia` | Google Cloud project → enable YouTube Data API → OAuth client "Desktop app" → sign in once with the brand channel; the refresh token stays in the `.env` | 10,000 units a day; an upload costs ~1,600 (≈6 a day). Videos from an unverified app may be locked private until the app passes Google's audit: test one first | not built yet |
| YouTube (browser) | YouTube Studio in the person's Chrome, same method as Part C (it has its own scheduler) | none | Studio's layout changes; slower | works in principle, not tried |
| Instagram | Instagram Graph API with an own Meta app (same calls as B8) and a long-lived token | Meta developer app → Instagram Graph API → token for the Business account | 50 API posts a day; still needs a public video URL | not built yet (today through Zapier) |
| Instagram (browser) | Meta Business Suite in Chrome (it schedules Reels) | none | layout changes | not tried |
| TikTok | TikTok Studio in Chrome (Part C) | none | 10 days ahead | **in use** |
| TikTok (API) | Content Posting API | a TikTok developer app; until TikTok audits it, posts can only be private | audit takes weeks | not worth it now |

Rule of thumb: an official API is the steadier route (no screen to break); the browser route needs no app or audit and
uses the person's own session, so it is the fallback when an API is closed or capped.
