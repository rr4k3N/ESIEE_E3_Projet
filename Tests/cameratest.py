import cv2

# Test plusieurs index possibles (0, 1, 2)
for i in range(3):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Caméra détectée à l'index {i}")
        cap.release()
    else:
        print(f"❌ Aucune caméra à l'index {i}")
