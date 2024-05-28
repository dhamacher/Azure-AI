from dotenv import load_dotenv
from pathlib import Path
from core.const import LOGGER_NAME, KEY, REGION

import os
import azure.cognitiveservices.speech as speechsdk
import wave
import logging


logger = logging.getLogger(LOGGER_NAME)


def save_audio_file(filename, audio_data):
    try:
        with wave.open(filename, 'wb') as audio_file:
            audio_file.setnchannels(2)
            audio_file.setsampwidth(2)
            audio_file.setframerate(48000)
            audio_file.writeframes(audio_data)
    except Exception as e:
        logger.exception(str(e))


def delete_file(path:str):
    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
        else:
            logger.error("The file does not exist")
    except Exception as e:
        logger.exception(str(e))


def recognize_from_audio_file(path:str) -> str:
    try:
        key = KEY
        region = REGION
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        speech_config.speech_recognition_language="en-US"
        
        audio_config = speechsdk.audio.AudioConfig(filename=path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            return "No speech could be recognized"
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            reason = cancellation_details.reason
            if reason.reason == speechsdk.CancellationReason.Error:
                return f"Error details: {reason.error_details}"
    except Exception as e:
        logger.exception(str(e))
        return "An error occurred. Review the logs for more information."
            

def recognize_from_microphone():   
    speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
    speech_config.speech_recognition_language="en-US"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")