# Modelo de Lupa

Regresión logística sobre rasgos hasheados y estilométricos. El mismo cálculo existe en Python (`features.py`) y en JavaScript (`src/index.src.html`); la prueba de paridad da una diferencia máxima de 0,000005 en la probabilidad.

## Archivos

- `features.py`: tokenización, hash FNV-1a de 32 bits (palabras, pares de palabras, fragmentos de 3 a 5 letras) en 2^18 posiciones, y 16 medidas de estilo.
- `train.py`: carga los corpus, separa el 15 % de los documentos para prueba, elige `C` con validación, entrena, cuantiza los pesos a int8 y evalúa.
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
python3 model/build.py
```

Tarda unos 25 minutos con 4 núcleos y necesita unos 8 GB de RAM.
