from difflib import SequenceMatcher
import cv2
import pytesseract
import os
import numpy as np
from datetime import datetime
from src.processing.logging import setup_logger


class FrameProcessor:
    """
    A class used to process frames in a video.

    ...

    Attributes
    ----------
    lower_yellow : np.ndarray
        lower color range for yellow in HSV color space
    upper_yellow : np.ndarray
        upper color range for yellow in HSV color space
    lower_white : np.ndarray
        lower color range for white in HSV color space
    upper_white : np.ndarray
        upper color range for white in HSV color space
    custom_config : str
        the custom configuration for Tesseract OCR

    Methods
    -------
    process_yellow_frame(frame):
        Processes a frame and extracts yellow text from it.
    process_white_frame(frame):
        Processes a frame and extracts white text from it.
    """

    def __init__(self, lower_yellow, upper_yellow, lower_white, upper_white, custom_config):
        """
        Constructs all the necessary attributes for the FrameProcessor object.

        Parameters
        ----------
        lower_yellow : np.ndarray
            lower color range for yellow in HSV color space
        upper_yellow : np.ndarray
            upper color range for yellow in HSV color space
        lower_white : np.ndarray
            lower color range for white in HSV color space
        upper_white : np.ndarray
            upper color range for white in HSV color space
        custom_config : str
            the custom configuration for Tesseract OCR
        """
        self.lower_yellow = lower_yellow
        self.upper_yellow = upper_yellow
        self.lower_white = lower_white
        self.upper_white = upper_white
        self.custom_config = custom_config
        self.crop_coords_yellow = [700, 1000, 150, 1600]  # add this line
        self.crop_coords_white = [800, 1000, 150, 1700]  # add this line

    def process_yellow_frame(self, frame):
        """
        Process a frame of a video.

        Args:
        frame (numpy.ndarray): A frame from a video.

        Returns:
        str: The processed frame.
        """
        # Convert BGR to HSV
        cropped_frame = frame[self.crop_coords_yellow[0]:self.crop_coords_yellow[1], self.crop_coords_yellow[2]:self.crop_coords_yellow[3]]
        hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
        # Threshold the HSV image to get only the specified colors
        mask = cv2.inRange(hsv, self.lower_yellow, self.upper_yellow)
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(cropped_frame, cropped_frame, mask=mask)

        # Convert the result to grayscale
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

        # Use Tesseract to do OCR on the processed image
        text = pytesseract.image_to_string(gray, config=self.custom_config)

        return text, gray


    def process_white_frame(self, frame):
        """
        Process a frame of a video.

        Args:
        frame (numpy.ndarray): A frame from a video.

        Returns:
        str: The processed frame.
        """
        # Convert BGR to HSV
        cropped_frame = frame[self.crop_coords_white[0]:self.crop_coords_white[1], self.crop_coords_white[2]:self.crop_coords_white[3]]
   
        hsv_white = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
        # Threshold the HSV image to get only the specified colors
        mask = cv2.inRange(hsv_white, self.lower_white, self.upper_white)
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(cropped_frame, cropped_frame, mask=mask)

        # Convert the result to grayscale
        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

        # Use adaptive thresholding to convert the image to binary
    #    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Use Tesseract to do OCR on the processed image
    #    text = pytesseract.image_to_string(thresh, config=self.custom_config)

        text = pytesseract.image_to_string(gray, config=self.custom_config)

        return text, gray

    
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
                  upper_yellow=np.array([33, 255, 255]), 
                  lower_white=np.array([232]),
                  upper_white=np.array([255]),
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
        frame_processor = FrameProcessor(lower_yellow, upper_yellow, lower_white, upper_white, custom_config)

        with open(os.path.join(topic_dir, f'{video_file_name}.txt'), 'a') as topic_file:
            while cap.isOpened():
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                ret, frame = cap.read()

                if ret:
                    extracted_text_yellow, gray_yellow = frame_processor.process_yellow_frame(frame)
                    similarity = similarity_score(current_topic, extracted_text_yellow)

                    if 7 < len(extracted_text_yellow) < 150 and similarity < 0.7:
                        extracted_text_white, gray_white = frame_processor.process_white_frame(frame)
                        
                        if current_topic:
                            topic_end_time = frame_to_time(current_frame, 25)
                            topic_file.write(f'End: {topic_end_time}\n')

                        current_topic = extracted_text_yellow


                        topic_start_time = frame_to_time(current_frame, 25)
                        topic_file.write(f'\nTimestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')                   
                        topic_file.write(f'Similarity score: {similarity}\n')
                        topic_file.write(f'Video file: {video_file_name}\n')
                        topic_file.write(f'Start: {topic_start_time}\n')    
                        topic_file.write(f'Frame: {current_frame}\n')                             
                        topic_file.write(f'Speaker: {current_topic}')
                        topic_file.write(f'Topic: {extracted_text_white}\n')                     


                        cv2.imwrite(os.path.join(frames_dir, f'original_frame_{current_frame}.png'), frame)
                        cv2.imwrite(os.path.join(frames_dir, f'processed_yellow_frame_{current_frame}.png'), gray_yellow)
                        cv2.imwrite(os.path.join(frames_dir, f'processed_white_frame_{current_frame}.png'), gray_white)

                        print(f"New Speaker: '{current_topic}\nTopic: {extracted_text_white}' starts at frame {current_frame}")


                else:
                    print(f"Frame {current_frame} not read correctly.")
                    break

                current_frame += frame_skip

        cap.release()
