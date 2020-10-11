#!/usr/bin/env python3

import os,sys,inspect, random, copy
import itertools
import time

# Import the AIMA libraries from the parent directory
try:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from search import Problem, astar_search
except:
    print("Could not import from parent folder... Exiting")
    sys.exit(1)


# Missionaries Problem: Encoding
# State = {n(Boates-on-1), n(Missionaries-on-1), n(Cannibals-on-1), n(Boats-on-2), n(Missionaries-on-2), n(Cannibals-on-2)}
# Initial state: (1, 3, 3, 0, 0 0)
# Final State (0, 0, 0, 1, 3, 3)

class MissionariesProblem(Problem):
    def __init__(self):
        self.initial = (1, 3, 3, 0, 0, 0)
        self.goal = (0, 0, 0, 1, 3, 3)
        super().__init__(self.initial, self.goal)
    
    def is_state_valid(self, state, orig_state):
        for x in state:
            if x < 0:
                return False
        for x in state:
            if x > 3:
                return False
        if (state[0] + state[3]) != 1: # num-boats = 1
            return False
        if (state[1] + state[4]) != 3 or (state[2] + state[5]) != 3: # n-miss = n-can = 3
            return False
        if (state[1] != 0 and (state[1] < state[2])):
            return False
        if (state[4] != 0 and (state[4] < state[5])):
            return False
        s1 = state[0] + state[1] + state[2]
        s2 = orig_state[0] + orig_state[1] + orig_state[2]
        d = s1 - s2
        if (d > 3 or d < -3): # Cannot move more than 3 items at a time
            return False
        if (orig_state[0] == state[0]): # Have to move boat
            return False
        return True

    # We can short-circuit the work here and avoid writing a lot of code
    # By returning the new state itself in actions
    def actions(self, state):
        # Create an array of what should be added to each state. This will
        # Result in invalid states, but we'll weed them out by calling is_valid_state
        # Each delta will be of the form of (1, -1, 0, 1, 0, 1),
        # Formally, delta = {s1, s2, s3, s4, s5, s6} where si belongs to {-1, 0, 1}
        # This delta will be added to the states
        orig_state = copy.deepcopy(state)
        delta_states =[ \
            (-1, 0, -2, 1, 0, 2),  # Right 2C 1B
            (-1, -2, 0, 1, 2, 0),  # Right 2M 1B
            (-1, 0, -1, 1, 0, 1),  # Right 1C 1B
            (-1, -1, 0, 1, 1, 0),  # Right 1M 1B
            (-1, -1, -1, 1, 1, 1), # Right 1C 1M 1B
            (1, 0, 2, -1, 0, -2),  # Left 2C 1B
            (1, 2, 0, -1, -2, 0),  # Left 2M 1B
            (1, 0, 1, -1, 0, -1),  # Left 1C 1B
            (1, 1, 0, -1, -1, 0),  # Left 1M 1B
            (1, 1, 1, -1, -1, -1)  # Left 1C 1M 1B
            ]
        temp_new_states = []
        new_states = []
        for i in range(len(delta_states)):
            arr1 = list(delta_states[i])
            arr2 = list(state)
            arr3 = [a + b for a, b in zip(arr1, arr2)]
            temp_new_states.append(tuple(arr3))
            if (self.is_state_valid(tuple(arr3), orig_state)):
                new_states.append(tuple(arr3))
        return new_states

    def result(self, state, action):
        assert(True == isinstance(action, tuple))
        return copy.deepcopy(action)
        
    def goal_test(self, state):
        return (0, 0, 0, 1, 3, 3) == state

    def value(self, state):
        b2 = state[3] + state[4] + state[5]
        b1 = state[0] + state[1] + state[2]

def my_heuristic(state):
    s = state.state
    s1 = (0, 0, 0, 1, 3, 3)
    m = 0
    for i, j in zip(s, s1):
        m += ((i - j) * (i - j))
    return m

def missionary_problem():
    srch = astar_search(MissionariesProblem(), my_heuristic)
    print(srch.solution())

def main():
    missionary_problem()

if "__main__" == __name__:
    main()