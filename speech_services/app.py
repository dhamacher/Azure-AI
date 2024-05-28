from flask import Flask, request, jsonify
from flask import render_template
from dotenv import load_dotenv
from pathlib import Path
import core.speech_to_text as stt
import os
import logging

LOGGER_NAME = "SPEECH-SVC"
load_dotenv()

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(LOGGER_NAME)
current_path = Path(__file__).absolute().parent
AUDIO_OUTPUT_PATH = Path(current_path / str(os.environ.get('AUDIO_OUTPUT_PATH')))
app = Flask(__name__)

@app.route('/audio', methods=['POST'])
def audio():
    try:
        logger.debug("Received audio file")
        audio_file = request.files['file']
        if audio_file.filename == '':
            logger.error("No selected file")
            return 'No selected file'
        audio_data = audio_file.read()
        if len(audio_data) == 0:
            logger.error("Empty file")
            return 'Empty file'
        file_path = str(Path(AUDIO_OUTPUT_PATH / '35643.wav'))
        stt.save_audio_file(file_path, audio_data)
        logger.debug(f"File saved to {file_path}")
        result = stt.recognize_from_audio_file(file_path)        
        return jsonify(result)
    except Exception as e:
        logger.exception(str(e))

@app.route("/")
def hello_world():
    return render_template('index.html')