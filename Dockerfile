FROM ubuntu:18.04
FROM python:3.7.0
LABEL maintainer="Your Name <youremailaddress@provider.com>"
RUN apt-get update -y 
RUN apt-get install -y tesseract-ocr-eng && apt-get install -y python3-pip python3-dev
RUN python3 -m pip install --upgrade pip
RUN apt install libgl1-mesa-glx -y
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY . /app
CMD [ "python", "./app.py" ]