# Variety between episodes: the general formula (any brand, any topic)

Every brand keeps its template: the same beats, the same alternation (host, then the subject on screen), the same way of
telling. What changes from one video to the next, for **any topic** (an artwork, a news story, a legend, a case, a product),
is four choices made from the script. Without them a channel's videos read as copies of each other even when the topics
differ. *(review 2026-11-09, Cool Culture Club: "the template works, but the videos look the same from one to the next")*

## How it is used
1. Before writing, Claude proposes **3 combinations** for the topic, one line each: hook + order + tone + ending (+ host,
   where the brand has more than one).
2. The person picks one. Then the script is written against it.
3. `python engine/qa_guion.py <project>` checks the script (below). Nothing is generated until it passes.
4. When the script is approved, `--registrar` adds the episode to the brand's `episodios.json`.

## 1. Hooks (the first line)
| Key | Type | What it is | Artwork | News / case |
|---|---|---|---|---|
| `numero` | Impossible number | one hard number that sounds wrong | "193 paintings nobody could see for 20 years." | "Eleven scientists died in five months." |
| `orden` | Order to the viewer | tell them where to look or what to do, now | "Pause on the bottom left corner. See the eye?" | "Read the date on that letter again." |
| `voz_artista` | The subject speaks | open on the subject's own words, as a confession | "'I want to paint like a madman,' he wrote." | "'I made a decision that has become unavoidable.'" |
| `pregunta` | Uncomfortable question | a question about the viewer | "Would you hide your best work until you die?" | "Would you board that ship?" |
| `error` | The mistake | something wrong, on purpose or not | "There's a mistake in this painting. It's on purpose." | "The official report gets one thing wrong." |
| `en_frio` | Cold open | the first line is over the subject (no host); silence first, then the voice; the host enters on line 2 | (the work in silence) "This was painted by a woman who talked to spirits." | (the place in silence) "This bridge has a railing 43 inches high." |
| `dato_raro` | Strange fact (the template's original) | the strangest true detail, said as gossip | Bosch: "Someone painted sheet music on a man's butt." | — spent: use it rarely |

## 2. Order of the beats (the alternation stays)
| Key | Order | Sequence | Engine |
|---|---|---|---|
| `clasico` | Classic | hook, who/what, look closer, twist, quote, story, debate, unknown, close | default |
| `revelacion` | Reveal | hook, the thing itself, detail, story... and only late who made it / who it was | `ficha_en`: the portrait card on a late B line |
| `cita_primero` | Quote first | the quote right after the hook, then who, story, detail, close | the `__cita__` line 2nd or 3rd |
| `detalle_primero` | Detail first | the closest detail first, then who, story, quote, close | the magnifier details on line 1's subject |

## 3. Tone (the host performs it; it writes every action line)
| Key | Tone | How the host speaks and moves |
|---|---|---|
| `chisme` | Gossip | leaning in, eyes darting, "you did not hear this from me" |
| `detective` | Detective | slow, narrowed eyes, pieces laid out one by one, the answer held back |
| `seco` | Deadpan | flat face, short sentences, the joke in what is not said |
| `asombro` | Awe | wide eyes, slower, real wonder, one whispered line |
| `defensa` | Defender | indignant on the subject's behalf |
A brand with a fixed narrator voice (Cult Pixel's masked storyteller) maps tone onto pace, pauses and the size of his gestures.

## 3b. Acting direction, line by line (every host line)
Every host line in the script carries `"direccion": {"emocion", "entra", "gesto", "sale"}` so the scenes connect:
- **emocion**: what the host feels in this line (follows the episode's tone, but moves: awe, then indignation, then a secret);
- **entra**: how the line starts, tied to how the scene before ended (after a quote: eyes low out of respect; after a punch-in:
  landing big);
- **gesto**: the gesture and the word it lands on;
- **sale**: the pose the line ends on, which is where the edit cuts to the next scene.
The `accion` sent to the video model is built from these four. `qa_guion.py` refuses a host line without them.
*(review 2026-11-09: "a description of what the head does, so we have context between scene and scene")*

## 4. Endings (the last line)
| Key | Type | What it is | Example |
|---|---|---|---|
| `giro` | Twist | a last fact that reframes the whole video | "...and she asked for it all to stay hidden. We didn't listen." |
| `callback` | Callback | close the hook's loop with its own words | hook "See the eye?" -> "Now you can't unsee it." |
| `reto` | Challenge | a task for the viewer | "Find the second face. First one in the comments wins." |
| `cliffhanger` | Cliffhanger | point to the next episode | "Next: the man who painted his own funeral." |
| `sobre_ti` | About you | a question about the viewer's own life | "Would you have kept them hidden?" |
| `mudo` | Silent | no spoken call to action: a look to the lens, the on-screen button only | (a look; the button) |
| `debate` | Debate (the template's original) | "X or Y? Tell me..." | spent: use it rarely |

## 5. Rules the QA checks
- The combination (hook + order + tone + ending) repeats none of the brand's last 4 episodes.
- Hook type and ending type differ from the previous episode's.
- No spent phrase. Every brand lists its own in `brand.json` → `variedad.gastadas` (phrases its early videos used so often
  they now make them sound alike).
- The order is wired (reveal has `ficha_en`, quote-first places the quote 2nd or 3rd, a cold open starts on a B line, a silent
  ending asks for nothing).
- Length in the brand's range (`variedad.palabras`, default 120-160 words) and a `research.md` with a source for every fact.

## 6. Visual variety (inside the brand's look, never invented)
Alternate hosts where the brand has more than one; change which of the template's own modules carries each beat; let the
punch-in pattern and the quote's place follow the order. Never a new treatment the template does not have.

## 7. In the project
`proyecto.json` → `"variacion": {"gancho", "orden", "tono", "final", "presentador"}` and, for the reveal order, `"ficha_en"`.
The brand's `episodios.json` keeps the history.
