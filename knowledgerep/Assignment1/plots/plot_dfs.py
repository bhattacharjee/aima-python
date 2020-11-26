#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(2, 2)
print(ax, type(ax), len(ax))

x = [10.09950494, 16.43167673, 27.03701167]

ax[0][0].set(title="Goal Tests", xlabel="sqrt(n_squares)", ylabel="Goal Tests")
y1 = [24, 59, 251]
ax[0][0].plot(x, y1, label="Depth First w/o History", color="blue", marker='o')
y1 = [46, 116, 405]
ax[0][0].plot(x, y1, label="Depth First with History", color="red", marker='o')
ax[0][0].set_ylim(bottom=0)
fig.legend()

ax[0][1].set(title="States", xlabel="sqrt(n_squares)", ylabel="States")
y1 = [55, 157, 752]
ax[0][1].plot(x, y1, label="Depth First w/o History", color="blue", marker='o')
y1 = [62, 184, 718]
ax[0][1].plot(x, y1, label="Depth First with History", color="red", marker='o')
ax[0][1].set_ylim(bottom=0)


ax[1][0].set(title="Search Time", xlabel="sqrt(n_squares)", ylabel="Search Time (s)")
y1 = [0.019, 0.126, 1.581]
ax[1][0].plot(x, y1, label="Depth First w/o History", color="blue", marker='o')
y1 = [0.064, 0.413, 2.116]
ax[1][0].plot(x, y1, label="Depth First with History", color="red", marker='o')
ax[1][0].set_ylim(bottom=0)

ax[1][1].set(title="Memory", xlabel="sqrt(n_squares)", ylabel="MB")
y1 = [66.49, 68.04, 68.89]
ax[1][1].plot(x, y1, label="Depth First w/o History", color="blue", marker='o')
y1 = [66.48, 66.41, 67.6]
ax[1][1].plot(x, y1, label="Depth First with History", color="red", marker='o')

plt.gca().yaxis.set_minor_formatter(NullFormatter())
plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25, wspace=0.35)
plt.show()
