import cv2
import base64
import requests
#remove-item alias:\curl
#curl -XGET "http://localhost:5000/image" -d '{\"task_id\": \"3\"}'
import json

def display_image(Img):
    cv2.imshow('Image',Img)
    cv2.waitKey(1000)

def send_data(jpg_as_text):
    url         = "http://localhost:5000/image-sync"
    data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\"","model":"custom"}
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
        print(res.text)
        return 0
    else:
        return 1



ids = []
for i in range(1):
    imagename = 'test_img/inpt.png'

    Img             = cv2.imread(imagename)
    # display_image(Img) 
    retval, buffer  = cv2.imencode(imagename[-4:], Img)
    jpg_as_text     = base64.b64encode(buffer)

    ids.append(send_data(jpg_as_text))

for i in ids:
    while recieve_output(i['task_id'],i['token']):
        pass


# Get Curl command for the image
# J = "curl -XPOST \"http://localhost:5000/image-sync\" -d '{\\\"image_data\\\":\\\""+str(jpg_as_text)[2:-1]+"\\\"}'"
# print(J)

# print("\\")