from BaseCamera import Camera
from Robot import Robot, DIR
from flask import Flask, render_template, Response, request, jsonify
from threading import Thread
from time import sleep
import cv2


def cam_thread(cam: Camera):
    while True:
        global is_no_device, frame
        img_buf, suc = cam.capture_frame()
        img = cv2.imencode('.jpg', img_buf)[1].tobytes()
        
        is_no_device, frame = not suc, img

        sleep(0.03)


global is_no_device, frame, speed
app = Flask(__name__)

cam = Camera(0)
cam.listen_for_cam()

bot = Robot('/dev/ttyUSB0', 115200)
speed = 90
bot.listen_for_con()


thread = Thread(target=cam_thread, args=(cam,))
thread.daemon = True
thread.start()

is_no_device, frame = True, cam._no_device_frame()



@app.route("/")
def home():
    return render_template("index.html")


def gen():
    while True: 
        yield (b'--frame\r\n'
               b'Content-Type: image/jpg\r\n\r\n' + frame + b'\r\n')

        sleep(0.03)

@app.route("/video")
def video():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/frame")
def frame():
    return Response(frame, mimetype="image/jpg", status=200 if not is_no_device else 201)

@app.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    direction = data.get("direction", "").strip()
    
    if direction in ["up", "down", "left", "right", "stop"]:
        if direction == "up":
            bot.move(DIR.FORWARD, speed)
        elif direction == "down":
            bot.move(DIR.BACK, speed)
        elif direction == "left":
            bot.move(DIR.LEFT, speed)
        elif direction == "right":
            bot.move(DIR.RIGHT, speed)
        elif direction == "stop":
            bot.move(DIR.STOP, speed)
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "invalid command"}), 400



def main():
    app.run(host="0.0.0.0", port=8000)

        

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("Process killed by user")