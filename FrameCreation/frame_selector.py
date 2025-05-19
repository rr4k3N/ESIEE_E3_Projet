import cv2
import numpy as np
import os
import shutil

class FrameSelector:
    def __init__(self, source_folder, selected_folder, interval_sec=1, n_best=2):
        self.source_folder = source_folder
        self.selected_folder = selected_folder
        self.interval_sec = interval_sec
        self.n_best = n_best
        if not os.path.exists(selected_folder):
            os.makedirs(selected_folder)

    def score_frame(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        mean_lum = np.mean(gray)
        std_lum = np.std(gray)
        score = laplacian_var - abs(mean_lum - 127) - std_lum * 2
        return score

    def is_overexposed(self, frame, white_threshold=240, white_ratio_threshold=0.05):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        white_pixels = cv2.countNonZero(cv2.inRange(gray, white_threshold, 255))
        total_pixels = gray.size
        white_ratio = white_pixels / total_pixels
        return white_ratio > white_ratio_threshold

    def select_best_frames(self, num_to_select=2):
            files = [f for f in os.listdir(self.source_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            print(f"Fichiers trouvés dans {self.source_folder} : {files}")
            if not files:
                print("Aucune frame à traiter.")
                return []
        
            scored_frames = []
        
            for f in files:
                path = os.path.join(self.source_folder, f)
                img = cv2.imread(path)
                if img is None:
                    print(f"Impossible de lire {f}, ignoré.")
                    continue
        
                score = self.score_frame(img)
                overexposed = self.is_overexposed(img)
                print(f"Score {score:.2f} pour {f} (surexposé: {overexposed})")
        
                scored_frames.append({
                    "filename": f,
                    "score": score,
                    "overexposed": overexposed
                })
        
            # Trier par score décroissant
            scored_frames.sort(key=lambda x: x["score"], reverse=True)
        
            # Séparer frames valides / invalides
            valid_frames = [f for f in scored_frames if not f["overexposed"]]
            selected = []
        
            if len(valid_frames) >= num_to_select:
                selected = valid_frames[:num_to_select]
            else:
                print(f"Pas assez de frames valides, sélection des {num_to_select} meilleures globalement.")
                selected = scored_frames[:num_to_select]
        
            selected_filenames = [f["filename"] for f in selected]
            print(f"Frames sélectionnées : {selected_filenames}")
        
            # Déplacement des frames sélectionnées, suppression du reste
            for f in scored_frames:
                src = os.path.join(self.source_folder, f["filename"])
                if f["filename"] in selected_filenames:
                    dst = os.path.join(self.selected_folder, f["filename"])
                    print(f"Déplacement {f['filename']} vers {self.selected_folder}")
                    shutil.move(src, dst)
                else:
                    try:
                        print(f"Suppression {f['filename']}")
                        os.remove(src)
                    except Exception as e:
                        print(f"Erreur suppression {f['filename']}: {e}")
        
            return selected_filenames
