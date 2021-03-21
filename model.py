import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import os
import cv2
import random
import imutils
from imutils import contours
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,ZeroPadding2D,Flatten,Dropout,Activation,Conv2D,MaxPooling2D,Softmax
from keras.optimizers import Adam
from keras.losses import categorical_crossentropy
from keras.callbacks import ModelCheckpoint, EarlyStopping

# tf.config.optimizer.set_jit(True)

CHARS   = ' '+'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'+';:><.,+=-_'+'1234567890'

IMG_SIZE        = 30
BATCH_SIZE      = 100
LR              = 1e-3
CHPK_PATH       = "checkpoints\\cp.ckpt"
CHAR_SIZE       = len(CHARS)
EPOCHS          = 100

class CNNModel():
    def __init__(self,input_shape,lr=LR,batchsize=BATCH_SIZE,epochs=EPOCHS):
        self.model          = Sequential()
        self.input_shape    = input_shape
        self.lr             = lr
        self.batchsize      = batchsize
        self.epochs         = EPOCHS
        pass
    
    def VGG16net(self):
        self.model.add(ZeroPadding2D((1,1),input_shape=self.input_shape[1:]))
        self.model.add(Conv2D(64,(3,3)))
        self.model.add(Activation("relu"))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Conv2D(64,(3,3)))
        self.model.add(Activation("relu"))
        self.model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))

        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Conv2D(128,(3,3)))
        self.model.add(Activation("relu"))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Conv2D(128,(3,3)))
        self.model.add(Activation("relu"))
        self.model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))

        
        self.model.add(Flatten())
        self.model.add(Dense(4096, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(4096, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(73, activation='softmax'))
    
    def compile_model(self):
        opt = Adam(lr=self.lr)
        self.model.compile(optimizer=opt,loss = categorical_crossentropy, metrics=['accuracy'])

    def load_model(self):
        self.model.load_weights(CHPK_PATH)
        print("Model Load Complete")

    def train(self,trainX,trainY):
        checkpoint = ModelCheckpoint(CHPK_PATH, monitor='val_accuracy', verbose=1, save_best_only=True, save_weights_only=True, mode='auto', period=1)
        
        
        early = EarlyStopping(monitor='val_accuracy', min_delta=0.001, patience=10, verbose=1, mode='auto')
        self.model.fit(trainX,trainY,batch_size=self.batchsize,epochs=self.epochs, verbose=1,validation_split=0.25,callbacks=[early,checkpoint])

class images():
    def __init__(self,input_imgs,blur_kernal=(5,5),canny_thresh=150,otpt_size=(60,60)):
        self.input          = input_imgs
        self.blur_kernal    = blur_kernal
        self.CannyThresh    = canny_thresh
        self.size           = otpt_size
        self.test_output    = []
        self.display_output = None
        self.pos            = []

    def find_lines(self):
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (self.input.shape[1], 1))
        gray        = cv2.cvtColor(self.input, cv2.COLOR_BGR2GRAY)  
        _,thresh1   = cv2.threshold(gray, 0, 255,cv2.THRESH_OTSU|cv2.THRESH_BINARY_INV)
        dilation    = cv2.dilate(thresh1, rect_kernel, iterations = 1)
        ctrs        = cv2.findContours(dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        ctrs        = imutils.grab_contours(ctrs)
        ctrs        = contours.sort_contours(ctrs, method="top-to-bottom")
        self.lineco = []
        im2         = self.input.copy()
        for i,cnt in enumerate(ctrs[1] ):
            x, y, w, h = cnt
            if w*h>50*50:
                self.lineco.append([x, y])

        self.tot_lines = len(self.lineco)
        self.test_output    = [None for i in range(self.tot_lines)] 
        self.lineco = np.array(self.lineco)

    def process1(self):
        self.find_lines()

        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))

        gray        = cv2.cvtColor(self.input, cv2.COLOR_BGR2GRAY)  
        _,thresh1   = cv2.threshold(gray, 0, 255,cv2.THRESH_OTSU|cv2.THRESH_BINARY_INV)
        dilation    = cv2.dilate(thresh1, rect_kernel, iterations = 1)
        ctrs        = cv2.findContours(dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        ctrs        = imutils.grab_contours(ctrs)
        ctrs        = contours.sort_contours(ctrs, method="left-to-right")
        coordinates = []
        im2         = self.input.copy()
        for i,cnt in enumerate(ctrs[1] ):
            x, y, w, h = cnt
            if w*h>25*20:
                k = np.argmin(np.abs(self.lineco[:,1]-y))
                roi = thresh1[y:y + h, x:x + w]
                thresh = roi
                (tH, tW) = thresh.shape

                if tW > tH:
                    thresh = imutils.resize(thresh, width=self.size[1])
                else:
                    thresh = imutils.resize(thresh, height=self.size[0])

                padded = cv2.resize(thresh, (self.size[1], self.size[0]))

                padded1 = padded.astype("float32") / 255.0

                pd_expanded     = np.expand_dims(padded1,axis=0)
                pd_expanded_1   = np.expand_dims(pd_expanded,axis=3)
                if type(self.test_output[k]) == type(None):
                    self.test_output[k] = pd_expanded_1
                    self.pos            = [(x,y)]
                    # print(self.test_output.shape)
                else:
                    self.test_output[k] = np.append(self.test_output[k],pd_expanded_1,axis=0)
                    self.pos.append((x,y))
                cv2.imwrite("imgs\\a"+str(i)+".png", padded)

    def predict(self,net):
        self.chars = [None for i in range(self.tot_lines)]
        for i,line in enumerate(self.test_output):
            self.chars[i] = np.argmax(net.model.predict(line),axis=1)
            self.chars[i] = "".join(list(map(lambda x:CHARS[x],self.chars[i])))
            # print(sorted(self.char))
        self.chars = "\n".join(self.chars)
        return self.chars

def get_text(image):
    net = CNNModel((None,IMG_SIZE ,IMG_SIZE ,1))
    net.VGG16net()
    net.compile_model()
    net.load_model()

    test = images(image,otpt_size=(30,30))
    test.process1()
    test.predict(net)
    # # print(image)
    # # print(test.test_output)
    print(test.chars)
    return test.chars