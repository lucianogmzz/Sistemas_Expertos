import json
import os

CHARACTER_FILE = "characters.json"
MIN_QUESTIONS = 5
CATEGORY_ORDER = ["rol", "genero", "aspecto", "personalidad", "narrativa", "estilo", "distintivo"]

QUESTION_TEMPLATES = {
    "rol": "¿Trabaja en {value}?",
    "genero": "¿Es {value}?",
    "aspecto": "¿Tiene {value}?",
    "personalidad": "¿Es {value}?",
    "narrativa": "¿Es uno de los personajes {value}?",
    "estilo": "¿Suele usar {value}?",
    "distintivo": "¿Presenta {value}?"
}

def load_characters(path=CHARACTER_FILE):
    if not os.path.exists(path):
        print("⚠️ No se encontró el archivo characters.json.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ask_yes_no(prompt):
    while True:
        a = input(prompt + " (s/n): ").strip().lower()
        if a in ("s", "si", "sí"):
            return True
        if a in ("n", "no"):
            return False
        print("Por favor, responde con 's' o 'n'.")

def format_question(attribute, value):
    template = QUESTION_TEMPLATES.get(attribute, "¿{value}?")
    return template.format(value=value)

def ask_question(attribute, remaining_chars, asked_features):
    """
    Escoge un rasgo no preguntado de la categoría y genera pregunta natural.
    Filtra candidatos según la respuesta.
    """
    counts = {}
    for char in remaining_chars:
        values = char.get(attribute, [])
        if isinstance(values, str):
            values = [values]
        for v in values:
            if v not in asked_features:
                counts[v] = counts.get(v, 0) + 1

    if not counts:
        return remaining_chars, asked_features

    # Elegir rasgo más común
    value = max(counts.items(), key=lambda x: x[1])[0]
    question = format_question(attribute, value)
    answer = ask_yes_no(question)
    asked_features.add(value)

    # Filtrar candidatos
    new_remaining = []
    for char in remaining_chars:
        vals = char.get(attribute, [])
        if isinstance(vals, str):
            vals = [vals]
        if (answer and value in vals) or (not answer and value not in vals):
            new_remaining.append(char)

    return new_remaining, asked_features

def guess_character():
    characters = load_characters()
    if not characters:
        print("No hay personajes disponibles.")
        return

    remaining_chars = characters.copy()
    asked_count = 0
    asked_features = set()
    category_index = 0

    print("\n🧠 Piensa en un personaje de The Office y responde con 's' o 'n'.")

    # Preguntas por categorías en orden, mínimo 5
    while asked_count < MIN_QUESTIONS and remaining_chars:
        category = CATEGORY_ORDER[category_index % len(CATEGORY_ORDER)]
        remaining_chars, asked_features = ask_question(category, remaining_chars, asked_features)
        asked_count += 1
        category_index += 1

    # Continuar preguntando por descarte si quedan varios candidatos
    while len(remaining_chars) > 1:
        # Elegir el primer candidato y preguntar directamente
        candidate = remaining_chars[0]
        answer = ask_yes_no(f"¿El personaje es {candidate['nombre']}?")
        if answer:
            print(f"\n🎉 ¡El personaje es {candidate['nombre']}!")
            return
        else:
            remaining_chars.pop(0)

    # Si queda un solo candidato
    if remaining_chars:
        print(f"\n🎉 ¡El personaje es {remaining_chars[0]['nombre']}!")
    else:
        print("\n🤔 No pude adivinar el personaje. 😅")

def main():
    print("=== 🧩 Akinator: The Office (Motor por descarte con características múltiples) ===")
    while True:
        guess_character()
        if not ask_yes_no("\n¿Quieres jugar otra vez?"):
            break
    print("\n✅ Gracias por jugar.")

if __name__ == "__main__":
    main()
