from flask import Flask, jsonify, render_template, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sqlite3
from dotenv import load_dotenv
load_dotenv()  # This line loads the environment variables from the .env file


app = Flask(__name__)

# Spotify API credentials
client_id = '0dac66ab362e40b6b01f22ab18976966'
client_secret = '99781acabaec43b28ee20ac5f4fcd464' 
redirect_uri = 'http://localhost:8888/callback'
scope = 'playlist-read-private'

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scope))

# SQLite database file
db_file = 'spotify_tracks.db'

@app.route('/')
def home():
    return render_template('landing_page.html')

@app.route('/fetch_on_repeat')
def fetch_on_repeat():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist and add a column for reviews
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name TEXT,
            album_name TEXT,
            artist_name TEXT,
            review TEXT  -- Added column for storing reviews
        )
    ''')

    # Fetch the 'On Repeat' playlist
    playlists = sp.current_user_playlists()
    on_repeat_playlist = next((p for p in playlists['items'] if p['name'] == 'On Repeat'), None)

    if on_repeat_playlist:
        playlist_id = on_repeat_playlist['id']
        tracks = sp.playlist_tracks(playlist_id)
        for item in tracks['items']:
            track = item['track']
            album = track['album']
            artist = track['artists'][0]['name']
            # Save to SQLite database
            cursor.execute('''
                INSERT INTO tracks (track_name, album_name, artist_name, review) VALUES (?, ?, ?, ?)
            ''', (track['name'], album['name'], artist, None))
            conn.commit()
    else:
        return jsonify({'status': 'On Repeat playlist not found'})

    cursor.close()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)

