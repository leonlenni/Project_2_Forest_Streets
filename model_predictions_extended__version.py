import cv2
import numpy as np
from ultralytics import YOLO

# ----------------- Pfade -----------------
model_path = '/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/test_predictions/yolo11n-seg.pt'
test_image = '/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/test_predictions/test_image1.png'
output_overlay = "/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/test/test_overlay.png"

# ----------------- Klassen & Farben -----------------
class_colors = {0: (0, 0, 255), 1: (0, 255, 0)}  # BGR

# ----------------- Bild laden -----------------
img = cv2.imread(test_image)

# ----------------- Modell laden -----------------
model = YOLO(model_path)

# ----------------- Prediction -----------------
results = model.predict(
    test_image,
    project='/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/test',  
    save=True,   # speichert automatisch das PNG in 'project' Ordner
    show=True,
    conf=0.05    # niedrig für Debug
)

# ----------------- Masken-Overlay -----------------
for result in results:
    if result.masks is not None:
        for polygon in result.masks.xy:
            pts = np.array(polygon, np.int32)
            cv2.polylines(img, [pts], isClosed=True, color=(255,0,0), thickness=2)
            overlay = img.copy()
            cv2.fillPoly(overlay, [pts], color=(0,255,0))
            alpha = 0.3
            img = cv2.addWeighted(overlay, alpha, img, 1-alpha, 0)
    else:
        print("Keine Masken vorhergesagt für dieses Bild.")

# ----------------- Overlay speichern -----------------
cv2.imwrite(output_overlay, img)
print("Overlay gespeichert:", output_overlay)

cv2.imshow("YOLO Segmentation Overlay", img)
cv2.waitKey(0)
cv2.destroyAllWindows()