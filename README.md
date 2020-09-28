# spotify-netviz
Preparation of Spotify library data for use in network visualizations. In other words, this project was created to investigate the connectivity of a network from a user's Spotify library. 
This project is not used to visualize the network; rather, it simply prepares Spotify library network data for use in a program such as [Gephi]. Additionally, it will output Spotify [Audio Features] data for your own statistical analysis, if you are so inclined.
If you would like to see a live demo of what this project is capable of, you can check out [my library]. Note: I used Gephi for visualizing the network itself and [Gexf-js] for the webpage.

## Preparation
This project is designed to access either your private/collaborative/public playlist data or Saved Tracks data (or a combination of both). If you are planning on only working with your Saved Tracks, you can skip to the next section.
If you are working with playlists, you must first obtain the ID of both the playlist creator and playlist itself for every playlist you plan to analyze. The easiest way to do this is by finding the playlist in your Spotify client and right clicking on the name of the creator/playlist > Share > Copy Spotify URI.
![alt text][playlisturi]
![alt text][useruri]
Once you have both of these URIs, create a .xlsx spreadsheet with the following format:

| creator     |       playlist_uri        |
| :---        |           ---:            |
| spotify     |   37i9dQZF1DX6ujZpAN0v9r  |
| spotify     |   37i9dQZF1DX6ALfRKlHn1t  |

This program supports as many playlists as you would like to include. Be sure to remove the "spotify:user:" or "spotify:playlist:" to isolate the ID for each of the above columns. Then, save that spreadsheet to the same directory as the executable/main.py.

## Installation
You can either download the standalone executable (if you are on Windows), or the source code itself if you are not a fan of executables or are on OSX or Linux. If the latter, install the dependencies and just run main.py -- and voilà!

## Roadmap
Eventually I would like to add some more functionality to further releases including:
* More output formats for additional network visualization software
* Finishing Time Interval data for dynamic graphs (for checking out music taste over time)

## License
[MIT]


[Gephi]: https://gephi.org/
[Audio Features]: https://developer.spotify.com/documentation/web-api/reference/tracks/get-several-audio-features/
[my library]: https://tbrittain.com/new-viz-library/
[Gexf-js]: https://github.com/raphv/gexf-js
[MIT]: https://choosealicense.com/licenses/mit/
[playlisturi]: https://tbrittain.com/images/readme/playlisturi.jpg "Copying playlist URI in Spotify client"
[useruri]: https://tbrittain.com/images/readme/useruri.jpg "Copying user URI in Spotify client"
