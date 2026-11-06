# Writing the script (template artist_short)

- 10 lines following `template.json` › `estructura`; ~140-160 words in total → 55-65 s with holds.
- **A lines** (presenter): conversational, one idea, ≤ 20 words; an `accion` for hands and face that fits the words (an open hand
  toward one side for each option in the closing question: the detail cards follow that side); no "..." (H3 invents words).
- **B lines** (voice-over): the story over the artworks; name each artwork with a clear word so it can enter on it.
- `tts`: the same text with ElevenLabs v3 tags (`[excited]`, `[whispers]`) and "..." for pauses (B lines only).
- `momentos_a`: for each A line, `[["obra", "<stem>", "<word>"], ["etq", "<Label>", "<word>"], ["cta", "Drop your answer", "comments"]]`.
  The first `obra` of a talking line is where the cut to the artwork happens (under stripes).
- `obras_b`: for each B line, `[["<stem>", "<word>"]]`, one artwork per short line; each must be on screen ≥ 1.8 s.
- `titulos`: title and date for every artwork stem; `cita`: lines of ≤ 12-ish letters reflow automatically, `clave` the word in lime.
- `juntas`: names that span two words ("Edgar Allan", "Allan Poe").
- Read it aloud with a timer before generating.
