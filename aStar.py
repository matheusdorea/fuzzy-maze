import heapq

class AStar:
    def __init__(self, maze):
        """Inicializa o A* com um objeto maze"""
        self.rows = maze.rows
        self.cols = maze.cols
        self.grid = maze.grid
        self.start = maze.start
        self.end = maze.end
        self.FREE = maze.FREE
        self.OBSTACLE = maze.OBSTACLE
        self.WALL = maze.WALL
        self.START = maze.START 
        self.END = maze.END

    def heuristic(self, pos1, pos2):
        """Calcula a heurística (distância de Manhattan)"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_neighbors(self, node):
        """Retorna os vizinhos válidos de um nó"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # cima, baixo, esquerda, direita
        neighbors = []
        
        for dr, dc in directions:
            new_row, new_col = node[0] + dr, node[1] + dc
            
            # Verifica se está dentro dos limites
            if (0 <= new_row < self.rows and 0 <= new_col < self.cols):
                cell = self.grid[new_row][new_col]
                # Para A* com custos, permite movimento através de obstáculos
                # Apenas paredes são realmente intransponíveis
                if cell != self.WALL:
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def get_movement_cost(self, from_pos, to_pos):
        """
        Calcula o custo de mover de uma posição para outra
        - Espaços livres: custo 1
        - Obstáculos: custo 3 (mais caro, mas possível)
        - Start/End: custo 1
        """
        target_cell = self.grid[to_pos[0]][to_pos[1]]
        
        if target_cell == self.OBSTACLE:
            return 3  # Custo alto para passar por obstáculos
        elif target_cell in [self.FREE, self.START, self.END]:
            return 1  # Custo normal para espaços livres
        else:
            return 1  # Custo padrão para outros casos
        
    def search(self):
        """
        Implementação rigorosa do algoritmo A* seguindo as regras acadêmicas padrão
        Retorna: (caminho_encontrado, caminho, custo_total, nós_explorados)
        """
        if self.start == self.end:
            return True, [self.start], 0, 1
        
        import heapq
        
        # OPEN SET: nós a serem avaliados (heap com f-score como prioridade)
        open_set = []
        heapq.heappush(open_set, (self.heuristic(self.start, self.end), self.start))
        
        # CLOSED SET: nós já avaliados
        closed_set = set()
        
        # g(n): custo real do início até o nó n
        g_score = {self.start: 0}
        
        # f(n) = g(n) + h(n): função de avaliação total
        f_score = {self.start: self.heuristic(self.start, self.end)}
        
        # Para reconstruir o caminho
        came_from = {}
        
        nodes_explored = 0
        
        while open_set:
            # REGRA A*: Pega o nó com menor f(n) do OPEN SET
            current_f, current = heapq.heappop(open_set)
            
            # CORREÇÃO: Ignora entradas desatualizadas no heap
            if current in closed_set:
                continue
                
            # CORREÇÃO: Verifica se f-score ainda é válido
            if current in f_score and current_f > f_score[current]:
                continue
            
            # REGRA A*: Move do OPEN SET para o CLOSED SET
            closed_set.add(current)
            nodes_explored += 1
            
            # REGRA A*: Se chegou ao objetivo, reconstrói e retorna caminho
            if current == self.end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.start)
                path.reverse()
                return True, path, g_score[self.end], nodes_explored
            
            # REGRA A*: Para cada vizinho do nó atual
            for neighbor in self.get_neighbors(current):
                # Se vizinho está no CLOSED SET, ignora
                if neighbor in closed_set:
                    continue
                
                # Calcula tentative_g_score = g(current) + dist(current, neighbor)
                tentative_g_score = g_score[current] + self.get_movement_cost(current, neighbor)
                
                # REGRA A*: Se este caminho para neighbor é melhor que qualquer anterior
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # Este é o melhor caminho até agora. Registra!
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, self.end)
                    
                    # CORREÇÃO: Sempre adiciona ao heap (permite múltiplas entradas)
                    # O heap automaticamente manterá a ordenação correta
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # Se OPEN SET está vazio e não chegamos ao objetivo, não há caminho
        return False, [], float('inf'), nodes_explored
    
    def search_with_callback(self, callback=None, max_steps=2000):
        """
        A* rigoroso com callback para visualização seguindo regras acadêmicas
        callback: função chamada com (current, closed_set, open_set, g_scores, f_score, g_score)
        """
        if self.start == self.end:
            return True, [self.start], 0, 1
        
        import heapq
        
        # OPEN SET: nós a serem avaliados
        open_set = []
        heapq.heappush(open_set, (self.heuristic(self.start, self.end), self.start))
        
        # CLOSED SET: nós já avaliados
        closed_set = set()
        
        # g(n): custo real do início até o nó n
        g_score = {self.start: 0}
        
        # f(n) = g(n) + h(n): função de avaliação total
        f_score = {self.start: self.heuristic(self.start, self.end)}
        
        # Para reconstruir o caminho
        came_from = {}
        
        nodes_explored = 0
        
        while open_set and nodes_explored < max_steps:
            # REGRA A*: Pega o nó com menor f(n) do OPEN SET
            current_f, current = heapq.heappop(open_set)
            
            # CORREÇÃO: Ignora entradas desatualizadas no heap
            if current in closed_set:
                continue
                
            # CORREÇÃO: Verifica se f-score ainda é válido
            if current in f_score and current_f > f_score[current]:
                continue
            
            # REGRA A*: Move do OPEN SET para o CLOSED SET
            closed_set.add(current)
            nodes_explored += 1
            
            # Callback para visualização
            if callback:
                open_nodes = {node for _, node in open_set if node not in closed_set}
                callback(current, closed_set.copy(), open_nodes, g_score.copy(), current_f, g_score[current])
            
            # REGRA A*: Se chegou ao objetivo, reconstrói caminho
            if current == self.end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(self.start)
                path.reverse()
                return True, path, g_score[self.end], nodes_explored
            
            # REGRA A*: Para cada vizinho do nó atual
            for neighbor in self.get_neighbors(current):
                # Se vizinho está no CLOSED SET, ignora
                if neighbor in closed_set:
                    continue
                
                # Calcula tentative_g_score = g(current) + dist(current, neighbor)
                tentative_g_score = g_score[current] + self.get_movement_cost(current, neighbor)
                
                # REGRA A*: Se este caminho é melhor que qualquer anterior
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # Este é o melhor caminho até agora. Registra!
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, self.end)
                    
                    # CORREÇÃO: Sempre adiciona ao heap
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return False, [], float('inf'), nodes_explored
    
    def search_simple(self):
        """
        Versão simplificada do A* que trata obstáculos como barreiras
        Útil para comparação com o BFS do maze
        """
        if self.start == self.end:
            return True, [self.start], 0, 1
        
        heap = [(self.heuristic(self.start, self.end), 0, self.start, [self.start])]
        g_scores = {self.start: 0}
        f_scores = {self.start: self.heuristic(self.start, self.end)}
        visited = set()
        nodes_explored = 0
        
        while heap:
            f_score, g_score, current_pos, path = heapq.heappop(heap)
            
            # Se já foi visitado ou temos f-score melhor, pula
            if current_pos in visited:
                continue
                
            if current_pos in f_scores and f_score > f_scores[current_pos]:
                continue
            
            visited.add(current_pos)
            nodes_explored += 1
            
            if current_pos == self.end:
                return True, path, g_score, nodes_explored
            
            # Para busca simples, só considera vizinhos livres
            for neighbor in self.get_simple_neighbors(current_pos):
                if neighbor not in visited:
                    tentative_g_score = g_score + 1  # Custo fixo de 1
                    
                    # Só adiciona se for caminho melhor
                    if neighbor not in g_scores or tentative_g_score < g_scores[neighbor]:
                        g_scores[neighbor] = tentative_g_score
                        h_score = self.heuristic(neighbor, self.end)
                        tentative_f_score = tentative_g_score + h_score
                        
                        # Só adiciona se f-score for melhor
                        if neighbor not in f_scores or tentative_f_score < f_scores[neighbor]:
                            f_scores[neighbor] = tentative_f_score
                            new_path = path + [neighbor]
                            heapq.heappush(heap, (tentative_f_score, tentative_g_score, neighbor, new_path))
        
        return False, [], float('inf'), nodes_explored
    
    def get_simple_neighbors(self, node):
        """Retorna apenas vizinhos livres (sem obstáculos ou paredes)"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        
        for dr, dc in directions:
            new_row, new_col = node[0] + dr, node[1] + dc
            
            if (0 <= new_row < self.rows and 0 <= new_col < self.cols):
                cell = self.grid[new_row][new_col]
                # Só aceita espaços livres, start e end
                if cell in [self.FREE, self.START, self.END]:
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def visualize_path_with_costs(self, path):
        """Visualiza o caminho encontrado mostrando os custos"""
        if not path:
            print("Nenhum caminho encontrado")
            return
        
        # Cria uma cópia do grid para visualização
        visual_grid = self.grid.copy()
        total_cost = 0
        
        # Marca o caminho e calcula custo total
        for i, pos in enumerate(path):
            row, col = pos
            if i == 0:  # Start
                visual_grid[row][col] = 'S'
            elif i == len(path) - 1:  # End
                visual_grid[row][col] = 'E'
            else:
                # Calcula custo de estar nesta posição
                if i > 0:
                    cost = self.get_movement_cost(path[i-1], pos)
                    total_cost += cost
                visual_grid[row][col] = '*'
        
        print(f"\n=== Caminho A* (com custos variáveis) ===")
        print("S=Start, E=End, *=Caminho, #=Obstáculo(custo 3), .=Livre(custo 1), █=Parede")
        print("-" * (self.cols * 2 + 1))
        for row in visual_grid:
            print(' '.join(row))
        print("-" * (self.cols * 2 + 1))
        print(f"Comprimento do caminho: {len(path)} passos")
        print(f"Custo total: {total_cost}")
        
        # Mostra detalhes do custo
        print(f"\nDetalhes dos custos:")
        for i in range(1, len(path)):
            from_pos, to_pos = path[i-1], path[i]
            cost = self.get_movement_cost(from_pos, to_pos)
            heuristic_cost = self.heuristic(to_pos, self.end)  
            total_cost = cost + heuristic_cost
            cell_type = self.grid[to_pos[0]][to_pos[1]]
            cell_name = 'obstáculo' if cell_type == self.OBSTACLE else 'livre'
            print(f"  {from_pos} → {to_pos}: custo total {total_cost} ({cell_name})")
        print()
    
    def compare_search_methods(self):
        """Compara A* com custos vs A* simples"""
        print("🔍 Comparando métodos de busca A*:")
        
        # A* com custos (permite obstáculos)
        found1, path1, cost1, nodes1 = self.search()
        
        # A* simples (obstáculos como barreiras)
        found2, path2, cost2, nodes2 = self.search_simple()
        
        print(f"A* com custos: {'✓' if found1 else '✗'} | "
              f"Caminho: {len(path1) if found1 else 0} | "
              f"Custo: {cost1 if found1 else '∞'} | "
              f"Nós: {nodes1}")
        
        print(f"A* simples:    {'✓' if found2 else '✗'} | "
              f"Caminho: {len(path2) if found2 else 0} | "
              f"Custo: {cost2 if found2 else '∞'} | "
              f"Nós: {nodes2}")
        
        if found1 and found2:
            if len(path1) < len(path2):
                print("🎯 A* com custos encontrou caminho mais curto!")
            elif len(path1) > len(path2):
                print("🎯 A* simples encontrou caminho mais curto!")
            else:
                print("📍 Ambos encontraram caminhos do mesmo tamanho")
        elif found1 and not found2:
            print("🎯 Apenas A* com custos encontrou caminho!")
        elif found2 and not found1:
            print("🎯 Apenas A* simples encontrou caminho!")
        
        return (found1, path1, cost1), (found2, path2, cost2)

