#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(2, 2)
print(ax, type(ax), len(ax))

x = [10.09950494, 16.43167673, 27.03701167]
x1 = [10.09950494, 27.03701167]

ax[0][0].set(title="nSteps", xlabel="sqrt(n_squares)", ylabel="nSteps")
y1 = [33, 110, 327]
ax[0][0].plot(x, y1, label="DFS with Length", color="blue", marker='o')
y1 = [15, 36, 53]
ax[0][0].plot(x, y1, label="BFS with Length", color="red", marker='o')
y1 = [15, 53, ]
ax[0][0].plot(x1, y1, label="UCS with Length", color="green", marker='o')
ax[0][0].set_ylim(bottom=0)
ax[0][0].legend()

ax[0][1].set(title="Successors", xlabel="sqrt(n_squares)", ylabel="Successors")
y1 = [45, 115, 404, ]
ax[0][1].plot(x, y1, label="DFS with Length", color="blue", marker='o')
y1 = [283, 219557, 227716, ]
ax[0][1].plot(x, y1, label="BFS with Length", color="red", marker='o')
y1 = [377, 231030]
ax[0][1].plot(x1, y1, label="UCS with Length", color="green", marker='o')


ax[1][0].set(title="Search Time", xlabel="sqrt(n_squares)", ylabel="Search Time (s)")
y1 = [0.064, 0.413, 2.116, ]
ax[1][0].plot(x, y1, label="DFS with Length", color="blue", marker='o')
y1 = [0.276, 2584.57, 2691.58, ]
ax[1][0].plot(x, y1, label="BFS with Length", color="red", marker='o')
y1 = [0.3912, 4681.72812]
ax[1][0].plot(x1, y1, label="UCS with Length", color="green", marker='o')

ax[1][1].set(title="Memory", xlabel="sqrt(n_squares)", ylabel="MB")
y1 = [66.48, 66.41, 67.6, ]
ax[1][1].plot(x, y1, label="DFS with Length", color="blue", marker='o')
y1 = [66.45, 309.58, 471.43, ]
ax[1][1].plot(x, y1, label="BFS with Length", color="red", marker='o')
y1 = [66.59, 476.1796875]
ax[1][1].plot(x1, y1, label="UCS with Length", color="green", marker='o')

fig.suptitle("Uninformed search\nLength/history of body considered\n(More states)")
plt.show()
