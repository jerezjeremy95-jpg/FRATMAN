---
description: Revisa un copy con el Guardián de marca y claims en Sonnet, y delega en Opus el juicio de las piezas sensibles (salud, alcohol, datos, sorteos, menores)
argument-hint: "[marca] [copy pegado o ruta del archivo]"
model: sonnet
effort: medium
---

Usa la skill `guardian-marca` para revisar la pieza de abajo. Lee primero el Core Brand de la marca. Si no se sabe de qué marca es, pregúntalo en una línea antes de empezar.

Si la pieza toca salud (promete algo al cuerpo o a la mente), alcohol, datos personales, sorteos o menores, o va a pauta pagada, delega el juicio de claims en el subagente `auditor-claims` (Opus, esfuerzo alto) y arma tú el reporte final.

$ARGUMENTS
