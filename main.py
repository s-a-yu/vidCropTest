import json
import subprocess
import os

# Load insights JSON data
with open('/Users/steph/PycharmProjects/videoCropTest/insights.json') as f:
    insights = json.load(f)

# Function to generate FFMPEG crop command
def generate_crop_command(input_file, output_file, x, y, width, height, start_time, duration):
    # Calculate crop size to fit within the input video dimensions
    input_width = 640
    input_height = 360
    crop_width = min(width, input_width - x)
    crop_height = min(height, input_height - y)

    return [
        'ffmpeg',
        '-i', input_file,
        '-vf', f'crop={crop_width}:{crop_height}:{x}:{y},scale=1080:1920',  # Crop and scale to iPhone screen dimensions
        '-ss', start_time,
        '-t', duration,
        '-c:v', 'libx264',  # Use H.264 codec for video
        '-c:a', 'aac',  # Use AAC codec for audio
        '-b:v', '2M',  # Set video bitrate
        '-b:a', '128k',  # Set audio bitrate
        '-pix_fmt', 'yuv420p',  # Ensure compatibility with QuickTime
        '-movflags', '+faststart',  # Enable progressive download
        output_file
    ]

# Define input and output files
input_file = '/Users/steph/PycharmProjects/videoCropTest/inputvid.mp4'
output_file_prefix = 'output_clip'
final_output_file = 'final_output.mp4'
final_cropped_output_file = 'final_output_cropped.mp4'

# Extract relevant segments and crop parameters
commands = []
segment_index = 1
clip_files = []

for video in insights['videos']:
    for person in video['insights']['namedPeople']:
        for instance in person['instances']:
            start_time = instance['start']
            end_time = instance['end']
            start_time_seconds = int(start_time.split(":")[1]) * 60 + float(start_time.split(":")[2])
            end_time_seconds = int(end_time.split(":")[1]) * 60 + float(end_time.split(":")[2])
            duration_seconds = end_time_seconds - start_time_seconds
            duration = f"00:00:{duration_seconds:05.2f}"

            # Set default crop parameters, adjust as needed
            x = 0
            y = 0
            width = 640  # Input video width
            height = 360  # Input video height

            output_file = f"{output_file_prefix}_{segment_index}.mp4"
            clip_files.append(output_file)
            segment_index += 1
            commands.append(generate_crop_command(input_file, output_file, x, y, width, height, start_time, duration))

# Execute FFMPEG commands to create individual clips
for command in commands:
    subprocess.run(command)

# Create a text file with the list of clips to concatenate
with open('clips_to_concat.txt', 'w') as f:
    for clip_file in clip_files:
        f.write(f"file '{clip_file}'\n")

# Concatenate the clips into a single output video
concat_command = [
    'ffmpeg',
    '-f', 'concat',
    '-safe', '0',
    '-i', 'clips_to_concat.txt',
    '-c', 'copy',
    final_output_file
]

subprocess.run(concat_command)

# Crop the final concatenated video to mobile phone ratio (9:16)
final_crop_command = [
    'ffmpeg',
    '-i', final_output_file,
    '-vf', 'scale=1080:1920,crop=1080:1920',
    '-c:v', 'libx264',
    '-c:a', 'aac',
    '-b:v', '2M',
    '-b:a', '128k',
    '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart',
    final_cropped_output_file
]

subprocess.run(final_crop_command)

# Clean up individual clip files and the text file
for clip_file in clip_files:
    os.remove(clip_file)
os.remove('clips_to_concat.txt')
os.remove(final_output_file)
