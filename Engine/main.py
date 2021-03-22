import os
import re
import sys
import time

import pyaudio
import wave
import unicodedata
import hashlib
import dotenv
import azure.cognitiveservices.speech as speechsdk
import cli_ui
import traceback

sys.path.append('../')

# noinspection PyUnresolvedReferences
from AnswerGeneration.main import generate_answer

dotenv.load_dotenv()
AZURE_KEY = os.getenv('AZURE_KEY')
AZURE_REGION = os.getenv('AZURE_REGION')

speech_config = speechsdk.SpeechConfig(subscription=AZURE_KEY, region=AZURE_REGION)
speech_config.speech_synthesis_voice_name = 'en-US-BenjaminRUS'

speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=speechsdk.AudioConfig(use_default_microphone=True), language="en-GB")
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

pa = pyaudio.PyAudio()


def slugify(value, allow_unicode=False):
    value = str(value)

    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')

    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def get_wav_path(text: str) -> str:
    return f"../data/Wojtek/{slugify(text)}.{hashlib.sha1(text.encode('utf-8')).hexdigest()[:4]}.wav"


def mic_to_text() -> str:
    result_text = None

    def cb_recognized(evt: speechsdk.SpeechRecognitionEventArgs):
        nonlocal result_text
        if not result_text and len(evt.result.text) > 0:
            result_text = evt.result.text

    speech_recognizer.recognized.connect(cb_recognized)
    speech_recognizer.start_continuous_recognition()
    cli_ui.info_1('Listening...')

    try:
        while not result_text:
            time.sleep(0.05)
    except (Exception, KeyboardInterrupt) as ex:
        speech_recognizer.stop_continuous_recognition()
        raise ex

    speech_recognizer.stop_continuous_recognition()

    assert isinstance(result_text, str)
    return result_text


def text_to_wav(text: str, path: str) -> bool:
    if os.path.exists(path):
        print_function_result('text_to_wav', [text], "cached")
        return True

    result = speech_synthesizer.speak_text(text)

    if len(result.audio_data) < 1:
        print_function_result('text_to_wav', [text], result.reason)
        return False

    stream = speechsdk.AudioDataStream(result)
    stream.save_to_wav_file(path)
    print_function_result('text_to_wav', [text], result.reason)
    return True


def play_wav(path: str) -> None:
    if not os.path.exists(path):
        print_function_result("play_wav", [path], "not_found")
        return

    with wave.open(path, 'r') as f:
        audio_rate = f.getframerate()
        audio_buffer_size = int(audio_rate / 10)

        stream = pa.open(
            rate=audio_rate,
            channels=f.getnchannels(),
            format=pa.get_format_from_width(f.getsampwidth()),
            frames_per_buffer=audio_buffer_size,
            output=True,
        )

        while True:
            buffer = f.readframes(audio_buffer_size)

            if len(buffer) == 0:
                break

            stream.write(buffer)

        stream.close()
        print_function_result("play_wav", [path], "success")


def print_function_result(fn_name: str, fn_params: any, fn_result: any) -> None:
    if not isinstance(fn_params, list):
        fn_params = [fn_params]

    cli_ui.info('Executed function:', cli_ui.yellow, fn_name)
    cli_ui.info_2('Params:', f'; '.join(fn_params))
    cli_ui.info_2('Return:', cli_ui.bold, fn_result)


def process_question(question: str) -> None:
    cli_ui.info_1('[⏱️]', 'Processing question:', cli_ui.standout, question)

    answer = generate_answer(question)
    answer_path = get_wav_path(answer)

    cli_ui.info_1('[✅]', 'Generated answer:', cli_ui.standout, cli_ui.bold, cli_ui.green, answer)

    if text_to_wav(answer, answer_path):
        play_wav(answer_path)


def mode_manual_input() -> None:
    try:
        while True:
            question = cli_ui.ask_string('Enter your question:')
            process_question(question)
    except KeyboardInterrupt:
        pass


def mode_mic_input() -> None:
    try:
        while True:
            question = mic_to_text()
            process_question(question)
    except KeyboardInterrupt:
        pass


def mode_exit() -> None:
    exit(0)


if __name__ == '__main__':
    mode_dict = {
        'manual_input': mode_manual_input,
        'mic_input': mode_mic_input,
        'exit': mode_exit,
    }
    mode_keys = [*mode_dict.keys()]

    while True:
        try:
            mode_key = cli_ui.ask_choice('Select application mode', choices=mode_keys)
            mode_dict[mode_key]()
        except (Exception, KeyboardInterrupt):
            try:
                traceback.print_exc()
            except:
                pass
