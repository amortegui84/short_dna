"""Writes D:/short_dna/library/tomas/tomas.json: dynamic shots for a masked, mouthless narrator (research 2026-11-12: 10 reference
Shorts measured shot by shot; rules for MiniMax H3: one action, every object already in the start frame, rigid mask, gloves)."""
import json
from pathlib import Path

R = ("One single action. Every object he uses is already in the start frame; nothing appears from outside it. The mask is rigid and "
     "nothing on it moves.")
SOLO = "He is the only person in the frame."
GENTE = ("Everyone else is an ordinary passer-by dressed for the place and its year: they never look at him or the lens, never touch "
         "him, and their faces stay small, turned away or softly blurred by motion; every one of them has a normal body. Signs, screens "
         "and billboards glow with abstract colour and light only: no letters, no logos, no brands.")
MANOS = "Gloved hands stay large and slow, never crossed or interlaced."
T = []


def t(id, nombre, cat, e, beats, verbo, camara, inicio, entra, gesto, sale, riesgo, sigue=None, props=None, solo_maestro=False, extra="",
      gente=False, lugar_tipo=None):
    T.append({"id": id, "nombre": nombre, "categoria": cat, "energia": e, "beats": beats, "verbo": verbo, "camara": camara,
              "inicio": inicio, "entra": entra, "gesto": gesto, "sale": sale, "riesgo": riesgo, "props": props or [],
              "sigue": sigue or "he holds the last pose, very still, then looks back into the lens.", "solo_maestro": solo_maestro,
              "gente": gente, "lugar_tipo": lugar_tipo or "",
              "reglas": " ".join(x for x in (R, GENTE if gente else SOLO, MANOS, extra) if x)})


SEL = "handheld selfie video: the phone in his own outstretched right hand just out of frame at the bottom left, the frame sways gently"
# ---------------- camera handling
t("CH01", "Camera grab", "camara", 5, ["hook", "transition"], "grabs the camera",
  "handheld phone camera that starts lying on a desk pointing up at a dark ceiling, is lifted by his gloved hand and swung up to his mask; from 3 s on a steady handheld selfie close-up",
  "View from a phone lying on a desk looking up at a dark ceiling in {lugar}; his gloved hand already grips the edge of the frame at the bottom right; the edge of his black hood visible.",
  "with his gloved hand gripping the phone at the bottom of the frame", "he lifts the phone and swings it up and around to his mask in one fast move, then holds it steady at arm's length, head tilted",
  "in a steady handheld selfie close-up, head tilted, facing the lens", "H: the swing smears; cut on the smear and keep the last 4 s")
t("CH02", "Selfie walk-and-talk", "camara", 3, ["setup", "context"], "walks toward the camera", "ultra-wide " + SEL + " with his steps, slightly low angle",
  "SELFIE FRAMING: an ultra-wide arm's-length selfie, the camera held in his own gloved right hand; his right arm and shoulder reach toward the lens from the lower left corner and fill it; his masked head and chest only, slightly low angle, the mask in the upper third; behind him {lugar}.",
  "walking slowly, filming himself at arm's length", "he keeps walking at a steady pace; near the end he tilts his head toward the lens",
  "walking, head tilted toward the lens", "M: keep the background simple")
t("CH03", "Turn the camera on himself", "camara", 4, ["hook"], "turns the camera on himself",
  "handheld phone camera first pointed at {prop}, then panned in one smooth move to his mask in close-up",
  "POINT OF VIEW: the camera looks at {prop} in {lugar}; he is NOT in the centre: only the dark edge of his black hood and one shoulder enter at the far left edge of the frame, out of focus.",
  "holding the phone pointed at {prop}", "he pans the phone in one smooth move from {prop} to his own mask and leans in slightly",
  "close-up selfie, leaning in, facing the lens", "M-H: the pan can change the room; keep it dark", props=["case board", "map", "photo wall"])
t("CH04", "Lean into the lens", "camara", 3, ["escalation", "pre_reveal"], "leans into the lens", "locked-off camera at eye level, medium shot that he fills as he leans in",
  "Locked-off medium shot at eye level in {lugar}; he sits facing the lens, gloves resting on his knees.",
  "seated, gloves on his knees", "he slowly leans forward until the mask almost fills the frame and holds there, a tiny head tilt",
  "leaning in, the mask filling the frame", "L (the reference push-in done with the body)")
t("CH05", "Pull back from the lens", "camara", 3, ["reveal_place"], "pulls back from the lens", "handheld camera, starts on an extreme close-up of the mask and widens as he leans back",
  "Extreme close-up of the mask, eye level, handheld, in {lugar}; only the mask and the hood edge in frame.",
  "with the mask very close to the lens", "he leans back slowly and the frame widens to a medium shot that shows {lugar} behind him",
  "in a medium shot with the place behind him, facing the lens", "L")
t("CH06", "Phone jolt", "camara", 4, ["scare"], "jolts", "handheld selfie medium close-up that is suddenly jostled for one second, then still",
  "Handheld selfie medium close-up at arm's length in {lugar}.", "filming himself, still", "the phone is jolted for one second, his head snaps to one side, then everything is still",
  "still, head turned slightly, then back to the lens", "M: blur; use 1-2 s")
t("CH07", "Phone on the ground", "angulo", 2, ["setup"], "crouches toward the camera", "phone lying on the ground looking straight up at him, locked off",
  "WORM'S-EYE VIEW: the camera lies on the ground looking straight up; he stands over the lens, seen from below, his hood and mask against the sky or ceiling above; {lugar}.",
  "standing over the phone", "he crouches down toward the lens until the mask is in close-up", "crouched, the mask close, facing the lens", "L")
t("CH08", "Car selfie at night", "camara", 2, ["setup", "road"], "drives", "phone on a dashboard mount, three-quarter angle on the driver, night streetlights sweeping across",
  "Dashboard-mount phone view, three-quarter angle, at night: he sits behind the wheel of {lugar}, both gloves on the wheel, streetlights through the window.",
  "behind the wheel, gloves on the wheel", "passing streetlight sweeps across the mask; halfway he slowly turns his head to the lens",
  "head turned to the lens, gloves on the wheel", "L: hands stay on the wheel")
# ---------------- lens proximity and gestures
t("LP01", "Object to the lens", "objeto", 4, ["hook", "proof"], "holds up an object", "locked-off medium close-up; the object comes toward the lens and fills the frame, focus shifting to it",
  "Medium close-up in {lugar}; he holds {prop} at chest height in a full gloved grip, facing the lens.",
  "holding {prop} at chest height", "he pushes {prop} straight toward the lens until it fills the frame and holds it there",
  "holding {prop} close to the lens", "M: say the object keeps its exact shape", props=["case file", "old photograph", "cassette", "ticket", "key"],
  extra="The object keeps its exact shape and surface; no writing appears on it.")
t("LP02", "Finger to the mask (shh)", "gesto", 2, ["pre_reveal"], "raises a finger to the mask", "locked-off close-up",
  "Close-up in {lugar}; one gloved index finger already raised beside the mask.", "with one gloved finger raised beside the mask",
  "he moves the finger in front of the lower part of the mask in a silent hush and tilts his head", "finger in front of the mask, head tilted", "M: one finger, glove on")
t("LP03", "Snap", "gesto", 5, ["transition", "punch"], "snaps his fingers", "locked-off medium close-up",
  "Medium close-up in {lugar}; his gloved hand raised near the lens with the fingers already pinched together.", "with his gloved hand raised, fingers pinched",
  "one snap, the hand drops, a slight lurch toward the lens", "hand lowered, facing the lens", "H: fingers deform; cut on the snap frame and add the sound")
t("LP05", "Head tilt", "gesto", 1, ["question"], "tilts his head", "locked-off close-up", "Locked-off close-up in {lugar}; the mask straight on.",
  "still, straight on", "a slow head tilt to the right, a hold, then slowly back", "straight on again", "L: safe filler")
t("LP06", "Slow turn to camera", "gesto", 2, ["reveal"], "turns to the camera", "locked-off close-up", "SIDE VIEW: a close-up of him in strict profile, his head turned 90 degrees to the left so the camera sees the side of the hood and the edge of the mask, the painted eye not visible; {lugar}.",
  "in profile, looking into the dark", "over four seconds his head turns until the painted eye faces the lens, then stillness", "facing the lens, still", "L")
t("LP07", "Hood pulled down", "gesto", 2, ["whisper"], "pulls the hood down", "locked-off close-up",
  "Close-up in {lugar}; both gloves hold the edge of the hood near his temples.", "holding the hood edge with both gloves",
  "he pulls the hood lower until its shadow falls over the eye", "the hood low, the eye in shadow, facing the lens", "L")
t("LP08", "Palms: wait", "gesto", 3, ["but_wait"], "raises his palms", "locked-off medium shot",
  "Medium shot in {lugar}; both gloves raised at chest height, palms out, fingers together.", "palms raised at chest height",
  "one small push of the palms toward the lens, then a hold", "palms raised, still", "M")
t("LP09", "Slow clap", "gesto", 2, ["irony"], "claps slowly", "locked-off medium shot", "Medium shot in {lugar}; his gloves apart at chest height.",
  "gloves apart at chest height", "three slow claps, then he stops, head tilted", "hands together, head tilted", "M-H: hands large and slow")
# ---------------- angles
t("AN01", "Top-down desk", "angulo", 3, ["evidence", "setup"], "slides a photograph", "camera directly overhead, locked off",
  "Directly overhead view of a desk in {lugar}: an open folder, a map and a few photographs; his gloved hands rest at the edges; the top of his hood at the bottom of the frame.",
  "with his gloves at the edges of the desk", "his hands slide one photograph to the centre and tap it once", "one glove resting on the photograph",
  "M: photos keep their content", props=["folder", "photographs", "map"], extra="The photographs keep their content; no writing appears.")
t("AN02", "From below", "angulo", 3, ["menace"], "bends toward the camera", "very low angle from the floor, locked off",
  "Very low angle from the floor in {lugar}; he stands over the lens, a ceiling bulb behind his head.", "standing over the lens",
  "he slowly bends down into the lens until the hood fills the frame", "the hood filling the frame", "L")
t("AN03", "From above", "angulo", 2, ["aftermath"], "lifts his head", "high angle looking down, slow push-in",
  "High angle looking down at him seated on a chair in {lugar}.", "seated, head lowered", "a slow push-in from above; near the end he lifts his head to the lens",
  "head lifted to the lens", "L")
t("AN04", "Tilted close-up", "angulo", 3, ["wrongness"], "tilts with the frame", "close-up framed at a 20 degree tilt, harsh side light, handheld drift",
  "Close-up framed at a 20 degree tilt in {lugar}, harsh light from one side.", "tilted in the frame", "a slow handheld drift; he rotates his head to match the tilt",
  "head tilted with the frame, facing the lens", "L")
t("AN05", "Over the shoulder", "angulo", 2, ["research"], "looks at a screen", "over-the-shoulder shot, slow push past his shoulder toward the screen",
  "Over his right shoulder in {lugar}: the hood edge in the foreground and {prop} glowing in front of him, out of focus.", "seated before {prop}",
  "the camera pushes slowly past his shoulder toward the glow; at the end he turns his head back to the lens", "head turned back to the lens",
  "L: screen text garbles, keep it blank", props=["an old CRT screen", "a microfilm reader", "a laptop"])
t("AN06", "Ultra-wide close-up", "angulo", 4, ["hook"], "bobs toward the lens", "ultra-wide close-up 30 cm from the lens, handheld micro-shake",
  "Ultra-wide close-up 30 cm from the lens in {lugar}: the mask big, the shoulders small.", "very close to the lens",
  "he bobs slightly closer and tilts his head", "very close, head tilted", "M: distortion can warp the mask; say the mask shape is unchanged",
  extra="The mask shape is unchanged by the lens.")
t("AN07", "Through a gap", "angulo", 2, ["spying"], "turns to the gap", "view through a door gap or blinds, slow push toward the gap",
  "View through a narrow door gap in {lugar}; he sits far away in a medium shot.", "sitting far away, seen through the gap",
  "a slow push toward the gap; near the end he turns his head to the lens", "head turned to the lens", "L")
t("AN08", "Chest camera POV", "angulo", 3, ["exploration"], "walks forward", "chest-mounted camera looking down at his gloves holding a flashlight, walking, bobbing",
  "Chest-mounted camera view in {lugar}: his gloves hold a lit flashlight, its beam on the floor ahead.", "walking with the flashlight",
  "he walks forward, the beam swinging over the walls", "stopped, the beam on the far wall", "M: hands mid-size", props=["flashlight"])
# ---------------- props
t("PR01", "Newspaper lowered", "objeto", 3, ["hook", "reveal"], "lowers a newspaper", "locked-off medium shot",
  "Medium shot in {lugar}; an open old newspaper covers his face, his gloved fingers on its top edge, the page plain grey with no readable print.",
  "behind an open newspaper", "he lowers the paper to chest height and the mask appears, staring at the lens", "the paper at chest height, facing the lens",
  "M: print garbles; overlay the real headline in the edit", props=["old newspaper"], extra="The newspaper print is soft grey blocks; no readable words.")
t("PR02", "Coffee, never drinks", "objeto", 1, ["setup", "calm_open"], "holds a coffee mug", "locked-off medium shot",
  "Medium shot at a table in {lugar}; both gloves around a steaming mug of coffee.", "both gloves around a steaming mug",
  "he lifts the mug to chest height, the steam curls up away from him, he tilts his head and sets it down", "the mug back on the table, facing the lens",
  "L: never bring the mug to the mask", props=["coffee mug"], extra="The mug never touches the mask; the steam rises away from the mask.")
t("PR03", "Coffee from behind", "objeto", 2, ["pause"], "raises a mug", "camera behind him, over the shoulder",
  "Behind him in {lugar}, his hood centred, a mug in his right glove at his side.", "seen from behind, mug at his side",
  "he raises the mug toward his face; the hood hides it; then he lowers it and turns his head toward the lens", "head turned toward the lens",
  "M: the drink stays hidden by the hood", props=["coffee mug"])
t("PR04", "Flashlight under the mask", "objeto", 3, ["campfire_hook"], "switches on a flashlight", "dark locked-off close-up",
  "Dark close-up in {lugar}; a switched-off flashlight held below the mask.", "in the dark, flashlight off below the mask",
  "he clicks it on, the mask lights from below, a slow head tilt", "lit from below, head tilted", "L: the switch-on is in the prompt", props=["flashlight"])
t("PR05", "Flashlight sweep", "objeto", 3, ["escalation", "transition"], "sweeps a flashlight", "dark medium shot, locked off",
  "Dark medium shot in {lugar}; his flashlight already on, pointing at the floor.", "with the flashlight beam on the floor",
  "he sweeps the beam across the room and back to the lens, flaring", "the beam on the lens, flaring", "M: the flare is a good cut point", props=["flashlight"])
t("PR06", "Cassette in", "objeto", 2, ["evidence"], "loads a cassette", "close-up on a tape recorder, locked off",
  "Close-up of an old tape recorder on a table in {lugar}; a cassette in his glove above the slot.", "with a cassette above the slot",
  "he pushes the cassette in, presses play, and turns his head to the lens", "head turned to the lens", "M-H: small parts; keep them large", props=["cassette", "tape recorder"])
t("PR08", "Folder drop", "objeto", 4, ["escalation"], "drops a folder", "locked-off medium shot",
  "Medium shot in {lugar}; he holds a closed thick folder at shoulder height above a desk.", "holding a closed folder at shoulder height",
  "he drops it flat on the desk with a thud and leans over it", "leaning over the folder, facing the lens", "M: prompt a closed folder", props=["closed folder"])
t("PR09", "Map trace", "objeto", 2, ["setup_where"], "traces a route", "top-down on a map, slow push-in",
  "Top-down view of an old map on a table in {lugar}, soft and without readable names; one gloved finger rests on a point.", "finger on the map",
  "the finger slides slowly along a route", "finger at the end of the route", "M: map text garbles; keep it soft", props=["old map"])
t("PR10", "Phone call", "objeto", 3, ["voice_reveal"], "holds a phone receiver", "locked-off close-up",
  "Close-up in {lugar}; an old telephone receiver held against the side of his hood.", "the receiver against his hood",
  "he stays still listening, then slowly turns his head to the lens", "receiver at his hood, facing the lens", "L", props=["old telephone"])
t("PR11", "Screen glow", "objeto", 2, ["episode"], "leans toward a glowing screen", "medium shot lit only by a screen, slow push-in",
  "Medium shot in {lugar}, lit only by {prop} in front of him.", "lit by the screen", "the screen flickers on the mask; he leans closer", "leaning toward the glow, facing the lens",
  "L", props=["an old CRT screen", "an arcade screen", "a radar scope"])
t("PR12", "Match flame", "objeto", 2, ["whisper"], "strikes a match", "locked-off close-up",
  "Close-up in {lugar}; an unlit match in one glove, the matchbox in the other.", "holding an unlit match and the box",
  "he strikes it once; the small flame lights the painted eye; he watches it", "watching the small flame", "M: a small flame only, never smoke",
  props=["matches"], extra="A small clean flame; no smoke at all.")
# ---------------- transitions and loops
t("TR01", "Palm covers the lens", "transicion", 4, ["cut"], "covers the lens", "locked-off medium close-up",
  "Medium close-up in {lugar}; his gloved palm raised at chest height.", "palm raised", "his palm moves to cover the lens completely (black by two seconds)",
  "the lens covered, black", "L: black hides any morph; cut on it")
t("TR03", "Hood into black", "transicion", 3, ["act_break"], "leans into black", "locked-off close-up",
  "Close-up in {lugar}; his head tilting down.", "head tilting down", "he leans forward until the hood fills the frame to black", "the hood filling the frame, black", "L")
t("TR04", "Loop pose", "transicion", 2, ["cta", "loop"], "settles into the opening pose", "same framing as the episode's first narrator shot",
  "The same framing and place as the episode's first narrator shot: {lugar}.", "almost in the opening pose", "he settles into the exact opening pose and holds it",
  "in the opening pose", "L: generate from the first frame")
t("TR06", "Lights off", "transicion", 3, ["ending", "loop"], "switches off the light", "locked-off medium shot",
  "Medium shot in {lugar}; his glove on a lamp chain beside him.", "glove on the lamp chain", "he pulls the chain; the room goes black; only the painted eye catches a faint glint",
  "in the dark, the eye faintly lit", "L", props=["lamp with a chain"])

# ---------------- impossible (review 2026-11-12: "impossible, dangerous things that escape reality, but simple and coherent with
# the story"): physics is broken on purpose and calmly; everything else in the frame stays physically right
IMP = "The impossible balance is deliberate and calm: he never wobbles or falls; everything else in the frame obeys physics."
t("IM01", "Balanced on a tip", "imposible", 4, ["hook", "reveal", "tension"], "stands balanced on a tip", "static wide shot from slightly below, wind moving his robe",
  "Wide shot from slightly below: he stands perfectly upright and still, impossibly balanced on the very tip of {prop}, {lugar}; the empty drop around him.",
  "standing on the very tip of {prop}", "he stays perfectly balanced while the wind whips his robe; slowly he turns his head to the lens",
  "balanced on the tip, facing the lens", "M: the model may make him fall; say he never wobbles", props=["the edge of a roof", "a lamppost", "the tail fin of a plane", "the end of open stairs"], extra=IMP)
t("IM02", "Tightrope", "imposible", 4, ["escalation"], "walks on a wire", "side tracking shot at his height, the drop below",
  "Side view at his height: he walks on a single taut wire strung across {lugar}, high above the ground, arms slightly out, the drop below.",
  "on the wire, mid-step", "he takes three slow calm steps along the wire, then stops and turns his head to the lens", "standing still on the wire, facing the lens",
  "M: keep the wire simple and the steps slow", extra=IMP)
t("IM03", "Chair on one leg", "imposible", 3, ["setup", "irony"], "sits on a tilted chair", "locked-off medium-wide shot at eye level",
  "Medium-wide shot at eye level in {lugar}: he sits calmly on a wooden chair tilted far back, balanced on one single back leg, the other three legs in the air.",
  "seated on the tilted chair", "the chair stays impossibly balanced; he folds nothing, only lifts his head slowly to the lens", "balanced, facing the lens",
  "M: say the chair never falls", props=["wooden chair"], extra=IMP)
t("IM04", "Legs over the void", "imposible", 3, ["pause", "aftermath"], "sits on an edge", "static shot from behind and slightly above, the drop below",
  "From behind and slightly above: he sits on the very edge of {prop}, his legs dangling over a deep drop, {lugar} far below.",
  "seated on the edge", "the wind moves his robe; slowly he turns his head over his shoulder to the lens", "looking back at the lens over his shoulder",
  "L", props=["a rooftop", "a cliff", "the open door of a flying plane", "a bridge girder"], extra=IMP)
t("IM05", "Floating seated", "imposible", 4, ["reveal", "supernatural"], "floats in the air", "locked-off medium-wide shot",
  "Medium-wide shot in {lugar}: he sits cross-legged floating a metre above the ground, perfectly still, his robe hanging down.",
  "floating, still", "he rises a little higher, very slowly, and turns his head to the lens", "floating higher, facing the lens", "M", extra=IMP)
t("IM06", "Standing on a moving vehicle", "imposible", 5, ["hook", "escalation"], "stands on a moving vehicle", "camera tracking alongside, wind and speed",
  "Tracking shot alongside: he stands upright and calm on top of {prop}, {lugar}, the world rushing past, his robe whipping in the wind.",
  "standing on top of {prop}", "he keeps standing calmly as it races; he turns his head to the lens", "standing, facing the lens",
  "H: speed smears; use 3-4 s", props=["the wing of a flying airliner", "the roof of a moving train", "the roof of a speeding car"], extra=IMP)
t("IM07", "Standing on water", "imposible", 3, ["eerie"], "stands on water", "static wide shot at water level",
  "Wide shot at water level: he stands still on the surface of {lugar}, the water rippling around his feet without sinking.",
  "standing on the water", "small ripples spread from his feet; he turns his head slowly to the lens", "standing on the water, facing the lens", "M", extra=IMP)
# ---------------- environment (he touches the place)
t("EN01", "Hand along the wall", "entorno", 2, ["setup", "exploration"], "runs his glove along a surface", "handheld following shot, medium",
  "Medium handheld shot in {lugar}: he walks slowly with his gloved hand touching {prop}.", "walking, glove on {prop}",
  "his glove slides along {prop} as he walks, then he stops and faces the lens", "stopped, facing the lens", "L", props=["a wall", "a railing", "a fence", "the side of a car"])
t("EN02", "Opens a door into the scene", "entorno", 3, ["transition", "reveal_place"], "opens a door", "locked-off shot from inside the room",
  "From inside {lugar}: a closed door; his gloved hand already on the handle, the door just opening, his hood visible in the gap.",
  "hand on the handle, the door ajar", "he pushes the door open and steps into the room, facing the lens", "inside the room, facing the lens", "M")
t("EN03", "Kicks something", "entorno", 4, ["punch"], "kicks", "low static shot at ground level",
  "Low shot at ground level in {lugar}; {prop} lies near his boot.", "standing by {prop}", "he kicks {prop} away with one boot; it skids out of frame", "standing, facing the lens",
  "M: the object keeps its shape", props=["a tin can", "a pile of papers", "sand", "dry leaves"])
# ---------------- details (story told without his mask on screen)
t("DT01", "Gloved hand detail", "detalle", 2, ["evidence", "pause"], "places an object", "extreme close-up on his gloved hand, locked off",
  "Extreme close-up in {lugar}: his gloved hand holds {prop} just above a surface.", "hand holding {prop}", "he slowly sets {prop} down and lifts the hand away",
  "{prop} resting alone", "L: hand big in frame", props=["a tie", "a key", "a ticket", "a coin"], extra="Only his gloved hand is in the frame; the mask is not shown.")
t("DT02", "Boots walking", "detalle", 2, ["transition", "setup"], "walks", "low tracking shot at boot level",
  "Low shot at boot level in {lugar}: his black boots and the hem of his robe mid-step.", "mid-step", "his boots walk forward through the frame and out",
  "the empty ground", "L", extra="Only his boots and robe hem are in the frame.")
t("DT03", "Silhouette in the distance", "detalle", 2, ["mood", "aftermath"], "stands far away", "static extreme wide shot",
  "Extreme wide shot of {lugar}: he is a small dark hooded silhouette far away.", "small and far away", "he stays still while the light changes; the camera pushes in slowly",
  "still a silhouette, slightly closer", "L")

# ---------------- crowds (he is the one still, odd or ignored point in a busy public place tied to the story)
MULT = "a busy public place tied to the story, in its year (a station concourse, a city crossing, a market, a subway car, a square)"
t("MU01", "Still in a rushing crowd", "multitud", 3, ["hook", "eerie"], "stands still in a crowd", "static wide shot at eye level, slow shutter",
  "Wide shot at eye level in {lugar}, packed with people: he stands perfectly still in the middle facing the lens while passers-by stream past him on both sides.",
  "standing still, the crowd flowing around him", "the crowd rushes past in motion blur; he stays sharp and still and tilts his head slightly toward the lens",
  "still in the crowd, facing the lens", "M: faces in the crowd; keep them small and blurred", gente=True, lugar_tipo=MULT)
t("MU02", "Walking against the flow", "multitud", 4, ["setup", "context", "escalation"], "walks against the crowd",
  "handheld camera walking backwards in front of him at chest height",
  "Medium-wide handheld shot in {lugar}, crowded: he walks toward the lens through a crowd that all moves the other way, past his shoulders.",
  "walking toward the lens against the flow", "he keeps walking steadily toward the lens while people part around him without looking",
  "a medium close-up, facing the lens", "M", gente=True, lugar_tipo=MULT)
t("MU03", "Stops in the middle of the crossing", "multitud", 3, ["setup_where", "context"], "stops on a crosswalk",
  "static wide shot from the far side of the street, slightly high",
  "Wide shot from across the street at {lugar}: a busy crosswalk full of pedestrians crossing both ways; he is among them mid-street.",
  "crossing with the pedestrians", "he stops in the middle of the crossing while everyone keeps walking, and turns to face the lens",
  "standing still mid-crossing, facing the lens", "M: walking legs; keep people mid-size", gente=True,
  lugar_tipo="a busy city street crossing tied to the story")
t("MU04", "In the packed carriage", "multitud", 2, ["pause", "mood", "irony"], "rides among strangers", "static medium shot inside the carriage",
  "Medium shot inside {lugar}, a packed carriage: commuters stand and sit close together, swaying; he sits among them facing the lens.",
  "seated among the commuters", "the carriage sways and the lights flicker past the windows; nobody notices him; he leans slightly toward the lens",
  "leaning in, facing the lens", "M", gente=True, lugar_tipo="a train, subway or bus of the story's year")
t("MU05", "The crowd freezes", "multitud", 5, ["reveal", "supernatural", "punch"], "walks through a frozen crowd", "handheld medium-wide shot",
  "Medium-wide shot in {lugar}, crowded: every passer-by is frozen mid-step like statues; he alone is moving, already walking between them toward the lens.",
  "walking between the frozen people", "he walks between the frozen people toward the lens; nobody else moves at all",
  "a medium close-up in front of the frozen crowd, facing the lens", "H: the frozen people start moving; keep the clip short (4-5 s)",
  gente=True, lugar_tipo=MULT, extra="The frozen people are completely motionless for the whole clip: no blinking, no swaying.")
t("MU06", "Found from above", "multitud", 3, ["hook", "reveal_place"], "looks up from a crowd", "overhead drone shot pushing straight down",
  "High overhead shot looking straight down on {lugar}, full of people moving in every direction; he is one small still dark hood among them.",
  "a small dark hood among the crowd", "the camera descends straight toward him while the crowd moves; he tilts his mask up to the lens",
  "close above him, mask tilted up to the lens", "M: small figures; hood stays recognisable", gente=True, lugar_tipo=MULT)
# ---------------- documentary (observational camera grammar: far, hidden, following, framed)
t("DO01", "Long-lens zoom to him", "documental", 4, ["hook", "reveal"], "talks to a far camera",
  "long telephoto lens from far away across the place, a fast smooth zoom in from an extreme wide shot to a medium close-up",
  "Extreme wide telephoto shot from far across {lugar}: he is a tiny dark hooded figure in the distance, already facing this far camera.",
  "tiny in the distance, facing the camera", "the camera zooms in fast and smoothly across the whole distance until he fills the frame, talking calmly to the lens",
  "a medium close-up through the long lens, compressed background, facing the lens", "M: zoom speed smears; keep the zoom to the first 3 s")
t("DO02", "Security camera", "documental", 3, ["evidence", "eerie", "spying"], "stares up at a security camera",
  "fixed high corner security-camera angle, wide lens, grainy black-and-white",
  "High corner security-camera view of {lugar}, grainy black-and-white, slightly fish-eye; he stands below, already looking up at the camera.",
  "standing below, looking up", "he walks slowly closer under the camera and keeps staring up into it",
  "close under the camera, mask tilted up to the lens", "L", extra="No timestamp, no on-screen text: the image is clean.")
t("DO03", "Following him", "documental", 3, ["setup", "exploration"], "is followed", "handheld camera following close behind him at shoulder height",
  "Handheld shot from close behind him in {lugar}: his black hood and shoulders fill the lower frame as he walks away from the camera.",
  "walking away from the camera", "he walks a few steps, stops, and turns around to face the lens as if he knew he was followed",
  "turned around, facing the lens", "M: the turn; the mask must stay the same", sigue="he steps toward the lens and talks.")
t("DO04", "Across the street", "documental", 2, ["context", "spying"], "talks across a street",
  "static telephoto shot from across a street, traffic and people crossing the foreground",
  "Telephoto shot from across the street at {lugar}: he stands on the far pavement facing the lens; cars and passers-by cross the foreground, partly blocking him.",
  "on the far pavement, facing the lens", "traffic and people pass in the foreground; in each gap he is still there, calmly talking to the lens",
  "seen through a gap in the traffic, facing the lens", "M", gente=True, lugar_tipo="a street of the story's place and year")
t("DO05", "Interview chair", "documental", 2, ["context", "research", "pause"], "sits for an interview",
  "locked-off documentary interview framing, medium shot, he sits slightly off-centre",
  "Documentary interview framing in {lugar}: he sits in a chair slightly off-centre, his mask turned just off the lens toward an unseen interviewer, one soft key light.",
  "seated, looking just off the lens", "he answers calmly, then slowly turns his mask from the interviewer to look straight into the lens",
  "seated, looking straight into the lens", "L")
t("DO06", "Drone pull-back", "documental", 3, ["aftermath", "reveal_place", "loop"], "is left behind by the camera",
  "camera pulls back and rises smoothly like a drone, from a medium shot to a high wide shot",
  "Medium shot in {lugar}: he stands facing the lens; the place stretches out behind him.",
  "facing the lens", "the camera pulls back and rises while he stays still and keeps looking up at it, until the whole place is revealed and he is small",
  "a high wide shot of the place, he is small and still looking up", "L")
t("DO07", "Rack focus", "documental", 2, ["evidence", "tension"], "waits behind an object", "static close shot, focus pulls from foreground to background",
  "Close shot in {lugar}: {prop} sharp in the foreground; he stands behind it out of focus, a soft dark shape facing the lens.",
  "a blurred shape behind {prop}", "the focus slowly shifts from {prop} to him; he becomes sharp, facing the lens", "sharp, behind the blurred {prop}, facing the lens",
  "L", props=["a ticket on a counter", "a glass of water", "a photograph on a table", "a key on a table"])
t("DO08", "Snap zoom", "documental", 4, ["punch", "scare"], "is snap-zoomed", "static medium shot with one sudden fast zoom in",
  "Medium shot in {lugar}: he stands calmly, talking to the lens.", "medium shot, talking",
  "on one key word the camera snaps in fast to an extreme close-up of his mask and holds",
  "an extreme close-up of the mask, very still", "M: the snap smears; cut on it")

for x in T:   # shots that move toward him lose background detail by design (clips.py broken-clip check)
    x["acerca"] = x["id"] in {"CH01", "CH02", "CH03", "CH04", "CH05", "CH06", "CH07", "LP01", "AN02", "AN03", "AN06", "DT02", "DT03", "PR11", "AN05", "AN07", "PR03", "LP06", "IM04", "CH08", "MU02", "MU05", "MU06", "DO01", "DO03", "DO06", "DO07", "DO08"}
out = Path("D:/short_dna/library/tomas/tomas.json"); out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({"_doc": "Dynamic narrator shots (engine/tomas_lib.py). Crowd shots (gente: true) need a busy public place tied to the story (lugar_tipo). Research 2026-11-12: 10 reference Shorts (median shot 2.1 s, prop-to-lens the top energiser, longest hold on the reveal). Risk: L low, M medium, H likely to fail in AI video. Cut each 8 s clip into 2-3 shots in the edit.",
                           "tomas": T}, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(T), "shots")
