# 安装依赖：pip install pygame==2.5.2
import pygame
import sys
import json
import os
from datetime import datetime

from config import *
from entities import Snake, Food
from ai import SnakeAI
from ui import Button

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.load_config()
        self.screen = pygame.display.set_mode((self.window_size, self.window_size))
        self.clock = pygame.time.Clock()
        self.init_fonts()
        self.ai = SnakeAI(self)
        self.history = self.load_history()
        self.state = "START"
        self.reset()
        self.init_ui()

    def init_fonts(self):
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
        self.cell_size = self.window_size // GRID_SIZE

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
        on_off = "ON" if self.ai_enabled else "OFF"
        self.top_buttons[1].text_suffix = f": {on_off}"
        if "MENU" in self.buttons: self.buttons["MENU"][3].text_suffix = f": {on_off}"
        
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
        # 使用真实时间戳
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.history.append({"score": score, "date": now})
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
        
        # 1. 先处理进食与尾部移动
        if head == self.food.position:
            self.score += 10
            self.update_title()
            # 如果没有地方生成食物，说明通关
            if not self.food.respawn(self.snake.body):
                self.save_history(self.score)
                self.state = "OVER"
                return
        else:
            # 没吃到食物，移除尾部（蛇身整体前移一格）
            self.snake.pop_tail()

        # 2. 最后进行死亡碰撞检测
        # 此时检测的是移动并更新尾部后的状态，允许蛇头进入刚移开的尾巴格子
        if (not self.wrap_around and self.snake.check_wall_collision()) or self.snake.check_self_collision():
            self.save_history(self.score)
            self.state = "OVER"
            return

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
                    h_surf = self.font_ui.render(f"{i+1}. {ld['score']}: {e['score']} ({e.get('date', 'N/A')})", True, COLOR_WHITE)
                    self.screen.blit(h_surf, (self.window_size//2 - 120*self.scale_factor, (150 + i*30)*self.scale_factor))
            
            if self.state in self.buttons:
                for b in self.buttons[self.state]: b.draw(self.screen, self.window_size, self.scale_factor, ld)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events(); self.update(); self.draw(); self.clock.tick(FPS)

if __name__ == "__main__":
    SnakeGame().run()
