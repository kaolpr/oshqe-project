from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

import numpy as np
from scipy.spatial import Delaunay
from collections import defaultdict
import math


def create_concave_hull(points, alpha):
    """
    Computes the concave hull (alpha-shape) of a set of 2D points.

    Args:
        points (np.ndarray): A NumPy array of shape (n, 2) representing the points.
        alpha (float): The alpha value controlling the "tightness" of the hull.
                       A smaller alpha creates a tighter, more detailed hull.
                       A larger alpha results in a hull closer to the convex hull.

    Returns:
        list: A list of (x, y) tuples representing the ordered points of the concave hull.
              Returns an empty list if a hull cannot be formed.
    """
    if len(points) < 4:
        # A hull requires at least 3 points, but 4 are needed for Delaunay
        # to work robustly in all cases.
        return [tuple(p) for p in points]

    # 1. Create a Delaunay triangulation of the points
    try:
        tri = Delaunay(points)
    except Exception as e:
        print(f"Delaunay triangulation failed: {e}")
        return []

    # 2. Filter triangles based on the circumradius and edge lengths
    # An alternative and simpler approach is to filter edges directly by length.

    # Create a set of all edges from the triangulation
    edges = set()
    # A dictionary to look up opposite vertices for edge-triangle mapping
    edge_to_triangle = defaultdict(list)

    for i, simplex in enumerate(tri.simplices):
        for j in range(3):
            p1_idx, p2_idx = simplex[j], simplex[(j + 1) % 3]
            # Sort to ensure edge is unique regardless of direction
            edge = tuple(sorted((p1_idx, p2_idx)))
            edges.add(edge)
            edge_to_triangle[edge].append(i)

    # 3. Filter edges based on length (controlled by alpha)
    # Here, alpha is used as a length threshold.
    # A good starting point for alpha can be the average or median edge length.
    boundary_edges = []
    for edge in edges:
        p1_idx, p2_idx = edge
        p1 = points[p1_idx]
        p2 = points[p2_idx]

        length = math.sqrt(np.sum((p1 - p2)**2))

        # The alpha condition
        if length < alpha:
            # An edge is part of the boundary if it's part of only one triangle
            # or if its length meets the alpha criteria (for internal edges).
            # For simplicity in this concave hull, we check if it is a boundary edge
            # of the Delaunay triangulation OR if it is short enough.
            # A true alpha shape also checks circumradius, but length is a good proxy.
            if len(edge_to_triangle[edge]) == 1:
                boundary_edges.append(edge)

    if not boundary_edges:
        print("Warning: No boundary edges found for the given alpha. Try a larger value.")
        return []

    # 4. Stitch the boundary edges together into a single ordered path
    # Create an adjacency list for the boundary points
    adj_list = defaultdict(list)
    for p1_idx, p2_idx in boundary_edges:
        adj_list[p1_idx].append(p2_idx)
        adj_list[p2_idx].append(p1_idx)

    # Perform a walk along the boundary
    start_node = boundary_edges[0][0]
    current_node = start_node
    prev_node = -1  # A value that cannot be a point index
    path = []

    for _ in range(len(boundary_edges)):
        path.append(current_node)

        neighbors = adj_list[current_node]

        # Find the next node that is not the one we just came from
        next_node = -1
        if len(neighbors) == 1:  # End of a segment
            if neighbors[0] != prev_node:
                next_node = neighbors[0]
        else:  # Most common case
            for neighbor in neighbors:
                if neighbor != prev_node:
                    next_node = neighbor
                    break

        if next_node == -1 or next_node == start_node:  # Path is closed or stuck
            break

        prev_node = current_node
        current_node = next_node

    # Convert path of indices back to coordinates
    hull_points = [tuple(points[i]) for i in path]
    return hull_points


# Load image
image_top = Image.open("img/logo4_top.png").convert("L")
image_top = image_top.resize((256, 256))

image_bottom = Image.open("img/logo4_bottom.png").convert("L")
image_bottom = image_bottom.resize((256, 256))
array_top = np.array(image_top)
array_bottom = np.array(image_bottom)

# Extract dark pixels
# Adjust the threshold for better contrast (darker details)
threshold = 200  # was 128
mask_top = array_top < threshold
mask_bottom = array_bottom < threshold

# Get coordinates of dark pixels
y_coords_top, x_coords_top = np.where(mask_top)
y_coords_bottom, x_coords_bottom = np.where(mask_bottom)

# Normalize and center
height, width = array_top.shape
x_top = x_coords_top / width - 0.5
y_top = 0.5 - y_coords_top / height

height, width = array_bottom.shape
x_bottom = x_coords_bottom / width - 0.5
y_bottom = 0.5 - y_coords_bottom / height

# Optional: downsample for speed
x_top = x_top[::1]
y_top = y_top[::1]

x_bottom = x_bottom[::1]
y_bottom = y_bottom[::1]
# Combine top and bottom points
plt.scatter(x_top, y_top, color="blue", s=1, label="Top")

points_top = np.array([(x_i, y_i) for x_i, y_i in zip(x_top, y_top)])
hull_top = create_concave_hull(points_top, alpha=2.5)
loop_points_top = hull_top
loop_points_top = np.append(loop_points_top, [loop_points_top[0]], axis=0)
plt.scatter(loop_points_top[:, 0], loop_points_top[:,
            1], color="red", s=1, label="Top Hull")

points_bottom = np.array([(x_i, y_i) for x_i, y_i in zip(x_bottom, y_bottom)])
hull_bottom = ConvexHull(points_bottom)
loop_points_bottom = points_bottom[hull_bottom.vertices]
loop_points_bottom = np.append(
    loop_points_bottom, [loop_points_bottom[0]], axis=0)

x_top = [x_i for x_i, _ in loop_points_top]
y_top = [y_i for _, y_i in loop_points_top]

x_bottom = [x_i for x_i, _ in loop_points_bottom]
y_bottom = [y_i for _, y_i in loop_points_bottom]

# Combine top and bottom points
x_top.extend(x_bottom)
y_top.extend(y_bottom)


print(f"Number of points: {len(x_top)}")


np.savetxt("converted_arrays.csv", np.column_stack(
    (x_top, y_top)), delimiter=",", header="x,y", comments='')

# Plot
plt.figure(figsize=(6, 6))
plt.plot(x_top, y_top, color="black")
plt.axis("equal")
plt.axis("off")
plt.tight_layout()
plt.show()
