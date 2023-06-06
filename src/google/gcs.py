import os
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud import speech_v1p1beta1 as speech
from typing import Optional

class AudioProcessor:
    """
    This class provides functionality to handle audio files stored on Google Cloud Storage. 
    Current operations include uploading audio files and transcribing them using Google Speech-to-Text.
    """
    def __init__(self, client_file: str, bucket_name: str):
        """
        Initialize the Transcriber with authentication credentials and the name of the bucket where audio files are stored.

        Args:
            client_file (str): The path to the service account json file for authentication.
            bucket_name (str): The name of the Google Cloud Storage bucket where audio files are stored.
        """
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = client_file
        credentials = service_account.Credentials.from_service_account_file(client_file)
        self.storage_client = storage.Client()
        self.client = speech.SpeechClient(credentials=credentials)
        self.bucket = self.storage_client.get_bucket(bucket_name)

    def upload_files_to_bucket(self, folder_path: str):
        """
        Uploads all .wav files from a local directory to the Google Cloud Storage bucket.

        Args:
            folder_path (str): The local path to the folder containing the .wav files to be uploaded.
        """
        prefix = os.path.basename(folder_path)

        # Find all .wav files in the folder tree, excluding those in 'unlabeled' directories
        for root, dirs, files in os.walk(folder_path):
            if 'unlabeled' not in root:  # exclude 'unlabeled' directories
                for file in files:
                    if file.endswith('.wav'):
                        file_path = os.path.join(root, file)
                        blob_name = os.path.relpath(file_path, folder_path)  # Get the relative path to use as blob name
                        blob_name = f"{prefix}/{blob_name}"  # Prepend the prefix
                        blob_name = blob_name.replace('\\', '/')  # Replace backslashes with forward slashes
                        blob = self.bucket.blob(blob_name)
                        blob.upload_from_filename(file_path)
                        print(f"File {file_path} uploaded to {self.bucket.name}/{blob_name}.")

    def transcribe_audio_files(self, prefix: str, text_folder_path: str, api_version: str, max_transcriptions: Optional[int] = None):
        """
        Transcribes audio files stored on Google Cloud Storage.

        Args:
            prefix (str): The prefix to filter audio files in the bucket.
            text_folder_path (str): The local path where the transcriptions will be saved.
            api_version (str): The version of the Google Speech-to-Text API to use ('V1' or 'V2').
            max_transcriptions (int, optional): The maximum number of transcriptions to create. If None, all audio files will be transcribed.
        """
        text_folder_path = os.path.join(text_folder_path, api_version)
        blobs = self.bucket.list_blobs(prefix=prefix)
        transcribed_count = 0

        for blob in blobs:
            if blob.name.endswith('.wav'):
                gcs_uri = f'gs://{self.bucket.name}/{blob.name}'
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=44100,
                    language_code='is-IS',
                    model='default'
                )

                # Construct the output file path
                output_file_path = blob.name.replace('.wav', '.txt').replace(prefix, text_folder_path)
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                # Check if the output file already exists, skip this blob if it does
                if os.path.isfile(output_file_path):
                    print(f"File {output_file_path} already exists, skipping...")
                    continue

                audio = speech.RecognitionAudio(uri=gcs_uri)
                operation = self.client.long_running_recognize(config=config, audio=audio)
                print(f"Waiting for operation: \n {output_file_path}\nto complete...")
                response = operation.result(timeout=60*20)

                with open(output_file_path, 'w') as f:
                    for result in response.results:
                        # Write each transcription to the file
                        f.write(result.alternatives[0].transcript + '\n')

                transcribed_count += 1   # Increment the count here

                if max_transcriptions and transcribed_count >= max_transcriptions:
                    break
