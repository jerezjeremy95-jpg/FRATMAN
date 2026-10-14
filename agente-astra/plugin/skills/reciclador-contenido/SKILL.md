---
name: reciclador-contenido
description: Reciclador de contenido de Astra. Toma una pieza ya aprobada (carrusel, post del Design Board, caption o guion) y la convierte en un paquete multicanal (guion de Reel, secuencia de Stories, post de LinkedIn y 2 o 3 variantes de caption) sin agregar claims nuevos, en el tono del Core Brand y con pase final del Guardián. Úsala cuando pidan reciclar, reutilizar, adaptar, "sacarle más jugo" a un post o carrusel, convertirlo en Reel, Stories o LinkedIn, o hacer variantes de caption para una marca.
---

# Reciclador de contenido

Una pieza aprobada se convierte en un paquete para varios canales. La regla de oro: **se cambia el formato, no la promesa**. El mensaje, los datos y los claims salen de la pieza original. Así el paquete hereda la aprobación que ya tuvo la pieza y el riesgo no crece.

## Entradas
1. **La pieza aprobada.** Puede ser el texto de un carrusel (por slide), un post del Design Board (campos `POST N`, `Texto` o `Texto imagen 1/2…`, `Copy`, `Fondo`, `Letras`, `Imagen`), un caption o un guion. Si llega en imagen o PDF, transcríbela primero.
2. **La marca y su Core Brand** (Drive: `/Astra/Clientes/[Marca]/00_Core_Brand`): tono, persona gramatical, público, prohibiciones y claims aprobados.
3. **Canales.** Por defecto los cuatro: Reel, Stories, LinkedIn y captions. Haz solo los que pidan, si piden menos.
4. **Opcionales:** objetivo (alcance, guardados, reservas, leads B2B), fecha o temporada, CTA fijo ("link en la bio"), duración del Reel y quién puede salir en cámara.

Si no te dicen que la pieza está aprobada, sigue igual, pero pasa también la pieza original por el Guardián y avisa arriba: **"Pieza original sin aprobación confirmada"**.

Referencias de esta skill:
- `references/formatos-canal.md`: estructura y medidas de cada canal. Léelo antes de escribir.
- `references/claims-riesgo.md`: lo que no se puede prometer y cómo decirlo bien.
- `references/principios-astra.md`: reglas de la agencia.

## Proceso

### 1. Materia prima (antes de escribir nada)
Saca de la pieza original:
- **Idea central** en una frase.
- **Puntos de apoyo** (3 a 5).
- **Inventario de claims y datos**: copia literal de todo lo que la pieza afirma (beneficios, cifras, precios, fechas, ingredientes, lugares, nombres). **Es la única fuente permitida.** Todo lo que el paquete afirme tiene que estar en este inventario o en los claims aprobados del Core Brand.
- **CTA** original y palabras del tono que conviene repetir.
- **Elementos visuales** (colores, estilo, fotos disponibles) si vienen del Design Board.

### 2. Adaptar por canal
Sigue `references/formatos-canal.md`. Cada canal toma un ángulo distinto de la misma idea; no es copiar y pegar el mismo texto:
- **Reel:** el punto más visual o sorprendente como gancho en los primeros 3 segundos.
- **Stories:** la idea en 3 a 5 pantallas, con al menos una interacción (encuesta, pregunta, quiz o slider) y CTA al final.
- **LinkedIn:** el ángulo de negocio o de oficio: proceso, detrás de cámaras, decisión, comunidad. Va en la página de LinkedIn de la marca. Si es para el LinkedIn de Astra (caso de éxito), primero hace falta la autorización del cliente: márcalo en "Por confirmar".
- **Captions:** 3 variantes con intención distinta: A corta, B historia y C conversación (termina en pregunta).

### 3. Si falta un dato
No lo inventes. Si un canal lo necesita (fecha, horario, precio, dirección, cupos), escribe `[confirmar: dato]` y súmalo a la lista "Por confirmar". Mejor un hueco visible que un dato falso.

### 4. Verificación mecánica
Si puedes ejecutar código, corre `scripts/verificar_copy.py` (está en la carpeta de esta skill) sobre el paquete, con las palabras prohibidas y la leyenda obligatoria del Core Brand:
`python3 scripts/verificar_copy.py paquete.md --prohibidas "palabra1,palabra2" --leyenda "texto exacto"`
El script revisa que los tiempos del Reel cuadren y cuenta caracteres y hashtags mejor que un modelo de lenguaje. Corrige lo que marque. Si no puedes ejecutar código, revisa esos puntos a mano.

### 5. Pase del Guardián
Revisa el paquete completo con el criterio de `references/claims-riesgo.md`, como lo haría el Guardián (o invoca la skill `guardian-marca` si está disponible). Aplica las correcciones **antes** de entregar y cuenta qué cambiaste. Revisa sobre todo:
- Que no aparezca ningún beneficio, cifra o dato fuera del inventario.
- Que se respeten las prohibiciones del Core Brand en guion, Stories, LinkedIn y captions.
- Que el texto en pantalla y los stickers también estén limpios.

### En Cowork o Claude Code con el plugin agente-astra
- Extraer la pieza de un archivo o de un DB largo: subagente `agente-astra:extractor-piezas` (Haiku).
- Escribir las adaptaciones: subagente `agente-astra:redactor-multicanal` (Sonnet). Pásale la materia prima, el inventario de claims, el Core Brand y la ruta de `references/formatos-canal.md`.
- Verificación mecánica: subagente `agente-astra:verificador-formato` (Haiku), con la ruta de `scripts/verificar_copy.py`.
- Pase del Guardián en marcas de salud, bienestar, alimentos o alcohol: subagente `agente-astra:auditor-claims` (Opus), con la ruta de `references/claims-riesgo.md`. En las demás marcas, hazlo tú.

## Formato de salida

```
## Reciclaje — [Marca] · desde: [pieza original] · [AAAA-MM-DD]

**Materia prima**
- Idea central: …
- Inventario de claims y datos permitidos: "…", "…"
- CTA original: …

### 1. Reel · [duración] s
| Tiempo | Toma / visual | Texto en pantalla | Voz o audio |
|---|---|---|---|
| 0–3 s | … | … | … |
**Audio:** [tipo de audio: original, voz en off o biblioteca comercial; sin canciones comerciales]
**Caption del Reel:** …

### 2. Stories ([n] pantallas)
| # | Visual | Texto | Interacción |
|---|---|---|---|

### 3. Post de LinkedIn
[Post completo. Las 2 primeras líneas son el gancho.]

### 4. Captions
**A · Corta:** …
**B · Historia:** …
**C · Conversación:** …

### Pase del Guardián
**Veredicto:** 🟢 | 🟡 | 🔴 — [cambios aplicados en una lista corta]

### Por confirmar
- [confirmar: …]

REGISTRO-GUARDIAN {…una sola línea, mismo formato que la skill guardian-marca, con "pieza":"Reciclaje de …"}
```

## Qué no hacer
- No agregar beneficios, cifras, precios, fechas, premios ni testimonios que no estén en la pieza.
- No cambiar la oferta ni las condiciones de la pieza original.
- No usar canciones comerciales, logos de terceros ni personas que no estén autorizadas.
- No publicar, programar ni enviar nada: entregas un borrador para el equipo.
- No rellenar: si un canal no le sirve a esta pieza (por ejemplo, LinkedIn para una promo de un día), dilo y propón no hacerlo.
