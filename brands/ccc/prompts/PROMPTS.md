# Cool Culture Club: generation prompts (reference, verbatim)

Source: the project handoff (Nov 2026), `references/bosch_template/Cool Culture Club Handoff.html`. These produced the approved
presenters and the Bosch avatar clips. Keep the identity lines unchanged when generating new poses or clips.

## How they were written (what worked)
- Framing: say that the top of the cap, both ears, the chin and the ends of the hair sit inside the frame, head ~60% of the frame height; portrait aspect (4:5 or 2:3) helps long hair fit.
- A backwards cap needs explaining: "strap and back panels facing forward over the forehead, brim pointing behind the head".
- Gradients on fabric: a dyed ombre with a direction ("lower left to upper right"), not a flat overlay.
- Clean skin: list every unwanted mark; the one tattoo is "the only mark anywhere on his skin".
- "His left" gets confused with the viewer's left: say "on the right side of the image" if it lands wrong.
- The approved guy render came out more stylized (closer to a Pixar look) with hoops in both ears; his video prompt describes the render, not the image prompt.

## Girl presenter · image prompt
File: `prompts/girl_image.txt`

```
A grotesque, hyperrealistic 3D character head floating in space, underground art-toy aesthetic.
Levitating head of a young woman, no body, no neck. Strongly caricatured facial proportions with extreme material realism.
Full head and full hair completely visible inside the frame, nothing cropped: the cap, both ears, the chin and the ends of the hair all sit well within the image borders.
Centered composition, head occupying about 60% of the frame height, generous empty space on all four sides, straight-on front view at eye level, slightly zoomed out.
Very large dominant eyes, icy blue/gray, visible sclera veins, wet glossy reflections.
Small compact nose with a slightly upturned tip, thick sculptural lips, defined cheekbones, oversized slightly protruding ears.
Facial proportions pushed beyond realism but still clearly human.
Sarcastic, confident expression: asymmetrical mocking smile, cold eyes that do not smile.
Unimpressed, superior attitude.
Dark eyeshadow and heavy eyeliner, slightly messy and worn-in makeup, subtle skin shine visible.
Dark espresso-brown hair, long and straight, falling loosely and floating slightly below the head, slightly messy with flyaways, individual strands visible, the full length of the hair shown.
5-panel cap worn backwards, the adjustable strap and back panels facing forward over the forehead, brim pointing behind the head and not visible from the front. The cap fabric is dyed in a smooth diagonal ombré gradient running corner to corner across the cap, from vivid orange at the lower left side to magenta-fuchsia at the upper right side, the colors blending softly at an angle across the panels, nylon or cotton twill fabric texture, visible panel seams and light wear.
Silver septum ring, a thin circular bull ring hanging from the center of the nose just above the upper lip, realistic polished metal reflections, sitting naturally against the nostrils.
One tiny silver stud in one earlobe, subtle and minimal, realistic metal reflection.
Ultra-hyperrealistic skin: visible pores, freckles, micro-wrinkles, peach fuzz, uneven tone, subtle redness and oiliness. Skin feels alive and tactile, no cracks or stylization.
Green gradient background (deep forest green to light mint), clean and seamless.
Hard studio lighting, high contrast, sharp focus emphasizing exaggerated anatomy.
Ultra-high resolution, physically based rendering, strong subsurface scattering.
Raw, macarra, confrontational.
```

## Guy presenter · image prompt
File: `prompts/guy_image.txt`

```
A grotesque, hyperrealistic 3D character head floating in space, underground art-toy aesthetic.
Levitating head of a young Black African American man, no body, no neck, no hat. Strongly caricatured facial proportions with extreme material realism.
Full head and full hair completely visible inside the frame, nothing cropped: the top of the head, both ears, the chin and the ends of the dreadlocks all sit well within the image borders.
Centered composition, head occupying about 60% of the frame height, generous empty space on all four sides, straight-on front view at eye level, slightly zoomed out.
Very large dominant eyes, deep dark brown irises almost black, clean bright whites, wet glossy reflections.
Broad nose with a rounded tip, thick sculptural lips, strong defined cheekbones, firm jawline, oversized slightly protruding ears.
Facial proportions pushed beyond realism but still clearly human.
Sarcastic, confident expression: asymmetrical mocking smile, cold eyes that do not smile.
Unimpressed, superior attitude.
Heavy-lidded eyes, thick natural eyebrows, light stubble along the jaw and upper lip, subtle skin shine visible.
Medium-deep brown skin with warm golden undertones, rich but not the darkest tone.
Long thick dreadlocks growing from the scalp and fully visible on top of the head, dense and textured, falling loosely and floating slightly below the head, individual locs visible with frizz and natural fibers, the full length of the locs shown.
One big circular silver hoop through the earlobe, thick and bold, realistic polished metal reflections.
Small tattoo under his left eye: a thin-line outlined triangle, dark ink, sitting on the upper cheekbone. This single triangle is the only tattoo and the only mark anywhere on his skin.
Ultra-hyperrealistic clean skin: visible pores, fine hair, micro-texture and natural oiliness, smooth even complexion. Completely unmarked skin apart from the triangle: no other tattoos, no face paint, no scarification, no scars, no stains, no spots, no moles, no freckles, no blemishes, no redness, no discoloration, no dirt. Skin feels alive and tactile, no cracks or stylization.
Magenta-red gradient background, darker at the top (deep crimson-magenta) fading to lighter at the bottom (soft pinkish red), clean and seamless.
Hard studio lighting, high contrast, sharp focus emphasizing exaggerated anatomy.
Ultra-high resolution, physically based rendering, strong subsurface scattering.
Raw, macarra, confrontational.

Negative: scars, scarification, stains, spots, moles, freckles, blemishes, redness, face paint, extra tattoos, tribal markings, dirt, discoloration, hat, cap
```

## Guy presenter · Bosch Clip A (20 s)
File: `prompts/seedance_guy_bosch_clip_a.txt`

```
Image-to-video. Animate this exact character: a stylized 3D art-toy floating head, no body, no neck, no hands. Keep his identity exactly as in the image for the whole clip: warm brown skin, long thick dreadlocks with braided rows on top hanging well below the chin, dark brown eyes, thick eyebrows, light goatee stubble, big silver hoop earrings in both ears, and the small thin-line triangle tattoo under his left eye. No hat. Static magenta-red gradient background, darker at the top and lighter at the bottom. Locked-off camera, head centered and fully in frame, dreadlocks fully visible.
He speaks to camera in English, young African American male voice, smooth, natural, gossipy and playful, the same voice throughout, with precise lip sync. Three separate lines, each followed by a short pause:

Line 1: "Someone painted sheet music on a man's butt... five hundred years ago."

Line 2: "Look closely at the hell panel. Monsters, giant instruments... and a guy with a song on his backside."

Line 3: "And here's the thing: we know almost nothing about Bosh. No letters, no diary. Just these paintings."

Exaggerated, cartoonishly expressive art-toy performance: big eyebrow moves, cheeks squashing, wide clear mouth shapes. He mostly faces the lens with small bobs; turns his head only when the beat calls for it, then returns to the lens for each punchline. Natural blinks every 2-4 s, quick blinks on emphasis. The heavy dreadlocks swing with weight and momentum on every head movement and settle naturally afterwards; the hoop earrings swing slightly. Cheeky, sarcastic attitude.
[0-1s] He floats slightly toward the lens with a scandalised grin.
[1-2.5s] Eyes dart left then right as if sharing gossip.
[2.5-4s] Facing the lens, eyebrows shoot up.
[4-5s] Short snort of laughter.
[5-5.8s] Pause: silent, he settles to a neutral face looking into the lens, one blink.
[5.8-7.5s] He squints one eye and pushes toward the lens as if through a magnifying glass on "look closely at the hell panel".
[7.5-8.5s] Eyes snap wide in mock horror on "monsters".
[8.5-10s] Head sways side to side in rhythm on "giant instruments", locs swinging.
[10-11.5s] Back to the lens, smirk building on "and a guy with a song on his".
[11.5-12.5s] Bursts out laughing on "backside", head tipping back, locs bouncing.
[12.5-13.3s] Pause: silent, he settles to a neutral face looking into the lens, one blink.
[13.3-14.5s] One eyebrow up, slight lean in on "and here's the thing".
[14.5-16s] Exaggerated facial shrug, eyebrows high, head tilted, lips pulled down on "we know almost nothing about Bosh".
[16-17.5s] Two sharp little head shakes on "no letters", "no diary", locs swaying.
[17.5-19s] Head turns slightly to one side then swings back with wide intense eyes on "just these paintings".
[19-20s] Holds eye contact with a mocking half-smile.
Avoid: body, neck, shoulders, hands, arms, extra limbs, camera movement, zoom, cropping, head leaving the frame, dreadlocks cut off by the frame, hat, earrings disappearing, tattoo moving or disappearing, extra tattoos, face morphing, identity drift, static frozen face, stiff mouth, subtitles, on-screen text.
```

## Subject cutout prompt (any artist)
File: `prompts/subject_cutout.txt`

```
Turn the person in this image into a modern photocopy cutout: same face, same features, same clothing, head and shoulders only. Crisp high-contrast black and white like a fresh laser photocopy with a fine halftone dot texture, deep blacks and clean whites. Cut out by hand along the silhouette with a thin even white paper border. Isolated on a transparent background, no shadow.
```

## Rotation expression
File: `prompts/stop_motion_jitter.expr.txt`

```
// stop-motion jitter once the piece has landed
if (time < inPoint + 0.9) value; else { posterizeTime(6); seedRandom(index, true); value + (wiggle(1, 1.2) - value); }
```

## Seedance clips: how they are split and performed
- Image-to-video in Seedance 2.5 with the avatar still as the start frame; up to 30 s per clip.
- 5 avatar lines (~29 s of speech) go into two clips: Clip A (L01+L03+L05, ~20 s) and Clip B (L08+L10, ~16 s). One clip per line is the fallback when a long clip drifts in identity or lip sync.
- Between lines the avatar settles to a neutral face for under a second and blinks: those pauses are the cut points for the B shots.
- More expressive than a real person (big eyebrows, cheeks squashing, wide mouth shapes); head turns only when the line calls for one, back to the lens for every punchline; blinks every 2-4 s.
- Timestamped beats ([2.5-4s]) tie each expression to a word. The negative prompt goes last as an `Avoid:` line (to the top if hands or a body appear).
- Hand gestures from the script become face or head moves: the presenters have no hands.
- Girl version of any clip: swap the identity line for her look (backwards orange-to-fuchsia cap, dark hair, icy blue eyes, heavy smudged eyeliner, freckles, septum ring, ear stud) and "his locs" for "her hair". Her full Clip A/B prompts live in the source project's `Claude/bosch_avatar_seedance_prompts.md` (not in this folder).

## Voice workflow
- Seedance's own voice gives the exact lip sync; ElevenLabs Speech-to-Speech swaps its timbre to the series voice, keeping rhythm and pauses. B lines are direct ElevenLabs voice-over, so the voice matches across the video.
- Names the model may mispronounce get a guide in brackets: "Hieronymus Bosch [heer-ON-ih-mus Bosh]".

## Bricolage kit sheets
- One sheet per group, GPT Image 2.6 (Weave), transparent background, high quality, 1536x1024. Every prompt ends with: "Isolated elements on a transparent background, flat top-down view, spread out with clear space between them, none touching, none cut off by the edge, no shadow, no background."
- Name label: black gaffer tape with the name in white paint marker; spell the name letter by letter in the prompt.
- Avoid lists keep: aged paper, sepia, newspaper clippings, typewriter text (the brief is modern).
- Rejected: artist-specific stickers (Bosch creatures: the kit must be generic); crops of real paintings with nudity through OpenAI (blocked and still charged: crop locally).
