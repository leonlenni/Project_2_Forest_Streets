#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test-Skript: Raster + YOLO Labels Overlay mit Debug
@author: leonhofmann
"""

import json
import rasterio
import numpy as np
import cv2
import os

# ----------------- Pfade -----------------
raster_path = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/test_raster_for_training.tif"
geojson_path = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/test_poly_for_training.geojson"
output_label = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/image1.txt"
output_overlay = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/overlay_debug.png"

# ----------------- Klassen & Farben -----------------
class_names = {0: "road", 1: "hiking"}
class_colors = {0: (0, 0, 255), 1: (0, 255, 0)}  # BGR

# ----------------- Schritt 1: TXT aus GeoJSON -----------------
with rasterio.open(raster_path) as src:
    transform = src.transform
    width = src.width
    height = src.height

with open(geojson_path) as f:
    data = json.load(f)

lines = []

for feature in data["features"]:
    class_id = feature["properties"]["RoadTyp"]
    multipolygon = feature["geometry"]["coordinates"]
    for polygon in multipolygon:
        ring = polygon[0]
        line = str(class_id)
        for x, y in ring:
            col, row = ~transform * (x, y)  # Geo -> Pixel
            xn = col / width
            yn = row / height
            line += f" {xn} {yn}"
        lines.append(line)

with open(output_label, "w") as f:
    f.write("\n".join(lines))

print("YOLO label file erstellt:", output_label)

# ----------------- Schritt 2: Raster -> PNG -----------------
with rasterio.open(raster_path) as src:
    if src.count >= 3:
        img = np.dstack([src.read(1), src.read(2), src.read(3)])
    else:
        img = src.read(1)
        img = np.stack([img]*3, axis=-1)
    # 8-bit Normalisierung
    if img.dtype != np.uint8:
        img_min = img.min()
        img_max = img.max()
        img = ((img - img_min)/(img_max - img_min)*255).astype(np.uint8)

cv2.imwrite(output_overlay, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
print("PNG Raster gespeichert (als Overlay-Basis):", output_overlay)

# ----------------- Schritt 3: Overlay der Polygone -----------------
# Neues Overlay Bild
overlay_img = img.copy()

with open(output_label, "r") as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split()
    if len(parts) < 3:
        continue
    class_id = int(parts[0])
    coords = parts[1:]
    points = []
    for i in range(0, len(coords), 2):
        xn = float(coords[i])
        yn = float(coords[i+1])
        x = int(xn * width)
        y = int(yn * height)
        points.append([x, y])
    points = np.array(points, np.int32)

    # Debug: Pixelpunkte
    print(f"Class {class_id} points:", points)

    # Polygon zeichnen
    color = class_colors.get(class_id, (255, 255, 0))
    cv2.polylines(overlay_img, [points], isClosed=True, color=color, thickness=2)

    # Füllen mit Alpha
    temp = overlay_img.copy()
    cv2.fillPoly(temp, [points], color=color)
    alpha = 0.3
    overlay_img = cv2.addWeighted(temp, alpha, overlay_img, 1-alpha, 0)

    # Klassennamen
    name = class_names.get(class_id, str(class_id))
    cv2.putText(overlay_img, name, (points[0][0], points[0][1]-5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)

# Speichern & Anzeigen
cv2.imwrite(output_overlay, overlay_img)
print("Overlay Bild gespeichert:", output_overlay)
cv2.imshow("Overlay Debug", overlay_img)
cv2.waitKey(0)
cv2.destroyAllWindows()