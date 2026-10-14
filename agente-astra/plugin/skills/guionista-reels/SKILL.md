---
name: guionista-reels
description: Guionista de Reels para las marcas de Astra. Convierte una idea, un brief, una señal del Radar Cibao o una fecha (temporada de béisbol, Navidad, fin de año) en un guion de Reel listo para grabar: 3 hooks, tabla de tomas con tiempos, texto en pantalla, voz, audio seguro, CTA, caption y notas de producción, en el tono del Core Brand y sin claims riesgosos. Úsala cuando pidan un guion, un Reel, un TikTok, un video corto, "qué grabamos" o ideas de video para una marca, aunque no digan "guion".
---

# Guionista de Reels

Escribe Reels que se puedan grabar con lo que el equipo tiene a mano y que el cliente pueda aprobar sin sustos. Un buen guion de Astra es: claro en el segundo 1, local sin ser cliché, en la voz de la marca y sin promesas que no se puedan sostener.

## Entradas
1. **Marca y Core Brand** (Drive: `/Astra/Clientes/[Marca]/00_Core_Brand`): tono, pilares, público, prohibiciones y claims aprobados.
2. **Idea o brief.** Si viene del Radar Cibao, conserva su fuente y su fecha límite.
3. **Objetivo:** alcance, comunidad, venta o asistencia a un evento o activación.
4. **Recursos:** quién puede salir en cámara (talento, empleados o nadie), locación, producto y nivel de producción. Por defecto: celular, una locación y sin talento pagado.
5. **Duración.** Por defecto, entre 15 y 30 segundos. Si la idea necesita más, justifícalo.

Lo que falte, asúmelo con la opción más sencilla y márcalo `[confirmar: …]`. No frenes el trabajo por preguntas que el equipo puede contestar después.

Referencias de esta skill:
- `references/formatos-canal.md`: medidas, zonas seguras y estructura de Reels y Stories.
- `references/temporadas.md`: temporada de béisbol, feriados y fechas comerciales de octubre a febrero, con lo que hay que verificar.
- `references/claims-riesgo.md`: lo que no se puede prometer, sobre todo en salud, alcohol y marcas de terceros.
- `references/principios-astra.md`: reglas de la agencia.

## Proceso
1. **Ángulo en una frase:** "Para [público], mostrar [idea] para que [acción]". Si no cabe en una frase, la idea está muy abierta: elige una sola.
2. **Tres hooks distintos** (primeros 3 segundos, imagen y texto):
   - **Pregunta o reto:** algo que el público se pregunta de verdad.
   - **Contraste o sorpresa:** un antes y después de situación (nunca de cuerpo), o algo inesperado.
   - **POV o situación local:** una escena que cualquiera en Santiago o el Cibao reconoce.
   Recomienda uno y explica en una línea por qué.
3. **Estructura:** hook (0 a 3 s), desarrollo en tomas cortas de 2 a 4 s con una idea por toma, remate y CTA en los últimos 2 o 3 segundos. Los tiempos de la tabla tienen que sumar la duración total.
4. **Texto en pantalla:** corto y legible en un vistazo, fuera de las zonas que tapa la interfaz (ver `formatos-canal.md`). El video se tiene que entender sin sonido.
5. **Audio:** audio original, voz en off o la biblioteca de audio comercial de la plataforma. Las canciones en tendencia muchas veces no están disponibles para cuentas de empresa; si propones un tipo de música, describe el estilo y no una canción comercial.
6. **Contexto local y temporadas.** Usa `references/temporadas.md` y verifica las fechas antes de ponerlas en el guion.
   - **Béisbol:** sin logos, uniformes, mascotas ni nombres oficiales de la liga o los equipos, salvo licencia o patrocinio confirmado. Las referencias genéricas sí funcionan: "noche de pelota", "la pelota invernal", el ambiente del estadio, el colmado viendo el juego.
   - **Fechas religiosas** (por ejemplo, Altagracia o Reyes): tono respetuoso y sin símbolos religiosos como gancho comercial.
7. **Verificación mecánica.** Si puedes ejecutar código, corre `scripts/verificar_copy.py` (está en la carpeta de esta skill) sobre el guion para confirmar que los tiempos cuadran con la duración y que no hay palabras prohibidas ni falta la leyenda obligatoria: `python3 scripts/verificar_copy.py guion.md --prohibidas "…" --leyenda "…"`.
8. **Pase del Guardián** al guion completo (hooks, texto en pantalla, voz y caption) con el criterio de `references/claims-riesgo.md`. Corrige antes de entregar.

### En Cowork o Claude Code con el plugin agente-astra
- Escribir hooks, tomas y caption: subagente `agente-astra:redactor-multicanal` (Sonnet), con la ruta de `references/formatos-canal.md`.
- Revisar que los tiempos sumen y contar caracteres: subagente `agente-astra:verificador-formato` (Haiku), con la ruta de `scripts/verificar_copy.py`.
- Pase del Guardián en marcas de salud, bienestar, alimentos o alcohol: subagente `agente-astra:auditor-claims` (Opus), con la ruta de `references/claims-riesgo.md`.

## Formato de salida

```
## Guion Reel — [Marca] · [idea] · [duración] s · [AAAA-MM-DD]
**Ángulo:** …
**Objetivo:** … · **Fuente de la idea:** [Radar Cibao, fecha / brief / fecha comercial]

**Hooks**
1. Pregunta: …
2. Contraste: …
3. POV local: …
**Recomendado:** n.º X, porque …

| Tiempo | Toma | Acción | Texto en pantalla | Voz o audio |
|---|---|---|---|---|
| 0–3 s | … | … | … | … |

**CTA:** …
**Audio:** …
**Caption:** … (con 1 o 2 emojis y CTA)

**Notas de producción**
- Lista de tomas para grabar en orden práctico (no en orden de edición).
- Props, locación y quién sale en cámara.
- Permisos: autorización de imagen de quien aparece, permiso de la locación y licencias si aplican.

### Pase del Guardián
**Veredicto:** 🟢 | 🟡 | 🔴 — [cambios aplicados]

### Por confirmar
- [confirmar: …]

REGISTRO-GUARDIAN {…una sola línea, mismo formato que la skill guardian-marca, con "pieza":"Guion Reel: …"}
```

## Qué no hacer
- No poner antes y después de cuerpos, ni promesas de salud, peso o energía.
- No mostrar marcas, logos, uniformes ni canciones de terceros sin licencia confirmada.
- Con alcohol: nada de menores ni de personas que parezcan menores, nada de conducir, de exceso ni de rendimiento deportivo. Incluye la leyenda de consumo responsable.
- No poner personas en cámara si la marca o el brief dicen "sin personas": resuélvelo con producto, espacios, texto y voz.
- No inventar datos para el gancho ("el 80 % de los dominicanos…"). Si no hay fuente, el gancho es otro.
- No publicar ni programar: entregas un guion para que el equipo lo apruebe.
