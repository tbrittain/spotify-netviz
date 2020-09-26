import pandas as pd
import auth
import os
import time
from tqdm import tqdm
import re
import io_functions


def saved_lib_results():
    results = auth.spotify.current_user_saved_tracks()
    tracks = results['items']
    while results['next']:
        results = auth.spotify.next(results)
        tracks.extend(results['items'])
    return tracks


def playlist_track_results(username, playlist_id):
    # better result retrieval that ignores the 100 track query limit
    # from https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist
    results = auth.spotify.user_playlist_tracks(username, playlist_id)
    tracks = results['items']
    while results['next']:
        results = auth.spotify.next(results)
        tracks.extend(results['items'])
    return tracks


# noinspection PyTypeChecker
# type checker not a fan of the data='null' optional parameter but it works fine when overwritten by saved tracks
def get_track_info(method, username='null', playlist_id='null', data='null'):
    """

    :param data:
    :param method: Method of result retrieval, from either playlist (playlist_track_results)
    or saved tracks (saved_lib_results)
    :param username: Spotify username URI for the owner of the given playlist
    :param playlist_id: Spotify playlist URI
    :return: Pandas DataFrame with the following attributes for each song: artist, artist ID, song, song ID,
    album, album ID, date when song was added to playlist, direct link to album art, as well as Spotify audio
    features
    """

    feature_list = ['artist', 'artist_uri', 'artist_id', 'song', 'song_uri', 'song_id', 'album', 'album_uri',
                    'album_id', 'added_at', 'art_link', 'song_length', 'preview_url', 'key', 'time_signature', 'tempo',
                    'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                    'valence']

    total_playlist_array = pd.DataFrame(columns=feature_list)  # create dataframe with above columns

    # method parameter determines how results are retrieved
    global tracks
    if method == 'playlist':
        tracks = playlist_track_results(username, playlist_id)  # store items of results as tracks
    elif method == 'saved':
        tracks = data
        playlist_id = 'Saved'
    # print("Performing metadata retrieval on playlist ID " + str(playlist_id) + " of track length " + str(len(tracks)))

    inner = tqdm(desc=f'Playlist {playlist_id}', unit='track', total=len(tracks), leave=False)
    try:
        for song in tracks:
            # general features for each track
            # TODO: also consider using song(['track']['artists'][0]['name'],
            track_info = {'artist': (song['track']['album']['artists'][0]['name']),
                          'artist_uri': (song['track']['album']['artists'][0]['uri']),
                          'artist_id': (song['track']['album']['artists'][0]['id']),
                          'song': (song['track']['name']),
                          'song_uri': (song['track']['uri']),
                          'song_id': (song['track']['id']),
                          'album': (song['track']['album']['name']),
                          'album_uri': (song['track']['album']['uri']),
                          'album_id': (song['track']['album']['id']),
                          'added_at': (song['added_at'][:10]),
                          'art_link': (song['track']['album']['images'][0]['url']),
                          'song_length': (float(song['track']['duration_ms']) / 60000)}

            if song['track']['preview_url'] is not None:  # adds track preview url if it exists
                track_info['preview_url'] = song['track']['preview_url']

            # documentation: https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/
            audio_analysis = auth.spotify.audio_features(song['track']['uri'])[0]
            # key: https://en.wikipedia.org/wiki/Pitch_class
            track_info['key'] = (audio_analysis['key'])
            track_info['time_signature'] = (audio_analysis['time_signature'])
            # TODO: consider some maths on tempo because often the Spotify tempo is double the actual
            track_info['tempo'] = (audio_analysis['tempo'])
            track_info['danceability'] = (audio_analysis['danceability'])
            track_info['energy'] = (audio_analysis['energy'])
            track_info['loudness'] = (audio_analysis['loudness'])
            track_info['speechiness'] = (audio_analysis['speechiness'])
            track_info['acousticness'] = (audio_analysis['acousticness'])
            track_info['instrumentalness'] = (audio_analysis['instrumentalness'])
            track_info['liveness'] = (audio_analysis['liveness'])
            track_info['valence'] = (audio_analysis['valence'])

            # create new dataframe and concatenate with full dataframe
            track_array = pd.DataFrame(track_info, index=[0])
            total_playlist_array = pd.concat([total_playlist_array, track_array], ignore_index=True)
            inner.update(1)
    except IndexError:  # a track attribute did not exist, then just skip. happens occasionally when no artist found.
        pass

    return total_playlist_array


def multiple_playlist_track_info(playlist_excel, saved_library=False):
    """

    :param saved_library: Optional - combines playlist data with saved library song data
    :param playlist_excel: Excel file with the following columns verbatim: creator and playlist_id. In the creator
    column, paste the URI of the creator of the playlist, and in the playlist_id column, paste the playlist URI.
    :return: Pandas DataFrame with the following attributes for each song: artist, artist ID, song, song ID,
    album, album ID, date when song was added to playlist, direct link to album art, as well as Spotify audio
    features
    """
    # import dataframe of playlists to download
    playlist_retrieval_time = time.time()
    playlist_array = pd.read_excel(playlist_excel, sheet_name=0)

    # reformat dataframe to dictionary
    reformatted_playlists = {}
    for index, row in playlist_array.iterrows():
        reformatted_playlists[row['playlist_id']] = row['creator']

    # init a single df for all playlist info
    feature_list = ['artist', 'artist_uri', 'artist_id', 'song', 'song_uri', 'song_id', 'album', 'album_uri',
                    'album_id', 'added_at', 'art_link', 'song_length', 'preview_url', 'key', 'time_signature', 'tempo',
                    'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                    'valence']

    overall_playlist_df = pd.DataFrame(columns=feature_list)

    # iterate get_playlist_track_info for each playlist in the excel file
    # outer = tqdm(desc='Overall progress', unit='playlist',
    #              total=len(reformatted_playlists.items()), leave=True)

    for playlist_id, creator in reformatted_playlists.items():
        playlist_df = get_track_info(username=creator, playlist_id=playlist_id, method='playlist')
        overall_playlist_df = pd.concat([overall_playlist_df, playlist_df])

    if saved_library:  # gathers saved song library and combines with playlist info
        saved_song_analysis_data = saved_lib_results()
        saved_song_analysis_data = get_track_info(method='saved', data=saved_song_analysis_data)
        overall_playlist_df = pd.concat([overall_playlist_df, saved_song_analysis_data])

        # outer.update(1)

    # isolate unique instances of songs by filtering uri
    overall_playlist_df = overall_playlist_df.drop_duplicates(subset=['song_uri'])

    process_time = round(time.time() - playlist_retrieval_time, 2)
    if process_time > 60:  # prints minutes and seconds if process time longer than a minute
        minutes = int(round(process_time / 60, 0))
        seconds = round(process_time % 60, 0)
        print(f'Overall playlist retrieval succeeded in {minutes} minutes and {seconds} seconds')
    else:
        print(f'Overall playlist retrieval succeeded in {process_time} seconds')
    return overall_playlist_df


def generate_network_edges(raw_output):
    """

    :param raw_output: Output from either get_playlist_track_info or multiple_playlist_track_info
    :return: DataFrame containing network edges (source and target), time interval, and edge weight
    """
    network_features = {'Source', 'Target', 'Time Interval'}
    network_edges = pd.DataFrame(columns=network_features)
    pd.options.display.width = 0

    # TODO: reformat added_at column to mm-dd-yyyy
    # c) song -> album
    song_df = raw_output[['song_id', 'album_id', 'added_at']].copy()
    song_df = song_df.rename(columns={'song_id': 'Source', 'album_id': 'Target', 'added_at': 'Time Interval'})
    song_df['Weight'] = 1.0  # initialize weight column as all songs are of equal weight
    network_edges = pd.concat([network_edges, song_df])  # add song_df to network_edges
    network_edges = network_edges.reindex(columns=['Source', 'Target', 'Time Interval', 'Weight'])

    album_weight_reference = song_df[['Target', 'Weight']]  # create df for counting weight in the album-artist and
    # artist-genre edges below
    album_weight_reference = album_weight_reference['Target'].value_counts()
    album_weight_reference = pd.DataFrame(album_weight_reference)
    album_weight_reference = album_weight_reference.reset_index()
    album_weight_reference = album_weight_reference.rename(columns={'Target': 'Weight', 'index': 'album_id'})

    # b) album -> artist
    raw_album_df = raw_output[['album_id', 'artist_id', 'added_at']].copy()
    reduced_albums = raw_album_df.drop_duplicates(subset=['album_id'])
    reduced_albums = pd.merge(reduced_albums, album_weight_reference, on='album_id', how='inner')  # adds album weights
    reduced_albums = reduced_albums.rename(
        columns={'album_id': 'Source', 'artist_id': 'Target', 'added_at': 'Time Interval'})
    network_edges = pd.concat([network_edges, reduced_albums])  # add reduced_albums to network_edges

    artist_weight_reference = reduced_albums[['Target', 'Weight']]  # create df for counting weight for artist-genre
    artist_weight_reference = pd.DataFrame(artist_weight_reference)
    artist_weight_reference = artist_weight_reference.rename(columns={'Target': 'Source'})
    artist_weight_reference = artist_weight_reference.groupby(['Source']).sum()  # sum album weights into artist weight
    artist_weight_reference = artist_weight_reference.reset_index()

    # a) artist -> genre
    raw_artist_df = raw_output[['artist', 'artist_id', 'added_at']].copy()  # copy only artist & id for new df
    reduced_artists = raw_artist_df.drop_duplicates(subset=['artist'])  # reduce to only uniques

    artist_ids = []  # extract artist ids for argument in spotipy artist function
    for index, row in reduced_artists.iterrows():
        artist_ids.extend([row['artist_id']])

    artist_genres = {}  # produce dictionary of artist id : genres
    for item in artist_ids:
        artist_genres[item] = auth.spotify.artist(item)['genres']

    pre_artist_df = []  # produce list of dictionaries for each artist id : genre combination
    for key, value in artist_genres.items():
        for genre in value:
            artist_genre_pair = {'artist_id': key, 'genre': genre}
            pre_artist_df.append(artist_genre_pair)

    artist_id_genre_df = pd.DataFrame(pre_artist_df)  # create dataframe using list of dictionaries made above
    artist_inner_join = pd.merge(reduced_artists, artist_id_genre_df, on='artist_id', how='inner')
    artist_inner_join = artist_inner_join.reindex(columns=['artist', 'genre', 'artist_id', 'added_at'])
    del artist_inner_join['artist']
    artist_inner_join = artist_inner_join.rename(columns={'artist_id': 'Source',
                                                          'genre': 'Target', 'added_at': 'Time Interval'})
    artist_inner_join = pd.merge(artist_inner_join, artist_weight_reference, on='Source', how='inner')  # adds artist
    # weights
    network_edges = pd.concat([network_edges, artist_inner_join])  # add inner_join to network_edges

    # network_edges = network_edges.reset_index(drop=True, inplace=True)

    return network_edges


def generate_network_nodes(raw_output, edge_output, get_art=True):
    """

    :param raw_output: Output from get_track_info or multiple_playlist_track_info
    :param edge_output: Output from generate_network_edges
    :param get_art: True to retrieve art hyperlink or download locally
    :return: Pandas DataFrame containing network nodes (ID, label, Song URI/genre link)
    """
    pd.options.display.width = 0
    edge_to_genre = edge_output[['Source', 'Target', 'Time Interval']].copy()  # create initial nodes df
    # interval_copy = network_nodes
    edge_to_genre = pd.concat([edge_to_genre['Source'], edge_to_genre['Target']])  # produced series from 2 dfs
    edge_to_genre = pd.DataFrame(edge_to_genre)  # convert back to df
    edge_to_genre = edge_to_genre.reset_index()
    del edge_to_genre['index']
    edge_to_genre.columns.values[0] = 'Id'  # renamed column based on index because it was being finicky
    edge_to_genre = edge_to_genre.drop_duplicates(subset=['Id'])
    edge_to_genre = edge_to_genre.reset_index()
    del edge_to_genre['index']

    # extract non-spotify ID genres into separate df
    row_list = []
    for index, row in edge_to_genre.iterrows():
        row_list.extend(row)
    genre_list = []
    for item in row_list:
        if item[0].isalpha():
            genre_list.append(item)
    genre_df = pd.DataFrame(genre_list)
    genre_df['Label'] = genre_df[0]
    genre_df.columns.values[0] = 'Id'

    # add EveryNoise link as genre URL attribute
    genre_url_list = []
    for index, row in genre_df.iterrows():
        genre = row['Id']
        genre = re.sub('[ \-&]', '', genre)  # removes [ -&] characters from genre name
        link = f'http://everynoise.com/engenremap-{genre}.html'
        genre_url_dict = {'Id': row['Id'], 'URL': link}
        genre_url_list.append(genre_url_dict)
    genre_urls = pd.DataFrame(genre_url_list)
    genre_df = pd.merge(genre_df, genre_urls, on='Id')

    # TODO all below is WIP for time interval
    # network_nodes = pd.merge(network_nodes, interval_copy, how='inner', on='Target')
    # del network_nodes['Source']

    # del interval_copy['Target']
    # interval_copy = interval_copy.rename(columns={'Source': 'Target'})

    # network_nodes = pd.merge(network_nodes, interval_copy, how='inner', on='Target')
    # network_nodes = network_nodes.drop_duplicates(subset=['Target'])

    # adding label for identification of spotify IDs
    songs = raw_output[['song_id', 'song', 'song_uri', 'preview_url']].copy()  # added song preview url
    songs = songs.rename(columns={'song_id': 'Id', 'song': 'Label', 'song_uri': 'URL', 'preview_url': 'Preview URL'})

    albums = raw_output[['album_id', 'album', 'album_uri']].copy()
    albums = albums.rename(columns={'album_id': 'Id', 'album': 'Label', 'album_uri': 'URL'})

    artists = raw_output[['artist_id', 'artist', 'artist_uri']].copy()
    artists = artists.rename(columns={'artist_id': 'Id', 'artist': 'Label', 'artist_uri': 'URL'})

    spotify_ids = pd.concat([songs, albums, artists])
    spotify_ids = spotify_ids.drop_duplicates(subset=['Id'])
    spotify_ids = spotify_ids.reset_index()
    del spotify_ids['index']

    network_nodes = pd.concat([spotify_ids, genre_df])
    network_nodes = network_nodes.reset_index()
    del network_nodes['index']

    if get_art:
        # downloads album arts and merges album art paths with the output dataframe for Gephi
        print('Store album arts locally or as hyperlink?')
        art_response = io_functions.user_input_parser(['local', 'link'])
        if art_response == 'local':
            download_bool = True
        else:
            download_bool = False
        art_path_df = album_art_path_append(raw_output=raw_output, download_bool=download_bool)
        network_nodes = pd.merge(network_nodes, art_path_df, on='Id', how='left')

    # print(network_nodes)
    return network_nodes


def album_art_path_append(raw_output, download_bool):
    """

    :param raw_output: Output from get_track_info or multiple_playlist_track_info
    :param download_bool: True to download artist/album images (also depends on "Associate album arts to albums only,
    or to both albums and songs?" prompt: 'both' response for album art and artist art.
    :return: Pandas DataFrame with song/artist/album ID and local path to art)
    """
    pd.options.display.width = 0

    print('Associate album arts to albums only, or to both albums and songs?')
    dl_choice = io_functions.user_input_parser(['album', 'both'])
    if dl_choice == 'album':
        album_img = raw_output[['album_id', 'art_link']].copy()
        album_img = album_img.rename(columns={'album_id': 'Id'})
        id_img = album_img

    else:
        artist_img = raw_output[['artist', 'artist_id']].copy()  # this path also downloads artist image
        artist_img = artist_img.drop_duplicates(subset=['artist_id'])
        artist_img_list = []

        for index, row in artist_img.iterrows():
            if row[0].isalpha and len(row) != 22:  # criteria to isolate artist_id rows from artist rows
                try:
                    artist_img_dict = {'Id': row['artist_id'], 'art_link': io_functions.get_artist_art(row)}
                    artist_img_list.append(artist_img_dict)
                except IndexError:  # handles in case no artist image available
                    pass

        artist_img_links = pd.DataFrame(artist_img_list)
        artist_img = artist_img.rename(columns={'artist_id': 'Id'})
        artist_img = pd.merge(artist_img, artist_img_links, on='Id')
        del artist_img['artist']

        song_img = raw_output[['song_id', 'art_link']].copy()
        song_img = song_img.rename(columns={'song_id': 'Id'})

        album_img = raw_output[['album_id', 'art_link']].copy()
        album_img = album_img.rename(columns={'album_id': 'Id'})

        id_img = pd.concat([song_img, album_img, artist_img])
        id_img = id_img.query('Id != "Various Artists"')  # gets rid of pesky Various Artists

    id_img = id_img.drop_duplicates(subset=['Id'])
    # adds .jpeg to end of URL. this actually breaks the link
    # for index, row in id_img.iterrows():
    #     row['art_link'] = row['art_link'].replace(row['art_link'], row['art_link']+'.jpeg')
    #     print(row['art_link'])

    art_retrieval_time = time.time()
    path_list = []
    if download_bool:
        try:
            os.mkdir('album_arts')  # tries to make new album art directory
        except FileExistsError:  # fails because already exists
            pass
        outer = tqdm(desc='Art download', unit='images', total=len(id_img), leave=True)
        os.chdir('album_arts')  # change directory here, not inside for loop. was causing an error
        for index, row in id_img.iterrows():
            path_dict = {}
            try:
                io_functions.art_download(spotify_id=row['Id'], url=row['art_link'])
            except AttributeError:
                pass  # occasionally get this error: AttributeError: 'NoneType' object has no attribute 'timeout'
                # not sure if that means data was not retrieved from the url or not

            path_dict['Id'] = row['Id']
            path_dict['image'] = ('album_arts/' + row['Id'] + '.jpg')  # added album art directory as root
            path_list.append(path_dict)
            outer.update(1)

        process_time = round(time.time() - art_retrieval_time, 2)
        if process_time > 60:  # prints minutes and seconds if process time longer than a minute
            minutes = int(round(process_time / 60, 0))
            seconds = round(process_time % 60, 0)
            print(f'Overall playlist retrieval succeeded in {minutes} minutes and {seconds} seconds')
        else:
            print(f'Overall playlist retrieval succeeded in {process_time} seconds')

        path_df = pd.DataFrame(path_list)
    else:
        id_img = id_img.rename(columns={'art_link': 'image'})  # does not download art
        path_df = id_img

    return path_df
