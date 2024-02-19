import numpy as np
import matplotlib.animation
import matplotlib.pyplot as plt


def update_plot(i):
    x,y = random_points(i**2)
    plt.cla()
    plt.scatter(x,y)


fig1, ax1 = plt.subplots()


def random_points(number_of_points = 1000):
    rng = np.random.default_rng()
    points_x = rng.random(number_of_points)
    points_y = rng.random(number_of_points)
    return points_x, points_y

ani = matplotlib.animation.FuncAnimation(fig1, update_plot, interval=50)

print("asdasd")
plt.show()

print("ASDASD")



