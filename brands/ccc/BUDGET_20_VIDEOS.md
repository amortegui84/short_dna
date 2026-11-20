# Cool Culture Club: budget for 20 videos (Kling 4.0 at 720p + ElevenLabs)

Prices checked 2026-11-16 on fal.ai and elevenlabs.io (sources at the end). Nothing has been spent.

## 1. Assumptions
| Item | News reaction (x10) | Artist short (x10) |
|---|---|---|
| Length | ~65 s | ~60 s |
| Host seconds generated in Kling | ~65 s (the head says all 10 lines; hidden shots still need her voice) | ~38 s (5 host lines + closing smile; the B lines are voice-over) |
| Hand insert (Kling) | 5 s | 5 s |
| Head accessory start frame (mask, crown...) | local edit of the approved still: USD 0 | same |
| Works, footage, cut-outs, edit, render, QA | local: USD 0 | same |

Kling 4.0 (fal, `kling/v4/image-to-video`): USD 0.157 per output second at 720p (USD 0.235 at 1080p), native audio
with lip sync included, clips of 3 to 30 s, 9:16 supported. The head's speech is then converted to the series voice with
ElevenLabs speech-to-speech (as with Seedance).

## 2. Kling 4.0 (fal, paid per second, no subscription)
| | Per news video | Per artist video | 20 videos |
|---|---|---|---|
| Host | 65 s = USD 10.21 | 38 s = USD 5.97 | USD 161.80 |
| Hand insert | 5 s = USD 0.79 | 5 s = USD 0.79 | USD 15.70 |
| **Subtotal** | **USD 11.00** | **USD 6.75** | **USD 177.50** |
| With one re-take margin (+30%) | USD 14.30 | USD 8.78 | **USD 230.80** |
| First test (1 clip of 10 s per head, 3 heads) | | | USD 4.71 |
| **Kling total to load on fal** | | | **~USD 235** |

At 1080p the same plan is ~USD 345. Seedance 2.5 at 720p (USD 0.46/s) would be ~USD 690. MiniMax H3 local is USD 0.

## 3. ElevenLabs (credits from the monthly plan)
| Use | Credits per video | 20 videos |
|---|---|---|
| Speech-to-speech of the host (1,000 credits a minute) | news ~1,100 / artist ~650 | ~17,500 |
| Artist voice-over: TTS v3 + speech-to-speech (B lines) | artist ~950 | ~9,500 |
| Music, ~70 s track (900 credits a minute), 2 tries | ~2,100 | ~42,000 |
| Re-take margin (+30%) | | ~20,700 |
| **Total** | | **~90,000 credits** |

The Creator plan (USD 22 a month, USD 11 the first month; 121,000 credits, unused credits roll over up to 2 months)
covers all 20 videos in one month with ~30,000 credits to spare. Pro (USD 99, 600,000 credits) is only needed above ~25
videos a month. Music made on a paid plan includes commercial rights for social video; film, TV, radio and streaming
releases need Enterprise. Because CCC is a client's series, confirm with the client who holds the music licence (the
track is licensed to the account that generates it).

## 4. Total cash for the 20 videos
| Item | USD |
|---|---|
| Kling 4.0 at 720p on fal (with margin and the first test) | ~235 |
| ElevenLabs Creator, one month | 22 (11 with the first-month offer) |
| **Total** | **~USD 257** (about USD 12.85 a video) |

Without the +30% margin: ~USD 204. Subscriptions already paid (Adobe, Figma) are not counted.

## 5. Open points before spending
- fal's own comparison page said Kling 4.0 API access was "coming soon"; another source says the endpoints opened on
  2026-10-24. Check the API answers before loading money.
- Kling's lip sync and the series voice through speech-to-speech are untested on our heads: run the USD 4.71 test first
  (3 heads, one line each) and check the transcript, the mouth and the voice.
- If the head is hidden on ~20% of a news video, those lines can be TTS voice-over instead of Kling: saves ~USD 2 a news
  video (~USD 20 in total).

## 6. Per episode (the 20 scripts + the extra, 2026-11-16)
Same assumptions as section 1. The hidden-head spans don't save Kling seconds (her voice still comes from the clip).
| # | ID | Episode | Kling host | Hand | Kling | +30 % margin | ElevenLabs credits (+30 %) |
|---|---|---|---|---|---|---|---|
| 1 | N01 | Comedian | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 2 | A02 | Van Gogh | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| 3 | N04 | Beeple | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 4 | A04 | Dadd | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| 5 | N02 | Sunflowers soup | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 6 | A05 | Munch | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| 7 | N08 | King Charles | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 8 | A01 | Caravaggio | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| 9 | N06 | Mona Lisa | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 10 | A03 | Goya | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| 11 | N07 | AI State Fair | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 12 | A07 | Van Meegeren | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| 13 | N05 | Gold toilet | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 14 | A06 | Bruegel | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| 15 | N10 | The jar | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 16 | A10 | Remedios Varo | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 (+ licence, not quoted) |
| 17 | N03 | Salvator Mundi | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 18 | A08 | Messerschmidt | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| 19 | N09 | The bored guard | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
| 20 | A09 | Louis Wain | 38 s | 5 s | USD 6.75 | USD 8.78 | ~4,800 |
| X | X01 | Wu-Tang (extra) | 65 s | 5 s | USD 11.00 | USD 14.30 | ~4,200 |
ElevenLabs credits per video: news = host speech-to-speech ~1,100 + music ~2,100; artist = STS ~650 + VO (TTS + STS) ~950 +
music ~2,100; both +30 %.

**Totals.** 20 videos: Kling ~USD 231 + first test USD 4.71 = ~USD 235; ElevenLabs ~90,000 credits (Creator, USD 22).
With the extra: Kling ~USD 249, ~94,000 credits. With the proposed voice test (~10,000 credits): ~104,000 of the
Creator plan's 121,000. **Cash: ~USD 271 for 21 videos** (~USD 12.90 a video). Remedios Varo's licence (VEGAP/ARS) is
not included.

## 7. Head on screen at 50 % (decided 2026-11-16, replaces sections 2, 4 and 6 for Kling)
The head is on screen for 5 of the 10 lines (A lines, generated in Kling with her own lip-synced voice). The other 5 are
voice-over (B lines: ElevenLabs TTS with the host's tags, then speech-to-speech to the host's voice, so it sounds the same).
Kling is paid only for A lines. Each script in `SCRIPTS_20.md` marks its A and B lines.
| | News video (~65 s) | Artist video (~60 s) |
|---|---|---|
| Kling: host (A lines) | ~33 s = USD 5.18 | ~30 s = USD 4.71 |
| Kling: hand insert | 5 s = USD 0.79 | 5 s = USD 0.79 |
| **Kling per video** | **USD 5.97** | **USD 5.50** |
| With +30 % re-take margin | USD 7.76 | USD 7.14 |
| ElevenLabs credits (+30 %) | ~4,900 (host STS ~550, VO TTS + STS ~1,100, music ~2,100) | ~5,000 |
| Before (head speaking every line) | USD 11.00 / 14.30 | USD 6.75 / 8.78 |

**Totals.** 20 videos: Kling ~USD 149 + first test USD 4.71 = **~USD 154**; ElevenLabs ~99,000 credits. With the Wu-Tang
extra: Kling **~USD 162**, ~104,000 credits; + the voice test (~10,000) = ~114,000 of the Creator plan's 121,000 (tight:
if re-takes run over, one month of Pro or a second Creator month). **Cash: ~USD 176 for 20 videos, ~USD 184 for 21**
(was ~USD 257 / 271). If the faster voice brings videos to ~57 s, the host drops to ~29 s a video and Kling a little more.
Remedios Varo's licence is still not included.

The A and B lines are grouped in blocks (A 2-3 · B 4-5 · A 2-3), not alternated; the A count stays 5, so these numbers
don't change.

## 8. The 10 selected videos
Order, heads and per-video budget in `SELECTED_10.md`: 5 news + 5 artists, Kling ~USD 57 (~USD 79 with the re-take margin
and the first test), ~49,500 ElevenLabs credits, **~USD 101 cash**.

## Sources
- fal Kling 4.0 image-to-video: https://fal.ai/models/kling/v4/image-to-video
- fal Kling 4.0 vs 3.0 (endpoints, audio, prices): https://fal.ai/learn/devs/kling-4-0-vs-kling-3-0
- ElevenLabs pricing: https://elevenlabs.io/pricing
- Kling 4.0 API pricing (third party): https://aireiter.com/blog/kling-4-0-api-pricing-fal-cost-vs-seedance-vidu
- Eleven Music cost (third party): https://www.stork.ai/blog/elevenlabs-music-2026
