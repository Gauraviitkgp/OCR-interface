import cv2
import base64
import requests
#remove-item alias:\curl
#curl -XGET "http://localhost:5000/image" -d '{\"task_id\": \"3\"}'
import json
imagename = 'test_img/0.png'

Img         = cv2.imread(imagename)
# display_image(Img) 
_, buffer   = cv2.imencode(imagename[-4:], Img)
jpg_as_text = base64.b64encode(buffer)
url         = "http://localhost:5000/image-sync"

# Test 1: Send no data
data        = ""
res         = requests.post(url, data=json.dumps(data))
print(res.text)

# Test 2: Send abrupt key
data        = {"abcd": "efgh"}
res         = requests.post(url, data=json.dumps(data))
print(res.text)

# Test 3: Send abrupt multiple keys
data        = {"abcd": "efgh","fegh": "efghx"}
res         = requests.post(url, data=json.dumps(data))
print(res.text)

# Test 3: Send fake data
data        = {"image_data": "adasd"}
res         = requests.post(url, data=json.dumps(data))
print(res.text)

# Test 4: Send empty data
data        = {"image_data": ""}
res         = requests.post(url, data=json.dumps(data))
print(res.text)

# Test 5: Send correct data
data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\""}
res         = requests.post(url, data=json.dumps(data))
print(res.text)