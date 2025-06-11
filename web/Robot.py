from threading import Thread
from time import sleep
from Logger import Logger
import config
import cv2
import serial

# LeftMode (0: Back, 1: Brake, 2: Forward)
# LeftPWM
# RightMode
# RightPWM
class DIR:
    STOP    = 0
    FORWARD = 1
    LEFT    = 2
    RIGHT   = 3
    BACK    = 4



class Robot:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.logger = Logger(config.LOG_LEVEL, "SERIAL")
        
        self.con = None
        self.listen_thread = None

    def _open(self, do_log=False):
        try:
            if self.con is None:
                self.con = serial.Serial(self.port, self.baudrate)
                self.logger.info(f'Successfuly connected to port: {self.port}')
                return True

            elif not self.con.isOpen(): 
                self.con.open()
                self.logger.info(f'Successfuly connected to port: {self.port}')
                return True

        except serial.SerialException as e:
            if do_log:
                self.logger.error(f'Could\'t connect to serail port: {self.port} ({e})')
            self.con = None
            return False
    
    def is_open(self):
        return self.con is not None and self.con.isOpen()

    def open(self):
        if self.is_opened():
            self.logger.warn('Serial port is already connected')
            return

        self._openi(do_log=True)

    def close(self):
        if not self.is_opened():
            self.logger.warn('The serial port is not connected')
            return 

        self.con.close()


    def _con_listener(self):
        res = False
        while not res:
            res = self._open(do_log=False)
            sleep(0.2)

    def is_listening(self):
        return self.listen_thread is not None and self.listen_thread.is_alive()

    def listen_for_con(self):
        if self.is_listening():
            self.logger.warn('Already listening for Serial device to connect to')
            return 

        self.listen_thread = Thread(target=self._con_listener)
        self.listen_thread.deamon = True
        self.listen_thread.start()

    def stop_listener(self):
        if not self.is_listening():
            self.logger.warn('Not listening for Serial device')
            return
        
        self.listen_thread.kill()


    def write(self, buf):
        if not self.is_open():
            if not self.is_listening():
                self.logger.error('Lost conection to Serial')
                self.listen_for_con()

            return False
        
        try:
            self.con.write(buf)
        except:
            self.con.close()
            if not self.is_listening():
                self.logger.error('Lost conection to Serial')
                self.listen_for_con()

            return False

        return True
    
    def flush(self):
        self.write(bytes([70, 76]))

    def _send_command(self, lmode, lpwm, rmode, rpwm):
        self.write(bytes([72, 66, lmode, lpwm, rmode, rpwm]))

    def move(self, direction, speed):
        if direction == DIR.STOP:
            self._send_command(1, speed, 1, speed)
        elif direction == DIR.FORWARD:
            self._send_command(0, speed, 0, speed)
        elif direction == DIR.LEFT:
            self._send_command(0, speed, 2, speed)
        elif direction == DIR.RIGHT:
            self._send_command(2, speed, 0, speed)
        elif direction == DIR.BACK:
            self._send_command(2, speed, 2, speed)






