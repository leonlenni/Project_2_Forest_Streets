#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create the yaml file for yolo, its needed to tell the mpdel where your dataset (training
 and validation is stored, how it structured as well as the number and names of the classes
 it allocated the label directory by it self (need to follow the same structure as the pngs)
"""

import yaml


output_path = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/Modelparams/dataset.yaml"

# Content of yaml file as python-dict
data = {
    # basis directory
    "path": "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/BeispielDaten",    
    # training pngs    
    "train": "images/train",  
    # validation pngs
    "val": "images/val",     
    # class mapping
    "names": {
        0: "road",
        1: "hiking",
        2: "skitroad"
    }     
}

# write file 
with open(output_path, "w") as f:
    yaml.dump(data, f, default_flow_style=False)

print("dataset.yaml created successfullly")


