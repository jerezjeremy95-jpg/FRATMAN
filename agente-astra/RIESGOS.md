# Medición del riesgo del Agente Astra

Este documento mide el riesgo de usar el agente en el trabajo de Astra: qué puede salir mal, cuánto pesa, qué lo mitiga y cuánto riesgo queda. Las cifras de detección salen de pruebas reales con marcas ficticias (`evals/`), no de suposiciones.

**Fecha:** 2026-10-15 · **Versión del agente:** 0.2.0 · **Estado:** propuesta para un piloto, pendiente de aprobación de Astra.

## 1. Resumen
<!-- RESUMEN -->

## 2. Cómo se mide
- **Probabilidad (P):** 1 muy baja · 2 baja · 3 media · 4 alta · 5 muy alta.
- **Impacto (I):** 1 mínimo · 2 menor (se corrige dentro del equipo) · 3 moderado (lo nota el cliente) · 4 grave (reclamo, retiro de la pieza, daño de reputación) · 5 crítico (sanción, pérdida del cliente o problema legal).
- **Nivel = P × I:** 1–4 🟢 bajo · 5–9 🟡 medio · 10–16 🟠 alto · 20–25 🔴 crítico.
- **Inherente:** usar Claude en el chat sin el agente, o no usar IA, y sin controles adicionales. En las pruebas es la configuración "Sonnet sin skill".
- **Residual:** con el agente, sus controles y la aprobación humana obligatoria.
- Cuando hay datos de las pruebas, la probabilidad residual se apoya en ellos (sección 4). Las pruebas son pocas (11 casos), así que una probabilidad baja no se lee como "cero".

## 3. Matriz de riesgos

| # | Riesgo | Inherente | Controles del agente | Residual | Evidencia |
|---|---|---|---|---|---|
| R1 | Se publica una **promesa de salud** (cura, elimina, quema grasa, "detox") | 3×5 = 15 🟠 | Guardián con catálogo de claims de salud y marco legal RD; Opus para salud; aprobación humana | 1×5 = 5 🟡 | Casos 1, 2 y 5: los tres modelos con skill detectaron todas las promesas de salud |
| R2 | La IA **inventa una cifra, precio, fecha u hora** al redactar | 4×4 = 16 🟠 | Regla de no inventar datos (`[confirmar]`); `verificar_copy.py` lista cada cifra para cotejarla; pase del Guardián | 2×4 = 8 🟡 | Sin skill, inventó datos en 3 de 6 piezas; con skill, en 1 de 12 (corregido en la iteración 2, sección 4) |
| R3 | **Falso negativo:** el Guardián no marca un riesgo real | 3×4 = 12 🟠 | Catálogo con 16 tipos y patrones; la duda sube la severidad; "Para decidir por un humano"; Opus o Fable en piezas sensibles | 2×4 = 8 🟡 | 0 riesgos sembrados sin detectar con skill (sección 4); la muestra es chica y los riesgos nuevos pueden no estar en el catálogo |
| R4 | **Fatiga por falsas alarmas:** el equipo deja de leer al Guardián | 3×2 = 6 🟡 | Sección "Lo que NO es problema"; severidad baja para estilo; controles limpios en las pruebas | 1×2 = 2 🟢 | 0 falsos positivos medios o altos en los controles limpios con skill; sin skill hubo 1 |
| R5 | **Sobreconfianza:** se envía sin leer porque "el Guardián dijo verde" | — (lo crea el agente) | 🟢 dice "listo para aprobación humana", no "aprobado"; aprobación humana obligatoria; revisión de una muestra semanal en el tablero | 2×4 = 8 🟡 | Riesgo de proceso: las pruebas no lo miden. Se vigila en el piloto |
| R6 | Se sube **material confidencial** del cliente a la IA sin autorización | 3×4 = 12 🟠 | Principio 2: solo el Core Brand y las piezas de Astra; el agente pregunta antes de usar briefs, métricas o contratos | 2×4 = 8 🟡 | Depende de las personas; el agente solo lo recuerda |
| R7 | **Datos personales** de asistentes sin consentimiento (Ley 172-13) | 3×4 = 12 🟠 | Guardián marca los pedidos de datos por comentarios o DM y las mecánicas sin aviso; principio 5 | 1×4 = 4 🟢 | Caso 2: los cuatro configs marcaron el pedido de cédula por comentarios como alto |
| R8 | **Marcas de terceros** (LIDOM, equipos, logos, música) sin licencia (Ley 20-00) | 3×4 = 12 🟠 | Regla de béisbol del Guionista; Guardián marca logos, camisetas y hashtags oficiales; audio de biblioteca comercial | 1×4 = 4 🟢 | Caso 3 y guion de temporada (202) |
| R9 | **Alcohol** sin la leyenda legal, con consumo excesivo o cerca de menores (Ley 42-01, Ley 136-03) | 3×5 = 15 🟠 | Leyenda de la Ley 42-01, art. 123, en el catálogo y en el Core Brand de prueba; Guardián marca "de un solo trago" y "el que más se tome" | 1×5 = 5 🟡 | Caso 3 (sección 4) y control limpio de Monteluz (caso 6) |
| R10 | **Sorteo o promoción sin registro** ni bases (Res. 009-2011, Res. 016-2014) | 3×4 = 12 🟠 | Guardián marca sorteos sin bases y ofertas sin fechas ni condiciones; pide registro con 21 días de antelación | 1×4 = 4 🟢 | Casos 2, 3 y 8 |
| R11 | **El marco legal se interpreta mal** (el agente no es abogado) | 2×5 = 10 🟠 | `marco-rd.md` con fuentes y nivel de confianza; las dudas legales van a "Para decidir por un humano" o al abogado del cliente | 1×5 = 5 🟡 | Revisión independiente con Fable (sección 4) |
| R12 | **El repositorio es público** y en él termina material de Astra | 3×4 = 12 🟠 | Solo marcas ficticias en el repo; `validar.py` busca datos sensibles antes de empaquetar | 1×4 = 4 🟢 (al pasarlo a privado) | Hoy el repo `FRATMAN` es público: ver la recomendación |
| R13 | **Se mezclan agencias** (Coa Digital Lab y Astra) | 2×4 = 8 🟡 | Principio 7; el plugin solo trae material de Astra; cuentas y carpetas separadas | 1×4 = 4 🟢 | Revisado: no hay referencias a otra agencia en el plugin |
| R14 | **Continuidad:** el agente depende de quien lo armó (la pasantía termina el 18 de diciembre) | 4×3 = 12 🟠 | README, guía de integraciones, pruebas reproducibles, una sola fuente de referencias (`compartido/`) | 2×3 = 6 🟡 (al pasarlo a una cuenta de Astra) | Ver la recomendación |
| R15 | **Referencias desactualizadas** (límites de las plataformas, leyes, fechas de temporada) | 3×3 = 9 🟡 | Tablas con fecha y fuente; "si la plataforma cambió, gana la plataforma"; revisión trimestral | 2×3 = 6 🟡 | `formatos-canal.md` y `marco-rd.md` fechados el 2026-10-14 |
| R16 | **Cambios en los modelos o en los límites de uso** del plan | 3×2 = 6 🟡 | Enrutamiento por modelo; las skills funcionan en cualquier modelo; el Guardián en Haiku también detectó los riesgos de las pruebas | 2×2 = 4 🟢 | En esta construcción se alcanzaron los límites de uso dos veces (sección 6) |
| R17 | **Make falla** y el registro no llega a Sheets | 3×2 = 6 🟡 | El reporte completo queda en Drive; la línea de registro se valida con código; Make solo mueve datos | 2×2 = 4 🟢 | Solo afecta la medición, no las piezas |

## 4. Lo que midieron las pruebas
<!-- PRUEBAS -->
Las pruebas usan tres marcas ficticias: Vergel (jugos), Estudio Ámbar (meditación) y Monteluz (cerveza). Cada caso corrió una vez por configuración. Un juez (Sonnet) calificó a ciegas, sin saber qué modelo escribió cada salida. Los chequeos de formato (registro, frases que sobreviven en la corrección) los hace código. Detalle y método en `evals/README.md`; resultados en `evals/resultados/`.

### 4.1 Guardián: 8 casos, 37 riesgos sembrados (21 altos) y 2 copys limpios de control

| Configuración | Riesgos detectados | Altos marcados como altos | Falsas alarmas (media o alta) | Veredicto correcto | Registro válido | Corrección que mete un claim nuevo | Tiempo promedio |
|---|---|---|---|---|---|---|---|
| Haiku con skill | 37/37 | 21/21 | 0 | 8/8 | 8/8 | 1 de 8 | 98 s |
| Sonnet con skill | 37/37 | 21/21 | 0 | 8/8 | 8/8 | 0 de 8 | 85 s |
| Opus con skill | 37/37 | 21/21 | 0 | 8/8 | 8/8 | 1 de 8 | 143 s |
| Sonnet sin skill | 37/37 | 20/21 | 2 | 8/8* | 0/8 | 1 de 8 | 35 s |

\* Sin skill, el veredicto lo dedujo el juez del texto libre. En un caso era ambiguo: decía "no se puede publicar" y luego "se puede publicar tal cual".

Cómo leerlo:
- **La detección salió perfecta en todas las configuraciones, incluso sin skill.** Eso no prueba que el falso negativo sea cero: indica que los riesgos sembrados eran claros. Por eso la probabilidad residual de R3 queda en 2 y no en 1, y por eso la auditoría propone seis casos difíciles (4.4).
- **Lo que aporta la skill en el Guardián** es que el resultado sea confiable y medible: 0 falsas alarmas (sin skill, 2), severidades consistentes, veredicto claro, registro para el tablero (8/8 frente a 0/8) y versión corregida limpia. Además permite que Haiku rinda como los modelos grandes.
- **El error que sí apareció está en la corrección.** Al quitar una cifra sin fuente, Opus escribió "Si lo pruebas, repites" y Haiku escribió "Cada vez más empresas de Santiago confían en nosotros". Son el mismo claim, más vago. Se agregó la regla "un claim que quitas no vuelve con otras palabras" (4.3).

### 4.2 Reciclador y Guionista: 6 casos

| Skill | Haiku con skill | Sonnet con skill | Sonnet sin skill |
|---|---|---|---|
| Reciclador (3 casos): expectativas cumplidas | 100 % | 100 % | 79 % |
| Guionista (3 casos): expectativas cumplidas | 97 % → 100 % en la iteración 2 | 100 % | 63 % |
| Piezas con datos inventados (cifras, horas, escasez) | 1 de 6 → 0 en la iteración 2 | 0 de 6 | 3 de 6 |

Sin skill, Sonnet no hizo el pase del Guardián en ninguna pieza, entregó un solo gancho en vez de tres y agregó frases que no estaban aprobadas, como "Misión del día: que llegue bien frío" o una variedad de cerveza tomada del Core Brand como si fuera un claim. Ese es el riesgo R2 medido.

### 4.3 Iteración 2: se repitió solo lo que falló

| Caso | Antes | Cambio en la skill | Después |
|---|---|---|---|
| Guionista 201, Haiku | Inventó "2 p. m." en el gancho | Regla: sin horas, temperaturas ni escasez inventadas | 10/10, sin datos inventados |
| Guionista 203, Haiku | 12/12 | (control de que la regla no rompe nada) | 12/12 |
| Guardián 1, Opus | "Si lo pruebas, repites" | Regla: un claim quitado no vuelve con otras palabras (con ejemplos distintos a los de la prueba) | 13/13, corrección sin claims nuevos |
| Guardián 5, Haiku | "Cada vez más empresas confían" | La misma regla | 9/9, corrección sin claims nuevos |

### 4.4 Auditoría independiente
<!-- AUDITORIA -->

### 4.5 Límites de estas pruebas
- Son pocas: 11 casos, una corrida por configuración, así que no hay medición de variación. Una diferencia de un caso no es una tendencia.
- Las marcas y los copys son ficticios. Faltan piezas reales del equipo, con sus imágenes y su contexto.
- El juez también es un modelo. Califica a ciegas y con una verdad de referencia escrita, pero no reemplaza a una persona.
- A mitad de las pruebas se corrigió la leyenda de alcohol de Monteluz, tras la investigación legal. Los casos afectados quedaron documentados en `evals/README.md`.
- Se midió la calidad de cada skill, no si el agente las activa solo cuando debe. Para eso hay una suite en `plugin/evals/` que todavía no se corrió.

## 5. Recomendación
<!-- RECOMENDACION -->
**Sí a un piloto de 4 semanas**, con estas condiciones:

1. **Antes de usarlo con material real**, pasar el repositorio a privado o moverlo a una cuenta de Astra. Hoy `FRATMAN` es público (R12).
2. **El Guardián es obligatorio** antes de enviar cualquier copy al cliente, y una persona firma la aprobación. 🟢 significa "listo para aprobación humana", no "aprobado" (R5).
3. **Modelos:** Sonnet para redactar y para el Guardián del día a día. Opus cuando la pieza toca salud, alcohol, datos personales, sorteos o menores, o va a pauta pagada. Haiku para extraer, contar y verificar. Si el plan lo permite, Fable para auditar una campaña grande antes de enviarla. En esta construcción, Fable no estuvo disponible por el límite de gasto de la cuenta.
4. **Empezar con 2 marcas** y medir en Sheets y Looker: piezas revisadas, veredictos, tipos de hallazgo y cuántas correcciones del Guardián se aceptan tal cual.
5. **Revisar una muestra cada semana:** 5 piezas en 🟢 elegidas al azar, que relee otra persona. Si aparece un riesgo que el Guardián no marcó, se agrega como caso de prueba y se ajusta la skill.
6. **Correr los casos difíciles de la auditoría** (`evals/guardian-marca-dificiles.evals.json`) antes de ampliar el piloto a marcas de salud o alcohol.
7. **Criterios para pasar de piloto a uso normal:** cero incidentes publicados, menos de 1 falsa alarma por cada 10 piezas según el equipo y menos tiempo de revisión que hoy.
8. **Antes del 18 de diciembre**, transferir el plugin, el repositorio y el tablero a cuentas de Astra y nombrar a una persona responsable de mantener las referencias (R14).

## 6. Bitácora de esta construcción
<!-- BITACORA -->
- **14 de octubre, noche:** se construyeron las tres skills, la skill orquestadora, 4 subagentes con su modelo fijo, 4 comandos, las referencias compartidas (principios, catálogo de claims, marco legal dominicano, formatos por canal, temporadas, modelos) y las pruebas con tres marcas ficticias.
- **Investigación:** marco legal dominicano (Ley 358-05, Res. 016-2014, Ley 42-01, Ley 172-13, sorteos, Ley 136-03, Ley 20-00) y límites vigentes de Instagram y LinkedIn. Cambios que trajo: la leyenda legal de alcohol ("El consumo de alcohol perjudica la salud"), el máximo de 5 hashtags en Instagram y la responsabilidad solidaria de la agencia en la publicidad.
- **Pruebas:** 50 corridas en la iteración 1 y 6 en la iteración 2, más 18 calificaciones a ciegas. Solo las corridas usaron unos 4.9 millones de tokens (unidades de texto).
- **Límites de uso:** se alcanzó el límite semanal y luego el de sesión del plan, lo que cortó corridas que hubo que repetir. Al final, Fable se rechazó por el límite de gasto mensual y la auditoría se hizo con Opus.
- **Incidentes:** un subagente creó por error una sesión de Claude Code vacía (`session_013GXAhuoF94vvuJ9Z8kp5Ud`). No consumió nada y está pendiente de archivar.
- **Ajustes por resultados:** la corrección de la leyenda de Monteluz; la regla de no inventar horas ni escasez; la regla de no reformular claims; el Guardián del día a día pasó de Opus a Sonnet.
- **Repositorio:** el PR #2 (primer borrador) se fusionó el 14 de octubre. Este trabajo va en el PR #4.
