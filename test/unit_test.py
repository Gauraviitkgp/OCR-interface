import unittest
import cv2
import base64
import requests
import json
import re
import time
imagename = 'test/imgs/1.jpg'

Img         = cv2.imread(imagename)
# display_image(Img) 
_, buffer   = cv2.imencode(imagename[-4:], Img)
jpg_as_text = base64.b64encode(buffer)
url         = "http://localhost:5000/image-sync"
url1        = "http://localhost:5000/image"

p1          = re.compile('{\s*"task_id":\s*"\w*",\s*"token": ".*"[\s]*}')
p2          = re.compile('ERROR: Incorrect Encoding Please Re-Check image code:\d*')

class TestOCRInterface(unittest.TestCase):
      
    def setUp(self):
        pass

    def checkcorrect(self,res_dict):
        self.assertTrue("error" in res_dict)
        self.assertTrue("message" in res_dict)
        self.assertTrue("text" in res_dict)

        self.assertEqual(res_dict["error"],0)
        self.assertNotEqual(res_dict["text"],None)
    
    # Test 1: Send no data
    def test_no_data(self):
        data        = ""
        res         = requests.post(url, data=json.dumps(data))
        self.assertEqual(res.text, 'ERROR: Please Enter "image_data" data in column')
    
    # Test 2: Send Random Key
    def test_send_random_key(self):
        data        = {"abcd": "efgh"}
        res         = requests.post(url, data=json.dumps(data))
        self.assertEqual(res.text, 'ERROR: Please Enter "image_data" data in column')

    # Test 3: Send Multiple Random Key
    def test_send_multiple_random_key(self):
        data        = {"abcd": "efgh","fegh": "efghx"}
        res         = requests.post(url, data=json.dumps(data))
        self.assertEqual(res.text, 'ERROR: Please Enter "image_data" data in column')

    # Test 4: Send Fake Data
    def test_fake_data(self):
        data        = {"image_data": "adasd"}
        res         = requests.post(url, data=json.dumps(data))
        self.assertNotEqual(None,p1.match(res.text))

        data1       = res.text
        res1        = requests.post(url1, data=json.dumps(data1))
        res_dict    = json.loads(res1.text)
        self.assertTrue("error" in res_dict)
        self.assertTrue("message" in res_dict)
        self.assertEqual(res_dict["error"],1)
        self.assertEqual(res_dict["message"],"ERROR: Incorrect Encoding Please Re-Check")
    # Test 5: Send empty data
    def test_empty_data(self):
        data        = {"image_data": ""}
        res         = requests.post(url, data=json.dumps(data))
        self.assertEqual(res.text, 'ERROR: Please Enter Some "image_data" data in column')

    # Test 6: Send correct data
    def test_send_correct_data(self):
        data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\""}
        res         = requests.post(url, data=json.dumps(data))
        self.assertNotEqual(None,p1.match(res.text))
        time.sleep(5)
        data1       = res.text
        res1        = requests.post(url1, data=json.dumps(data1))
        res_dict    = json.loads(res1.text)
        
        self.checkcorrect(res_dict)    

    def test_some_extra_data_too(self):
        data        = {"image_data": "\""+str(jpg_as_text)[2:-1]+"\"", "abcd":"edfgh"}
        res         = requests.post(url, data=json.dumps(data))
        self.assertNotEqual(None,p1.match(res.text))
        time.sleep(5)
        data1       = res.text
        res1        = requests.post(url1, data=json.dumps(data1))
        res_dict    = json.loads(res1.text)
        
        self.checkcorrect(res_dict)    
    
    # Test 9: Send a dict in image_data requests incorrect
    def test_incorrect_dict(self):
        data        = {"image_data": {"1":"233","2":"2332"}}
        res         = requests.post(url, data=json.dumps(data))
        self.assertNotEqual(None,p1.match(res.text))

        time.sleep(5)

        data1       = res.text
        res1        = requests.post(url1, data=json.dumps(data1))
        res_dict    = json.loads(res1.text)
        self.assertTrue("error" in res_dict)
        self.assertTrue("message" in res_dict)
        self.assertEqual(res_dict["error"],1)
        self.assertEqual(res_dict["message"],"ERROR: Incorrect Encoding Please Re-Check image id:1")
        # print("Running test 9:\n",res1.text)

    # Test 10: Send a dict in image_data requests correct
    def test_correct_dict(self):
        data        = {"image_data": {"1":"\""+str(jpg_as_text)[2:-1]+"\"","2":"\""+str(jpg_as_text)[2:-1]+"\""}}
        res         = requests.post(url, data=json.dumps(data))
        self.assertNotEqual(None,p1.match(res.text))

        time.sleep(5)

        data1       = res.text
        res1        = requests.post(url1, data=json.dumps(data1))
        res_dict    = json.loads(res1.text)
        
        self.checkcorrect(res_dict)        

    def test_incorrect_list(self):
        data        = {"image_data": ["233","2332"]}
        res         = requests.post(url, data=json.dumps(data))
        self.assertNotEqual(None,p1.match(res.text))

        time.sleep(5)

        data1       = res.text
        res1        = requests.post(url1, data=json.dumps(data1))
        res_dict    = json.loads(res1.text)
        self.assertTrue("error" in res_dict)
        self.assertTrue("message" in res_dict)
        self.assertEqual(res_dict["error"],1)
        self.assertNotEqual(None,p2.match(res_dict["message"]))

    def test_correct_list(self):
        data        = {"image_data": [str(jpg_as_text)[2:-1],str(jpg_as_text)[2:-1]]}
        res         = requests.post(url, data=json.dumps(data))
        self.assertNotEqual(None,p1.match(res.text))

        time.sleep(5)

        data1       = res.text
        res1        = requests.post(url1, data=json.dumps(data1))
        res_dict    = json.loads(res1.text)
        self.checkcorrect(res_dict)  

    # Test 16: Check incorrect task id
    def test_incorrect_task_id(self):
        data        = {"task_id": 541131,"token":0}
        res         = requests.post(url1, data=json.dumps(data))
        self.assertEqual(res.text, 'ERROR: The specified task id does not exist. Please check')

    # Test 17: Check no task id
    def test_no_task_id(self):
        data        = {"token":0}
        res         = requests.post(url1, data=json.dumps(data))
        self.assertEqual(res.text, 'ERROR: Please enter a column with name "task_id"')
    # Test 18: Check empty
    def test_empty(self):
        data        = {}
        res         = requests.post(url1, data=json.dumps(data))
        self.assertEqual(res.text, 'ERROR: Please enter a column with name "task_id"')
    # Test 19: Check no token id
    def test_no_token_id(self):
        data        = {"task_id": 0}
        res         = requests.post(url1, data=json.dumps(data))
        self.assertEqual(res.text, 'ERROR: Token is not specified. Please add a token column into your data')
    # Test 20: Random token id 
    def test_random_token_id(self):
        data        = {"task_id": 0,"token":0}
        res         = requests.post(url1, data=json.dumps(data))
        res_dict    = json.loads(res.text)

        self.assertTrue("error" in res_dict)
        self.assertTrue("message" in res_dict)
        self.assertEqual(res_dict["error"],1)
        self.assertEqual(res_dict["message"],"ERROR: Invalid token. Please try again with Valid Token")
if __name__ == '__main__':
    unittest.main()