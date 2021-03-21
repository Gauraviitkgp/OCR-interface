import numpy as np
import random
from PIL import ImageFont, ImageDraw, Image
import cv2

DISPLAY     = False
HEIGHT      = 30
WIDTH       = 30
CHANNELS    = 3
CHARS       = ' '+'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'+';:><.,+=-_'+'1234567890'
FONTPATHS   = ['C:\\Windows\\Fonts\\verdanab.ttf','C:\\Windows\\Fonts\\ARIALN.TTF','C:\\Windows\\Fonts\\calibri.ttf','C:\\Windows\\Fonts\\times.ttf']
LEN_DATASET = 10000 if DISPLAY is False else 10

fontpaths   = random.choices(FONTPATHS,k=LEN_DATASET)
bs,gs,rs,a  = 0,0,0,0
# bgclr,ag    = np.random.randint(0,254,size=LEN_DATASET),0
fontsizes   = 24
textxpos    = HEIGHT//10 
textypos    = WIDTH//10
i           = 0
txts        = random.choices(CHARS,k=LEN_DATASET)
y           = np.empty(LEN_DATASET,dtype=object)
X           = np.ones((LEN_DATASET,HEIGHT,WIDTH,CHANNELS), np.uint8)



def generate_random_image():
    blank_image = X[i]*255
    fontpath    = fontpaths[i]
    b,g,r       = bs,gs,rs
    font        = ImageFont.truetype(fontpath, fontsizes)
    img_pil     = Image.fromarray(blank_image)
    draw        = ImageDraw.Draw(img_pil)

    text        = txts[i]


    w,h = draw.textsize(text, font=font)
    # w0,h0,w1,h1 = draw.textbbox((0,0),text,anchor='lt')
    # print(w,h)
    draw.text((0, 0),text  ,spacing=0, font = font, fill = (b, g, r, a))
    for t, char in enumerate(text):
        right, bottom = font.getsize(text)
        width, height = font.getmask(char).size
        right += 0
        bottom += 0
        top = bottom - height
        left = right - width

        # draw.rectangle((left, top, right, bottom), None, "#f00")
    # cv2.imshow("res1",np.array(img_pil))
    # draw.rectangle([(0, 0),(w, h)], outline ="red")

    img_pil     = img_pil.crop((left, top, right, bottom))  
    img_pil     = img_pil.resize((HEIGHT, WIDTH) )
    img         = np.array(img_pil)
    # print(text)
    X[i]        = img
    y[i]        = text
    # X.append(img)
    # y.append(text)
    if i%100==0:
        print(i,"completed")
    
    if DISPLAY:
        cv2.imshow("res",img)
        cv2.waitKey()
        cv2.imwrite(".\\dataset\\"+str(i)+".png", img)
        cv2.destroyAllWindows()
for i in range(LEN_DATASET):
    generate_random_image()

if not DISPLAY:
    np.savez_compressed('dataset\\X_char',X)
    np.savez_compressed('dataset\\y_char',y)
# print(X)
# print(y)

