from threading import Thread
from time import sleep
from Logger import Logger
import config
import cv2
import numpy as np


class Camera:
    def __init__(self, source=None, res=(640, 480)):
        self.source = source
        self.logger = Logger(config.LOG_LEVEL, "CAMERA")
        self.res = res

        self.cam = None
        self.listen_thread = None

    def _open(self, do_log=False): 
        if self.source is None: return True
        cam = cv2.VideoCapture(self.source)

        if not cam.isOpened():
            if do_log: self.logger.error(f'Could\'t connect to camera: {self.source}')
            return False

        self.res = (int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.cam = cam
        self.logger.info(f'Successfuly connected to camera: {self.source}')
        return True
    
    def is_opened(self):
        return self.cam is not None and self.cam.isOpened()

    def open(self):
        if self.is_opened(): 
            self.logger.warn('The camera is already open')
            return

        self._open(do_log=True)
    
    def close(self):
        if not self.is_opened():
            self.logger.warn('The camera is not open')
            return
        
        self.cam.release()

    
    def _cam_listener(self):
        res = False
        while not res:
            res = self._open(do_log=False)
            sleep(0.2)

    def is_listening(self):
        return self.listen_thread is not None and self.listen_thread.is_alive()

    def listen_for_cam(self):
        if self.is_listening():
            self.logger.warn('Already listening for camera to connect to')
            return

        self.listen_thread = Thread(target=self._cam_listener)
        self.listen_thread.daemon = True
        self.listen_thread.start()
    
    def stop_listener(self):
        if not self.is_listening():
            self.logger.warn('Not listening for camera')
            return

        self.listen_thread.kill()
    

    def _no_device_frame(self):
        img_arr = (np.random.random(self.res[::-1]) * 255).astype('uint8')
        img = cv2.cvtColor(img_arr, cv2.COLOR_GRAY2BGR)

        cx, cy = self.res[0] // 2, self.res[1] // 2
        text_size, _ = cv2.getTextSize('No Device', cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        tx, ty = text_size

        cv2.rectangle(img, (cx - tx // 2 - 10, cy + ty // 2 + 10), (cx + tx // 2 + 10, cy - ty // 2 - 10), (0, 0, 0), -1)
        cv2.putText(img, 'No Device', (cx - tx // 2, cy + ty // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        return img

    def capture_frame(self):
        if not self.is_opened():
            if not self.is_listening() and self.source is not None:
                self.logger.error('Lost connection to camera')
                self.listen_for_cam()
            
            return self._no_device_frame()
        
        suc, frame = self.cam.read()
        if not suc: 
            self.logger.error('Lost connection to camera')
            if self.is_opened(): self.cam.release()
            self.listen_for_cam()
            return self._no_device_frame()
        
        return frame

