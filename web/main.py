from BaseCamera import Camera
from flask import Flask, render_template, Response
from threading import Thread
from time import sleep
import cv2


global frame
app = Flask(__name__)

def cam_thread(cam: Camera):
    while True:
        global frame
        img = cv2.imencode('.jpg', cam.capture_frame())[1].tobytes()
        frame = (b'--frame\r\n'
                 b'Content-Type: image/jpg\r\n\r\n' + img + b'\r\n')

        sleep(0.03)

def gen():
    while True: 
        yield frame
        sleep(0.03)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/video")
def video():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


def main():
    global frame
    cam = Camera(0)
    cam.listen_for_cam()

    frame = cam._no_device_frame()


    thread = Thread(target=cam_thread, args=(cam,))
    thread.daemon = True
    thread.start()

    app.run(host="0.0.0.0", port=8000)

        

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("Process killed by user")



# img = cv2.imencode('.jpg',self.frames)[1].tobytes()

# def gen(camera):
# 	logger.debug("Starting stream")
# 	while True:
# 		frame = camera.get_frame()
# 		yield (b'--frame\r\n'
# 			   b'Content-Type: image/jpg\r\n\r\n' + frame + b'\r\n')
            
    # return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')