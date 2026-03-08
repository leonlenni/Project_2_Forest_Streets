#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 16:00:00 2026

@author: leonhofmann
"""

import cv2
import numpy as np
import os

# --------- Pfade anpassen ----------
image_path = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/images/train/image1.png"
label_path = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/labels/train/image1.txt"
output_path = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/visual_label_overlay.png"

# Optional: Farben für jede Klasse
class_colors = {
    0: (0, 0, 255),    # Rot für Klasse 0
    1: (0, 255, 0),    # Grün für Klasse 1
}

# Bild einlesen
img = cv2.imread(image_path)
h, w = img.shape[:2]

# Labels einlesen
with open(label_path, "r") as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split()
    if len(parts) < 3:
        continue

    class_id = int(parts[0])
    coords = parts[1:]

    # Polygonpunkte konvertieren: normiert 0-1 → Pixelkoordinaten
    points = []
    for i in range(0, len(coords), 2):
        xn = float(coords[i])
        yn = float(coords[i+1])
        x = int(xn * w)
        y = int(yn * h)
        points.append([x, y])

    points = np.array(points, dtype=np.int32)

    # Polygon auf Bild zeichnen
    color = class_colors.get(class_id, (255, 255, 0))
    cv2.polylines(img, [points], isClosed=True, color=color, thickness=2)
    # optional: Füllen
    overlay = img.copy()
    cv2.fillPoly(overlay, [points], color=color)
    alpha = 0.3
    img = cv2.addWeighted(overlay, alpha, img, 1-alpha, 0)

# Bild speichern
cv2.imwrite(output_path, img)
print("Overlay-Bild mit Labels gespeichert:", output_path)

# optional: Bild direkt anzeigen
cv2.imshow("YOLO Labels Overlay", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

