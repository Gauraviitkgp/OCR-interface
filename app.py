import flask
from flask import request, jsonify
import base64 
import matplotlib.pyplot as plt
import numpy as np
import cv2
import pytesseract
import threading 
import time
import os
import jwt
import datetime
from model import get_text
SECRET_KEY =  os.urandom(24)

class img_rqst():
    def __init__(self,request,requestID=0):
        """Image Request Handler

        Args:
            request (flask:request): A flask request
            requestID (int, optional): An Id for a request. Defaults to 0.
        """
        self.error      = {"error":0,"message":""}

        self.request    = request
        self.requestID  = requestID
        self.data       = request.get_json(force=True)
        self.token      = None
        if self.__check_for_errors__():
            return
        self.img        = None
        self.encoding   = request.charset #Encoding
        self.tess_otpt  = None
        self.dict_otpt  = {"text":None}

        self.__encode_auth_token__()

        self.dict_rID   = {"task_id": str(requestID),"token":self.token}
        
        # self.run_tesseract()
    def __encode_auth_token__(self):
        """
            Generates the Auth Token
            :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=120),
                'iat': datetime.datetime.utcnow(),
                'sub': self.requestID
            }
            self.token =  jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e
    def decode_auth_token(self,auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token,SECRET_KEY,algorithms='HS256')
            return 0
        except jwt.ExpiredSignatureError:
            self.error  = {"error":1,"message":"ERROR: Signature expired. Please use a new request."}
            return 1
        except jwt.InvalidTokenError:
            self.error  = {"error":1,"message":"ERROR: Invalid token. Please try again with Valid Token"}
            return 1
        
    def run_tesseract(self):
        """Runs the tessereact OCR engine by calling specific steps
        """
        temp = self.data['image_data']
        if type(self.data['image_data']) is dict:
            self.dict_otpt["text"] = {}
            for key,values in temp.items():
                self.data['image_data'] = values
                if self.__decode_img__():
                    self.error["message"] += " image id:"+key
                    return
                tess_otpt = self.__apply_tess__()
                self.dict_otpt["text"][key] = tess_otpt["text"]

        elif type(self.data['image_data']) is list:
            self.dict_otpt["text"] = []
            for values in temp:
                self.data['image_data'] = values
                if self.__decode_img__():
                    self.error["message"] += " image code:"+values
                    return
                tess_otpt = self.__apply_tess__()
                self.dict_otpt["text"].append(tess_otpt["text"])
        else:
            if self.__decode_img__():
                return
            self.dict_otpt = self.__apply_tess__()

        self.data['image_data'] = temp 
        
        print("Request",self.requestID,"completed" )
    def __check_for_errors__(self):
        """Checks for Errors if any. Any error would be appended to self.error as a dict

        Returns:
            int: 1 if error is there  else 0
        """
        if 'image_data' not in self.data:
            self.error  = {"error":1,"message":"ERROR: Please Enter \"image_data\" data in column"}
            return 1
        elif self.data['image_data'] is "":
            self.error  = {"error":1,"message":"ERROR: Please Enter Some \"image_data\" data in column"}
            return 1
        return 0


    def __decode_img__(self):
        """Decodes the image from base64 stype to Numpy

        Returns:
            int: 1 if decoding encountered an error 0 if not
        """            
        encoded64_image = self.data['image_data']
        try:
            image_64_decode = base64.decodebytes(encoded64_image.encode(encoding=self.encoding))
        except:
            self.error  = {"error":1,"message":"ERROR: Incorrect Encoding Please Re-Check"}
            return 1
        nparr           = np.frombuffer(image_64_decode, np.uint8)
        self.img        = cv2.imdecode(nparr,0)
        return 0

    def __apply_tess__(self):
        """Applies tesseract for the decoded image
        """
        if 'model' not in self.data or self.data['model'] == 'tesseract':
            self.tess_otpt = pytesseract.image_to_string(self.img)
        elif self.data['model'] == 'custom':
            # print(self.img.shape)
            backtorgb = cv2.cvtColor(self.img,cv2.COLOR_GRAY2RGB)
            self.tess_otpt = get_text(backtorgb)
        else:
            self.error  = {"error":1,"message":"ERROR: Model not found please check current avialable models are custom and tesseract"}
        
        return {"text":self.tess_otpt}

    def show(self,windowname="Input_Image",waitkey=1000):
        """Displays the input image

        Args:
            windowname (str, optional): Windowname. Defaults to "Input_Image".
            waitkey (int, optional): OpenCV waitkey to pause. Defaults to 1000.
        """
        cv2.imshow(windowname,self.img)
        cv2.waitKey(waitkey)

    def get_text(self):
        """Returns the OCR-text

        Returns:
            json: a json object of ocr text
        """
        print(self.tess_otpt)
        return jsonify(self.dict_otpt)

tasks   = {}
threads = []

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def start_tess(rqst):
    """A function to initiate tesseract

    Args:
        rqst (img_rqst object): object which would run tesseract
    """
    rqst.run_tesseract()


@app.route('/', methods=['GET'])
def home():
    return "<h1>OCR engine </h1><p>This site is for recieving and OCR output for sample inputs.</p>"

@app.route('/image-sync', methods=['GET','POST'])
def recognize():
    if request.method == 'POST':
        rqst = img_rqst(request,len(tasks))
        if rqst.error["error"]:
            return rqst.error["message"]

        tasks[rqst.requestID] = rqst
        A = threading.Thread(target=start_tess, args=(rqst,))
        threads.append(A)
        A.start()
        print("Request",rqst.requestID,"initiated")
        return jsonify(rqst.dict_rID)
    return "Request not processed.\n"

@app.route('/image', methods=['GET','POST'])
def check():
    data       = request.get_json(force=True)
    try:
        task_id = int(data["task_id"])
    except ValueError:
        return "ERROR: Please enter an integer value in task_id column; Currently entered:"+data["task_id"]
    except KeyError:
        return "ERROR: Please enter a column with name \"task_id\""

    if "token" not in data:
        return "ERROR: Token is not specified. Please add a token column into your data"

    if task_id not in tasks:
        return "ERROR: The specified task id does not exist. Please check"
    else:
        tasks[task_id].decode_auth_token(data["token"])
        if tasks[task_id].error["error"]:
            return jsonify(tasks[task_id].error)
        return jsonify(tasks[task_id].dict_otpt)

@app.route('/threads', methods=['GET'])
def print_active_threads():
    """Prints the list of active threads

    Returns:
        str: List of Active threads in seperate lines
    """
    main_thread = threading.current_thread()
    threads     = ""
    for t in threading.enumerate():
        if t is main_thread:
            continue
        print(t.getName())
        threads+=t.getName()+"\n"
    return threads
        # logging.debug('joining %s', t.getName())
    
# app.run(port=5000,host='0.0.0.0')
if os.name == 'nt':
    app.run(port=5000)
else:
    app.run(port=5000,host='0.0.0.0')

for thread in threads:
    thread.join()