from flask import Flask, request, url_for, session, redirect, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "client-id"
CLIENT_SECRET = "client-secret"
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
    track_ids = [track['id'] for track in user_top_songs['items']]
    recommended_tracks = []
    for track_id in track_ids:
        recommendations = sp.recommendations(seed_tracks=[track_id], limit=1)
        recommended_tracks.append(f"{recommendations['tracks'][0]['name'].replace('\u2019', "'")} - {recommendations['tracks'][0]['artists'][0]['name'].replace('\u2019', "'")}")
    return jsonify({
        'top_tracks': tracks,
        'recommended_tracks': recommended_tracks
    })



if __name__ == '__main__':
    app.run()
