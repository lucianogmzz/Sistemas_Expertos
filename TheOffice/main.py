import json
import random
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # pip install pillow

# ==============================
# CONFIGURACIÓN BÁSICA
# ==============================
MIN_QUESTIONS = 5
JSON_FILE = "characters.json"
CATEGORY_ORDER = ["rol", "genero", "aspecto", "personalidad", "narrativa", "estilo", "distintivo"]

# ==============================
# CARGA / GUARDADO
# ==============================
def load_knowledge(filename=JSON_FILE):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
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
        self.root.geometry("960x750")
        self.root.configure(bg="#1c3d5a")

        # ----- Canvas principal con scrollbar vertical -----
        self.canvas = tk.Canvas(root, bg="#1c3d5a", highlightthickness=0)
        self.v_scroll = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # ----- Frame (contenido) dentro del canvas -----
        # Creamos main_frame y lo insertamos. Mantendremos su ancho igual al ancho del canvas
        self.main_frame = tk.Frame(self.canvas, bg="#1c3d5a")
        self.window_id = self.canvas.create_window((0, 0), window=self.main_frame, anchor="n")

        # Actualizar scrollregion cuando cambie el contenido
        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Ajustar el ancho del frame para que coincida con el canvas (para centrar contenido)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Habilitar scroll con rueda en la ventana
        self._bind_mousewheel()

        # Estado y datos
        self.ui_mode = "asking"
        self.characters = load_knowledge()

        # ----------------- INTERFAZ -----------------
        # Título centrado (al usar un frame con ancho igual al canvas, pack center funcionará)
        self.title_label = tk.Label(
            self.main_frame,
            text="Akinator The Office",
            font=("Impact", 36, "bold"),
            fg="white",
            bg="#1c3d5a"
        )
        self.title_label.pack(pady=(16, 8))
        
        # --- SUBTÍTULO CONTEXTUAL ---
        self.subtitle_label = tk.Label(
            self.main_frame,
            text="Piensa en un personaje de The Office… ¿lo tienes? ¡Lo adivinaré!",
            font=("Arial", 16, "italic"),
            fg="#dcdcdc",
            bg="#1c3d5a"
        )
        self.subtitle_label.pack(pady=(0, 20))

        # Texto de pregunta centrado
        self.question_label = tk.Label(
            self.main_frame,
            text="Piensa en un personaje de The Office 😏",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#1c3d5a",
            wraplength=820,
            justify="center"
        )
        self.question_label.pack(pady=(6, 18))

        # Botones Sí / No centrados
        self.button_frame = tk.Frame(self.main_frame, bg="#1c3d5a")
        self.button_frame.pack(pady=8)

        self.yes_btn = tk.Button(
            self.button_frame, text="Sí", width=14, bg="#2e8b57", fg="white",
            font=("Arial", 14, "bold"), command=lambda: self.answer("s")
        )
        self.no_btn = tk.Button(
            self.button_frame, text="No", width=14, bg="#b22222", fg="white",
            font=("Arial", 14, "bold"), command=lambda: self.answer("n")
        )
        # Los pack aquí dentro del button_frame mantienen los botones centrados en la pantalla
        self.yes_btn.pack(side="left", padx=36)
        self.no_btn.pack(side="left", padx=36)

        # Zona de imagen / resultado
        self.image_label = tk.Label(self.main_frame, bg="#1c3d5a")
        self.image_label.pack(pady=14)
        self.result_label = tk.Label(self.main_frame, text="", fg="white", bg="#1c3d5a", font=("Arial", 16))
        self.result_label.pack()

        # Botones de reinicio y de enseñar (ocultos inicialmente)
        self.restart_btn = tk.Button(
            self.main_frame, text="Jugar de nuevo", width=18,
            bg="#4682b4", fg="white", font=("Arial", 13, "bold"), command=self.reset_game
        )
        self.restart_btn.pack(pady=10)
        self.restart_btn.pack_forget()

        self.teach_btn = tk.Button(
            self.main_frame, text="Enseñarme un nuevo personaje", width=28,
            bg="#ff8c00", fg="white", font=("Arial", 13, "bold"), command=self.open_teach_panel
        )
        self.teach_btn.pack(pady=8)
        self.teach_btn.pack_forget()

        # ---------- Panel de enseñanza (contenedor con su propio canvas para scroll) ----------
        self.teach_frame_container = tk.Frame(self.main_frame, bg="#1c3d5a")
        # dentro: canvas + scrollbar + inner frame (para permitir scroll del formulario)
        self.teach_canvas = tk.Canvas(self.teach_frame_container, bg="#274960", highlightthickness=0, height=340)
        self.teach_v = ttk.Scrollbar(self.teach_frame_container, orient="vertical", command=self.teach_canvas.yview)
        self.teach_canvas.configure(yscrollcommand=self.teach_v.set)
        self.teach_inner = tk.Frame(self.teach_canvas, bg="#274960")
        self.teach_canvas.create_window((0, 0), window=self.teach_inner, anchor="nw")
        self.teach_inner.bind("<Configure>", lambda e: self.teach_canvas.configure(scrollregion=self.teach_canvas.bbox("all")))
        # pack para el container (se hará visible con pack cuando se abra)
        # preparar campos
        labels = [
            ("Nombre:", "nombre"),
            ("Rol:", "rol"),
            ("Género:", "genero"),
            ("Aspecto (separa con comas):", "aspecto"),
            ("Personalidad (separa con comas):", "personalidad"),
            ("Narrativa (principal/secundario):", "narrativa"),
            ("Estilo (separa con comas):", "estilo"),
            ("Distintivo (separa con comas):", "distintivo"),
        ]
        self.teach_entries = {}
        for i, (lab_txt, key) in enumerate(labels):
            lbl = tk.Label(self.teach_inner, text=lab_txt, anchor="w", fg="white", bg="#274960", font=("Arial", 11))
            lbl.grid(row=i, column=0, sticky="w", padx=10, pady=6)
            ent = tk.Entry(self.teach_inner, width=48, font=("Arial", 11))
            ent.grid(row=i, column=1, padx=10, pady=6)
            self.teach_entries[key] = ent

        btn_save = tk.Button(self.teach_inner, text="Guardar personaje", bg="#2e8b57", fg="white",
                             font=("Arial", 11, "bold"), command=self.save_new_character)
        btn_cancel = tk.Button(self.teach_inner, text="Cancelar", bg="#b22222", fg="white",
                               font=("Arial", 11, "bold"), command=self.cancel_teach)
        btn_save.grid(row=len(labels), column=0, padx=10, pady=12, sticky="ew")
        btn_cancel.grid(row=len(labels), column=1, padx=10, pady=12, sticky="ew")

        # empaquetado interno del teach container (canvas + scrollbar)
        self.teach_canvas.pack(side="left", fill="both", expand=True)
        self.teach_v.pack(side="right", fill="y")

        # ----------------- Inicializar juego -----------------
        self.reset_game()

    # ----------------- Helpers de layout / scroll -----------------
    def _on_canvas_configure(self, event):
        """Ajusta el ancho del main_frame a ancho del canvas para que pack center funcione y mantiene scrollregion."""
        try:
            canvas_width = event.width
            # ajustar el ancho del frame dentro del canvas
            self.canvas.itemconfigure(self.window_id, width=canvas_width)
        except Exception:
            pass

    def _bind_mousewheel(self):
        """Bind ratón para scroll: Windows/macOS y X11"""
        # Windows / macOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        # X11 (Linux) scroll
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)   # up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)   # down

    def _on_mousewheel_windows(self, event):
        # event.delta positivo = hacia arriba; la cantidad varía por OS
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-3, "units")
        else:
            self.canvas.yview_scroll(3, "units")

    # ----------------- Estados botones -----------------
    def set_buttons_to_answer_mode(self):
        self.ui_mode = "asking"
        self.yes_btn.config(text="Sí", bg="#2e8b57", command=lambda: self.answer("s"), state="normal")
        self.no_btn.config(text="No", bg="#b22222", command=lambda: self.answer("n"), state="normal")

    def set_buttons_to_confirm_mode(self):
        self.ui_mode = "confirm"
        self.yes_btn.config(text="Correcto", bg="#2e8b57", command=self.confirm_yes, state="normal")
        self.no_btn.config(text="Incorrecto", bg="#b22222", command=self.confirm_no, state="normal")

    # ----------------- Lógica principal (motor intacto) -----------------
    def reset_game(self):
        self.remaining_chars = self.characters.copy()
        self.asked_features = set()
        self.asked_count = 0
        self.category_index = 0
        self.image_label.config(image="", text="")
        self.result_label.config(text="")
        self.restart_btn.pack_forget()
        self.teach_btn.pack_forget()
        self.teach_frame_container.pack_forget()
        self.question_label.config(text="Piensa en un personaje de The Office 😏")
        self.set_buttons_to_answer_mode()
        self.next_question()

    def next_question(self):
        if not self.remaining_chars:
            self.show_message("No estoy seguro de quién podría ser 😔")
            self.show_teach_option()
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
                c for c in self.remaining_chars if (self.feature in c.get(category, [])) or (self.feature == c.get(category))
            ]
        else:
            self.remaining_chars = [
                c for c in self.remaining_chars if not ((self.feature in c.get(category, [])) or (self.feature == c.get(category)))
            ]
        self.asked_features.add(self.feature)
        self.next_question()

    def guess_character(self, character):
        name = character["nombre"]
        self.current_guess = character
        self.question_label.config(text="Creo que estás pensando en...")
        self.show_image(name)
        self.result_label.config(text=f"🕵️‍♂️ {name}")
        self.set_buttons_to_confirm_mode()

    # ----------------- Confirmaciones -----------------
    def confirm_yes(self):
        self.question_label.config(text="¡Genial! Sabía que lo adivinaría 😏")
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")
        self.show_restart_button()

    def confirm_no(self):
        self.open_teach_panel()

    # ----------------- Enseñanza -----------------
    def open_teach_panel(self):
        self.ui_mode = "teaching"
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")
        self.restart_btn.pack_forget()
        self.teach_btn.pack_forget()

        for key in self.teach_entries:
            self.teach_entries[key].delete(0, tk.END)

        self.question_label.config(text="Enséñame al personaje completando los campos 👇")
        # mostrar el contenedor y dentro su canvas con scrollbar
        self.teach_frame_container.pack(pady=12, fill="x")
        # Forzamos que el teach_canvas tenga el ancho del main canvas
        self.teach_canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def save_new_character(self):
        nombre = self.teach_entries["nombre"].get().strip()
        if not nombre:
            self.question_label.config(text="El nombre es obligatorio.")
            return
        if any(c['nombre'].lower() == nombre.lower() for c in self.characters):
            self.question_label.config(text="Ya conozco a ese personaje.")
            self.teach_frame_container.pack_forget()
            self.show_restart_button()
            return

        nuevo = {
            "nombre": nombre,
            "rol": self.teach_entries["rol"].get().strip(),
            "genero": self.teach_entries["genero"].get().strip(),
            "aspecto": [x.strip() for x in self.teach_entries["aspecto"].get().split(",") if x.strip()],
            "personalidad": [x.strip() for x in self.teach_entries["personalidad"].get().split(",") if x.strip()],
            "narrativa": self.teach_entries["narrativa"].get().strip(),
            "estilo": [x.strip() for x in self.teach_entries["estilo"].get().split(",") if x.strip()],
            "distintivo": [x.strip() for x in self.teach_entries["distintivo"].get().split(",") if x.strip()]
        }

        self.characters.append(nuevo)
        save_knowledge(self.characters)
        self.question_label.config(text=f"✅ Aprendí sobre {nombre}. ¡Gracias!")
        self.show_image(nombre)
        self.result_label.config(text=f"🕵️‍♂️ {nombre}")
        self.teach_frame_container.pack_forget()
        self.show_restart_button()

    def cancel_teach(self):
        self.teach_frame_container.pack_forget()
        self.question_label.config(text="Enseñanza cancelada.")
        self.show_restart_button()

    # ----------------- UI auxiliares -----------------
    def show_image(self, name):
        # buscar jpg o png
        img_path = None
        for ext in ("jpg", "png"):
            p = os.path.join("images", f"{name}.{ext}")
            if os.path.exists(p):
                img_path = p
                break

        if img_path:
            try:
                img = Image.open(img_path).resize((260, 340))
                self.char_img = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.char_img, text="")
            except Exception:
                self.image_label.config(image="", text="(Error cargando imagen)", fg="white")
        else:
            self.image_label.config(image="", text="(Imagen no disponible)", fg="white")

    def show_message(self, text):
        self.question_label.config(text=text)
        self.image_label.config(image="", text="")
        self.result_label.config(text="")

    def show_restart_button(self):
        self.restart_btn.pack(pady=10)
        self.yes_btn.config(state="disabled")
        self.no_btn.config(state="disabled")
        self.ui_mode = "idle"

    def show_teach_option(self):
        self.teach_btn.pack(pady=8)
        self.show_restart_button()

# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    app = TheOfficeUI(root)
    root.mainloop()
