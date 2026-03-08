from ultralytics import YOLO
import numpy as np
import cv2

# trainiertes Modell laden
model = YOLO('/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/runs/test_train12/weights/best.pt')

# Bild laden
img_path = '/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/temp_testing_raster_pgs/image_4324.png'
img = cv2.imread(img_path)

# Vorhersage auf Bild
results = model.predict(
    source=img_path,
    project='/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/test',  # expliziter Ordner
    save=True,
    show=True
)

# Masken auf Bild zeichnen
for result in results:
    if result.masks is not None:
        for polygon in result.masks.xy:
            pts = np.array(polygon, np.int32)
            cv2.polylines(img, [pts], isClosed=True, color=(255, 0, 0), thickness=2)
            overlay = img.copy()
            cv2.fillPoly(overlay, [pts], color=(0, 255, 0))
            alpha = 0.3
            img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    else:
        print("Keine Masken vorhergesagt für dieses Bild.")

# Optional: das Ergebnis speichern
cv2.imwrite('/Users/leonhofmann/Desktop/MMES/Protject 2/Yolo11/test/predict_overlay.png', img)