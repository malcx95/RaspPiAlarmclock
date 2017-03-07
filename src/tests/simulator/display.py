import os

class SimulatorDisplay(object):

    def __init__(self):
        self.blink_enabled = False
        self.cursor_enabled = False
        self.char_grid = [[x for x in ' ' * 16], 
                          [x for x in ' ' * 16]]
        self.cursor = (0, 0)

    def create_char(self, *args):
        pass

    def blink(self, value):
        self.blink_enabled = value

    def show_cursor(self, value):
        self.cursor_enabled = value

    def set_cursor(self, col, row):
        self.cursor = (col, row)

    def write8(self, char, char_mode=False):
        col, row = self.cursor
        self.char_grid[row][col] = chr(char)

    def clear(self):
        self.char_grid = [[x for x in '        '], 
                          [x for x in '        ']]

