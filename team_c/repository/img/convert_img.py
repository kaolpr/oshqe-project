import csv
from svgpathtools import svg2paths2
import matplotlib.pyplot as plt

paths, attrs, svg_attr = svg2paths2("WF_logo.svg")


fig, ax = plt.subplots(1, 3, figsize=(9, 3))

# Ignore filled shapes (if needed)
centerline_paths = []
for path, attr in zip(paths, attrs):
    if attr.get('fill') in (None, 'none') and attr.get('stroke') not in (None, 'none'):
        centerline_paths.append(path)

print(f"Found {len(paths)} centerline paths.")

# for path in paths:


for seg in paths[0][:22]:
    pts = [seg.point(t/100) for t in range(101)]
    xs = [pt.real for pt in pts]
    ys = [pt.imag for pt in pts]
    ax[0].plot(xs, ys)

for seg in paths[1][:30]:
    pts = [seg.point(t/100) for t in range(101)]
    xs = [pt.real for pt in pts]
    ys = [pt.imag for pt in pts]
    ax[0].plot(xs, ys)

ax[0].set_aspect('equal')
# plt.show()

paths_1_outer = paths[0][:22]
paths_2_outer = paths[1][:30]


def start_from_segment(path, segment_index):
    """Start from a specific segment in a path."""
    return path[segment_index:] + path[:segment_index]


paths_1_outer = start_from_segment(paths_1_outer, 15)
paths_2_outer = start_from_segment(paths_2_outer, 8)

# convert other paths to points


def convert_path_to_points(path, num_points=100):
    points = []
    for seg in path:
        pts = [seg.point(t / num_points) for t in range(num_points + 1)]
        points.extend(pts)
    return points


points_1_outer = convert_path_to_points(paths_1_outer)
points_2_outer = convert_path_to_points(paths_2_outer)

ax[1].plot([pt.real for pt in points_1_outer], [
    pt.imag for pt in points_1_outer], label='Outer Path 1')
ax[1].plot([pt.real for pt in points_2_outer], [
    pt.imag for pt in points_2_outer], label='Outer Path 2')

# plot the fisrt point of each path in red
ax[1].plot(points_1_outer[0].real, points_1_outer[0].imag,
           'ro', label='Start Point 1')
ax[1].plot(points_2_outer[0].real, points_2_outer[0].imag,
           'ro', label='Start Point 2')

ax[1].set_aspect('equal')
ax[1].set_title('Outer Paths')
ax[1].legend()

# combine the two outer paths
combined_outer_points = points_1_outer + points_2_outer
# normalize the points to a 0,1 range
min_x = min(pt.real for pt in combined_outer_points)
max_x = max(pt.real for pt in combined_outer_points)
min_y = min(pt.imag for pt in combined_outer_points)
max_y = max(pt.imag for pt in combined_outer_points)

combined_outer_points = [complex((pt.real - min_x) / (max_x - min_x) if max_x > min_x else 0,
                                 (pt.imag - min_y) / (max_y - min_y) if max_y > min_y else 0)
                         for pt in combined_outer_points]

ax[2].plot([pt.real for pt in combined_outer_points], [
    pt.imag for pt in combined_outer_points], label='Combined Outer Path')
ax[2].plot(combined_outer_points[0].real, combined_outer_points[0].imag,
           'ro', label='Start Point Combined')
ax[2].set_aspect('equal')
ax[2].set_title('Combined Outer Path')
ax[2].legend()
plt.tight_layout()
plt.savefig('combined_outer_path.png', dpi=300)
plt.show()


# Save the combined outer path to a csv file
with open('combined_outer_path.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['x', 'y'])
    for pt in combined_outer_points:
        writer.writerow([pt.real, pt.imag])
