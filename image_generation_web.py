from flask import Flask, render_template, Response, request, redirect, session
from spotipy.oauth2 import SpotifyOAuth
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
import os
import sqlite3
from io import BytesIO
from base64 import b64encode
from get_reviews_from_gemini import *
from collect_spotify_playlist import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_very_secret_key'  # Replace 'your_very_secret_key' with a strong, unique value


# Configure Vertex AI
project_id = "artisticsymphony"
vertexai.init(project=project_id, location="us-central1")
model = ImageGenerationModel.from_pretrained("imagegeneration@006")

# Database connection
def connect_db():
    conn = sqlite3.connect('spotify_tracks.db')
    cursor = conn.cursor()
    return conn, cursor

def close_db(conn):
    conn.commit()
    conn.close()

def fetch_songs_and_reviews(api_key):
    # Example implementation
    try:
        # Logic to fetch songs and reviews using the API key
        # This should return a dictionary where keys are song names and values are lists of images
        return {}  # Return an empty dictionary if no data is fetched
    except Exception as e:
        print(f"Error fetching songs and reviews: {e}")
        return {}

# Fetch song reviews from the database
def fetch_reviews(cursor):
    cursor.execute("SELECT id, review, track_name FROM tracks")  # Assuming 'track_name' is the column name
    songs = cursor.fetchall()
    return songs

def create_images(review, song_name, song_id):
    images = []
    try:
        prompt = f"Create an artistic scenery based on the following review: '{review}'"
        response = model.generate_images(
            prompt=prompt,
            number_of_images=3,
            language="en",
            aspect_ratio="1:1",
            safety_filter_level="block_none",
            person_generation="allow_adult"
        )

        for idx, image in enumerate(response):
            image_filename = f"{song_name.replace(' ', '_')}_{song_id}_{idx}.png"
            image_path = f'generated_images/{image_filename}'
            image.save(location=image_path, include_generation_parameters=True)
            
            with open(image_path, "rb") as img_file:
                images.append(b64encode(img_file.read()).decode('utf-8'))
    except Exception as e:
        print(f"Error generating images for review: {e}")
    return images

def fetch_images():
    images = []
    directory = 'generated_images'
    for filename in os.listdir(directory):
        if filename.endswith(".png"):
            song_name = filename.rsplit('_', 2)[0].replace('_', ' ')
            with open(os.path.join(directory, filename), "rb") as img_file:
                image_data = b64encode(img_file.read()).decode('utf-8')
                images.append({'data': image_data, 'song_name': song_name})
    return images

@app.route('/')
def homepage():
    return render_template('login.html')

@app.route('/spotify_login')
def spotify_login():
    sp_oauth = SpotifyOAuth(client_id='', client_secret='', redirect_uri='http://localhost:8888/callback', scope='playlist-read-private')
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(client_id='', client_secret='', redirect_uri='http://localhost:8888/callback', scope='playlist-read-private')
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    return render_template('success_login.html')

@app.route('/generate_images')
def generate_images():
    conn, cursor = connect_db()  # Connect to the database
    reviews = fetch_reviews(cursor)  # Fetch reviews from the database
    image_data_list = []  # This will store dictionaries with image data and song names

    for review in reviews:
        song_id, review_text, song_name = review
        # Generate images for each review
        image_b64_list = create_images(review_text, song_name, song_id)  # This should return a list of base64 strings
        for image_b64 in image_b64_list:
            image_data_list.append({'data': image_b64, 'song_name': song_name})  # Append a dictionary for each image

    close_db(conn)  # Close the database connection
    return render_template('display_images.html', images=image_data_list)


@app.route('/display_images_page')
def display_images_page():
    images = fetch_images()
    return render_template('display_images_page.html', images=images)

@app.route('/fetch_songs', methods=['POST'])
def fetch_songs():
    api_key = request.form['api_key']
    songs_reviews = fetch_songs_and_reviews(api_key)
    if not isinstance(songs_reviews, dict):
        print("Expected songs_reviews to be a dictionary.")
        songs_reviews = {}
    return render_template('review_images.html', songs_reviews=songs_reviews)

@app.route('/display_images/<int:song_id>')
def display_images_route(song_id):
    conn, cursor = connect_db()
    cursor.execute("SELECT review, track_name FROM tracks WHERE id = ?", (song_id,))
    review, song_name = cursor.fetchone()
    images = create_images(review, song_name, song_id)
    close_db(conn)
    return render_template('display_images.html', images=images, song_id=song_id)

if __name__ == "__main__":
    app.run(debug=True, port=8888)