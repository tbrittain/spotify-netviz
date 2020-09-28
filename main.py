import analysis
import os
import glob
import io_functions
import resize
# import pyfiglet
import time
from banner import banner

# ascii_banner = pyfiglet.figlet_format("Spotify Netviz", font="kban")
print("\n")
banner()
time.sleep(2)
print("Please see the readme for documentation"
      "\nCopyright (c) 2020 Trey Brittain"
      "\ntbrittain.com"
      "\nRelease v0.1"
      "\n")

path = os.getcwd()
# save original file path

print('Analyze saved track library (Liked Songs) or playlists?'
      '\nIf analyzing playlists, please refer to readme for setup')
search_type = io_functions.user_input_parser(['saved', 'playlist', 'both'])
global song_analysis_data
if search_type == 'playlist' or search_type == 'both':
    while True:
        try:
            print(f'Contents of current directory: {glob.glob("*.xlsx")}')
            imported_file = input('Enter the name of the Excel file to import (without extension): ')
            if search_type == 'both':
                saved_library_search = True
                song_analysis_data = analysis.multiple_playlist_track_info(imported_file + ".xlsx",
                                                                           saved_library=saved_library_search)
            else:
                song_analysis_data = analysis.multiple_playlist_track_info(imported_file + ".xlsx")
            break
        except FileNotFoundError:
            print(f'Excel file {imported_file}.xlsx not found. Please try again.')
elif search_type == 'saved':
    song_analysis_data = analysis.saved_lib_results()
    song_analysis_data = analysis.get_track_info(method='saved', data=song_analysis_data)

network_edge_data = analysis.generate_network_edges(song_analysis_data)

# prompt user on whether they would like album arts to be downloaded because this can be
# a rather large download depending on the number of songs analyzed
print('\nWould you like to retrieve album arts?')
art_response = io_functions.user_input_parser(['yes', 'no'])
if art_response == 'yes':
    get_art_bool = True
else:
    get_art_bool = False
os.chdir(path=path)
network_node_data = analysis.generate_network_nodes(song_analysis_data, network_edge_data, get_art=get_art_bool)

# export dataframes
print("\nEnter your desired output file format.")
file_format = io_functions.user_input_parser(['xlsx', 'csv'])
file_name = input("Enter output file name: ")

os.chdir(path)
io_functions.playlist_export(song_analysis_data, file_name + '_audio_features', file_format)
io_functions.playlist_export(network_edge_data, file_name + '_edges', file_format)
io_functions.playlist_export(network_node_data, file_name + '_nodes', file_format)

if get_art_bool:
    print(
        '\nWould you like to resize album arts to half width/height? '
        '\nTheir current average dimensions are around 600x600 pixels'
        '\nResizing would reduce the individual file size substantially.')
    resize_response = io_functions.user_input_parser(['yes', 'no'])
    if resize_response == 'yes':
        resize.resize_arts()
print('\nAll operations complete.')
time.sleep(3)
