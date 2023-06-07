FROM apache/airflow:2.6.1

USER root

RUN apt-get update && apt-get install -y \
    gcc \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# download isl.traineddata
RUN mkdir -p /usr/share/tesseract-ocr/4.00/tessdata && \
    curl -L -o /usr/share/tesseract-ocr/4.00/tessdata/isl.traineddata https://github.com/tesseract-ocr/tessdata/blob/main/isl.traineddata


# Copy the necessary files for installation
COPY requirements.txt /requirements.txt
COPY setup.py /setup.py
COPY src/ /src/

USER airflow

RUN pip install --no-cache-dir -r /requirements.txt \
    && pip install .

COPY dags/ /opt/airflow/dags/