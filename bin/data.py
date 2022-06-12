import csv
import pandas as pd


DATA_PATH = "data/"

# FETCH DATA ENTRY POINTS

def fetch_user_playlist_tracks(sp, debug=False):
    # Fetch playlists
    if debug: print("Reading playlist data...", end='\t')
    playlists = fetch_playlists(sp)
    if debug: print("Done reading {} playlists.".format(str(playlists.shape[0])))

    #Fetch tracks from playlist
    tracks = pd.DataFrame()
    for i, playlist in playlists.iterrows():
        if debug:
            #if i > 2: continue
            print("\tReading playlist '{}' ({} tracks)...".format(playlist['name'], playlist['track_count']), end='\t')
        playlist_tracks = fetch_tracks_from_playlist(sp, playlist.uri)
        playlist_tracks['playlist'] = playlist['name']
        tracks = pd.concat([tracks, playlist_tracks])
        if debug: print("Done.")
    save_tracks(tracks, "playlist")

def fetch_user_top_tracks(sp, debug=False):
    if debug: print("Fetching top tracks...", end='\t')
    ranges = ['short_term', 'medium_term', 'long_term']
    top_tracks = pd.DataFrame()
    for r in ranges:
        tracks = fetch_top_tracks(sp, r)
        top_tracks = pd.concat([top_tracks, tracks])
    save_tracks(top_tracks, "toptracks")
    if debug: print("Done.")


# FETCH DATA

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

def fetch_top_tracks(sp, time_range, audio_features=True, genres=True):
    results = sp.current_user_top_tracks(time_range=time_range)
    top_tracks = results['items']
    while results['next'] is not None:
        results = sp.next(results)
        top_tracks.extend(results['items'])
    track_list = []
    for i, track in enumerate(top_tracks):
        if not track['is_local']:
            try:
                track = get_track_metadata(track)
                track['rank'] = i+1
                track['time_range'] = time_range
                if audio_features:
                    audio_features = fetch_audio_features(sp, track['uri'])
                    track = track | audio_features
                if genres:
                    genres = fetch_genres(sp, track['artist_uri'], track['album_uri'])
                    track = track | genres
                track_list.append(track)
            except TypeError:
                continue
    top_tracks = pd.DataFrame(track_list)
    return top_tracks
    
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
                track = get_track_metadata(track['track'])
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
    track = {'name': track['name'],
             'id': track['id'],
             'uri': track['uri'],
             'popularity': track['popularity'],
             'artist_name': track['artists'][0]['name'],
             'artist_id': track['artists'][0]['id'],
             'artist_uri': track['artists'][0]['uri'],
             'album_name': track['album']['name'],
             'album_id': track['album']['id'],
             'album_uri': track['album']['uri'],
             'release_date': track['album']['release_date'],
             'duration_ms': track['duration_ms'],
             'image_url': track['album']['images'][0]['url']}
    return track


# FILE MANAGEMENT

def save_tracks(tracks, preffix, genres=True):
    if genres:
        genre_list = []
        for i, track in tracks.iterrows():
            for g in track['genres']:
                if g is not None:
                    genre_list.append({'track_id': track['id'],
                                       'genre': g})
        genre_list = pd.DataFrame(genre_list)
        genre_list.to_csv("{}{}_genres.csv".format(DATA_PATH, preffix))
    del(tracks['genres'])
    tracks.to_csv("{}{}_tracks.csv".format(DATA_PATH, preffix), encoding='utf-8', index=False)
    
