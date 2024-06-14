import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, Response, url_for, session, redirect, jsonify

CLIENT_ID = "#####"
CLIENT_SECRET = "#####"
SECRET_KEY = "secret_key"
TOKEN_INFO = "token_info"
SHORT_TERM = "short_term"

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'Spotify API Cookie'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=url_for("callback", _external=True),
        scope="user-top-read user-library-read"
    )

def generate_yt_link(judulLagu):
    formatted_title = judulLagu.replace(" ", "+")
    return f"https://www.youtube.com/results?search_query={formatted_title}"

def generate_spotify_link(judulLagu):
    formatted_title = judulLagu.replace(" ", "%20")
    return f"https://open.spotify.com/search/{formatted_title}"

@app.route("/")
def index():
    return Response("Not Found", status=404)

@app.route("/login")
def login():
    global min_valence, max_valence, min_danceability, max_danceability, min_energy, max_energy, mood
    mood = request.args.get('mood')
    if mood == 'happy':
        min_danceability = 0.2
        max_danceability = 1
        min_energy = 0.2
        max_energy = 1
        min_valence = 0.5
        max_valence = 1
    elif mood == 'sad':
        min_danceability = 0
        max_danceability = 0.8
        min_energy = 0
        max_energy = 0.8
        min_valence = 0
        max_valence = 0.5
    elif mood == 'angry':
        min_danceability = 0.2
        max_danceability = 1
        min_energy = 0.2
        max_energy = 1
        min_valence = 0.25
        max_valence = 1
    elif mood == 'disgust':
        min_danceability = 0.2
        max_danceability = 1
        min_energy = 0.2
        max_energy = 1
        min_valence = 0
        max_valence = 0.75
    elif mood == 'fear':
        min_danceability = 0
        max_danceability = 0.8
        min_energy = 0
        max_energy = 0.8
        min_valence = 0
        max_valence = 0.75
    elif mood == 'surprise':
        min_danceability = 0.2
        max_danceability = 1
        min_energy = 0.2
        max_energy = 1
        min_valence = 0.25
        max_valence = 1
    else:
        min_danceability = 0
        max_danceability = 1
        min_energy = 0
        max_energy = 1
        min_valence = 0
        max_valence = 1
    print(mood)
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    if code:
        token_info = sp_oauth.get_access_token(code)
        session[TOKEN_INFO] = token_info
        return redirect(url_for("getTracks"))
    else:
        return redirect(url_for("login"))

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired: 
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    return token_info

@app.route("/getTracks")
def getTracks():
    token_info = get_token()
    if not token_info:
        return redirect(url_for("login", _external=True))
    if os.path.exists(".cache"): 
        os.remove(".cache")
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_top_songs = sp.current_user_top_tracks(
        limit=10,
        offset=0,
        time_range="short_term"
    )
    tracks = [f"{track['name'].replace('\u2019', "'")} - {track['artists'][0]['name'].replace('\u2019', "'")}" for track in user_top_songs['items']]
    track_ids = [track['id'] for track in user_top_songs['items']]
    recommended_tracks = []
    recommended_tracks_ids = []
    yt_links = []
    spotify_links = []
    for track_id in track_ids:
        recommendations = sp.recommendations(
            seed_tracks=[track_id],
            min_danceability=min_danceability,
            max_danceability=max_danceability,
            min_energy=min_energy,
            max_energy=max_energy,
            min_valence=min_valence,
            max_valence=max_valence,
            limit=1
        )
        recommended_track = f"{recommendations['tracks'][0]['name'].replace('\u2019', "'")} - {recommendations['tracks'][0]['artists'][0]['name'].replace('\u2019', "'")}"
        recommended_tracks.append(recommended_track)
        recommended_tracks_ids.append(recommendations['tracks'][0]['id'])
        yt_links.append(generate_yt_link(recommended_track))
        spotify_links.append(generate_spotify_link(recommended_track))
    if os.path.exists(".cache"): 
        os.remove(".cache")
    return jsonify({
        'access_token': token_info['access_token'],
        'top_tracks': tracks,
        'recommended_tracks': recommended_tracks,
        'recommended_tracks_ids': recommended_tracks_ids,
        'yt_links': yt_links,
        'spotify_links': spotify_links,
        'mood': mood
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
