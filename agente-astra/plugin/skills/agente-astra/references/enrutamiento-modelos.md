# Enrutamiento de modelos de Claude

Usar siempre el modelo más grande no es lo más inteligente. Gasta el límite de uso del plan más rápido, tarda más y no mejora las tareas mecánicas. Usar siempre el más pequeño ahorra, pero en una revisión de claims de salud un error sale publicado. La regla:

> **Si el error saldría publicado o toca salud, alcohol o datos personales, usa un modelo fuerte. Si el error se nota y se corrige en un minuto, usa uno ligero.**

## Tabla de enrutamiento

| Paso | Ejemplos | Modelo | Esfuerzo |
|---|---|---|---|
| Mecánico | Transcribir un DB o un carrusel, contar caracteres y hashtags, sumar tiempos, ordenar, resumir | **Haiku** | bajo |
| Redacción | Guiones, Stories, LinkedIn, captions, variantes, hooks | **Sonnet** | medio |
| Juicio | Veredicto del Guardián en salud, bienestar, alimentos o alcohol; mecánicas con datos o sorteos; casos ambiguos; estrategia | **Opus** | alto |
| Crítico | Auditoría completa antes de una campaña grande o sensible; revisión adversarial ("intenta colar un claim") | **Fable** | alto |

## Cómo se aplica en cada lugar

- **Claude.ai (chat):** la persona elige el modelo en el selector **antes** de escribir. El agente recomienda el modelo en una línea cuando la tarea lo amerita. Una práctica que funciona: redactar con Sonnet y, antes de enviar al cliente, abrir el Guardián en Opus.
- **Cowork o Claude Code con el plugin:** el enrutamiento es automático.
  - Subagentes: `extractor-piezas` y `verificador-formato` (Haiku, esfuerzo bajo), `redactor-multicanal` (Sonnet, esfuerzo medio) y `auditor-claims` (Opus, esfuerzo alto).
  - Comandos: `/agente-astra:extraer` (Haiku), `/agente-astra:reciclar` y `/agente-astra:guion` (Sonnet), y `/agente-astra:guardian` (Opus, esfuerzo alto).
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
(Se completa con los resultados de `evals/`: detección de riesgos por modelo, falsos positivos y tiempo.)
