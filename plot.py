import matplotlib.pyplot as plt
import numpy as np


with open('jep.txt', 'r') as aa:
    y = np.array([int(line) for line in aa])

with open('jep2.txt', 'r') as bb:
    a = []
    c = []
    for line in bb:
        if int(line)>0:
            a.append(int(line)-1)
        elif int(line)<0:
            c.append(-int(line)-1)

x = np.array([a for a in np.arange(0, len(y))])
b = [y[i] for i in a]
d = [y[i] for i in c]
print(len(a))
print(len(c))


plt.scatter(x, y, color='blue', s=5)
plt.scatter(a, b, color='red')
plt.scatter(c, d, color='black')
plt.show()