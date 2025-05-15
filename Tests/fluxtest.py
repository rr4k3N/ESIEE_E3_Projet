import sys
import os

# Ajouter le dossier parent à PYTHONPATH pour importer Camera.webcam
sys.path.append(os.path.abspath("../Camera"))

from webcam import Webcam

def main():
    cam = Webcam(width=640, height=480, fps=30, output_dir="../FrameCreation/Frames")
    cam.capture_frames(duration_sec=10)

if __name__ == "__main__":
    main()

