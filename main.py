
import cv2
from flask import Flask, flash, request, send_from_directory, render_template, Response
import time
import numpy as np
import base64
from PIL import Image
from flask_cors import CORS, cross_origin
import subprocess
import os
import shutil
import uuid
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # ignore tf warnings
import tensorflow as tf
import webbrowser
import urllib

camera = 1
ser = None
message = ""
classes = []
current_class = ""
model = ""
class_names = []

camera_object = cv2.VideoCapture(0)

with open("preferences.txt", "r") as file:
    lines = file.readlines()
    for line in lines:
        if line.startswith("http://"):
            IP_PORT = line.strip()
            print(IP_PORT)
            break

image = cv2.imread("offline.jpg")
ret, jpeg = cv2.imencode('.jpg', image)
pic = jpeg.tobytes()
        

def display_video():
    global pic
    global camera
    while True:
        if camera == 0:
            try:
                with urllib.request.urlopen(IP_PORT+'/get_video_frame') as f:
                    image=f.read()
                    
            except urllib.error.URLError as e:
                print(e.reason)
                time.sleep(1)
                image = ""

            if image !="":
                try:
                    nparr = np.frombuffer(image, np.uint8)
                    image_2 = cv2.imdecode(nparr,cv2.IMREAD_UNCHANGED) 
                    cv2.imwrite("temp.jpg", image_2)
                    ret, jpeg = cv2.imencode('.jpg', image_2)
                    pic = jpeg.tobytes()
                except:
                    pass
                #print("Video stream error")
        else:
            try:
                ret, picture = camera_object.read()
                k = 4
                width = int((picture.shape[1])/k)
                height = int((picture.shape[0])/k)
                picture = cv2.resize(picture, (width, height), interpolation=cv2.INTER_AREA)
                cv2.imwrite("temp.jpg", picture)
                ret, jpeg = cv2.imencode('.jpg', picture)
                pic = jpeg.tobytes()
            except:
                print("Camera error")

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + pic + b'\r\n\r\n')


def train():
    global model
    global class_names
    global message

    try:
        img_height = 180
        img_width = 180

        train_ds = tf.keras.utils.image_dataset_from_directory(
          "classes",
          labels="inferred",
          image_size=(img_height, img_width)
          )

        class_names = train_ds.class_names

        num_classes = len(class_names)

        model = tf.keras.models.Sequential([
          tf.keras.layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
          tf.keras.layers.Conv2D(16, 3, padding='same', activation='relu'),
          tf.keras.layers.MaxPooling2D(),
          tf.keras.layers.Conv2D(32, 3, padding='same', activation='relu'),
          tf.keras.layers.MaxPooling2D(),
          tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu'),
          tf.keras.layers.MaxPooling2D(),
          tf.keras.layers.Flatten(),
          tf.keras.layers.Dense(128, activation='relu'),
          tf.keras.layers.Dense(num_classes)
        ])

        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])

        epochs=10
        history = model.fit(train_ds, epochs=epochs)

        message = "Training Successful"
    except:
        message = "Training Failed"

def predict(data):
    global model
    global class_names

    img_height = 180
    img_width = 180

    if model != "":
        img = tf.keras.utils.load_img(
            "temp.jpg", target_size=(img_height, img_width)
        )
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0) 

        predictions = model.predict(img_array)
        score = tf.nn.softmax(predictions[0])

        if data == "class":
            return str(class_names[np.argmax(score)])
        else:
            return str(round(100 * np.max(score)))

def run_code(code):
    global proc

    if code != "":
        code_head ='''
# coding: latin-1
import src.fetchbot as fetchbot
import time

'''

        code = code_head + code
        with open("temp.py", "w+") as file:
            file.write(code)

        try:
            subprocess.Popen.terminate(proc)
        except:
            print("No process to terminate")

        proc = subprocess.Popen(['python','temp.py'])

    else:
        try:
            subprocess.Popen.terminate(proc)
        except:
            print("No process to terminate")
        global message
        message = ""

def display_images():
    global classes
    global current_class
    images = []
    if len(classes) > 0:
        class_directory = f"classes/{current_class}/"
        list_of_images = filter( lambda x: os.path.isfile(os.path.join(class_directory, x)),
                        os.listdir(class_directory) )
        list_of_images = sorted( list_of_images,
                                key = lambda x: os.path.getmtime(os.path.join(class_directory, x))
                                )
        for filename in list_of_images:
            with open(f"classes/{current_class}/{filename}", "rb") as image_file:
                encoded_string = (base64.b64encode(image_file.read())).decode()
                images.append(encoded_string)
        images.reverse()
    return images

def get_classes():
    global classes
    global current_class
    classes = []
    for folder in os.listdir(f"classes/"):
        classes.append(folder)
    if len(classes) > 0:
        current_class = classes[-1]
    return

def delete_classes():
    global current_class
    current_class = ""
    if os.path.isdir("classes") == True:
        shutil.rmtree("classes")
        os.mkdir("classes")
    else:
        os.mkdir("classes")
    return

def copy_image(target):
    try:
        shutil.copyfile("temp.jpg", target)
        img = Image.open(target)
        img.verify()
        return
    except:
        print("Bad image")
        copy_image(target)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

webbrowser.open("index.html")

@app.route('/video')
def video():
    global camera
    #if camera == 0:
    #    connect()
    return render_template("video.html")

@app.route('/jquery-3.6.0.js')
def js():
    return app.send_static_file('jquery-3.6.0.js')

@app.route('/video_feed')
def video_feed():
    return Response(display_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera', methods=['POST'])
def switch_camera():
    global camera
    if camera == 0:
        camera = 1
    else:
        camera =0
    return video()       

@app.route('/command', methods=['POST'])
def command():
    command = (request.data).decode()

    if command != "":    
        if command == "forward":
            print("forward")
            res=urllib.request.urlopen(IP_PORT+"/forward")
                    
        elif command == "backward":
            print("backward")
            res=urllib.request.urlopen(IP_PORT+"/backward")
                    
        elif command == "left":
            print("left")
            res=urllib.request.urlopen(IP_PORT+"/left")
                    
        elif command == "right":
            print("right")
            res=urllib.request.urlopen(IP_PORT+"/right")
        
        else:
            print(command) 

    return "200"

@app.route('/code', methods=['POST'])
def code():
    code = (request.data).decode()
    run_code(code)
    return "200"

@app.route('/message_in', methods=['POST'])
def message_in():
    global message
    message = ((request.data).decode('latin-1'))
    return "200"

@app.route('/message_out', methods=['POST'])
def message_out():
    global message
    return Response(message)

@app.route('/predict', methods=['POST'])
def predict_():
    data = (request.data).decode()

    return Response(predict(data))

@app.route('/classifier')
def classifier():
    run_code("")
    if os.path.isdir("classes") != True:
        os.mkdir("classes")
    get_classes()
    return render_template("classifier.html", classes=classes, images=display_images())

@app.route('/new_class', methods=['POST'])
def new_class():
    global classes
    global current_class
    if request.method == 'POST':
        new_class = request.form['new_class']
        if (new_class != "") and (new_class not in classes):
            classes.append(new_class)
            os.mkdir("classes/"+new_class)
            current_class = new_class
    return render_template("classifier.html", classes=classes, images=display_images())

@app.route('/select_class', methods=['POST'])
def select_class():
    global classes
    global current_class
    selected_class = request.form["selected_class"]
    classes.remove(selected_class)
    classes.sort()
    classes.append(selected_class)
    current_class = selected_class
    return render_template("classifier.html", classes=classes, images=display_images())

@app.route('/train', methods=['POST'])
def train_model():
    global classes
    if len(classes) > 0:
        train()
    return render_template("classifier.html", classes=classes, images=display_images())

@app.route('/delete_class', methods=['POST'])
def delete_class():
    global classes
    global current_class
    if current_class in classes:
        classes.remove(current_class)
    if os.path.isdir("classes/"+current_class) == True:
        shutil.rmtree("classes/"+current_class)
    if len(classes) > 0:
        current_class = classes[-1]
    else:
        current_class = ""
    return render_template("classifier.html", classes=classes, images=display_images())

@app.route('/delete_all', methods=['POST'])
def delete_all():
    global classes
    global current_class
    classes = []
    current_class = ""
    delete_classes()
    return render_template("classifier.html", classes=classes, images=display_images())

@app.route('/get_image', methods=['POST'])
def get_image():
    global current_class
    if current_class != "":
        unique = str(uuid.uuid4())
        print(unique)
        target = f"classes/{current_class}/{unique}.jpg"
        print(target)
        copy_image(target)
            
    return render_template("classifier.html", classes=classes, images=display_images())

app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)