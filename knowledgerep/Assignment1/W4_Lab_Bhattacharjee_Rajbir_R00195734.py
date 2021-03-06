#!/usr/bin/env python3

import sys
import os, inspect

try:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir)
    from logic import *
except:
    print("Could not import")
    sys.exit(1)

def question_b():
    entails_table = [\
            ["False", "True"], \
            ["True", "False"], \
            ["A & B", "(A ==> B) & (B ==> A)"], \
            ["(A ==> B) & (B ==> A)", "A | B"], \
            ["(A ==> B) & (B <== A)", "~A | B"], \
            ["(A & B) ==> C", "(A ==> C) | (B ==> C)"] \
            ]
    for i in entails_table:
        print(f"Checking if {i[0]} entails {i[1]}")
        try:
            print(tt_entails(expr(i[0]), expr(i[1])))
        except:
            print(tt_entails(to_cnf(expr(i[0])), to_cnf(expr(i[1]))))

    print("Checking for (C ∨ (¬A ∧ ¬B)) ≡ ((A ⇒ C) ∧ (B ⇒ C))")
    b1 = tt_entails(expr("C | (~A | ~B)"), expr("(A ==> C) & (B ==> C)"))
    b2 = tt_entails(expr("(A ==> C) & (B ==> C)"), expr("C | (~A | ~B)"))
    print(b1 and b2)

    entails_table = [\
            ["(A | B) & (~C | ~D | E)", "(A | B)"], \
            ["(A | B) & (~C | ~D | E)", "(A | B) & (~D | E)"]]
    for i in entails_table:
        print(f"Checking if {i[0]} entails {i[1]}")
        try:
            print(tt_entails(expr(i[0]), expr(i[1])))
        except:
            print(tt_entails(to_cnf(expr(i[0])), to_cnf(expr(i[1]))))


    print("Checking satisfiability of (A | B) & (~(A ==> B))")
    print(dpll_satisfiable(expr("(A | B) & (~(A ==> B))")))

    print("checking satisfiability of ((A ==> B) & (A <== B)) & (~A | B)")
    print(dpll_satisfiable(expr("((A ==> B) & (A <== B)) & (~A | B)")))

    n1 = dpll_satisfiable(expr("(((A ==> B) & (A <== B)) ==> C) & (((A ==> B) & (A <== B)) <== C)"))
    n2 = dpll_satisfiable(expr("(A ==> B) & (A <== B)"))
    if (len(n1) == (len(n2) * 2)):
        print("Both of them have the same number of models")
    print("---->", len(n1), f"\n{n1}", len(n2), f"\n{n2}")

question_b()
