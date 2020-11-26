#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(2, 2)
print(ax, type(ax), len(ax))

x = [10.09950494, 16.43167673, 27.03701167, 76.15773106 ]

ax[0][0].set(title="nSteps", xlabel="sqrt(n_squares)", ylabel="nSteps")
y1 = [15, 36, 77]
ax[0][0].plot(x[:3], y1, label="GBFS w/o Length", color="blue", marker='o')
y1 = [2.05, 3.655, 3.59, 547.19]
ax[0][0].plot(x, y1, label="A* w/o Length", color="green", marker='o')
y1 = [15]
ax[0][0].plot(x[:1], y1, label="RBFS w/o Length", color="red", marker='^')
ax[0][0].legend()
#fig.legend()

ax[0][1].set(title="Successors", xlabel="sqrt(n_squares)", ylabel="Successors")
y1 = [23, 39, 137, ]
ax[0][1].plot(x[:3], y1, label="GBFS w/o Length", color="blue", marker='o')
y1 = [28, 588, 198, 12305, ]
ax[0][1].plot(x, y1, label="A* w/o Length", color="green", marker='o')
y1 = [35]
ax[0][1].plot(x[:1], y1, label="RBFS w/o Length", color="red", marker='^')


ax[1][0].set(title="Search Time", xlabel="sqrt(n_squares)", ylabel="Search Time (s)")
y1 = [0.088, 0.293, 2.053, ]
ax[1][0].plot(x[:3], y1, label="GBFS w/o Length", color="blue", marker='o')
y1 = [0.085, 3.346, 3.213, 1100.5, ]
ax[1][0].plot(x, y1, label="A* w/o Length", color="green", marker='o')
y1 = [0.112]
ax[1][0].plot(x[:1], y1, label="RBFS w/o Length", color="red", marker='^')

ax[1][1].set(title="Memory", xlabel="sqrt(n_squares)", ylabel="MB")
y1 = [66.17, 66.51, 66.92, ]
ax[1][1].plot(x[:3], y1, label="GBFS w/o Length", color="blue", marker='o')
y1 = [66.47, 67.41, 67.11, 278.68, ]
ax[1][1].plot(x, y1, label="A* w/o Length", color="green", marker='o')
y1 = [66.4]
ax[1][1].plot(x[:1], y1, label="RBFS w/o Length", color="red", marker='^')

plt.suptitle("Informed Search\nBody Length/History Excluded")
plt.show()
