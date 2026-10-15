# Agente Astra

Agente de contenido para el equipo de Astra, hecho con Claude. Revisa, recicla y escribe contenido para las marcas clientes con las reglas de la agencia, y usa el modelo de Claude que conviene en cada paso.

> **Todo lo que produce es un borrador.** Una persona del equipo aprueba antes de que algo llegue al cliente. El agente no publica, no programa y no envía nada.

## Qué hace

| Herramienta | Para qué | Entrega |
|---|---|---|
| **Guardián de marca y claims** (`guardian-marca`) | Revisar un copy antes de enviarlo o publicarlo | Veredicto 🔴/🟡/🟢, cada riesgo con su corrección, versión corregida, preguntas para un humano y una línea de registro para medir |
| **Reciclador de contenido** (`reciclador-contenido`) | Sacarle más a una pieza aprobada | Guion de Reel, Stories, post de LinkedIn y 3 captions, sin claims nuevos y con pase del Guardián |
| **Guionista de Reels** (`guionista-reels`) | Pasar de una idea, un brief o una fecha a un video | 3 hooks, tabla de tomas, texto en pantalla, audio seguro, caption y notas de producción |
| **Agente Astra** (`agente-astra`) | Pedir en lenguaje normal o combinar pasos | Elige la herramienta, el orden y el modelo, y aplica los principios |

Se integra con las skills que el equipo ya usa (Radar Cibao, Design Board) y con el stack actual: Drive para los Core Brand, Canva, Make para mover datos, Google Sheets y Looker Studio para medir, y Trello para lo aprobado. Costo adicional: **US$0**.

## Un modelo para cada tarea

| Paso | Modelo | Dónde se aplica |
|---|---|---|
| Mecánico: extraer texto, contar, sumar tiempos | **Haiku** | Subagentes `extractor-piezas` y `verificador-formato`, comando `/agente-astra:extraer` |
| Redacción: guiones, Stories, LinkedIn, captions | **Sonnet** | Subagente `redactor-multicanal`, comandos `/agente-astra:reciclar` y `/agente-astra:guion` |
| Guardián del día a día | **Sonnet** | Comando `/agente-astra:guardian` |
| Juicio de piezas sensibles: salud, alcohol, datos, sorteos, menores, pauta | **Opus** (esfuerzo alto) | Subagente `auditor-claims` (el Guardián delega en él) |
| Crítico: auditoría antes de una campaña grande | **Fable** | A pedido, en el chat |

En Claude.ai el modelo lo elige la persona y el agente recomienda cuál usar. En Cowork y Claude Code el enrutamiento es automático. Detalle y resultados medidos: [`compartido/enrutamiento-modelos.md`](compartido/enrutamiento-modelos.md).

## Instalación

### Opción A (recomendada) · Plugin desde Cowork
1. En la app de escritorio de Claude: **Customize → Plugins → Add marketplace** → escribe `jerezjeremy95-jpg/FRATMAN`.
2. Instala **agente-astra**.
3. Listo. El plugin queda guardado en tu cuenta, así que sus skills también aparecen en el **chat de Claude.ai** y en **Claude Code**. En Cowork, además, se activan los subagentes y comandos con su modelo fijo.
4. Conecta Google Drive (y Canva, si lo usan) para que el agente lea los Core Brand.

Para actualizar: **Check for updates** en el marketplace, o activa **Sync automatically**.
Sin GitHub: en la página de Plugins, sube el archivo `dist/agente-astra-plugin.zip`.

### Opción B · Solo las skills, en Claude.ai
1. Descarga los zip de [`dist/`](dist/): `agente-astra.zip`, `guardian-marca.zip`, `reciclador-contenido.zip` y `guionista-reels.zip`.
2. En Claude.ai: **Customize → Skills** → sube cada zip. La ejecución de código tiene que estar activada en **Settings → Capabilities**.
3. Opcional: crea el Proyecto "Agente Astra" con [`proyecto-claude/instrucciones.md`](proyecto-claude/instrucciones.md).

### Opción C · Claude Code
```
/plugin install agente-astra --marketplace jerezjeremy95-jpg/FRATMAN
```
En versiones anteriores a la 2.1.275, en dos pasos: `/plugin marketplace add jerezjeremy95-jpg/FRATMAN` y después `/plugin install agente-astra@fratman`.

## Cómo pedir las cosas

- "Revisa este caption de [marca] antes de mandárselo al cliente: …"
- "Recicla este carrusel aprobado de [marca] para Reel, Stories y LinkedIn."
- "Guion de Reel de 20 s para [marca] por el inicio de la temporada de pelota."
- "Agente Astra: del Design Board de [marca] de este mes, revisa los posts y recicla los dos mejores."
- En Cowork o Claude Code: `/agente-astra:guardian [marca] [copy]` corre la revisión en Sonnet y pasa a Opus las piezas sensibles.

## Principios
Todo es borrador; del material de clientes solo se usa lo autorizado; no se inventan precios ni cifras; sin promesas médicas; los datos de asistentes requieren consentimiento y son del cliente; la anfitriona del evento es la marca; una agencia a la vez; costo cero. Texto completo: [`compartido/principios-astra.md`](compartido/principios-astra.md).

## Riesgo medido
Las herramientas se probaron con marcas ficticias y riesgos sembrados, en tres modelos, con y sin skill. Resultados, matriz de riesgos y recomendaciones: [`RIESGOS.md`](RIESGOS.md).

## Estructura

```
agente-astra/
├── plugin/                 ← lo que se instala (skills, subagentes y comandos)
│   ├── .claude-plugin/plugin.json
│   ├── skills/             agente-astra · guardian-marca · reciclador-contenido · guionista-reels
│   ├── agents/             extractor-piezas · verificador-formato · redactor-multicanal · auditor-claims
│   └── commands/           guardian · reciclar · guion · extraer
├── compartido/             ← fuente única de las referencias que comparten las skills
├── scripts/                ← sincronizar, validar y empaquetar
├── evals/                  ← pruebas: marcas ficticias, casos, calificación y resultados
├── docs/integraciones.md   ← Make, Google Sheets, Looker Studio y Trello a costo cero
├── proyecto-claude/        ← instrucciones para un Proyecto de Claude.ai
├── dist/                   ← zips listos para instalar
└── RIESGOS.md              ← medición del riesgo
```

## Mantenimiento
1. Edita las referencias compartidas en `compartido/`, nunca dentro de cada skill.
2. Corre `python3 scripts/empaquetar.py`. Sincroniza, valida (incluye la revisión de datos sensibles para el repo público) y regenera `dist/`.
3. Si cambias el criterio del Guardián, vuelve a correr las pruebas de `evals/` (ver `evals/README.md`).
