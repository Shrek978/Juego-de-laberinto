import pygame
import random
import heapq
import cv2
import numpy as np



# Configuración del laberinto
tamano_cuadro = 20
ancho = 68
alto = 38
anchura, altura = ancho * tamano_cuadro, alto * tamano_cuadro
inicio = (1, 1)

def encontrar_salida(laberinto):
    for y in range(alto - 2, 0, -1):
        for x in range(ancho - 2, 0, -1):
            if laberinto[y][x] == 0:
                return x, y
    return ancho - 2, alto - 2

# Inicializar Pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Pantalla completa
anchura, altura = screen.get_size()  # Ajustar dimensiones a la pantalla
clock = pygame.time.Clock()

# Reproducir música de fondo
pygame.mixer.init()
pygame.mixer.music.load("background.mp3")  # Cargar el archivo MP3
pygame.mixer.music.play(-1)  # Reproducir en bucle infinito

# Cargar efecto de sonido para recoger frutas
fruit_sound = pygame.mixer.Sound("fruit_sound.mp3")

# Cargar imágenes
pared = pygame.image.load("wall.png")
pared = pygame.transform.scale(pared, (tamano_cuadro, tamano_cuadro))
camino = pygame.image.load("path.png")
camino = pygame.transform.scale(camino, (tamano_cuadro, tamano_cuadro))
jugador = pygame.image.load("player.png")
jugador = pygame.transform.scale(jugador, (tamano_cuadro, tamano_cuadro))
salida = pygame.image.load("exit.png")
salida = pygame.transform.scale(salida, (tamano_cuadro, tamano_cuadro))
solucion = pygame.image.load("solution.png")
solucion = pygame.transform.scale(solucion, (tamano_cuadro, tamano_cuadro))

# Cargar frutas
fotos_frutas = [
    pygame.image.load("fruit1.png"),
    pygame.image.load("fruit2.png"),
    pygame.image.load("fruit3.png"),
    pygame.image.load("fruit4.png"),
    pygame.image.load("fruit5.png"),
    pygame.image.load("fruit6.png")
]
fotos_frutas = [pygame.transform.scale(img, (tamano_cuadro, tamano_cuadro)) for img in fotos_frutas]

def reproducir_video(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        frame = pygame.transform.scale(frame, (anchura, altura))
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        if pygame.event.get(pygame.QUIT):
            cap.release()
            pygame.quit()
            return
    cap.release()

def generar_mazmorra():
    grid = [[1 for _ in range(ancho)] for _ in range(alto)]
    stack = [(inicio[0], inicio[1])]
    grid[inicio[1]][inicio[0]] = 0

    while stack:
        x, y = stack[-1]
        neighbors = [(x + dx, y + dy) for dx, dy in [(0, 2), (2, 0), (-2, 0), (0, -2)]
                      if 0 < x + dx < ancho-1 and 0 < y + dy < alto-1 and grid[y + dy][x + dx] == 1]

        if neighbors:
            nx, ny = random.choice(neighbors)
            grid[(ny + y) // 2][(nx + x) // 2] = 0
            grid[ny][nx] = 0
            stack.append((nx, ny))
        else:
            stack.pop()

    return grid

def Aasterisco(laberinto, inicio, final):
    open_list = [(0, inicio)]
    came_from = {}
    g_score = {inicio: 0}
    f_score = {inicio: abs(inicio[0] - final[0]) + abs(inicio[1] - final[1])}

    while open_list:
        _, current = heapq.heappop(open_list)
        if current == final:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < ancho and 0 <= neighbor[1] < alto and laberinto[neighbor[1]][neighbor[0]] == 0:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + abs(neighbor[0] - final[0]) + abs(neighbor[1] - final[1])
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))
    return []

def dibujar_laberinto(laberinto, path=None, frutas=None, abrir_salida=False):
    screen.fill((0, 0, 0))
    for y in range(alto):
        for x in range(ancho):
            if laberinto[y][x] == 1:
                screen.blit(pared, (x * tamano_cuadro, y * tamano_cuadro))
            else:
                screen.blit(camino, (x * tamano_cuadro, y * tamano_cuadro))
    if path:
        for x, y in path:
            screen.blit(solucion, (x * tamano_cuadro, y * tamano_cuadro))
    if frutas:
        for fx, fy, una_fruta in frutas:
            screen.blit(una_fruta, (fx * tamano_cuadro, fy * tamano_cuadro))
    if abrir_salida:
        screen.blit(salida, (final[0] * tamano_cuadro, final[1] * tamano_cuadro))

def generar_frutas(laberinto, numero_frutas=4):
    frutas = []
    while len(frutas) < numero_frutas:
        fx = random.randint(1, ancho - 2)
        fy = random.randint(1, alto - 2)
        if laberinto[fy][fx] == 0 and (fx, fy) != inicio and (fx, fy) != final and (fx, fy) not in [(f[0], f[1]) for f in frutas]:
            # Asignar fruta de la lista de imágenes de forma secuencial
            frutas.append((fx, fy, fotos_frutas[len(frutas) % len(fotos_frutas)]))
    return frutas


laberinto = generar_mazmorra()
global final
final = encontrar_salida(laberinto)
frutas = generar_frutas(laberinto)
frutas_requeridas = len(frutas)
coordenada_x, coordenada_y = inicio[0] * tamano_cuadro, inicio[1] * tamano_cuadro
velocidad = 2
keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False}
mostrar_solucion = False
solution_path = []
frutas_recogidas = 0
    
ejecutando = True
while ejecutando:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False
        if event.type == pygame.KEYDOWN:
            if event.key in keys:
                keys[event.key] = True
            if event.key == pygame.K_SPACE:
                mostrar_solucion = not mostrar_solucion
                if mostrar_solucion:
                    solution_path = Aasterisco(laberinto, ((coordenada_x + tamano_cuadro // 2) // tamano_cuadro, (coordenada_y + tamano_cuadro // 2) // tamano_cuadro), final)
                else:
                    solution_path = []
        if event.type == pygame.KEYUP:
            if event.key in keys:
                keys[event.key] = False
        
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]:
        dx = -velocidad
    if keys[pygame.K_RIGHT]:
        dx = velocidad
    if keys[pygame.K_UP]:
        dy = -velocidad
    if keys[pygame.K_DOWN]:
        dy = velocidad
        
    new_x, new_y = coordenada_x + dx, coordenada_y + dy
    tile_x = (new_x + tamano_cuadro // 2) // tamano_cuadro
    tile_y = (new_y + tamano_cuadro // 2) // tamano_cuadro
        
    if 0 <= tile_x < ancho and 0 <= tile_y < alto and laberinto[tile_y][tile_x] == 0:
        coordenada_x, coordenada_y = new_x, new_y
        
        # Se ejecuta cuando el jugador toma una fruta
    for fx, fy, una_fruta in frutas[:]:
        if ((coordenada_x + tamano_cuadro // 2) // tamano_cuadro, (coordenada_y + tamano_cuadro // 2) // tamano_cuadro) == (fx, fy):
            frutas.remove((fx, fy, una_fruta))
            frutas_recogidas += 1
            fruit_sound.play()  
        
        # Comprobar si se recogieron todas las frutas
    abrir_salida = (frutas_recogidas == frutas_requeridas)
        
        # Ocurre al ganar
    if abrir_salida and ((coordenada_x + tamano_cuadro // 2) // tamano_cuadro, (coordenada_y + tamano_cuadro // 2) // tamano_cuadro) == final:
        reproducir_video("win_video.mp4")
        break
        
    dibujar_laberinto(laberinto, solution_path if mostrar_solucion else None, frutas, abrir_salida)
    screen.blit(jugador, (coordenada_x, coordenada_y))
    pygame.display.flip()

pygame.quit()


