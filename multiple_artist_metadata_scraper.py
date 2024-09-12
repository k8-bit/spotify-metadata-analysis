# Import libraries
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.express as px

# Credentials from Spotify for developers
cid = 'your client id here'
secret = 'your client secret here'

# Authentication
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Create dataframe
artist_data = []

# Define list of artist URIs
artist_uris = [
    'spotify:artist:54D10LTFNUkbYKH9OmW2C7',  # URI 1 -- BABY
    'spotify:artist:6t0WjFRLm8nYasSkwNQQtV',  # URI 2 -- TNB
    'spotify:artist:6hNNPYUZagXKDedaDDnTH7'   # URI 3 -- WK
]

# Loop through each artist URI
for artist_uri in artist_uris:
    # Create list of albums for the artist
    results = sp.artist_albums(artist_uri, album_type='album')
    albums = results['items']
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])

    # Store unique album names and IDs
    names = []
    album_ids = []
    for album in albums:
        name = album['name'].lower()
        if name not in names:
            names.append(name)
            album_ids.append(album['id'])

    # Retrieve track-specific details for each album
    for album_id in album_ids:
        results = sp.album_tracks(album_id)
        album_info = sp.album(album_id)
        tracks = results['items']

        # Results from Spotify API come back in pages
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        # Process each track
        for track in tracks:
            track_row = {
                'artist': sp.artist(artist_uri)['name'],  # Get artist name
                'spotify_id': track['id'],
                'spotify_uri': track['uri'],
                'album': album_info['name'],
                'name': track['name'],
                'release_date': album_info['release_date'],
                'track_number': track['track_number'],
                'popularity': sp.track(track['id'])['popularity']
            }

            # Get track features
            features = sp.audio_features(track['id'])[0]
            track_row.update({
                'danceability': features['danceability'],
                'energy': features['energy'],
                'key': features['key'],
                'loudness': features['loudness'],
                'mode': features['mode'],
                'speechiness': features['speechiness'],
                'acousticness': features['acousticness'],
                'instrumentalness': features['instrumentalness'],
                'liveness': features['liveness'],
                'valence': features['valence'],
                'tempo': features['tempo'],
                'duration_ms': features['duration_ms'],
                'time_signature': features['time_signature']
            })

            artist_data.append(track_row)

# Define columns for dataframe
cols = ['artist', 'spotify_id', 'spotify_uri', 'album', 'name', 'popularity', 'release_date', 
        'track_number', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 
        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']

# Create dataframe
df = pd.DataFrame(artist_data, columns=cols)

# Export dataframe to CSV
df.to_csv('combined_artists_data.csv', index=False)

# Function to map artist names to abbreviations
def map_artist_name(artist_name):
    if artist_name == 'The Nocturnal Broadcast':
        return 'TNB'
    elif artist_name == 'Baby in the 90s':
        return 'BABY'
    elif artist_name == 'Wonder Kid':
        return 'WK'
    else:
        return artist_name  # If no match, keep the original name

# Apply the mapping function to the 'artist' column
df['artist'] = df['artist'].apply(map_artist_name)

# Convert track duration from milliseconds to minutes
df['duration_min'] = df['duration_ms'] / 60000

# Drop the specified columns
df = df.drop(columns=['tempo', 'time_signature', 'spotify_id', 'spotify_uri', 'key'])

# Display the updated DataFrame
print(df.head())

# Export dataframe to CSV file
df.to_csv('master_file.csv', index=False)