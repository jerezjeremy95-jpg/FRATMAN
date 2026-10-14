# Integraciones a costo cero

**Claude trabaja en el chat y Make solo mueve datos.** No se usa la API de Claude ni servicios de pago adicionales. Todo corre con lo que el equipo ya tiene: Drive, Google Sheets, Looker Studio, Make y Trello.

```
Claude (chat o Cowork)                 Make (solo mueve datos)                    Tablero
──────────────────────                 ───────────────────────                    ───────
Guardián → reporte en Doc  ──Drive──▶  Lee el Doc → extrae REGISTRO → fila  ──▶  Google Sheets ──▶ Looker Studio
                                         (y si está aprobado → tarjeta)    ──▶  Trello
```

## 1. Registro de riesgos: Guardián → Sheets → Looker Studio

**Para qué sirve:** contar cuántas piezas se revisan, cuántos riesgos altos se atajan antes de llegar al cliente y de qué tipo son. Con eso, el riesgo se mide con datos y se ve si baja mes a mes.

**Paso del equipo (en Claude):**
1. Correr el Guardián. Todo reporte termina con una línea `REGISTRO-GUARDIAN {…}` en JSON de una sola línea.
2. Guardar el reporte como Google Doc en la carpeta **`/Astra/Guardian/`**, con el nombre `AAAA-MM-DD_Marca_pieza`. Si el conector de Drive permite crear archivos, Claude lo guarda; si no, se copia y pega en un Doc nuevo dentro de esa carpeta.

**Escenario de Make** (módulos estándar):
1. **Google Drive · Watch Files in a Folder**: carpeta `/Astra/Guardian/`.
2. **Google Docs · Get Content of a Document**: el Doc nuevo.
3. **Text parser · Match pattern**: patrón `REGISTRO-GUARDIAN\s*(\{.*\})`; se toma el grupo 1.
   - Si alguien pegó el texto a mano, Google Docs puede cambiar las comillas rectas por comillas tipográficas (“ ”). Antes de leer el JSON, reemplázalas por comillas rectas con la función `replace` de Make.
4. **JSON · Parse JSON**: estructura con los campos del registro.
5. **Google Sheets · Add a Row**: hoja `registro`, con las columnas `fecha · marca · pieza · canal · veredicto · n_alta · n_media · n_baja · tipos · core_brand · link_doc`.
6. (Opcional) **Iterator** sobre `hallazgos` → **Google Sheets · Add a Row** en una hoja `hallazgos` (`fecha · marca · tipo · severidad · texto`).

Cada documento usa unas 5 o 6 operaciones de Make, más una por hallazgo si se usa el paso 6. Revisen que el volumen mensual quepa en el plan actual de Make.

**Tablero en Looker Studio** (fuente: la hoja de Google Sheets, con el conector nativo gratuito):
- Piezas revisadas por semana y por marca.
- Veredictos: % rojo, amarillo y verde (la meta es que el rojo baje con el tiempo).
- **Riesgos altos atajados** antes de llegar al cliente, por mes. Es el indicador principal del valor del Guardián.
- Tipos de riesgo más frecuentes (salud, cifras, promociones…), para saber qué reforzar con el equipo o con cada cliente.

> ¿Por qué Sheets y no Airtable para esto? Looker Studio lee Google Sheets gratis con su conector nativo. Para Airtable normalmente hace falta un conector de terceros, y muchos son de pago. Airtable puede seguir usándose para lo que ya lo usen.

## 2. Aprobado → tarjeta en Trello

1. Cuando una persona aprueba un borrador, lo mueve a **`/Astra/Aprobados/`** (o le agrega `APROBADO` al nombre).
2. **Make:** Google Drive · Watch Files in a Folder → **Trello · Create a Card** en el tablero de la marca, con el título del archivo y el link en la descripción.

Es el mismo patrón que ya usa el Radar Cibao para las ideas aprobadas.

## 3. Lo que NO se automatiza (a propósito)
- **Publicar o programar posts:** siempre lo hace una persona.
- **Enviar al cliente:** siempre lo hace una persona.
- **Llamar a Claude desde Make:** requeriría la API de Claude (costo extra) y quitaría la revisión humana del medio.

## 4. Privacidad
- Los registros guardan el texto de los hallazgos (frases del copy), no datos personales. No pongas datos de personas en los copys de prueba.
- La hoja de registro y el tablero son internos de Astra: compártelos solo con el equipo.
