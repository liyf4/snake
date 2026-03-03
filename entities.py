import random
from config import GRID_SIZE, DIR_RIGHT

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
