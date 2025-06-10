from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull


# Load image
image = Image.open("img/logo4.png").convert("L")
image = image.resize((256, 256))
array = np.array(image)

# Extract dark pixels
# Adjust the threshold for better contrast (darker details)
threshold = 200  # was 128
mask = array < threshold

# Get coordinates of dark pixels
y_coords, x_coords = np.where(mask)

# Normalize and center
height, width = array.shape
x = x_coords / width - 0.5
y = 0.5 - y_coords / height

# Optional: downsample for speed
x = x[::8]
y = y[::8]
points = np.array([(x_i, y_i) for x_i, y_i in zip(x,y)])
hull = ConvexHull(points)
loop_points = points[hull.vertices]
loop_points = np.append(loop_points, [loop_points[0]], axis=0)

x = [x_i for x_i, _ in loop_points]
y = [y_i for _, y_i in loop_points]

print(f"Number of points: {len(x)}")




np.savetxt("converted_arrays.csv", np.column_stack((x, y)), delimiter=",", header="x,y", comments='')

# Plot
plt.figure(figsize=(6, 6))
plt.plot(x, y, color="black")
plt.axis("equal")
plt.axis("off")
plt.tight_layout()
plt.show()
