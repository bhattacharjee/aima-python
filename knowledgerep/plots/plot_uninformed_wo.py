#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(2, 2)
print(ax, type(ax), len(ax))

x = [10.09950494, 16.43167673, 27.03701167]

ax[0][0].set(title="nSteps", xlabel="sqrt(n_squares)", ylabel="nSteps")
y1 = [15, 36, 185,]
ax[0][0].plot(x, y1, label="DFS w/o Length", color="blue", marker='o')
y1 = [15, 36, 53,]
ax[0][0].plot(x, y1, label="BFS w/o Length", color="red", marker='o')
y1 = [15, 36, 53,]
ax[0][0].plot(x, y1, label="UCS w/o Length", color="green", marker='o')
ax[0][0].set_ylim(bottom=0)
ax[0][0].legend()
fig.legend()

ax[0][1].set(title="Successors", xlabel="sqrt(n_squares)", ylabel="Successors")
y1 = [23, 58, 250, ]
ax[0][1].plot(x, y1, label="DFS w/o Length", color="blue", marker='o')
y1 = [148, 2337, 428, ]
ax[0][1].plot(x, y1, label="BFS w/o Length", color="red", marker='o')
y1 = [162, 2526, 436]
ax[0][1].plot(x, y1, label="UCS w/o Length", color="green", marker='o')


ax[1][0].set(title="Search Time", xlabel="sqrt(n_squares)", ylabel="Search Time (s)")
y1 = [0.019, 0.126, 1.581]
ax[1][0].plot(x, y1, label="DFS w/o Length", color="blue", marker='o')
y1 = [0.167, 5.701, 2.85, ]
ax[1][0].plot(x, y1, label="BFS w/o Length", color="red", marker='o')
y1 = [0.228, 7.013, 3.478]
ax[1][0].plot(x, y1, label="UCS w/o Length", color="green", marker='o')

ax[1][1].set(title="Memory", xlabel="sqrt(n_squares)", ylabel="MB")
y1 = [66.49, 68.04, 68.89, ]
ax[1][1].plot(x, y1, label="DFS w/o Length", color="blue", marker='o')
y1 = [68.09, 71.2, 67.815, ]
ax[1][1].plot(x, y1, label="BFS w/o Length", color="red", marker='o')
y1 = [66.4, 72.89, 67.851, ]
ax[1][1].plot(x, y1, label="UCS w/o Length", color="green", marker='o')

plt.gca().yaxis.set_minor_formatter(NullFormatter())
plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25, wspace=0.35)
plt.show()
