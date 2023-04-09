import matplotlib.pyplot as plt
import numpy as np


with open('jep.txt', 'r') as aa:
    y = np.array([int(line) for line in aa])

with open('jep2.txt', 'r') as bb:
    a = np.array([int(line) for line in bb])

x = np.array([a for a in np.arange(0, len(y))])
# b = [30000 for i in range(len(y))]
# for num in a:
#     b[num] = y[num]
b = [y[i] for i in a]


plt.scatter(x, y, color='blue', s=3)
plt.scatter(a, b, color='red')
plt.show()