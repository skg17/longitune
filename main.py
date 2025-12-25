import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
from youtube_search import YoutubeSearch
import yt_dlp

load_dotenv()

cid = os.getenv('SPOTIPY_CLIENT_ID')
secret = os.getenv('SPOTIPY_CLIENT_SECRET')
playlist_id = os.getenv('SPOTIFY_PLAYLIST_ID')

client_credentials_manager = SpotifyClientCredentials(client_id = cid, client_secret = secret)
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
    cover = tracks[i]['track']['album']['images'][0]['url']

    print(f'Processing Track {i} of {len(tracks)}: {artist} - {song}, {album}')

    search_term = tracks[i]['track']['name'] + " " + tracks[i]['track']['artists'][0]['name']
    results = YoutubeSearch(search_term, max_results=10).to_dict()
    url = "https://www.youtube.com" + results[0]['url_suffix']

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': f'./downloads/{artist}/{album}/{song}.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'remote_components': ['ejs:github']
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])