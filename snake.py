# 安装依赖：pip install pygame==2.5.2
import pygame
import sys
import random
import json
import os
import heapq
import math

# --- 类常量定义 ---
DEFAULT_WINDOW_SIZE = 600
GRID_SIZE = 20
FPS = 60
CONFIG_FILE = "snake_config.json"
HISTORY_FILE = "snake_history.json"

# 颜色定义 (RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (40, 40, 40)
COLOR_LIGHT_GRAY = (100, 100, 100)
COLOR_GREEN = (0, 255, 0)
COLOR_BRIGHT_GREEN = (50, 255, 50)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 120, 215)
COLOR_DISABLED = (60, 60, 60)
COLOR_OVERLAY = (0, 0, 0, 180)

# 方向定义
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# --- 国际化资源 ---
LANGUAGES = {
    "zh": {
        "title": "贪吃蛇",
        "score": "得分",
        "start": "开始游戏",
        "ai_auto": "AI 自动游玩",
        "resume": "继续游戏",
        "main_menu": "返回主菜单",
        "history": "历史记录",
        "settings": "设置",
        "quit": "退出",
        "restart": "重新开始",
        "back": "返回",
        "speed": "移动速度",
        "size": "画面尺寸",
        "wall": "边界碰撞",
        "ai_depth": "AI 预测深度",
        "language": "语言",
        "game_over": "游戏结束!",
        "win": "你赢了!",
        "slow": "慢",
        "medium": "中",
        "fast": "快",
        "solid": "实体",
        "wrap": "穿透",
        "ai_status_chase": "正在寻找食物",
        "ai_status_survival": "生存模式",
        "top_scores": "最高得分"
    },
    "en": {
        "title": "Snake",
        "score": "Score",
        "start": "Start Game",
        "ai_auto": "AI Auto Play",
        "resume": "Resume",
        "main_menu": "Main Menu",
        "history": "History",
        "settings": "Settings",
        "quit": "Quit",
        "restart": "Restart",
        "back": "Back",
        "speed": "Speed",
        "size": "Size",
        "wall": "Wall",
        "ai_depth": "AI Depth",
        "language": "Language",
        "game_over": "Game Over!",
        "win": "You Win!",
        "slow": "Slow",
        "medium": "Medium",
        "fast": "Fast",
        "solid": "Solid",
        "wrap": "Wrap",
        "ai_status_chase": "Chasing Food",
        "ai_status_survival": "Survival Mode",
        "top_scores": "TOP 10 SCORES"
    }
}

class Snake:
    def __init__(self):
        mid = GRID_SIZE // 2
        self.body = [(mid, mid), (mid - 1, mid), (mid - 2, mid)]
        self.direction = DIR_RIGHT
        self.direction_queue = []

    def move(self, wrap_around=False):
        if self.direction_queue:
            self.direction = self.direction_queue.pop(0)
            
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_x, new_y = head_x + dx, head_y + dy
        
        if wrap_around:
            new_x %= GRID_SIZE
            new_y %= GRID_SIZE
            
        new_head = (new_x, new_y)
        self.body.insert(0, new_head)
        return new_head

    def pop_tail(self):
        self.body.pop()

    def check_self_collision(self):
        head = self.body[0]
        return head in self.body[1:]

    def check_wall_collision(self):
        head_x, head_y = self.body[0]
        return head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE

class Food:
    def __init__(self):
        self.position = (0, 0)

    def respawn(self, snake_body):
        all_cells = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
        possible_cells = [cell for cell in all_cells if cell not in snake_body]
        if not possible_cells:
            return False
        self.position = random.choice(possible_cells)
        return True

class SnakeAI:
    def __init__(self, game):
        self.game = game
        self.prediction_depth = 2

    def get_distance(self, p1, p2):
        dx = abs(p1[0] - p2[0])
        dy = abs(p1[1] - p2[1])
        if self.game.wrap_around:
            dx = min(dx, GRID_SIZE - dx)
            dy = min(dy, GRID_SIZE - dy)
        return dx + dy

    def get_neighbors(self, pos, snake_body):
        neighbors = []
        for dx, dy in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]:
            nx, ny = pos[0] + dx, pos[1] + dy
            if self.game.wrap_around:
                nx %= GRID_SIZE
                ny %= GRID_SIZE
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
        while open_set:
            _, current = heapq.heappop(open_set)
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
        head = snake_body[0]
        tail = snake_body[-1]
        tail_path = self.a_star(head, tail, snake_body)
        if tail_path: return tail_path[0]
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
        max_search = GRID_SIZE * GRID_SIZE
        while queue and count < max_search:
            curr = queue.pop(0)
            if curr in visited: continue
            visited.add(curr)
            count += 1
            queue.extend(self.get_neighbors(curr, snake_body))
        return count

    def get_next_direction(self):
        head = self.game.snake.body[0]
        target = self.game.food.position
        body = self.game.snake.body
        path = self.a_star(head, target, body)
        if path:
            next_step = path[0]
            virtual_body = [next_step] + body[:-1]
            if self.a_star(next_step, virtual_body[-1], virtual_body) or \
               self.count_reachable_space(next_step, virtual_body) > len(body):
                return self.pos_to_dir(head, next_step)
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

class Button:
    def __init__(self, anchor_x, anchor_y, width, height, text_key, font, color=COLOR_BLUE, text_color=COLOR_WHITE, icon=None, is_toggle=False):
        self.anchor_x = anchor_x # 0.0 to 1.0
        self.anchor_y = anchor_y # 0.0 to 1.0
        self.base_width = width
        self.base_height = height
        self.text_key = text_key
        self.font = font
        self.color = color
        self.text_color = text_color
        self.icon = icon
        self.is_toggle = is_toggle
        self.hovered = False
        self.animation_scale = 1.0
        self.rect = pygame.Rect(0, 0, width, height)

    def draw(self, screen, window_size, scale_factor, lang_dict):
        target_scale = 1.05 if self.hovered else 1.0
        self.animation_scale += (target_scale - self.animation_scale) * 0.2
        
        w = self.base_width * scale_factor * self.animation_scale
        h = self.base_height * scale_factor * self.animation_scale
        cx = window_size * self.anchor_x
        cy = window_size * self.anchor_y
        
        self.rect = pygame.Rect(0, 0, max(w, 44*scale_factor), max(h, 44*scale_factor))
        self.rect.center = (cx, cy)

        draw_color = [min(255, c + 30) if self.hovered else c for c in self.color]
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=int(5 * scale_factor))
        
        if self.icon == 'gear':
            self._draw_gear(screen, self.rect, scale_factor)
        elif self.text_key:
            text = lang_dict.get(self.text_key, self.text_key)
            # 处理带变量的文本
            if hasattr(self, 'text_suffix'): text += self.text_suffix
            
            text_surf = self.font.render(text, True, self.text_color)
            if scale_factor != 1.0:
                new_size = (int(text_surf.get_width() * scale_factor), int(text_surf.get_height() * scale_factor))
                text_surf = pygame.transform.smoothscale(text_surf, new_size)
            screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def _draw_gear(self, screen, rect, scale):
        cx, cy = rect.center
        r = rect.width * 0.3
        pygame.draw.circle(screen, self.text_color, (cx, cy), r, int(2*scale))
        for i in range(8):
            angle = math.radians(i * 45)
            x1, y1 = cx + math.cos(angle)*r, cy + math.sin(angle)*r
            x2, y2 = cx + math.cos(angle)*(r+5*scale), cy + math.sin(angle)*(r+5*scale)
            pygame.draw.line(screen, self.text_color, (x1, y1), (x2, y2), int(2*scale))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.load_config()
        self.cell_size = self.window_size // GRID_SIZE
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        self.clock = pygame.time.Clock()
        self.init_fonts()
        self.ai = SnakeAI(self)
        self.history = self.load_history()
        self.state = "START"
        self.reset()
        self.init_ui()

    def init_fonts(self):
        # 尝试加载中文字体
        font_names = ["microsoftyahei", "simhei", "arial"]
        self.font_main = self._get_font(font_names, 36, True)
        self.font_ui = self._get_font(font_names, 24)
        self.font_small = self._get_font(font_names, 18)

    def _get_font(self, names, size, bold=False):
        for name in names:
            try: return pygame.font.SysFont(name, size, bold)
            except: continue
        return pygame.font.SysFont(None, size, bold)

    def load_config(self):
        default = {"size": 600, "lang": "zh", "speed": 100, "wrap": False, "ai": False, "ai_depth": 2}
        if os.path.exists(CONFIG_FILE):
            try: 
                with open(CONFIG_FILE, "r") as f: default.update(json.load(f))
            except: pass
        self.window_size = default["size"]
        self.lang = default["lang"]
        self.logic_interval = default["speed"]
        self.wrap_around = default["wrap"]
        self.ai_enabled = default["ai"]
        self.ai_depth = default["ai_depth"]

    def save_config(self):
        config = {"size": self.window_size, "lang": self.lang, "speed": self.logic_interval, 
                  "wrap": self.wrap_around, "ai": self.ai_enabled, "ai_depth": self.ai_depth}
        with open(CONFIG_FILE, "w") as f: json.dump(config, f)

    def init_ui(self):
        self.scale_factor = max(0.75, min(1.5, self.window_size / 600.0))
        bw, bh = 220, 50
        self.top_buttons = [
            Button(0.08, 0.08, 44, 44, None, self.font_ui, icon='gear'),
            Button(0.25, 0.08, 120, 44, "ai_auto", self.font_small)
        ]
        self.top_buttons[1].text_suffix = f": {'ON' if self.ai_enabled else 'OFF'}"
        
        self.buttons = {
            "START": [
                Button(0.5, 0.45, bw, bh, "start", self.font_ui),
                Button(0.5, 0.55, bw, bh, "ai_auto", self.font_ui)
            ],
            "PAUSED": [
                Button(0.5, 0.45, bw, bh, "resume", self.font_ui),
                Button(0.5, 0.55, bw, bh, "main_menu", self.font_ui)
            ],
            "MENU": [
                Button(0.5, 0.35, bw, bh, "resume", self.font_ui),
                Button(0.5, 0.45, bw, bh, "history", self.font_ui),
                Button(0.5, 0.55, bw, bh, "settings", self.font_ui),
                Button(0.5, 0.65, bw, bh, "ai_auto", self.font_ui),
                Button(0.5, 0.75, bw, bh, "quit", self.font_ui, COLOR_RED)
            ],
            "OVER": [Button(0.5, 0.6, bw, bh, "restart", self.font_ui)],
            "SETTINGS": [
                Button(0.5, 0.2, bw, bh, "language", self.font_ui),
                Button(0.5, 0.3, bw, bh, "speed", self.font_ui),
                Button(0.5, 0.4, bw, bh, "size", self.font_ui),
                Button(0.5, 0.5, bw, bh, "wall", self.font_ui),
                Button(0.5, 0.6, bw, bh, "ai_depth", self.font_ui),
                Button(0.5, 0.8, bw, bh, "back", self.font_ui)
            ],
            "HISTORY": [Button(0.5, 0.85, bw, bh, "back", self.font_ui)]
        }
        self.update_button_texts()

    def update_button_texts(self):
        ld = LANGUAGES[self.lang]
        self.top_buttons[1].text_suffix = f": {'ON' if self.ai_enabled else 'OFF'}"
        if "MENU" in self.buttons: self.buttons["MENU"][3].text_suffix = f": {'ON' if self.ai_enabled else 'OFF'}"
        
        s_btn = self.buttons["SETTINGS"]
        s_btn[0].text_suffix = f": {self.lang.upper()}"
        speeds = {150: ld["slow"], 100: ld["medium"], 50: ld["fast"]}
        s_btn[1].text_suffix = f": {speeds.get(self.logic_interval, '???')}"
        s_btn[2].text_suffix = f": {self.window_size}x{self.window_size}"
        s_btn[3].text_suffix = f": {ld['wrap'] if self.wrap_around else ld['solid']}"
        s_btn[4].text_suffix = f": {self.ai_depth}"

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try: 
                with open(HISTORY_FILE, "r") as f: return json.load(f)
            except: return []
        return []

    def save_history(self, score):
        self.history.append({"score": score, "date": pygame.time.get_ticks()})
        self.history = sorted(self.history, key=lambda x: x["score"], reverse=True)[:10]
        with open(HISTORY_FILE, "w") as f: json.dump(self.history, f)

    def reset(self):
        self.snake = Snake()
        self.food = Food()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.last_update_time = pygame.time.get_ticks()
        self.start_ticks = pygame.time.get_ticks()
        self.survival_time = 0
        self.update_title()

    def update_title(self):
        ld = LANGUAGES[self.lang]
        pygame.display.set_caption(f"{ld['title']} - {ld['score']}: {self.score}")

    def handle_events(self):
        m_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_config(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING": self.state = "MENU"
                    elif self.state in ["MENU", "PAUSED"]: self.state = "PLAYING"
                    else: self.state = "MENU"
                elif self.key_to_dir(event.key) and self.state == "PLAYING":
                    new_dir = self.key_to_dir(event.key)
                    base = self.snake.direction_queue[-1] if self.snake.direction_queue else self.snake.direction
                    # 防冲突
                    if (new_dir[0] + base[0], new_dir[1] + base[1]) != (0, 0):
                        if len(self.snake.direction_queue) < 2: self.snake.direction_queue.append(new_dir)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn in self.top_buttons:
                    if btn.is_clicked(m_pos): self.handle_click(btn.text_key or "gear")
                if self.state in self.buttons:
                    for btn in self.buttons[self.state]:
                        if btn.is_clicked(m_pos): self.handle_click(btn.text_key)

        for b in self.top_buttons: b.hovered = b.rect.collidepoint(m_pos)
        if self.state in self.buttons:
            for b in self.buttons[self.state]: b.hovered = b.rect.collidepoint(m_pos)

    def key_to_dir(self, key):
        if key in [pygame.K_UP, pygame.K_w]: return DIR_UP
        if key in [pygame.K_DOWN, pygame.K_s]: return DIR_DOWN
        if key in [pygame.K_LEFT, pygame.K_a]: return DIR_LEFT
        if key in [pygame.K_RIGHT, pygame.K_d]: return DIR_RIGHT
        return None

    def handle_click(self, key):
        if key in ["start", "restart"]: self.reset(); self.state = "PLAYING"
        elif key == "ai_auto": self.ai_enabled = not self.ai_enabled; self.update_button_texts()
        elif key == "resume": self.state = "PLAYING"
        elif key == "main_menu": self.state = "START"
        elif key == "history": self.state = "HISTORY"
        elif key == "settings" or key == "gear": self.state = "SETTINGS"
        elif key == "quit": self.save_config(); pygame.quit(); sys.exit()
        elif key == "back": self.state = "MENU"
        elif key == "language": self.lang = "en" if self.lang == "zh" else "zh"; self.update_button_texts(); self.update_title()
        elif key == "speed":
            intervals = [150, 100, 50]
            self.logic_interval = intervals[(intervals.index(self.logic_interval)+1)%3]
            self.update_button_texts()
        elif key == "size":
            sizes = [600, 800, 400]
            self.window_size = sizes[(sizes.index(self.window_size)+1)%3]
            self.cell_size = self.window_size // GRID_SIZE
            self.screen = pygame.display.set_mode((self.window_size, self.window_size))
            self.init_ui()
        elif key == "wall": self.wrap_around = not self.wrap_around; self.update_button_texts()
        elif key == "ai_depth":
            depths = [2, 5, 10, 20]
            self.ai_depth = depths[(depths.index(self.ai_depth)+1)%4]
            self.ai.prediction_depth = self.ai_depth
            self.update_button_texts()

    def update(self):
        if self.state != "PLAYING": return
        curr = pygame.time.get_ticks()
        self.survival_time = (curr - self.start_ticks) // 1000
        if curr - self.last_update_time < self.logic_interval: return
        self.last_update_time = curr
        
        if self.ai_enabled:
            d = self.ai.get_next_direction()
            if d != self.snake.direction and not self.snake.direction_queue:
                self.snake.direction_queue.append(d)
        
        head = self.snake.move(self.wrap_around)
        if (not self.wrap_around and self.snake.check_wall_collision()) or self.snake.check_self_collision():
            self.save_history(self.score); self.state = "OVER"; return
        if head == self.food.position:
            self.score += 10; self.update_title()
            if not self.food.respawn(self.snake.body): self.state = "OVER"
        else: self.snake.pop_tail()

    def draw(self):
        self.screen.fill(COLOR_BLACK)
        ld = LANGUAGES[self.lang]
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, COLOR_GRAY, (i*self.cell_size, 0), (i*self.cell_size, self.window_size))
            pygame.draw.line(self.screen, COLOR_GRAY, (0, i*self.cell_size), (self.window_size, i*self.cell_size))
        
        pygame.draw.rect(self.screen, COLOR_RED, (self.food.position[0]*self.cell_size, self.food.position[1]*self.cell_size, self.cell_size, self.cell_size))
        for i, (bx, by) in enumerate(self.snake.body):
            pygame.draw.rect(self.screen, COLOR_BRIGHT_GREEN if i==0 else COLOR_GREEN, (bx*self.cell_size, by*self.cell_size, self.cell_size, self.cell_size))

        for btn in self.top_buttons: btn.draw(self.screen, self.window_size, self.scale_factor, ld)

        if self.state != "PLAYING":
            overlay = pygame.Surface((self.window_size, self.window_size), pygame.SRCALPHA)
            overlay.fill(COLOR_OVERLAY)
            self.screen.blit(overlay, (0,0))
            titles = {"START": ld["title"], "PAUSED": ld["resume"], "MENU": ld["settings"], "OVER": ld["game_over"], "SETTINGS": ld["settings"], "HISTORY": ld["top_scores"]}
            t_surf = self.font_main.render(titles.get(self.state, ""), True, COLOR_WHITE)
            self.screen.blit(t_surf, t_surf.get_rect(center=(self.window_size//2, 80*self.scale_factor)))

            if self.state == "HISTORY":
                for i, e in enumerate(self.history):
                    h_surf = self.font_ui.render(f"{i+1}. {ld['score']}: {e['score']}", True, COLOR_WHITE)
                    self.screen.blit(h_surf, (self.window_size//2 - 80*self.scale_factor, (150 + i*30)*self.scale_factor))
            
            if self.state in self.buttons:
                for b in self.buttons[self.state]: b.draw(self.screen, self.window_size, self.scale_factor, ld)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events(); self.update(); self.draw(); self.clock.tick(FPS)

if __name__ == "__main__":
    SnakeGame().run()
