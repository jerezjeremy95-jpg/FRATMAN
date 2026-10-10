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

`index.html` es una herramienta propia (marca, textos y diseño originales) que reproduce el flujo funcional:

- Entrada por texto pegado, arrastrar archivo o subir `.txt`, `.docx` (mammoth) y `.pdf` (pdf.js).
- Límite de 15 000 palabras y mínimo de 40.
- Probabilidad global en un indicador semicircular, reparto IA / revisar / humano por palabras.
- Resaltado por oración; al tocar una oración se ven las razones de su puntuación.
- Cinco señales del documento explicadas: variación entre oraciones, densidad de expresiones típicas de IA, conectores al inicio, marcas de voz humana y diversidad léxica (MATTR).
- Español e inglés, con detección automática del idioma.

**Diferencias deliberadas**: todo se calcula en el navegador (privacidad, sin servidor, sin coste), no hay muro de pago ni humanizador, y el aviso de límites es visible.

**Limitación honesta**: usa heurísticas, no un modelo entrenado ni perplejidad real. Para acercarse a la precisión de un servicio comercial, el siguiente paso sería un backend que:
- calcule la perplejidad por token con un modelo abierto (p. ej. GPT-2 o Llama pequeño), o
- use un clasificador entrenado (p. ej. un RoBERTa afinado en textos humanos/IA en español), o
- pida a un LLM vía API que evalúe el texto, combinando su juicio con las señales actuales.

## Fuentes

- https://gptzero.me/news/justdone-ai-review/
- https://cybernews.com/partner-content/justdone-all-in-one-ai-detection-and-humanizing-tool-review/
- https://aumiqx.com/ai-tools/justdone-ai-review-all-in-one-writing-tool/
- https://chatai.guide/?p=365
- https://mpgone.com/is-justdone-ai-accurate-we-tested-everything/
- https://lynote.ai/blog/just-done-ai-review
