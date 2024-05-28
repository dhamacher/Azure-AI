from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

KEY                 = os.environ.get('SPEECH_KEY')
REGION              = os.environ.get('SPEECH_REGION')
LOGGER_NAME         = os.environ.get('LOGGER_NAME')
AUDIO_OUTPUT_PATH   = os.environ.get('AUDIO_OUTPUT_PATH')

GOOGLE_AUTH_CLIENT_SECRET               = os.environ.get('GOOGLE_AUTH_CLIENT_SECRET')
GOOGLE_AUTH_CLIENT_ID                   = os.environ.get('GOOGLE_AUTH_CLIENT_ID')
GOOGLE_AUTH_CLIENT_SECRETS_FILE_PATH    = os.environ.get('GOOGLE_AUTH_CLIENT_SECRETS_FILE_PATH')
SCOPES                                  = os.environ.get('SCOPES')
OAUTHLIB_INSECURE_TRANSPORT             = os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')