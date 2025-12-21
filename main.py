import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

cid = os.getenv('SPOTIPY_CLIENT_ID')
secret = os.getenv('SPOTIPY_CLIENT_SECRET')
playlist_id = os.getenv('SPOTIFY_PLAYLIST_ID')

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_tracks(playlist_id):
    results = sp.playlist_items(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

tracks = get_playlist_tracks(playlist_id)

for i in range(len(tracks)):
    song = tracks[i]['track']['name']
    album = tracks[i]['track']['album']['name']
    artist = tracks[i]['track']['artists'][0]['name']

    print(f'{artist} - {song}, {album}')