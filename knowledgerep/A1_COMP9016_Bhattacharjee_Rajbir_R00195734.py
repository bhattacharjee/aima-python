#!/usr/bin/env python3
import os,sys,inspect
import time

# Is curses available or not?
g_curses_available = True

# Import the AIMA libraries from the parent directory
try:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from agents import Environment, Thing
except:
    print("Could not import from parent folder... Exiting")
    sys.exit(1)

# Curses is only available in linux, in windows, continue without it
try:
    import curses
except:
    g_curses_available = False
    print("Curses is not available, continuing without it...")

class TwoDThing(Thing):
    def __init__(self, x = 0, y = 0, display='T'):
        super().__init__()
        self.x = x
        self.y = y
        self.display = display

    def get_location(self):
        return (self.x, self.y)

    def get_display(self):
        return self.display


class Wall(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, '#')

class Door(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, 'D')

# Create our own 2D environment
class TwoDEnvironment(Environment):
    def __init__(self, rows, cols):
        global g_curses_available
        super().__init__()
        self.rows = rows
        self.cols = cols
        if g_curses_available:
            self.window = curses.initscr()
    
    def __del__(self):
        global g_curses_available
        if g_curses_available:
            curses.endwin()

    # If curses is not supported, print the maze in text format
    def print_state_text(self):
        print("TODO: code print_state_text")

    # Use ncurses to print the maze
    def print_state_curses(self):
        for i in range(self.cols + 2):
            self.window.addstr(0, i, '#')
            self.window.addstr(self.rows+1, i, '#')
        for i in range(self.rows):
            self.window.addstr(i+1, 0, '#')
            self.window.addstr(i+1, self.cols + 1, '#')
        for i in range(self.rows):
            for j in range(self.cols):
                self.window.addstr(i+1, j+1, ' ')
        for thing in self.things:
            if isinstance(thing, TwoDThing):
                x, y = thing.get_location()
                c = thing.get_display()
                self.window.addstr(x+1, y+1, c)
        self.window.refresh()

    def print_state(self):
        global g_curses_available
        if g_curses_available:
            return self.print_state_curses()
        else:
            return self.print_state_text()

class TwoDMaze(TwoDEnvironment):
    def __init__(self, mazeString=str):
        mazeString = [list(x.strip()) for x in mazeString.split("\n") if x]
        rows = len(mazeString)
        cols = len(mazeString[0])
        super().__init__(rows, cols)
        for i in range(rows):
            for j in range(cols):
                if '#' == mazeString[i][j]:
                    wall = Wall(i, j)
                    self.add_thing(wall)
                if 'x' == mazeString[i][j]:
                    door = Door(i, j)
                    self.add_thing(door)


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
