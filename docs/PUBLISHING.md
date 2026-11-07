# Publishing: from a finished cut to YouTube Shorts, Instagram Reels and TikTok

| Network | Route | Why this route |
|---|---|---|
| YouTube Shorts | Zapier MCP (YouTube actions + YouTube API requests) | free plan; private upload, then the AI label and public |
| Instagram Reels | Zapier MCP (Instagram for Business + Graph API requests) | free plan; Zapier's own Publish Video times out, the Graph API route does not |
| TikTok | PostWire MCP (`postwire-mcp`) | Zapier has no TikTok action; PostWire is an audited TikTok app, so it can post publicly, privately or as a draft, with TikTok's AI label |

PostWire can also post to YouTube, Instagram, Facebook, LinkedIn, X, Bluesky and Mastodon. On its free plan (10 posts a
month, 2 networks per post) it is kept for TikTok. Zapier covers YouTube and Instagram.

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
