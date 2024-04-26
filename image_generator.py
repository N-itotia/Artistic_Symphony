import google.generativeai as genai
import os
import sqlite3
import requests


# Configure Gemini API with your API key from the .env file
genai.configure(api_key='')  # Replace with your actual API key
image_model = genai.GenerativeModel('models/gemini-pro')  # Assuming model availability

# Database connection
def connect_db():
  conn = sqlite3.connect('spotify_tracks.db')
  cursor = conn.cursor()
  return conn, cursor

def close_db(conn):
  conn.commit()
  conn.close()

# Fetch song reviews from the database
def fetch_reviews(cursor):
  cursor.execute("SELECT id, review FROM tracks")
  songs = cursor.fetchall()
  return songs

# Generate images based on reviews and save them (assuming model availability)
def generate_and_save_images(review, track_id):
  os.makedirs('photos', exist_ok=True)  # Ensure the directory exists
  for i in range(3):
    image_prompt = f"Create an artistic representation of the following review: '{review}'"
    try:
      image = image_model.generate_content(image_prompt)
      image_path = f'photos/{track_id}_{i+1}.png'
      with open(image_path, 'wb') as file:
        file.write(image)
    except Exception as e:  # Handle potential errors during image generation
      print(f"Error generating image {i+1} for track {track_id}: {e}")

def main():
  # Connect to database
  conn, cursor = connect_db()

  # Fetch song reviews from the database
  songs = fetch_reviews(cursor)

  for song_id, review in songs:
    # Generate images based on the review and save them (assuming model availability)
    generate_and_save_images(review, song_id)

  # Close database connection
  close_db(conn)

if __name__ == "__main__":
  main()
