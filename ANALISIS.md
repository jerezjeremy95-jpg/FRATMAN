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
- Explicación en lenguaje sencillo: veredicto en palabras («Probablemente escrito con IA»), una lista «¿Por qué?» con razones que citan el propio texto (las de Claude y las que detecta la página: expresiones de asistente, frases que empiezan con palabras de enlace, cierre que resume, ritmo uniforme, falta de datos concretos; o, al revés, experiencia propia, datos concretos, ritmo irregular, tono espontáneo) y, al tocar una frase, qué tiene de IA o de humano. Lo técnico queda en «Detalles técnicos».

### Versión actual: Claude como detector principal + modelo en español

**Por qué cambió.** Al pulsar la segunda opinión de Claude, el porcentaje caía mucho. La causa no era un fallo de cálculo:
1. La página promediaba 50/50 el modelo y Claude, como si ambos fueran igual de fiables.
2. La instrucción anterior para Claude decía «Sé prudente: un texto humano formal no es IA por ser formal», lo que lo empujaba hacia «humano».
3. Claude usa una escala propia: a textos de IA actuales les da 45-92 % y a textos humanos 3-10 %. Promediar ese 50 % con un 95 % del modelo bajaba la nota aunque Claude estuviera reconociendo IA.

**Cómo se midió.** Un subagente Claude Sonnet 5.5 (esfuerzo medio) aplicó la nueva instrucción (`model/claude_prompt.txt`) a 48 textos en español de etiqueta conocida que ningún modelo usó para entrenar: 24 humanos (redacciones de estudiantes, noticias, prensa, debates, tuits) y 24 de IA (Haiku con temas no vistos, el conjunto inicial y GPT-3/BLOOM). Con esas respuestas se ajustó una regresión logística (`model/fit_combo.py`, validación cruzada de 10 bloques).

| 48 textos en español | Aciertos | IA detectada | Humanos marcados como IA |
|---|---|---|---|
| Modelo local solo | 77,1 % | 62,5 % | 8,3 % |
| Claude Sonnet 5.5 solo (umbral 50 %) | 89,6 % | 79,2 % | 0,0 % |
| Promedio 50/50 (página anterior) | 83,3 % | 70,8 % | 4,2 % |
| **Combinación con pesos medidos (página actual)** | **97,9 %** | **100 %** | 4,2 % |

Claude separó perfectamente los textos humanos de los de IA actual (AUROC 1,0), pero falla con texto corto de modelos antiguos (GPT-3/BLOOM); ahí el modelo local lo complementa. En la combinación Claude pesa unas cuatro veces más que el modelo. La muestra es pequeña (48 textos): el 97,9 % tiene un margen de error amplio (aprox. 89-100 %).

**Modelo local (versión 4), entrenado solo en español** con unos 60 000 documentos: AuTexTification (tuits, manuales y textos legales; GPT-3 y BLOOM), Europarl, noticias EFE, prensa de AnCora, textos web de GSD, el Spanish Fake News Corpus (noticias escritas por personas), redacciones de estudiantes de COWS-L2H y 256 textos de IA actuales escritos por Haiku, Sonnet y Opus para este proyecto (`model/data/es_ia_generado.txt`).

| Modelo local, 6 675 documentos de prueba en español | Resultado |
|---|---|
| Aciertos | 90,6 % (AUROC 0,970) |
| Humanos marcados como IA | 7,9 % (4,3 % en textos de 40+ palabras) |
| Redacciones de estudiantes / noticias / prensa / debates marcadas como IA | 0 % / 2,2 % / 8,3 % / 0,7 % |
| IA actual detectada | 61 % |

Sin Claude (por ejemplo, en GitHub Pages) la página funciona solo con el modelo local y lo indica.

### Prueba de resistencia frente a texto «humanizado»

Los humanizadores reescriben texto de IA para engañar a los detectores. Lupa no incluye un humanizador; esta prueba interna sirve para comprobar si el detector resiste esas técnicas (`model/robustez_humanizado.py`).

Un subagente reescribió 80 textos de IA con cuatro técnicas típicas (40 de la partición de prueba para medir y 40 de entrenamiento): parafraseo genérico, voz personal con anécdotas, imperfecciones (frases desiguales, tildes y puntuación descuidadas, coloquialismos) y quitar frases típicas y estructura de plantilla. Claude Sonnet 5.5 evaluó los 40 de prueba mezclados con 14 textos humanos de control.

| 40 textos de IA de prueba, IA detectada | Original | Humanizado |
|---|---|---|
| Modelo local (umbral 50 %) | 60 % | 42 % |
| Claude solo, umbral 50 % | — | 55 % (imperfecciones 10 %, sin plantilla 20 %) |
| **Página: Claude + modelo con escala calibrada** | — | **100 % (las cuatro técnicas)** |

Claude da a los humanizados notas de 22-88 % y a los humanos de control 2-12 %: aunque con su umbral nominal de 50 % se le escapan, nunca confundió un humanizado con un humano (AUROC 1,0). Por eso la página no usa su 50 % tal cual sino una escala calibrada.

Combinación final (102 textos con nota de Claude, validación cruzada): **99,0 % de aciertos, 100 % de IA detectada (incluida la humanizada) y 2,6 % de humanos marcados como IA** (un tuit), frente a 65,7 % del modelo local solo y 77,5 % de Claude solo con su umbral nominal. Después se desplazó la constante de la combinación para que la frontera de Claude (≈17 %) quede a medio camino entre la nota humana más alta (12 %) y la IA humanizada más baja (22 %): con ese margen, ningún texto humano de la prueba pasa del 38 % de nota final.

Entrenar el modelo local con los 40 humanizados de entrenamiento no ayudó (42 % → 42,5 % de detección y algo más de falsos positivos), así que se mantiene el modelo 4.

**Límites de esta prueba**: muestras pequeñas (40 humanizados, 38 humanos); las reescrituras las hizo Claude y las juzgó Claude, lo que puede favorecerlo; no se probaron humanizadores comerciales ni otros detectores porque no son accesibles desde el entorno de trabajo.

### Repositorios revisados que no se incorporaron

- `ai-detected/ai-detectors`: lista de detectores de imágenes, video, audio y deepfakes. No aplica a texto.
- `ai-detected/ai-content-detectors`: lista de detectores de texto comerciales, sin código ni datos. De ahí se comprobaron dos consejos: los textos de menos de 200 palabras dan más falsos positivos (confirmado; ahora la página lo avisa) y «las palabras de duda indican IA» (no se confirma: el modelo aprendió que *may*, *likely* o *podría* apuntan a IA, pero *might*, *seems*, *parece* o *quizás* apuntan a humano, así que no se añadió esa regla).

## 6. Claude en la página (gratis para quien lo usa)

La versión publicada en claude.ai usa la capacidad `sample` de los artifacts: la página le pide a Claude Sonnet 5.5 (esfuerzo medio) que puntúe el texto y cada bloque de ~150 palabras, **con la cuenta de Claude de quien abre la página**. No hace falta clave de API ni servidor; consume el uso normal de su plan.

- La revisión se lanza al pulsar «Analizar texto»; los textos largos se envían en partes de ~1 800 palabras, dos a la vez.
- La página muestra qué modelo respondió realmente (si Sonnet 5.5 no está disponible, Claude usa el modelo por defecto de la cuenta).
- La nota final combina Claude y el modelo local con los pesos medidos; si Claude no está disponible, la nota es solo del modelo local.

¿Y la API de Anthropic directamente? Requiere una clave de pago y un servidor propio que la esconda; no es gratuita.

## Fuentes

- https://gptzero.me/news/justdone-ai-review/
- https://cybernews.com/partner-content/justdone-all-in-one-ai-detection-and-humanizing-tool-review/
- https://aumiqx.com/ai-tools/justdone-ai-review-all-in-one-writing-tool/
- https://chatai.guide/?p=365
- https://mpgone.com/is-justdone-ai-accurate-we-tested-everything/
- https://lynote.ai/blog/just-done-ai-review
