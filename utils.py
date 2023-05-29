import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler
from flask import session

# load the env file
load_dotenv()

# Determine the current environment
env = os.getenv("FLASK_ENV", "development")

# Determine the parent directory
parent_directory = os.path.expanduser("~/Desktop/flask_deploy")

# Create a dedicated folder for your application's cache
cache_file = os.path.join(parent_directory, "cache.json")

# Create the cache handler with the parent directory folder
cache_handler = CacheFileHandler(cache_file)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Scope for the required permissions
scope = "user-library-read user-top-read user-read-recently-played"


# Set the redirect URI based on the environment
if env == "development":
    redirect_uri = "http://localhost:5000/callback"
else:
    redirect_uri = "https://spotifyanalytics.onrender.com/callback"

# Create SpotifyOAuth instance
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
)


# get the access token
def get_access_token():
    if "access_token" in session:
        return session["access_token"]

    try:
        token_info = sp_oauth.validate_token(sp_oauth.cache_handler.get_cached_token())
        if token_info is None:
            # No cached token found, obtain a new one
            auth_url = sp_oauth.get_authorize_url()
            return f'<p>Please <a href="{auth_url}">authorize</a> the application.</p>'

        access_token = token_info["access_token"]
        session["access_token"] = access_token  # Store access token in the session

        return access_token

    except spotipy.SpotifyException as e:
        error_message = "An error occurred while retrieving the access token."
        print(f"Exception: {str(e)}")
        return error_message


def get_popularity_group(popularity):
    if popularity > 80:
        return "superstar"
    elif popularity >= 70:
        return "well_known"
    elif popularity >= 60:
        return "known"
    elif popularity >= 50:
        return "moderately_known"
    else:
        return "up_and_coming"


def get_top_track(artist_id):
    access_token = get_access_token()  # Replace with your access token retrieval logic

    sp = spotipy.Spotify(auth=access_token)
    top_tracks = sp.artist_top_tracks(artist_id)

    if top_tracks and "tracks" in top_tracks:
        tracks = top_tracks["tracks"]
        if tracks:
            top_track = tracks[0]
            track_name = top_track["name"]
            album = top_track["album"]["name"]
            track_url = top_track["external_urls"]["spotify"]
            preview_url = top_track["preview_url"]
            return {
                "Track_Name": track_name,
                "Album": album,
                "Track_URL": track_url,
                "Preview_URL": preview_url,
            }

    return None


def get_top_artists(time_range, limit=6):
    access_token = get_access_token()

    sp = spotipy.Spotify(auth=access_token)
    results = sp.current_user_top_artists(time_range=time_range, limit=limit)
    top_artists = results["items"]

    top_artist_list = []
    for i, artist in enumerate(top_artists):
        artist_name = artist["name"]
        artist_image = artist["images"][0]["url"] if artist["images"] else None
        popularity = artist["popularity"]
        top_track = get_top_track(artist["id"])

        # Grouping popularity into categories
        popularity_group = get_popularity_group(popularity)

        top_artist_list.append(
            {
                "Artist_name": artist_name,
                "Artist_image": artist_image,
                "Popularity": popularity,
                "Popularity_group": popularity_group,
                "Top_track": top_track,
            }
        )

    return top_artist_list


def userProfile():
    access_token = get_access_token()
    sp = spotipy.Spotify(auth=access_token)
    user_data = sp.current_user()
    display_name = user_data["display_name"]
    profile_image = user_data["images"][0]["url"] if user_data["images"] else None
    return {"display_name": display_name, "profile_image": profile_image}
