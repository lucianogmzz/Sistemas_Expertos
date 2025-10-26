import json
import random
import os
import tkinter as tk
from PIL import Image, ImageTk  # pip install pillow

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
# INTERFAZ GRÁFICA
# ==============================
class TheOfficeUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Akinator The Office")
        self.root.geometry("900x650")
        self.root.configure(bg="#1c3d5a")

        self.ui_mode = "asking"

        # --- CONTENEDOR CENTRAL ---
        self.main_frame = tk.Frame(root, bg="#1c3d5a")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # --- TÍTULO ---
        self.title_label = tk.Label(
            self.main_frame,
            text="Akinator The Office",
            font=("Impact", 36, "bold"),
            fg="white",
            bg="#1c3d5a"
        )
        self.title_label.pack(pady=(0, 20))

        # --- LOGO OPCIONAL ---
        if os.path.exists("logo.png"):
            logo_img = Image.open("logo.png").resize((200, 80))
            self.logo = ImageTk.PhotoImage(logo_img)
            tk.Label(self.main_frame, image=self.logo, bg="#1c3d5a").pack(pady=(0, 20))

        # --- PREGUNTA ---
        self.question_label = tk.Label(
            self.main_frame,
            text="Bienvenido a Dunder Mifflin 🎬",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#1c3d5a",
            wraplength=700,
            justify="center"
        )
        self.question_label.pack(pady=20)

        # --- BOTONES SÍ / NO ---
        self.button_frame = tk.Frame(self.main_frame, bg="#1c3d5a")
        self.button_frame.pack(pady=10)

        self.yes_btn = tk.Button(
            self.button_frame,
            text="Sí",
            width=14,
            bg="#2e8b57",
            fg="white",
            font=("Arial", 14, "bold"),
            command=lambda: self.answer("s")
        )
        self.no_btn = tk.Button(
            self.button_frame,
            text="No",
            width=14,
            bg="#b22222",
            fg="white",
            font=("Arial", 14, "bold"),
            command=lambda: self.answer("n")
        )
        self.yes_btn.grid(row=0, column=0, padx=40)
        self.no_btn.grid(row=0, column=1, padx=40)

        # --- ZONA DE RESULTADOS ---
        self.image_label = tk.Label(self.main_frame, bg="#1c3d5a")
        self.image_label.pack(pady=25)
        self.result_label = tk.Label(self.main_frame, text="", fg="white", bg="#1c3d5a", font=("Arial", 16))
        self.result_label.pack()

        # --- BOTÓN DE REINICIO ---
        self.restart_btn = tk.Button(
            self.main_frame,
            text="Jugar de nuevo",
            width=18,
            bg="#4682b4",
            fg="white",
            font=("Arial", 13, "bold"),
            command=self.reset_game
        )
        self.restart_btn.pack(pady=15)
        self.restart_btn.pack_forget()

        # --- Motor ---
        self.characters = load_knowledge()
        self.reset_game()

    # ==============================
    # ESTADOS DE LOS BOTONES
    # ==============================
    def set_buttons_to_answer_mode(self):
        self.ui_mode = "asking"
        self.yes_btn.config(text="Sí", bg="#2e8b57", command=lambda: self.answer("s"))
        self.no_btn.config(text="No", bg="#b22222", command=lambda: self.answer("n"))
        self.yes_btn.config(state="normal")
        self.no_btn.config(state="normal")

    def set_buttons_to_confirm_mode(self):
        self.ui_mode = "confirm"
        self.yes_btn.config(text="Correcto", bg="#2e8b57", command=self.confirm_yes)
        self.no_btn.config(text="Incorrecto", bg="#b22222", command=self.confirm_no)
        self.yes_btn.config(state="normal")
        self.no_btn.config(state="normal")

    # ==============================
    # LÓGICA PRINCIPAL
    # ==============================
    def reset_game(self):
        self.remaining_chars = self.characters.copy()
        self.asked_features = set()
        self.asked_count = 0
        self.category_index = 0
        self.image_label.config(image="", text="")
        self.result_label.config(text="")
        self.restart_btn.pack_forget()
        self.question_label.config(text="Piensa en un personaje de The Office 😏")
        self.set_buttons_to_answer_mode()
        self.next_question()

    def next_question(self):
        if not self.remaining_chars:
            self.show_message("No estoy seguro de quién podría ser 😔")
            self.show_restart_button()
            return

        if (self.asked_count >= MIN_QUESTIONS and len(self.remaining_chars) == 1):
            self.guess_character(self.remaining_chars[0])
            return

        category = CATEGORY_ORDER[self.category_index % len(CATEGORY_ORDER)]
        opciones = []
        for char in self.remaining_chars:
            value = char.get(category)
            if isinstance(value, list):
                for v in value:
                    if v not in self.asked_features:
                        opciones.append(v)
            elif isinstance(value, str):
                if value not in self.asked_features:
                    opciones.append(value)

        if not opciones:
            self.category_index += 1
            self.next_question()
            return

        self.feature = random.choice(opciones)
        pregunta = f"¿El {category} es '{self.feature}'?"
        self.question_label.config(text=pregunta)
        self.category_index += 1
        self.asked_count += 1
        self.set_buttons_to_answer_mode()

    def answer(self, ans):
        if self.ui_mode != "asking":
            return

        category = CATEGORY_ORDER[(self.category_index - 1) % len(CATEGORY_ORDER)]
        if ans == "s":
            self.remaining_chars = [
                c for c in self.remaining_chars
                if (self.feature in c.get(category, [])) or (self.feature == c.get(category))
            ]
        else:
            self.remaining_chars = [
                c for c in self.remaining_chars
                if not ((self.feature in c.get(category, [])) or (self.feature == c.get(category)))
            ]
        self.asked_features.add(self.feature)
        self.next_question()

    def guess_character(self, character):
        name = character["nombre"]
        self.question_label.config(text=f"Creo que estás pensando en...")
        self.show_image(name)
        self.result_label.config(text=f"🕵️‍♂️ {name}")
        self.set_buttons_to_confirm_mode()

    # ==============================
    # CONFIRMACIÓN
    # ==============================
    def confirm_yes(self):
        self.question_label.config(text="¡Genial! Sabía que lo adivinaría 😏")
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")
        self.show_restart_button()  # ✅ ahora aparece el botón Jugar de nuevo

    def confirm_no(self):
        self.question_label.config(text="Vaya — no lo adiviné. Puedes enseñarme abriendo la consola.")
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")
        self.show_restart_button()

    # ==============================
    # UI AUXILIARES
    # ==============================
    def show_image(self, name):
        img_path_jpg = os.path.join("images", f"{name}.jpg")
        img_path_png = os.path.join("images", f"{name}.png")
        img_path = img_path_jpg if os.path.exists(img_path_jpg) else (img_path_png if os.path.exists(img_path_png) else None)

        if img_path:
            img = Image.open(img_path).resize((250, 320))
            self.char_img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.char_img, text="")
        else:
            self.image_label.config(image="", text="(Imagen no disponible)", fg="white")

    def show_message(self, text):
        self.question_label.config(text=text)
        self.image_label.config(image="", text="")
        self.result_label.config(text="")

    def show_restart_button(self):
        """Muestra el botón de jugar de nuevo."""
        self.restart_btn.pack(pady=15)
        self.restart_btn.lift()

# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    app = TheOfficeUI(root)
    root.mainloop()
