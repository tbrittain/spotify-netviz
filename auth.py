import spotipy
from spotipy.oauth2 import SpotifyPKCE

auth_manager = SpotifyPKCE(client_id='cc77361c432c4bc28740a3a27828b5ae',
                           redirect_uri='http://localhost:8888/callback/',
                           scope='playlist-read-collaborative playlist-read-private user-library-read')
spotify = spotipy.Spotify(auth_manager=auth_manager)
