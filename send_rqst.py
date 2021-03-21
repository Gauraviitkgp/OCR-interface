import cv2
import base64
import requests
import os
import time
#remove-item alias:\curl
#curl -XGET "http://localhost:5000/image" -d '{\"task_id\": \"3\"}'
import json

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images

def display_image(Img):
    cv2.imshow('Image',Img)
    cv2.waitKey(1000)

def send_data(jpg_as_text):
    url         = "http://localhost:5000/image-sync"
    if type(jpg_as_text) is dict:
        data        = {"image_data": jpg_as_text}

    else:
        data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\""}
    # json.
    res         = requests.post(url, data=json.dumps(data))
    json_data   = json.loads(res.text)
    print(res.text)
    return json_data

def recieve_output(task_id,token_id):
    url         = "http://localhost:5000/image"
    data        = {"task_id": task_id,"token":token_id}

    res         = requests.get(url, data=json.dumps(data))
    json_data   = json.loads(res.text)
    if json_data["text"] is not None:
        print(task_id,"\n",res.text)
        return 0
    else:
        return 1



folder = "test_img"
images = os.listdir(folder)
dct = {}
print(images)
for imagename in images:

    Img             = cv2.imread(os.path.join(folder,imagename))
    # display_image(Img) 
    retval, buffer  = cv2.imencode(os.path.join(folder,imagename)[-4:], Img)
    jpg_as_text     = base64.b64encode(buffer)

    dct[imagename] = "\""+str(jpg_as_text)[2:-1]+"\""

# print(dct)
ids = send_data(dct)


while recieve_output(ids['task_id'],ids['token']):
    time.sleep(1)
    pass


# Get Curl command for the image
# J = "curl -XPOST \"http://localhost:5000/image-sync\" -d '{\\\"image_data\\\":\\\""+str(jpg_as_text)[2:-1]+"\\\"}'"
# print(J)

# print("\\")