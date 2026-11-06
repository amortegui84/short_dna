# proyecto.json

One video = one folder in `work_dir` with this file. Complete examples: `examples/03_bosch`, `examples/04_redon`.

| Field | Type | Meaning |
|---|---|---|
| `slug` | str | folder name and file names (`04_redon`) |
| `plantilla`, `estilo`, `personaje`, `look` | str | library entries (template, style, character, look key in `character.json`) |
| `escena` | str, optional | a start image inside the project; overrides the look |
| `numero` | int | episode number (artist card "No. 04") |
| `artista`, `fechas`, `lema` | str | artist card |
| `gancho` | str | hook label (top capsule in the first line) |
| `retrato` | str | artwork stem used for the cut-out portrait |
| `voz` | str, optional | ElevenLabs voice id; default: the character's |
| `ritmo_b` | float | voice-over speed (1.0 natural) |
| `pausa_b` | float | seconds the artwork holds after each voice-over line (1.2) |
| `cita` | {lineas, autor, clave} | the quote, its author line and the key word in lime |
| `palabras_clave` | [[line, word, label]] | labels over voice-over artworks on a word |
| `obras_descarga` | {stem: url} | public-domain artworks (Wikimedia Commons file URLs) |
| `titulos` | {stem: [title, date]} | title cards |
| `momentos_a` | {line: [[kind, value, word]]} | talking lines: `obra` (artwork stem), `etq` (label), `cta` (call to action), `lapiz`, `flecha`; enters on `word` |
| `obras_b` | {line: [[stem, word]]} | voice-over lines: artworks on the word that names them (each ≥ 1.8 s) |
| `juntas` | [[w1, w2]] | word pairs a subtitle line never splits |
| `musica` | {tags, bpm, key} or null | music prompt; null = the style's default |
| `lineas` | list | `{id, tipo: A|B, texto, tts, accion (A), obras (B; ["__cita__"] for the quote line)}` |
| `fuentes` | list | sources from research.md |
| `inicios` | {line: path} | written by the `inicios` stage |
