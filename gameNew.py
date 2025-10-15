import pygame
import heapq
import maze
from fuzzy_battery import decide_goal
import numpy as np

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
pygame.display.toggle_fullscreen()

screen_w, screen_h = screen.get_size()
clock = pygame.time.Clock()
running = True
font = pygame.font.SysFont("Arial", 24)

tile_size = 60
move_speed = 3

maze_obj = maze.Maze(20, 20, obstacle_prob=0.02, seed=np.random.randint(1000), ensure_path=True)
maze_map = maze_obj.grid

colors = {
    "█": (0, 0, 0),
    ".": (255, 255, 255),
    "#": (255, 0, 0),
    "S": (0, 200, 0),
    "E": (200, 0, 0),
    "?": (200, 200, 200)
}

start, end = None, None
chargers = []
for y, row in enumerate(maze_map):
    for x, cell in enumerate(row):
        if cell == "S":
            start = (x, y)
        elif cell == "E":
            end = (x, y)
        elif cell == "#":
            chargers.append((x, y))

known_map = [["?" for _ in row] for row in maze_map]
known_map[start[1]][start[0]] = "S"
for cx, cy in chargers:
    known_map[cy][cx] = "#"

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def neighbors(pos, known_map):
    x, y = pos
    steps = [(1,0), (-1,0), (0,1), (0,-1)]
    result = []
    for dx, dy in steps:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(known_map) and 0 <= nx < len(known_map[0]):
            if known_map[ny][nx] != "█":
                result.append((nx, ny))
    return result

def astar(start, goal, known_map):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for n in neighbors(current, known_map):
            tentative_g = g_score[current] + 1
            if n not in g_score or tentative_g < g_score[n]:
                came_from[n] = current
                g_score[n] = tentative_g
                f_score[n] = tentative_g + heuristic(n, goal)
                heapq.heappush(open_set, (f_score[n], n))
    return None

def sense_environment(real_map, known_map, pos):
    x, y = pos
    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(real_map) and 0 <= nx < len(real_map[0]):
            known_map[ny][nx] = real_map[ny][nx]
            
def reset_game():
    global maze_map, known_map, start, end, chargers
    global player_tile, player_pos, path, current_tile_index
    global battery_level, is_charging, goal_type, target_goal

    maze_obj = maze.Maze(20, 20, obstacle_prob=0.02, seed=np.random.randint(1000), ensure_path=True)
    maze_map = maze_obj.grid

    start, end = None, None
    chargers = []
    for y, row in enumerate(maze_map):
        for x, cell in enumerate(row):
            if cell == "S":
                start = (x, y)
            elif cell == "E":
                end = (x, y)
            elif cell == "#":
                chargers.append((x, y))

    known_map = [["?" for _ in row] for row in maze_map]
    known_map[start[1]][start[0]] = "S"
    for cx, cy in chargers:
        known_map[cy][cx] = "#"

    player_tile = start
    player_pos = pygame.Vector2((start[0] + 0.5) * tile_size, (start[1] + 0.5) * tile_size)
    path = []
    current_tile_index = 0

    battery_level = 100.0
    is_charging = False
    goal_type = "end"
    target_goal = end

path = []
current_tile_index = 0
player_tile = start
player_pos = pygame.Vector2((start[0] + 0.5) * tile_size, (start[1] + 0.5) * tile_size)
robot_surf = pygame.Surface((tile_size * 0.4, tile_size * 0.4), pygame.SRCALPHA)
robot_surf.fill((0, 0, 255))

battery_level = 100.0
battery_drain_rate = 0.05
battery_drain_move = 0.2
battery_charge_rate = 0.6
is_charging = False
charging_target = None
goal_type = "end"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    px, py = player_tile
    
    if player_tile == end:
        reset_game()
        continue

    if is_charging:
        battery_level = min(100.0, battery_level + battery_charge_rate)
        if battery_level >= 100.0:
            is_charging = False
            charging_target = None
    else:
        battery_level = max(0.0, battery_level - battery_drain_rate)
        distances = [abs(px - cx) + abs(py - cy) for (cx, cy) in chargers] if chargers else [999]
        closest_dist = min(distances)
        distance_to_end = min(20, abs(px - end[0]) + abs(py - end[1]))
        try:
            goal_type = decide_goal(battery_level, closest_dist, distance_to_end)
        except Exception as e:
            goal_type = "recharge"
        target_goal = end if goal_type == "end" else min(chargers, key=lambda c: abs(px - c[0]) + abs(py - c[1]))

        if not path or target_goal != (path[-1] if path else None):
            path = astar(player_tile, target_goal, known_map)
            current_tile_index = 0

    if not is_charging and path and current_tile_index < len(path) - 1:
        next_tile = path[current_tile_index + 1]
        nx, ny = next_tile

        if maze_map[ny][nx] == "█":
            known_map[ny][nx] = "█"
            path = astar(player_tile, target_goal, known_map)
            current_tile_index = 0
        else:
            target_pos = pygame.Vector2((nx + 0.5) * tile_size, (ny + 0.5) * tile_size)
            direction = (target_pos - player_pos)
            distance = direction.length()

            if distance > 0:
                direction = direction.normalize()
                player_pos += direction * move_speed

            if distance < move_speed:
                player_pos = target_pos
                player_tile = next_tile
                current_tile_index += 1
                battery_level = max(0.0, battery_level - battery_drain_move)
                sense_environment(maze_map, known_map, player_tile)

                if goal_type == "recharge" and player_tile in chargers:
                    is_charging = True
                    charging_target = player_tile
                    path = None
                    current_tile_index = 0

    camera_offset = pygame.Vector2(
        player_pos.x - screen_w / 2,
        player_pos.y - screen_h / 2
    )
    map_width = len(maze_map[0]) * tile_size
    map_height = len(maze_map) * tile_size
    camera_offset.x = max(0, min(camera_offset.x, map_width - screen_w))
    camera_offset.y = max(0, min(camera_offset.y, map_height - screen_h))

    screen.fill("white")
    for y, row in enumerate(known_map):
        for x, cell in enumerate(row):
            color = colors.get(cell, (200, 200, 200))
            rect = pygame.Rect(x * tile_size - camera_offset.x, y * tile_size - camera_offset.y, tile_size, tile_size)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 1)

    if path:
        for (x, y) in path:
            pygame.draw.rect(screen, (0, 0, 255),
                             pygame.Rect(x * tile_size - camera_offset.x + tile_size * 0.25,
                                         y * tile_size - camera_offset.y + tile_size * 0.25,
                                         tile_size * 0.5, tile_size * 0.5), 2)

    rect = robot_surf.get_rect(center=(player_pos.x - camera_offset.x, player_pos.y - camera_offset.y))
    screen.blit(robot_surf, rect)

    pygame.draw.rect(screen, (50, 50, 50), (50, 50, 200, 25))
    pygame.draw.rect(screen, (0, 255, 0), (50, 50, 2 * battery_level, 25))
    pygame.draw.rect(screen, (0, 0, 0), (50, 50, 200, 25), 2)

    status = "Modo: " + ("Carregando" if is_charging else ("Buscando Saída" if goal_type == "end" else "Buscando Carregador"))
    text = font.render(f"{status} | Bateria: {battery_level:.1f}%", True, (0, 0, 0))
    screen.blit(text, (50, 90))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
