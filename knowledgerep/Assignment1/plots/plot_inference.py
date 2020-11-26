#!/usr/bin/python3

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

fig, ax = plt.subplots(1, 3)
print(ax, type(ax), len(ax))

# Number of Steps
x = [10.09950494, 16.43167673, 27.03701167, 76.15773106, ]

ax[0].set(title="Sentences in KB", xlabel="sqrt(n_squares)", ylabel="n(Sentences)")
y1 = [1242, 3282, 9084, 70894, ]
ax[0].plot(x, y1, color="blue", marker='o')

x = y1
y1 = [0.185, 1.23, 12.003, 179.09]
ax[1].set(title="Query Latency", xlabel="n(Sentences)", ylabel="Time (s)")
ax[1].plot(x, y1, label="pl_fc_entails", marker='o')

y1 = [3.00E-06, 3.66E-06, 3.00E-06, 4.00E-06, ]
ax[1].set(title="Query Latency", xlabel="n(Sentences)", ylabel="Time (s)")
ax[1].plot(x, y1, label="fol_bc_ask", marker='o')
ax[1].legend()

y1 = [67.64, 70.468, 79.69, 166.69, ]
ax[2].set(title="Peak Memory Usage", xlabel="n(Sentences)", ylabel="MB")
ax[2].plot(x, y1, label="pl_fc_entails", marker='o')
y1 = [67.6, 70.1, 69.91, 75.35, ]
ax[2].plot(x, y1, label="fol_bc_ask", marker='o')
ax[2].legend()


fig.suptitle("Inference Searches Compared")

plt.show()
