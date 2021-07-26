import cv2
import base64
import requests
#remove-item alias:\curl
#curl -XGET "http://localhost:5000/image" -d '{\"task_id\": \"3\"}'
import json
imagename = 'imgs/0.jpg'

Img         = cv2.imread(imagename)
# display_image(Img) 
_, buffer   = cv2.imencode(imagename[-4:], Img)
jpg_as_text = base64.b64encode(buffer)
url         = "http://localhost:5000/image-sync"
url1        = "http://localhost:5000/image"

# Test 1: Send no data
data        = ""
res         = requests.post(url, data=json.dumps(data))
print("Running test 1:\n",res.text)

# Test 2: Send abrupt key
data        = {"abcd": "efgh"}
res         = requests.post(url, data=json.dumps(data))
print("Running test 2:\n",res.text)

# Test 3: Send abrupt multiple keys
data        = {"abcd": "efgh","fegh": "efghx"}
res         = requests.post(url, data=json.dumps(data))
print("Running test 3:\n",res.text)

# Test 4: Send fake data
data        = {"image_data": "adasd"}
res         = requests.post(url, data=json.dumps(data))
print("Running test 4:\n",res.text)

# Test 5: Send empty data
data        = {"image_data": ""}
res         = requests.post(url, data=json.dumps(data))
print("Running test 5:\n",res.text)

# Test 6: Send correct data
data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\""}
res         = requests.post(url, data=json.dumps(data))
print("Running test 6:\n",res.text)

# Test 7: Send correct data and some extra data
data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\"", "abcd":"edfgh"}
res         = requests.post(url, data=json.dumps(data))
print("Running test 7:\n",res.text)

# Test 8: Send 60 requests
for i in range(60):
    res         = requests.post(url, data=json.dumps(data))
    print("Running test 8:\n",res.text)

# Test 9: Send a dict in image_data requests incorrect
data        = {"image_data": {"1":"233","2":"2332"}}
res         = requests.post(url, data=json.dumps(data))
print("Running test 9:\n",res.text)

# Test 10: Send a dict in image_data requests correct
data        = {"image_data": {"1":"\""+str(jpg_as_text)[2:-1]+"\"","2":"\""+str(jpg_as_text)[2:-1]+"\""}}
res         = requests.post(url, data=json.dumps(data))
print("Running test 10:\n",res.text)

# Test 11: Send a list in image_data requests incorrect
data        = {"image_data": ["233","2332"]}
res         = requests.post(url, data=json.dumps(data))
print("Running test 11:\n",res.text)

# Test 12: Send a list in image_data requests correct
data        = {"image_data": [str(jpg_as_text)[2:-1],str(jpg_as_text)[2:-1]]}
res         = requests.post(url, data=json.dumps(data))
print("Running test 12:\n",res.text)

# Test 13: Change model to tess
data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\"","model":"tesseract"}
res         = requests.post(url, data=json.dumps(data))
print("Running test 13:\n",res.text)

# Test 14: Change model to custom
data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\"","model":"custom"}
res         = requests.post(url, data=json.dumps(data))
print("Running test 14:\n",res.text)

# Test 15: Change model to faltu
data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\"","model":"faltu"}
res         = requests.post(url, data=json.dumps(data))
print("Running test 15:\n",res.text)

# Test 16: Check incorrect task id
data        = {"task_id": 541131,"token":0}
res         = requests.post(url1, data=json.dumps(data))
print("Running test 16:\n",res.text)

# Test 17: Check no task id
data        = {"token":0}
res         = requests.post(url1, data=json.dumps(data))
print("Running test 17:\n",res.text)

# Test 18: Check empty
data        = {}
res         = requests.post(url1, data=json.dumps(data))
print("Running test 18:\n",res.text)

# Test 19: Check no token id
data        = {"task_id": 0}
res         = requests.post(url1, data=json.dumps(data))
print("Running test 19:\n",res.text)

# Test 20: Random token id
data        = {"task_id": 0,"token":0}
res         = requests.post(url1, data=json.dumps(data))
print("Running test 19:\n",res.text)
