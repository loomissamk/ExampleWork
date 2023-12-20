import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the equations
def f1(x, y, z):
    return 3*x + y + z

def f2(x, y, z):
    return x + y + 3*z

# Create a meshgrid of points
x = np.linspace(-10, 10, 100)
y = np.linspace(-10, 10, 100)
X, Y = np.meshgrid(x, y)

# Evaluate the functions for the given meshgrid
Z1 = f1(X, Y, 0)
Z2 = f2(X, Y, 0)

# Create the first figure
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the first plane
ax.plot_surface(X, Y, Z1, alpha=0.5)

# Plot the second plane
ax.plot_surface(X, Y, Z2, alpha=0.5)

# Set labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Planes')

# Show the first figure
plt.show()

# Create the second figure
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Evaluate the functions for the shifted meshgrid
Z1_shifted = f1(X + 9, Y + 2, 2)
Z2_shifted = f2(X + 9, Y + 2, 2)

# Plot the first shifted plane
ax.plot_surface(X, Y, Z1_shifted, alpha=0.5)

# Plot the second shifted plane
ax.plot_surface(X, Y, Z2_shifted, alpha=0.5)

# Set labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Shifted Planes')

# Show the second figure
plt.show()