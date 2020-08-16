import os

from flask import Flask
import logging

import cv2
import time
from datetime import datetime

from keras.models import load_model
from keras.preprocessing import image
from keras.models import model_from_json
import numpy as np
from PIL import Image
import keras

app = Flask(__name__)

json_file = open('model-covers.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
app.model = model_from_json(loaded_model_json)

app.rtsp_url = os.getenv('RTSP_URL')

# load weights into new model
app.model.load_weights("model_covers_saved.h5")
logging.info("Loaded model")

@app.route('/covers-status', methods=['GET'])
def cover_status():

    ret_val = 'unknown' 

    rtsp_url = app.rtsp_url
        
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        app.logger.error("Failed to open stream!")
        return ret_val
        
    ret, frame = cap.read()
    if ret==False:
        app.logger.error("Failed to read stream!")
        return ret_val
  
    img_cropped = frame[400:1080, 100:1300]

    image=Image.fromarray(
                        cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB)
                        )
    image = image.resize((320,170))
    input_arr = keras.preprocessing.image.img_to_array(image)
    input_arr /= 255.0
    input_arr = np.array([input_arr])  # Convert single image to a batch.
    
    classes = (app.model.predict(input_arr) > 0.5).astype("int32")
    
    ret_val = "on" if classes[0][0] == 1 else "off"
    
    
    return ret_val


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")