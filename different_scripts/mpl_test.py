from matplotlib import pyplot as plt
import numpy as np

data = np.linspace(0.1, 100, 1000)

plt.plot(data, np.log(data))

plt.savefig("test.png")
plt.show()

