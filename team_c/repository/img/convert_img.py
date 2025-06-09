from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

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
x = x[::1]
y = y[::1]
print(f"Number of points: {len(x)}")

# save to file "converted_arrays.csv"
# give title "x,y"

np.savetxt("converted_arrays.csv", np.column_stack((x, y)), delimiter=",", header="x,y", comments='')

# # Plot
# plt.figure(figsize=(6, 6))
# plt.scatter(x, y, s=0.2, color="black")
# plt.axis("equal")
# plt.axis("off")
# plt.tight_layout()
# plt.show()
