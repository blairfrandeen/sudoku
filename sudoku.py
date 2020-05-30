from csp import CSP, Constraint
from math import sqrt
from typing import NamedTuple, List, Dict, Optional
from sudoku_graphics import SudokuGraphics
import numpy as np
# Note: numpy does not fully support type annotations.
# There seems to have been some discusion about it on GitHubb
# Could be something cool to contribute to..........


class BoardLocation(NamedTuple):
    row: int
    column: int

# variables: locations on the sudoku board (81 of them)
# domain: each variable can have a value from 1-9
# constraints:
#   1. Numbers on each row must be unique
#   2. Numbers in each column must be unique
#   3. Numbers in each 3x3 subgrid must be unique

# I need to decide if I am going to solve this using the methods in the book
# or using NumPy. I am going to start by using the methods in the book.
# Using numpy will not work with the generic csp, since the geneic
# csp uses assignments as dictionaries of values and domains, whereas
# numpy could have the assignment be an entire numpy array.

# TODO: Rewrite the CSP framework within this module so that this
#   works fully with numpy. Write some unit tests and profile
#   code to get a comparison of how long things actually take.


class Sudoku:
    # TODO: See if I can clean up this class definition and stay
    #   within the CSP framework. I currently have self.grid (numpy array)
    #   self.locations(list of BoardLocations), and self._assignment
    #   (format for passing info to backtracking search and constraints)
    def __init__(self, size: Optional[int] = 9,
                 values: Optional[Dict[BoardLocation, int]] = None,
                 graphics: Optional = False):
        if sqrt(size) % 1 != 0:
            raise ValueError('Size of Sudoku board must be a perfect square!')
        self.size: int = size
        self.grid = np.zeros((size, size), dtype=int)
        self.locations: List = []
        self.domain = list(range(1, self.size + 1))
        if values:
            for location in values:
                self.grid[location.row, location.column] = values[location]
                self.locations.append(location)
        else:
            for row in range(0, self.size):
                for column in range(0, self.size):
                    self.locations.append(BoardLocation(row, column))
        self.g = SudokuGraphics(self) if graphics else None

    @property
    def _assignment(self) -> Dict[BoardLocation, int]:
        assignment: Dict[BoardLocation, int] = dict()
        for location in self.locations:
            assignment[location] = self.grid[location.row, location.column]
        return assignment

    def __repr__(self):
        return repr(self.grid)

    def solve(self, shuffle_variables=False, shuffle_domains=True):
        # variables: List[BoardLocation] = self.locations
        if shuffle_variables:
            np.random.shuffle(self.locations)
        domains: Dict[BoardLocation, List] = {}
        for variable in self.locations:
            if shuffle_domains:
                np.random.shuffle(self.domain)
            domains[variable] = self.domain

        csp: CSP[BoardLocation, int] = CSP(self.locations, domains)

        # Time to make some constraints
        csp.add_constraint(SudokuConstraint(self.locations, self.size))
        # csp.add_constraint(SudokuPresetConstraint(self._assignment))
        # TODO: Figure out why the second constraint doesn't always seem
        #   to stick. Hypothesis is that the first constraint cannot
        #   be satisfied because the random inputs are currently not
        #   valid (they do not themselves do a backtracking search)

        solution = Sudoku(values=csp.backtracking_search(graphics=self.g))
        if self.g:
            self.g.stay_open()
        else:
            print(solution)

    def fill_random(self, percent_to_fill: float):
        # TODO: Make this a version of csp.backtracking_search.
        #   I think that this can be done simply with two steps:
        #   First, use np.shuffle to shuffle the inputs of backtracking
        #   Search by shuffling self.locations when I pass it into
        #   A new CSP. Second, use only a subset of the inputs
        #   so that the board is not completely filled up.
        # integer number of cells to fill
        n_cells_to_fill: int = int(percent_to_fill * (self.size ** 2))
        # integer index of the grid
        grid_indices = list(range(0, self.size ** 2))
        # shuffle to randomize, and take the first n_cells_to_fill
        np.random.shuffle(grid_indices)
        indices_to_fill: List[int] = grid_indices[0:n_cells_to_fill]

        constraint = SudokuConstraint(self.locations, self.size)
        print(indices_to_fill)
        print(len(self._assignment))
        for index in indices_to_fill:
            # use integer and modulus division to get index back to row & col
            row, column = index // self.size, index % self.size
            # shuffle the domain
            np.random.shuffle(self.domain)
            # create an iterator for the shuffled domain, and assign the first value
            domain_iter = iter(self.domain)
            self.grid[row, column] = next(domain_iter)
            # verify that the sudoku constraint is satisfied
            #   for the grid. If not, choose a new number
            while not constraint.satisfied(self._assignment):
                try:
                    self.grid[row, column] = next(domain_iter)
                except:
                    self.g.update_cells(self._assignment)
                    print('ERROR!')
                    print(row, column)
                    self.g.stay_open()


class SudokuPresetConstraint(Constraint[BoardLocation, int]):
    def __init__(self, setup: Dict[BoardLocation, int]) -> None:
        super().__init__(list(setup.keys()))
        self.setup = setup

    def satisfied(self, assignment: Dict[BoardLocation, int]):
        for location in assignment:
            # print(location, self.setup[location], assignment[location])
            if assignment[location] == 0:
                return True # ok for cells not assigned
            elif assignment[location] != self.setup[location]:
                print('got here')
                return False
        return True


class SudokuConstraint(Constraint[BoardLocation, int]):
    def __init__(self, board_locations, size):
        super().__init__(board_locations) # variables
        self.size = size
        # self.board = np.zeros((self.size, self.size), dtype=int)
        # TODO: Figure out why I can't make an empty array once
        #   Using the code above in satisfied() produces an empty matrix
        #   as the solution.

    def satisfied(self, assignment: Dict[BoardLocation, int]) -> bool:
        # TODO: Chance data type to int8. Consider running
        #   a comparison to see if it speeds things up
        board = np.zeros((self.size, self.size), dtype=int)
        # fill up the array
        if assignment is not None:
            for location in assignment:
                board[location.row, location.column] = assignment[location]

        # test rows on board
        for row in board:
            if not self.test_unique(row):
                return False
        # test cols on board.T
        for column in board.T:
            if not self.test_unique(column):
                return False
        # test the subgrids
        s = int(sqrt(self.size)) # subgrid size
        for r in range(s):
            for c in range(s):
                sub_grid = board[s*r:s*(r+1), s*c:s*(c+1)]
                if not self.test_unique(sub_grid.flatten()):
                    return False
        return True

    # TODO: Determine if this needs to be nested in the satisfied()
    #   constraint, left as a static method, or moved outside
    #   of this class
    @staticmethod
    def test_unique(array: np.array):
        # remove zeros from the array
        array = list(filter(lambda x: x != 0, array))
        value_counts = np.unique(array, return_counts=True)[1]
        if len(value_counts) == 0:
            return True # empty array
        elif len(set(value_counts)) > 1 or value_counts[0] > 1:
            return False
        else:
            return True


if __name__ == '__main__':
    # create a blank sudoku board:
    s = Sudoku(size=9, graphics=True)

    # fill it with pre-defined numbers
    # s.fill_random(0.8)
    # solve it
    s.solve()
    s.g.stay_open()
    print(s)

