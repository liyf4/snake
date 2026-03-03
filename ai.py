import heapq
from config import GRID_SIZE, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT

class SnakeAI:
    def __init__(self, game):
        self.game = game
        self.prediction_depth = 2
        self.hamiltonian_cycle = self.generate_hamiltonian_cycle()

    def generate_hamiltonian_cycle(self):
        """生成一个简单的哈密顿回路 (S型路径)"""
        # 假设 GRID_SIZE 是偶数
        path = {}
        # 0,0 -> 0,1 -> 0,2 ... -> 0,GRID-1
        # -> 1,GRID-1 -> 1,GRID-2 ... -> 1,0
        # ...
        for x in range(GRID_SIZE):
            if x % 2 == 0:
                # 向下走
                for y in range(GRID_SIZE - 1):
                    path[(x, y)] = (x, y + 1)
                # 最后一格向右
                if x < GRID_SIZE - 1:
                    path[(x, GRID_SIZE - 1)] = (x + 1, GRID_SIZE - 1)
                else:
                    # 最后一列回到起点 (这里是简单的回路闭合)
                    path[(x, GRID_SIZE - 1)] = (x, GRID_SIZE - 2) # 修正：最后一列需要特殊处理
            else:
                # 向上走
                for y in range(GRID_SIZE - 1, 0, -1):
                    path[(x, y)] = (x, y - 1)
                # 第一格向右
                if x < GRID_SIZE - 1:
                    path[(x, 0)] = (x + 1, 0)
        
        # 修正最后一列和回程
        # 上述逻辑在 GRID_SIZE 为偶数时，最后一列向上走到 (GRID-1, 0)
        # 我们需要从 (GRID-1, 0) 回到 (0, 0)
        # 重构一个更通用的 S 型回路：
        cycle = {}
        # 第一列向下
        for y in range(GRID_SIZE - 1):
            cycle[(0, y)] = (0, y + 1)
        # 底边向右一格
        cycle[(0, GRID_SIZE - 1)] = (1, GRID_SIZE - 1)
        
        # 剩余部分蛇形排布
        for x in range(1, GRID_SIZE):
            if x % 2 == 1: # 奇数列向上
                for y in range(GRID_SIZE - 1, 0, -1):
                    cycle[(x, y)] = (x, y - 1)
                if x < GRID_SIZE - 1:
                    cycle[(x, 0)] = (x + 1, 0)
                else:
                    cycle[(x, 0)] = (0, 0) # 最后一格回起点
            else: # 偶数列向下
                for y in range(0, GRID_SIZE - 1):
                    cycle[(x, y)] = (x, y + 1)
                if x < GRID_SIZE - 1:
                    cycle[(x, GRID_SIZE - 1)] = (x + 1, GRID_SIZE - 1)
        
        # 此时第一行除了 (0,0) 都被占用了，(1,0) -> (2,0) -> (3,0) ...
        # 需要确保 (0,0) 能够从某处进入。在上面的逻辑中，最后一列向上走到 (GRID-1, 0) 后直接跳回了 (0,0)
        # 这在 GRID_SIZE > 2 时会跳过第一行的大部分。
        # 重新设计一个更标准的回路：
        standard_cycle = {}
        # 1. 第一行全部向左 (除了 0,0)
        for x in range(1, GRID_SIZE):
            standard_cycle[(x, 0)] = (x - 1, 0)
        standard_cycle[(0, 0)] = (0, 1)
        
        # 2. 剩余部分蛇形
        for x in range(GRID_SIZE):
            if x % 2 == 0: # 偶数列向下 (除了第一行)
                for y in range(1, GRID_SIZE - 1):
                    standard_cycle[(x, y)] = (x, y + 1)
                if x < GRID_SIZE - 1:
                    standard_cycle[(x, GRID_SIZE - 1)] = (x + 1, GRID_SIZE - 1)
            else: # 奇数列向上 (除了第一行)
                for y in range(GRID_SIZE - 1, 1, -1):
                    standard_cycle[(x, y)] = (x, y - 1)
                if x < GRID_SIZE - 1:
                    standard_cycle[(x, 1)] = (x + 1, 1)
                else:
                    standard_cycle[(x, 1)] = (x, 0) # 最后一列回到第一行
        
        return standard_cycle

    def get_distance(self, p1, p2):
        dx, dy = abs(p1[0] - p2[0]), abs(p1[1] - p2[1])
        if self.game.wrap_around:
            dx, dy = min(dx, GRID_SIZE - dx), min(dy, GRID_SIZE - dy)
        return dx + dy

    def get_neighbors(self, pos, snake_body):
        neighbors = []
        for dx, dy in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]:
            nx, ny = pos[0] + dx, pos[1] + dy
            if self.game.wrap_around:
                nx, ny = nx % GRID_SIZE, ny % GRID_SIZE
            elif nx < 0 or nx >= GRID_SIZE or ny < 0 or ny >= GRID_SIZE:
                continue
            if len(snake_body) > 1 and (nx, ny) == snake_body[1]:
                continue
            if (nx, ny) not in snake_body[:-1]:
                neighbors.append((nx, ny))
        return neighbors

    def a_star(self, start, target, snake_body):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.get_distance(start, target)}
        
        # 使用 prediction_depth 限制搜索范围
        max_nodes = self.prediction_depth * 100 
        nodes_searched = 0

        while open_set and nodes_searched < max_nodes:
            _, current = heapq.heappop(open_set)
            nodes_searched += 1
            if current == target:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            for neighbor in self.get_neighbors(current, snake_body):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.get_distance(neighbor, target)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None

    def get_safe_move(self, snake_body):
        head, tail = snake_body[0], snake_body[-1]
        tail_path = self.a_star(head, tail, snake_body)
        if tail_path: return tail_path[0]
        
        # 使用 BFS 计算空间，受限于 prediction_depth
        possible_moves = self.get_neighbors(head, snake_body)
        if not possible_moves: return None
        best_move, max_space = None, -1
        for move in possible_moves:
            space = self.count_reachable_space(move, snake_body)
            if space > max_space: max_space, best_move = space, move
        return best_move

    def count_reachable_space(self, start, snake_body):
        visited = set(snake_body)
        queue = [start]
        count = 0
        # 限制计算深度
        max_search = min(GRID_SIZE * GRID_SIZE, self.prediction_depth * 50)
        while queue and count < max_search:
            curr = queue.pop(0)
            if curr in visited: continue
            visited.add(curr)
            count += 1
            queue.extend(self.get_neighbors(curr, snake_body))
        return count

    def get_hamiltonian_move(self, head):
        """获取哈密顿回路中的下一步"""
        return self.hamiltonian_cycle.get(head)

    def can_shortcut(self, head, target, snake_body):
        """检查是否可以安全地抄近道"""
        # 如果蛇太长（超过一半），强制走哈密顿回路以保安全
        if len(snake_body) > (GRID_SIZE * GRID_SIZE) // 2:
            return False
            
        path = self.a_star(head, target, snake_body)
        if not path: return False
        
        # 模拟走完捷径后的安全性
        next_step = path[0]
        virtual_body = [next_step] + snake_body[:-1]
        
        # 捷径必须满足：1. 依然在哈密顿路径上落后于尾部位置（简化：能到达尾部）
        if self.a_star(next_step, virtual_body[-1], virtual_body):
            return next_step
        return False

    def get_next_direction(self):
        head = self.game.snake.body[0]
        target = self.game.food.position
        body = self.game.snake.body

        # 1. 尝试抄近道吃食物 (A*)
        shortcut = self.can_shortcut(head, target, body)
        if shortcut:
            return self.pos_to_dir(head, shortcut)

        # 2. 如果不安全或没路径，遵循哈密顿回路
        # 注意：穿墙模式下哈密顿回路失效，退回到基础 AI
        if not self.game.wrap_around:
            next_step = self.get_hamiltonian_move(head)
            if next_step and next_step not in body[:-1]:
                return self.pos_to_dir(head, next_step)

        # 3. 兜底策略：走空间或追尾
        safe_step = self.get_safe_move(body)
        if safe_step: return self.pos_to_dir(head, safe_step)
        
        return self.game.snake.direction

    def pos_to_dir(self, start, end):
        dx, dy = end[0] - start[0], end[1] - start[1]
        if self.game.wrap_around:
            if dx > 1: dx = -1
            elif dx < -1: dx = 1
            if dy > 1: dy = -1
            elif dy < -1: dy = 1
        return (dx, dy)
