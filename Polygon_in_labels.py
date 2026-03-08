#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch-Konvertierung von GeoJSON-Labels zu .txt (YOLO-Format) für alle Rasterbilder
Created on Fri Mar  6 14:40:36 2026
@author: leonhofmann
"""

import json
import rasterio
from pathlib import Path

# Ordner
image_dirs = [
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/images/train",
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/images/val"
]

label_dirs = [
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/labels/train",
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/labels/val"
]

def convert_geojson_to_yolo(raster_path, geojson_path, output_label_path):
    # Raster öffnen
    with rasterio.open(raster_path) as src:
        transform = src.transform
        width = src.width
        height = src.height

    # GeoJSON laden
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
                col, row = ~transform * (x, y)
                xn = col / width
                yn = row / height
                line += f" {xn} {yn}"
            lines.append(line)

    output_label_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_label_path, "w") as f:
        f.write("\n".join(lines))

    print("YOLO label erstellt:", output_label_path)

# Durch alle Bilder iterieren
for img_dir, lbl_dir in zip(image_dirs, label_dirs):
    img_dir_path = Path(img_dir)
    lbl_dir_path = Path(lbl_dir)

    for raster_file in img_dir_path.glob("*.tif"):
        geojson_file = lbl_dir_path / (raster_file.stem + ".geojson")
        output_label_file = lbl_dir_path / (raster_file.stem + ".txt")

        if geojson_file.exists():
            convert_geojson_to_yolo(raster_file, geojson_file, output_label_file)
        else:
            print(f"Keine passende GeoJSON gefunden für {raster_file.name}")