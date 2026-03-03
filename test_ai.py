import unittest
from snake import Snake, GRID_SIZE, DIR_RIGHT, DIR_LEFT, DIR_UP, DIR_DOWN, SnakeGame, SnakeAI

class TestSnakeAI(unittest.TestCase):
    def setUp(self):
        self.game = SnakeGame()
        self.ai = SnakeAI(self.game)

    def test_get_distance(self):
        self.assertEqual(self.ai.get_distance((0,0), (3,4)), 7)
        self.assertEqual(self.ai.get_distance((5,5), (5,5)), 0)

    def test_get_neighbors_no_wrap(self):
        self.game.wrap_around = False
        neighbors = self.ai.get_neighbors((0,0), [(0,0)])
        # (0,0) 的邻居在不穿墙且无阻挡时应只有 (1,0) 和 (0,1)
        self.assertIn((1,0), neighbors)
        self.assertIn((0,1), neighbors)
        self.assertEqual(len(neighbors), 2)

    def test_get_neighbors_with_body(self):
        self.game.wrap_around = False
        # 蛇身在 (1,0) (1,1)，头在 (0,0)
        # 邻居：(0,1) 是尾部 -> 允许；(1,0) 是身体 -> 排除
        neighbors = self.ai.get_neighbors((0,0), [(0,0), (1,0), (0,1)])
        self.assertNotIn((1,0), neighbors)
        self.assertIn((0,1), neighbors)

    def test_a_star_simple_path(self):
        self.game.wrap_around = False
        start = (0,0)
        target = (2,0)
        # 蛇身远离路径
        body = [(0,0), (0,5), (0,6)]
        path = self.ai.a_star(start, target, body)
        self.assertIsNotNone(path)
        self.assertEqual(path, [(1,0), (2,0)])

    def test_a_star_blocked_path(self):
        self.game.wrap_around = False
        start = (0,0)
        target = (2,0)
        # 完全堵死 (0,0) 的所有邻居
        # (0,0) 的有效邻居只有 (1,0) 和 (0,1)
        # 我们把这两个都设为身体的一部分且不是尾部
        body = [(0,0), (1,0), (0,1), (1,1)] # (1,1) 是尾部，但它不直接连 (0,0)
        path = self.ai.a_star(start, target, body)
        self.assertIsNone(path)

    def test_pos_to_dir(self):
        self.assertEqual(self.ai.pos_to_dir((0,0), (1,0)), DIR_RIGHT)
        self.assertEqual(self.ai.pos_to_dir((0,0), (0,1)), DIR_DOWN)

if __name__ == '__main__':
    unittest.main()
