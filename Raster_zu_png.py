#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch-Konvertierung von Rasterbildern (TIFF) zu PNG
Die PNGs werden im gleichen Ordner wie die TIFFs gespeichert.
"""

import rasterio
import numpy as np
import cv2
from pathlib import Path

# Directory with QGIS Tifs
image_dirs = [
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/images/train",
    "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten/images/val"
]

#list of converted tifs to delete them afterwards
converted_tiffs = []

# looop through all tiffs
for img_dir in image_dirs:
    img_dir_path = Path(img_dir)

    for raster_file in img_dir_path.glob("*.tif"):
        # open single raster (DSM is greyscaled but increased functionality)
        with rasterio.open(raster_file) as src:
            # check RGB or Single-Band
            if src.count >= 3:
                img = np.dstack([src.read(1), src.read(2), src.read(3)])
            else:
                img = src.read(1)
                # copying the channels bc model expects 3 channels (faking RGB)
                img = np.stack([img]*3, axis=-1)

            # YOLO needs pictures in special format uint8 (values between 0-256 check if its the case)
            # if not normalize the range of the picture to 0-1 then mutiply by 256 -> uint8
            if img.dtype != np.uint8:
                img_min = img.min()
                img_max = img.max()
                if img_max > img_min:
                    # transform to uint8
                    img = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
                else:
                    # if emoty picture create black .png (cant divide by 0 (previous equation))
                    img = np.zeros_like(img, dtype=np.uint8)

        # Saven PNG in TiFF Directory (DELETE TIFF AFTER WORKFLOW IS SET UP)
        output_path = raster_file.with_suffix(".png")
        cv2.imwrite(str(output_path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        print("Saved image:", output_path)
        # Only track the TIFF we converted
        converted_tiffs.append(raster_file)

# DELETE only TIFFs converted not working
#for tif_file in converted_tiffs:
#    if tif_file.exists():
#        tif_file.unlink()
#        print(f"Deleted original TIFF: {tif_file}")