
class SimulatorDisplay(object):

    def __init__(self):
        self.char_grid = [[x for x in '        '], 
                          [x for x in '        ']]
        self.cursor = (0, 0)

    def create_char(self, *args):
        pass

    def blink(self, value):
        pass

    def show_cursor(self, value):
        pass

    def set_cursor(self, col, row):
        pass

    def write8(self, char, char_mode=False):
        print "Writing..."
        print char

    def clear(self):
        pass
