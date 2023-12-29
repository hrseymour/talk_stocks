from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

import yfinance as yf
import logging
import os

HOST_URL='transformerapi.com'

GOOGLE_APIS_URL='https://www.googleapis.com'
GOOGLE_OAUTH2_URL='https://accounts.google.com/o/oauth2'

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('TRANSFORMER_API_SECRET_KEY')

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url=f'{GOOGLE_OAUTH2_URL}/token',
    access_token_params=None,
    authorize_url=f'{GOOGLE_OAUTH2_URL}/auth',
    authorize_params=None,
    api_base_url=f'{GOOGLE_APIS_URL}/oauth2/v1/',
    redirect_uri=f'https://{HOST_URL}/authorize',
    client_kwargs={'scope': f'{GOOGLE_APIS_URL}/auth/userinfo.email'}
)

def is_authenticated(api_key = ''):
    return 'user_token' in session or api_key == app.secret_key

@app.route('/')
def index():
    return {'status': 'OK'}

@app.route('/quote/<symbol>', methods=['GET'])
def get_quote(symbol):
    api_key = request.headers.get('X-API-Key', '')
    if not is_authenticated(api_key):
        # Return a 401 Unauthorized status code with a message
        return jsonify({"error": "Authentication required"}), 401
        # Redirect the user to login if they are not already logged in
        #  return redirect(url_for('login'))

    df = yf.download(symbol, period='1d', progress=False)
    data = df.iloc[0].to_dict()
    data['symbol'] = symbol
    data = {k.lower().replace(' ', '_'): v for k, v in data.items()}

    # data['user_email'] = session.get('user_email', 'N/A')
    return jsonify(data)

@app.route('/login')
def login():
    # Store the URL the user wants to go to in session
    next_url = request.args.get('next') or url_for('index')
    session['next_url_after_login'] = next_url

    # Proceed with Google Authentication
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()

    userinfo_endpoint = f'{GOOGLE_APIS_URL}/oauth2/v2/userinfo'
    resp = google.get(userinfo_endpoint, token=token)
    user_info = resp.json()

    session['user_token'] = token
    session['user_email'] = user_info.get('email')

    next_url = session.pop('next_url_after_login', url_for('index')) 
    return redirect(next_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def main() -> None:
    app.run(debug=True, host="0.0.0.0", port=443, ssl_context='adhoc')

if __name__ == "__main__":
    main()

