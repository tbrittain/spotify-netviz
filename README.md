# spotify-netviz

This project will prepare Spotify library data for use in network visualizations. In other words, this project was created to investigate the connectivity of a network from a user's Spotify library. 

This project is not used to visualize the network; rather, it simply prepares Spotify library network data for use in a program such as [Gephi]. 

Additionally, it will output Spotify [Audio Features] data for your own statistical analysis, if you are so inclined.

If you would like to see a live demo of what this project is capable of, you can check out [my library]. Note: I used Gephi for visualizing the network itself and [Gexf-js] for the webpage.

## Installation

You can either download the standalone executable (if you are on Windows), or the source code itself if you are not a fan of executables or are on OSX or Linux. If the latter, install the dependencies in requirements.txt and just run main.py -- and voilà!

## Preparation

This project is designed to access either your private/collaborative/public playlist data or Saved Tracks data (or a combination of both). If you are planning on only working with your Saved Tracks, you can skip to the next section.

If you are working with playlists, you must first obtain the ID of both the playlist creator and playlist itself for every playlist you plan to analyze. The easiest way to do this is by finding the playlist in your Spotify client and right clicking on the name of the creator/playlist > Share > Copy Spotify URI.

![alt text][playlisturi]

![alt text][useruri]

Once you have located both of these URIs, create a .xlsx spreadsheet with the following format:

| creator     |       playlist_id         |
| :---        |           ---:            |
| spotify     |   37i9dQZF1DX6ujZpAN0v9r  |
| spotify     |   37i9dQZF1DX6ALfRKlHn1t  |

This program supports as many playlists as you would like to include. Be sure to remove the "spotify:user:" or "spotify:playlist:" to isolate the ID for each of the above columns. Then, save that spreadsheet to the same directory as the executable/main.py.

## Execution

### Authorization and Song Retrieval

Upon running the program and selecting whether you are working with Saved Tracks/playlists/both, your browser will open for Spotify authorization. Simply sign in to Spotify and agree to the terms. That'll look something like this once you have signed in:

![alt text][authorize]

Upon accepting, the program will download song information from the specified track location(s). *Depending on the number of tracks to analyze, this step could take quite some time as the program typically averages around 20 tracks parsed per second.*

During this step, the program is performing 3 operations:
1. Compiling an array of general track information and Spotify Audio Features for each track
2. Taking the general track information to create an array of edges with direction from song &rarr; album, album &rarr; artist, and artist &rarr; genre
3. Creating an array of nodes (along with various attributes such as previews for songs, links to genres on [EveryNoise], Spotify URI for songs/albums/artists ,and optional album art images)

### Album Arts
*Images for this section TBA*
Afterwards, you will be prompted on whether to obtain album art data. 
If you select yes, album arts can either be saved locally or as the hyperlink itself. The local option will save the album art images to disk in an album_arts folder.

The next prompt is whether album arts should be associated with solely the album nodes or both albums and the album's songs. This choice determines which nodes receive an "image" attribute so that the art will can be viewed directly on the network graph. Based on whether you selected local download of arts or hyperlink, the image attribute will be either a relative file location (e.g. album_arts/image.jpg) or the hyperlink.

If you choose the "both" association option, it will additionally retrieve images for artists as well. The album only option does not currently have this feature.

*If you are saving the arts locally, this download will take slightly over double the amount of time that the song retrieval took, as the program typically averages around 8 arts downloaded per second.*

### Export

Finally, the program saves 3 separate .csv or .xlsx files for each of the arrays above:
1. Audio Features
2. Edges
3. Nodes

### Art resizing

One additional feature upon spreadsheet export is the ability to resize downloaded album arts. The original album art sizes are around 600x600 pixels for each file. 
If you select "yes" for this operation, the program creates an album_arts_resized/ folder and halves the dimensions of each of the downloaded images.

## Gephi Import

TBA

## Roadmap

Eventually I would like to add some more functionality to further releases including:
* More output formats for additional network visualization software if they do not support the current Edge and Node format (as this has only been tested with Gephi)
* Finishing Time Interval data for dynamic graphs (for observing music taste over time)
* Adjusting the algorithm for associating songs with artists. Currently does so through song &rarr; album &rarr; artist, but this does not take into account songs with 2+ artists

## License
[MIT]


[Gephi]: https://gephi.org/
[Audio Features]: https://developer.spotify.com/documentation/web-api/reference/tracks/get-several-audio-features/
[my library]: https://tbrittain.com/new-viz-library/
[Gexf-js]: https://github.com/raphv/gexf-js
[MIT]: https://choosealicense.com/licenses/mit/
[playlisturi]: https://tbrittain.com/images/readme/playlisturi.jpg "Copying playlist URI in Spotify client"
[useruri]: https://tbrittain.com/images/readme/useruri.jpg "Copying user URI in Spotify client"
[authorize]: https://tbrittain.com/images/readme/authorize.jpg "Spotify browser authentication"
[EveryNoise]: http://everynoise.com/
