import cv2
import numpy as np
import os
import shutil
from datetime import datetime

class FrameSelector:
    def __init__(self, source_folder, selected_folder, interval_sec=1):
        self.source_folder = source_folder
        self.selected_folder = selected_folder
        self.interval_sec = interval_sec
        if not os.path.exists(selected_folder):
            os.makedirs(selected_folder)

    def score_frame(self, img):
        """Calcule un score basé sur netteté et luminosité uniforme"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Netteté (variance du Laplacien)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Luminosité moyenne et écart type (plus petit = plus uniforme)
        mean_lum = np.mean(gray)
        std_lum = np.std(gray)

        # Score global : privilégier netteté élevée, luminosité moyenne autour de 127, faible stddev
        score = laplacian_var - abs(mean_lum - 127) - std_lum * 2
        return score

    def is_overexposed(self, frame, white_threshold=240, white_ratio_threshold=0.05):
   	 """
   	 Détecte si une frame est surexposée en analysant le ratio de pixels très clairs."""
   	 gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
   	 white_pixels = cv2.countNonZero(cv2.inRange(gray, white_threshold, 255))
   	 total_pixels = gray.size
   	 white_ratio = white_pixels / total_pixels
	 return white_ratio > white_ratio_threshold
    
    def select_best_frame(self):
	    files = [f for f in os.listdir(self.source_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
	    if not files:
	        print("Aucune frame à traiter.")
	        return None

	    best_score = -float('inf')
	    best_file = None

	    for f in files:
	        path = os.path.join(self.source_folder, f)
	        img = cv2.imread(path)
	        if img is None:
	            continue

	        if self.is_overexposed(img):
	            continue

	        score = self.score_frame(img)
	        if score > best_score:
	            best_score = score
	            best_file = f

	    if best_file:
	        # Déplacer la meilleure frame
	        src = os.path.join(self.source_folder, best_file)
	        dst = os.path.join(self.selected_folder, best_file)
	        shutil.move(src, dst)

	        # Supprimer les autres frames
	        for f in files:
	            if f != best_file:
	                try:
	                    os.remove(os.path.join(self.source_folder, f))
	                except Exception as e:
	                    print(f"Erreur suppression {f}: {e}")

