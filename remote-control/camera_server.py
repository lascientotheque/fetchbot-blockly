#!/usr/bin/env python
# coding: utf-8

try:
    import motor_control
except:
    print("No detected GPIO pin for motor control")

# For receiving images from the camera
import cv2

# For the Web server
import flask  


# Set motor speed
motor_speed=0.25
# Set duration
duration=0.5

camera_object = cv2.VideoCapture(0)

# Start Flask app (Web server)
app = flask.Flask("Remote control")



# Define the control as a function of the URL
@app.route('/')
def index():
    return flask.render_template("index.html")

@app.route('/video_feed')
def video_feed():

    ret, picture = camera_object.read()
    #picture_rgb = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB)
    picture_rgb=picture

    ret, jpeg = cv2.imencode('.jpg', picture_rgb)
    pic = jpeg.tobytes()

    return(pic)

@app.route('/forward')
def button_forward():
    motor_control.forward(speed=motor_speed, duration=duration)
    return ""
    
@app.route('/backward')
def button_backward():
    motor_control.backward(speed=motor_speed, duration=duration)
    return ""
    
@app.route('/left')
def button_left():
    motor_control.turn_left(speed=motor_speed, duration=duration)
    return ""
    
@app.route('/right')
def button_right():
    motor_control.turn_right(speed=motor_speed, duration=duration)
    return ""

# Start Web server
app.run(host='0.0.0.0', port=2204, threaded=True, debug=False)

