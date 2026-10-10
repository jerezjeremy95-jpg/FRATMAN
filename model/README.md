# Modelo de Lupa

Regresión logística sobre rasgos hasheados y estilométricos (versión 2). El mismo cálculo existe en Python (`features.py`) y en JavaScript (`src/index.src.html`); la prueba de paridad da una diferencia máxima de 0,000005 en la probabilidad.

## Archivos

- `features.py`: tokenización, hash FNV-1a de 32 bits (palabras, pares de palabras, fragmentos de 3 a 5 letras) en 2^18 posiciones, y 15 medidas de estilo (sin la longitud del texto, que en los corpus era un atajo).
- `train.py`: carga los corpus, toma fragmentos de cualquier parte de cada documento, deja fuera los documentos de prueba (`test_groups.json`), elige `C` con validación, entrena y cuantiza los pesos a int8.
- `evaluate.py`: auditoría con la lógica exacta de la página (oraciones, ventanas, bloques); escribe en el modelo las métricas que muestra la página.
- `test_groups.json`: identificadores de los 11 872 documentos de prueba congelados (sin texto).
- `build.py`: inserta `lupa-model.json` en `src/index.src.html` y genera `index.html`.
- `data/es_ia_moderno.txt`: 86 textos en español escritos con un asistente de IA para este proyecto (estilo de IA actual).
- `lupa-model.json`: pesos entrenados y métricas.

## Datos de entrenamiento

Los textos de los corpus no se incluyen en el repositorio; solo los pesos aprendidos. Revisa la licencia de cada corpus antes de reutilizarlos.

| Corpus | Idioma | Contenido |
|---|---|---|
| AuTexTification (IberLEF 2023), subtarea 1 | es, en | Tuits, manuales y textos legales humanos frente a GPT-3 y BLOOM |
| Ghostbuster (Verma et al., 2023), CC BY 3.0 | en | Ensayos, noticias de Reuters y relatos humanos frente a ChatGPT y Claude |
| Europarl (NLTK) | es | Debates parlamentarios (humano formal) |
| CoNLL-2002 (NLTK) | es | Noticias de la agencia EFE (humano) |
| `data/es_ia_moderno.txt` | es | Texto de IA actual |
| human_detectors (Russell et al., 2025), MIT | en | Solo prueba: 300 artículos de 2024, humanos frente a GPT-4o, Claude 3.5 Sonnet y o1-pro |

## Reentrenar

```bash
pip install scikit-learn regex scipy pandas
python3 model/train.py --data <carpeta con AUTEXTIFICATION/, europarl_raw/, conll2002/> \
  --ghost <clon de vivek3141/ghostbuster-data> --hd <human_detectors.json>
python3 model/evaluate.py --bench <bench.json> --write-metrics
python3 model/build.py
```

`bench.json` es la lista de documentos de prueba (`{text, y, lang, source, group}`) cuyos grupos están en `test_groups.json`; se genera con los mismos corpus y no se incluye en el repositorio.

Tarda unos 25 minutos con 4 núcleos y necesita unos 8 GB de RAM.
