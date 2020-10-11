#!/usr/bin/env python3
import os,sys,inspect, random
import time

# Is curses available or not?
g_curses_available = True

# Import the AIMA libraries from the parent directory
try:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from agents import Environment, Thing, Direction, Agent
except:
    print("Could not import from parent folder... Exiting")
    sys.exit(1)

# Curses is only available in linux, in windows, continue without it
try:
    import curses
except:
    g_curses_available = False
    print("Curses is not available, continuing without it...")

#g_curses_available = False

class TwoDThing(Thing):
    def __init__(self, x = 0, y = 0, display='T'):
        super().__init__()
        self.location = [x, y]
        self.display = display

    def get_location(self):
        return (self.location[0], self.location[1])

    def set_location(self, location = []):
        self.location = location

    def get_display(self):
        return self.display

class Power(TwoDThing):
    def __init__(self, x, y):
        self.power_value = -1
        super().__init__(x, y, 'o')

    def set_power_value(self, i: int):
        self.power_value = i

    def get_power_value(self):
        assert(-1 != self.power_value)
        return self.power_value

    def get_display(self):
        return str(self.power_value)

class Wall(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, '#')

class Door(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, 'D')

def get_updated_row_col(x, y, action):
    row = x
    col = y
    if "moveUp" == action:
        row -= 1
    elif "moveDown" == action:
        row += 1
    elif "moveLeft" == action:
        col -= 1
    elif "moveRight" == action:
        col += 1
    else:
        row = col = -1
    return row, col

# Create our own 2D environment
class TwoDEnvironment(Environment):
    def __init__(self, rows, cols, restore_power=False):
        global g_curses_available
        self.stored_power = None
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.thedoor = None
        self.restore_power = restore_power # Powers once taken should reappear
        #self.matrix = [[None] * cols] * rows
        self.matrix = [[None for i in range(cols)] for j in range(rows)]
        if g_curses_available:
            self.window = curses.initscr()

    def is_done(self):
        dr_row = dr_col = -1
        ag_row, ag_col = self.agents[0].get_location()
        assert(None != ag_row and None != ag_col)
        if None == self.thedoor:
            for thing in self.things:
                if (isinstance(thing, Door)):
                    self.thedoor = thing
        assert(None != self.thedoor)
        dr_row, dr_col = self.thedoor.get_location()
        assert(None != dr_row and None != dr_col and -1 != dr_row and -1 != dr_col)
        done = (dr_row == ag_row and dr_col == ag_col)
        return done

    def __del__(self):
        global g_curses_available
        if g_curses_available:
            curses.endwin()


    def execute_action(self, agent, action):
        if None == action:
            return
        row, col = agent.get_location()
        assert(self.matrix[row][col] == agent)
        assert(None != row)
        assert(None != col)
        newrow, newcol = get_updated_row_col(row, col, action)
        assert(-1 != newrow)
        assert(-1 != newcol)
        self.matrix[row][col] = None
        old_object = self.matrix[newrow][newcol]
        self.matrix[newrow][newcol] = agent
        if (None != old_object and isinstance(old_object, Power)):
            agent.num_power += old_object.get_power_value()
            self.things.remove(old_object)
        agent.set_location(newrow, newcol)
        agent.num_moves += 1
        if None != self.stored_power and True == self.restore_power:
            self.add_thing(self.stored_power, [row, col])
            self.stored_power = None
        if True == self.restore_power and old_object != None and isinstance(old_object, Power):
            self.stored_power = old_object
        pass

    def percept(self, agent):
        percept = {}
        x, y = agent.get_location()
        percept["dimensions"] = [self.rows, self.cols]
        percept["location"] = [x, y]
        percept["things"] = []
        for thing in self.things:
            percept["things"].append(thing)
        return percept

    def add_thing(self, thing, location):
        row = location[0]
        col = location[1]
        super().add_thing(thing, location)
        self.matrix[row][col] = thing

    def get_print_matrix(self):
        m = [[' ' for i in range(self.cols + 2)] for j in range(self.rows + 2)]
        for i in range(self.cols +2):
            m[0][i] = '#'
            m[self.rows+1][i] = '#'
        for i in range(self.rows):
            m[i+1][0] = '#'
        for thing in self.things:
            if isinstance(thing, TwoDThing) or isinstance(thing, TwoDAgent):
                x, y = thing.get_location()
                c = thing.get_display()
                m[x+1][y+1] = c
        return m

    # If curses is not supported, print the maze in text format
    def print_state_text(self):
        m = self.get_print_matrix()
        for i in m:
            print(''.join(i))

    # Use ncurses to print the maze
    def print_state_curses(self):
        m = self.get_print_matrix()
        for i, arr in enumerate(m):
            for j, c in enumerate(arr):
                self.window.addstr(i, j, c)
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
                    self.add_thing(wall, [i,j])
                if 'x' == mazeString[i][j]:
                    door = Door(i, j)
                    self.add_thing(door, [i,j])
                if mazeString[i][j] in list('0123456789'):
                    power = Power(i, j)
                    power_value = int(mazeString[i][j])
                    power.set_power_value(power_value)
                    self.add_thing(power, [i, j])

def get_agent_location_from_maze_string(mazeString=str):
    mazeString = [list(x.strip()) for x in mazeString.split("\n") if x]
    rows = len(mazeString)
    cols = len(mazeString[0])
    for i in range(rows):
        for j in range(cols):
            if 'o' == mazeString[i][j]:
                return i, j
    return -1, -1

class TwoDAgent(Agent):
    def __init__(self, program=None):
        self.x = self.y = 1
        self.current_display = 0
        self.direction = Direction.D
        self.num_moves = 0
        self.num_power = 0
        self.cost_incurred = 0
        self.points = 0
        super().__init__(program)

    def set_location(self, x, y):
        self.location = [x, y]

    def get_location(self):
        return self.location[0], self.location[1]
    
    def get_display(self):
        next_item = list("-\\|/")
        next_item = list("-*\\*|*/*")
        self.current_display += 1
        self.current_display = self.current_display  % len(next_item)
        return next_item[self.current_display]

# SimpleReflexProgram randomly chooses a move in any direction
# as long as it doesn't hit a wall
def SimpleReflexProgram():
    # Percepts are of the form
    # {
    #    "dimensions" = [row, col],
    #    "location": [row, col],
    #    "things" : [thing1, thing2, thing3]
    # }
    move_table = {
        (-1, 0): "moveUp",
        (1, 0): "moveDown",
        (0, -1): "moveLeft",
        (0, 1): "moveRight"
    }

    # Recreate the matrix from the percepts
    matrix = None

    # Helper routine to get the candidate moves, it doesn't care
    # whether the move is blocked by a wall or not 
    # However, it checks whether the move is out of bounds
    # or not
    def get_candidate_positions(ag_location, mt_dimensions):
        row = ag_location[0]
        col = ag_location[1]
        total_rows = mt_dimensions[0]
        total_cols = mt_dimensions[1]
        temp = [ (row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        candidates = []
        for row, col in temp:
            if (row >= 0 and row < total_rows and col >= 0 and col < total_cols):
                candidates.append((row, col))
        return candidates
 
    def program(percepts):
        nonlocal matrix
        rowCandidate = colCandidate = -1
        mt_dimensions = percepts["dimensions"]
        ag_location = percepts["location"]
        things = percepts["things"]

        # First recreate the matrix
        matrix = [[None for i in range(mt_dimensions[1])] for j in range(mt_dimensions[0])]
        for thing in things:
            row = thing.location[0]
            col = thing.location[1]
            matrix[row][col] = thing

        # Get the candidate positions
        candidate_positions = get_candidate_positions(ag_location, mt_dimensions)
        # Randomly select a new position
        while 0 != len(candidate_positions):
            i = random.randrange(0, len(candidate_positions))
            x, y = candidate_positions[i]
            if not isinstance(matrix[x][y], Wall):
                rowCandidate = x
                colCandidate = y
                break
            else:
                del candidate_positions[i]
        # Convert position to move (eg. [0, 0] -> MoveUp)
        if -1 != rowCandidate and -1 != colCandidate:
            row_move = rowCandidate - ag_location[0]
            col_move = colCandidate - ag_location[1]
            move = move_table[(row_move, col_move)]
            assert(None != move)
            return move
        return None

    return program



smallMaze = """
##############################
#         #              #   #
#o####    ########       #   #
#    #    #              #   #
#    ###     #####  ######   #
#      #     #   #  #      ###
#     #####    #    #  # x   #
#              #       #     #
##############################"""

smallMazeWithPower = """
##############################
#   3 5   #     1        #   #
#o#### 77 ########   3 5 #   #
# 2  #  8 # 9 9 2 3 ^    # ^ #
#    ###  7  #####  ######   #
#  9   #     #   #  #      ###
#     ##### 6  #  7 #  # x   #
#  3      5    #  8    #     #
##############################"""


def RunReflexAgentRandomAlgorithm(mazeString: str):
    env = TwoDMaze(mazeString)
    agent = TwoDAgent(SimpleReflexProgram())
    ag_x, ag_y = get_agent_location_from_maze_string(mazeString)
    assert(-1 != ag_x and -1 != ag_y)
    env.add_thing(agent, (ag_x,ag_y))
    while not env.is_done():
        env.step()
        for i in range(6):
            env.print_state()
    time.sleep(1)
    del env
    print(f"Num_Moves: = {agent.num_moves} Power_Points = {agent.num_power}")

def main():
    RunReflexAgentRandomAlgorithm(smallMazeWithPower)

if "__main__" == __name__:
    main()