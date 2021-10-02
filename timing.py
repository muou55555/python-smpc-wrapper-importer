import matplotlib.pyplot as plt

sizes = [3, 3, 3, 9, 12, 12, 12, 18, 30, 30, 38, 38, 38, 41, 48, 50, 50]#54
times = [5, 6, 5, 8,  6,  5,  6,  6,  6,  5,  8,  5,  6,  6,  5,  8,  6]

plt.scatter(sizes, times)
plt.show()