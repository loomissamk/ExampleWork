import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the equations of the planes
def plane1(x, y):
    return 3 * x + y

def plane2(x, z):
    return x + 3 * z

# Create a grid of x, y, and z values
x = np.linspace(-10, 10, 100)
y = np.linspace(-10, 10, 100)
z = np.linspace(-10, 10, 100)
X, Y = np.meshgrid(x, y)

# Calculate the corresponding z values for each plane
Z1 = plane1(X, Y)
Z2 = plane2(X, Z1)

# Plot the planes
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z1, alpha=0.5, cmap='viridis', edgecolor='k')
ax.plot_surface(X, Y, Z2, alpha=0.5, cmap='plasma', edgecolor='k')

# Calculate the line of intersection
A = np.array([[3, 1], [1, 3]])
b = np.array([0, 0])
intersection = np.linalg.solve(A, b)

# Plot the line of intersection
t = np.linspace(-10, 10, 100)
x_line = intersection[0] * t
y_line = intersection[1] * t
z_line = plane1(x_line, y_line)
ax.plot(x_line, y_line, z_line, color='red', label='Intersection')

# Set axis labels and legend
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()

# Show the plot
plt.show()

