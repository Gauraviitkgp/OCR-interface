import cv2
import base64
import requests
#remove-item alias:\curl
import json

def display_image(Img):
    cv2.imshow('Image',Img)
    cv2.waitKey(1000)

def send_data(jpg_as_text):
    url = "http://localhost:5000/image-sync"
    data = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\""}
    # json.
    res = requests.post(url, data=json.dumps(data))
    print(res.text)

imagename = 'test_img/img1.png'

Img             = cv2.imread(imagename)
# display_image(Img) 
retval, buffer  = cv2.imencode(imagename[-4:], Img)
jpg_as_text     = base64.b64encode(buffer)

send_data(jpg_as_text)

# Get Curl command for the image
# J = "curl -XPOST \"http://localhost:5000/image-sync\" -d '{\\\"image_data\\\":\\\""+str(jpg_as_text)[2:-1]+"\\\"}'"
# print(J)

# print("\\")