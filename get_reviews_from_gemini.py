import google.generativeai as genai
import os
import sqlite3
import collect_spotify_playlist

# Configure Gemini API with your API key from the .env file
genai.configure(api_key=os.environ['API_KEY'])
model = genai.GenerativeModel('gemini-pro')

# Database connection
def connect_db():
  conn = sqlite3.connect('spotify_tracks.db')
  cursor = conn.cursor()
  return conn, cursor

def close_db(conn):
  conn.commit()
  conn.close()

# Fetch song reviews using Gemini API
def fetch_review_summary(album_name, artist_name):
  prompt = f"Can you give a summary for the reviews of the album, '{album_name}' by '{artist_name}' as a paragraph?"
  response = model.generate_content(prompt)
  return response.text

# Update song review in database
def update_song_review(cursor, track_id, review):
  cursor.execute("UPDATE tracks SET review = ? WHERE id = ?", (review, track_id))

def main():
  # Connect to database
  conn, cursor = connect_db()

  # Fetch songs from the database
  cursor.execute("SELECT id, album_name, artist_name FROM tracks")
  songs = cursor.fetchall()

  for song_id, album_name, artist_name in songs:
    # Get review summary from Gemini API
    review = fetch_review_summary(album_name, artist_name)

    # Update song review in the database
    update_song_review(cursor, song_id, review)

  # Close database connection
  close_db(conn)

if __name__ == "__main__":
  main()
