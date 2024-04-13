import sqlite3
import google.generativeai as genai
import os
import collect_spotify_playlist

# Load environment variables (assuming API key is stored in API_KEY)
os.environ.load_dotenv()

# Database connection
db_file = 'spotify_tracks.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Configure Gemini API
genai.configure(api_key=os.environ['API_KEY'])
model = genai.GenerativeModel('gemini-pro')


def fetch_review(album_name, artist_name):
  """Fetches a review summary for the given album and artist using Gemini API.

  Args:
      album_name: Name of the album.
      artist_name: Name of the artist.

  Returns:
      A string containing the review summary or an empty string if the API call fails.
  """
  prompt = f"Can you give a summary for the reviews for: the album, {album_name} by {artist_name} as a paragraph?"
  try:
    response = model.generate_content(prompt)
    return response.text
  except Exception as e:
    print(f"Error fetching review for {album_name} by {artist_name}: {e}")
    return ""


# Loop through songs in the database
cursor.execute("SELECT * FROM tracks")
for row in cursor.fetchall():
  track_id, track_name, album_name, artist_name = row

  # Fetch review using Gemini API
  review = fetch_review(album_name, artist_name)

  # Update database with review
  cursor.execute("UPDATE tracks SET review=? WHERE id=?", (review, track_id))
  conn.commit()

  print(f"Fetched review for: {track_name} - {album_name} by {artist_name}")

# Close connections
cursor.close()
conn.close()

print("Review fetching complete!")
