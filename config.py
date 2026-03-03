import pygame

# --- 游戏基础设置 ---
DEFAULT_WINDOW_SIZE = 600
GRID_SIZE = 20  # 必须是偶数以支持哈密顿回路
CELL_SIZE = DEFAULT_WINDOW_SIZE // GRID_SIZE
FPS = 60
CONFIG_FILE = "snake_config.json"
HISTORY_FILE = "snake_history.json"

# --- 颜色定义 (RGB) ---
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

# --- 方向定义 ---
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
