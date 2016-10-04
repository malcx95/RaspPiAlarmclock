import os

class SimulatorDisplay(object):

    def __init__(self):
        #self.window = window
        self.char_grid = [[x for x in ' ' * 16], 
                          [x for x in ' ' * 16]]
        self.cursor = (0, 0)

    def create_char(self, *args):
        pass

    def blink(self, value):
        pass

    def show_cursor(self, value):
        pass

    def set_cursor(self, col, row):
        self.cursor = (col, row)

    def write8(self, char, char_mode=False):
        col, row = self.cursor
        self.char_grid[row][col] = chr(char)
        self._update()

    def clear(self):
        self.char_grid = [[x for x in '        '], 
                          [x for x in '        ']]
        self._update()

    def _update(self):
        os.system("clear")
        print ''.join(x for x in self.char_grid[0])
        print ''.join(x for x in self.char_grid[1])

