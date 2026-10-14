# Medición del riesgo del Agente Astra

Este documento mide el riesgo de usar el agente en el trabajo de Astra: qué puede salir mal, cuánto pesa, qué lo mitiga y cuánto riesgo queda. Las cifras de detección salen de pruebas reales (`evals/`), no de suposiciones.

**Fecha:** 2026-10-14 · **Versión del agente:** 0.1.0 · **Estado:** propuesta para piloto, pendiente de aprobación de Astra.

## 1. Resumen
<!-- RESUMEN -->
(Se completa con los resultados de las pruebas.)

## 2. Cómo se mide
- **Probabilidad (P):** 1 muy baja · 2 baja · 3 media · 4 alta · 5 muy alta.
- **Impacto (I):** 1 mínimo · 2 menor (se corrige internamente) · 3 moderado (lo nota el cliente) · 4 grave (reclamo, retiro de la pieza, daño de reputación) · 5 crítico (sanción, pérdida del cliente o problema legal).
- **Nivel = P × I:** 1–4 🟢 bajo · 5–9 🟡 medio · 10–16 🟠 alto · 20–25 🔴 crítico.
- **Inherente** = el trabajo de hoy, sin agente. **Residual** = con el agente, sus controles y la aprobación humana.
- Donde hay datos de las pruebas, la probabilidad residual se apoya en ellos (sección 4).

## 3. Matriz de riesgos
<!-- MATRIZ -->
(Se completa con los resultados de las pruebas.)

## 4. Lo que midieron las pruebas
<!-- PRUEBAS -->
(Se completa con los resultados de las pruebas.)

## 5. Recomendación
<!-- RECOMENDACION -->
(Se completa con los resultados de las pruebas.)

## 6. Bitácora de esta sesión
<!-- BITACORA -->
(Se completa al final.)
