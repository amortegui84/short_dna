# Guiones para revisar: primeros episodios con la fórmula de variedad

La plantilla es la misma (cabeza, obra, cabeza, obra). Cambian el gancho, el orden, el tono y el final, y cada línea de la
cabeza trae su dirección de actuación: emoción, cómo entra (enlazada con la escena anterior), el gesto y cómo sale (la pose
donde se corta). Fórmula general: `docs/templates/variedad.md`. QA: `python engine/qa_guion.py <proyecto>` (los dos pasan).

## Ep 01 · Hilma af Klint
**Combinación:** apertura en frío · orden de revelación · tono de asombro · final con giro · presentador chico

| # | En pantalla | Texto | Emoción | Entra | Gesto | Sale (corte) |
|---|---|---|---|---|---|---|
| L01 | Obra en frío (The Ten Largest), silencio y luego voz | These paintings are taller than a door. They were painted in 1907, before anyone called anything abstract art. | — | — | — | corte a la cabeza |
| L02 | Cabeza | The woman who painted them said she didn't paint them alone. | asombro contenido | ya inclinado hacia la cámara, como si acabara de ver las pinturas con nosotros | las cejas suben lento en "didn't paint them alone", sonrisa de incredulidad | quieto, ojos muy abiertos → The Five |
| L03 | Obra (Primordial Chaos) | Five women met every week in Stockholm for séances. They called themselves The Five. | — | — | — | → cabeza |
| L04 | Cabeza → lupas sobre las espirales | Zoom into the spirals: no sketches underneath. She swore the shapes came all at once. | curiosidad intensa | desde neutro, entrecierra los ojos | se acerca a la lente como mirando dentro del cuadro en "zoom into the spirals"; abre los ojos de golpe en "all at once" | ojos abiertos, labios entreabiertos → la cita |
| L05 | Cita en tiras | "The pictures were painted directly through me, without any preliminary drawings, and with great force." | — | — | — | → cabeza |
| L06 | Cabeza | She showed them to the most famous mystic of her time. He said nobody would understand them for fifty years. | indignación suave por ella | mirada baja y quieta después de la cita, por respeto, y sube a la cámara | inclina la cabeza en "the most famous mystic"; niega lento una vez en "fifty years" | mirada firme y seria → "dejó de pintar" |
| L07 | Obras (The Swan, Altarpiece) | She stopped painting for four years. Then she came back and finished the series. | — | — | — | → ficha |
| L08 | **Ficha** (la revelación) | Her name was Hilma af Klint. Stockholm, 1862 to 1944. | — | — | — | → cabeza |
| L09 | Cabeza | Before she died, she asked that this work stay hidden until twenty years after her death. | complicidad, un secreto | muy cerca de la lente, como a punto de susurrar | baja la voz; los ojos quietos en "stay hidden"; un parpadeo lento en "twenty years" | se queda cerca y quieto un instante → salto de encuadre |
| L10 | Cabeza (cerrado) | In 2019, her show became the most visited in the Guggenheim's history. The mystic was wrong. It took a century. | orgullo y asombro final | cae grande con el golpe de zoom; sonrisa orgullosa que crece en "most visited" | ceja en "the mystic was wrong"; en "it took a century" sostiene la mirada en silencio con un leve gesto de no poder creerlo | quieto, sonriendo, mirándonos: aparece el botón |

153 palabras, unos 58 s. El chico todavía no tiene imagen aprobada; si lo prefieres, lo hace la chica.

## Ep 04 · Odilon Redon
**Combinación:** orden al espectador · cita primero · tono seco · final callback · presentadora chica

| # | En pantalla | Texto | Emoción | Entra | Gesto | Sale (corte) |
|---|---|---|---|---|---|---|
| L01 | Cabeza → lupa sobre el ojo | Pause on the sky. That balloon has an eye, and it is looking straight at you. | seca, inexpresiva | cara de póker, mirada fija en la lente | en "looking straight at you" solo los ojos suben lento al cielo y vuelven | ojos de vuelta a la cámara, cero expresión → la cita |
| L02 | Cita en tiras | "My drawings inspire, and are not to be defined." | — | — | — | → cabeza |
| L03 | Cabeza | So, don't ask what it means. He won't tell you. He's been dead since 1916. | desinterés irónico | con la misma cara plana con la que salió | un parpadeo lento en "he won't tell you"; mínimo encogimiento de cabeza en "dead since 1916" | inmóvil → ficha |
| L04 | Ficha | Odilon Redon. Bordeaux, 1840. Born Bertrand: he took the name Odilon from his mother, Odile. | — | — | — | → cabeza |
| L05 | Cabeza → un noir | For decades he drew only in black. Charcoal, lithographs. He called them his noirs. | seca | plana, la voz pareja | las cejas casi no se mueven; un asentimiento mínimo en "his noirs" | quieta → los dibujos negros |
| L06 | Obras (un noir, el ojo-globo) | In 1884 a famous novel gave its decadent hero a collection of Redon drawings. Suddenly, Paris wanted one. | — | — | — | → cabeza |
| L07 | Cabeza → flores en pastel | Then, after 1900, the black stopped. Pastels, oil, colour everywhere. Same man. | sorpresa contenida | plana | los ojos se abren un instante en "colour everywhere" y vuelven planos en "same man" | plana otra vez, como si nada → las flores |
| L08 | Obras (flores, The Cyclops) | In 1913, New York's Armory Show gave him more space than any other artist. | — | — | — | → cabeza |
| L09 | Cabeza | He wanted the logic of the visible at the service of the invisible. A very normal goal. | ironía | cara de póker perfecta mientras lo cita | una ceja sube en "a very normal goal" | la ceja queda arriba → salto de encuadre |
| L10 | Cabeza (cerrado) | So. The balloon with the eye? It is still looking at you. Don't look up. | seca, un poco inquietante | cae grande con el golpe de zoom, cara de póker | los ojos suben y vuelven en "still looking at you"; en "don't look up" queda totalmente quieta y parpadea lento | quieta, mirándonos: aparece el botón |

145 palabras, unos 55 s.

## Qué falta antes de producir (no se hizo: solo guiones)
- Bajar las obras de dominio público y confirmar los títulos exactos (lista en `obras_por_bajar` de cada proyecto).
- Voz, clips, armado y render (H3 local o Seedance), cuando se aprueben los guiones.
- Al aprobar: `python engine/qa_guion.py <proyecto> --registrar` los agrega a `episodios.json`.
