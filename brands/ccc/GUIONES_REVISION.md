# Guiones para revisar: primeros episodios con la fórmula de variedad

La plantilla es la misma (cabeza, obra, cabeza, obra). Cambian el gancho, el orden, el tono y el final.
Fórmula general: `docs/templates/variedad.md`. QA: `python engine/qa_guion.py <proyecto>` (los dos pasan).

## Ep 01 · Hilma af Klint
**Combinación:** apertura en frío · orden revelación · tono asombro · final giro · presentador chico.
Se diferencia de Dürer y Blake en que abre sin cabeza, sobre las pinturas, y no dice quién es la artista hasta la línea 8.
Cierra con un dato que da vuelta la historia, sin pregunta de debate.

| # | Pantalla | Texto (inglés, como se dice) |
|---|---|---|
| L01 | Obra en frío: The Ten Largest | These paintings are taller than a door. They were painted in 1907, before anyone called anything abstract art. |
| L02 | Cabeza (asombro) | The woman who painted them said she didn't paint them alone. |
| L03 | Obra: Primordial Chaos | Five women met every week in Stockholm for séances. They called themselves The Five. |
| L04 | Cabeza, luego lupas sobre las espirales | Zoom into the spirals: no sketches underneath. She swore the shapes came all at once. |
| L05 | Cita en tiras | "The pictures were painted directly through me, without any preliminary drawings, and with great force." |
| L06 | Cabeza | She showed them to the most famous mystic of her time. He said nobody would understand them for fifty years. |
| L07 | Obras: The Swan, Altarpiece | She stopped painting for four years. Then she came back and finished the series. |
| L08 | **Ficha** (revelación) | Her name was Hilma af Klint. Stockholm, 1862 to 1944. |
| L09 | Cabeza (secreto) | Before she died, she asked that this work stay hidden until twenty years after her death. |
| L10 | Cabeza (giro) | In 2019, her show became the most visited in the Guggenheim's history. The mystic was wrong. It took a century. |

153 palabras, unos 58 s. El chico todavía no tiene imagen aprobada; si lo prefieres, lo hace la chica.

## Ep 04 · Odilon Redon
**Combinación:** gancho orden al espectador · cita primero · tono seco · final callback · presentadora chica.
Abre ordenándote mirar el cielo de la obra. La cita del artista va en la segunda línea, el tono es seco y sin
exageración, y el final vuelve al gancho ("Don't look up") en vez de preguntar.

| # | Pantalla | Texto |
|---|---|---|
| L01 | Cabeza, luego lupa sobre el ojo | Pause on the sky. That balloon has an eye, and it is looking straight at you. |
| L02 | Cita en tiras | "My drawings inspire, and are not to be defined." |
| L03 | Cabeza (seca) | So, don't ask what it means. He won't tell you. He's been dead since 1916. |
| L04 | Ficha | Odilon Redon. Bordeaux, 1840. Born Bertrand: he took the name Odilon from his mother, Odile. |
| L05 | Cabeza, luego un noir | For decades he drew only in black. Charcoal, lithographs. He called them his noirs. |
| L06 | Obras: un noir, el ojo-globo | In 1884 a famous novel gave its decadent hero a collection of Redon drawings. Suddenly, Paris wanted one. |
| L07 | Cabeza, luego flores en pastel | Then, after 1900, the black stopped. Pastels, oil, colour everywhere. Same man. |
| L08 | Obras: flores, The Cyclops | In 1913, New York's Armory Show gave him more space than any other artist. |
| L09 | Cabeza | He wanted the logic of the visible at the service of the invisible. A very normal goal. |
| L10 | Cabeza (callback) | So. The balloon with the eye? It is still looking at you. Don't look up. |

145 palabras, unos 55 s.

## Qué falta antes de producir (no se hizo: solo guiones)
- Bajar las obras de dominio público y confirmar los títulos exactos (lista en `obras_por_bajar` de cada proyecto).
- Voz, clips, armado y render (H3 local o Seedance), cuando se aprueben los guiones.
- Al aprobar: `python engine/qa_guion.py <proyecto> --registrar` los agrega a `episodios.json`.
