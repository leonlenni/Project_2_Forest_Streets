#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch conversion of GeoJSON labels to YOLO format for all raster images.
Corrected version that handles empty labels, Polygon/MultiPolygon geometries, and proper YOLO formatting.

CHECK SAME CRS BETWEEN RASTER AND 
"""

import json
import rasterio
from pathlib import Path

# Directetoy of geotifs and geojsons created with QGIS (already seperated in training and validation)
image_dirs = [
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/images/train",
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/images/val"
]

label_dirs = [
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/labels/train",
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/labels/val"
]


# Optional: map RoadTyp (Yolo needs to  be int and start with 0, edit this if QGIS categories dont start with 0)
roadtyp_to_class = {
    0: 0,  
    1: 1,
    2: 2
}

def convert_geojson_to_yolo(raster_path, geojson_path, output_label_path):
    """
    This function converts one image + one GeoJSON into a YOLO .txt.
    """
    # Raster öffnen
    #This is needed because GeoJSON uses map coordinates but YOLO needs pixel coordinates.
    with rasterio.open(raster_path) as src:
        transform = src.transform
        width = src.width
        height = src.height

    # load GeoJSON (label polygon)
    with open(geojson_path) as f:
        data = json.load(f)
        
    #create empty list to initate yolo compatible .txt
    lines = []

    # Convert each geoJSON polygon to normalized YOLO segmentation coordinates
    for feature in data["features"]:
        # Map RoadTyp to 0-based class (only matters if defined differently)
        road_typ = feature["properties"].get("RoadTyp", 0)
        class_id = roadtyp_to_class.get(road_typ, 0)
        #Handle potential multipolygon: This standardizes them into a list of polygons.
        geom_type = feature["geometry"]["type"]
        if geom_type == "Polygon":
            polygons = [feature["geometry"]["coordinates"]]
        elif geom_type == "MultiPolygon":
            polygons = feature["geometry"]["coordinates"]
        else:
            continue  # skip non-polygon geometries
        #CORE funtionality: GeoJson map coordinates transformed into for Yolo needed normalized pixel coordinates
        for polygon in polygons:
            ring = polygon[0]  # outer ring (Yolo supports no polygons with holes)
            # initiate yolo .txt file/format
            line = str(class_id)
            for x, y in ring:
                # invert transform to account for different direction (QGIS (world coordinates) starts coordinates differently then the yolo algorithm (pixel))
                col, row = ~transform * (x, y)  # map world coordinates to pixel
                # normalization of x coordinated for yolo (coordinates between 0 and 1)
                xn = col / width
                # normalization y coordinates for yolo (coordinates between 0 and 1)
                yn = row / height
                # setup coordinate for .txt -> format x1 y1 x2 y2... (pixel coordinates)
                line += f" {xn} {yn}"
            #add to file
            lines.append(line)


    # create output folder 
    output_label_path.parent.mkdir(parents=True, exist_ok=True)
    # write .txt with YOLO labels
    with open(output_label_path, "w") as f:
        f.write("\n".join(lines))

    print("YOLO label created:", output_label_path)

# iterate through all rasters and and apply the function previously defined
    #pairs raster and Geojsonfolder 
for img_dir, lbl_dir in zip(image_dirs, label_dirs):
    #raster path refrence
    img_dir_path = Path(img_dir)
    #raster path refrence

    lbl_dir_path = Path(lbl_dir)

    #looping through all rasters in directory
    for raster_file in img_dir_path.glob("*.tif"):
        #set up label name for file (name without old extensiosn)
        geojson_file = lbl_dir_path / (raster_file.stem + ".geojson")
        # create final file name 
        output_label_file = lbl_dir_path / (raster_file.stem + ".txt")
        
        #check if geojson exist otherwise create an empty file for true negatives
        if geojson_file.exists():
            #apply function
            convert_geojson_to_yolo(raster_file, geojson_file, output_label_file)
        else:
            # Create empty YOLO label for images with no roads
            output_label_file.parent.mkdir(parents=True, exist_ok=True)
            output_label_file.touch()
            print(f"Keine GeoJSON gefunden, leere YOLO Datei erstellt für {raster_file.name}")
            
            
            
# AFTER all conversion loops are done delete the old files
for lbl_dir in label_dirs:
    lbl_dir_path = Path(lbl_dir)
    for geojson_file in lbl_dir_path.glob("*.geojson"):
        geojson_file.unlink()  # delete the file
        print(f"Deleted GeoJSON: {geojson_file}")