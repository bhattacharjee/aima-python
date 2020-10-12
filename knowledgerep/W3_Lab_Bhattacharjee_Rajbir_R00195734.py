#!/usr/bin/env python3

import os,sys,inspect, random, copy
import itertools
import time
import argparse

# Import the AIMA libraries from the parent directory
try:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from search import Problem, astar_search, EightPuzzle, hill_climbing, simulated_annealing, simulated_annealing_full, NQueensProblem
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
        new_states = []
        for i in range(len(delta_states)):
            arr1 = list(delta_states[i])
            arr2 = list(state)
            arr3 = [a + b for a, b in zip(arr1, arr2)]
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
        return b

def my_heuristic(state):
    s = state.state
    s1 = (0, 0, 0, 1, 3, 3)
    m = 0
    for i, j in zip(s, s1):
        m += ((i - j) * (i - j))
    return m

def missionary_problem():
    print("*" * 80)
    print("Missionary problem, the encoding is a set of tuples")
    print("Encoding: (nBoat, nMissionaries, nCannibals, nBoats2, nMissionaries2, nCannibals2) eg. (1, 3, 3, 0, 0, 0)")
    print("The first three numbers denote the numbers of boats, missionaries, cannibals on the first side")
    print("The second three numbers denote the numbers of boats, missionaries, cannibals on the other side")
    print("The solution is displayed as the state after executing every move")
    srch = astar_search(MissionariesProblem(), my_heuristic)
    print('-' * 80)
    [print("%3d" % (i + 1), ". ", j) for i, j in enumerate(srch.solution())]
    print("*" * 80)

class MyEightPuzzle(EightPuzzle):
    def value(self, state):
        assert(isinstance(state, tuple))
        distance = 0
        for i in range(10):
            lc = abs(i//3 - state[i//3]) + abs(i%3 - state[i%3])
            distance += lc
        return distance

def EightPuzzleDriver():
    hill_solved_count = 0
    hill_attempted_count = 0
    sa_attempted_count = 0
    sa_solved_count = 0
    saf_attempted_count = 0
    saf_solved_count = 0
    solution = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    for i in itertools.permutations(list("012345678")):
        initial = tuple([int(j) for j in list(i)])
        my_8_pz = MyEightPuzzle(initial)

        hc = hill_climbing(my_8_pz)
        hill_attempted_count += 1
        if (solution == hc):
            print(f"Hill climbing solved {initial} -> {state}")
            hill_solved_count += 1
        
        my_8_pz = MyEightPuzzle(initial)
        sa = simulated_annealing(my_8_pz)
        sa_attempted_count += 1
        if (solution == sa):
            print(f"Simulated annealing solved {initial} -> {state}")
            sa_solved_count += 1

        my_8_pz = MyEightPuzzle(initial)
        saf = simulated_annealing_full(my_8_pz)
        saf_attempted_count += 1
        if (solution == saf):
            print(f"Simulated annealing full solved {initial} -> {state}")
            saf_solved_count += 1

        if hill_attempted_count > 1000:
            break
        
    print(f"8-puzzle: Hill climbing (solved / attempted):                     {hill_solved_count} / {hill_attempted_count}")
    print(f"8-puzzle: Simulated annealing (solved / attempted):               {sa_solved_count} / {sa_attempted_count}")
    print(f"8-puzzle: Simulated annealing full (solved / attempted):          {saf_solved_count} / {saf_attempted_count}")

class MyNQueen(NQueensProblem):
    def value(self, state):
        """Return number of conflicting queens for a given node"""
        num_conflicts = 0
        for (r1, c1) in enumerate(state):
            for (r2, c2) in enumerate(state):
                if (r1, c1) != (r2, c2):
                    num_conflicts += self.conflict(r1, c1, r2, c2)
        return -1 * num_conflicts

def NQueenDriver():
    attempted = 0
    hc_solved = 0
    sa_solved = 0
    saf_solved = 0

    for i in range(1000):
        attempted += 1

        hc = hill_climbing(MyNQueen(8))
        if -1 not in hc:
            hc_solved += 1
            print(f"hill_climbing solution: {hc}")
        
        sa = simulated_annealing(MyNQueen(8))
        if -1 not in sa:
            sa_solved += 1
            print(f"simulated annealing solution: {sa}")

        saf = simulated_annealing_full(MyNQueen(8))
        if -1 not in saf:
            saf_solved += 1
            print(f"Simulated annealing full solved: {saf}")
    print(f"N-Queen: Hill climbing (solved/attempted)                {hc_solved} / {attempted}")
    print(f"N-Queen: Simulated annealing (solved/attempted)          {sa_solved} / {attempted}")
    print(f"N-Queen: Simluated annealing full (solved/attempted)     {saf_solved} / {attempted}")




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-mc", "--missionary-cannibal", action="store_true", help="Solve the missionaries problem")
    parser.add_argument("-p8", "--puzzle-8", action="store_true", help="Solve the 8-puzzle")
    parser.add_argument("-nq", "--n-queen", action="store_true", help="Solve the N-Queens puzzle")
    args = parser.parse_args()
    if (args.missionary_cannibal):
        missionary_problem()
    if (args.puzzle_8):
        EightPuzzleDriver()
    if (args.n_queen):
        NQueenDriver()
    if (not args.missionary_cannibal and not args.puzzle_8 and not args.n_queen):
        parser.print_help()


if "__main__" == __name__:
    main()
