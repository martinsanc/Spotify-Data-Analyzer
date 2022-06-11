import csv
import pandas as pd


DATA_PATH = "data/"

# ENTRY POINT

def fetch_user_playlist_tracks(sp, debug=False):
    # Fetch playlists
    if debug: print("Reading playlist data...", end='\t')
    playlists = fetch_playlists(sp)
    playlists.to_json("{}user_playlists.json".format(DATA_PATH), double_precision=5, indent=2)
    if debug: print("Done reading {} Rows".format(str(playlists.shape[0])))

    #Fetch tracks from playlist
    tracks = pd.DataFrame()
    for i, playlist in playlists.iterrows():
        if debug:
            if i > 3:
                continue
            print("\tReading playlist '{}' ({} tracks)...".format(playlist['name'], playlist['track_count']), end='\t')
        playlist_tracks = fetch_tracks_from_playlist(sp, playlist.uri)
        playlist_tracks['playlist'] = playlist['name']
        tracks = pd.concat([tracks, playlist_tracks])
        if debug: print("Done.")
    return tracks


# LOADING DATAFRAMES

def fetch_playlists(sp):
    results = sp.current_user_playlists()
    playlists = results['items']
    while results['next'] is not None:
        results = sp.next(results)
        playlists.extend(results['items'])
    playlist_list = []
    for i, playlist in enumerate(playlists):
        playlist_list.append(get_playlist_metadata(playlist))
    playlists = pd.DataFrame(playlist_list)
    return playlists

def fetch_tracks_from_playlist(sp, playlist_uri, audio_features=True, genres=True):
    results = sp.playlist_tracks(playlist_uri)
    tracks = results['items']
    while results['next'] is not None:
        results = sp.next(results)
        tracks.extend(results['items'])
    track_list = []
    for i, track in enumerate(tracks):
        if not track['is_local']:
            try:
                track = get_track_metadata(track)
                if audio_features:
                    audio_features = fetch_audio_features(sp, track['uri'])
                    track = track | audio_features
                if genres:
                    genres = fetch_genres(sp, track['artist_uri'], track['album_uri'])
                    track = track | genres
                track_list.append(track)
            except TypeError:
                continue
    tracks = pd.DataFrame(track_list)
    return tracks

def fetch_audio_features(sp, track_uri):
    results = sp.audio_features(track_uri)
    audio_features = {
        'track_uri': track_uri,
        'danceability': results[0]['danceability'],
        'energy': results[0]['energy'],
        'key': results[0]['key'],
        'loudness': results[0]['loudness'],
        'mode': results[0]['mode'],
        'speechiness': results[0]['speechiness'],
        'acousticness': results[0]['acousticness'],
        'instrumentalness': results[0]['instrumentalness'],
        'liveness': results[0]['liveness'],
        'valence': results[0]['valence'],
        'tempo': results[0]['tempo'],
        'duration_ms': results[0]['duration_ms'],
        'time_signature': results[0]['time_signature']
    }
    return audio_features

def fetch_genres(sp, artist_uri, album_uri):
    results_artist = sp.artist(artist_uri)
    results_album = sp.album(album_uri)
    genres = results_album['genres'] + results_artist['genres']
    return {'genres': genres}


# GET METADATA

def get_playlist_metadata(playlist):
    playlist = {'name': playlist['name'],
                'id': playlist['id'],
                'uri': playlist['uri'],
                'description': playlist['description'],
                'collaborative': playlist['collaborative'],
                'public': playlist['public'],
                'owner_name': playlist['owner']['display_name'],
                'owner_id': playlist['owner']['id'],
                'owner_uri': playlist['owner']['uri'],
                'track_count': playlist['tracks']['total']}
    return playlist

def get_track_metadata(track):
    track = {'name': track['track']['name'],
             'id': track['track']['id'],
             'uri': track['track']['uri'],
             'popularity': track['track']['popularity'],
             'artist_name': track['track']['artists'][0]['name'],
             'artist_id': track['track']['artists'][0]['id'],
             'artist_uri': track['track']['artists'][0]['uri'],
             'album_name': track['track']['album']['name'],
             'album_id': track['track']['album']['id'],
             'album_uri': track['track']['album']['uri'],
             'release_date': track['track']['album']['release_date'],
             'duration_ms': track['track']['duration_ms'],
             'image_url': track['track']['album']['images'][0]['url']}
    return track