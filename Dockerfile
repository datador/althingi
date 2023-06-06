FROM arm64v8/python:3.8-slim-buster

RUN apt-get update && apt-get install -y \
    gcc \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install apache-airflow

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# download isl.traineddata
RUN mkdir -p /usr/share/tesseract-ocr/4.00/tessdata && \
    wget -O /usr/share/tesseract-ocr/4.00/tessdata/isl.traineddata https://github.com/tesseract-ocr/tessdata/blob/main/isl.traineddata

COPY dags/ /root/airflow/dags/
COPY src/ /src/

USER root