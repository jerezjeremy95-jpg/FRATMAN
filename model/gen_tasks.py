"""Genera los encargos (en español) con los que los subagentes escriben textos de IA para entrenar y probar.

Cada encargo imita una petición real a un asistente: género + tema + extensión + a veces un estilo.
Los temas se reparten entre entrenamiento y prueba para que la prueba use temas nunca vistos.
"""
import json
import random
import sys

R = random.Random(2026)

TEMAS = [
    "el uso del celular en las escuelas", "la inteligencia artificial en la educación", "el cambio climático en el Caribe",
    "la contaminación de los ríos", "el reciclaje en los hogares", "la salud mental de los jóvenes", "el teletrabajo",
    "la inflación y el costo de la canasta básica", "el turismo en Punta Cana", "la migración hacia Estados Unidos",
    "el béisbol dominicano", "el reguetón y la música urbana", "la lectura en la era digital", "las redes sociales y la autoestima",
    "la seguridad ciudadana", "el tránsito en Santo Domingo", "el transporte público", "la energía solar",
    "los apagones", "la escasez de agua", "la agricultura familiar", "el precio del aguacate", "la pesca artesanal",
    "las elecciones municipales", "la corrupción", "la educación financiera", "el emprendimiento juvenil",
    "las criptomonedas", "la ciberseguridad", "el comercio electrónico", "las pequeñas empresas", "el marketing digital",
    "Instagram para negocios locales", "la publicidad engañosa", "la comida rápida", "la dieta mediterránea",
    "el sedentarismo", "el dengue", "la vacunación infantil", "el embarazo adolescente", "la violencia de género",
    "la igualdad salarial", "los derechos de los animales", "la adopción de mascotas", "el maltrato animal",
    "la importancia del sueño", "el estrés en la universidad", "la procrastinación", "aprender un segundo idioma",
    "estudiar en el extranjero", "las becas universitarias", "el costo de la matrícula", "la deserción escolar",
    "los videojuegos", "la piratería", "el streaming", "los podcasts", "el periodismo local", "las noticias falsas",
    "la libertad de prensa", "la pandemia de COVID-19", "la salud pública", "los hospitales públicos",
    "el envejecimiento de la población", "las pensiones", "la vivienda", "los alquileres", "la gentrificación",
    "el carnaval", "la Semana Santa", "la Navidad en familia", "el merengue", "la bachata", "la gastronomía local",
    "el sancocho", "el café de montaña", "el cacao orgánico", "las playas", "los parques nacionales",
    "la deforestación", "los huracanes", "los terremotos", "la sequía", "el plástico de un solo uso",
    "la moda rápida", "la ropa de segunda mano", "los influencers", "el consumo responsable", "las compras en línea",
    "la banca digital", "los pagos con el celular", "el ahorro", "las deudas con tarjetas de crédito",
    "la automatización del trabajo", "los robots en las fábricas", "el futuro del empleo", "las habilidades blandas",
    "el liderazgo", "el trabajo en equipo", "la atención al cliente", "las reuniones de trabajo", "el síndrome de burnout",
    "la familia", "la amistad", "el primer amor", "la soledad", "la jubilación", "los abuelos", "la crianza de los hijos",
    "el voluntariado", "la religión en la vida diaria", "la tolerancia", "la discriminación", "el racismo",
    "la historia de Santo Domingo", "la independencia", "los taínos", "la arquitectura colonial", "los museos",
    "el cine latinoamericano", "una serie de moda", "un libro que te cambió la vida", "la poesía", "el teatro",
    "el fútbol", "los Juegos Olímpicos", "el atletismo", "el ciclismo urbano", "el gimnasio", "correr una maratón",
    "la astronomía", "los viajes espaciales", "la biotecnología", "la medicina personalizada", "las vacunas de ARN",
    "los teléfonos plegables", "la realidad virtual", "los autos eléctricos", "el metro", "las bicicletas compartidas",
]

GENEROS = [
    # (clave, plantilla de encargo, rango de palabras)
    ("noticia", "Escribe una noticia de unas {n} palabras sobre {t}.", (150, 300)),
    ("noticia", "Redacta una nota de prensa de unas {n} palabras sobre un hecho reciente relacionado con {t}.", (120, 250)),
    ("academico", "Escribe un párrafo académico de unas {n} palabras para el marco teórico de una tesis sobre {t}.", (120, 260)),
    ("academico", "Redacta la introducción (unas {n} palabras) de un trabajo universitario sobre {t}.", (150, 300)),
    ("academico", "Escribe el planteamiento del problema de una investigación sobre {t}, en unas {n} palabras.", (120, 250)),
    ("ensayo", "Escribe un ensayo corto de unas {n} palabras sobre {t}.", (180, 350)),
    ("ensayo", "Escribe un ensayo argumentativo de unas {n} palabras sobre {t}.", (180, 350)),
    ("personal", "Escribe una redacción de unas {n} palabras, como estudiante, sobre {p}.", (120, 280)),
    ("opinion", "Escribe un artículo de opinión de unas {n} palabras sobre {t}.", (150, 300)),
    ("blog", "Escribe una entrada de blog de unas {n} palabras sobre {t}.", (150, 300)),
    ("resena", "Escribe una reseña de unas {n} palabras de {r}.", (80, 220)),
    ("redes", "Escribe una publicación para Instagram de una marca local sobre {t}.", (30, 90)),
    ("redes", "Escribe un tuit sobre {t}.", (15, 50)),
    ("correo", "Escribe un correo electrónico de unas {n} palabras {c}.", (80, 200)),
    ("guia", "Explica paso a paso, en unas {n} palabras, cómo {h}.", (100, 250)),
    ("legal", "Redacta un artículo de un reglamento interno de una institución sobre {t}, en unas {n} palabras.", (80, 200)),
    ("discurso", "Escribe una intervención de un diputado en el Congreso sobre {t}, de unas {n} palabras.", (150, 300)),
    ("explicacion", "Explícame en unas {n} palabras qué es y por qué importa {t}.", (100, 250)),
    ("marketing", "Escribe la descripción de un producto o servicio relacionado con {t}, de unas {n} palabras.", (60, 160)),
    ("relato", "Escribe un relato corto de unas {n} palabras sobre {t}.", (150, 300)),
    ("foro", "Responde en un foro, en unas {n} palabras, a alguien que pregunta por {t}.", (80, 200)),
    ("carta", "Escribe una carta de motivación de unas {n} palabras para una beca relacionada con {t}.", (150, 280)),
]

PERSONAL = [
    "una persona famosa que admiras", "tus vacaciones perfectas", "un lugar especial para ti", "algo terrible que te pasó",
    "tu ciudad", "tu familia", "un recuerdo de la infancia", "tu mejor amigo", "un viaje inolvidable", "tu comida favorita",
    "un lugar que no te gusta", "algo hermoso que viste", "tu primer día de universidad", "tus metas para el futuro",
    "una tradición de tu país", "un maestro que te marcó", "tu fin de semana ideal", "un error del que aprendiste",
]
RESENAS = [
    "un restaurante de comida criolla", "un teléfono de gama media", "una película de suspenso", "una novela latinoamericana",
    "un hotel en la playa", "unos audífonos inalámbricos", "una cafetería del centro", "un curso en línea de inglés",
    "una serie de televisión", "un gimnasio del barrio", "una aplicación de delivery", "un concierto en vivo",
    "una laptop para estudiantes", "una crema hidratante", "un libro de autoayuda", "una pizzería",
]
CORREOS = [
    "a un profesor para pedir una prórroga", "a un cliente para enviar una cotización", "al equipo para cambiar una reunión",
    "a recursos humanos para pedir vacaciones", "a un proveedor para reclamar un pedido atrasado",
    "a una empresa para postular a un empleo", "a un compañero para pedir apuntes", "al banco para reportar un cobro indebido",
    "a los padres de familia sobre una actividad escolar", "a un cliente para agradecer su compra",
]
COMO = [
    "preparar un presupuesto mensual", "estudiar para un examen final", "hacer un currículum", "cuidar plantas en casa",
    "empezar a correr", "abrir una cuenta de ahorro", "preparar una entrevista de trabajo", "organizar una fiesta de cumpleaños",
    "reducir el uso del celular", "aprender a cocinar arroz", "escribir una buena introducción", "citar en APA",
    "crear contenido para Instagram", "ahorrar energía en casa", "hacer una presentación en PowerPoint", "cambiar una llanta",
]
ESTILOS = [
    (0.50, ""),
    (0.14, " Escríbelo con un tono natural y cercano, como lo escribiría una persona común."),
    (0.10, " Que no parezca escrito por una inteligencia artificial."),
    (0.08, " Usa un registro muy formal."),
    (0.04, " Usa expresiones de República Dominicana."),
    (0.03, " Usa expresiones de México."),
    (0.03, " Usa expresiones de Argentina."),
    (0.03, " Usa expresiones de España."),
    (0.03, " Usa expresiones de Colombia."),
    (0.02, " Escríbelo como un estudiante de secundaria."),
]


def estilo():
    x, acc = R.random(), 0
    for p, s in ESTILOS:
        acc += p
        if x < acc:
            return s
    return ""


def make(n, temas, start_id, tag):
    out = []
    for k in range(n):
        key, tpl, (lo, hi) = R.choice(GENEROS)
        words = R.randrange(lo, hi + 1, 10) if hi - lo > 20 else R.randint(lo, hi)
        req = tpl.format(n=words, t=R.choice(temas), p=R.choice(PERSONAL), r=R.choice(RESENAS), c=R.choice(CORREOS), h=R.choice(COMO))
        out.append({"id": f"{tag}{start_id + k:04d}", "genero": key, "encargo": req + estilo()})
    return out


temas = TEMAS[:]
R.shuffle(temas)
cut = int(len(temas) * 0.85)
train = make(1110, temas[:cut], 0, "g")
bench = make(150, temas[cut:], 0, "b")
out = sys.argv[1]
json.dump({"train": train, "bench": bench, "temas_prueba": temas[cut:]}, open(out, "w"), ensure_ascii=False, indent=0)
print(len(train), len(bench), "temas prueba:", len(temas[cut:]))
from collections import Counter
print(Counter(t["genero"] for t in train).most_common())
print(sum(1 for t in train if "inteligencia artificial" in t["encargo"] and "parezca" in t["encargo"]), "humanizados")
