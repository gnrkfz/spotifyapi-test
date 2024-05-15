from flask import Flask, request, url_for, session, redirect, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "1ac04515e52e48a79520e730d7a609c8"
CLIENT_SECRET = "92e9bd847c9b49a38526a7c340a67259"
SECRET_KEY = "seret-key"
TOKEN_CODE = "token_info"
SHORT_TERM = "short_term"

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-top-read user-library-read"
    )

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = SECRET_KEY

@app.route("/")
def index():
    return render_template("index.html", title="Welcome")

@app.route("/login")
def login():
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-top-read user-library-read"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/redirectPage")
def redirectPage():
    code = request.args.get('code')
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("redirectPage", _external=True),
        scope="user-top-read user-library-read"
    )
    token_info = sp_oauth.get_access_token(code) 
    session[TOKEN_CODE] = token_info
    return redirect(url_for("getTrack", _external=True))
def get_token():
    token_info = session.get(TOKEN_CODE, None)
    return token_info

@app.route("/getTrack")
def getTrack():
    user_token = get_token()
    if not user_token:
        return redirect(url_for("login", _external=True))
    sp = spotipy.Spotify(
        auth=user_token['access_token']
    )
    user_top_songs = sp.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range="short_term"
    )
    track_titles = [track['name'].replace('\u2019', "'") for track in user_top_songs['items']]
    return track_titles



if __name__ == '__main__':
    app.run()