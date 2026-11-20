# Cool Culture Club: script requirements

Three steps added to every CCC Short, in this order: **write the script → verify facts → check length → (production) → check audio**.
A script is not done until it passes all three.

> **Supersedes:** `docs/LEARNINGS.md` sets the render at loudnorm **-20 LUFS** (and QA at -20 ± 1.5). For CCC Shorts the
> target is now **-14 LUFS** (section 3). The first five CCC renders measured -20 LUFS and sound quieter than the feed.

---

## 1. Verify every fact after writing the script

Once the script is written, and before voice or edit:

1. **List every checkable claim**: what the voice-over says, **and** the on-screen callouts, subtitles and the date or place
   lines on callouts. That means names, dates, places, numbers, prices, quotes, court outcomes and cause and effect
   ("he did it because…").
2. **Build a verification table**, one row per claim:

   | # | Claim as written | Source (link) | Status |
   |---|---|---|---|
   | 1 | "$6.2 million at Sotheby's" | sothebys.com / NYT | ✅ Verified |
   | 2 | … | … | ⚠️ Corrected / ❌ Unverified |

3. **Source rules:**
   - Primary sources first: the museum, the auction house, the court record, the artist's statement. Otherwise reference
     outlets (NYT, The Guardian, BBC, AP, Reuters, The Art Newspaper, ARTnews, Artnet).
   - **Numbers and prices** need **2 independent sources**. State the currency and, for conversions, the exchange date.
   - **Quotes** are word for word, with who said it and where.
   - **Court outcomes** must be exact: convicted, fined, acquitted, appeal, date.
   - No "this year" or "last year": they go stale. Write the year.
4. **An unverifiable claim is cut or hedged** ("reportedly", "according to…"). It is never published as fact.
5. Hand back the **corrected script** with the table, and mark what changed.

**Open claims in the current CCC Shorts** (confirm or fix):
- **Comedian:** "BANANA STOLEN · Centre Pompidou-Metz · 2026".
- **Bored Guard:** "sentenced to 180 hours of community service, then cleared on appeal".
- **Beeple:** "$100,000 a dog, all sold" and "22 million people watched the last minutes".
- **Wu-Tang:** "nobody can sell it until 2103" is probably wrong: the contract bars *releasing or commercialising* the
  album until 2103, and it has been sold. Use "release". Also confirm "a judge agreed: the album can be a trade secret"
  (Sept 2025).

---

## 2. Every video runs longer than 60 seconds

TikTok's Creator Rewards only pays for originals **over 1 minute**. CCC makes **one cut over 60 s** for all three
platforms: YouTube Shorts and Instagram Reels allow up to 3 minutes, so it still counts as a Short and a Reel.

- **Final render target: 62-75 s.** Hard minimum **61.0 s**. 60.0 s does not count.
- **Script length:** at our voice pace (about 160 words a minute) that is **170-200 words**. Estimate the length before
  generating the voice.
- **Lengthen with content, never padding:**
  - one more fact or twist (another incident, the museum's or artist's reaction, what the restoration cost, what happened
    next);
  - a second open question mid-video that pays off at the end;
  - **not** held frames, silences, long pauses or repeated lines. They sink retention.
- **The pace stays:** something new on screen every 2-3 seconds, start to end.
- **Music:** over 60 s, use only own music or YouTube Audio Library tracks. A Content ID claim on music blocks a Short
  longer than 60 s worldwide (see `docs/PLATFORMS.md`).
- **Check:** after export, measure the file:
  `ffprobe -v error -show_entries format=duration -of csv=p=0 video.mp4` must give 61 or more.

Current Shorts to lengthen: Comedian 57.5 s (+4 s), Wu-Tang 54.9 s (+7 s), Beeple 47 s (+15 s), Bored Guard 43.7 s
(+18 s), Mona Lisa 43.5 s (+18 s).

---

## 3. Audio levels for YouTube, Instagram and TikTok

All three platforms normalise around **-14 LUFS**. Quieter sounds weaker than the rest of the feed and people swipe.
Louder gets turned down and can clip.

### Final master

| Parameter | Target |
|---|---|
| **Integrated loudness** | **-14 LUFS** (accepted: -15 to -13) |
| **True peak** | **≤ -1 dBTP**. Aim for -1.5 dBTP, since AAC encoding can add peaks. |
| **Loudness range (LRA)** | ≤ 7 LU. 3-6 is fine for voice-over. |
| **Codec** | AAC-LC |
| **Sample rate** | 48 kHz |
| **Channels** | Stereo. Check it also works in mono (most people listen on the phone speaker). |
| **Audio bitrate** | 320 kbps (256 kbps minimum) |

### Mix (before mastering)

- **The voice-over leads.** Its short-term loudness sits at -14 to -12 LUFS.
- **Music bed 12-18 dB under the voice**, ducked further under speech.
- **Sound effects** (whooshes, hits) never louder than the voice.
- Voice EQ: high-pass at about 80 Hz and a little presence at 3-5 kHz so it reads on a phone speaker.
- **No clipping** on any track or the master.

### How to apply it

After Effects has no limiter or LUFS meter. Normalise last, on the exported file:

- **Premiere:** Essential Sound → Dialogue → Loudness → Auto-Match, -14 LUFS.
- **Audition:** Match Loudness, -14 LUFS, true peak -1.5 dBTP.
- **ffmpeg** (video stream copied, not re-encoded):
  ```
  ffmpeg -i in.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=7 -c:a aac -b:a 320k -ar 48000 out.mp4
  ```

### Required check before publishing

```
ffmpeg -nostats -i out.mp4 -af ebur128=peak=true -f null -
```
The summary must show **I between -15 and -13 LUFS** and **Peak at -1 dBFS or lower**. Otherwise master again.

---

## Checklist per video

- [ ] Verification table done; unverified claims cut or hedged
- [ ] On-screen callouts match the verified script
- [ ] Script is 170-200 words
- [ ] Final render is **61 s or longer** (checked with ffprobe)
- [ ] Music is own or Audio Library
- [ ] Audio: **-14 LUFS ±1**, true peak **≤ -1 dBTP**, AAC 48 kHz stereo 320 kbps (checked with ebur128)
