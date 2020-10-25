#!/usr/bin/env python3
import os,sys,inspect, random, collections, copy, pickle
import argparse
import time
import logging
logging.basicConfig(level=logging.INFO)

# Is curses available or not?
g_curses_available = True
g_suppress_state_printing = False
g_state_print_same_place_loop_count = 6
g_state_refresh_sleep = 0.05
g_self_crossing_not_allowed = True
g_search_should_consider_history = False
g_pygame_available = False
g_use_pygame = True
g_graphics_sleep_time = 0.01
g_use_tkinter = True
g_tkinter_available = False
g_kb_print_profile_information = True
g_agent_initial_max_length = 8
g_agent_can_grow = True
g_profile_knowledgebase = True
g_perf_run = True
g_override_global_algorithm = -1


if not g_perf_run:
    try:
        import pygame
        g_pygame_available = True
    except:
        g_use_pygame = False
        logging.error("PyGame is not available, running in text mode")

    try:
        import tkinter
        g_tkinter_available = True
    except:
        g_use_tkinter = False
        logging.error("Tkinter is not available, running in text mode")
else:
    g_use_pygame = g_pygame_available = False
    g_use_tkinter = g_tkinter_available = False

# Import the AIMA libraries from the parent directory
try:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir)
    from agents import Environment, Thing, Direction, Agent
    from search import Problem, astar_search, depth_first_graph_search, iterative_deepening_search
    from search import depth_first_tree_search, breadth_first_graph_search, uniform_cost_search
    from search import greedy_best_first_graph_search, recursive_best_first_search
    from logic import *
except:
    logging.error("Could not import from parent folder... Exiting")
    sys.exit(1)

# Curses is only available in linux, in windows, continue without it
try:
    import curses
except:
    g_curses_available = False
    logging.error("Curses is not available, continuing without it...")

tinyMaze = """
#################
#G           #  #
#o####       #  #
# #  #  #  # x  #
#     #         #
#################"""
tinyMazeWithHawk = """
#################
##     #     #  #
#o###H       #  #
# #H##  #  #    #
#            x  #
#################"""
smallHawkTestMaze= """
##############################
# x       #                  #
# ####                       #
#HHHHHHHHHHHHHHHHHHHHHHHHH   #
#    ###     #####  ######   #
#                          ###
#    HHHHHHHHHHHHHHHHHHHHHHHH#
#                           o#
##############################"""
smallHawkTestMaze2= """
##############################
# x       #                  #
# ####                       #
#HHHHHHHHHHHHHHHHHHHHHHHHH   #
#    ###     #####  ######   #
#                          ###
#    H  H  H  H  H  H  H # H #
#                       H   o#
##############################"""
smallMaze = """
##############################
#G        #              #   #
#o####    ########       #   #
#GS  #    #              #   #
#    ###     #####  ######   #
#      #     #   #  #      ###
#     #####    #    #  # x   #
#              #       #     #
##############################"""

smallMazeForceToHawk = """
##############################
#     H   #              #   #
#o####    ########       #   #
###  #    #              #   #
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

mediumHawkTestMaze= """
###########################################
#     #                #              #   #
#o    #        ####    ########       #   #
#     #####       #    #              #   #
#         #       ###     #####  ######   #
#   #######  ####   #     #   #  #      ###
#   #  #           #####    #    #  # x   #
#H  #  #              #     #       #     #
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
#HHHH#########     ########               #
#   H#             #           #########  #
#o  H                                     #
###########################################"""

largeMaze = """
####################################################################################################################
#                                                                                                                  #
#                   #                  ############################            #        ####    ########       #   #
#                   #                                                              #       #    #              #   #
#                   #############################                                  #       ###     #####  ######   #
#                           G   GG#                                          #######  ####         #   #  #        #
#                           G     #                                          #  #              ##    #    #  # x   #
#                                G#          ###########################     #  #              #     #       #     #
#           ################      #                                             #    ######    #         #         #
#                                 #                                             #              #         #  ########
#                    #                                                         ##     ##########         #         #
#                    #                                            #                                ############    #
#  G          G      #     #####################################  #          ##             #            #         #
#          G         #                                            #           #########     ########               #
#                    #           S             S                 S#           #             #           #########  #
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
#     #    S    G            #        #############################       #                           #            #
#     #                      #                                            #                           #            #
#     #                      #                         #                  #                           #            #
#     #                      #                         #                  #                           #            #
#     #    G                 #                         #                  #                           #            #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#S                           #                                            #                                        #
#o                                                                                                                 #
#G                                                                                                                 #
####################################################################################################################"""

largeMazeWithHawk = """
####################################################################################################################
#                                                                                                                  #
#                   #                  ############################            #        ####    ########       #   #
#                   #                                                              #       #    #              #   #
#                   #############################                                  #       ###     #####  ######   #
#                           G   GG#                                          #######  ####         #   #  #        #
#                           G     #                                          #  #              ##    #    #  # x   #
#                                G#          ###########################     #  #              #     #       #     #
#           ################      #                                             #    ######    #         #         #
#                                 #                                             #              #         #  ########
#                    #                                                         ##     ##########         #         #
#                    #                                            #                                ############    #
#  G          G      #     #####################################  #          ##             #            #         #
#          G         #                                            #           #########     ########               #
#                    #           S             S                 S#           #             #           #########  #
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
#     #    S    G            #        #############################       #                           #            #
#     #                      #                                            #                           #            #
#     #                      #                         #                  #                           #            #
#     #                      #                         #                  #                           #            #
#     #    G                 #                         #                  #                           #            #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#     #                      #                         #                  #                                        #
#######                      #                                            #                                        #
#o                                                                                                                 #
###HH##                                                                                                            #
####################################################################################################################"""
g_stuck_banner = """
  ********       **********       **     **         ******        **   **       **
 **//////       /////**///       /**    /**        **////**      /**  **       /**
/**                 /**          /**    /**       **    //       /** **        /**
/*********          /**          /**    /**      /**             /****         /**
////////**          /**          /**    /**      /**             /**/**        /**
       /**          /**          /**    /**      //**    **      /**//**       // 
 ********           /**          //*******        //******       /** //**       **
////////            //            ///////          //////        //   //       // """

g_stuck_banner1 = """
:'######:::::'########::::'##::::'##:::::'######:::::'##:::'##::::'####:
'##... ##::::... ##..::::: ##:::: ##::::'##... ##:::: ##::'##::::: ####:
 ##:::..:::::::: ##::::::: ##:::: ##:::: ##:::..::::: ##:'##:::::: ####:
. ######:::::::: ##::::::: ##:::: ##:::: ##:::::::::: #####:::::::: ##::
:..... ##::::::: ##::::::: ##:::: ##:::: ##:::::::::: ##. ##:::::::..:::
'##::: ##::::::: ##::::::: ##:::: ##:::: ##::: ##:::: ##:. ##:::::'####:
. ######:::::::: ##:::::::. #######:::::. ######::::: ##::. ##:::: ####:
:......:::::::::..:::::::::.......:::::::......::::::..::::..:::::....::"""

g_stuck_banner2 = """
  ********       **********       **     **         ******        **   **       **
 **//////       /////**///       /**    /**        **////**      /**  **       /**
/**                 /**          /**    /**       **    //       /** **        /**
/*********          /**          /**    /**      /**             /****         /**
////////**          /**          /**    /**      /**             /**/**        /**
       /**          /**          /**    /**      //**    **      /**//**       // 
 ********           /**          //*******        //******       /** //**       **
////////            //            ///////          //////        //   //       // """


class Utils:
    def manhattan_distance(l1, l2):
        assert((isinstance(l1, tuple) or isinstance(l1, list)) and 2 == len(l1))
        assert((isinstance(l2, tuple) or isinstance(l2, list)) and 2 == len(l2))
        logging.debug(f"{l1[0]} {l1[1]} {l2[0]} {l2[1]} {abs(l1[0] - l2[0])} {abs(l1[1] - l2[1])}")
        return abs(l1[0] - l2[0]) + abs(l1[1] - l2[1])

    def euclidean_distance(l1, l2):
        assert((isinstance(l1, tuple) or isinstance(l1, list)) and 2 == len(l1))
        assert((isinstance(l2, tuple) or isinstance(l2, list)) and 2 == len(l2))
        return math.sqrt((l1[0] - l2[0])**2 + (l1[1] - l2[1])**2)

    def get_matrix_for_program(rows, cols, things, include_grow_shrink=False):
        matrix = [[' ' for i in range(cols)] for j in range(rows)]
        for thing in things:
            if not isinstance(thing, Agent):
                (row, col) = tuple(thing.location)
                if (isinstance(thing, Wall)):
                    matrix[row][col] = '#'
                if (isinstance(thing, Door)):
                    matrix[row][col] = 'D'
                if (include_grow_shrink and isinstance(thing, Grow)):
                    matrix[row][col] = 'G'
                if (include_grow_shrink and isinstance(thing, Shrink)):
                    matrix[row][col] = 'S'
        return matrix

    def convert_text_matrix_to_object(rows, cols, tmatrix):
        matrix = [[None for i in range(cols)] for j in range(rows)]
        for i in range(rows):
            for j in range(cols):
                if '#' == tmatrix[i][j]:
                    matrix[i][j] = Wall(i, j)
                if 'G' == tmatrix[i][j]:
                    matrix[i][j] = Grow(i, j)
                if 'S' == tmatrix[i][j]:
                    matrix[i][j] = Shrink(i, j)
                if 'D' == tmatrix[i][j]:
                    matrix[i][j] = Door(i, j)
        return matrix

    def create_things_array_from_text_matrix(rows, cols, tmatrix):
        things = []
        for i in range(rows):
            for j in range(cols):
                thing = None
                if '#' == tmatrix[i][j]:
                    thing = Wall(i, j)
                if 'G' == tmatrix[i][j]:
                    thing = Grow(i, j)
                if 'S' == tmatrix[i][j]:
                    thing = Shrink(i, j)
                if 'D' == tmatrix[i][j]:
                    thing = Door(i, j)
                if (None != thing):
                    thing.set_location([i, j])
                    things.append(thing)
        return things

    def get_matrix_for_problem(rows:int, cols:int, things):
        """Another variant of the state matrix for search problems
        Get the matrix of all non-agent objects to store as the state of a search problem
        This does a shallow copy of the objects, as a deep-copy is not required

        Args:
            rows (int): rows in the matrix
            cols (int): columns in the matrix
            things ([type]): list of things from the percept

        Returns:
            list of list: matrix containing all objects at their respective loctations, except the agent
        """
        matrix = [[None for i in range(cols)] for j in range(rows)]
        for thing in things:
            if not isinstance(thing, Agent):
                (r, c) = tuple(thing.location)
                matrix[r][c] = thing
        return matrix

    def get_new_max_length(agent_max_length, direction):
        agent_max_length += (5 * direction)
        #agent_max_length += (1 * direction)
        if (agent_max_length < 0):
            agent_max_length = 0
        return agent_max_length

    def verify_agent_view_doesnt_have_hawk(things):
        for thing in things:
            if thing.is_hidden_from_agent():
                return False
        return True

    def get_adjacent_squares(loc, dimensions):
        (x, y) = tuple(loc)
        (r, c) = tuple(dimensions)
        candidates = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        ret = []
        for i in candidates:
            (x, y) = i
            if x >= 0 and x < r and y >=0 and y < c:
                ret.append(i)
        return ret

    def get_logic_symbol(prefix, location):
        (x, y) = tuple(location)
        return "%s_%0.3d_%0.3d" % (prefix, x, y)

    def update_kb_for_location(kb, percepts):
        assert(isinstance(kb, SnakeKnowledgeBaseToDetectHawk))
        location = percepts["location"]
        feelings = percepts["feelings"]
        shreik_heard = False
        if None != feelings and len(feelings) > 0:
            shreik_heard = True
        if None != kb:
            if shreik_heard:
                kb.tell_location_nothawk(tuple(location))
                logging.debug(f"Feelings are {feelings}")
            else:
                kb.tell_location_safe(tuple(location))
        return shreik_heard

    def create_initial_kb(percepts, algorithm):
        global g_override_global_algorithm
        shreik_heard = False
        thealgorithm = algorithm
        if g_override_global_algorithm != -1:
            logging.info(f"theAlgorithm = {g_override_global_algorithm}")
            thealgorithm = g_override_global_algorithm
        assert(Utils.verify_agent_view_doesnt_have_hawk(percepts["things"]))
        (row, col) = tuple(percepts["dimensions"])
        location = percepts["location"]
        matrix = Utils.get_matrix_for_program(row, col,\
                percepts["things"], include_grow_shrink=True)
        kb = SnakeKnowledgeBaseToDetectHawk(matrix, (len(matrix), len(matrix[0])), thealgorithm)
        return kb

    def trim_candidate_if_hawk(kb, shreik_heard, candidates, a_loc, mt_dim):
        if shreik_heard and kb:
            temp = []
            for cand in candidates:
                hawk = kb.ask_if_location_hawk(tuple(cand))
                if not hawk:
                    temp.append(cand)
                else:
                    logging.info(f"{cand} is definitely a hawk. skipping...")
            return temp
        else:
            return candidates

# Super-class for all things in 2-D environment
# An additional get_display() method returns a character
# Which the environment can use to print a board if required
class TwoDThing(Thing):
    def __init__(self, x = 0, y = 0, display='T'):
        """constructor

        Args:
            x (int, optional): row of the item. Defaults to 0.
            y (int, optional): column of the item. Defaults to 0.
            display (str, optional): character to display when printing the board for this item. Defaults to 'T'.
        """
        super().__init__()
        self.location = [x, y]
        self.display = display
        self.agent_cannot_see_me = False
        self.i_can_kill_agent = False

    def get_location(self):
        """get the location for this item

        Returns:
            tuple: tuple of row, column
        """
        return (self.location[0], self.location[1])

    def set_location(self, location = []):
        """Set the location for this item

        Args:
            location (list, optional): location [row, col]. Defaults to [].
        """
        self.location = location

    def get_display(self):
        """Get the display character

        Returns:
            str: character to display on the board corresponding to this object
        """
        return self.display

    def is_hidden_from_agent(self):
        return self.agent_cannot_see_me

    def can_kill_agent(self, ag_location):
        if self.i_can_kill_agent and tuple(self.location) == tuple(ag_location):
            return True
        return False

    def get_agent_feelings(self, ag_loc):
        return None


# Class power
class Power(TwoDThing):
    def __init__(self, x, y):
        self.power_value = -1
        super().__init__(x, y, 'o')

    def set_power_value(self, i: int):
        self.power_value = i

    # Get the value of the power, this is similar to points
    def get_power_value(self):
        assert(-1 != self.power_value)
        return self.power_value

    # Get the display character, overriding that from the parent class
    def get_display(self):
        return str(self.power_value)

# Wall
class Wall(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, '#')

# door
class Door(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, 'D')

# Grow the snake's size if the option is specified
class Grow(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, 'G')

# Shrink the snake's size if the option is specified
class Shrink(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, 'S')

"""
Hawks eat snakes. However, the snake cannot see the Hawk.
But the snake can hear the hawk's shriek only if its head is in a
square directly left, or right or above or below the hawk's
"""
class Hawk(TwoDThing):
    def __init__(self, x, y):
        super().__init__(x, y, 'H')
        self.is_alive = True
        self.i_can_kill_agent = True
        self.agent_cannot_see_me = True

    def get_agent_feelings(self, ag_loc):
        if 1 == Utils.manhattan_distance(ag_loc, self.get_location()):
            return "shriek"


class SimpleGraphics():
    SQUARE_SIZE = 10
    RADIUS = SQUARE_SIZE // 2
    def __init__(self, rows, cols):
        global g_state_refresh_sleep
        global g_state_print_same_place_loop_count
        (rows, cols) = (cols, rows)
        self.rows = rows
        self.cols = cols
        self.numpass, self.numfail = pygame.init()
        self.is_inited = False
        if (self.numfail <= 1):
            #g_state_refresh_sleep = 0
            g_state_print_same_place_loop_count = 1
            self.is_inited = True
        else:
            logging.error(f"Failed to initialize pygame graphics: numfail = {self.numfail}")
        self.screen = pygame.display.set_mode(\
                [(rows + 5) * SimpleGraphics.SQUARE_SIZE,\
                (cols + 5) * SimpleGraphics.SQUARE_SIZE])
        self.screen.fill((255, 255, 255))

    def is_initialized(self):
        return self.is_inited

    def is_valid_matrix(self, m):
        rows = len(m);
        cols = 0;
        for i in range(rows):
            if cols < len(m[i]):
                cols = len(m[i])
        (rows, cols) = (cols, rows)
        if rows > self.rows or cols > self.cols:
            return False
        return True

    def fill_screen(self):
        self.screen.fill((255, 255, 255))

    def draw_circle(self, x, y, diameter, color):
        (x, y) = (y, x)
        radius = diameter // 2
        (rx, ry) = (x + radius, y + radius)
        pygame.draw.circle(self.screen, color, (rx, ry), radius)

    def draw_square(self, x, y, width, color):
        (x, y) = (y, x)
        #rect = pygame.Rect(x, y, width, width)
        pygame.draw.rect(self.screen, color, (x, y, width, width))

    def update(self, m):
        global g_graphics_sleep_time
        if not self.is_inited:
            return
        assert(isinstance(m, list))
        if not self.is_valid_matrix(m):
            return
        self.screen.fill((255, 255, 255))
        for i in range(len(m)):
            for j in range(len(m[i])):
                c = m[i][j]
                xoff = SimpleGraphics.SQUARE_SIZE * (i + 1);
                yoff = SimpleGraphics.SQUARE_SIZE * (j + 1);
                if ('#' == c):
                    self.draw_square(xoff, yoff, SimpleGraphics.SQUARE_SIZE, (0, 0, 255))
                elif ('*' == c or '-' == c or '|' == c or '/' == c or '\\' == c):
                    color = (0, 0, 0) if '*' != c else (255, 0, 0)
                    self.draw_circle(xoff, yoff, SimpleGraphics.SQUARE_SIZE, color)
                elif ('*' == c):
                    self.draw_circle(xoff, yoff, SimpleGraphics.SQUARE_SIZE, (255, 0, 0))
                elif ('D' == c):
                    self.draw_square(xoff, yoff, SimpleGraphics.SQUARE_SIZE, (0, 0, 0))
                elif ('G' == c):
                    self.draw_square(xoff, yoff, SimpleGraphics.SQUARE_SIZE, (0xef, 0xfa, 0x11))
                elif ('S' == c):
                    self.draw_square(xoff, yoff, SimpleGraphics.SQUARE_SIZE, (0x53, 0xef, 0x21))
                elif ('H' == c):
                    color = (111, 179, 247)
                    self.draw_circle(xoff, yoff, SimpleGraphics.SQUARE_SIZE, color)
        pygame.display.flip()
        time.sleep(g_graphics_sleep_time)

class SimpleGraphicsTkinter():
    SQUARE_SIZE = 10
    RADIUS = SQUARE_SIZE // 2

    def __init__(self, rows, cols):
        global g_state_refresh_sleep
        global g_state_print_same_place_loop_count
        (rows, cols) = (cols, rows)
        self.rows = rows
        self.cols = cols
        self.is_inited = False
        self.master = tkinter.Tk()
        self.labels = []
        logging.info("Tkinter {}".format(self.master))
        if (None != self.master):
            self.canvas = tkinter.Canvas(self.master,\
                    width=((rows + 5)*SimpleGraphicsTkinter.SQUARE_SIZE),\
                    height=((cols + 5) * SimpleGraphicsTkinter.SQUARE_SIZE))
            self.is_inited = True
            g_state_print_same_place_loop_count = 1
            self.canvas.update()

    def is_initialized(self):
        return self.is_inited

    def is_valid_matrix(self, m):
        rows = len(m);
        cols = 0;
        for i in range(rows):
            if cols < len(m[i]):
                cols = len(m[i])
        (rows, cols) = (cols, rows)
        if rows > self.rows or cols > self.cols:
            return False
        return True

    def fill_screen(self):
        self.screen.fill((255, 255, 255))

    def draw_circle(self, x, y, diameter, color):
        (x, y) = (y, x)
        self.canvas.create_oval(x, y, x + diameter + 1, y + diameter + 1, fill=self.get_color_string(color), outline="")

    def get_color_string(self, color: tuple):
        stringcolor = "#"
        for i in color:
            tempstr = "%.2x" % i
            stringcolor = stringcolor + tempstr
        return stringcolor

    def draw_square(self, x, y, width, color):
        (x, y) = (y, x)
        self.canvas.create_rectangle(x, y, x + width + 1, y + width + 1, fill=self.get_color_string(color), outline="")
        #rect = pygame.Rect(x, y, width, width)

    def clear_labels(self):
        for i in self.labels:
            i.destroy()
        self.labels = []

    def update(self, m):
        global g_graphics_sleep_time
        if not self.is_inited:
            return
        assert(isinstance(m, list))
        self.canvas.delete("all")
        if not self.is_valid_matrix(m):
            return
        self.clear_labels()
        for i in range(len(m)):
            for j in range(len(m[i])):
                c = m[i][j]
                xoff = SimpleGraphicsTkinter.SQUARE_SIZE * (i + 1);
                yoff = SimpleGraphicsTkinter.SQUARE_SIZE * (j + 1);
                if ('*' == c or '-' == c or '|' == c or '/' == c or '\\' == c):
                    color = (0, 0, 0) if '*' != c else (255, 0, 0)
                    self.draw_circle(xoff, yoff, SimpleGraphicsTkinter.SQUARE_SIZE, color)
                elif ('#' == c):
                    self.draw_square(xoff, yoff, SimpleGraphicsTkinter.SQUARE_SIZE, (0, 0, 255))
                elif ('D' == c):
                    self.draw_square(xoff, yoff, SimpleGraphicsTkinter.SQUARE_SIZE, (0, 0, 0))
                    l = tkinter.Label(self.master, text = c, fg="white", bg="black")
                    l.place(y=xoff, x=yoff,\
                            width=SimpleGraphicsTkinter.SQUARE_SIZE, height=SimpleGraphicsTkinter.SQUARE_SIZE)
                    self.labels.append(l)
                elif ('G' == c):
                    self.draw_square(xoff, yoff, SimpleGraphicsTkinter.SQUARE_SIZE, (0xef, 0xfa, 0x11))
                    l = tkinter.Label(self.master, text = c, fg="black", bg=self.get_color_string((0xef, 0xfa, 0x11)))
                    l.place(y=xoff, x=yoff,\
                            width=SimpleGraphicsTkinter.SQUARE_SIZE, height=SimpleGraphicsTkinter.SQUARE_SIZE)
                    self.labels.append(l)
                elif ('S' == c):
                    self.draw_square(xoff, yoff, SimpleGraphicsTkinter.SQUARE_SIZE, (0x53, 0xef, 0x21))
                    l = tkinter.Label(self.master, text = c, fg="black", bg=self.get_color_string((0x53, 0xef, 0x21)))
                    l.place(y=xoff, x=yoff,\
                            width=SimpleGraphicsTkinter.SQUARE_SIZE, height=SimpleGraphicsTkinter.SQUARE_SIZE)
                    self.labels.append(l)
                elif ('H' == c):
                    color = (111, 179, 247)
                    self.draw_circle(xoff, yoff, SimpleGraphicsTkinter.SQUARE_SIZE, color)
                    l = tkinter.Label(self.master, text = c, fg="black", bg=self.get_color_string(color))
                    l.place(y=xoff, x=yoff,\
                            width=SimpleGraphicsTkinter.SQUARE_SIZE, height=SimpleGraphicsTkinter.SQUARE_SIZE)
                    self.labels.append(l)
        self.canvas.pack()
        self.canvas.update()
        self.master.update()
        time.sleep(g_graphics_sleep_time)


counter = 0
# Create our own 2D environment
class TwoDEnvironment(Environment):
    def __init__(self, rows, cols, restore_power=True, initial_agent_max_length=8, ag_can_grow=True):
        global g_curses_available
        self.stored_power = None
        super().__init__()
        self.stuck_banner_completed = False
        self.last_banner_used = 0
        self.rows = rows
        self.agent_max_length = initial_agent_max_length
        self.cols = cols
        self.is_stuck = False
        self.goal_distance = -1
        self.thedoor = None
        self.agent_can_grow = ag_can_grow
        self.restore_power = restore_power # Powers once taken should reappear
        self.agent_history = collections.deque()
        self.matrix = [[None for i in range(cols)] for j in range(rows)] # 2D array
        self.graphics = None
        self.graphics_failed = False
        self.agent_died = False
        if g_curses_available:
            self.window = curses.initscr()

    # If the agent has just moved over a grow/shrink square, then this is called
    # to adjust the size of the history of agent's movements that the environment

    # keeps track of
    def process_agent_grow_shrink(self, direction):
        if not self.agent_can_grow:
            return
        self.agent_max_length = Utils.get_new_max_length(self.agent_max_length, direction)
        if (direction != 0):
            global counter
            counter = counter + 1
        self.trim_history()

    def process_agent_grow_shrink2(self, should_grow, should_shrink):
        direction = 0
        direction = 1 if should_grow else direction
        direction = -1 if should_shrink else direction
        return self.process_agent_grow_shrink(direction)

    # If the agent is stuck, or the agent has reached the door, return true
    def is_done(self):
        if self.is_stuck:
            return True
        if not self.agents[0].is_alive:
            print("Agent is not alive, game over")
            self.agent_died = True
            return True
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

    # deletion of the object must close the ncurses session if it was started
    def __del__(self):
        global g_curses_available
        if g_curses_available:
            curses.endwin()

    def trim_history(self):
        while(len(self.agent_history) > self.agent_max_length):
            self.agent_history.popleft()

    def old_object_processing(self, old_object):
        should_grow = False
        should_shrink = False
        num_power = 0
        if None == old_object:
            return should_grow, should_shrink, num_power
        if (isinstance(old_object, Power)):
            agent.num_power += old_object.get_power_value()
        if (isinstance(old_object, Grow)):
            should_grow = True
        if (isinstance(old_object, Shrink)):
                should_shrink = True
        if (not self.restore_power):
            self.things.remove(old_object)
        return should_grow, should_shrink, num_power

    def stash_old_object(self, old_object):
        if True == self.restore_power and old_object != None:
            if isinstance(old_object, Power) or isinstance(old_object, Grow)\
                    or isinstance(old_object, Shrink):
                self.stored_power = old_object

    def restore_old_object(self):
        if True == self.restore_power and None != self.stored_power:
            (row, col) = tuple(self.stored_power.location)
            self.matrix[row][col] = self.stored_power
            self.stored_power = None

    def update_agent(self, agent, r, c, n_power):
        agent.num_power = n_power
        agent.set_location(r, c)
        agent.num_moves += 1

    """
    Sequence of actions
    1. Convert the move to the newrow, newcol
    2. Set the matrix position at curent row, col to None (agent was there till nwo)
    3. If old-row, old-col are not already in history, add them to the history
    4. Trim the history to size if required
    5. Restore the stashed object in the matrix at row, col if applicable
    6. Stash the object at newrow, newcol for later
    7. Update the matrix to reflect the agent at newrow, newcol
    8. Update the agent's internal location and other parameters
    9. If we stepped on a square that grows or shrinks us, change the length of the history dequeue
    """
    def execute_action(self, agent, action):
        should_grow = False
        should_shrink = False
        global g_self_crossing_not_allowed
        if None == action:
            return
        row, col = agent.get_location()
        assert(self.matrix[row][col] == agent and None != row and None != col)
        # 1. Get Where we are to move to
        newrow, newcol = NextMoveHelper.get_updated_row_col(row, col, action)
        assert(-1 != newrow and -1 != newcol)
        self.matrix[row][col] = None
        # 2. Update history with the current row, column if required
        if (len(self.agent_history) > 0 and \
            (row, col) != self.agent_history[len(self.agent_history) - 1]) or\
            (0 == len(self.agent_history)):
            self.agent_history.append((row, col))
            self.trim_history()
        assert((newrow, newcol) not in self.agent_history or not g_self_crossing_not_allowed)
        self.restore_old_object()
        old_object = self.matrix[newrow][newcol]
        self.matrix[newrow][newcol] = agent
        # 3. If we stepped on something in the new row, col, we must grow or shrink
        should_grow, should_shrink, num_power = self.old_object_processing(old_object)
        self.update_agent(agent, newrow, newcol, num_power)
        if None != self.stored_power and True == self.restore_power:
            if self.stored_power not in self.things:
                self.add_thing(self.stored_power, [row, col])
            else:
                self.stored_power.location = [row, col]
            self.stored_power = None
        self.stash_old_object(old_object)
        # 4. Do the actual growing/shrinking
        self.process_agent_grow_shrink2(should_grow, should_shrink)
        for thing in self.things:
            if thing.can_kill_agent(agent.get_location()):
                agent.is_alive = False
                print(f"Agent is now dead, {thing} killed it at location {agent.get_location()}")

    # "dimensions" : dimensions of board
    # "location" : location of agent
    # "things" : list of things
    # "goal_direction": direction of goal [dx, dy] dx/dy can be negative
    # "agent_history": list of past locations of the agent [(r,c), (r,c), ..]
    # 'agent_can_grow": can the agent shrink and grow?
    # 'agent_max_length': maximum length till which the agent can grow (excluding head)
    # 'agent_history': the history of the places the agent has been, also doubles as the body
    def percept(self, agent):
        percept = {}
        thedoor = None
        x, y = agent.get_location()
        percept["dimensions"] = [self.rows, self.cols]
        percept["location"] = [x, y]
        percept["things"] = []
        percept["agent_history"] = []
        percept["agent_can_grow"] =  self.agent_can_grow
        percept["agent_max_length"] = self.agent_max_length
        percept["history"] = copy.deepcopy(self.agent_history)
        percept["feelings"] = []
        [percept["agent_history"].append(l) for l in self.agent_history]
        for thing in self.things:
            if not thing.is_hidden_from_agent():
                percept["things"].append(thing)
            if (isinstance(thing, Door)):
                thedoor = thing
            if thing.is_hidden_from_agent():
                feelings = thing.get_agent_feelings(agent.get_location())
                if (None != feelings):
                    logging.info(f"Agent at location {x}, {y} felt {feelings} from {thing} at {thing.get_location()}")
                    percept["feelings"].append(feelings)
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

    def print_stuck_banner(self, m, is_recursing=False):
        global g_stuck_banner, g_stuck_banner1
        try:
            self.last_banner_used = 0 if self.last_banner_used != 0 else 1
            banner = g_stuck_banner if 0 == self.last_banner_used else g_stuck_banner1
            assert(None != m and isinstance(m, list))
            for i, line in enumerate(banner.split('\n')):
                for j, c in enumerate(list(line)):
                    try:
                        m[i][j] = c
                    except:
                        pass
        except:
            if not is_recursing:
                m = [[' ' for i in range(200)] for j in range(200)]
                return self(self, m, is_recursing=True)

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
        if self.is_stuck:
            self.print_stuck_banner(m)
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
        return 0

    def display_graphics(self):
        global g_use_tkinter, g_tkinter_available, g_use_pygame, g_pygame_available
        m = self.get_print_matrix()
        if (None == self.graphics):
            if (g_use_tkinter and g_tkinter_available):
                self.graphics = SimpleGraphicsTkinter(len(m), len(m[0]))
            else:
                if (g_use_pygame and g_pygame_available):
                    self.graphics = SimpleGraphics(len(m), len(m[0]))
        if (None == self.graphics or not self.graphics.is_inited):
            logging.error("0. Graphics failed, not going to use graphics")
            self.graphics_failed = True
        try:
            if not self.graphics_failed:
                self.graphics.update(m)
        except:
            logging.error("1. Graphics failed. not goint to use graphics")
            self.graphics_failed = True

    def print_state(self):
        global g_suppress_state_printing
        global g_state_refresh_sleep
        global g_state_print_same_place_loop_count
        global g_curses_available
        global g_pygame_available, g_use_pygame
        global g_tkinter_available
        if g_suppress_state_printing:
            return
        global g_curses_available
        if (g_pygame_available and g_use_pygame) or g_tkinter_available:
            self.display_graphics()
        if g_curses_available:
            self.print_state_curses()
            if (not self.is_stuck or not self.stuck_banner_completed):
                for i in range(g_state_print_same_place_loop_count):
                    self.print_state_curses()
                    if (0 != g_state_refresh_sleep):
                        if (None == self.graphics or False == self.graphics.is_initialized()):
                            time.sleep(g_state_refresh_sleep)
                self.stuck_banner_completed = True
            return
        else:
            return self.print_state_text()

class TwoDMaze(TwoDEnvironment):
    NUM_NULL_MOVES_TILL_STUCK = 2
    def __init__(self, mazeString=str):
        global g_agent_can_grow
        global g_agent_initial_max_length
        mazeString = [list(x.strip()) for x in mazeString.split("\n") if x]
        self.stuck_detect = collections.deque()
        rows = len(mazeString)
        cols = len(mazeString[0])
        self.dimensions = (rows, cols)
        super().__init__(rows, cols, ag_can_grow=g_agent_can_grow,\
                initial_agent_max_length=g_agent_initial_max_length)
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
                if 'G' == mazeString[i][j]:
                    grow = Grow(i, j)
                    self.add_thing(grow, [i, j])
                if 'S' == mazeString[i][j]:
                    shrink = Shrink(i, j)
                    self.add_thing(shrink, [i, j])
                if 'H' == mazeString[i][j]:
                    hawk = Hawk(i, j)
                    self.add_thing(hawk, [i, j])
        print(f"StartingRun with MazeSize = ({rows}, {cols})")

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
        the_agent = None
        the_door = None
        for thing in self.things:
            if isinstance(thing, Agent):
                the_agent = thing
            if isinstance(thing, Door):
                the_door = thing
        x1, y1 = the_door.get_location()
        x2, y2 = the_agent.get_location()
        self.goal_distance = Utils.manhattan_distance((x1, y1), (x2, y2))
        return self.is_stuck

    def __del__(self):
        global g_curses_available
        if g_curses_available:
            curses.endwin()
            g_curses_available = False
        the_door = None
        for thing in self.things:
            if isinstance(thing, Door):
                the_door = thing
        x1, y1 = the_door.get_location()
        initial_goal_distance = Utils.manhattan_distance((x1, y1), self.initial_agent_location)
        print("=" * 120)
        stuck = self.got_stuck()
        agent = self.agents[0]
        print(f"Dimensions = {self.dimensions}")
        print(f"Agent = {agent}")
        print(f"IsAgentStuck = {stuck}")
        print(f"DidAgentDie = {False == agent.is_alive}")
        print(f"AgentNumMoves = {agent.num_moves}")
        print(f"InitialDistanceToGoal = {initial_goal_distance}")
        print(f"RemainingDistanceToGoal = {self.goal_distance}")
        print(f"DistanceCloserToGoal = {initial_goal_distance - self.goal_distance}")
        print(f"AgentLenth = {len(self.agent_history) + 1}")

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

    def is_hidden_from_agent(self):
        return False

    def can_kill_agent(self, ag_loc):
        return False

    def get_agent_feelings(self, ag_loc):
        return None

class NextMoveHelper(object):
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

    # Helper routine to get the candidate moves, it doesn't care
    # whether the move is blocked by a wall or not 
    # However, it checks whether the move is out of bounds
    # or not
    # It also checks if the move is within the body of the agent (snake)
    def get_candidate_positions(ag_location, mt_dimensions, history):
        global g_self_crossing_not_allowed
        (row, col) = tuple(ag_location)
        (total_rows, total_cols) = tuple(mt_dimensions)
        temp = [ (row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
        candidates = []
        assert(None != history)
        for row, col in temp:
            if (row >= 0 and row < total_rows and col >= 0 and col < total_cols):
                if (0 == len(history) or False == g_self_crossing_not_allowed
                        or ((row, col) not in history)):
                    candidates.append((row, col))
        return candidates

    def get_move_string(dx, dy):
        return NextMoveHelper.move_table[(dx, dy)]

    def get_new_location(move, x, y):
        if (isinstance(x, list) or isinstance(x, tuple)):
            y = x[0]
            x = x[1]
        if None == move:
            return x, y
        delta = NextMoveHelper.backward_move_table[move]
        assert(None != delta)
        x = x + delta[0]
        y = y + delta[1]
        return x, y

    def get_move_string2(oldx, oldy, newx, newy):
        return NextMoveHelper.get_move_string(newx - oldx, newy - oldy)

    def get_move_string3(old, new):
        assert((isinstance(old, list) or isinstance(old, tuple)) and 2 == len(old))
        assert((isinstance(new, list) or isinstance(new, tuple)) and 2 == len(new))
        return NextMoveHelper.get_move_string2(old[0], old[1], new[0], new[1])

    def get_move_suitability(oldx, oldy, newx, newy, gdx, gdy):
        gdx = 0 if 0 == gdx else gdx // abs(gdx)
        gdy = 0 if 0 == gdy else gdy // abs(gdy)
        dx = newx - oldx
        dy = newy - oldy
        dx = 0 if 0 == dx else dx // abs(dx)
        dy = 0 if 0 == dy else dy // abs(dy)
        score = 2
        if (dy == gdy):
            score += 1
        if (dx == gdx):
            score += 1
        return score

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

# SimpleReflexProgram randomly chooses a move in any direction
# as long as it doesn't hit a wall
def SimpleReflexProgram(weighted_rand_sel=False, use_inference=False):
    # Percepts are of the form
    # {
    #    "dimensions" = [row, col],
    #    "location": [row, col],
    #    "things" : [thing1, thing2, thing3]
    # }

    use_kb = use_inference
    kb = None
    # Recreate the matrix from the percepts
    matrix = None
    use_weighted_random_selection = weighted_rand_sel

    def select_random(cp):
        rowCandidate = colCandidate = -1
        while 0 != len(cp):
            i = random.randrange(0, len(cp))
            x, y = cp[i]
            if not isinstance(matrix[x][y], Wall):
                rowCandidate = x
                colCandidate = y
                break
            else:
                del cp[i]
        return rowCandidate, colCandidate

    def get_goal_directions(percepts):
        goal_direction = percepts["goal_direction"]
        dx = goal_direction[0]
        dy = goal_direction[1]
        dx = dx if 0 == dx else dx // abs(dx)
        dy = dy if 0 == dy else dy // abs(dy)
        return dx, dy

    def recreate_board(percepts):
        things = percepts["things"]
        mt_dimensions = percepts["dimensions"]
        matrix = [[None for i in range(mt_dimensions[1])] for j in range(mt_dimensions[0])]
        for thing in things:
            row = thing.location[0]
            col = thing.location[1]
            matrix[row][col] = thing
        return matrix

    def program(percepts):
        nonlocal matrix, use_weighted_random_selection, use_kb, kb
        assert(Utils.verify_agent_view_doesnt_have_hawk(percepts["things"]))
        shreik_heard = False
        rowCandidate = colCandidate = -1
        mt_dimensions = percepts["dimensions"]
        ag_location = percepts["location"]
        things = percepts["things"]
        history = percepts["agent_history"]
        if use_kb and None == kb:
            kb = Utils.create_initial_kb(percepts, SnakeKnowledgeBaseToDetectHawk.USE_DEFAULT_ALGORITHM)
        if None != kb:
            shreik_heard = Utils.update_kb_for_location(kb, percepts)
        dx, dy = get_goal_directions(percepts)
        assert(Utils.verify_agent_view_doesnt_have_hawk(percepts["things"]))
        # First recreate the matrix
        matrix = recreate_board(percepts)
        # Get the candidate positions
        candidate_positions = []
        # Assign higher probability to those which are in the direction of the door
        temp_positions = NextMoveHelper.get_candidate_positions(ag_location, mt_dimensions, history)
        for item in temp_positions:
            nx = item[0]
            ny = item[1]
            if (use_weighted_random_selection):
                weight = NextMoveHelper.get_move_suitability(ag_location[0], ag_location[1], nx, ny, dx, dy)
            else:
                weight = 1
            for i in range(weight):
                candidate_positions.append(copy.deepcopy(item))
        if shreik_heard and kb:
            candidate_positions = Utils.trim_candidate_if_hawk(kb, \
                    shreik_heard, candidate_positions, tuple(ag_location), \
                    tuple(mt_dimensions))
        # Randomly select a new position
        rowCandidate, colCandidate = select_random(candidate_positions)
        # Convert position to move (eg. [0, 0] -> MoveUp)
        if -1 != rowCandidate and -1 != colCandidate:
            move = NextMoveHelper.get_move_string2(ag_location[0], ag_location[1], rowCandidate, colCandidate)
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
def GoalDrivenAgentProgram(use_inference=False, norandom=False):
    # Gaol driven greedy search may get stuck. If it does
    # We need to randomly go to a new node which we haven't visited earlier
    doing_random = False
    visited_matrix = None
    use_kb = use_inference
    kb = None
    shreik_heard = False

    def get_matrix(rows, cols, things):
        return Utils.get_matrix_for_program(rows, cols, things)

    def get_random_move(matrix, a_loc, history):
        nonlocal kb, shreik_heard
        assert(None != matrix and isinstance(matrix, list) and isinstance(matrix[0], list))
        mt_dim = [len(matrix), len(matrix[0])]
        rowCandidate = colCandidate = -1
        candidate_positions = NextMoveHelper.get_candidate_positions(a_loc, mt_dim, history)
        if shreik_heard and kb:
            logging.debug("Trimming")
            candidate_positions = Utils.trim_candidate_if_hawk(kb,\
                    shreik_heard, candidate_positions, tuple(a_loc), tuple(mt_dim))
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
            move = NextMoveHelper.get_move_string(row_move, col_move)
            assert(None != move)
            return move
        assert(True) # Should never reach here
        return None


    def get_goal_directed_new_location_int(matrix, m_rows, m_cols, a_row, a_col, dx, dy, history):
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

    def get_goal_directed_new_location(matrix, m_rows, m_cols, a_row, a_col, dx, dy, history):
        nonlocal kb, shreik_heard
        r, c = get_goal_directed_new_location_int(matrix, m_rows, m_cols,\
                a_row, a_col, dx, dy, history)
        if shreik_heard and None != kb and (-1, -1) != (r, c) and kb.ask_if_location_hawk((r, c)):
            return -1, -1
        return r, c


    def get_action_string(n_r, n_c, o_r, o_c):
        dx = n_r - o_r
        dy = n_c - o_c
        assert(None != NextMoveHelper.get_move_string(dx, dy))
        return NextMoveHelper.get_move_string(dx, dy)

    # Validate that the next move is not out of bounds
    def validate_move(move, a_row, a_col, rows, cols):
        nr, nc = NextMoveHelper.get_updated_row_col(a_row, a_col, move)
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
        nonlocal visited_matrix, doing_random
        nonlocal use_kb, kb, shreik_heard
        assert(Utils.verify_agent_view_doesnt_have_hawk(percepts["things"]))
        rows = percepts["dimensions"][0]
        cols = percepts["dimensions"][1]
        a_row = percepts["location"][0]
        a_col = percepts["location"][1]
        dx = percepts["goal_direction"][0]
        dy = percepts["goal_direction"][1]
        history = percepts["agent_history"]
        if use_kb and None == kb:
            kb = Utils.create_initial_kb(percepts, SnakeKnowledgeBaseToDetectHawk.USE_DEFAULT_ALGORITHM)
        if None != kb:
            shreik_heard = Utils.update_kb_for_location(kb, percepts)
        assert(Utils.verify_agent_view_doesnt_have_hawk(percepts["things"]))
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
                # TODO: RB: Remove randomness and see what happens
                if (False == norandom):
                    doing_random = True
                else:
                    return None
        assert(True == doing_random)
        move = get_random_move(matrix, [a_row, a_col], history)
        assert(None == move or validate_move(move, a_row, a_col, rows, cols))
        return move

    return program

# Utility based agent program. This program calculates the utility function
# For each of the candidate locations, and then chooses the one that
# maximizes the utility function
def UtilityBasedAgentProgram(use_inference=False):

    # Agent program's memories of places visited, this becomes important
    # To the utility function because a negative score must be associated
    # with places we've visited so that we don't get stuck in a loop
    memories = None
    use_kb = use_inference
    kb = None

    def utility_function(percepts, location, goal, matrix):
        nonlocal memories
        GOAL_SCALING_FACTOR = -100 * (len(percepts["history"]) + 1)
        HISTORY_SCALING_FACTOR = 100
        MEMORY_SCALING_FACTOR = -10
        GROWTH_SCALING_FACTOR = -100 * (len(percepts["history"]) + 1)
        SHRINK_SCALING_FACTOR = 200 * (len(percepts["history"]) + 1)
        assert((isinstance(location, tuple) or isinstance(location, list)) and 2 == len(location))
        assert(None != memories and None != matrix and isinstance(matrix, list))
        (row, col) = tuple(location)
        utility_score = 0
        # The further the goal is the less should be the score
        # (goal_direction is already an offset, so this should be minimized)
        utility_score += Utils.manhattan_distance(location, goal) * GOAL_SCALING_FACTOR
        # The closer you get to your body, the less you score.
        for loc in percepts["agent_history"]:
            utility_score += Utils.manhattan_distance(loc, location) * HISTORY_SCALING_FACTOR
        try:
            utility_score += MEMORY_SCALING_FACTOR * memories[row][col]
        except IndexError:
            pass
        if 'G' == matrix[row][col]:
            utility_score += GROWTH_SCALING_FACTOR
        if 'S' == matrix[row][col]:
            utility_score += SHRINK_SCALING_FACTOR
        return utility_score

    def get_candidate_positions(percepts, matrix, shreik_heard):
        import sys
        nonlocal kb, use_kb
        a_loc = percepts['location']
        mt_dim = percepts["dimensions"]
        history = percepts["history"]
        gd = percepts["goal_direction"]
        goal = (a_loc[0] + gd[0], a_loc[1] + gd[1])
        candidates = NextMoveHelper.get_candidate_positions(a_loc, mt_dim, history)
        matrix = Utils.get_matrix_for_program(mt_dim[0],\
                                    mt_dim[1], percepts["things"])
        max_utility = -1 * sys.maxsize - 1
        candidates_not_walls = []
        for candidate in candidates:
            (r, c) = candidate
            if ('#' == matrix[r][c]):
                continue
            candidates_not_walls.append(candidate)
        candidates_not_walls = Utils.trim_candidate_if_hawk(kb, shreik_heard, candidates_not_walls, a_loc, mt_dim)
        if (None == candidates_not_walls or 0 == len(candidates_not_walls)):
            return candidates_not_walls
        utility_socres = [utility_function(percepts, candidate, goal, matrix)\
                            for candidate in candidates_not_walls]
        max_utility = max(utility_socres)
        selected_candidates = []
        for candidate in candidates_not_walls:
            utility = utility_function(percepts, candidate, goal, matrix)
            if (utility == max_utility):
                selected_candidates.append(candidate)
        return selected_candidates

    def program(percepts):
        nonlocal memories
        nonlocal use_kb, kb
        shreik_heard = False
        assert(Utils.verify_agent_view_doesnt_have_hawk(percepts["things"]))
        (row, col) = tuple(percepts["dimensions"])
        (row, col) = tuple(percepts["dimensions"])
        location = percepts["location"]
        matrix = Utils.get_matrix_for_program(row, col,\
                percepts["things"], include_grow_shrink=True)
        if use_kb and None == kb:
            kb = Utils.create_initial_kb(percepts, SnakeKnowledgeBaseToDetectHawk.USE_DEFAULT_ALGORITHM)
        if None != kb:
            shreik_heard = Utils.update_kb_for_location(kb, percepts)
            logging.info(f"shreik_heard = {shreik_heard}")
        if None == memories:
            memories = [[0 for i in range(col)] for j in range(row)]
        candidates = get_candidate_positions(percepts, matrix, shreik_heard)
        if (None == candidates or 0 == len(candidates)):
            return None
        candidate = random.choice(candidates)
        if (None != candidate):
            memories[candidate[0]][candidate[1]] += 1
        return NextMoveHelper.get_move_string3(percepts["location"], candidate)

    return program

class SearchHelper:
    def get_text_matrix_for_search(percepts):
        things = percepts["things"]
        (maxrow, maxcol) = tuple(percepts["dimensions"])
        return Utils.get_matrix_for_program(maxrow, maxcol, things, True)

    def convert_percepts_to_state(percepts:dict):
        global g_search_should_consider_history
        matrix = SearchHelper.get_text_matrix_for_search(percepts)
        ag_hist = []
        if g_search_should_consider_history:
            ag_hist = list(percepts["agent_history"])
        (curx, cury) = tuple(percepts["location"])
        (goalx, goaly) = tuple(percepts["goal_direction"])
        goalx += curx
        goaly += cury
        agent_can_grow = percepts["agent_can_grow"]
        agent_max_length = percepts["agent_max_length"]
        (dimx, dimy)= tuple(percepts["dimensions"])
        tup = ([matrix], [ag_hist], [[curx, cury]], [[goalx, goaly]], agent_can_grow, agent_max_length, [[dimx, dimy]])
        tup = pickle.dumps(tup)
        return tup

    def convert_state_to_percepts(state):
        global g_search_should_consider_history
        ag_hist = None
        state = pickle.loads(state)
        textmatrix = state[0][0]
        if g_search_should_consider_history:
            ag_hist = collections.deque(state[1][0])
        location = state[2][0]
        goal = state[3][0]
        agent_can_grow = state[4]
        agent_max_length = state[5]
        dimensions = state[6][0]
        matrix = Utils.convert_text_matrix_to_object(dimensions[0], dimensions[1], textmatrix)
        goal_dir_x = goal[0] - location[0]
        goal_dir_y = goal[1] - location[1]
        goal = [goal_dir_x, goal_dir_y]
        percepts = {}
        percepts["matrix"] = matrix
        if g_search_should_consider_history:
            percepts["agent_history"] = ag_hist
        percepts["location"] = location
        percepts["goal_direction"] = goal
        percepts["agent_can_grow"] = agent_can_grow
        percepts["agent_max_length"] = agent_max_length
        percepts["dimensions"] = dimensions
        percepts["things"] = Utils.create_things_array_from_text_matrix(dimensions[0], dimensions[1], textmatrix)
        return percepts

    """
    Sequence of actions performed in execute_action
    1. Convert the move to the newrow, newcol
    2. Set the matrix position at curent row, col to None (agent was there till nwo)
    3. If old-row, old-col are not already in history, add them to the history
    4. Trim the history to size if required
    5. Restore the stashed object in the matrix at row, col if applicable
    6. Stash the object at newrow, newcol for later
    7. Update the matrix to reflect the agent at newrow, newcol
    8. Update the agent's internal location and other parameters
    9. If we stepped on a square that grows or shrinks us, change the length of the history dequeue
    """
class MazeSearchProblem(Problem):
    def __init__(self, initial, goal=None):
        self.cand_moves = self.succs = self.goal_tests = self.states = 0
        self.found = None
        super().__init__(initial, goal)

    # This function has been copied from search.py
    def __repr__(self):
        string = "%15.15s %25.25s %15.15s %15.15s\n" %\
                ("n_Sccessors", "n_CandidatesConsidered", "n_GoalTests", "n_States")
        string += "%15d %25d %15d %15d" % (self.succs, self.cand_moves, self.goal_tests, self.states)
        return string

    def actions(self, state):
        global g_search_should_consider_history
        """
            state["matrix"]             - matrix of all objects (shallow copy)
            state["agent_history"]      - deque of locations of history (deep copy)
            state["location"]           - current location
            state["goal"]               - goal
            state["agent_can_grow"]     - can the agent grow?
            state["agent_max_length"]   - maximum length of the agent
            state["dimensions"]         - dimensions of the matrix
        """
        state = SearchHelper.convert_state_to_percepts(state)
        ag_location = state["location"]
        (oldrow, oldcol) = tuple(ag_location)
        mt_dimensions = state["dimensions"]
        if (g_search_should_consider_history):
            history = state["agent_history"]
        else:
            history = []
        matrix = state["matrix"]
        logging.debug(f"{state['agent_max_length']}")
        candidate_positions = NextMoveHelper.get_candidate_positions(ag_location, mt_dimensions, history)
        candidate_moves = []
        logging.debug(f"{state['location']}" + "---->" + f"{candidate_positions}")
        for pos in candidate_positions:
            (row, col) = tuple(pos)
            if not isinstance(matrix[row][col], Wall):
                candidate_moves.append(NextMoveHelper.get_move_string2(oldrow, oldcol, row, col))
        self.succs += 1
        self.cand_moves += len(candidate_moves)
        logging.debug(f"{oldrow}, {oldcol}, {candidate_moves}")
        return candidate_moves

    """
    Sequence of actions:
    1. Get candidate locations
    2. Discard walls from candidate locations
    3. Update the history and trim if required
    4. Update the agent's location to the new location
    6. If we stepped on a square that grows/shrinks, change the length of history deque
    """
    def result(self, state, action):
        global g_search_should_consider_history
        self.states += 1
        state = SearchHelper.convert_state_to_percepts(state)
        agent_max_length = state["agent_max_length"]
        agent_can_grow = state["agent_can_grow"]
        matrix = state["matrix"]
        logging.debug(type(state["goal_direction"]))
        # Get the old goal direction, this will be updated
        (goaldx, goaldy) = tuple(state["goal_direction"])
        logging.debug(f"Initial: {goaldx}, {goaldy}")
        # def get_new_location(move, x, y):
        (curx, cury) = tuple(state["location"])
        (newx, newy) = NextMoveHelper.get_new_location(action, curx, cury)
        logging.debug(f"{action} : ({curx}, {cury}) --> ({newx}, {newy})")
        # Calculate the absolute goal
        (goalx, goaly) = (curx + goaldx, cury + goaldy)
        # Get the new goal directions
        (goaldx, goaldy) = (goalx - newx, goaly - newy)
        state["goal_direction"] = [goaldx, goaldy]
        logging.debug(f"Final: {goaldx}, {goaldy}")
        (offx, offy) = (newx - curx, newy - cury)
        if (g_search_should_consider_history and agent_can_grow):
            history = state["agent_history"]
            logging.debug(f"history = {history}")
            if (len(history) > 0 and (curx, cury) != history[len(history) - 1]) or (0 == len(history)):
                history.append((curx, cury))
                while(len(history) > agent_max_length):
                    history.popleft()
            state["agent_history"] = history
        state["location"] = [newx, newy]
        if None != matrix[newx][newy]:
            direction = 0
            if isinstance(matrix[newx][newy], Grow):
                direction = 1
            if isinstance(matrix[newx][newy], Shrink):
                direction = -1
            if (0 != direction):
                agent_max_length = Utils.get_new_max_length(agent_max_length, direction)
                state["agent_max_length"] = agent_max_length
        return SearchHelper.convert_percepts_to_state(state)

    def goal_test(self, state):
        self.goal_tests += 1
        state = SearchHelper.convert_state_to_percepts(state)
        matrix = state["matrix"]
        (curx, cury) = tuple(state["location"])
        if (isinstance(matrix[curx][cury], Door)):
            return True
        return False

def SearchBasedAgentProgram(algorithm=astar_search, useheuristic=False, use_inference=False):

    search_results = None
    search_results_deque = collections.deque()
    search_completed = False
    stats = None
    search_algorithm = algorithm
    perf_string = ""
    use_heuristic = useheuristic
    use_kb = use_inference
    kb = None
    known_hawks = []


    def time_and_run_algorithm(problem, heuristic):
        nonlocal search_algorithm
        nonlocal perf_string
        nonlocal use_heuristic
        time1 = time.perf_counter()
        if (use_heuristic):
            srch = algorithm(problem, heuristic)
        else:
            srch = algorithm(problem)
        time2 = time.perf_counter()
        perf_string = f"Time taken by {algorithm}: {time2 - time1}\n"
        return srch

    def get_state_for_search(percepts):
        return SearchHelper.convert_percepts_to_state(percepts)

    def heuristic(node):
        percept = SearchHelper.convert_state_to_percepts(node.state)
        (curx, cury) = tuple(percept["location"])
        (goalx, goaly) = tuple(percept["goal_direction"])
        goalx += curx
        goaly += cury
        logging.debug(f"Heuristic returned: {Utils.manhattan_distance([curx, cury], [goalx, goaly])}")
        return Utils.manhattan_distance([curx, cury], [goalx, goaly])

    def program(percepts, get_stats=False, recursed=False):
        nonlocal search_results, search_results_deque, search_completed
        nonlocal stats, algorithm, perf_string, use_kb, kb, known_hawks
        assert(get_stats or Utils.verify_agent_view_doesnt_have_hawk(percepts["things"]))
        shreik_heard = False
        if (get_stats):
            if (None == stats):
                stats = ""
            if (None != perf_string):
                stats = "\n\n" + perf_string + stats + "\n"
            return stats
        location = percepts["location"]
        (row, col) = tuple(location)
        if use_kb and None == kb and not recursed:
            kb = Utils.create_initial_kb(percepts, SnakeKnowledgeBaseToDetectHawk.USE_DEFAULT_ALGORITHM)
        if None != kb:
            shreik_heard = Utils.update_kb_for_location(kb, percepts)
        action = None
        if (not search_completed):
            # If we know there is a hawk at a location, treat it as a wall
            logging.debug(percepts)
            copy_of_percepts = copy.deepcopy(percepts)
            for hawk in known_hawks:
                (x, y) = tuple(hawk)
                copy_of_percepts["things"].append(Wall(x, y))
            state = SearchHelper.convert_percepts_to_state(copy_of_percepts)
            logging.debug(state)
            problem = MazeSearchProblem(state)
            srch = time_and_run_algorithm(problem, heuristic)
            stats = problem.__repr__()
            if None != srch and None != srch.solution():
                solution = srch.solution()
                if None != solution:
                    for action in solution:
                        search_results_deque.append(action)
            search_completed = True
        try:
            action = search_results_deque.popleft()
            if None != kb and shreik_heard:
                # If we heard a shreik, check if the candidate is not a known hawk
                (newrow, newcol) = NextMoveHelper.get_updated_row_col(row, col, action)
                if kb.ask_if_location_hawk((newrow, newcol)):
                    # If we hit a known hawk, then just treat the hawk as if it
                    # was a wall, and rerun the search
                    logging.info(f"Location {newrow}, {newcol} is a hawk, replanning")
                    known_hawks.append((newrow, newcol,))
                    search_completed = False
                    search_results_deque.clear()
                    return program(copy.deepcopy(percepts), get_stats=False, recursed=True)
        except IndexError:
            action = None
        return action

    return program

"""
1. The symbols are of two types, and have the forms:
    NOTHAWK_055_021
    NOTSHREIK_001_002
    WALL_001_002
2. For every piece of the wall, assert that it is not a hawk, example
   if there is a wall at 2, 2, assert:
       WALL_001_002 ==> NOTHAWK_001_002
3. For every position (i, j) Assert:
    (NOTSHREIK_UP & NOTSHREIK_DOWN & NOTSHREIK_LEFT & NOTSHREIK_RIGHT) ==> NOTHAWK
"""
class SnakeKnowledgeBaseToDetectHawk(object):
    USE_DEFAULT_ALGORITHM = 0
    USE_FOL_BC = 1
    USE_FOL_FC = 2 # This is very very slow
    def __init__(self, initial_matrix, dimensions, algorithm=USE_DEFAULT_ALGORITHM):
        self.matrix = initial_matrix
        self.total_perf = 0
        self.total_count = 0
        self.clauses = []
        self.tell_count = 0
        self.tell_perf = 0
        self.ask_perf = 0
        self.ask_count = 0
        (self.rows, self.cols) = tuple(dimensions)
        if SnakeKnowledgeBaseToDetectHawk.USE_DEFAULT_ALGORITHM == algorithm:
            self.kb = PropDefiniteKB()
        else:
            self.kb = FolKB()
        self.algorithm = algorithm
        if None != self.kb:
            self.create_base_rules()

    def __del__(self):
        if not g_profile_knowledgebase:
            return
        if self.algorithm == SnakeKnowledgeBaseToDetectHawk.USE_DEFAULT_ALGORITHM:
            print("Using pl_fc_entails")
        elif self.algorithm == SnakeKnowledgeBaseToDetectHawk.USE_FOL_FC:
            print("Using fol_fc_ask")
        elif self.algorithm == SnakeKnowledgeBaseToDetectHawk.USE_FOL_BC:
            print("Using fol_bc_ask")
        else:
            assert(False)
        if self.ask_count > 0:
            avg = self.ask_perf / self.ask_count
            print(f"ask() called {self.ask_count} times with average {avg} seconds")
        if self.tell_count > 0:
            avg = self.tell_perf / self.tell_count
            print(f"tell() called {self.ask_count} times with average {avg} seconds")
        print(f"n(Clauses) = {len(self.kb.clauses)}")

    def append_clause(self, clause):
        if clause not in self.clauses:
            logging.debug("Adding " + clause)
            self.clauses.append(clause)
            if g_profile_knowledgebase:
                time1 = time.perf_counter()
            self.kb.tell(expr(clause))
            if g_profile_knowledgebase:
                time2 = time.perf_counter()
                time2 = time2 - time1
                self.tell_perf += time2
                self.tell_count += 1


    def create_simple_rules(self):
        for i in range(self.rows):
            for j in range(self.cols):
                hawk = Utils.get_logic_symbol("HAWK", (i, j))
                nothawk = Utils.get_logic_symbol("NOTHAWK", (i, j))
                shreik = Utils.get_logic_symbol("SHREIK", (i, j))
                notshreik = Utils.get_logic_symbol("NOTSHREIK", (i, j))
                wall = Utils.get_logic_symbol("WALL", (i, j))
                # WALL ==> NOTHAWK
                self.append_clause("%s ==> %s" % (wall, nothawk))
                # SHREIK ==> NOTHAWK
                self.append_clause("%s ==> %s" % (shreik, nothawk))
                # NOTSHREIK ==> NOTHAWK
                self.append_clause("%s ==> %s" % (notshreik, nothawk))
                # Create rules for walls, doors, and grow/shrink
                c = self.matrix[i][j]
                if c in list("#DGS"):
                    clause = Utils.get_logic_symbol("WALL", (i, j))
                    self.append_clause(clause)
                    clause = Utils.get_logic_symbol("NOTHAWK", (i, j))
                    self.append_clause(clause)

    def create_compound_clauses1_helper(self, array):
        ret = []
        for i in range(len(array)):
            a = copy.deepcopy(array)
            b = a[i]
            del(a[i])
            ret.append((b, a,))
        return ret

    def create_compound_clauses1(self):
        for i in range(self.rows):
            for j in range(self.cols):
                hawk = Utils.get_logic_symbol("HAWK", (i, j))
                nothawk = Utils.get_logic_symbol("NOTHAWK", (i, j))
                shreik = Utils.get_logic_symbol("SHREIK", (i, j))
                notshreik = Utils.get_logic_symbol("NOTSHREIK", (i, j))
                wall = Utils.get_logic_symbol("WALL", (i, j))
                adj = Utils.get_adjacent_squares((i, j), (self.rows, self.cols))
                # HAWK ==> SHREIK1, HAWK ==> SHREIK2 ...
                for a in adj:
                    a_shreik = Utils.get_logic_symbol("SHREIK", a)
                    self.append_clause("%s ==> %s" % (hawk, a_shreik))
                # NOTSHREIK ==> NOTHAWK1, NOTSHREIK => NOTHAWK2, ...
                for a in adj:
                    a_nothawk = Utils.get_logic_symbol("NOTHAWK", a)
                    self.append_clause("%s ==> %s" % (notshreik, nothawk))
                # NOTHAWK1 & NOTHAWK2 & NOTHAWK3 & SHREIK ==> HAWK4
                for (hk, nthkarr) in self.create_compound_clauses1_helper(adj):
                    hk = Utils.get_logic_symbol("HAWK", hk)
                    nthkarr = [Utils.get_logic_symbol("NOTHAWK", i) for i in nthkarr]
                    nthkarr.append(shreik)
                    lhs = " & ".join(nthkarr)
                    clause = "%s ==> %s" % (lhs, hk)
                    self.append_clause(clause)
                # NOTSHREIK1 & NOTSHREIK2 & NOTSHREIK3 & NOTSHREIK4 ==> NOTHAWK
                nshrk = [Utils.get_logic_symbol("NOTSHREIK", a) for a in adj]
                nshrk = " & ".join(nshrk)
                self.append_clause("%s ==> %s" % (nshrk, nothawk))

    def create_base_rules(self):
        self.create_simple_rules()
        self.create_compound_clauses1()
        logging.debug(f"Num Clauses = {len(self.kb.clauses)}")

    def get_clauses(self):
        return self.kb.clauses

    def tell_location_safe(self, location):
        """
        - Current location doesn't have a shreik
        - tell that the current location does not have a hawk
        """
        notshreik = Utils.get_logic_symbol("NOTSHREIK", location)
        nothawk = Utils.get_logic_symbol("NOTHAWK", location)
        self.append_clause(notshreik)
        self.append_clause(nothawk)

    def tell_location_nothawk(self, location):
        nothawk = Utils.get_logic_symbol("NOTHAWK", location)
        shreik = Utils.get_logic_symbol("SHREIK", location)
        self.append_clause(nothawk)
        self.append_clause(shreik)

    def ask_if_location_not_hawk(self, location):
        print("In ask")
        hwk = expr(Utils.get_logic_symbol("NOTHAWK", location))
        fn = pl_fc_entails
        fn = fol_bc_ask if self.algorithm == SnakeKnowledgeBaseToDetectHawk.USE_FOL_BC else fn
        fn = fol_fc_ask if self.algorithm == SnakeKnowledgeBaseToDetectHawk.USE_FOL_FC else fn
        if g_profile_knowledgebase:
            time1 = time.perf_counter()
        gen = fn(self.kb, hwk)
        if g_profile_knowledgebase:
            time2 = time.perf_counter()
            time2 = time2 - time1
            print(f"Ask took {time2}")
            self.ask_perf += time2
            self.ask_count += 1
        ret = False
        if (isinstance(gen, bool)):
            ret = gen
        else:
            for i in gen:
                ret = True
        logging.info(f"checking if location is not hawk {location} = {ret}")
        return ret

    def ask_if_location_hawk_maybe(self, location):
        return not self.ask_if_location_not_hawk(location)

    def ask_if_location_hawk(self, location):
        hwk = expr(Utils.get_logic_symbol("HAWK", location))
        fn = pl_fc_entails
        fn = fol_bc_ask if self.algorithm == SnakeKnowledgeBaseToDetectHawk.USE_FOL_BC else fn
        fn = fol_fc_ask if self.algorithm == SnakeKnowledgeBaseToDetectHawk.USE_FOL_FC else fn
        if g_profile_knowledgebase:
            time1 = time.perf_counter()
        gen = fn(self.kb, hwk)
        if g_profile_knowledgebase:
            time2 = time.perf_counter()
            time2 = time2 - time1
            self.ask_perf += time2
            self.ask_count += 1
        ret = False
        if (isinstance(gen, bool)):
            ret = gen
        else:
            for i in gen:
                ret = True
        logging.info(f"checking if location is hawk {location} = {ret}")
        return ret

def RunAgentAlgorithm(program, mazeString: str):
    global g_state_print_same_place_loop_count
    global g_state_refresh_sleep
    global g_curses_available
    env = TwoDMaze(mazeString)
    agent = TwoDAgent(program)
    ag_x, ag_y = get_agent_location_from_maze_string(mazeString)
    assert(-1 != ag_x and -1 != ag_y)
    env.add_thing(agent, (ag_x,ag_y))
    env.initial_agent_location = (ag_x, ag_y)
    while not env.is_done():
        env.step()
        loop_count = g_state_print_same_place_loop_count if g_curses_available else 1
        for i in range(loop_count):
            env.print_state()
            if (0 != g_state_refresh_sleep):
                time.sleep(g_state_refresh_sleep)
    try:
        statsString = f"Stats = {program(None, get_stats=True)}"
    except:
        statsString = "Search Stats not available"
    del env
    print(statsString)

def process():
    #RunAgentAlgorithm(SimpleReflexProgram(), smallMaze)
    #RunAgentAlgorithm(GoalDrivenAgentProgram(), smallMaze)
    #RunAgentAlgorithm(SimpleReflexProgram(), smallMazeWithPower)
    #RunAgentAlgorithm(SimpleReflexProgram(), mediumMaze2)
    #RunAgentAlgorithm(GoalDrivenAgentProgram(), mediumMaze2)
    #RunAgentAlgorithm(SimpleReflexProgram(False), largeMaze)
    #RunAgentAlgorithm(SimpleReflexProgram(True), largeMaze)
    #RunAgentAlgorithm(GoalDrivenAgentProgram(), largeMaze)
    #RunAgentAlgorithm(UtilityBasedAgentProgram(), largeMaze)
    #RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), smallMaze)
    #RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), mediumMaze)
    #RunAgentAlgorithm(UtilityBasedAgentProgram(use_inference=True), smallHawkTestMaze2)
    #RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True, use_inference=False), smallHawkTestMaze2)
    #RunAgentAlgorithm(GoalDrivenAgentProgram(use_inference=True), smallHawkTestMaze2)
    #RunAgentAlgorithm(SimpleReflexProgram(use_inference=True), smallHawkTestMaze2)
    pass

g_run_profiles = {
            1: {
                "description": "Simple reflex agent with small maze",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(), smallMaze)"]
                },
            2: {
                "description": "Simple reflex agent with medium maze",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(), mediumMaze)"]
                },
            3: {
                "description": "Simple reflex agent with medium maze 2",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(), mediumMaze2)"]
                },
            4: {
                "description": "Simple reflex agent with large maze with weighted randomized selection",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(), largeMaze)"]
                },
            5: {
                "description": "Simple reflex agent with small maze with weighted randomized selection",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(weighted_rand_sel=True), smallMaze)"]
                },
            6: {
                "description": "Simple reflex agent with medium maze with weihted randomized selection",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(weighted_rand_sel=True), mediumMaze)"]
                },
            7: {
                "description": "Simple reflex agent with medium maze 2 with weighted randomized selection",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(weighted_rand_sel=True), mediumMaze2)"]
                },
            8: {
                "description": "Simple reflex agent with large maze with weighted randomized selection",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(weighted_rand_sel=True), largeMaze)"]
                },
            9: {
                "description": "Goal Driven (norandom) with Small Maze",
                "commands": ["RunAgentAlgorithm(GoalDrivenAgentProgram(norandom=True), smallMaze)"]
                },
            10: {
                "description": "Goal Driven (norandom) with Medium Maze",
                "commands": ["RunAgentAlgorithm(GoalDrivenAgentProgram(norandom=True), mediumMaze)"]
                },
            11: {
                "description": "Goal Driven (norandom) with Large Maze",
                "commands": ["RunAgentAlgorithm(GoalDrivenAgentProgram(norandom=True), largeMaze)"]
                },
            12: {
                "description": "Goal Driven (with random) with Small Maze",
                "commands": ["RunAgentAlgorithm(GoalDrivenAgentProgram(), smallMaze)"]
                },
            13: {
                "description": "Goal Driven (with random) with Small Maze",
                "commands": ["RunAgentAlgorithm(GoalDrivenAgentProgram(), mediumMaze)"]
                },
            14: {
                "description": "Goal Driven (with random) with Small Maze",
                "commands": ["RunAgentAlgorithm(GoalDrivenAgentProgram(), largeMaze)"]
                },
            15: {
                "description": "Utility based with Small Maze",
                "commands": ["RunAgentAlgorithm(UtilityBasedAgentProgram(), smallMaze)"]
                },
            16: {
                "description": "Utility based with Small Maze",
                "commands": ["RunAgentAlgorithm(UtilityBasedAgentProgram(), mediumMaze)"]
                },
            17: {
                "description": "Utility based with Small Maze",
                "commands": ["RunAgentAlgorithm(UtilityBasedAgentProgram(), largeMaze)"]
                },
            18: {
                "description": "Depth-first search, tiny maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=depth_first_graph_search), tinyMaze)"]
                },
            19: {
                "description": "Depth-first search, small maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=depth_first_graph_search), smallMaze)"]
                },
            20: {
                "description": "Depth-first search, medium maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=depth_first_graph_search), mediumMaze)"]
                },
            21: {
                "description": "Depth-first search, large maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=depth_first_graph_search), largeMaze)"]
                },
            22: {
                "consider_history": True,
                "description": "Depth-first search, tiny maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=depth_first_graph_search), tinyMaze)"]
                },
            23: {
                "consider_history": True,
                "description": "Depth-first search, small maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=depth_first_graph_search), smallMaze)"]
                },
            24: {
                "consider_history": True,
                "description": "Depth-first search, medium maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=depth_first_graph_search), mediumMaze)"]
                },
            25: {
                "consider_history": True,
                "description": "Depth-first search, large maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=depth_first_graph_search), largeMaze)"]
                },
            26: {
                "description": "breadth-first-graph search, tiny maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), tinyMaze)"]
                },
            27: {
                "description": "breadth-first-graph search, small maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), smallMaze)"]
                },
            28: {
                "description": "breadth-first-graph search, medium maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), mediumMaze)"]
                },
            29: {
                "description": "breadth-first-graph search, large maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), largeMaze)"]
                },
            30: {
                "consider_history": True,
                "description": "breadth-first-graph search, tiny maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), tinyMaze)"]
                },
            31: {
                "consider_history": True,
                "description": "breadth-first-graph search, small maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), smallMaze)"]
                },
            32: {
                "consider_history": True,
                "description": "breadth-first-graph search, medium maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), mediumMaze)"]
                },
            33: {
                "consider_history": True,
                "description": "breadth-first-graph search, large maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=breadth_first_graph_search), largeMaze)"]
                },
            34: {
                "description": "uniform-cost-search search, tiny maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=uniform_cost_search), tinyMaze)"]
                },
            35: {
                "description": "uniform-cost-search search, small maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=uniform_cost_search), smallMaze)"]
                },
            36: {
                "description": "uniform-cost-search search, medium maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=uniform_cost_search), mediumMaze)"]
                },
            37: {
                "description": "uniform-cost-search search, large maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=uniform_cost_search), largeMaze)"]
                },
            38: {
                "consider_history": True,
                "description": "uniform-cost-search search, tiny maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=uniform_cost_search), tinyMaze)"]
                },
            39: {
                "consider_history": True,
                "description": "uniform-cost-search search, small maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=uniform_cost_search), smallMaze)"]
                },
            40: {
                "consider_history": True,
                "description": "uniform-cost-search search, medium maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=uniform_cost_search), mediumMaze)"]
                },
            41: {
                "consider_history": True,
                "description": "uniform-cost-search search, large maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=uniform_cost_search), largeMaze)"]
                },
            42: {
                "description": "greedy_best_first_graph_search search, tiny maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=greedy_best_first_graph_search, useheuristic=True), tinyMaze)"]
                },
            43: {
                "description": "greedy_best_first_graph_search search, small maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=greedy_best_first_graph_search, useheuristic=True), smallMaze)"]
                },
            44: {
                "description": "greedy_best_first_graph_search search, medium maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=greedy_best_first_graph_search, useheuristic=True), mediumMaze)"]
                },
            45: {
                "description": "greedy_best_first_graph_search search, large maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=greedy_best_first_graph_search, useheuristic=True), largeMaze)"]
                },
            46: {
                "consider_history": True,
                "description": "greedy_best_first_graph_search search, tiny maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=greedy_best_first_graph_search, useheuristic=True), tinyMaze)"]
                },
            47: {
                "consider_history": True,
                "description": "greedy_best_first_graph_search search, small maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=greedy_best_first_graph_search, useheuristic=True), smallMaze)"]
                },
            48: {
                "consider_history": True,
                "description": "greedy_best_first_graph_search search, medium maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=greedy_best_first_graph_search, useheuristic=True), mediumMaze)"]
                },
            49: {
                "consider_history": True,
                "description": "greedy_best_first_graph_search search, large maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=greedy_best_first_graph_search, useheuristic=True), largeMaze)"]
                },
            50: {
                "description": "recursive_best_first_search search, tiny maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=recursive_best_first_search, useheuristic=True), tinyMaze)"]
                },
            51: {
                "description": "recursive_best_first_search search, small maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=recursive_best_first_search, useheuristic=True), smallMaze)"]
                },
            52: {
                "description": "recursive_best_first_search search, medium maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=recursive_best_first_search, useheuristic=True), mediumMaze)"]
                },
            53: {
                "description": "recursive_best_first_search search, large maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=recursive_best_first_search, useheuristic=True), largeMaze)"]
                },
            54: {
                "consider_history": True,
                "description": "recursive_best_first_search search, tiny maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=recursive_best_first_search, useheuristic=True), tinyMaze)"]
                },
            55: {
                "consider_history": True,
                "description": "recursive_best_first_search search, small maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=recursive_best_first_search, useheuristic=True), smallMaze)"]
                },
            56: {
                "consider_history": True,
                "description": "recursive_best_first_search search, medium maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=recursive_best_first_search, useheuristic=True), mediumMaze)"]
                },
            57: {
                "consider_history": True,
                "description": "recursive_best_first_search search, large maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=recursive_best_first_search, useheuristic=True), largeMaze)"]
                },
            58: {
                "description": "astar_search search, tiny maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), tinyMaze)"]
                },
            59: {
                "description": "astar_search search, small maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), smallMaze)"]
                },
            60: {
                "description": "astar_search search, medium maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), mediumMaze)"]
                },
            61: {
                "description": "astar_search search, large maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), largeMaze)"]
                },
            62: {
                "consider_history": True,
                "description": "astar_search search, tiny maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), tinyMaze)"]
                },
            63: {
                "consider_history": True,
                "description": "astar_search search, small maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), smallMaze)"]
                },
            64: {
                "consider_history": True,
                "description": "astar_search search, medium maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), mediumMaze)"]
                },
            65: {
                "consider_history": True,
                "description": "astar_search search, large maze (body-length considered)",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True), largeMaze)"]
                },
            66: {
                "consider_history": True,
                "description": "Inference Search (astar) based agent on tiny Maze with Hawk",
                "commands": ["RunAgentAlgorithm(SearchBasedAgentProgram(algorithm=astar_search, useheuristic=True, use_inference=True), tinyMazeWithHawk)"]
                },
            67: {
                "consider_history": True,
                "description": "Inference with Simple Reflex Agent Program (small Maze with Hawk)",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(use_inference=True), smallHawkTestMaze2)"]
                },
            68: {
                "consider_history": True,
                "description": "Inference with Simple Reflex Agent Program (medium Maze With Hawk)",
                "commands": ["RunAgentAlgorithm(SimpleReflexProgram(use_inference=True), mediumHawkTestMaze)"]
                },
            69: {
                "description": "inference with utility based agent program, large maze (body-length not considered)",
                "commands": ["RunAgentAlgorithm(UtilityBasedAgentProgram(use_inference=True), largeMazeWithHawk)"]
                },
        }

def print_configuration_help():
    global g_run_profiles, g_search_should_consider_history
    for i, j in g_run_profiles.items():
        print("%3d\t%s" % (i, j["description"]))

def main():
    global g_curses_available, g_suppress_state_printing, g_state_refresh_sleep, g_self_crossing_not_allowed
    global g_state_print_same_place_loop_count, g_tkinter_available, g_use_tkinter, g_pygame_available, g_use_pygame
    global g_agent_can_grow, g_agent_initial_max_length, g_profile_knowledgebase
    global g_run_profiles, g_search_should_consider_history, g_override_global_algorithm
    parser = argparse.ArgumentParser()
    parser.add_argument("-nonc", "--no-ncurses", help="Do not use ncurses", action="store_true")
    parser.add_argument("-ssp", "--suppress-state-printing",\
            help="Do not print the board matrix after each step", action="store_true")
    parser.add_argument("-rd", "--refresh-delay",default=0.005, help="Number of seconds between refreshes", type=float)
    parser.add_argument("-ac", "--allow-crossing-self", help="Allow crossing over one's body", action="store_true")
    parser.add_argument("-ng", "--no-graphics", help="Do not use graphics", action="store_true")
    parser.add_argument("-acg", "--agent-cannot-grow", help="Agent cannot grow", action="store_true")
    parser.add_argument("-amaxlen", "--agent-initial-max-length", type=int, help="Agent maximum lenth initially",\
                            default=8)
    parser.add_argument("-profkb", "--profile-knowledge-base", help="Print profiling information of knowledgebase",\
                            action="store_true")
    parser.add_argument("-config" "--configuration", type=int,\
            help="The configuration of the run, mandatory", default=999)
    parser.add_argument("-inferalgo", "--inference-algorithm", type=int, default=-1,
            help="0 - pl_fc_entails, 1 = fol_bc_ask, 2 = fol_fc_ask")
    args = parser.parse_args()
    g_curses_available = False if args.no_ncurses else g_curses_available
    g_suppress_state_printing = True if args.suppress_state_printing else g_suppress_state_printing
    g_state_refresh_sleep = 0 if args.refresh_delay < 0.0001 else args.refresh_delay
    g_self_crossing_not_allowed = not args.allow_crossing_self
    g_agent_can_grow = False if args.agent_cannot_grow else g_agent_can_grow
    g_override_global_algorithm = args.inference_algorithm if -1 != args.inference_algorithm else g_override_global_algorithm
    g_agent_initial_max_length = args.agent_initial_max_length if args.agent_initial_max_length >= 0\
            else g_agent_initial_max_length
    g_profile_knowledgebase = True if args.profile_knowledge_base else g_profile_knowledgebase
    if args.no_graphics:
        g_tkinter_available = g_use_tkinter = False
        g_pygame_available = g_use_pygame = False
    if g_suppress_state_printing:
        g_state_refresh_sleep = 0
        g_state_print_same_place_loop_count
    if 999 == args.config__configuration:
        print("Please specify the configuration with the -config flag, legend below:")
        print_configuration_help()
        print("-" * 120)
        parser.print_help()
        sys.exit(1)
    config = g_run_profiles[args.config__configuration]
    try:
        if config["consider_history"]:
            g_search_should_consider_history = True
    except:
        g_search_should_consider_history = False
    for i in config["commands"]:
        print(config["description"])
        print("-" * 120)
        print(config["commands"])
        time1 = time.perf_counter()
        eval(i)
        time1 = time.perf_counter() - time1
        print(f"TimeToRun = {time1}")
    print('*' * 120)

if "__main__" == __name__:
    main()
