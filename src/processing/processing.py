from difflib import SequenceMatcher
import cv2
import pytesseract
import os
import numpy as np
from datetime import datetime
from src.processing.logging import setup_logger


class FrameProcessor:
    def __init__(self, lower_color, upper_color, custom_config, crop_coords):
        self.lower_color = lower_color
        self.upper_color = upper_color
        self.custom_config = custom_config
        self.crop_coords = crop_coords

    def process_frame(self, frame):
        # Crop the frame to the area where text usually appears
        cropped_frame = frame[self.crop_coords[0]:self.crop_coords[1], self.crop_coords[2]:self.crop_coords[3]]
        # Convert the cropped frame to HSV
        hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
        # Threshold the HSV image to get only the specified colors
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(cropped_frame, cropped_frame, mask=mask)
        # Convert to grayscale
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        # Extract text from the processed frame
        extracted_text = pytesseract.image_to_string(gray, config=self.custom_config)

        return extracted_text

def frame_to_time(frame_number, fps):
    """
    Converts a frame number to a time string.

    Args:
    frame_number (int): The frame number.
    fps (int): The frames per second.

    Returns:
    str: The time in the format 'minutes:seconds'.
    """
    total_seconds = frame_number / fps
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes}:{seconds:02d}"

def similarity_score(a, b):
    """
    Calculates and returns the similarity score between two strings.

    Args:
    a (str): The first string.
    b (str): The second string.

    Returns:
    float: The similarity score.
    """
    return SequenceMatcher(None, a, b).ratio()

def process_frame(frame, lower_yellow, upper_yellow, custom_config):
    """
    Processes a frame from a video and extracts text.

    Args:
    frame (numpy.ndarray): The frame to process.
    lower_yellow (numpy.ndarray): The lower color range for yellow.
    upper_yellow (numpy.ndarray): The upper color range for yellow.
    custom_config (str): The custom configuration for Tesseract OCR.

    Returns:
    str: The extracted text.
    """
    # Crop the frame to the area where text usually appears
    cropped_frame = frame[700:1000, 50:1600]
    # Convert the cropped frame to HSV
    hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image to get only yellow colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(cropped_frame, cropped_frame, mask=mask)
    # Convert to grayscale
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    # Extract text from the processed frame
    extracted_text = pytesseract.image_to_string(gray, config=custom_config)

    return extracted_text

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