# Enrutamiento de modelos de Claude

Usar siempre el modelo más grande no es lo más inteligente. Gasta el límite de uso del plan más rápido, tarda más y no mejora las tareas mecánicas. Usar siempre el más pequeño ahorra, pero en una revisión de claims de salud un error sale publicado. La regla:

> **Si el error saldría publicado o toca salud, alcohol o datos personales, usa un modelo fuerte. Si el error se nota y se corrige en un minuto, usa uno ligero.**

## Tabla de enrutamiento

| Paso | Ejemplos | Modelo | Esfuerzo |
|---|---|---|---|
| Mecánico | Transcribir un DB o un carrusel, contar caracteres y hashtags, sumar tiempos, ordenar, resumir | **Haiku** | bajo |
| Redacción | Guiones, Stories, LinkedIn, captions, variantes, hooks | **Sonnet** | medio |
| Revisión | Guardián del día a día: tono, prohibiciones, cifras, promociones, en copys sin temas sensibles | **Sonnet** | medio |
| Juicio | Guardián cuando la pieza toca salud (promete algo al cuerpo o a la mente), alcohol, datos personales, sorteos o menores, o va a pauta pagada; casos ambiguos; estrategia | **Opus** | alto |
| Crítico | Auditoría completa antes de una campaña grande o sensible; revisión adversarial ("intenta colar un claim") | **Fable** | alto |

## Cómo se aplica en cada lugar

- **Claude.ai (chat):** la persona elige el modelo en el selector **antes** de escribir. El agente recomienda el modelo en una línea cuando la tarea lo amerita. Una práctica que funciona: redactar con Sonnet y, antes de enviar al cliente, abrir el Guardián en Opus.
- **Cowork o Claude Code con el plugin:** el enrutamiento es automático.
  - Subagentes: `extractor-piezas` y `verificador-formato` (Haiku, esfuerzo bajo), `redactor-multicanal` (Sonnet, esfuerzo medio) y `auditor-claims` (Opus, esfuerzo alto).
  - Comandos: `/agente-astra:extraer` (Haiku), `/agente-astra:reciclar` y `/agente-astra:guion` (Sonnet), y `/agente-astra:guardian` (Sonnet, que delega en `auditor-claims`, en Opus, las piezas sensibles).
- **Make:** no usa Claude. Solo mueve datos, así que no gasta modelo.

## Peso relativo de cada modelo

Como referencia de cuánto "pesa" cada modelo, estos son los precios públicos de la API por millón de tokens (entrada / salida). Astra no usa la API: en el plan del chat, el peso se nota en lo rápido que se gasta el límite de uso.

| Modelo | Entrada | Salida | Frente a Haiku |
|---|---|---|---|
| Haiku 5.5 | US$0.10 | US$0.50 | 1× |
| Sonnet 5.5 | US$2 | US$10 | 20× |
| Opus 5.5 | US$4 | US$20 | 40× |
| Fable 5.1 | US$10 | US$50 | 100× |

Precios de la documentación oficial de Anthropic, consultada el 2026-10-14. Pueden cambiar.

## Cuándo subir de modelo
- El modelo ligero duda o deja preguntas abiertas sobre un claim de salud, alcohol o datos personales: repite el Guardián en Opus.
- Una pieza va a pauta pagada, a un medio o a un evento masivo: auditoría con Fable antes de enviarla al cliente.
- El cliente ya reclamó por un tema: ese tema se revisa siempre con Opus.

## Lo que midieron las pruebas
Pruebas del 14 y 15 de octubre de 2026, con marcas ficticias (detalle en `RIESGOS.md` y `evals/`). Una corrida por caso y modelo, calificada a ciegas.

**Guardián** (8 casos, 37 riesgos sembrados, 2 copys limpios de control):

| Modelo | Riesgos detectados | Altos como altos | Falsas alarmas | Corrección con claim nuevo | Tiempo promedio |
|---|---|---|---|---|---|
| Haiku con skill | 37/37 | 21/21 | 0 | 1 de 8 | 98 s |
| Sonnet con skill | 37/37 | 21/21 | 0 | 0 de 8 | 85 s |
| Opus con skill | 37/37 | 21/21 | 0 | 1 de 8 | 143 s |
| Sonnet sin skill | 37/37 | 20/21 | 2 | 1 de 8 | 35 s, sin registro ni formato |

**Reciclador y Guionista** (6 casos): con skill, Haiku y Sonnet cumplieron casi todo (Haiku inventó una hora en un gancho; se corrigió la regla y en la segunda ronda ya no pasó). Sin skill, Sonnet inventó datos en 3 de 6 piezas y no hizo el pase del Guardián.

Qué se concluye:
- **Con la skill, el modelo pesa menos que la skill.** Haiku detectó lo mismo que Opus. Lo que cambia es el costo y el tiempo.
- **Sonnet es el mejor punto medio** para el Guardián del día a día: el mejor resultado, ningún claim nuevo en las correcciones y más rápido que Opus.
- **Opus no detectó más en estos casos**, que son claros. Se mantiene para lo sensible (salud, alcohol, datos, sorteos, menores, pauta) hasta probarlo con los casos difíciles de la auditoría (`evals/guardian-marca-dificiles.evals.json`), donde el criterio fino sí puede pesar.
- **Haiku sirve para borradores con skill y para lo mecánico**, pero su corrección necesita la regla de no reformular claims (ya agregada) y una revisión humana como cualquier otra.
