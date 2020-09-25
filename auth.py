import spotipy
from spotipy.oauth2 import SpotifyPKCE

auth_manager = SpotifyPKCE()
spotify = spotipy.Spotify(auth_manager=auth_manager)

