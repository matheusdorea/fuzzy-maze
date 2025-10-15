import random
import numpy as np
from collections import deque
import sys
import os
from aStar import AStar

# Add aStar directory to path
# sys.path.append(os.path.join(os.path.dirname(__file__), 'aStar'))
# from aStar import AStar

class Maze:
    def __init__(self, rows, cols, obstacle_prob=0.2, seed=None, ensure_path=True):
        self.rows = rows
        self.cols = cols
        self.seed = seed
        self.ensure_path = ensure_path
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        self.FREE = '.'      # Espaço livre
        self.OBSTACLE = '#'  # Obstáculo
        self.WALL = '█'      # Parede
        self.START = 'S'     # Início
        self.END = 'E'       # Fim
        
        self.grid = np.full((rows, cols), self.FREE, dtype=str)
        self.start = (0, 0)
        self.end = (rows - 1, cols - 1)
        
        self.generate(obstacle_prob)

    def generate(self, obstacle_prob=0.2):
        """Gera labirinto garantindo que sempre existe um caminho"""
        if self.seed is not None:
            random.seed(self.seed)
        
        self.generate_obstacles(obstacle_prob)
        
        self.add_strategic_walls()
        
        self.grid[self.start[0]][self.start[1]] = self.START
        self.grid[self.end[0]][self.end[1]] = self.END
        
        if self.ensure_path:
            self.ensure_connectivity()
        
        return self.grid
    
    def generate_obstacles(self, obstacle_prob):
        """Gera obstáculos aleatórios evitando start e end"""
        for i in range(self.rows):
            for j in range(self.cols):
                # Não coloca obstáculo no start ou end
                if (i, j) == self.start or (i, j) == self.end:
                    continue
                if random.random() < obstacle_prob:
                    self.grid[i][j] = self.OBSTACLE

    
    def add_strategic_walls(self):
        """Adiciona paredes estratégicas sem bloquear completamente"""

        for j in range(0, self.cols, 3):  # A cada 3 posições
            if j < self.cols and (0, j) != self.start:
                self.grid[0][j] = self.WALL
        
        for j in range(1, self.cols, 3): 
            if j < self.cols and (self.rows-1, j) != self.end:
                self.grid[self.rows-1][j] = self.WALL
        
        for i in range(0, self.rows, 2):
            if i < self.rows and (i, 0) != self.start:
                self.grid[i][0] = self.WALL
            if i < self.rows and (i, self.cols-1) != self.end:
                self.grid[i][self.cols-1] = self.WALL
        
        wall_count = max(1, (self.rows * self.cols) // 20)
        for _ in range(wall_count):
            row = random.randint(1, self.rows-2)
            col = random.randint(1, self.cols-2)
            if (row, col) != self.start and (row, col) != self.end:
                self.grid[row][col] = self.WALL
    
    def is_valid_pos(self, row, col):
        """Verifica se a posição é válida - apenas paredes bloqueiam, obstáculos são transitáveis"""
        return (0 <= row < self.rows and 0 <= col < self.cols and 
                self.grid[row][col] != self.WALL)
    
    def ensure_connectivity(self):
        """Verifica conectividade - obstáculos são transitáveis, apenas paredes bloqueiam"""
        # BFS considerando que obstáculos são transitáveis (custo maior)
        visited = set()
        queue = deque([self.start])
        visited.add(self.start)
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while queue:
            row, col = queue.popleft()
            
            # Se chegou ao destino, há caminho
            if (row, col) == self.end:
                return True
            
            # Explora vizinhos - obstáculos são permitidos, apenas paredes bloqueiam
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                
                if ((new_row, new_col) not in visited and 
                    self.is_valid_pos(new_row, new_col)):
                    visited.add((new_row, new_col))
                    queue.append((new_row, new_col))
        
        # Se não encontrou caminho, é porque há paredes bloqueando
        print("🔧 Caminho bloqueado por paredes, criando abertura...")
        self._create_guaranteed_path()
        return True
    
    def _create_guaranteed_path(self):
        """Cria um caminho garantido removendo apenas paredes (obstáculos são transitáveis)"""
        # Remove apenas paredes para garantir conectividade (obstáculos podem ser atravessados)
        current_row, current_col = self.start
        target_row, target_col = self.end
        
        # Movimento horizontal primeiro
        while current_col != target_col:
            if current_col < target_col:
                current_col += 1
            else:
                current_col -= 1
            
            # Remove apenas paredes (obstáculos são mantidos pois são transitáveis)
            if self.grid[current_row][current_col] in [self.WALL]:
                self.grid[current_row][current_col] = self.FREE
        
        # Movimento vertical depois
        while current_row != target_row:
            if current_row < target_row:
                current_row += 1
            else:
                current_row -= 1
            
            # Remove apenas paredes (obstáculos são mantidos pois são transitáveis)
            if self.grid[current_row][current_col] in [self.WALL]:
                self.grid[current_row][current_col] = self.FREE
        
        # Garante que start e end estão corretos
        self.grid[self.start[0]][self.start[1]] = self.START
        self.grid[self.end[0]][self.end[1]] = self.END
    
    def display(self):
        """Exibe o labirinto de forma legível"""
        for row in self.grid:
            print(' '.join(row))
        print()
    
    def calculate_cost_with_astar(self):
        """Calcula o custo do caminho usando A* considerando obstáculos como transitáveis com custo maior"""
        astar = AStar(self)
        found, path, cost, explored = astar.search()
        if found:
            print(f"✅ Caminho encontrado! Passos: {len(path)}, Custo total: {cost}, Nós explorados: {explored}")
            astar.visualize_path_with_costs(path)
            return path, cost
        else:
            print("Nenhum caminho encontrado")
            return [], float('inf')
    
maze = Maze(10, 10, obstacle_prob=0.3, seed=76, ensure_path=True)
maze.display()

maze.calculate_cost_with_astar()
