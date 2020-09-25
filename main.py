import analysis
import os
import glob
import io_functions

path = os.getcwd()
# save original file path
print('Analyze saved track library or playlists?')
search_type = io_functions.user_input_parser(['saved', 'playlist'])
global song_analysis_data
if search_type == 'playlist':
    while True:
        try:
            # TODO: restrict showing directory contents to xlsx files
            print(f'Contents of current directory: {glob.glob("*.xlsx")}')
            imported_file = input('Enter the name of the Excel file to import (without extension): ')
            song_analysis_data = analysis.multiple_playlist_track_info(imported_file + ".xlsx")
            break
        except FileNotFoundError:
            print(f'Excel file {imported_file}.xlsx not found. Please try again.')
elif search_type == 'saved':
    # song_analysis_data = analysis.saved_lib_results() # need to modify authorization for this to work
    exit()

network_edge_data = analysis.generate_network_edges(song_analysis_data)

# prompt user on whether they would like album arts to be downloaded because this can be
# a rather large download depending on the number of songs analyzed
print('Would you like to retrieve album arts?')
art_response = io_functions.user_input_parser(['yes', 'no'])
if art_response == 'yes':
    get_art_bool = True
    try:
        os.mkdir('../album_arts')  # tries to make new album art directory
    except FileExistsError:  # fails because already exists
        pass
else:
    get_art_bool = False
os.chdir(path=path)
network_node_data = analysis.generate_network_nodes(song_analysis_data, network_edge_data, get_art=get_art_bool)

# export dataframes
print("Enter your desired output file format.")
file_format = io_functions.user_input_parser(['xlsx', 'csv'])
file_name = input("Enter output file name: ")

os.chdir(path)
io_functions.playlist_export(song_analysis_data, file_name + '_audio_features', file_format)
io_functions.playlist_export(network_edge_data, file_name + '_edges', file_format)
io_functions.playlist_export(network_node_data, file_name + '_nodes', file_format)
