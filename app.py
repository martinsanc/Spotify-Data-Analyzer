from flask import Flask, request, abort, Response, redirect
import os
import requests
import base64
import json

app = Flask(__name__)

@app.route('/')
def homepage():

    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    CALLBACK_URL = os.environ.get('CALLBACK_URL')
    REDIRECT_URL = os.environ.get('REDIRECT_URL')

    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

    auth_token = request.args.get('code')

    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": CALLBACK_URL
    }

    auth = "{}:{}".format(CLIENT_ID, CLIENT_SECRET)
    base64encoded = base64.urlsafe_b64encode(auth.encode('UTF-8')).decode('ascii')
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    response_data = json.loads(post_request.content)

    if 'error' in response_data:
        abort(400)
        abort(Response(response_data['error_description']))

    
    return redirect('{redirect}/{access}'.format(redirect=REDIRECT_URL, access=response_data['access_token']), code=302)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
