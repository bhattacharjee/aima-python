#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(2, 2)
print(ax, type(ax), len(ax))

x = [10.09950494, 16.43167673, 27.03701167, 76.15773106 ]

ax[0][0].set(title="nSteps", xlabel="sqrt(n_squares)", ylabel="nSteps")
y1 = [15, 36, 81, 179, ]
ax[0][0].plot(x, y1, label="GBFS w/o Length", color="blue", marker='o')
y1 = [15, 28, 41, ]
ax[0][0].plot(x[:3], y1, label="A* w/o Length", color="green", marker='o')
y1 = [15, 36, ]
ax[0][0].plot(x[:2], y1, label="RBFS w/o Length", color="red", marker='^')
ax[0][0].legend()

ax[0][1].set(title="Successors", xlabel="sqrt(n_squares)", ylabel="Successors")
y1 = [27, 43, 8851, 340, ]
ax[0][1].plot(x, y1, label="GBFS w/o Length", color="blue", marker='o')
y1 = [24, 30041, 24516, ]
ax[0][1].plot(x[:3], y1, label="A* w/o Length", color="green", marker='o')
y1 = [30, 113372, ]
ax[0][1].plot(x[:2], y1, label="RBFS w/o Length", color="red", marker='^')


ax[1][0].set(title="Search Time", xlabel="sqrt(n_squares)", ylabel="Search Time (s)")
y1 = [0.061, 0.269, 100.557, 21.85, ]
ax[1][0].plot(x, y1, label="GBFS w/o Length", color="blue", marker='o')
y1 = [0.071, 470.117, 546.872, ]
ax[1][0].plot(x[:3], y1, label="A* w/o Length", color="green", marker='o')
y1 = [0.091, 488.49, ]
ax[1][0].plot(x[:2], y1, label="RBFS w/o Length", color="red", marker='^')

ax[1][1].set(title="Memory", xlabel="sqrt(n_squares)", ylabel="MB")
y1 = [66.51, 66.43, 87.76, 75.35, ]
ax[1][1].plot(x, y1, label="GBFS w/o Length", color="blue", marker='o')
y1 = [66.52, 101.93, 124.99, ]
ax[1][1].plot(x[:3], y1, label="A* w/o Length", color="green", marker='o')
y1 = [66.53, 66.38, ]
ax[1][1].plot(x[:2], y1, label="RBFS w/o Length", color="red", marker='^')

fig.suptitle("Informed Search\nLength/History of body taken into account\n(more states)")
plt.show()
