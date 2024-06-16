import json
import subprocess

# Load insights JSON data
with open('/Users/steph/PycharmProjects/videoCropTest/insights.json') as f:
    insights = json.load(f)


# Function to generate FFMPEG crop command
def generate_crop_command(input_file, output_file, x, y, width, height, start_time, end_time):
    return [
        'ffmpeg',
        '-i', input_file,
        '-vf', f'crop={width}:{height}:{x}:{y}',
        '-ss', str(start_time),
        '-t', str(end_time),
        '-c:a', 'copy',
        output_file
    ]


# Define input and output files
input_file = '/Users/steph/PycharmProjects/videoCropTest/inputvid.mp4'
output_file = 'output_video.mp4'

# Extract relevant segments and crop parameters
commands = []
segment_index = 1
for video in insights['videos']:
    for ocr_entry in video['insights']['namedPeople']:
        x = ocr_entry['left']
        y = ocr_entry['top']
        width = ocr_entry['width']
        height = ocr_entry['height']

        for instance in ocr_entry['instances']:
            start_time = instance['start']
            end_time = instance['end']
            duration_seconds = (float(end_time.split(":")[2]) - float(start_time.split(":")[2]))
            duration = f"00:00:{duration_seconds:05.2f}"

            output_file = f"{output_file}_{segment_index}.mp4"
            segment_index += 1
            commands.append(generate_crop_command(input_file, output_file, x, y, width, height, start_time, duration))

# Execute FFMPEG commands
for command in commands:
    subprocess.run(command)
