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

### Modelo entrenado

Lupa usa una regresión logística entrenada (detalles y cómo reentrenarla en `model/README.md`):

- **Rasgos**: palabras, pares de palabras y fragmentos de 3 a 5 letras (hasheados en 262 144 posiciones) + 16 medidas de estilo.
- **Datos**: unos 125 000 ejemplos de AuTexTification (español e inglés, GPT-3 y BLOOM), Ghostbuster (ensayos, noticias y relatos en inglés, ChatGPT y Claude), Europarl y noticias EFE (español humano formal) y 86 textos en español escritos con un asistente de IA actual.
- **Pesos**: cuantizados a 8 bits e incrustados en la página (unos 340 KB).

Precisión con documentos que el modelo nunca vio (umbral 50 %):

| Conjunto de prueba | Aciertos | AUROC | Humanos marcados como IA |
|---|---|---|---|
| Español (todos) | 86,1 % | 0,938 | 13,6 % |
| Inglés (todos) | 87,1 % | 0,946 | 12,9 % |
| Inglés, artículos de 2024 (GPT-4o, Claude 3.5, o1), fuera del entrenamiento | 67,3 % | 0,710 | 15,3 % |

Comparación sobre una muestra equilibrada de 3 336 textos de prueba (textos de 40 palabras o más):

| | Detector por reglas anterior | Modelo entrenado |
|---|---|---|
| Español | 75,2 % (AUROC 0,67) | 91,0 % (AUROC 0,97) |
| Inglés | 51,6 % (AUROC 0,53) | 89,0 % (AUROC 0,96) |
| Artículos de 2024 | 52,7 % (AUROC 0,64) | 70,0 % (AUROC 0,74) |

**Límites, dichos claramente**:
- Con texto de modelos recientes que no estaban en el entrenamiento baja mucho: 70 % frente al 92 % (AUROC 0,997) que obtiene GPTZero en esos mismos 300 artículos. Falla sobre todo con o1-pro y con texto «humanizado».
- En textos cortos (tuits, párrafos sueltos) se equivoca más.
- Entre un 7 % y un 17 % de los textos humanos de prueba salen como IA según el tipo de texto. Por eso la página solo marca «Probable IA» a partir del 70 %.
- Ningún resultado sirve como prueba para acusar a alguien.

Para acercarse a un detector comercial haría falta un modelo de lenguaje (p. ej. un transformer multilingüe afinado o la perplejidad de un modelo abierto), que no cabe en una página estática, y más texto reciente de IA en español.

## Fuentes

- https://gptzero.me/news/justdone-ai-review/
- https://cybernews.com/partner-content/justdone-all-in-one-ai-detection-and-humanizing-tool-review/
- https://aumiqx.com/ai-tools/justdone-ai-review-all-in-one-writing-tool/
- https://chatai.guide/?p=365
- https://mpgone.com/is-justdone-ai-accurate-we-tested-everything/
- https://lynote.ai/blog/just-done-ai-review
