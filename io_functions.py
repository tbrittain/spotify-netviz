import os
from pathlib import Path
import urllib.request as request
import auth


def user_input_parser(choices):
    choice = ''
    while choice not in choices:
        choice = input('Please use one of the following options: %s: ' % ', '.join(choices))
    return choice


def get_artist_art(artist_id):
    results = auth.spotify.search(q='artist:' + artist_id, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        art = artist['images'][0]['url']
        return art


def art_download(spotify_id, url):
    os.chdir('../album_arts')
    art_path = str(os.getcwd() + '/' + spotify_id + '.jpg')
    art_path.replace('\\', '/')
    art_path = Path(art_path)

    if art_path.is_file():  # introduce check to determine if art present, and if so, no need to re-download
        pass
    else:
        f = open(spotify_id + '.jpg', 'wb')  # TODO: use with open instead of just open
        f.write(request.urlopen(url=url).read())
        f.close()


def playlist_export(playlist_dataframe, filename, file_format):
    # format must be either csv or xlsx
    if file_format == 'csv':
        try:
            playlist_dataframe.to_csv(filename + '.' + file_format)
            print("File " + '"' + filename + '.' + file_format + '"' + " exported to " + os.getcwd())
        except PermissionError:
            print('Coule not write to "' + filename + '.' + file_format + '". It may currently be in use. Please close '
                                                                          'any programs currently using it and try '
                                                                          'again.')
    elif file_format == 'xlsx':
        try:
            playlist_dataframe.to_excel(filename + '.' + file_format)
            print("File " + '"' + filename + '.' + file_format + '"' + " exported to " + os.getcwd())
        except PermissionError:
            print('Coule not write to "' + filename + '.' + file_format + '". It may currently be in use. Please close '
                                                                          'any programs currently using it and try '
                                                                          'again.')

