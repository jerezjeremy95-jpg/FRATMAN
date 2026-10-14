---
description: Pedido cercano (correo a un cliente) que NO debe activar las skills de contenido del agente.
tags: [activacion, negativo]
runs: 2
model: sonnet
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

Escríbeme un correo corto y amable para el cliente de la panadería pidiéndole el logo en alta resolución y los horarios actualizados del local para el post del sábado.
