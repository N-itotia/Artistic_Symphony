from flask import Flask, render_template, Response, request
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
import os
import sqlite3
from io import BytesIO
from base64 import b64encode

app = Flask(__name__)

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

def generate_images(review, song_name, song_id):
    images = []
    try:
        prompt = f"Create an artistic scenery based of the following review: '{review}'"
        print(f"Generating images with prompt: {prompt}")
        response = model.generate_images(
            prompt=prompt,
            number_of_images=3,
            language="en",
            aspect_ratio="1:1",
            safety_filter_level="block_none",
            person_generation="allow_adult"
        )
        print(f"Number of images generated: {len(response)}")  # Debug statement to check the number of images

        os.makedirs('generated_images', exist_ok=True)
        
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
            song_name = filename.rsplit('_', 2)[0].replace('_', ' ')  # Assuming filename format is 'song_name_song_id_idx.png'
            with open(os.path.join(directory, filename), "rb") as img_file:
                image_data = b64encode(img_file.read()).decode('utf-8')
                images.append({'data': image_data, 'song_name': song_name})
    return images

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/display_images_page')
def display_images_page():
    # Fetch images from the database or a predefined source
    images = fetch_images()  # This function needs to be implemented to fetch images
    return render_template('display_images_page.html', images=images)


@app.route('/fetch_songs', methods=['POST'])
def fetch_songs():
    api_key = request.form['api_key']
    songs_reviews = fetch_songs_and_reviews(api_key)
    if not isinstance(songs_reviews, dict):
        print("Expected songs_reviews to be a dictionary.")
        songs_reviews = {}  # Ensure it's a dictionary even if there was an error
    return render_template('review_images.html', songs_reviews=songs_reviews)

@app.route('/display_images/<int:song_id>')
def display_images(song_id):
    conn, cursor = connect_db()
    cursor.execute("SELECT review, track_name FROM tracks WHERE id = ?", (song_id,))
    review, song_name = cursor.fetchone()
    images = generate_images(review, song_name, song_id)
    close_db(conn)
    return render_template('display_images.html', images=images, song_id=song_id)

if __name__ == "__main__":
    app.run(debug=True)