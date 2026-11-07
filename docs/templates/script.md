# Writing the script (template artist_short)

A brand with `brands/<brand>/BIBLE.md` (Cult Pixel): read it first; it sets the constants and the topic knobs.

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

## Movement: never reuse footage, plan a chain of moves (rule, review 2026-11-06)
Reused footage (a clip looped, played backward, repeated in another section) looks broken in a video. Every second of the
presenter on screen is generated for that moment.
1. **Read what each stretch is about** before writing any `accion`: what the words describe (a fire, a document, a number, a
   question) is what the hands show (warm the hands over a light, hold up a page, count on the fingers, open both palms).
2. **Chain the moves.** Each `accion` starts where the previous one ended and ends where the next one can start: if L03 ends
   with a sphere back on the table and the hands resting, L05 starts from resting hands. Write the start and the end pose
   ("starting from his hands resting on the armrests, ... , ending with both palms open over the table").
3. **No move twice in one episode** (no two "points at the viewer", no two "tilts the head"); across the brand's last
   episode too.
4. **Where the voice goes on over the presenter** (a B line read while he stays on screen), write `continuacion`
   (`{"L03": "..."}`): what he does silently, illustrating those words, starting from the end pose of his line and ending in
   the start pose of the next scene. The stage `continuar` generates it (new footage, never a loop); without it, it derives
   the move from the words.
5. Hands only hold what was on the table or in the previous shot: nothing appears from nowhere or vanishes (ep03 L05).
6. **Never write "mimes holding a book" (or any object):** the video model draws the object (ep04 L08 got a real book).
   Describe only what the hands do (trace a line in the air, lay a palm flat) and end with "his hands stay empty: no book,
   no paper, no object of any kind".
7. **He faces the lens.** Never write him turning his head over his shoulder or looking behind him (ep05 review: "he looks
   back too much"); looking back is saved for the ending, where it pays off. End each action with "He keeps his face toward
   the lens".
8. **Calm hands, no pointing.** He is explaining, not miming: most of the time his hands rest or quietly handle
   something the place gives him (a leaf, a stick in the fire, a small animal: in ep05's jungle a poison dart frog). Move the
   hands a little only on the line that needs it, and never point at the lens (ep05 v2 review: "unnecessary hand movements").
   An episode with a prop says so in its start frames (`inicios_variantes`) and drops "hands stay empty" for those lines.
9. **Reframe.** Not every line in the same medium shot: mix close portraits (chest up) and medium shots in the start frames,
   and the edit punches in at sentence ends (zoom jumps) while he is on screen.
