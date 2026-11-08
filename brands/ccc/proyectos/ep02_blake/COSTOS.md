# Ep 02 William Blake: Seedance 2.5 test (fal.ai), cost and time

## Measured (480p test)
| Item | Amount | USD |
|---|---|---|
| Seedance 2.5 image-to-video, clip A (L01+L03+L05), 23 s at 480x854 | 236,000 tokens | 4.73 |
| Seedance 2.5 image-to-video, clip B (L08+L10 + closing smile), 15 s at 480x854 | 154,000 tokens | 3.08 |
| ElevenLabs: voice-over TTS (v3) | 537 characters | ~0.10 |
| ElevenLabs: speech-to-speech, every line | 63 s, ~1,050 credits | ~0.20 |
| Everything else (cut-outs, mattes, After Effects, render, QA) | local | 0 |
| **Total** | | **~8.10** |

Pricing: fal bills Seedance 2.5 by tokens = width x height x seconds x 24 / 1024, at USD 0.0214 per 1,000 tokens (audio
included). ElevenLabs at the Creator plan rate (~USD 0.00018-0.00022 per credit).

## Same episode at other resolutions (same 38 s of host footage)
| Resolution | Seedance | + voice | Episode | With one re-take margin (+30%) |
|---|---|---|---|---|
| 480p (tested) | 7.81 | 0.30 | ~8.10 | ~10.50 |
| 720p | 17.57 | 0.30 | ~17.90 | ~23.20 |
| 1080p | 39.52 | 0.30 | ~39.80 | ~51.70 |

## Time (request -> delivery)
- Request 20:34:42 -> delivered 21:12:04: **37 min**. That includes ~10 min fixing two gaps the first Seedance run exposed (montaje
  expected a TTS file for the host lines; the project lacked "gancho") and an After Effects restart.
- Without those: ~27 min.
  - Research and script: ~6 min.
  - Seedance: 9 min (two clips of 264 s each, one after the other; sent in parallel they would take ~4.5 min).
  - Voice, cut-outs and mattes: ~4 min.
  - After Effects build and render: ~8 min.

## Against MiniMax H3 (Dürer, local)
| | Seedance 2.5 (Blake) | MiniMax H3 local (Dürer) |
|---|---|---|
| Host footage | 2 clips, 38 s, 480x854 | 5 clips + 3 continuations, ~44 s, 768x1344 |
| Generation time | 9 min (4.5 min in parallel) | ~24 min for the 5 clips (+ ~7 min continuations) |
| Cost | USD 7.81 (480p) / 17.57 (720p) / 39.52 (1080p) | USD 0 (own GPU) |
| Expression | big: wide eyes, squints, eyebrow jumps, real laughs | moderate |
| Lip sync / words | Whisper match 1.00 on every line; final cut 0.99 | 0.91-1.00 per line; final cut 0.96 |
| Ending | generated in the same clip (closing smile) | needed a continuation clip |

Recipe: `engine/seedance.py <project> --res 480p|720p|1080p` (prompts from brands/ccc/prompts/PROMPTS.md, cost log in costos.json).
