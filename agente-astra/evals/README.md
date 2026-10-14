# Pruebas del agente (evals)

Sirven para **medir el riesgo con datos** en vez de suponerlo: cuántos riesgos atrapa el Guardián, cuántas falsas alarmas da, si el Reciclador y el Guionista inventan claims, y qué modelo de Claude conviene para cada paso.

## Reglas de las pruebas
- **Marcas 100 % ficticias** (`marcas-ficticias/`): Vergel (jugos), Estudio Ámbar (yoga y meditación) y Cervecera Monteluz (cerveza artesanal). No se usa material de clientes.
- **Riesgos sembrados a propósito**, con verdad de referencia escrita antes de correr las pruebas (`*.evals.json`).
- **Controles limpios**: copys sin riesgos, para medir las falsas alarmas.
- **Comparación justa**: el mismo pedido y el mismo Core Brand para todas las configuraciones. Lo único que cambia es el modelo y si tiene la skill.
- **Juez a ciegas**: un modelo calificador recibe las salidas como A, B, C… sin saber qué modelo ni qué configuración produjo cada una. Lo que se puede revisar con código (el registro JSON, el veredicto, las frases riesgosas que sobreviven en la versión corregida, los tiempos del Reel) se revisa con código.

## Casos

| Skill | Casos | Qué mide |
|---|---|---|
| `guardian-marca` | 8: 6 con riesgos sembrados (37 en total, 21 de severidad alta) y 2 controles limpios | Detección, severidad, veredicto, falsas alarmas, versión corregida limpia, sin claims nuevos y registro válido |
| `reciclador-contenido` | 3 (carrusel, post de Design Board y post de cerveza) | Las 4 partes completas, cero claims nuevos, prohibiciones, leyendas y formato |
| `guionista-reels` | 3 (ola de calor, temporada de béisbol, diciembre sin personas) | Hooks, tiempos que suman, sin datos inventados, sin marcas de terceros, leyendas y restricciones del brief |

## Configuraciones
- `<modelo>_con_skill`: el modelo lee la skill y la sigue.
- `<modelo>_sin_skill`: el mismo pedido, sin skill (línea base).
- Modelos: Haiku 5.5, Sonnet 5.5 y Opus 5.5. El juez es Sonnet 5.5.

## Cómo correrlas
```bash
# 1. Preparar carpetas e instrucciones
python3 evals/herramientas/preparar.py <iteración> guardian-marca opus_con_skill sonnet_con_skill haiku_con_skill sonnet_sin_skill haiku_sin_skill
# 2. Lanzar un subagente por run (modelo = el de la config) con el texto de instruccion.txt
# 3. Armar los paquetes anónimos para el juez y lanzar un juez por caso
python3 evals/herramientas/calificar.py paquetes evals/workspace/iteration-<n>/guardian-marca
# 4. Unir el juicio con los chequeos automáticos y resumir
python3 evals/herramientas/calificar.py consolidar evals/workspace/iteration-<n>/guardian-marca
python3 evals/herramientas/calificar.py resumen evals/workspace/iteration-<n>/guardian-marca
```

## Resultados
- `resultados/`: resúmenes por iteración y visor HTML con todas las salidas.
- La interpretación y su efecto en la matriz de riesgos están en [`../RIESGOS.md`](../RIESGOS.md).

## Límites (para no sobreinterpretar)
- Son pocos casos: sirven para comparar configuraciones y detectar fallas, no como garantía estadística.
- Un run por configuración en la primera iteración: puede haber variación entre corridas.
- Las marcas ficticias son más "obvias" que la vida real. En producción aparecerán riesgos más sutiles; por eso el Guardián no reemplaza la aprobación humana.
- **Contaminación controlada:** los ejemplos de las skills y del catálogo usan otras marcas y otras frases que los casos de prueba (se revisó con búsqueda literal). Sí comparten vocabulario estándar de alerta ("quema grasa", "sin efectos secundarios"), porque cualquier catálogo serio de claims lo incluye.
