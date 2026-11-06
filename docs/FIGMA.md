# Design stage in Figma (optional)

When the user wants to see the video before generating it, or a new style is being designed:
1. Create one 1080 x 1920 frame per section of the script (hook, artist card, each talking line, voice-over, quote, closing) in a
   Figma file of the user's (Figma MCP: `create_new_file` / `use_figma`, load the figma-use skill first).
2. Use the style tokens (`library/styles/<style>.json`): colours, type, safe area (x 40-950, y 150-1330), subtitle bar at y 1400.
   Place the presenter (a start frame or look), the artwork, labels and cards as they will appear; write the motion note under
   each frame (what enters on which word, which transition).
3. The user comments in Figma; turn each comment into script or style changes before generating.
4. Motion DNA can also bring Figma frames into After Effects (its `figma_build` tools) for a style that is designed frame by frame;
   the collage style builds from data instead, so the frames are the reference, not the source.
Keep brand logos out of the frames; names and brands on screen are fictional unless the topic is a real public-domain artist.
