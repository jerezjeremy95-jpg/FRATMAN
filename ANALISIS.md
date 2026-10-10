# Análisis: cómo funciona el detector de IA de JustDone

> Nota: el sitio `justdone.com` no fue accesible desde el entorno donde se hizo este análisis (el proxy bloquea el dominio). La información sale de reseñas públicas citadas al final. Comprueba precios y límites actuales en su web antes de tomar decisiones.

## 1. Qué ofrece

- **Detector de texto IA**: pegas texto o subes un archivo (PDF, Word, TXT) y devuelve una probabilidad global de IA y un informe por oración con las líneas resaltadas.
- **Límite por análisis**: según las reseñas, hasta unas 15 000 palabras por escaneo en planes de pago; en el plan gratuito, unas 80 palabras por escaneo.
- **Herramientas del mismo paquete**: humanizador (reescribe el texto para que no lo detecten), parafraseador, detector de plagio, corrector y asistente de redacción.

## 2. Cómo detecta (lo que se sabe)

JustDone no publica su modelo. Las reseñas describen una combinación de:

| Señal | Qué mide |
|---|---|
| Predictibilidad (perplejidad) | Qué tan esperable es cada palabra para un modelo de lenguaje. El texto generado es más predecible. |
| Ritmo (burstiness) | Variación en la longitud y estructura de las oraciones. Los humanos alternan más. |
| Frases genéricas | Giros que los modelos repiten («es importante destacar», «delve», «in today's…»). |
| Clasificador entrenado | Un modelo entrenado con corpus de texto humano y de IA que combina lo anterior en una probabilidad. |

El cálculo ocurre en sus servidores: el navegador envía el texto a su API y recibe la puntuación global y la puntuación por oración.

## 3. Cómo monetiza (el embudo)

1. **Página SEO gratuita** (`/ai-detector`): capta tráfico de búsquedas como «AI detector» o «detector de IA».
2. **Prueba gratuita muy limitada**: unas 80 palabras por escaneo. Basta para ver el resultado, no para usarlo de verdad.
3. **Registro obligatorio** para ver informes completos o textos largos.
4. **Prueba de pago barata**: las reseñas mencionan acceso de 7 días por unos 2 USD que se renueva automáticamente a una suscripción mensual (entre 19,99 y 39,99 USD/mes según la fuente).
5. **Venta cruzada**: el detector marca el texto como IA y ofrece «humanizarlo» con un clic dentro del mismo producto. Detectar y evadir la detección en la misma plataforma es un conflicto de interés evidente.

## 4. Precisión

Las reseñas coinciden en que sirve como filtro inicial, no como prueba. El propio sitio admite que ningún detector es exacto y que hay falsos positivos y falsos negativos. Una comparativa de 2026 lo situó por detrás de otros detectores.

## 5. Nuestra versión: Lupa

`index.html` es una herramienta propia (marca, textos y diseño originales), **gratis, sin registro y sin límite de usos**:

- Entrada por texto pegado, arrastrar archivo o subir `.txt`, `.docx` (mammoth) y `.pdf` (pdf.js).
- Hasta **50 000 palabras** por análisis (mínimo 40). Un texto de 50 000 palabras se analiza en unos 2 segundos.
- Probabilidad global, reparto IA / revisar / humano por palabras y resaltado por oración.
- Las palabras y pares de palabras que más empujaron hacia IA o hacia humano, en el documento y en cada oración.
- Señales de estilo explicadas (variación entre oraciones, conectores, primera persona, puntuación, vocabulario).
- Todo se calcula en el navegador: el texto no se envía a ningún servidor.

### Modelo entrenado (versión 2)

Lupa usa una regresión logística entrenada (detalles y cómo reentrenarla en `model/README.md`):

- **Rasgos**: palabras, pares de palabras y fragmentos de 3 a 5 letras (hasheados en 262 144 posiciones) + 15 medidas de estilo.
- **Datos**: unos 113 000 fragmentos de AuTexTification (español e inglés, GPT-3 y BLOOM), Ghostbuster (ensayos, noticias y relatos en inglés, ChatGPT y Claude), Europarl y noticias EFE (español humano formal) y 86 textos en español escritos con un asistente de IA actual.
- **Pesos**: cuantizados a 8 bits e incrustados en la página (unos 340 KB). El navegador reproduce exactamente el cálculo de Python (diferencia máxima 0,000001 en la probabilidad; 0 en la puntuación global).

### Auditoría de precisión

`model/evaluate.py` mide la página tal como funciona (separación en oraciones, ventanas de ~40 palabras por oración, bloques de ~150 palabras por documento) sobre 16 125 documentos de prueba congelados (`model/test_groups.json`) que ningún modelo usó para entrenar.

La auditoría encontró tres fallos en la versión 1, ya corregidos:

1. **Longitud como atajo**: la versión 1 usaba la longitud del texto como rasgo. En los corpus la longitud se correlaciona con la etiqueta, así que el resultado dependía del tamaño del fragmento y no del estilo. La versión 2 no la usa y se entrena con fragmentos tomados de cualquier parte de los documentos (no solo del inicio), con la misma distribución de longitudes para textos humanos y de IA.
2. **PDF y texto pegado con renglones partidos**: cada salto de línea cortaba la oración. Con renglones de PDF, los textos humanos marcados como IA subían del 17 % al 39 %. Ahora un salto simple no corta la oración y los PDF se reconstruyen por párrafos.
3. **Resaltado por oración**: en documentos que mezclan párrafos humanos y de IA, la versión 1 marcaba como IA la mitad de las oraciones humanas.

| Misma prueba, lógica de la página | Versión 1 (publicada antes) | Versión 2 (actual) |
|---|---|---|
| Documentos de prueba: aciertos | 85,5 % | 85,0 % |
| Documentos de prueba: AUROC | 0,934 | 0,930 |
| Humanos marcados como IA (umbral 50 %) | 17,0 % | **13,2 %** |
| Con renglones de PDF: humanos marcados como IA | 38,9 % | **5,2 %** |
| Oraciones humanas marcadas como IA en documentos mezclados (umbral 70 %) | 53,5 % | **18,1 %** |
| Artículos de 2024 (GPT-4o, Claude 3.5, o1-pro), fuera del entrenamiento | 70,0 % | **77,0 %** |
| — GPT-4o / Claude 3.5 Sonnet | 85,0 % / 73,3 % | **91,7 % / 86,7 %** |

Lo que empeora un poco: textos cortos de modelos antiguos (AuTexTification, GPT-3 y BLOOM): 82–84 % → 80–84 %, porque parte de ese acierto venía de la longitud. También se probaron la versión 1 con la nueva separación en oraciones y la media de ambos modelos; la versión 2 sola fue la mejor con texto de IA reciente y en el resaltado por oración.

Umbrales de la página, elegidos con estos datos (textos de 40 o más palabras):

| Umbral | Humanos marcados como IA (es / en) | IA detectada (es / en) |
|---|---|---|
| 70 % («Posiblemente IA», oraciones en rojo) | 5,4 % / 4,4 % | 80,4 % / 75,1 % |
| 85 % («Probablemente IA») | 2,4 % / 1,6 % | 67,8 % / 59,8 % |

Longitud: en inglés (clases equilibradas), los textos de 40–100 palabras aciertan el 83,9 % y los de más de 200, el 93,3 %. La página avisa cuando el texto tiene menos de 200 palabras.

**Límites, dichos claramente**:
- Con texto de modelos recientes que no estaban en el entrenamiento baja: 77 % frente al 92 % (AUROC 0,997) que obtiene GPTZero en esos mismos 300 artículos. Falla sobre todo con o1-pro y con texto «humanizado» (55 %).
- En textos cortos se equivoca más.
- Ningún resultado sirve como prueba para acusar a alguien.

Para acercarse a un detector comercial haría falta un modelo de lenguaje (p. ej. un transformer multilingüe afinado o la perplejidad de un modelo abierto), que no cabe en una página estática, y más texto reciente de IA en español.

### Repositorios revisados que no se incorporaron

- `ai-detected/ai-detectors`: lista de detectores de imágenes, video, audio y deepfakes. No aplica a texto.
- `ai-detected/ai-content-detectors`: lista de detectores de texto comerciales, sin código ni datos. De ahí se comprobaron dos consejos: los textos de menos de 200 palabras dan más falsos positivos (confirmado; ahora la página lo avisa) y «las palabras de duda indican IA» (no se confirma: el modelo aprendió que *may*, *likely* o *podría* apuntan a IA, pero *might*, *seems*, *parece* o *quizás* apuntan a humano, así que no se añadió esa regla).

## 6. Segunda opinión de Claude (gratis para quien lo usa)

La versión publicada en claude.ai incluye **«Revisar con Claude»**. Usa la capacidad `sample` de los artifacts de claude.ai: la página le pide a Claude que puntúe cada oración y explique el motivo, **con la cuenta de Claude de quien abre la página**. No hace falta clave de API ni servidor, y no tiene coste adicional: consume el uso normal del plan de esa persona (también el plan gratuito, con sus límites).

- La primera vez, claude.ai pide permiso para que la página use Claude.
- La puntuación final combina a partes iguales (en escala logit) el modelo entrenado y el juicio de Claude.
- Los textos largos se revisan en partes de unas 2 500 palabras, una tras otra; si se alcanza el límite de uso, se conservan las partes ya revisadas.
- Fuera de claude.ai (p. ej. GitHub Pages) el botón no aparece y el detector funciona solo con el modelo entrenado.
- La combinación con Claude no está medida en la auditoría (requiere llamadas reales a Claude).

¿Y la API de Anthropic directamente? Requiere una clave de pago y un servidor propio que la esconda; no es gratuita. Un MCP tampoco sirve aquí: los MCP conectan herramientas *a* Claude, no al revés.

## Fuentes

- https://gptzero.me/news/justdone-ai-review/
- https://cybernews.com/partner-content/justdone-all-in-one-ai-detection-and-humanizing-tool-review/
- https://aumiqx.com/ai-tools/justdone-ai-review-all-in-one-writing-tool/
- https://chatai.guide/?p=365
- https://mpgone.com/is-justdone-ai-accurate-we-tested-everything/
- https://lynote.ai/blog/just-done-ai-review
