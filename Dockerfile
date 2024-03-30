FROM python:3.9-slim-buster

RUN apt-get update && \
    apt-get -qq -y install tesseract-ocr && \
    apt-get -qq -y install libtesseract-dev
RUN  apt-get install libgl1-mesa-glx

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "--worker-class=gevent", "--worker-connections=1000" ,"--workers=3" ,"app:app"]
