# Cool Culture Club: voice and acting sheet per host (2026-11-16)

Why this exists: review 2026-11-16, "the voices are very slow and have no acting". Research:
`research_voice/ELEVENLABS_ACTING.md` (ElevenLabs docs + community, with sources). Nothing tested yet: every setting below
is a starting point for the voice test (section 5), not a verified value.

## 1. Diagnosis (measured on our cuts, Whisper + `engine/qa_voz.py`)
| Cut | Words | Length | Pace while speaking | Pauses ≥0.35 s | Pitch movement |
|---|---|---|---|---|---|
| **Bosch (client reference)** | 141 | 56 s | **212 wpm (3.5 w/s)** | **17** | 3.4 st |
| Dürer v7 | 163 | 70 s | 185 wpm | 25 | 3.9 st |
| Blake v2 | 174 | 68 s | 200 wpm | 21 | 3.8 st |
| Banksy v3 | 151 | 68 s | **175 wpm** | 25 | 3.9 st |
| Louvre v2 | 155 | 68 s | **181 wpm** | 27 | 3.7 st |

- We speak 15-18 % slower than the reference and pause ~50 % more, so ~150 words take 68 s instead of ~57 s.
- Pitch movement is fine, so "no acting" is not monotone pitch: it is pace, pauses, and delivery (no attitude, no reactions,
  no punch words).
- BIBLE §1 says "~2.6 words a second": that is words ÷ total length *including* pauses. Bosch = 2.5 gross / 3.5 net.
  **New target: ≥3.3 w/s while speaking, ≤18 pauses a minute (none over 0.4 s), 140-150 words in 55-58 s.**

## 2. Where the voice comes from (and so where the acting must be)
| Line | Route | What sets pace and acting |
|---|---|---|
| Host on screen (A lines, all news lines) | video model speaks (H3 local or Kling 4.0) → ElevenLabs speech-to-speech | **the video model's performance.** STS copies the input's timing and emotion exactly; it can't add speed or acting |
| Voice-over (B lines, artist format) | ElevenLabs TTS → STS (`sts.py --vo`) | the TTS text, tags, voice, and request length |

So there are two places to direct: the **video prompt** (how the head talks) and the **TTS text** (tags, punctuation,
whole beats). Never speed up STS output of a lip-synced clip (memory rule: a stretched VO breaks the lip sync).

## 3. Rules for every host
1. **Whole beats, not lines.** One TTS request = 2-4 lines (≥250 characters), cut back per line by word timestamps
   (`bloques_voz`). Single short lines come out flat and slow.
2. **Tags (v3/v4):** one attitude tag per beat, right before the words it colours, plus at most one reaction per beat.
   Pace: `[rushed]`, `[rapid-fire]` (official). Never `[slowly]`, `[long pause]`, `[pause]` mid-beat (they slow it down;
   the closing `[pause]` that stops v3 cutting off the last syllable stays, at the end only).
3. **Punctuation:** dashes and commas, never "..." (ellipses add weight and slow it). One word in CAPS per sentence for the
   punch. Continuous prose: no line breaks inside a request.
4. **Spoken, not written:** contractions, "okay", "wait", "so", questions to the viewer. The words in `SCRIPTS_20.md` stay;
   small fillers may be added at recording if they don't change the facts.
5. **Model:** A/B `eleven_v4` (new, Sep 2026: more emotive, follows tags better, no speed/style controls) against
   `eleven_v3` Creative (stability 0.0) / Natural (0.5). Never Robust (it flattens acting).
6. **Speech-to-speech:** `eleven_multilingual_sts_v2`, stability 0.55, similarity 0.8, **style 0**, background noise
   removal on. (Today CCC uses stability 0.35 / style 0.6: style adds wobble, not acting; the acting comes from the input.)
7. **Video prompt (H3 / Kling):** every host prompt says the pace and the attitude in plain words (section 4, "video
   direction"), and the dialogue uses the same dashes and CAPS as the TTS text.
8. **Measure every take:** `qa_voz.py` pace and pauses; a take under 3.0 w/s or with a pause over 0.4 s is redone, not
   stretched. Cut gaps of 80-200 ms in the edit to tighten; atempo only on audio-first lines (VO), max +8 %.
9. **The 90 % slot rule (user, 2026-11-16):** a slot of N seconds gets at most 0.9 × N seconds of voice (10 s of video →
   ≤ 9 s of speech). If a take runs long, re-take faster (pace tags, fewer words), never stretch it to fit.
   `voices/old/scripts_y_notas/design_voices.py` checks it on every new voice.

## 4. The three hosts

### H1 · Cap (`ccc_girl`) · voice id `WtzueDduRplMmiMJ3rZx` ("CCC H1 Cap" = cand 3, chosen 2026-11-17 after cand 2 sounded annoying; old `6u6J…` lost)
- **Who she is when she talks:** the friend who already knows the gossip and can't wait to tell you. Sarcastic,
  unimpressed by money and fame, eye-roll energy. Fast and bright; slows down only to drop a whisper on the juicy bit.
- **Pace:** 3.4-3.6 w/s while speaking. The fastest of the three on setups, the punchline lands short and flat.
- **Tag palette:** `[sarcastic]` `[mischievously]` `[dismissive]` `[casual]` `[whispers]` (no `[rushed]`, §7) (once per video) · reactions
  `[laughs]` `[scoffs]` `[chuckles]`.
- **Signature moves:** "Okay—", a scoff before a number, CAPS on the price or the absurd word, a tiny laugh after the punchline.
- **Avoid:** awe and wonder (that's H3), long build-ups, more than one whisper.
- **Video direction (H3/Kling prompt):** "talks fast and conversational, about 3.5 words per second, sarcastic, rolls her
  eyes, smirks on the punchline, no long pauses between sentences".
- **Example (N01 Comedian, L01-L03 as one request):**
  `[sarcastic] Twenty-five cents at a fruit stand. Six point two MILLION at Sotheby's. [dismissive] Same banana. [rushed] Miami, 2019 — Maurizio Cattelan tapes a banana to a wall. Price: one hundred twenty THOUSAND dollars. [scoffs] A day later, a performance artist peels it off and eats it — in front of everyone. [pause]`

### H2 · Locs (`ccc_guy`) · voice id `LOlwofyO2GY6ahNVTPyz` ("CCC H2 Locs", chosen 2026-11-17; old `6OzR…` lost)
- **Who he is when he talks:** the smooth storyteller who lowers his voice like he's letting you in on something. Laid-back
  but never slow: quick clauses, deadpan punchlines, a warm chuckle when the story gets absurd.
- **Pace:** 3.2-3.4 w/s while speaking. Relaxed rhythm, but no pauses longer than 0.3 s; the cool comes from tone, not
  from slowing down.
- **Tag palette:** `[curious]` `[cheeky]` `[deadpan]`* `[conspiratorial]`* `[rushed]` · reactions `[chuckles]` `[laughs]`
  (*not on the official list: verify in the test).
- **Signature moves:** "So—", a low "listen", one dry pause *before* the reveal (max 0.3 s), a chuckle on the absurd fact.
- **Avoid:** shouting, high-energy excitement, ending every line as a question.
- **Video direction:** "talks smoothly and quickly, about 3.3 words per second, relaxed and amused, raises one eyebrow
  on the reveal, small knowing smile, no long pauses".
- **Example (A01 Caravaggio, L01 + L03):**
  `[curious] Would you paint your own severed head — to get out of a murder charge? [chuckles] Because he did. [cheeky] His police record: sword charges, brawls, and a plate of ARTICHOKES thrown at a waiter. [pause]`

### H3 · Buns and glasses · voice id `KhgAWZAIJNJfWsZK130H` ("CCC H3 Buns", chosen 2026-11-17)
- **Who she is when she talks:** the art nerd who just found something and has to tell you RIGHT NOW. Giddy, curious,
  detail-obsessed, a little chaotic. Words tumble out when she's excited; she gasps at the detail and whispers the creepy part.
- **Pace:** 3.6-3.8 w/s while speaking: the fastest host. Speeds up through lists, brakes for one gasp.
- **Tag palette:** `[excited]` `[rapid-fire]` `[curious]` `[whispers]` `[gasps]`* · reactions `[giggles]`* `[laughs]`.
- **Signature moves:** "Wait— wait.", a gasp before the detail, lists said in one breath, "in PENCIL"-style CAPS on the
  tiny detail.
- **Avoid:** sarcasm and eye-rolls (that's H1), deadpan (that's H2).
- **Video direction:** "talks very fast and excited, about 3.7 words per second, wide eyes, leans in, quick gasps, nerdy
  grin, no long pauses".
- **Voice Design prompt (draft, `eleven_ttv_v3`, guidance 30-40 %, 3 voices per generation):**
  > American English, female, around 20, studio-quality recording.
  > Hyper-curious art-nerd vlogger; giddy, quick-witted, a little chaotic.
  > Bright, light voice speaking at a very fast, rapid-fire pace, words tumbling out when excited, sudden gasps, quick whispered asides and nerdy giggles.

  Preview text (≥250 characters, matches the persona):
  > [excited] Okay wait— wait. Zoom into the top left of that sky. [whispers] Someone wrote a sentence there. [gasps] In PENCIL. [rapid-fire] And for a hundred years everyone blamed a vandal, the museum, the cleaners, literally anyone— [giggles] and it was HIM the whole time.
- **Example (A05 Munch, L01 + L03 + L05):**
  `[excited] Zoom into the top left of that red sky — someone wrote a sentence there. [gasps] In PENCIL. [rapid-fire] For over a hundred years, everyone blamed a vandal. [whispers] 2021 — infrared scans, handwriting experts. It was Munch HIMSELF. [pause]`

## 4b. Same tone, three different hosts (review 2026-11-16: "the difference between the hosts' styles must be felt")
The episode's tone (BIBLE §9.3) says *what* the moment is; the host says *how* it sounds. Never let two hosts read alike.
| Tone | H1 Cap (sarcastic gossip) | H2 Locs (smooth storyteller) | H3 Buns (hyper art nerd) |
|---|---|---|---|
| chisme | eye-roll, scoff, CAPS on the price | lowered voice, "listen", warm chuckle | breathless, "wait wait", gasp on the detail |
| detective | dry, clipped, unimpressed by each clue | slow-burn, one eyebrow, beat before the reveal | piling clues fast, "and THEN", whisper the answer |
| seco | flat, the joke in the silence after | deadpan, almost bored, tiny smile | she can't do deadpan: give seco episodes to H1/H2 |
| asombro | "okay, that's actually insane" (sarcasm drops for once) | soft, impressed, one whispered line | full wonder, faster, a giggle |
| defensa | indignant, "excuse me?" | calm but firm, "let's be fair" | outraged on the artist's behalf, rapid-fire |
Each card in Figma carries a "Voice" line with its host's style; every TTS request and video prompt for that episode
uses that host's tags and video direction from section 4.

## 4c. Hard names: pronunciation (review 2026-11-16)
The name is said first by the **video model** (host lines) or by **TTS** (VO lines); speech-to-speech copies whatever it
hears. So the respelling goes into both the TTS text and the video dialogue, **never into the captions**.
- In `proyecto.json` (to build): `"pronunciacion": {"Caravaggio": "kah-rah-VAH-jee-oh", ...}`: tts.py and the host
  prompt swap the written name for the respelling; captions keep the real spelling; the Whisper check compares against
  the real spelling and accepts the respelling.
- ElevenLabs: respelling (alias) works on every model; v3/v4 also take IPA inline and in pronunciation dictionaries, but
  ElevenLabs says inline IPA on v3 is "not 100% consistent": use respelling first, IPA only for a name that still fails.
- Every new name is checked by ear on the first take; a wrong name is a failed take.

| Ep | Name (caption) | Say it (respelling) |
|---|---|---|
| N01, N05 | Maurizio Cattelan | mow-REET-see-oh kat-tuh-LAHN |
| N01, N05 | Sotheby's | SUTH-uh-beez |
| N01 | Seoul | SOHL |
| N04 | Art Basel | art BAH-zul |
| N04 | Beeple | BEE-pul |
| N02 | Vermeer / Monet | ver-MEER / moh-NAY |
| A02 | Gauguin / Arles | goh-GAN / ARL |
| A02 | Vincent van Gogh | VIN-sent van GOH |
| A04 | Osiris / Bethlem | oh-SY-ris / BETH-lum |
| A05 | Edvard Munch | ED-vard MOONK |
| N08 | Jonathan Yeo | JON-uh-thun YOH |
| N08 | Wallace and Gromit | WOL-iss and GROM-it |
| A01 | Caravaggio | kah-rah-VAH-jee-oh |
| A01 | Ranuccio Tomassoni | rah-NOO-choh toh-mah-SOH-nee |
| A03 | Francisco de Goya | fran-SIS-koh deh GOY-uh |
| A03 | Aragon / Bordeaux / Prado | AIR-uh-gon / bor-DOH / PRAH-doh |
| A03 | Los Caprichos | lohs kah-PREE-chohs |
| N07 | Théâtre D'opéra Spatial | tay-AH-truh doh-pay-RAH spah-SYAHL |
| A07 | Han van Meegeren | HAHN van MAY-guh-ren |
| A07 | Göring / Deventer / Delft | GUR-ing / DAY-ven-ter / DELFT |
| N05 | Blenheim / Guggenheim | BLEN-im / GOO-gun-hime |
| A06 | Pieter Bruegel / Ortelius | PEE-ter BROY-gul / or-TEE-lee-us |
| N10 | Hecht Museum | HEKT myoo-ZEE-um |
| A10 | Remedios Varo | reh-MEH-dyohs VAH-roh |
| A10 | Leonora Carrington / Homo rodans | lee-oh-NOR-uh KAIR-ing-tun / HOH-moh ROH-danz |
| A10 | Bayer / Octavio Paz | BY-er / ok-TAH-vyoh PAHS |
| N03 | Salvator Mundi | sal-VAH-tor MOON-dee |
| N03 | Louvre Abu Dhabi | LOOV-ruh AH-boo DAH-bee |
| A08 | Franz Xaver Messerschmidt | FRAHNTS ZAY-ver MESS-er-shmit |
| A08 | Pressburg / Bratislava | PRESS-burg / brah-tih-SLAH-vuh |
| N09 | Yekaterinburg | yeh-kah-tyeh-rin-BOORG |
| N09 | Anna Leporskaya | AH-nah leh-POR-skah-yah |
| A09 | Louis Wain | LOO-ee WAYN |
| X01 | Wu-Tang Clan / Martin Shkreli | WOO-tang klan / MAR-tin SHKREL-ee |
English pronunciations for an English-speaking audience (Van Gogh as "van GOH", not the Dutch). Verify the less common ones
(Leporskaya, Tomassoni, Hecht) against a native pronunciation source before the take.

## 5. Voice test (proposed; needs the user's OK before spending credits)
One script (N01 Comedian, ~150 words), in 3 beats, per host:
1. H1 and H2 with their current voices: `eleven_v3` Creative, `eleven_v3` Natural, `eleven_v4` (3 runs × 2 hosts).
2. H3: one Voice Design generation (3 candidate voices), then the best one through the same 3 runs.
3. STS check: one host clip through STS with the new settings (stability 0.55, style 0) vs the current ones.
4. Measure each take with `qa_voz.py` (pace, pauses, pitch) and play the best two per host side by side with Bosch.
Rough cost: ~9 TTS runs × ~900 characters ≈ 8,000-10,000 credits + Voice Design + ~1 min of STS (1,000 credits) — about
10 % of the Creator plan's monthly credits. Free otherwise (no fal, no GPU).

## 6. Engine changes to make after the test (not done yet)
- `characters/<host>/character.json` `voz`: per-host `modelo`, `stability`, `etiquetas` (the default attitude tag), `ritmo_objetivo`.
- `sts_ajustes` for CCC: stability 0.55, similarity 0.8, style 0 (if the test confirms it).
- `qa_voz.py`: fail a take under 3.0 w/s or with a pause over 0.4 s (today it only gates pitch).
- `clips.py` / the Kling prompt: append the host's "video direction" line to every host prompt.
- BIBLE §1: replace "~2.6 words a second" with the net target (≥3.3 w/s while speaking, ≤18 pauses a minute).

## 7. Voices fixed (2026-11-17)
The user picked from 9 Voice Design candidates (`voices/old/scripts_y_notas/REVIEW.md`): **H1 Cap = cand 3** `WtzueDduRplMmiMJ3rZx` (cand 2 `mb3M…` dropped, "a bit annoying"),
**H2 Locs = cand 2** `LOlwofyO2GY6ahNVTPyz`, **H3 Buns = cand 3** `KhgAWZAIJNJfWsZK130H` (ElevenLabs account in
`ccc/.env`). Feedback: "a little slow, but good". `eleven_v3` ignores `speed`; pace test of 4 routes in
`voices/old/scripts_y_notas/PACE_TEST.md` (files `voices/<host>/pace_*.mp3`).

**Voice-over rule (user, 2026-11-17 evening, chosen by ear: `proyectos/n01_comedian/vo/prueba_cap/5_estab05_un_bloque_sin_huecos.wav`,
"el 5 suena mucho mejor en bloque"; "el bloque sin huecos funciona mucho mejor"):**
- Every run of voice-over lines is generated as **one continuous block** (`proyecto.json` `"bloques_voz"`), never line by
  line: line by line, each sentence starts fresh and the read sounds like "word, space, word".
- **Cap: eleven_v3 stability 0.5** (was 1.0 Robust: monotone, word by word). Still no `[rushed]` and no speed-up.
- The gaps between words are tightened after (`comun.apretar_pausas`, run by montaje.py): ~0.08 s after a comma, ~0.2 s
  after a sentence end, only over real silence/breath inside Whisper's gap, never over the next word's soft onset (s, f, h:
  "Seoul" lost its S once); a tightened line that loses a word is thrown away.
- Respellings in CAPS can come out wrong in a block ("SOHL" -> "So Chell"): a name English TTS already says right stays
  plain ("Seoul"). Whisper hearing "France Zaver" for "FRAHNTS ZAY-ver" is a QA false alarm, not a cut.
- `voz.etiquetas` in character.json is a description, never text: tts.py only takes its first [tag] (a block once began
  "Reactions, ha ha ha").
- Measured on the A08 block: v4, v3 Conversational and tag changes did not speed the read (2.0-2.7 w/s); the script's
  short sentences set the pace. eleven_v4 is available but not better for this.

**Settings fixed after the pace test (user, 2026-11-17, files in `voices/old/prueba_velocidad/`):**
- **H1 Cap (RULE, user 2026-11-17):** `eleven_v3`, **stability 1.0** (Robust), attitude tags `[sarcastic]` `[dismissive]`
  `[casual]`, **never `[rushed]` / `[rapid-fire]`** and no speed-up (sped-up Cap is "too fast"). The 10 s test line runs
  ~10.5 s (user's reference ~11 s). Reference take: `voices/H1_cap/Cap_voz_elegida.mp3`. Cap gets the time her lines need
  (videos a few seconds longer) instead of the 90 % rule; the scripts stay as approved ("los guiones están al pelo").
- **H2 Locs:** `eleven_v3` (a/b), with tags. Already fits (6.6 s).
- **H3 Buns:** `eleven_multilingual_v2`, speed 1.15, stability 0.4, similarity 0.8, no tags (7.8 s). "All fine."
