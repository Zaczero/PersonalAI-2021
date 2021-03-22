import pyaudio
import wave
import unicodedata
import re
import hashlib
import os
import keyboard
import time
from zipfile import ZipFile

p = pyaudio.PyAudio()

AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RATE = 44100
AUDIO_CHUNKS_PER_SECOND = 10
AUDIO_CHUNK_SIZE = int(AUDIO_RATE / AUDIO_CHUNKS_PER_SECOND)
AUDIO_SAMPLE_SIZE = p.get_sample_size(AUDIO_FORMAT)


def slugify(value, allow_unicode=False):
    value = str(value)

    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')

    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def read_qa(collection_name):
    with open("../data/QA.txt") as f:
        text_raw = f.read().splitlines()

    text_valid_lines = text_raw[0::3] + text_raw[1::3]

    return {
        text_line: f"../data/{collection_name}/{slugify(text_line)}.{hashlib.sha1(text_line.encode('utf-8')).hexdigest()[:4]}.wav"
        for text_line in text_valid_lines
    }


def run_record_session(text, path):
    print()
    print('RECORD:', text)
    print()

    print('Hold SHIFT to record audio')

    while not keyboard.is_pressed('shift'):
        time.sleep(0.02)

    frames = []
    stream = p.open(format=AUDIO_FORMAT,
                    channels=AUDIO_CHANNELS,
                    rate=AUDIO_RATE,
                    frames_per_buffer=AUDIO_CHUNK_SIZE,
                    input=True)

    print('Recording...')

    while keyboard.is_pressed('shift'):
        frames.append(stream.read(AUDIO_CHUNK_SIZE))

    stream.stop_stream()
    stream.close()

    print('Recording stopped')
    print('Recording duration:', len(frames) / AUDIO_CHUNKS_PER_SECOND, 'seconds')

    with wave.open(path, 'wb') as wf:
        wf.setnchannels(AUDIO_CHANNELS)
        wf.setframerate(AUDIO_RATE)
        wf.setsampwidth(AUDIO_SAMPLE_SIZE)
        wf.writeframes(b''.join(frames))

    print('Saved recording to file:', path)


def pack_files(collection_name, text_path_dict):
    with ZipFile(f'../data/{collection_name}.zip', 'w') as f:
        for i, (text, path) in enumerate(text_path_dict.items()):
            if not os.path.exists(path):
                raise FileNotFoundError()
            f.write(path, f'{i:04d}.wav')

    with open(f'../data/{collection_name}.txt', 'w') as f:
        for i, (text, path) in enumerate(text_path_dict.items()):
            f.write(f'{i:04d}\t{text}\n')


name = input("Enter your name: ")

text_path_dict = read_qa(name)
directory_path = os.path.dirname(next(iter(text_path_dict.values())))

if not os.path.exists(directory_path):
    os.mkdir(directory_path)


for text, path in text_path_dict.items():
    if not os.path.exists(path):
            run_record_session(text, path)


# pack_files(name, text_path_dict)
