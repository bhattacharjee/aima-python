#!/usr/bin/env python3
import os,sys,inspect, random, collections
import time

# Is curses available or not?
g_curses_available = True
g_suppress_state_printing = False
g_state_print_same_place_loop_count = 6
g_state_refresh_sleep = 0
g_self_crossing_not_allowed = True

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
    MAX_AGENT_HISTORY = 10
    def __init__(self, rows, cols, restore_power=True):
        global g_curses_available
        self.stored_power = None
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.is_stuck = False
        self.thedoor = None
        self.restore_power = restore_power # Powers once taken should reappear
        self.agent_history = collections.deque()
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

    def is_done(self):
        if self.is_stuck:
            return True
        return super().is_done()

    def execute_action(self, agent, action):
        global g_self_crossing_not_allowed
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
        if len(self.agent_history) > 0 and \
                (row, col) != self.agent_history[len(self.agent_history) - 1]:
            self.agent_history.append((row, col))
            if (len(self.agent_history) > TwoDEnvironment.MAX_AGENT_HISTORY):
                while(len(self.agent_history) > TwoDEnvironment.MAX_AGENT_HISTORY):
                    self.agent_history.popleft()
        assert((newrow, newcol) not in self.agent_history or not g_self_crossing_not_allowed)
        old_object = self.matrix[newrow][newcol]
        self.matrix[newrow][newcol] = agent
        if (None != old_object and isinstance(old_object, Power)):
            agent.num_power += old_object.get_power_value()
            if (not self.restore_power):
                self.things.remove(old_object)
        agent.set_location(newrow, newcol)
        agent.num_moves += 1
        if None != self.stored_power and True == self.restore_power:
            if self.stored_power not in self.things:
                self.add_thing(self.stored_power, [row, col])
            else:
                self.stored_power.location = [row, col]
            self.stored_power = None
        if True == self.restore_power and old_object != None and isinstance(old_object, Power):
            self.stored_power = old_object

    # "dimensions" : dimensions of board
    # "location" : location of agent
    # "things" : list of things
    # "goal_direction": direction of goal [dx, dy] dx/dy can be negative
    # "agent_history": list of past locations of the agent [(r,c), (r,c), ..]
    def percept(self, agent):
        percept = {}
        thedoor = None
        x, y = agent.get_location()
        percept["dimensions"] = [self.rows, self.cols]
        percept["location"] = [x, y]
        percept["things"] = []
        percept["agent_history"] = []
        [percept["agent_history"].append(l) for l in self.agent_history]
        for thing in self.things:
            percept["things"].append(thing)
            if (isinstance(thing, Door)):
                thedoor = thing
        assert(None != thedoor)
        dx, dy = thedoor.get_location()
        assert(None != dx and None != dy)
        percept["goal_direction"] = [dx - x, dy - y]
        return percept

    def add_thing(self, thing, location):
        row = location[0]
        col = location[1]
        super().add_thing(thing, location)
        self.matrix[row][col] = thing
        if (True == isinstance(thing, Agent)):
            x, y = thing.get_location()
            self.agent_history.append((x, y))

    def get_print_matrix(self):
        theAgent = None
        m = [[' ' for i in range(self.cols + 2)] for j in range(self.rows + 2)]
        for i in range(self.cols +2):
            m[0][i] = '#'
            m[self.rows+1][i] = '#'
        for i in range(self.rows):
            m[i+1][0] = '#'
            m[i+1][self.cols+1] = '#'
        for thing in self.things:
            if isinstance(thing, TwoDThing) or isinstance(thing, TwoDAgent):
                x, y = thing.get_location()
                c = thing.get_display()
                m[x+1][y+1] = c
                if (isinstance(thing, TwoDAgent)):
                    theAgent = thing
        for location in self.agent_history:
            x = location[0]
            y = location[1]
            m[x+1][y+1] = '*'
        x, y = theAgent.get_location()
        m[x+1][y+1] = theAgent.get_display()
        if (True == self.is_stuck):
            for i, c in enumerate(list("S  T  U  C  K !!!")):
                m[0][i] = c
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
        global g_suppress_state_printing
        if g_suppress_state_printing:
            return
        global g_curses_available
        if g_curses_available:
            return self.print_state_curses()
        else:
            return self.print_state_text()

class TwoDMaze(TwoDEnvironment):
    NUM_NULL_MOVES_TILL_STUCK = 2
    def __init__(self, mazeString=str):
        mazeString = [list(x.strip()) for x in mazeString.split("\n") if x]
        self.stuck_detect = collections.deque()
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

    def is_deque_stuck(self, d):
        if (0 == len(d) or 1 == len(d) or None == d):
            return False
        for e in d:
            if (None != e):
                return False
        return True

    # There is a need to detect that the agent is stuck, hence
    # this function was copied over from the parent class, and a bit
    # of code added to check that there are no valid moves left
    def step(self):
        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.alive:
                    act = agent.program(self.percept(agent))
                    if (None == act or (not isinstance(act, list) and not isinstance(act, tuple))):
                        self.stuck_detect.append(act)
                    else:
                        [self.stuck_detect.append(a) for a in act]
                    actions.append(act)
                else:
                    actions.append("")
            for (agent, action) in zip(self.agents, actions):
                self.execute_action(agent, action)
            self.exogenous_change()
            while (len(self.stuck_detect) > TwoDMaze.NUM_NULL_MOVES_TILL_STUCK):
                self.stuck_detect.popleft()
            self.is_stuck = self.is_deque_stuck(self.stuck_detect)

    def got_stuck(self):
        return self.is_stuck

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
    def get_candidate_positions(ag_location, mt_dimensions, history):
        global g_self_crossing_not_allowed
        row = ag_location[0]
        col = ag_location[1]
        total_rows = mt_dimensions[0]
        total_cols = mt_dimensions[1]
        temp = [ (row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        candidates = []
        assert(None != history)
        for row, col in temp:
            if (row >= 0 and row < total_rows and col >= 0 and col < total_cols):
                if (0 == len(history) or False == g_self_crossing_not_allowed
                        or ((row, col) not in history)):
                    candidates.append((row, col))
        return candidates
 
    def program(percepts):
        nonlocal matrix
        rowCandidate = colCandidate = -1
        mt_dimensions = percepts["dimensions"]
        ag_location = percepts["location"]
        things = percepts["things"]
        history = percepts["agent_history"]

        # First recreate the matrix
        matrix = [[None for i in range(mt_dimensions[1])] for j in range(mt_dimensions[0])]
        for thing in things:
            row = thing.location[0]
            col = thing.location[1]
            matrix[row][col] = thing

        # Get the candidate positions
        candidate_positions = get_candidate_positions(ag_location, mt_dimensions, history)
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

# The goal driven agent program tries to go greedily towards a goal
# It just sees which direction the goal is and proceeds along that
# This algorithm suffers from the disadvantage that the agent might get
# stuck in cul-de-sacs.
# The easiest way to fix this problem was that if it ever got stuck,
# then the agent should make random moves till it reaches a node it has
# not visited previously.
# Once it visits a node that it hasn't visited previously, then it resumes
# the goal-driven approach once again
def GoalDrivenAgentProgram():
    # Gaol driven greedy search may get stuck. If it does
    # We need to randomly go to a new node which we haven't visited earlier
    doing_random = False
    visited_matrix = None
    move_table = {
        (-1, 0): "moveUp",
        (1, 0): "moveDown",
        (0, -1): "moveLeft",
        (0, 1): "moveRight"
    }
    backward_move_table = {
        "moveUp": (-1, 0),
        "moveDown": (1, 0),
        "moveLeft": (0, -1),
        "moveRight": (0, 1)
    }
    def get_matrix(rows, cols, things):
        matrix = [[' ' for i in range(cols)] for j in range(rows)]
        for thing in things:
            if not isinstance(thing, Agent):
                row = thing.location[0]
                col = thing.location[1]
                if (isinstance(thing, Wall)):
                    matrix[row][col] = '#'
                if (isinstance(thing, Door)):
                    matrix[row][col] = 'D'
        return matrix

    # Helper routine to get the candidate moves, it doesn't care
    # whether the move is blocked by a wall or not 
    # However, it checks whether the move is out of bounds
    # or not
    def get_candidate_positions(ag_location, mt_dimensions, history=None):
        global g_self_crossing_not_allowed
        row = ag_location[0]
        col = ag_location[1]
        total_rows = mt_dimensions[0]
        total_cols = mt_dimensions[1]
        assert(None != history)
        temp = [ (row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        candidates = []
        for row, col in temp:
            if (row >= 0 and row < total_rows and col >= 0 and col < total_cols):
                if (0 == len(history) or False == g_self_crossing_not_allowed \
                        or ((row, col) not in history)):
                    candidates.append((row, col))
        return candidates

    def get_random_move(matrix, a_loc, history):
        assert(None != matrix and isinstance(matrix, list) and isinstance(matrix[0], list))
        mt_dim = [len(matrix), len(matrix[0])]
        rowCandidate = colCandidate = -1
        candidate_positions = get_candidate_positions(a_loc, mt_dim, history)
        while 0 != len(candidate_positions):
            i = random.randrange(0, len(candidate_positions))
            x, y = candidate_positions[i]
            if '#' != matrix[x][y]:
                rowCandidate = x
                colCandidate = y
                break
            else:
                del candidate_positions[i]
        # Convert position to move (eg. [0, 0] -> MoveUp)
        if -1 != rowCandidate and -1 != colCandidate:
            row_move = rowCandidate - a_loc[0]
            col_move = colCandidate - a_loc[1]
            move = move_table[(row_move, col_move)]
            assert(None != move)
            return move
        assert(True) # Should never reach here
        return None


    def get_goal_directed_new_location(matrix, m_rows, m_cols, a_row, a_col, dx, dy, history):
        # Sometimes, try moving rows first, at other times, try moving columns first
        assert(None != history)
        if random.choice([True, False]):
            if (0 != dx):
                newrow = a_row + dx
                newcol = a_col
                if (newrow >= 0 and newrow < m_rows):
                    if (matrix[newrow][newcol] != '#'\
                            and (newrow, newcol) not in history):
                        return newrow, newcol
            if (0 != dy):
                newrow = a_row
                newcol = a_col + dy
                if (newcol >= 0 and newcol < m_cols):
                    if (matrix[newrow][newcol] != '#' \
                            and (newrow, newcol) not in history):
                        return newrow, newcol
        else:
            if (0 != dy):
                newrow = a_row
                newcol = a_col + dy
                if (newcol >= 0 and newcol < m_cols):
                    if (matrix[newrow][newcol] != '#' \
                            and (newrow, newcol) not in history):
                        return newrow, newcol
            if (0 != dx):
                newrow = a_row + dx
                newcol = a_col
                if (newrow >= 0 and newrow < m_rows):
                    if (matrix[newrow][newcol] != '#' \
                            and (newrow, newcol) not in history):
                        return newrow, newcol
        return -1, -1

    def get_action_string(n_r, n_c, o_r, o_c):
        nonlocal move_table
        dx = n_r - o_r
        dy = n_c - o_c
        assert(None != move_table[(dx, dy)])
        return move_table[(dx, dy)]

    # Validate that the next move is not out of bounds
    def validate_move(move, a_row, a_col, rows, cols):
        nr, nc = get_updated_row_col(a_row, a_col, move)
        if (nr < 0 or nc < 0):
            return False
        if (nr >= rows or nc >= cols):
            return False
        return True

    # "dimensions" : dimensions of board
    # "location" : location of agent
    # "things" : list of things
    # "goal_direction": direction of goal [dx, dy] dx/dy can be negative
    def program(percepts):
        nonlocal visited_matrix
        nonlocal doing_random
        rows = percepts["dimensions"][0]
        cols = percepts["dimensions"][1]
        a_row = percepts["location"][0]
        a_col = percepts["location"][1]
        dx = percepts["goal_direction"][0]
        dy = percepts["goal_direction"][1]
        history = percepts["agent_history"]
        assert(None != history)
        dx = dx if 0 == dx else dx // abs(dx)
        dy = dy if 0 == dy else dy // abs(dy)
        assert(a_row != None and a_col != None and rows != None and cols != None)
        assert(-1 != a_row and -1 != a_col and -1 != rows and -1 != cols)
        matrix = get_matrix(rows, cols, percepts["things"])
        if (None == visited_matrix):
            visited_matrix = [[False for i in range(cols)] for j in range(rows)]
        if (not visited_matrix[a_row][a_col]):
            doing_random = False
        visited_matrix[a_row][a_col] = True
        if (not doing_random):
            nr, nc = get_goal_directed_new_location(matrix, rows, cols, a_row, a_col, dx, dy, history)
            if (-1 != nr and -1 != nc):
                move = get_action_string(nr, nc, a_row, a_col)
                assert(None == move or validate_move(move, a_row, a_col, rows, cols))
                return move
            else:
                doing_random = True
        assert(True == doing_random)
        move = get_random_move(matrix, [a_row, a_col], history)
        assert(None == move or validate_move(move, a_row, a_col, rows, cols))
        return move
    
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

mediumMaze= """
###########################################
#     #                #              #   #
#o    #        ####    ########       #   #
#     #####       #    #              #   #
#         #       ###     #####  ######   #
#   #######  ####   #     #   #  #      ###
#   #  #           #####    #    #  # x   #
#   #  #              #     #       #     #
#      #    ######    #         #         #
#      #              #         #  ########
#     ##     ##########         #         #
#                         ############    #
#   ##             #            #         #
#    #########     ########               #
#    #             #           #########  #
#                                         #
###########################################"""

# Maze with fewer cul-de-sacs
mediumMaze2= """
###########################################
#                                         #
#     #        ####    ########       #   #
#         #       #    #              #   #
#         #       ###     #####  ######   #
#   #######  ####         #   #  #        #
#   #  #              ##    #    #  # x   #
#   #  #              #     #       #     #
#      #    ######    #         #         #
#      #              #         #  ########
#     ##     ##########         #         #
#                         ############    #
#   ##             #            #         #
#    #########     ########               #
#    #             #           #########  #
#o                                        #
###########################################"""

largeMaze = """
####################################################################################################################
#                                                                                                                  #
#                   #                  ############################            #        ####    ########       #   #
#                   #                                                              #       #    #              #   #
#                   #############################                                  #       ###     #####  ######   #
#                                 #                                          #######  ####         #   #  #        #
#                                 #                                          #  #              ##    #    #  # x   #
#                                 #          ###########################     #  #              #     #       #     #
#           ################      #                                             #    ######    #         #         #
#                                 #                                             #              #         #  ########
#                    #                                                         ##     ##########         #         #
#                    #                                            #                                ############    #
#                    #     #####################################  #          ##             #            #         #
#                    #                                            #           #########     ########               #
#                    #                                            #           #             #           #########  #
#                    #                                            #  ########                    #                 #
#                    #          #           #                     #                              #                 #
#                    #          #           #                     #             #          #     #                 #
#                    #          #           #                     #             #          #                       #
#                    #          #           #                     #             #          #           #           #
#                               #           #                     #   ########  #          #           #           #
#     #                                                           #             #          #           #           #
#     #                                                           #             #          #           #           #
#     #           ######################################          #             #          #    ###############    #
#     #                                                           #             #          #           #           #
#     #                                                           #             #          #           #           #
#     #                              #                            #  #########  #          #           #           #
#     #                              #                            #             #          #           #           #
#     #                              #                            #             #          #                       #
#     #                              #                            #             #          #        #  ##          #
#     #                              #                            #             #          #        #   #          #
#     #                              #                            #             #          #            #####      #
#     #                                                                         #          #                       #
#     #  ###################################       ########################                #                       #
#     #                                                                                    #   #############       #
#     #                                                                   #                #          #            #
#     #                      #                                            #                #          #            #
#     #                      #        #############################       #                           #            #
#     #                      #                                            #                           #            #
#     #                      #                         #                  #                           #            #
#     #                      #                         #                  #                           #            #
#     #                      #                         #                  #                           #            #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#                            #                                            #                                        #
#o                                                                                                                 #
#                                                                                                                  #
####################################################################################################################"""
def RunAgentAlgorithm(program, mazeString: str):
    global g_state_print_same_place_loop_count
    global g_state_refresh_sleep
    env = TwoDMaze(mazeString)
    agent = TwoDAgent(program)
    ag_x, ag_y = get_agent_location_from_maze_string(mazeString)
    assert(-1 != ag_x and -1 != ag_y)
    env.add_thing(agent, (ag_x,ag_y))
    while not env.is_done():
        env.step()
        for i in range(g_state_print_same_place_loop_count):
            env.print_state()
            if (0 != g_state_refresh_sleep):
                time.sleep(g_state_refresh_sleep)
    time.sleep(1)
    stuck = env.got_stuck()
    del env
    if (stuck):
        print("Got Stuck, didn't complete..")
    print(f"Num_Moves: = {agent.num_moves} Power_Points = {agent.num_power}")


def main():
    #RunAgentAlgorithm(SimpleReflexProgram(), smallMaze)
    #RunAgentAlgorithm(GoalDrivenAgentProgram(), smallMaze)
    RunAgentAlgorithm(SimpleReflexProgram(), smallMazeWithPower)
    RunAgentAlgorithm(GoalDrivenAgentProgram(), smallMazeWithPower)
    #RunAgentAlgorithm(SimpleReflexProgram(), mediumMaze2)
    #RunAgentAlgorithm(GoalDrivenAgentProgram(), mediumMaze2)
    #RunAgentAlgorithm(SimpleReflexProgram(), largeMaze)
    #RunAgentAlgorithm(GoalDrivenAgentProgram(), largeMaze)

if "__main__" == __name__:
    main()
