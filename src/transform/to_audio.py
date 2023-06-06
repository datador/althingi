import os
from moviepy.editor import AudioFileClip
from pydub import AudioSegment

def get_audio(video_dir='videos', audio_dir='audio/raw', video_format='.mp4', audio_format='.wav'):
    # Ensure audio directory exists
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    # Get a list of all .mp4 files in the videos directory
    video_files = [f for f in os.listdir(video_dir) if f.endswith(video_format)]

    # Loop through all .mp4 files
    for video_file in video_files:
        video_path = os.path.join(video_dir, video_file)
        audio_path = os.path.join(audio_dir, video_file.replace(video_format, audio_format))

        # Check if the audio file already exists. If it does, skip this video file.
        if os.path.isfile(audio_path):
            print(f"Audio file for {video_file} already exists. Skipping...")
            continue

        # Extract audio
        audio = AudioFileClip(video_path)
        audio_path_temp = audio_path.replace(audio_format, '_temp' + audio_format)
        audio.write_audiofile(audio_path_temp)

        audio_mono = AudioSegment.from_wav(audio_path_temp)

        if audio_mono.sample_width != 2:
            audio_mono = audio_mono.set_sample_width(2)

        # Ensure an even number of frames
        if len(audio_mono) % 2 != 0:
            audio_mono = audio_mono[:-1]

        audio_mono = audio_mono.set_channels(1)

        # Save mono audio
        audio_mono.export(audio_path, format='wav')

        # Delete temporary stereo file
        os.remove(audio_path_temp)

