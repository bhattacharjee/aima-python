#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(1, 3)
print(ax, type(ax), len(ax))

# Number of Steps
x = [16.43167673, 27.03701167, 76.15773106,]

ax[0].set(title="Avg n(Steps)", xlabel="sqrt(n_squares)", ylabel="Avg Steps")
y1 = [40, 3235, 650]
ax[0].plot(x, y1, label="Utility Based", color="blue", marker='o')
y1 = [537.64, 3590, 1311]
ax[0].plot(x, y1, label="Simple Reflex (weighted)", color="red", marker='o')
y1 = [3459, 7768.92, 91500.6]
ax[0].plot(x, y1, label="Simple Reflex (not weighted)", color="magenta", marker='o')
y1 = [111, 4058, 8117]
ax[0].plot(x, y1, label="Goal Driven", color="green", marker='o')


ax[0].set_ylim(bottom=0)
ax[0].legend()


# PEAK MEMORY
ax[1].set(title="Peak Memory", xlabel="sqrt(n_squares)", ylabel="MB")
ax[1].set_ylim(bottom=60)
ax[1].set_ylim(top=70)

y1 = [68.056, 66.45, 66.46]
ax[1].plot(x, y1, label="Utility Based", color="blue", marker='o')
y1 = [66.43, 66.43, 68.05]
ax[1].plot(x, y1, label="Simple Reflex (weighted)", color="red", marker='o')
y1 = [66.42, 66.36, 67.99]
ax[1].plot(x, y1, label="Goal Driven", color="green", marker='o')
y1 = [66.43, 66.43, 66.11]
ax[1].plot(x, y1, label="Simple Reflex (non weighted)", color="magenta", marker='o')
ax[1].legend()

ax[2].set(title="CPU", xlabel="sqrt(n_squares)", ylabel="Time (System+User)")
y1 = [1.46, 2.561, 2.31]
ax[2].plot(x, y1, label="Utility Based", color="blue", marker='o')
y1 = [2.58, 2.105, 2.67]
ax[2].plot(x, y1, label="Simple Reflex (weighted)", color="red", marker='o')
y1 = [1.129, 2.206, 2.206]
ax[2].plot(x, y1, label="Goal Driven", color="green", marker='o')
y1 = [3.13, 4.45, 75.147]
ax[2].plot(x, y1, label="Simple Reflex (non weighted)", color="magenta", marker='o')
ax[2].legend()

fig.suptitle("All Agents Compared")

plt.show()
