#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(1, 2)
print(ax, type(ax), len(ax))

# Number of Steps
x = [16.43167673, 27.03701167, 76.15773106,]
y1 = [111, 4058, 8117]
ax[0].set(title="Avg n(Steps)", xlabel="sqrt(n_squares)", ylabel="Avg Steps")
ax[0].plot(x, y1, label="Goal Driven", color="blue", marker='o')
ax[0].set_ylim(bottom=0)
ax[0].legend()



# PEAK MEMORY
y2 = [66.43, 66.43, 66.11]
y2 = [66.42, 66.36, 67.99]
ax[1].set(title="Peak Memory", xlabel="sqrt(n_squares)", ylabel="MB")
ax[1].plot(x, y2, label="Goal Driven", color="blue", marker='o')
ax[1].legend()


fig.suptitle("Goal Driven Agent\nnSteps = Moves the snake makes to the goal")
plt.show()
