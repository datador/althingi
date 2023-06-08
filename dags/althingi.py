from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

from src.download.get_videos import download_meetings
from src.transform.to_audio import get_audio
from src.processing.processing import process_video
from src.processing.process_audio import process_raw_audio
from src.processing.process_audio import label_processed_audio
from src.google.gcs import AudioProcessor


import numpy as np

project_dir = '/data/' # change to 'mnt/myssd/' when running on raspberry

def download_videos():
    download_meetings(first_meeting=110, max_downloads='all', max_retries=20, logging=True)

def transform_to_audio():
    get_audio(video_dir=project_dir+'videos', audio_dir=project_dir+'audio/raw', video_format='.mp4', audio_format='.wav')

def process_videos():
    process_video(video_dir='videos', log_dir='logs', 
                  lower_yellow=np.array([29, 100, 100]), 
                  upper_yellow=np.array([33, 255, 255]), 
                  lower_white=np.array([240]),
                  upper_white=np.array([255]),
                  custom_config=r'--oem 3 --psm 6 -l isl',
                  frame_skip=500)

def process_audio():
    process_raw_audio()

def label_audio():
    label_processed_audio()

def upload_gcs():
    gcs_processor = AudioProcessor('SA/sa-althingi.json', 'althingi-audio-bucket')
    gcs_processor.upload_files_to_bucket(project_dir + 'audio/labeled/20230601T132241-althingi-115')

def transcribe_gcs():
    gcs_processor = AudioProcessor(project_dir+'SA/sa-althingi.json', 'althingi-audio-bucket')
    gcs_processor.transcribe_audio_files(
        '20230601T132241-althingi-115',
        project_dir+'text/labeled/20230601T132241-althingi-115',
        'V1',
        max_transcriptions=1
    )

default_args = {
    'start_date': datetime(2023, 6, 1),
}

dag = DAG(
    'video_processing_dag',
    default_args=default_args,
    description='DAG for processing videos',
    schedule_interval='@once',
)

t1 = PythonOperator(
    task_id='download_videos',
    python_callable=download_videos,
    dag=dag,
)

t2 = PythonOperator(
    task_id='transform_to_audio',
    python_callable=transform_to_audio,
    dag=dag,
)

t3 = PythonOperator(
    task_id='process_videos',
    python_callable=process_videos,
    dag=dag,
)

t4 = PythonOperator(
    task_id='process_audio',
    python_callable=process_audio,
    dag=dag,
)

t5 = PythonOperator(
    task_id='label_audio',
    python_callable=label_audio,
    dag=dag,
)

t6 = PythonOperator(
    task_id='process_gcs',
    python_callable=upload_gcs,
    dag=dag,
)

t7 = PythonOperator(
    task_id='process_gcs',
    python_callable=transcribe_gcs,
    dag=dag,
)

t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7
