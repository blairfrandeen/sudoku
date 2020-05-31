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


def dict_to_array(dictionary: Dict[BoardLocation, int], size: int) -> np.array:
    array = np.zeros((size, size), dtype=np.int8)
    for key in dictionary:
        array[key] = dictionary[key]
    return array


class Sudoku:
    def __init__(self, size: Optional[int] = 9,
                 assignment: Optional[np.array] = None,
                 graphics: Optional = False):
        if sqrt(size) % 1 != 0:
            raise ValueError('Size of Sudoku board must be a perfect square!')
        self.size: int = size
        self.domain = list(range(1, self.size + 1))
        if assignment is None:
            self.assignment = np.zeros((size, size), dtype=np.int8)
        elif type(assignment) is dict:
            self.assignment = dict_to_array(assignment, self.size)
        self.locations: List[BoardLocation] = [BoardLocation(row, column)
                                               for row, r in enumerate(self.assignment)
                                               for column, _ in enumerate(r)]
        self.graphics = SudokuGraphics(self) if graphics else None

    def __len__(self):
        # return the number of locations in the numpy array that are not zero
        return len([cell for row in self.assignment for cell in row if cell != 0])

    def __contains__(self, item: BoardLocation):
        # return whether the item (location) is zero
        if item not in self.locations:
            raise IndexError(f'Looking for out of bounds {item} in Sudoku board')
        return self.assignment[item] != 0

    def __repr__(self):
        return repr(self.assignment)

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

        self.assignment = Sudoku(size=self.size, assignment=csp.backtracking_search(graphics=self.graphics))
        if self.graphics:
            self.graphics.stay_open()
        else:
            print(self.assignment)

    # TODO: Make this into a class method. It can then be called as
    #   S = Sudoku.fill_random(0.5) to create a random puzzle
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

    def satisfied(self, assignment: np.array) -> bool:
        # first round through backtracking_search will try to
        # pass a dict with the first value. This corrects
        # it to be an empty sudoku board
        if type(assignment) is dict:
            assignment = dict_to_array(assignment, self.size)

        # test rows on board
        for row in assignment:
            if not self._test_unique(row):
                return False
        # test cols on board.T
        for column in assignment.T:
            if not self._test_unique(column):
                return False
        # test the subgrids
        s = int(sqrt(self.size)) # subgrid size
        for r in range(s):
            for c in range(s):
                sub_grid: np.array = assignment[s*r:s*(r+1), s*c:s*(c+1)]
                if not self._test_unique(sub_grid.flatten()):
                    return False
        return True

    @staticmethod
    def _test_unique(array: np.array):
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
    # s.g.stay_open()

