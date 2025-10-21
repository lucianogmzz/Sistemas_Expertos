import json
import random
import os

# ==============================
# CONFIGURACIÓN BÁSICA
# ==============================
MIN_QUESTIONS = 5
JSON_FILE = "characters.json"

CATEGORY_ORDER = ["rol", "genero", "aspecto", "personalidad", "narrativa", "estilo", "distintivo"]


# ==============================
# FUNCIONES DE CARGA / GUARDADO
# ==============================
def load_knowledge(filename=JSON_FILE):
    if not os.path.exists(filename):
        print("⚠️ No se encontró la base de datos. Se creará una nueva.")
        return []
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            print("⚠️ Error al leer el archivo JSON. Se iniciará una base vacía.")
            return []


def save_knowledge(data, filename=JSON_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ==============================
# MOTOR DE PREGUNTAS
# ==============================
def ask_question(category, remaining_chars, asked_features):
    """Genera una pregunta basada en una categoría."""
    opciones = []
    for char in remaining_chars:
        value = char.get(category)
        if isinstance(value, list):
            for v in value:
                if v not in asked_features:
                    opciones.append(v)
        elif isinstance(value, str):
            if value not in asked_features:
                opciones.append(value)

    if not opciones:
        return remaining_chars, asked_features

    feature = random.choice(opciones)
    pregunta = f"¿El {category} es '{feature}'? (s/n): "
    ans = input(pregunta).strip().lower()

    # Filtrar candidatos
    if ans == "s":
        remaining_chars = [
            c for c in remaining_chars
            if (feature in c.get(category, [])) or (feature == c.get(category))
        ]
    else:
        remaining_chars = [
            c for c in remaining_chars
            if not ((feature in c.get(category, [])) or (feature == c.get(category)))
        ]

    asked_features.add(feature)
    return remaining_chars, asked_features


# ==============================
# FUNCIÓN DE APRENDIZAJE
# ==============================
def learn_new_character(characters):
    print("\n🤔 Parece que no acerté. ¡Enséñame un nuevo personaje!")
    nombre = input("¿En quién estabas pensando? ").strip()

    # Evitar duplicados
    if any(c['nombre'].lower() == nombre.lower() for c in characters):
        print("Ya conozco a ese personaje. Intentaré mejorar mis preguntas la próxima vez.")
        return characters

    nuevo = {
        "nombre": nombre,
        "rol": input("¿Qué rol tiene en la oficina?: ").strip(),
        "genero": input("¿Es hombre o mujer?: ").strip(),
        "aspecto": input("Menciona algunos rasgos físicos (separa con comas): ").split(","),
        "personalidad": input("Describe su personalidad (separa con comas): ").split(","),
        "narrativa": input("¿Es personaje principal o secundario?: ").strip(),
        "estilo": input("¿Cómo suele vestir?: ").split(","),
        "distintivo": input("¿Algún rasgo distintivo o hábito?: ").split(",")
    }

    # Limpieza de listas
    for key in ["aspecto", "personalidad", "estilo", "distintivo"]:
        nuevo[key] = [x.strip() for x in nuevo[key] if x.strip()]

    characters.append(nuevo)
    save_knowledge(characters)
    print(f"✅ ¡He aprendido sobre {nombre}! La próxima vez intentaré adivinarlo mejor.")
    return characters


# ==============================
# MOTOR PRINCIPAL
# ==============================
def main():
    print("🧠 Bienvenido al juego de The Office (modo experto)\n")

    while True:
        characters = load_knowledge()
        if not characters:
            print("No hay datos cargados. Agrega personajes antes de jugar.")
            return

        remaining_chars = characters.copy()
        asked_features = set()
        asked_count = 0
        category_index = 0

        # 🔸 Mínimo 5 preguntas, pero sigue si hay más de 1 candidato
        while (asked_count < MIN_QUESTIONS or len(remaining_chars) > 1) and remaining_chars:
            category = CATEGORY_ORDER[category_index % len(CATEGORY_ORDER)]
            remaining_chars, asked_features = ask_question(category, remaining_chars, asked_features)
            asked_count += 1
            category_index += 1

            # Si ya no hay personajes posibles
            if not remaining_chars:
                break

        # 🔸 Intentar adivinar
        if not remaining_chars:
            print("\nNo estoy seguro de quién podría ser 😔.")
            resp = input("¿Quieres enseñarme quién era? (s/n): ").lower()
            if resp == "s":
                characters = learn_new_character(characters)
        elif len(remaining_chars) == 1:
            personaje = remaining_chars[0]["nombre"]
            print(f"\nCreo que estás pensando en... 🕵️‍♂️ {personaje}")
            correcto = input("¿Adiviné correctamente? (s/n): ").lower()
            if correcto != "s":
                characters = learn_new_character(characters)
            else:
                print("😎 ¡Sabía que lo adivinaría!")
        else:
            print("\nTengo varias opciones en mente:")
            for c in remaining_chars:
                print(f" - {c['nombre']}")
            correcto = input("\n¿Está tu personaje en la lista? (s/n): ").lower()
            if correcto != "s":
                characters = learn_new_character(characters)

        # 🔁 Preguntar si desea jugar de nuevo
        again = input("\n¿Quieres jugar otra vez? (s/n): ").strip().lower()
        if again != "s":
            print("\n👋 ¡Gracias por jugar! ¡Vuelve pronto a Dunder Mifflin!")
            break
        else:
            print("\n🔄 Reiniciando el juego...\n")

# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    main()
