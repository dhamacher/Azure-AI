import flask
from flask import Flask, request, jsonify, url_for,redirect, render_template
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, login_user, UserMixin
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
from pathlib import Path
from core.const import LOGGER_NAME, AUDIO_OUTPUT_PATH, GOOGLE_AUTH_CLIENT_ID, GOOGLE_AUTH_CLIENT_SECRET, GOOGLE_AUTH_CLIENT_SECRETS_FILE_PATH,SCOPES
import core.speech_to_text as stt
import os
import logging
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery


load_dotenv()
login_manager = LoginManager()

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(LOGGER_NAME)
current_path = Path(__file__).absolute().parent
google_api_file_path = Path(current_path / GOOGLE_AUTH_CLIENT_SECRETS_FILE_PATH)
logger.info(f"Google API File Path: {str(google_api_file_path)}")
output_path = Path(current_path / str(AUDIO_OUTPUT_PATH))
logger.info(f"Output Path: {str(output_path)}")

# Check if the directory exists
if not output_path.exists():
    logger.info(f"Create Folder for Staging @ {str(output_path)}")
    output_path.mkdir(parents=True)

app = Flask(__name__)
app.secret_key = "supersekrit"  # Replace with your own secret key
login_manager.init_app(app)

# # Set up Google OAuth
# blueprint = make_google_blueprint(
#     client_id=GOOGLE_AUTH_CLIENT_ID,
#     client_secret=GOOGLE_AUTH_CLIENT_SECRET,
#     scope=SCOPES
# )
# app.register_blueprint(blueprint, url_prefix="/login")

class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

@app.route('/index')
def index():
  if 'credentials' not in flask.session:
    return flask.redirect('/')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  return render_template('index2.html')


@app.route('/')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      google_api_file_path, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      google_api_file_path, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('index'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.')
  else:
    return('An error occurred.')


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>')


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    message = "No File! Has Been Uploaded Yet!"
    file_url = None
    if request.method == 'GET':
        return render_template('upload.html')

    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    if file:
        # filename = secure_filename(file.filename)
        file_path = str(Path(output_path / 'uploaded_file.wav'))
        file_url = url_for('static', filename=file_path)
        file.save(file_path)
        result = stt.recognize_from_audio_file(file_path)
        return render_template('upload.html', message=result, file_url=file_url)

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
        file_path = str(Path(output_path / 'test_file.wav'))
        stt.save_audio_file(file_path, audio_data)
        logger.debug(f"File saved to {file_path}")
        result = stt.recognize_from_audio_file(file_path)        
        return jsonify(result)
    except Exception as e:
        logger.exception(str(e))