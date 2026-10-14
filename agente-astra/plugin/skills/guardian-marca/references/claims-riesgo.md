# Catálogo de claims riesgosos

Este catálogo sirve para revisar copys de redes sociales (captions, carruseles, texto en imagen, guiones, Stories, LinkedIn). Lo usan el Guardián (para revisar) y el Reciclador y el Guionista (para no crear el riesgo). Es una guía de criterio, no una lista de palabras prohibidas: lo que importa es **qué promete la frase**, no si contiene una palabra.

Contenido:
1. Severidades
2. Tipos de hallazgo (códigos para el registro)
3. Patrones por tipo, con alternativa segura
4. Lo que NO es problema (evitar falsos positivos)
5. Cómo escribir la corrección

---

## Por qué importa
En República Dominicana, el anunciante **y la agencia** responden solidariamente por la publicidad engañosa (`marco-rd.md` §1). Un claim que se escapa no es solo un problema del cliente: también es de Astra.

## 1. Severidades

| Severidad | Qué significa | Efecto en el veredicto |
|---|---|---|
| 🔴 **Alta** | Puede causar sanción, reclamo, daño de reputación o incumple una orden explícita del cliente. | Con una sola: **No publicar** hasta corregir. |
| 🟡 **Media** | Exagera, le faltan condiciones o se sale del tono; un cliente o un usuario lo puede cuestionar. | **Ajustar** antes de enviar. |
| 🔵 **Baja** | Mejora de estilo, claridad o formato. No es un riesgo. | Opcional. |

Regla de desempate: si dudas entre dos severidades porque falta información (¿hay estudio?, ¿hay licencia?), elige la más alta **y** agrega la pregunta en "Para decidir por un humano".

## 2. Tipos de hallazgo

Usa exactamente estos códigos en el registro JSON. Así el equipo puede contar en Looker Studio qué riesgos aparecen más.

| Código | Qué cubre |
|---|---|
| `salud` | Efectos en el cuerpo o la mente, enfermedades, órganos, resultados físicos. |
| `respaldo_falso` | "Recomendado por médicos", "clínicamente probado", "avalado por expertos" sin documento. |
| `cifra_sin_fuente` | Estadísticas, porcentajes, rankings, conteos de clientes o asistentes, "X de cada 10". |
| `absoluto` | El mejor, el único, el primero, 100 %, garantizado, siempre, nunca falla. |
| `comparativo` | Comparar o denigrar a competidores, nombrados o aludidos. |
| `precio_promocion` | Precios, descuentos, "gratis", vigencias, urgencia, sorteos y concursos. |
| `alcohol` | Menores, conducir, exceso, rendimiento o éxito asociado al alcohol, leyendas. |
| `datos_personales` | Pedir datos, registros, QR, fotos de asistentes, consentimiento. |
| `propiedad_intelectual` | Marcas, logos o nombres de terceros (ligas, equipos, eventos), música, imágenes ajenas. |
| `ambiental` | Eco, verde, sostenible, biodegradable, "salva el planeta". |
| `menores` | Contenido dirigido a niños o con su imagen. |
| `sensible` | Religión, política partidista, tragedias, burlas o estereotipos sobre grupos. |
| `publicidad_no_identificada` | Colaboraciones pagadas o testimonios sin identificar. |
| `prohibicion_core_brand` | Palabra, tema o recurso que el Core Brand de la marca prohíbe. |
| `tono` | Fuera del tono, la persona gramatical (tú o usted) o el público del Core Brand. |
| `estilo` | Ortografía, claridad, CTA débil, exceso de hashtags o emojis, frases genéricas. |

## 3. Patrones por tipo

### `salud` (el más importante)
**Alta** cuando la frase:
- nombra una enfermedad o condición (ansiedad, depresión, insomnio, inflamación, colesterol, diabetes, presión, gastritis…), un órgano o sistema (hígado, riñones, colon, sistema inmune, metabolismo) o un mecanismo (desintoxica, depura, quema grasa, acelera el metabolismo, regula, equilibra las hormonas);
- usa verbos médicos: cura, trata, sana, previene, alivia, elimina, combate, revierte;
- garantiza un resultado físico o pone plazo ("en 2 semanas", "baja 5 libras", "duerme toda la noche");
- dice "sin efectos secundarios" o "sin contraindicaciones";
- usa imágenes de antes y después.

**Media** cuando es un beneficio funcional vago, sin plazo ni garantía: "recarga tu energía", "te ayuda a relajarte", "para sentirte más liviano", "hidrata tu cuerpo", "menos tensión en la oficina". Se reformula como experiencia.

Las alternativas de esta tabla suponen que los datos que usan (ingredientes, método de preparación) son ciertos y están en la pieza o en el Core Brand. Si no lo están, usa una alternativa sin datos o márcalos con `[confirmar]`.

| Riesgoso | Alternativa segura |
|---|---|
| "Depura tu organismo" | Describir el producto, no el efecto: "verde, fresco y recién hecho" |
| "Baja de peso sin esfuerzo" | Eliminar. Si el Core Brand lo permite: "parte de tu rutina activa" |
| "Duerme mejor desde la primera noche" | "Un momento tranquilo para cerrar el día" |
| "Mejora tu sistema inmune" | Eliminar, o nombrar el ingrediente real sin atribuirle efecto: "con jengibre y limón" |
| "Más vitalidad cada mañana" | "Para arrancar la mañana con buen sabor" |
| "Sin contraindicaciones" | Eliminar |
| "Sanación emocional en cada clase" | "Un rato para ti en cada clase" |

Base legal: en alimentos y bebidas no se pueden sugerir efectos preventivos o curativos, y Pro Consumidor prohíbe anunciar curas, prevención o tratamientos rápidos o bajar de peso sin ejercicio sin prueba científica (`marco-rd.md` §2). Los medicamentos tienen reglas propias: si la pieza anuncia uno, es **Alta** y va a "Para decidir por un humano".

### `respaldo_falso`
"Recomendado por médicos o psicólogos", "clínicamente probado", "científicamente comprobado", "aprobado por nutricionistas": **Alta** salvo que exista un documento que el cliente haya autorizado a citar. Aunque exista, va a "Para decidir por un humano": el cliente o su área legal decide.

### `cifra_sin_fuente`
Toda cifra presentada como hecho necesita fuente: "8 de cada 10 personas lo recomiendan", "más de 1,000 familias ya lo prueban", "mejora la concentración un 30 %", "+5,000 asistentes", "#1 en ventas". **Alta** si parece un dato de estudio o de mercado; **Media** si es un dato interno del cliente que solo hay que confirmar (número de sucursales, años en el mercado).
Alternativa: `[confirmar: dato y fuente con el cliente]`, o quitar la cifra y quedarse con el mensaje: "cada vez más familias se suman".

### `absoluto`
"La mejor pizza del Cibao", "el único en RD", "el primero en el país", "100 % puro", "garantizado", "nunca falla", "calidad insuperable". Normalmente **Media**; **Alta** si es un dato comprobable falso o si compara con otros.
Alternativa: hablar de lo propio y concreto (si es cierto): "la pizza de la casa", "masa madre horneada en leña", "nuestra favorita".

### `comparativo`
La comparativa está prohibida si es engañosa, no objetiva o denigra (`marco-rd.md` §1). Nombrar o aludir a la competencia ("a diferencia de otras pizzerías que usan masa congelada", "mejor que [marca]"): **Alta**. Alternativa: decir lo propio sin comparar ("masa hecha cada mañana", solo si es un claim aprobado).

### `precio_promocion`
- Precio sin vigencia ni condiciones: **Media** → "RD$[confirmar] · válido hasta [confirmar fecha]". La ley pide que las ofertas digan inicio, fin, cantidad disponible y condiciones, con el precio en RD$ (`marco-rd.md` §1). "Hasta agotar existencia" sin cantidad también cuenta.
- "Gratis" con condiciones ocultas: **Media** → decir la condición: "primera clase sin costo, cupos limitados [confirmar cupos]".
- Urgencia o escasez sin dato ("últimas unidades", "solo hoy"): **Media**.
- Sorteos, concursos y "etiqueta a 3 amigos y participa" sin bases publicadas (fechas, mecánica, premio, quién puede participar, cómo se elige): **Alta**. Las bases se registran en Pro Consumidor **al menos 21 días antes** y la publicidad lleva un extracto de ellas; si hay boletos o venta, además se necesita licencia de Hacienda (`marco-rd.md` §5). Va a "Para decidir por un humano": ¿están registradas las bases?

### `alcohol`
**Alta**: dirigirse a menores o mostrar personas que parezcan menores; asociar el alcohol con conducir, con rendimiento deportivo, con éxito social o sexual; premiar o celebrar el exceso ("quien aguante más rondas…"); presentar el alcohol como solución a problemas o atribuirle bienestar o energía. **Falta de la leyenda legal "El consumo de alcohol perjudica la salud"** (Ley 42-01, art. 123; ver `marco-rd.md` §3): **Alta**. Si el Core Brand exige además su propia leyenda, también tiene que estar.
Buena práctica: las personas que aparecen bebiendo deben verse claramente adultas.

### `datos_personales`
**Alta**: pedir cédula, teléfono, dirección o datos de salud por comentarios o mensajes directos; formularios, QR o registros sin aviso de uso ni consentimiento; publicar fotos o videos de asistentes sin aviso ni permiso.
Alternativa: "Reserva por el link en la bio", con un formulario que tenga aviso de privacidad de la marca. En eventos: aviso visible de que se graba, y consentimiento al registrarse.

### `propiedad_intelectual`
**Alta**: logos, nombres oficiales, uniformes o mascotas de ligas, equipos, eventos o jugadores (por ejemplo LIDOM, cualquier equipo, la Serie del Caribe) sin licencia o patrocinio confirmado; canciones comerciales en piezas de marca; imágenes tomadas de internet como asset final.
Alternativa: referencias genéricas a la temporada ("noche de pelota", "temporada de béisbol", "la pelota invernal") sin logos ni nombres oficiales. Audio: biblioteca comercial de la plataforma, audio original o voz en off.

### `ambiental`
"cero impacto ambiental", "amigable con la Tierra", "biodegradable", "carbono neutral" sin certificación: **Media** (**Alta** si es absoluto y comprobable). Alternativa: decir el hecho concreto y verificable ("vasos de [material] [confirmar certificación]").

### `menores`
**Alta**: pedirle a niños que convenzan a sus padres de comprar; usar imagen de menores sin autorización de padres o tutores; cualquier relación de menores con alcohol.

### `sensible`
**Alta**: burlas o estereotipos sobre nacionalidad, raza, género, orientación, clase, región, religión o discapacidad; humor con tragedias; política partidista; temas religiosos usados como gancho comercial.

### `publicidad_no_identificada`
Influencer o creador que recomienda la marca sin identificar la colaboración: **Media**, y "Para decidir por un humano" si no se sabe si es pagada. Testimonios inventados o editados: **Alta**.

### `prohibicion_core_brand`
Cualquier palabra, tema o recurso que el Core Brand prohíbe: **Alta**, porque es una instrucción explícita del cliente. Cita la regla del Core Brand en el hallazgo.

### `tono`
Persona gramatical equivocada (usted en vez de tú), registro (corporativo en una marca cercana), humor donde el Core Brand pide seriedad, o al revés: **Media**. Frases genéricas de IA: **Baja**.

## 4. Lo que NO es problema

Marcar todo hace que el equipo ignore al Guardián. No marques:
- Opiniones claramente subjetivas o de sabor: "riquísimo", "te va a encantar", "nuestro favorito".
- Claims que el Core Brand lista como aprobados (por ejemplo, "hecho en RD" o "receta de la casa", si están en su lista).
- Invitaciones y descripciones de experiencia: "ven a desconectar", "un espacio para respirar", "para compartir con tu gente".
- Emojis, humor sano y expresiones dominicanas dentro del tono de la marca.
- Datos públicos con fuente (el clima, una fecha, una tendencia citada).
- Leyendas legales correctas.

## 5. Cómo escribir la corrección

1. **Del resultado a la experiencia.** "Adiós al estrés" → "un rato para ti".
2. **Del absoluto a lo concreto.** "La mejor pizza del Cibao" → "masa madre horneada en leña" (si es cierto y está aprobado).
3. **Del dato suelto a la fuente.** Cifra → fuente citada o `[confirmar: …]`.
4. **De la promo vaga a las condiciones.** Precio → vigencia; sorteo → bases.
5. **Si no hay versión segura, elimina** y dilo. Es mejor un copy más corto que uno riesgoso.
6. **Conserva el tono y la longitud** de la marca: la corrección tiene que sonar a la marca, no a un abogado.
7. **No metas claims nuevos** al corregir. Usa solo lo que ya decía la pieza o lo que el Core Brand tiene como claim aprobado. La corrección no puede crear un riesgo distinto.
