import numpy as np
import unittest
from sudoku import Sudoku

puzzle4 = np.array([[7, 0, 9, 0, 0, 0, 0, 0, 2],
                    [1, 0, 4, 0, 0, 0, 0, 5, 0],
                    [0, 2, 0, 1, 4, 9, 6, 0, 7],
                    [9, 0, 0, 0, 6, 8, 4, 7, 0],
                    [0, 4, 0, 3, 0, 0, 0, 0, 0],
                    [0, 7, 0, 0, 0, 0, 5, 0, 0],
                    [0, 0, 2, 0, 0, 1, 0, 6, 4],
                    [0, 8, 0, 0, 0, 0, 3, 0, 5],
                    [0, 1, 0, 0, 3, 7, 8, 2, 0]], dtype=np.int8)

puzzle6 = np.array([[7, 0, 0, 2, 3, 5, 8, 9, 0],
                    [0, 9, 1, 6, 0, 8, 0, 4, 3],
                    [0, 0, 0, 1, 4, 9, 7, 0, 6],
                    [0, 2, 5, 4, 6, 3, 9, 8, 0],
                    [6, 0, 4, 0, 0, 0, 2, 0, 0],
                    [9, 7, 0, 5, 0, 1, 0, 0, 4],
                    [4, 6, 9, 0, 5, 0, 0, 0, 8],
                    [3, 1, 7, 9, 8, 0, 0, 5, 0],
                    [0, 5, 0, 3, 1, 4, 6, 0, 9]], dtype=np.int8)

puzzle8 = np.array([[9, 5, 4, 2, 7, 6, 0, 0, 3],
                    [3, 7, 1, 5, 8, 9, 6, 2, 0],
                    [2, 6, 8, 4, 3, 1, 7, 9, 5],
                    [5, 3, 9, 0, 4, 0, 1, 6, 0],
                    [8, 4, 6, 7, 1, 0, 9, 3, 2],
                    [0, 1, 0, 6, 9, 0, 4, 5, 0],
                    [1, 8, 3, 0, 2, 0, 5, 4, 0],
                    [6, 2, 7, 1, 0, 4, 3, 8, 9],
                    [4, 9, 5, 3, 6, 8, 2, 0, 1]], dtype=np.int8)

invalid = np.array([[9, 5, 4, 2, 7, 6, 0, 0, 3],
                    [3, 7, 1, 5, 8, 9, 6, 2, 0],
                    [2, 6, 8, 4, 3, 1, 7, 9, 5],
                    [5, 3, 9, 0, 4, 0, 1, 6, 0],
                    [8, 4, 6, 7, 1, 1, 9, 3, 2],
                    [0, 1, 0, 6, 9, 0, 4, 5, 0],
                    [1, 8, 3, 0, 2, 0, 5, 4, 0],
                    [6, 2, 7, 1, 0, 4, 3, 8, 9],
                    [4, 9, 5, 3, 6, 8, 2, 0, 1]], dtype=np.int8)


class BaseTest(unittest.TestCase):
    def test_preset_easy(self):
        s = Sudoku(preset=puzzle8)
        solution = s.solve()
        self.assertIsNotNone(solution)

    def test_preset_medium(self):
        s = Sudoku(preset=puzzle6)
        solution = s.solve()
        self.assertIsNotNone(solution)

    def test_preset_hard(self):
        s = Sudoku(preset=puzzle4)
        solution = s.solve()
        self.assertIsNotNone(solution)

    def test_preset_invalid(self):
        s = Sudoku(preset=invalid)
        solution = s.solve()
        self.assertIsNone(solution)

    def test_consistent(self):
        s = Sudoku()
        self.assertTrue(s.consistent(puzzle6))
        self.assertFalse(s.consistent(invalid))

    def test_generate(self):
        s = Sudoku()
        s.generate(1)
        self.assertTrue(s.consistent(s.preset))

    def test_generate_and_solve(self):
        s = Sudoku()
        s.generate(0.5)
        s.solve()
        self.assertTrue(s.consistent(s.assignment + s.preset))


class GraphicsTest(unittest.TestCase):
    def test_preset_easy(self):
        s = Sudoku(preset=puzzle8, graphics=True)
        solution = s.solve()
        self.assertIsNotNone(solution)
        s.graphics.window.close()

    def test_preset_medium(self):
        s = Sudoku(preset=puzzle6, graphics=True)
        solution = s.solve()
        self.assertIsNotNone(solution)
        s.graphics.window.close()

    def test_preset_hard(self):
        s = Sudoku(preset=puzzle4, graphics=True)
        solution = s.solve()
        self.assertIsNotNone(solution)
        s.graphics.stay_open()
        s.graphics.window.close()

    def test_generate(self):
        s = Sudoku(graphics=True)
        s.generate(1)
        self.assertTrue(s.consistent(s.preset))
        s.graphics.window.close()

    def test_generate_and_solve(self):
        s = Sudoku(graphics=True)
        s.generate(0.08)
        s.solve()
        self.assertTrue(s.consistent(s.assignment + s.preset))
        s.graphics.window.close()


if __name__ == '__main__':
    unittest.main()
