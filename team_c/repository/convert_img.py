from PIL import Image
import numpy as np
# import cairosvg
import io
import os
import csv

def load_image_as_array(path):
    if path.endswith(".svg"):
        pass
        # png_data = cairosvg.svg2png(url=path)
        # image = Image.open(io.BytesIO(png_data)).convert("L")
    elif path.endswith(".png"):
        image = Image.open(path).convert("L")
    else:
        raise ValueError("Plik musi miec rozszerzeznie .png lub .svg")

    image = image.resize((256,256))
    data = np.array(image)
    return data

def extract_normalize_data(image_array, treshold=128):
    mask = image_array < treshold
    y_coords, x_coords = np.where(mask)

    height, width = image_array.shape
    x_norm = x_coords / width
    y_norm = y_coords / height
    return x_norm, y_norm

def save_xy_to_csv(x, y, filename):
    if len(x)!=len(y):
        raise ValueError("Co ty mi dajesz inne dlugosci")
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["x","y"])
        for xi, yi in zip(x,y):
            writer.writerow([xi,yi])


path = "img/logo.png"
img_array = load_image_as_array(path)
x, y = extract_normalize_data(img_array)
print("y", y)
print("x", x)
save_xy_to_csv(x,y,"converted_arrays.csv")


