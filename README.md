# Description
This is a code to run an OCR interface based on Docker build

# Steps to run
1. First clone the repository using `git clone https://github.com/Gauraviitkgp/OCR-interface.git`
2. Then build the docker image by using the command `docker build -t name:tag .`
3. Run the docker file on `docker run -p 5000:5000 name:tag`. Please ensure that the ports are mentioned correctly since they have been binded for it
4. POST the image request to http://localhost:5000/image-sync. Here the image json should contain a valid base64 image in “image_data” key and an optional “model” key. The model key can take two values “tesseract” for tesseract and “custom” for my model For eg. 
```
Data = {“image_data” : <base64 encoded>, “model” : :”tesseract”} for using tesseract
Data = {“image_data” : <base64 encoded>, “model” : :”custom”} for using custom-OCR
```
5. The localhost would return either of 2 things
    1. An error return. If there is an error in syntax then the server would immediately return an error json. For eg
`{"error":1,"message":"ERROR: Error name"}`
Here `error : 1` represent and error has occurred while reading the text. Error name would correspond to some description.
    2. An task_id or token if there is no syntax forms. The token should be used while requesting for output else it would give errors. If your syntax is correct. The server would return an example response
    ```
    { "task_id": "3",  "token": “eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MTYzMTM3MTIsImlhdCI6MTYxNjMxMzU5Miwic3ViIjozfQ.L018ZWCuEuFuN1hsyMv88Bb-CvEk6GeUYahz_koaQJU"}
    ```
    Token would expire after 2 mins. This could be changed from line 49 in app.py

6. To get output you need to run a GET command on  http://localhost:5000/image. This can return 3 things:
    1. An error return. If there is an error in processing the image then the server would immediately return an error json. For eg `{"error":1,"message":"ERROR: Error name"}`. Here `error : 1` represent and error has occurred while reading the text. Error name would correspond to some description
    2. A genuine output in that case return would be `{“text”: “You're Amazing”}`
    3. A return of text but text is null. It means that the server is still processing request and asks you to wait `{“text”: null}`

# Features
* The “image_data” in data is compatible as a dict or list. If you provide image data as a list of coded base64 images then it would give output in the SAME order. In case of the dict. It would provide output with the same keys.
* In most cases error would be notified via `{"error":1}` as an output sequence.
* To check the number of running threads make a api call to '/threads’
`curl -XGET "http://localhost:5000/threads"`
* To run an entire folder of images containing images id’d by their name in a dict use send_rqst.py. It subscribes to “./test_img” folder in your main directory. This will result in a query
    * `{“a0.png”:<a0 code>, “a1.png”:<a1 code>}`
* The application would fail if any of the images in the input set contains an error. However it would clearly specify in the input message which input image is causing the error
* Run `test.py` to run multiple predefined tests on the server.

# Model
## Flow
The model draws inspiration from MNIST and VGG net. First the input image is fed through a series of opencv transformations. We will take an example image to get what opencv does. 

--TODO: Update Later--




