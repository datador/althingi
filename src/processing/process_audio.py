import os
import re
import shutil
import json
from typing import Optional
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from pydub import AudioSegment


def process_map_audio_files(raw_dir: Optional[str] = 'audio/raw',
                        processed_dir: Optional[str] = 'audio/processed',
                        labeled_dir: Optional[str] = 'audio/labeled') -> None:
    """
    Processes raw audio files using a specified mapping and logs for further usage.

    Args:
        raw_dir (str, optional): Directory where raw audio files are located.
        processed_dir (str, optional): Directory to store processed audio files.
        labeled_dir (str, optional): Directory to store labeled audio files.

    Returns:
        None
    """

    # Create directory for processed audios if it does not exist
    os.makedirs(processed_dir, exist_ok=True)

    # Load party mapping from JSON file
    party_mapping_file = 'src/data/party_mapping.json'
    with open(party_mapping_file, 'r') as f:
        party_mapping = json.load(f)

    # Get the list of log directories in the topic logs directory
    log_dirs = os.listdir('logs/topic')

    for log_dir in log_dirs:
        log_dir_path = os.path.join('logs/topic', log_dir)

        # Ignore files, only process directories
        if not os.path.isdir(log_dir_path):
            continue

        video_file_name = log_dir

        # Path to the text file within the directory
        topic_file_path = os.path.join(log_dir_path, f'{video_file_name}.txt')

        with open(topic_file_path, 'r') as topic_file:
            lines = topic_file.readlines()
            topics = []
            start_times = []
            end_times = []
            for line in lines:
                line = line.strip()
                if line.startswith("Topic:"):
                    topic_name = line.split(":", 1)[1].strip()
                    if len(topic_name) > 7:  # Filter out topics with less than 7 characters
                        topics.append(topic_name)
                elif line.startswith("Start:"):
                    start_time = line.split(":", 1)[1].strip()
                    start_times.append(int(start_time.split(':')[0]) * 60 + int(start_time.split(':')[1]))  # Convert time to seconds
                elif line.startswith("End:"):
                    end_time = line.split(":", 1)[1].strip()
                    end_times.append(int(end_time.split(':')[0]) * 60 + int(end_time.split(':')[1]))  # Convert time to seconds

        # Create a directory under processed for the current audio file
        processed_file_dir = os.path.join(processed_dir, video_file_name)
        os.makedirs(processed_file_dir, exist_ok=True)

        # Iterate over each identified topic
        for i in range(len(topics)):
            topic = topics[i]

            start_time = start_times[i]
            if i + 1 < len(end_times):
                end_time = end_times[i + 1] - 1
            else:
                end_time = None

            # Cut the segment from the original audio
            original_audio_path = os.path.join(raw_dir, f'{video_file_name}.wav')  # Replace with your original audio path

            if end_time is not None:
                duration = end_time - start_time
            else:
                end_time = start_time + 10  # Set a default duration of 10 seconds if no end frame is specified
                duration = None

            # Replace unwanted characters with hyphen
            sanitized_topic = re.sub(' ', '-', topic)
            sanitized_topic = re.sub('[^0-9a-zA-Z -]+', '', sanitized_topic)

            output_filename = f"{sanitized_topic}-{round((start_time / 60), 1)}-{round((end_time / 60), 1)}.wav"
            output_filepath = os.path.join(processed_file_dir, output_filename)

            ffmpeg_extract_subclip(original_audio_path, start_time, end_time, targetname=output_filepath)

        # Create a corresponding directory in labeled audios
        labeled_file_dir = os.path.join(labeled_dir, video_file_name)
        os.makedirs(labeled_file_dir, exist_ok=True)

        # Create subdirectories for each party under the labeled file directory
        for party_name in set(party_mapping.values()):
            party_dir = os.path.join(labeled_file_dir, party_name)
            os.makedirs(party_dir, exist_ok=True)

        # Add 'unlabeled' subdirectory as well
        unlabeled_dir = os.path.join(labeled_file_dir, 'unlabeled')
        os.makedirs(unlabeled_dir, exist_ok=True)

        # Copy files to their respective subdirectories based on pattern match
        for filename in os.listdir(processed_file_dir):
            filepath = os.path.join(processed_file_dir, filename)
            if os.path.isfile(filepath):
                labeled = False
                for party_names, subdirectory in party_mapping.items():
                    if re.search(re.escape(party_names), filename):
                        target_dir = os.path.join(labeled_file_dir, subdirectory)
                        shutil.copy(filepath, os.path.join(target_dir, filename))
                        labeled = True
                        break

                # If no match found in party names, copy to 'unlabeled'
                if not labeled:
                    shutil.copy(filepath, os.path.join(unlabeled_dir, filename))


if __name__ == "__main__":
    process_map_audio_files()


def process_raw_audio(raw_dir='audio/raw', processed_dir='audio/processed'):
    """
    Processes raw audio files by cutting them into segments based on start and end times specified in the text files
    found in the 'logs/topic' directory. The processed audio segments are then saved to the 'processed_dir' directory.

    Args:
        raw_dir (str): The directory where raw audio files are located. Default is 'audio/raw'.
        processed_dir (str): The directory where processed audio files will be saved. Default is 'audio/processed'.
    """
    # Create directory for processed audios if it does not exist
    os.makedirs(processed_dir, exist_ok=True)

    # Get the list of log directories in the topic logs directory
    log_dirs = os.listdir('logs/topic')

    for log_dir in log_dirs:
        log_dir_path = os.path.join('logs/topic', log_dir)

        # Ignore files, only process directories
        if not os.path.isdir(log_dir_path):
            continue

        video_file_name = log_dir

        # Path to the text file within the directory
        topic_file_path = os.path.join(log_dir_path, f'{video_file_name}.txt')

        with open(topic_file_path, 'r') as topic_file:
            lines = topic_file.readlines()
            topics = []
            start_times = []
            end_times = []
            for line in lines:
                line = line.strip()
                if line.startswith("Speaker:"): # Topic changed to -> Speaker
                    topic_name = line.split(":", 1)[1].strip()
                    if len(topic_name) > 7:  # Filter out topics with less than 7 characters
                        topics.append(topic_name)
                elif line.startswith("Start:"):
                    start_time = line.split(":", 1)[1].strip()
                    start_times.append(int(start_time.split(':')[0]) * 60 + int(start_time.split(':')[1]))  # Convert time to seconds
                elif line.startswith("End:"):
                    end_time = line.split(":", 1)[1].strip()
                    end_times.append(int(end_time.split(':')[0]) * 60 + int(end_time.split(':')[1]))  # Convert time to seconds

        # Create a directory under processed for the current audio file
        processed_file_dir = os.path.join(processed_dir, video_file_name)
        os.makedirs(processed_file_dir, exist_ok=True)

        # Iterate over each identified topic
        for i in range(len(topics)):
            topic = topics[i]
            start_time = start_times[i]
            if i + 1 < len(end_times):
                end_time = end_times[i + 1] - 1
            else:
                end_time = None

            # Cut the segment from the original audio
            original_audio_path = os.path.join(raw_dir, f'{video_file_name}.wav')  # Replace with your original audio path

            if end_time is not None:
                duration = end_time - start_time
            else:
                end_time = start_time + 10  # Set a default duration of 10 seconds if no end frame is specified
                duration = None
                
            # Sanitize the name    
            sanitized_topic = re.sub(' ', '-', topic)
            sanitized_topic = re.sub('[^0-9a-zA-Z-ÁáÉéÍíÓóÚúÝýÐðÞþÆæÖö]+', '', sanitized_topic)


            output_filename = f"{sanitized_topic}-{round((start_time / 60), 1)}-{round((end_time / 60), 1)}.wav"
            output_filepath = os.path.join(processed_file_dir, output_filename)

            # Skip if the file has already been processed
            if not os.path.exists(output_filepath):
                ffmpeg_extract_subclip(original_audio_path, start_time, end_time, targetname=output_filepath)

import os
import shutil

def label_processed_audio(processed_dir='audio/processed', labeled_dir='audio/labeled'):
    """
    Takes processed audio files and maps them to the 'labeled_dir' directory based on the party mapping file.

    Args:
        processed_dir (str): The directory where processed audio files are located. Default is 'audio/processed'.
        labeled_dir (str): The directory where labeled audio files will be saved. Default is 'audio/labeled'.
    """
    # Load party mapping from JSON file
    party_mapping_file = 'src/data/party_mapping.json'
    with open(party_mapping_file, 'r') as f:
        party_mapping = json.load(f)

    # Get the list of processed directories in the processed directory
    processed_dirs = os.listdir(processed_dir)

    for dir_name in processed_dirs:
        processed_dir_path = os.path.join(processed_dir, dir_name)

        # Ignore files, only process directories
        if not os.path.isdir(processed_dir_path):
            continue

        # Check if the directory already exists in labeled_dir
        labeled_dir_path = os.path.join(labeled_dir, dir_name)
        if os.path.exists(labeled_dir_path):
            continue

        # Create a corresponding directory in labeled audios
        os.makedirs(labeled_dir_path, exist_ok=True)

        # Create subdirectories for each party under the labeled file directory
        for party_name in set(party_mapping.values()):
            party_dir = os.path.join(labeled_dir_path, party_name)
            os.makedirs(party_dir, exist_ok=True)

        # Add 'unlabeled' subdirectory as well
        unlabeled_dir = os.path.join(labeled_dir_path, 'unlabeled')
        os.makedirs(unlabeled_dir, exist_ok=True)

        # Copy files to their respective subdirectories based on pattern match
        for filename in os.listdir(processed_dir_path):
            filepath = os.path.join(processed_dir_path, filename)
            if os.path.isfile(filepath):
                labeled = False
                for party_names, subdirectory in party_mapping.items():
                    match = re.search(re.escape(party_names), filename)
                    if match:
                        target_dir = os.path.join(labeled_dir_path, subdirectory)
                        shutil.copy(filepath, os.path.join(target_dir, filename))
                        labeled = True
                        break

                # If no match found in party names, copy to 'unlabeled'
                if not labeled:
                    shutil.copy(filepath, os.path.join(unlabeled_dir, filename))


def copy_short_audio(labeled_dir='audio/labeled', short_dir='audio/short'):
    """
    Copies audio files from the 'labeled_dir' directory to the 'short_dir' directory, splitting them into segments
    that are below 60 seconds.

    Args:
        labeled_dir (str): The directory where labeled audio files are located. Default is 'audio/labeled'.
        short_dir (str): The directory where short audio files will be saved. Default is 'audio/short'.
    """
    # Create directory for short audios if it does not exist
    os.makedirs(short_dir, exist_ok=True)

    # Get the list of labeled directories in the labeled directory
    labeled_dirs = os.listdir(labeled_dir)

    for labeled_dir_name in labeled_dirs:
        labeled_dir_path = os.path.join(labeled_dir, labeled_dir_name)

        # Ignore files, only process directories
        if not os.path.isdir(labeled_dir_path):
            continue

        processed_dir_path = os.path.join('audio/processed', labeled_dir_name)
        if not os.path.isdir(processed_dir_path):
            continue

        short_file_dir = os.path.join(short_dir, labeled_dir_name)
        os.makedirs(short_file_dir, exist_ok=True)

        # Get the list of party directories within the labeled directory
        party_dirs = os.listdir(labeled_dir_path)

        for party_dir_name in party_dirs:
            party_dir_path = os.path.join(labeled_dir_path, party_dir_name)

            # Ignore files, only process subdirectories
            if not os.path.isdir(party_dir_path):
                continue

            short_party_dir = os.path.join(short_file_dir, party_dir_name)
            os.makedirs(short_party_dir, exist_ok=True)

            # Copy files and split into segments below 60 seconds
            for filename in os.listdir(party_dir_path):
                labeled_filepath = os.path.join(party_dir_path, filename)
                if os.path.isfile(labeled_filepath):
                    short_filepath = os.path.join(short_party_dir, filename)

                    audio = AudioSegment.from_file(labeled_filepath)
                    duration = len(audio) / 1000  # Duration in seconds

                    if duration <= 59.5:
                        shutil.copy(labeled_filepath, short_filepath)
                    else:
                        num_splits = int(duration / 59.5)  # Number of splits required
                        segment_duration = duration / num_splits  # Duration of each segment

                        for i in range(num_splits):
                            start_time = i * segment_duration * 1000  # Start time in milliseconds
                            end_time = (i + 1) * segment_duration * 1000  # End time in milliseconds
                            segment = audio[int(start_time):int(end_time)]
                            split_filename = os.path.splitext(filename)[0] + f"_{i+1}" + os.path.splitext(filename)[1]
                            split_filepath = os.path.join(short_party_dir, split_filename)
                            segment.export(split_filepath, format='wav')
