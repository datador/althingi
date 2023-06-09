FROM apache/airflow:2.6.1

USER root

RUN apt-get update && apt-get install -y \
    gcc \
    tesseract-ocr \
    libtesseract-dev \
    ffmpeg \ 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# download isl.traineddata
RUN mkdir -p /usr/share/tesseract-ocr/4.00/tessdata && \
    curl -L -o /usr/share/tesseract-ocr/4.00/tessdata/isl.traineddata https://github.com/tesseract-ocr/tessdata/blob/main/isl.traineddata

# Set the ownership and permissions for the data directory
RUN chown -R airflow:airflow /home/althingi/althingi/data && \
    chmod -R 777 /home/althingi/althingi/data

ENV PYTHONPATH=/opt/airflow/src

USER airflow

COPY requirements.txt .
COPY setup.py .
#COPY . .
COPY src /opt/airflow/src 

RUN ls -la
RUN pip install .
RUN pip install --no-cache-dir -r requirements.txt

COPY dags/ /opt/airflow/dags/









