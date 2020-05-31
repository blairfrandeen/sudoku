from graphics import GraphWin, Rectangle, Point, Line, Text
from math import sqrt
# TODO: Be consistent with rows & columns
# TODO: Make bold numbers for permanent assignments
# TODO: Graduate from graphics.py to using TKinter directly
GRID_SIZE = 50
# Because everything deserves dark mode :)
BACKGROUND_COLOR = 'gray22'
TEXT_COLOR = 'gray84'
GRID_COLOR_MAJOR = 'gold'
GRID_WIDTH_MAJOR = GRID_SIZE / 10
GRID_COLOR_MINOR = 'light goldenrod'
TEXT_COLORS = ['red', 'orange red', 'tomato', 'light coral',
               'coral', 'dark orange', 'orange', 'light salmon',
               'goldenrod2', 'gold2', 'gold', 'yellow2',
               'green yellow', 'yellow green', 'lawn green', 'cyan',
               'dodger blue', 'cornflower blue', 'CadetBlue1',
               'gray84']
# TEXT_COLORS = ({0: 'lawn green',
#                 1: 'medium spring green',
#                 2: 'spring green',
#                 3: 'pale green',
#                 4: 'gray84'})


class SudokuCell(Rectangle):
    def __init__(self, location, value) -> None:
        self.location = location
        self.value: int = value
        self.age: int = 0
        top_left: Point = Point(self.location.row * GRID_SIZE,
                                self.location.column * GRID_SIZE)
        bottom_right: Point = Point(top_left.x + GRID_SIZE,
                                    top_left.y + GRID_SIZE)
        center: Point = Point((top_left.x + bottom_right.x) / 2,
                       (top_left.y + bottom_right.y) / 2)
        super().__init__(top_left, bottom_right)
        self.setFill(BACKGROUND_COLOR)
        self.setOutline(GRID_COLOR_MINOR)
        self.text = Text(center, str(self.value))
        self.text.setSize(GRID_SIZE//2)
        self.text.setTextColor(TEXT_COLOR)


class SudokuGraphics:
    # TODO: Make type hints work for modules I'm not importing
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.window_size: int = GRID_SIZE * self.puzzle.size
        self.window: GraphWin = GraphWin("Sudoku", self.window_size,
                                         self.window_size, autoflush=False)
        self.assignment = self.puzzle.assignment
        self.locations = self.puzzle.locations
        self.cells = dict()
        self.num_colors = len(TEXT_COLORS)

        # grid is np array
        # make cell for each element in the grid
        # and draw them
        for location in self.locations:
            self.cells[location] =\
                SudokuCell(location, self.assignment[location.row, location.column])

        self.grid_lines = []
        subgrid_px = sqrt(self.puzzle.size) * GRID_SIZE
        self.subgrid_size = int(sqrt(self.puzzle.size))
        # TODO: Be consistent with 'size' and 'px'
        for n in range(1, self.subgrid_size):
            self.grid_lines.append(
                Line(Point(0, subgrid_px * n), Point(self.window_size, subgrid_px * n)))
            self.grid_lines.append(
                Line(Point(subgrid_px * n, 0), Point(subgrid_px * n, self.window_size)))

        for line in self.grid_lines:
            line.setWidth(GRID_WIDTH_MAJOR)
            line.setOutline(GRID_COLOR_MAJOR)
        self.draw_background()
        self.fill_cells()

    def update_cells(self, new_assignment):
        # new assignment is dict of locations and values

        for location in new_assignment:
            if new_assignment[location] == 0:
                continue
            self.cells[location].text.undraw()
            if new_assignment[location] != self.cells[location].value:
                self.cells[location].age = 0
                self.cells[location].value = new_assignment[location]
                self.cells[location].text.setText(str(new_assignment[location]))
            elif self.cells[location].age < len(TEXT_COLORS) - 1:
                self.cells[location].age += 1
            else:
                self.cells[location].age = len(TEXT_COLORS) - 1
            self.cells[location].text.setFill(TEXT_COLORS[self.cells[location].age])
            self.cells[location].text.draw(self.window)

        self.window.update()

    def draw_background(self):
        for cell in self.cells:
            self.cells[cell].draw(self.window)
        # draw extra thick lines for subgrids
        for line in self.grid_lines:
            line.draw(self.window)
        self.window.update()

    def fill_cells(self):
        for cell in self.cells:
            if self.cells[cell].value != 0:
                self.cells[cell].text.draw(self.window)
        self.window.update()

    def stay_open(self):
        while True:
            print('Press "q" to close graphics window.')
            graphics_exit = self.window.getKey()
            if graphics_exit == 'q':
                self.window.close()
                break


if __name__ == '__main__':

    pass
