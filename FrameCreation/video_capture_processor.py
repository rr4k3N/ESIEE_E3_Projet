import cv2
import time
import os
from .frame_selector import FrameSelector

class VideoCaptureProcessor:
    def __init__(self, gst_pipeline, frames_folder, selected_folder, frame_rate=30, selection_interval=1, n_best=2):
        self.gst_pipeline = gst_pipeline
        self.frames_folder = frames_folder
        self.selected_folder = selected_folder
        self.frame_rate = frame_rate
        self.selection_interval = selection_interval
        self.n_best = n_best
        self.frame_selector = FrameSelector(frames_folder, selected_folder, selection_interval, n_best)
        self.cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            raise RuntimeError("Erreur : impossible d'ouvrir la caméra.")

    def save_frame(self, frame, frame_id):
        filename = f"frame_{frame_id:06d}.jpg"
        filepath = os.path.join(self.frames_folder, filename)
        cv2.imwrite(filepath, frame)

    def process(self, duration_sec=10):
        if not os.path.exists(self.frames_folder):
            os.makedirs(self.frames_folder)
        if not os.path.exists(self.selected_folder):
            os.makedirs(self.selected_folder)

        start_time = time.time()
        frame_id = 0
        last_selection_time = start_time

        print("Capture démarrée...")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Erreur lecture frame.")
                break

            self.save_frame(frame, frame_id)
            frame_id += 1

            now = time.time()
            elapsed = now - last_selection_time
            if elapsed >= self.selection_interval:
                print(f"--- Sélection des meilleures frames après {elapsed:.2f} secondes ---")
                self.frame_selector.select_best_frames()
                last_selection_time = now

            if now - start_time > duration_sec:
                # Sélection finale sur les frames restantes
                print("--- Sélection finale avant arrêt ---")
                self.frame_selector.select_best_frames()
                break

        self.cap.release()
        print("Capture terminée.")
