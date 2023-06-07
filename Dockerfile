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

USER airflow

COPY . /app
WORKDIR /app

#COPY requirements.txt .

RUN ls -la
RUN pip install .
RUN pip install --no-cache-dir -r requirements.txt


COPY src/ /src/
COPY dags/ /opt/airflow/dags/









