"""
Diagrama de flujo (resumen)

Inicio
  -> Pantalla título (Iniciar investigación)
    -> Generar combinación secreta (culpable, ingrediente, lugar)
    -> Generar pistas iniciales (historias textuales coherentes)
    -> Pantalla de investigación (mostrar pista actual y botones "Siguiente pista" y "Hacer acusación")
      -> Siguiente pista: muestra otra pista (hasta límite)
      -> Hacer acusación -> Pantalla de acusación
         -> Seleccionar sospechoso, ingrediente y lugar (botones para ciclar opciones)
         -> Confirmar
            -> Si es correcto: mostrar FINAL correspondiente al culpable (1 de 5 finales)
            -> Si es incorrecto: mostrar mensaje de fallo + añadir pista nueva y volver a investigación
  -> Botón "Jugar de nuevo" reinicia todo

Notas de diseño:
- Estilo caricaturesco: gráficos simples dibujados con rectángulos, íconos de texto y sprites generados en tiempo de ejecución.
- Tonalidad: drama de competencia culinaria, texto en español con humor sutil.
- Sólo 5 finales (uno asignado por culpable). Al ganar, la narrativa final incluirá el ingrediente y la locación usados.

Requisitos:
- Python 3.8+
- pygame (pip install pygame)

Ejecución: python Clue_Restaurante_Prototype.py

"""

import pygame
import random
import sys

# --- Configuración ---
pygame.init()
WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Clue: ¿Quién arruinó el platillo?')
FONT = pygame.font.SysFont('arial', 20)
TITLE_FONT = pygame.font.SysFont('arial', 36, bold=True)
CLOCK = pygame.time.Clock()

# Datos del juego (en español)
SUSPECTS = ["Chef Camila", "Sous Chef Mateo", "Pastelera Luna", "Mesero Tomás", "Lavaplatos Nico"]
PLACES = ["Cocina principal", "Despensa", "Área de postres", "Comedor principal", "Oficina de la chef"]
INGREDIENTS = ["Sal", "Azúcar", "Ajo", "Pimienta cayena", "Comino"]

# Finales por culpable (plantilla)
FINALS = {
    "Chef Camila": (
        "La Chef Camila, cansada de recibir siempre críticas negativas, intentó darle una lección al crítico "
        "modificando el platillo final. Sin embargo, la presión y el caos de la cocina la traicionaron, y el "
        "plato terminó completamente arruinado. La lección terminó siendo para ella misma: la noche fue un desastre inolvidable."
    ),
    "Sous Chef Mateo": (
        "Mateo, resentido y celoso, vio la oportunidad perfecta para arruinar la reputación de Camila y tomar protagonismo. "
        "Su plan salió mal: la combinación de ingredientes fue un desastre total, dejando al equipo en shock y a él con una amarga lección sobre la ambición."
    ),
    "Pastelera Luna": (
        "Luna, ansiosa por impresionar y demostrar que podía superar al Sous Chef, decidió experimentar con los postres y el plato principal. "
        "El resultado fue un caos dulce y salado que dejó a todos estupefactos. Su ambición fue mayor que su destreza, y la noche quedó marcada por su error."
    ),
    "Mesero Tomás": (
        "Tomás, molesto porque el crítico fue grosero con él en visitas anteriores, decidió vengarse sutilmente durante el servicio. "
        "Al alterar algunos platos y servir con exagerada prisa, generó confusión y pequeños desastres en la cocina y el comedor, causando una escena caótica que nadie olvidará."
    ),
    "Lavaplatos Nico": (
        "Nico, siempre en las sombras, decidió que era el momento de despertar su creatividad culinaria, aunque nunca había cocinado. "
        "Con la intención de dejar su marca, manipuló ingredientes de manera improvisada. El resultado fue un desastre total, pero al menos Nico descubrió que la cocina requiere mucho más que buena intención."
    )
}


# --- Helpers para texto ---
def dibujar_texto_multiline(texto, rect, fuente, color=(0,0,0), linea_spacing=4):
    palabras = texto.split(' ')
    linea = ''
    yy = rect.top + 5
    for palabra in palabras:
        prueba = linea + ' ' + palabra if linea else palabra
        text_surf = fuente.render(prueba, True, color)
        if text_surf.get_width() > rect.width - 10:
            surf = fuente.render(linea, True, color)
            SCREEN.blit(surf, (rect.left + 5, yy))
            yy += fuente.get_height() + linea_spacing
            linea = palabra
        else:
            linea = prueba
    if linea:
        surf = fuente.render(linea, True, color)
        SCREEN.blit(surf, (rect.left + 5, yy))


# --- Botón helper ---
def dibujar_boton(rect, texto, activo=True):
    color = (200, 180, 250) if activo else (180, 180, 180)
    pygame.draw.rect(SCREEN, color, rect, border_radius=8)
    txt = FONT.render(texto, True, (0,0,0))
    SCREEN.blit(txt, (rect.x + 10, rect.y + rect.height//2 - txt.get_height()//2))

# --- Lógica del juego ---

class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.secret_suspect = random.choice(SUSPECTS)
        self.secret_place = random.choice(PLACES)
        self.secret_ingredient = random.choice(INGREDIENTS)
        self.pistas = []
        self.pistas_mostradas = 0
        self.selected = [0, 0, 0]
        self.result_correct = False
        self.scene = 'title'
        self.generate_initial_clues()  # ahora sí funciona

    def generate_initial_clues(self):
        self.pistas = []
        ing = self.secret_ingredient
        if ing == 'Sal':
            self.pistas += [
                'El sabor final tenía un matiz salado demasiado marcado; alguien tocó el sazonador.',
                'Se halló un frasco de sal con huellas en la cocina principal.',
                'El crítico frunció el ceño al probar el primer plato, claramente saturado de sal.',
                'Un recipiente de sal estaba caído cerca de la estación de cocción, con restos en el suelo.'
            ]
        elif ing == 'Azúcar':
            self.pistas += [
                'El plato tenía un regusto dulce imposible en un plato salado.',
                'Se encontraron restos blancos similares a azúcar cerca del área de postres.',
                'Unos granos de azúcar se vieron en la mesa del servicio principal.',
                'El toque dulce arruinó la armonía del plato; alguien añadió azúcar sin permiso.'
            ]
        elif ing == 'Ajo':
            self.pistas += [
                'Un fuerte olor a ajo impregnó la cocina; difícil de enmascarar.',
                'La chef comentó que alguien había olvidado cubrir los dientes de ajo en la despensa.',
                'El aroma a ajo era más fuerte en la zona donde se prepararon las entradas.',
                'Algunos clientes mencionaron un sabor inesperado a ajo en su plato.'
            ]
        elif ing == 'Pimienta cayena':
            self.pistas += [
                'El crítico tosió: algo picante invadió el paladar.',
                'Varios frascos de especias estaban abiertos; la pimienta cayena faltaba un poco.',
                'Se encontraron rastros de pimienta cayena cerca del área de condimentos.',
                'Un ligero enrojecimiento en el paladar del crítico indicó exceso de picante.'
            ]
        elif ing == 'Comino':
            self.pistas += [
                'El aroma era terroso y distintivo; el comino es difícil de disfrazar.',
                'Alguien comentó que el comino estaba fuera de lugar para ese platillo.',
                'Se hallaron restos de comino en utensilios que no correspondían a ese plato.',
                'Un ligero toque terroso fue detectado por el crítico en la degustación.'
            ]

        place = self.secret_place
        if place == 'Cocina principal':
            self.pistas += [
                'Algunos platos salieron directamente de la cocina principal con el problema evidente.',
                'El suelo de la cocina estaba resbaladizo; alguien derramó líquidos durante la preparación.',
                'Se encontraron ingredientes fuera de sus estantes en la cocina principal.'
            ]
        elif place == 'Despensa':
            self.pistas += [
                'La despensa estaba desordenada y un cajón con especias estaba abierto.',
                'Se notaron cajas fuera de lugar, como si alguien buscara algo con prisa.',
                'Un frasco de condimento estaba sobre la mesa en lugar de su lugar habitual.'
            ]
        elif place == 'Área de postres':
            self.pistas += [
                'Una nube de harina aún flotaba en el área de postres.',
                'Se detectó chocolate derramado en la encimera y utensilios desordenados.',
                'Alguien dejó bandejas con crema sin cubrir cerca de los postres.'
            ]
        elif place == 'Comedor principal':
            self.pistas += [
                'Mesas en el comedor reportaron platos con sabor extraño justo al servir.',
                'El servicio fue caótico, con algunos platos servidos fríos o demasiado calientes.',
                'Se notaron manchas de salsa en la alfombra; alguien tropezó al servir.'
            ]
        elif place == "Oficina de la chef":
            self.pistas += [
                'Se oyó una discusión en la oficina de la chef momentos antes del servicio.',
                'Alguien vio papeles de recetas arrugados en la oficina.',
                'La chef revisaba frenéticamente notas, indicando nerviosismo extremo.'
            ]

        suspect = self.secret_suspect
        if suspect == 'Chef Camila':
            self.pistas += [
                'La Chef Camila estuvo ajustando el tiempo de cocción con nervios a la vista.',
                'Sin embargo, alguien vio a Camila salir a hablar con el crítico.',
                'Camila revisaba los ingredientes con gesto preocupado y repetitivo.',
                'Se encontró un delantal con restos de varias preparaciones de la noche.'
            ]
        elif suspect == 'Sous Chef Mateo':
            self.pistas += [
                'Mateo estuvo manipulando las especias con manos temblorosas.',
                'Se oyó que Mateo quería cambiar la receta para impresionar.',
                'Mateo pasó más tiempo del habitual en la despensa, mezclando ingredientes.',
                'Alguien notó que Mateo tomaba notas mientras observaba los platos preparados.'
            ]
        elif suspect == 'Pastelera Luna':
            self.pistas += [
                'Luna estuvo cerca del plato principal un instante; confundió un frasco por accidente.',
                'Su delantal tenía restos dulces.',
                'Se encontraron utensilios mezclados entre postres y platos salados, posiblemente por Luna.',
                'Luna murmuraba correcciones de última hora mientras trabajaba en los postres.'
            ]
        elif suspect == 'Mesero Tomás':
            self.pistas += [
                'Tomás fue visto trasteando con los platos en la ruta al comedor.',
                'Algunos clientes mencionaron que Tomás sirvió con prisa.',
                'Tomás dejó caer un plato y lo reemplazó apresuradamente, generando confusión.',
                'Se vio a Tomás conversando nerviosamente con el personal de cocina.'
            ]
        elif suspect == 'Lavaplatos Nico':
            self.pistas += [
                'Nico, siempre silencioso, fue visto en la sombra observando la cocina.',
                'Alguien notó que Nico había guardado un frasco en un sitio inusual.',
                'Se encontraron utensilios limpios pero mal ubicados, posiblemente por Nico.',
                'Nico desapareció brevemente durante el caos del servicio, sin explicación.'
            ]

        random.shuffle(self.pistas)

    def next_clue(self):
        if self.pistas_mostradas < len(self.pistas):
            self.pistas_mostradas += 1
            return True
        return False

    def get_clues_shown(self):
        return self.pistas[:self.pistas_mostradas]

    def accuse(self, suspect_idx, ingredient_idx, place_idx):
        s = SUSPECTS[suspect_idx]
        i = INGREDIENTS[ingredient_idx]
        p = PLACES[place_idx]
        correct = (s == self.secret_suspect and i == self.secret_ingredient and p == self.secret_place)
        self.result_correct = correct
        return correct, (s, i, p)


# --- Instancia de juego ---
state = GameState()

# --- Funciones de pantalla ---

def screen_title():
    SCREEN.fill((250, 245, 240))
    
    # Título del juego
    title = TITLE_FONT.render('Clue: ¿Quién arruinó el platillo?', True, (60,20,20))
    SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 40))
    
    # Subtítulo
    subtitle = FONT.render('Un misterio culinario', True, (80,80,80))
    SCREEN.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 90))
    
    # Relato introductorio
    intro_text = (
        "Es una noche caótica en el restaurante 'Rosée', donde la famosa chef Camila dirige "
        "su brigada de cocina con mano firme. Hoy, el crítico gastronómico más importante del país hará su visita, "
        "y cada plato cuenta. Entre pedidos desbordados, ingredientes fuera de lugar y utensilios por el aire, "
        "la cocina se ha convertido en un campo de batalla. Los empleados luchan por reconocimiento, "
        "algunos buscan impresionar, otros aprovechan para sabotear discretamente el servicio. "
        "Nadie sabe quién realmente está detrás del desastre que amenaza arruinar la reputación del restaurante. "
        "Tu misión: investigar, recopilar pistas y descubrir quién, con qué ingrediente y en qué lugar, ha causado el caos."
    )
    dibujar_texto_multiline(intro_text, pygame.Rect(50, 130, WIDTH - 100, 220), FONT, color=(40,40,60), linea_spacing=6)
    
    # Botones de inicio e instrucciones
    start_rect = pygame.Rect(WIDTH//2 - 120, 370, 240, 50)
    instrucciones_rect = pygame.Rect(WIDTH//2 - 200, 440, 400, 40)
    dibujar_boton(start_rect, 'Iniciar investigación')
    dibujar_boton(instrucciones_rect, 'Cómo jugar: Recoge pistas y acusa correctamente')
    
    
    return start_rect



def screen_investigate():
    SCREEN.fill((245, 250, 250))
    header = TITLE_FONT.render('Investigación', True, (40,40,60))
    SCREEN.blit(header, (30, 20))

    # cuadro de texto para pistas a la izquierda
    clue_rect = pygame.Rect(30, 70, 460, 520)
    pygame.draw.rect(SCREEN, (230, 230, 240), clue_rect, border_radius=10)
    pygame.draw.rect(SCREEN, (0,0,0), clue_rect, 2, border_radius=10)
    clues = state.get_clues_shown()
    clue_area = pygame.Rect(clue_rect.left + 5, clue_rect.top + 5, clue_rect.width - 10, clue_rect.height - 10)
    y_offset = 0
    for c in clues:
        dibujar_texto_multiline('- ' + c, pygame.Rect(clue_area.left, clue_area.top + y_offset, clue_area.width, clue_area.height), FONT)
        y_offset += 60  # más espacio entre pistas

    # panel derecho con estado actual
    state_rect = pygame.Rect(500, 70, 460, 520)
    pygame.draw.rect(SCREEN, (235,235,245), state_rect, border_radius=10)
    pygame.draw.rect(SCREEN, (0,0,0), state_rect, 2, border_radius=10)
    dibujar_texto_multiline('Estado actual:', pygame.Rect(state_rect.left+10, state_rect.top+10, state_rect.width-20, state_rect.height), FONT)

    s_text = FONT.render('Sospechoso: ' + SUSPECTS[state.selected[0]], True, (0,0,0))
    i_text = FONT.render('Ingrediente: ' + INGREDIENTS[state.selected[1]], True, (0,0,0))
    p_text = FONT.render('Lugar: ' + PLACES[state.selected[2]], True, (0,0,0))
    SCREEN.blit(s_text, (state_rect.left + 10, state_rect.top + 50))
    SCREEN.blit(i_text, (state_rect.left + 10, state_rect.top + 90))
    SCREEN.blit(p_text, (state_rect.left + 10, state_rect.top + 130))

    # botones de acción
    next_rect = pygame.Rect(500, HEIGHT - 120, 200, 45)
    acusar_rect = pygame.Rect(720, HEIGHT - 120, 200, 45)
    dibujar_boton(next_rect, 'Siguiente pista' if state.pistas_mostradas < len(state.pistas) else 'Sin más pistas')
    dibujar_boton(acusar_rect, 'Hacer acusación')

    # botones para ciclar selecciones alineados con el texto
    s_y = state_rect.top + 50
    i_y = state_rect.top + 90
    p_y = state_rect.top + 130

    s_left = pygame.Rect(state_rect.left + 250, s_y, 30, 30)
    s_right = pygame.Rect(state_rect.left + 310, s_y, 30, 30)
    i_left = pygame.Rect(state_rect.left + 250, i_y, 30, 30)
    i_right = pygame.Rect(state_rect.left + 310, i_y, 30, 30)
    p_left = pygame.Rect(state_rect.left + 250, p_y, 30, 30)
    p_right = pygame.Rect(state_rect.left + 310, p_y, 30, 30)

    for r in [s_left, s_right, i_left, i_right, p_left, p_right]:
        pygame.draw.rect(SCREEN, (200,200,200), r, border_radius=6)

    SCREEN.blit(FONT.render('<', True, (0,0,0)), (s_left.x+8, s_left.y+4))
    SCREEN.blit(FONT.render('>', True, (0,0,0)), (s_right.x+6, s_right.y+4))
    SCREEN.blit(FONT.render('<', True, (0,0,0)), (i_left.x+8, i_left.y+4))
    SCREEN.blit(FONT.render('>', True, (0,0,0)), (i_right.x+6, i_right.y+4))
    SCREEN.blit(FONT.render('<', True, (0,0,0)), (p_left.x+8, p_left.y+4))
    SCREEN.blit(FONT.render('>', True, (0,0,0)), (p_right.x+6, p_right.y+4))

    return next_rect, acusar_rect, (s_left, s_right, i_left, i_right, p_left, p_right)






def screen_accuse():
    SCREEN.fill((255, 250, 240))
    header = TITLE_FONT.render('Acusar - Elige tu combinación', True, (50,20,20))
    SCREEN.blit(header, (30, 20))

    dibujar_texto_multiline('Selecciona un sospechoso, un ingrediente y un lugar. Luego confirma tu acusación.', pygame.Rect(30,80,920,100), FONT)

    s_big = TITLE_FONT.render(SUSPECTS[state.selected[0]], True, (0,0,0))
    i_big = FONT.render('Ingrediente: ' + INGREDIENTS[state.selected[1]], True, (0,0,0))
    p_big = FONT.render('Lugar: ' + PLACES[state.selected[2]], True, (0,0,0))
    SCREEN.blit(s_big, (30, 150))
    SCREEN.blit(i_big, (30, 220))
    SCREEN.blit(p_big, (30, 260))

    confirm_rect = pygame.Rect(30, HEIGHT - 120, 200, 45)
    back_rect = pygame.Rect(260, HEIGHT - 120, 200, 45)
    dibujar_boton(confirm_rect, 'Confirmar acusación')
    dibujar_boton(back_rect, 'Volver')

    return confirm_rect, back_rect

def screen_result(correct, guess):
    SCREEN.fill((245, 245, 250))
    s, i, p = guess
    if correct:
        header = TITLE_FONT.render('¡Acertaste!', True, (20,120,20))
        SCREEN.blit(header, (30, 30))
        # Crear rectángulos para dibujar texto multilinea
        final_rect = pygame.Rect(30, 100, 920, 100)
        detalle_rect = pygame.Rect(30, 220, 920, 50)
        final_text = FINALS[s]
        detalle = f"En realidad, {s} usó {i} en {p}."
        dibujar_texto_multiline(final_text, final_rect, FONT)
        dibujar_texto_multiline(detalle, detalle_rect, FONT)
        play_again = pygame.Rect(30, HEIGHT - 120, 240, 45)
        dibujar_boton(play_again, 'Jugar de nuevo')
        return play_again
    else:
        header = TITLE_FONT.render('No es correcto', True, (140,20,20))
        SCREEN.blit(header, (30, 30))
        fail_text = f"La combinación ({s} - {i} - {p}) no es la correcta. Se añade una pista más a la investigación."
        fail_rect = pygame.Rect(30, 100, 920, 100)
        dibujar_texto_multiline(fail_text, fail_rect, FONT)
        seguir = pygame.Rect(30, HEIGHT - 120, 240, 45)
        dibujar_boton(seguir, 'Seguir investigando')
        return seguir




def boton_click(rect, evento):
    if rect is None or evento is None:
        return False
    if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
        if rect.collidepoint(evento.pos):
            return True
    return False

# --- Bucle principal ---

def main_loop():
    running = True

    while running:
        CLOCK.tick(30)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False

            # --- ESCENA TÍTULO ---
            if state.scene == 'title':
                start_rect = screen_title()
                if boton_click(start_rect, evento):
                    state.scene = 'investigate'

            # --- ESCENA INVESTIGACIÓN ---
            elif state.scene == 'investigate':
                nxt_rect, acc_rect, cycles = screen_investigate()
                s_left, s_right, i_left, i_right, p_left, p_right = cycles

                # Botones de pista y acusación
                if boton_click(nxt_rect, evento):
                    if not state.next_clue():
                        state.pistas.append('No se hallaron huellas claras en el área; el servicio fue un caos.')
                if boton_click(acc_rect, evento):
                    state.scene = 'accuse'

                # Ciclar selección de sospechoso, ingrediente y lugar
                if boton_click(s_left, evento):
                    state.selected[0] = (state.selected[0] - 1) % len(SUSPECTS)
                if boton_click(s_right, evento):
                    state.selected[0] = (state.selected[0] + 1) % len(SUSPECTS)
                if boton_click(i_left, evento):
                    state.selected[1] = (state.selected[1] - 1) % len(INGREDIENTS)
                if boton_click(i_right, evento):
                    state.selected[1] = (state.selected[1] + 1) % len(INGREDIENTS)
                if boton_click(p_left, evento):
                    state.selected[2] = (state.selected[2] - 1) % len(PLACES)
                if boton_click(p_right, evento):
                    state.selected[2] = (state.selected[2] + 1) % len(PLACES)

            # --- ESCENA ACUSAR ---
            elif state.scene == 'accuse':
                confirm_rect, back_rect = screen_accuse()

                # Confirmar acusación
                if boton_click(confirm_rect, evento):
                    correct, guess = state.accuse(state.selected[0], state.selected[1], state.selected[2])
                    if not correct:
                        extra = generar_pista_extra(state, guess)
                        state.pistas.append(extra)
                    state.scene = 'result'  # Ir a pantalla de resultado

                # Volver a investigar
                if boton_click(back_rect, evento):
                    state.scene = 'investigate'

            # --- ESCENA RESULTADO ---
            elif state.scene == 'result':
                button = screen_result(state.result_correct, (SUSPECTS[state.selected[0]],
                                                              INGREDIENTS[state.selected[1]],
                                                              PLACES[state.selected[2]]))
                if boton_click(button, evento):
                    if state.result_correct:
                        state.reset()  # reinicia juego
                    state.scene = 'investigate'  # volver a investigación

        # --- Redibujar según escena ---
        if state.scene == 'title':
            screen_title()
        elif state.scene == 'investigate':
            screen_investigate()
        elif state.scene == 'accuse':
            screen_accuse()
        elif state.scene == 'result':
            screen_result(state.result_correct, (SUSPECTS[state.selected[0]],
                                                 INGREDIENTS[state.selected[1]],
                                                 PLACES[state.selected[2]]))

        pygame.display.flip()

    pygame.quit()
    sys.exit()




def generar_pista_extra(state, guess):
    # Genera una pista adicional tras acusación fallida para orientar al jugador.
    s, i, p = guess
    opciones = []
    # si el ingrediente es distinto al secreto, dar pista que lo exculpa o lo implica
    if i != state.secret_ingredient:
        opciones.append(f'Las pruebas no muestran evidencia suficiente de {i}; el aroma apunta a otra cosa.')
    else:
        opciones.append(f'El análisis confirma rastros de {i} alrededor del punto de preparación.')

    if s != state.secret_suspect:
        opciones.append(f'Una cámara captó a alguien distinto de {s} realizando movimientos sospechosos.')
    else:
        opciones.append(f'Una declaración reciente fortalece la sospecha contra {s}.')

    if p != state.secret_place:
        opciones.append(f'La ubicación reportada por testigos sugiere que el incidente no ocurrió en {p}.')
    else:
        opciones.append(f'Las huellas y olores conducen de nuevo a {p}.')

    return random.choice(opciones)

if __name__ == '__main__':
    main_loop()
