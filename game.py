import pygame
import math
import fuzzy

# === Inicialização do pygame ===
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

degree = 0
speed = 1
rotation_speed = 3

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

robot_size = (60, 40)
robot_surf = pygame.Surface(robot_size, pygame.SRCALPHA)
robot_surf.fill((255, 0, 0))

sensor_angles = [0, -90, 90, -45, 45]  # frente, direita, esquerda, diag direita, diag esquerda
sensor_range = 200

# === Mapa textual ===
map_str = """
S . . █ # . █ . . █
# . # . # . . . . .
█ . # . . # . . # █
. # . # # █ . . . .
█ . . . . . . . █ █
. . # . . █ # . . #
█ . . . # . # # # █
. . . . # . # # █ .
█ █ . . # . . . . █
. █ # . █ # # █ # E
"""

# === Converte para matriz (lista de listas) ===
maze = [row.split() for row in map_str.strip().split("\n")]
tile_size = 100

colors = {
    "█": (0, 0, 0),       # Parede - preto
    ".": (255, 255, 255), # Espaço livre - branco
    "#": (160, 160, 160), # Espaço especial - cinza
    "S": (0, 200, 0),     # Início - verde
    "E": (200, 0, 0)      # Final - vermelho
}

# === Loop principal ===
while running:
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Leitura do teclado
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        degree += rotation_speed
    if keys[pygame.K_d]:
        degree -= rotation_speed

    screen.fill("white")
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            color = colors.get(cell, (255,255,255))  # padrão: branco
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (100,100,100), rect, 1)  # grade leve

    rotated_robot = pygame.transform.rotate(robot_surf, degree)
    rect = rotated_robot.get_rect(center=player_pos)
    screen.blit(rotated_robot, rect)
    
    # === Sensores ===
    sensor_distances = []
    
    for angle_offset in sensor_angles:
        angle = degree + angle_offset
        # Calcula o vetor unitário
        dx = math.cos(math.radians(angle))
        dy = -math.sin(math.radians(angle))  # invertido no pygame
        # Raycasting
        
        distance = sensor_range
        for d in range(sensor_range):
            test_x = int(player_pos.x + dx*d)
            test_y = int(player_pos.y + dy*d)
            # Descobre qual célula o ponto está
            cell_x = test_x // tile_size
            cell_y = test_y // tile_size

            # Verifica se está dentro dos limites do mapa
            if 0 <= cell_y < len(maze) and 0 <= cell_x < len(maze[0]):
                # Se for parede preta, para o raio
                if maze[cell_y][cell_x] == "█":
                    distance = d
                    break
            else:
                # Fora do mapa, para o raio
                distance = d
                break
                
        sensor_distances.append(distance)
                
        # Desenha o sensor
        end_pos = (player_pos.x + dx*distance, player_pos.y + dy*distance)
        pygame.draw.line(screen, (0, 255, 0), player_pos, end_pos, 2)
        # Mostra a distância
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"{distance}", True, (0, 0, 0))
        screen.blit(text, end_pos)
    
    if len(sensor_distances) == 5:
        fuzzy.steering_sim.input['front'] = sensor_distances[0]
        fuzzy.steering_sim.input['right'] = sensor_distances[1]
        fuzzy.steering_sim.input['left'] = sensor_distances[2]
        fuzzy.steering_sim.input['diag_right'] = sensor_distances[3]
        fuzzy.steering_sim.input['diag_left'] = sensor_distances[4]
        try:
            fuzzy.steering_sim.compute()
            steer_angle = fuzzy.steering_sim.output['steering']
        except:
            print("Erro no cálculo fuzzy")
            steer_angle = 0
        print(f"Steer angle: {steer_angle}")
    else:
        steer_angle = 0
            
    degree = round(degree, 2)
    degree += steer_angle
    degree %= 360  # Mantém o ângulo entre 0a-359
    #atualiza a posição
    dx = math.cos(math.radians(degree))
    dy = math.sin(math.radians(degree))
    player_pos.x += dx * speed
    player_pos.y -= dy * speed
    
    # Atualiza a tela
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
