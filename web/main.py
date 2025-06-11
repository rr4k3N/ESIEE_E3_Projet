from BaseCamera import Camera
from Robot import Robot, DIR
from flask import Flask, render_template, Response, request, jsonify
from threading import Thread
from time import sleep
import cv2


def cam_thread(cam: Camera):
    while True:
        global frame
        img = cv2.imencode('.jpg', cam.capture_frame())[1].tobytes()
        frame = (b'--frame\r\n'
                 b'Content-Type: image/jpg\r\n\r\n' + img + b'\r\n')

        sleep(0.03)


global frame, speed
app = Flask(__name__)

cam = Camera(0)
cam.listen_for_cam()

bot = Robot('/dev/ttyUSB0', 115200)
speed = 90
bot.listen_for_con()


thread = Thread(target=cam_thread, args=(cam,))
thread.daemon = True
thread.start()

frame = cam._no_device_frame()



@app.route("/")
def home():
    return render_template("index.html")


def gen():
    while True: 
        yield frame
        sleep(0.03)

@app.route("/video")
def video():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


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
