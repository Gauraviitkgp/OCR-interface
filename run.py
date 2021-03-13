import flask
from flask import request, jsonify
import base64 
import matplotlib.pyplot as plt
import numpy as np
import cv2
import pytesseract
import threading 
import time

class img_rqst():
    def __init__(self,request,requestID=0):
        self.request    = request
        self.requestID  = requestID
        self.data       = request.get_json(force=True)
        self.img        = None
        self.encoding   = request.charset #Encoding
        self.tess_otpt  = None
        self.dict_otpt  = {"text":None}

        self.dict_rID   = {"task_id": str(requestID)}
        # self.run_tesseract()

    def run_tesseract(self):
        time.sleep(20)
        self.__decode_img__()
        self.__apply_tess__()
        

    def __decode_img__(self):
        encoded64_image = self.data['image_data']
        image_64_decode = base64.decodebytes(encoded64_image.encode(encoding=self.encoding))
        nparr           = np.frombuffer(image_64_decode, np.uint8)
        self.img        = cv2.imdecode(nparr,0)

    def __apply_tess__(self):
        self.tess_otpt = pytesseract.image_to_string(self.img)
        self.dict_otpt = {"text":self.tess_otpt}

    def show(self,windowname="Input_Image",waitkey=1000):
        cv2.imshow(windowname,self.img)
        cv2.waitKey(waitkey)

    def get_text(self):
        print(self.tess_otpt)
        return jsonify(self.dict_otpt)

tasks   = {}
threads = []

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def start_tess(rqst):
    rqst.run_tesseract()


@app.route('/', methods=['GET'])
def home():
    return "<h1>OCR engine </h1><p>This site is for recieving and OCR output for sample inputs.</p>"

@app.route('/image-sync', methods=['GET','POST'])
def recognize():
    if request.method == 'POST':
        rqst = img_rqst(request,len(tasks))
        tasks[rqst.requestID] = rqst
        A = threading.Thread(target=start_tess, args=(rqst,))
        threads.append(A)
        A.start()
        print("Request",rqst.requestID,"processed")
        return jsonify(rqst.dict_rID)
    return "Request not processed.\n"

@app.route('/image', methods=['GET','POST'])
def check():
    data       = request.get_json(force=True)
    try:
        task_id = int(data["task_id"])
    except ValueError:
        return "ERROR: Please enter an integer value in task_id column"

    if task_id not in tasks:
        return "ERROR: The specified task id does not exist. Please check"
    else:
        return jsonify(tasks[task_id].dict_otpt)
    
app.run()
# x = threading.Thread(target=recognize, args=())
for thread in threads:
    thread.join()