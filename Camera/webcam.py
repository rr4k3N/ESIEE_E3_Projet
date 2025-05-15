import cv2
import time
import os

class Webcam:
    def __init__(self, device="/dev/video0", width=640, height=480, fps=30, output_dir="../FrameCreation/Frames"):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        self.output_dir = output_dir
        self.cap = None
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _build_gst_pipeline(self):
        return (
            f"v4l2src device={self.device} ! "
            f"video/x-raw, width={self.width}, height={self.height}, framerate={self.fps}/1 ! "
            "nvvidconv ! video/x-raw(memory:NVMM), format=I420 ! "
            "nvvidconv ! video/x-raw, format=BGRx ! "
            "videoconvert ! video/x-raw, format=BGR ! appsink"
        )
    
    def open(self):
        gst_str = self._build_gst_pipeline()
        self.cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            raise RuntimeError("Erreur : impossible d'ouvrir la caméra avec le pipeline GStreamer.")
    
    def capture_frames(self, duration_sec=10):
        if self.cap is None:
            self.open()
        
        start_time = time.time()
        frame_idx = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Fin du flux ou erreur de capture.")
                break
            
            frame_idx += 1
            filename = os.path.join(self.output_dir, f"frame_{frame_idx:04d}.jpg")
            cv2.imwrite(filename, frame)
            
            elapsed = time.time() - start_time
            if elapsed >= duration_sec:
                break
        
        self.cap.release()
        print(f"Capture terminée, {frame_idx} frames sauvegardées dans {self.output_dir}.")

