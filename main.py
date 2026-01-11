import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os
from youtube_search import YoutubeSearch
import yt_dlp
import eyed3
import requests

load_dotenv()

cid = os.getenv('SPOTIPY_CLIENT_ID')
secret = os.getenv('SPOTIPY_CLIENT_SECRET')
playlist_id = input("Please enter a link to the Spotify playlist: ")

client_credentials_manager = SpotifyClientCredentials(client_id = cid, client_secret = secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_track_metadata(track):
    try:
        genre = sp.artist(track['artists'][0]['id'])['genres'][0].title()
    except:
        genre = None

    return {
        'artist': track['artists'][0]['name'],
        'name': track['name'],
        'album': track['album']['name'],
        'track_number': track['track_number'],
        'total_tracks': track['album']['total_tracks'],
        'release_date': track['album']['release_date'],
        'genre': genre,
        'cover': track['album']['images'][0]['url']
    }

def get_playlist_tracks(playlist_id):
    results = sp.playlist_items(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def download_track(url, path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': path,
        'noplaylist': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
        ],
        'quiet': True,
        'remote_components': ['ejs:github'],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def tag_metadata(path, metadata):
    audiofile = eyed3.load(path)

    if audiofile.tag is None:
        audiofile.initTag()

    audiofile.tag.artist = metadata['artist']
    audiofile.tag.album_artist = metadata['artist']
    audiofile.tag.album = metadata['album']
    audiofile.tag.title = metadata['name']
    audiofile.tag.genre = metadata['genre']
    audiofile.tag.release_date = metadata['release_date']
    audiofile.tag.track_num = (metadata['track_number'], metadata['total_tracks'])

    audiofile.tag.images.set(3, requests.get(metadata['cover']).content, "image/jpeg")

    audiofile.tag.save()

def format_name(name):
    return name.replace("/", "_")

tracks = get_playlist_tracks(playlist_id)

playlist_name = sp.playlist(playlist_id)['name']
playlist_owner = sp.playlist(playlist_id)['owner']['display_name']

with (open(f'downloads/{playlist_name}.m3u', 'a+') as playlist):
    print(f'\nProcessing playlist {playlist_name} by {playlist_owner}\n')

    for i in range(len(tracks)):
        metadata = get_track_metadata(tracks[i]['track'])
        song = metadata['name']
        album = metadata['album']
        artist = metadata['artist']
        path = f'./downloads/{format_name(artist)}/{format_name(album)}/{format_name(song)}.mp3'

        print(f'Processing Track {i+1} of {len(tracks)}: {artist} - {song}, {album}')

        if path.replace('./downloads/', '') not in playlist.read() and not os.path.exists(path):
            search_term = f'{song} {artist}'
            results = YoutubeSearch(search_term, max_results=10).to_dict()
            url = "https://www.youtube.com" + results[0]['url_suffix']

            download_track(url, path.replace('.mp3', ''))
            print('Download complete!')

            tag_metadata(path, metadata)
            print('Metadata tagging complete!')

            path = path.replace('./downloads/', '')
            playlist.write(f'{path}\n')
            print('Added song to playlist!\n')

        else:
            print('Track already exists!\n')