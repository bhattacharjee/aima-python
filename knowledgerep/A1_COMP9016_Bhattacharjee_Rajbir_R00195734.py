import os,sys,inspect
import time

try:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from agents import Environment, Thing
except:
    print("Could not import from parent folder... Exiting")
    sys.exit(1)

try:
    import curses
except:
    print("Could not import ncurses. Please install ncurses... Exiting")
    sys.exit(1)

class TwoDThing(Thing):
    def __init__(self, x = 0, y = 0, display='T'):
        super().__init__()
        self.x = x
        self.y = y
        self.display = display

    def get_location():
        return (self.x, self.y)

    def get_display():
        return self.display



class Wall(Thing):
    pass

# Create our own 2D environment
class TwoDEnvironment(Environment):
    def __init__(self, rows, cols):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.window = curses.initscr()
    
    def __del__(self):
        curses.endwin()

    def print_state(self):
        for i in range(self.cols + 2):
            self.window.addstr(0, i, '#')
            self.window.addstr(self.rows+1, i, '#')
        for i in range(self.rows):
            self.window.addstr(i+1, 0, '#')
            self.window.addstr(i+1, self.cols + 1, '#')
        for i in range(self.rows):
            for j in range(self.cols):
                self.window.addstr(i+1, j+1, 'E')
        self.window.refresh()

class TwoDMaze(TwoDEnvironment):
    def __init__(self, mazeString=str):
        mazeString = [list(x.strip()) for x in mazeString.split("\n") if x]
        rows = len(mazeString)
        cols = len(mazeString[0])
        super().__init__(rows, cols)


def create_2d_environment(maze=str):
    pass

maze = """
##############################
#         #              #   #
# ####    ########       #   #
#    #    #              #   #
#    ###     #####  ######   #
#      #     #   #  #  #   ###
#     #####    #    #  # x   #
#              #       #     #
##############################"""

def main():
    env = TwoDMaze(maze)
    env.print_state()
    time.sleep(2)
    pass

if "__main__" == __name__:
    main()
