from FrameCreation.video_capture_processor import VideoCaptureProcessor
from FrameCreation.frame_selector import FrameSelector

# Pipeline GStreamer (modifiable résolution/framerate)
gst_str = (
    "v4l2src device=/dev/video0 ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "nvvidconv ! video/x-raw(memory:NVMM), format=I420 ! "
    "nvvidconv ! video/x-raw, format=BGRx ! "
    "videoconvert ! video/x-raw, format=BGR ! appsink"
)

frames_folder = "./FrameCreation/RawFrames"
selected_folder = "./FrameCreation/SelectedFrames"

# Paramètres personnalisables
frame_rate = 30              # Nombre de frames par seconde
selection_interval = 1       # Intervalle de sélection (en secondes)
n_best_frames = 2            # Nombre de meilleures frames à garder à chaque intervalle
capture_duration = 10        # Durée totale de capture (en secondes)

# Lancement du processeur vidéo avec sélection des meilleures frames
processor = VideoCaptureProcessor(
    gst_pipeline=gst_str,
    frames_folder=frames_folder,
    selected_folder=selected_folder,
    frame_rate=frame_rate,
    selection_interval=selection_interval,
    n_best=n_best_frames
)

processor.process(duration_sec=capture_duration)
