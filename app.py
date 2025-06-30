import os
import random
import urllib.parse
from typing import List

import openai
import pandas as pd
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SPOTIFY_SCOPE = (
    "user-top-read user-read-recently-played "
    "playlist-read-private playlist-modify-public playlist-modify-private"
)


def get_spotify_client() -> spotipy.Spotify | None:
    """Return an authenticated Spotify client or None if not authorised."""
    if "sp" in st.session_state:
        return st.session_state["sp"]

    oauth = SpotifyOAuth(
        scope=SPOTIFY_SCOPE,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        cache_path=".cache",
        show_dialog=True,
    )

    # Try cached token first
    token_info = oauth.get_cached_token()
    if token_info and not oauth.is_token_expired(token_info):
        sp = spotipy.Spotify(auth=token_info["access_token"])
        st.session_state["sp"] = sp
        return sp

    # Not authorised yet -> ask user to log in
    auth_url = oauth.get_authorize_url()
    st.sidebar.markdown("### Step 1: Authorise with Spotify")
    st.sidebar.markdown(f"[Click here to authorise]({auth_url})")

    redirect_response = st.sidebar.text_input(
        "Step 2: Paste the full redirect URL here once you've authorised:",
        key="redirect_url",
    )

    if redirect_response:
        code = oauth.parse_response_code(redirect_response)
        if code:
            token_info = oauth.get_access_token(code=code, as_dict=True)
            if token_info:
                sp = spotipy.Spotify(auth=token_info["access_token"])
                st.session_state["sp"] = sp
                st.sidebar.success("Spotify authentication successful!")
                return sp
        st.sidebar.error("Failed to parse token. Please try again.")
    return None


def analyse_user_profile(sp: spotipy.Spotify) -> str:
    """Return a textual analysis of the user's listening habits."""
    if "analysis" in st.session_state:
        return st.session_state["analysis"]

    # Fetch top artists and tracks
    top_artists = sp.current_user_top_artists(limit=20, time_range="medium_term")["items"]
    top_tracks = sp.current_user_top_tracks(limit=50, time_range="medium_term")["items"]

    genres = []
    for artist in top_artists:
        genres.extend(artist["genres"])
    genre_series = pd.Series(genres)
    top_genres = genre_series.value_counts().head(10).index.tolist()

    artist_names = [a["name"] for a in top_artists[:10]]
    track_names = [t["name"] + " by " + t["artists"][0]["name"] for t in top_tracks[:10]]

    summary = (
        "Here are some key observations about the user's Spotify profile:\n"
        f"Top artists: {', '.join(artist_names)}.\n"
        f"Most common genres: {', '.join(top_genres)}.\n"
        f"Example favourite tracks: {', '.join(track_names)}.\n"
    )

    st.session_state["analysis"] = summary
    return summary


def chat_interface(sp: spotipy.Spotify):
    st.header("💬 Chat about your music taste")

    analysis_text = analyse_user_profile(sp)

    if "messages" not in st.session_state:
        st.session_state.messages: List[dict] = [
            {
                "role": "system",
                "content": (
                    "You are a helpful and upbeat music expert. "
                    "The user is authenticated with Spotify. "
                    "Below is a summary of their listening habits which you can use as context.\n\n"
                    + analysis_text
                ),
            }
        ]

    # Display previous messages
    for msg in st.session_state.messages[1:]:  # skip system
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("ai").markdown(msg["content"])

    user_prompt = st.chat_input("Ask me anything about your music...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
            )
            reply = response.choices[0].message.content.strip()

        st.chat_message("ai").markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})


def generate_playlist(sp: spotipy.Spotify):
    st.header("🎵 Create a new playlist")

    prompt = st.text_input("Describe the vibe / theme (e.g. 'Upbeat indie roadtrip'): ")
    num_tracks = st.slider("Number of tracks", min_value=10, max_value=50, value=25)
    create_btn = st.button("Create playlist")

    if create_btn and prompt:
        with st.spinner("Generating playlist..."):
            # Use user's top artists and genres as seeds when possible
            top_artists = sp.current_user_top_artists(limit=5, time_range="medium_term")["items"]
            seed_artists = [a["id"] for a in top_artists[:5]]

            recommendations = sp.recommendations(
                seed_artists=seed_artists[:5],
                limit=num_tracks,
                target_danceability=None,
            )
            uris = [track["uri"] for track in recommendations["tracks"]]
            user_id = sp.me()["id"]
            playlist = sp.user_playlist_create(
                user=user_id,
                name=prompt,
                public=True,
                description=f"Generated with SpotChat: {prompt}",
            )
            sp.playlist_add_items(playlist_id=playlist["id"], items=uris)
            st.success(f"Playlist '{playlist['name']}' created successfully!")
            st.markdown(f"[Open in Spotify]({playlist['external_urls']['spotify']})")


# ----------------------- Streamlit Layout ----------------------------------

st.set_page_config(page_title="SpotChat", page_icon="🎧")

sp_client = get_spotify_client()

if sp_client:
    tab_chat, tab_create = st.tabs(["Chat", "Create Playlist"])
    with tab_chat:
        chat_interface(sp_client)
    with tab_create:
        generate_playlist(sp_client)
else:
    st.title("🎧 SpotChat — Spotify & AI")
    st.write(
        "Authenticate with Spotify from the **sidebar** to start chatting "
        "about your music and creating playlists powered by AI!"
    )