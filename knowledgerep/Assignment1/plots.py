#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(1, 2)
print(ax, type(ax), len(ax))

# Number of Steps
x = [16.43167673, 27.03701167, 76.15773106,]
y1 = [40, 3235, 650]

ax[0].set(title="Avg n(Steps)", xlabel="sqrt(n_squares)", ylabel="Avg Steps")
ax[0].plot(x, y1, label="Utility Based", color="blue")
ax[0].set_ylim(bottom=0)
ax[0].legend()



# PEAK MEMORY
y2 = [68.056, 66.45, 66.46]

ax[1].set(title="Peak Memory", xlabel="sqrt(n_squares)", ylabel="MB")
ax[1].plot(x, y2, label="Utility Based", color="blue")
ax[1].set_ylim(bottom=60)
ax[1].set_ylim(top=70)
ax[1].legend()



plt.gca().yaxis.set_minor_formatter(NullFormatter())
plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25, wspace=0.35)
plt.show()
