import logging
import os
import time
from datetime import datetime
import numpy as np
from logging.handlers import RotatingFileHandler
import cv2
from src.processing.processing import process_frame, similarity_score, frame_to_time

def process_video(video_dir='videos', log_dir='logs/processing', 
                  lower_yellow=np.array([29, 100, 100]), 
                  upper_yellow=np.array([35, 255, 255]), 
                  custom_config=r'--oem 3 --psm 6 -l isl',
                  frame_skip=500):
    """
    Processes a video and extracts the topics discussed in it.

    Args:
    video_path (str): The path to the video file.
    logs_path (str): The path where the logs will be saved.
    frames_path (str): The path where the processed and original frames will be saved.
    lower_yellow (numpy.ndarray): The lower color range for yellow.
    upper_yellow (numpy.ndarray): The upper color range for yellow.
    custom_config (str): The custom configuration for Tesseract OCR.
    frame_skip (int): The number of frames to skip between processing.

    Returns:
    None
    """

    video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]

    for video_file in video_files:
        video_file_name = video_file.split('.')[0]
        topic_dir = os.path.join(log_dir, 'topic', video_file_name)
        processing_dir = os.path.join(log_dir, 'processing', video_file_name)
        frames_dir = os.path.join(log_dir, 'frames', video_file_name)

        # Create necessary directories if they don't exist
        os.makedirs(topic_dir, exist_ok=True)
        os.makedirs(processing_dir, exist_ok=True)
        os.makedirs(frames_dir, exist_ok=True)

        if os.path.exists(os.path.join(topic_dir, f'{video_file_name}.txt')):
            print(f"Skipping {video_file}, already processed.")
            continue

        print(f"Going over topics for {video_file}:")
        cap = cv2.VideoCapture(os.path.join(video_dir, video_file))
        processing_logged = False
        current_frame = 4000
        current_topic = ""

        with open(os.path.join(topic_dir, f'{video_file_name}.txt'), 'a') as topic_file:
            while cap.isOpened():
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                ret, frame = cap.read()

                if ret:
                    extracted_text, gray = process_frame(frame, lower_yellow, upper_yellow, custom_config)
                    similarity = similarity_score(current_topic, extracted_text)

                    if 7 < len(extracted_text) < 150 and similarity < 0.7:
                        if current_topic:
                            topic_end_time = frame_to_time(current_frame, 25)
                            topic_file.write(f'End: {topic_end_time}\n')

                        current_topic = extracted_text

                        topic_start_time = frame_to_time(current_frame, 25)
                        topic_file.write(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                        topic_file.write(f'Similarity score: {similarity}\n')
                        topic_file.write(f'Video file: {video_file_name}\n')
                        topic_file.write(f'Topic: {current_topic}\n')
                        topic_file.write(f'Start: {topic_start_time}\n')

                        cv2.imwrite(os.path.join(frames_dir, f'original_frame_{current_frame}.png'), frame)
                        cv2.imwrite(os.path.join(frames_dir, f'processed_frame_{current_frame}.png'), gray)

                        print(f"New topic '{current_topic}' starts at frame {current_frame}")

                else:
                    print(f"Frame {current_frame} not read correctly.")
                    break

                current_frame += frame_skip

        cap.release()