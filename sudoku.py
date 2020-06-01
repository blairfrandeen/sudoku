from math import sqrt
from typing import NamedTuple, List, Dict, Optional
from sudoku_graphics import SudokuGraphics
import numpy as np
import cProfile

# I'm now convinced that CSP is totally inappropriate to solve Sudoku.
# In other words, it has far more expandability than it needs to, and
# that makes it very slow for what should be a simpler problem.
# CSP allows for multiple variables, each having different domains,
# different constraints, or different types of variables. Sudoku,
# on the other hands, has the same variables, each variable has the
# same domain, and each variable has the exact same constraint.
# Using the csp framework this runs in about 2.2 seconds. let's see
# how well I can do without it now...


class BoardLocation(NamedTuple):
    row: int
    column: int


class Sudoku:
    def __init__(self, size: Optional[int] = 9,
                 assignment: Optional[np.array] = None,
                 preset: Optional[np.array] = None,
                 graphics: Optional = False):
        if sqrt(size) % 1 != 0:
            raise ValueError('Size of Sudoku board must be a perfect square!')
        self.size: int = size
        self.empty = np.zeros((self.size, self.size), dtype=np.int8)
        self.preset: np.array = self.empty if preset is None else preset
        self.domain = list(range(1, self.size + 1))
        if assignment is None:
            self.assignment = self.empty
        self.locations: List[BoardLocation] = [BoardLocation(row, column)
                                               for row, r in enumerate(self.assignment)
                                               for column, c in enumerate(r)
                                               if c == 0]
        self.graphics = SudokuGraphics(self) if graphics else None

    @staticmethod
    def num_assigned(assignment) -> int:
        # return the number of locations in the numpy array that are not zero
        return len([cell for row in assignment for cell in row if cell != 0])

    def __repr__(self) -> str:
        return repr(self.assignment)

    def generate(self, percent_to_fill) -> None:
        if percent_to_fill > 1 or percent_to_fill < 0:
            raise ValueError('Percent to fill should between 0 and 1')
        self.assignment = self.solve(fill_random=True)
        locations_to_empty = self.locations.copy()
        np.random.shuffle(locations_to_empty)
        number_to_empty = int((1 - percent_to_fill) * self.size * self.size)
        for location in locations_to_empty[0:number_to_empty]:
            self.assignment[location] = 0
        self.preset: np.array = self.assignment
        if self.graphics:
            self.graphics.set_presets(self.preset)

    def solve(self, assignment: Optional[np.array] = None,
              fill_random: bool = False) -> Optional[np.array]:
        if assignment is None:
            assignment = self.empty
        # base case:
        if self.num_assigned(assignment) + self.num_assigned(self.preset) == len(self.locations):
            self.assignment = assignment
            if self.graphics:
                for _ in range(self.graphics.num_colors):
                    self.graphics.update_cells(self.assignment)
            return self.assignment

        unassigned: List[BoardLocation] =\
            [l for l in self.locations if assignment[l] == 0 and self.preset[l] == 0]

        first: BoardLocation = unassigned[0]
        if fill_random:
            np.random.shuffle(self.domain)
        for value in self.domain:
            local_assignment: np.array = assignment.copy()
            local_assignment[first]: int = value
            if self.consistent(local_assignment + self.preset):
                result: np.array = self.solve(assignment=local_assignment)
                if result is not None:
                    return result
        return None

    def consistent(self, assignment: np.array) -> bool:
        # test for equality to preset:
        for location in self.locations:
            if self.preset[location] == 0 or assignment[location] == 0:
                continue
            elif assignment[location] != self.preset[location]:
                return False
        # test rows on board
        for row in assignment:
            if not self._test_unique(row):
                return False
        # test cols on board.T
        for column in assignment.T:
            if not self._test_unique(column):
                return False
        # test the subgrids
        s: int = int(sqrt(self.size)) # subgrid size
        for r in range(s):
            for c in range(s):
                sub_grid: np.array = assignment[s*r:s*(r+1), s*c:s*(c+1)]
                if not self._test_unique(sub_grid.flatten()):
                    return False
        if self.graphics:
            self.graphics.update_cells(assignment)
        return True

    @staticmethod
    def _test_unique(array: np.array) -> bool:
        # remove zeros from the array
        array = list(filter(lambda x: x != 0, array))
        value_counts = np.unique(array, return_counts=True)[1]
        if len(value_counts) == 0:
            return True  # empty array
        elif len(set(value_counts)) > 1 or value_counts[0] > 1:
            return False
        return True


if __name__ == '__main__':
    # create a blank sudoku board:
    # s.graphics.update_cells(s.assignment)
    # cProfile.run('sol = s.solve()')
    s = Sudoku(size=9, graphics=True, preset=None)
    s.generate(0.2)
    print(s.preset)
    sol = s.solve()
    print(sol + s.preset)
    s.graphics.stay_open()

