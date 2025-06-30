# Spotify Chat Playlist App

This Streamlit app lets you:

1. Authorise with Spotify.
2. Chat about your existing playlists and musical taste, powered by OpenAI.
3. Quickly generate new Spotify playlists based on your prompts.

---

## 1. Prerequisites

* Python 3.9+
* A Spotify **Developer Application** (needed for OAuth credentials).
* An OpenAI API key.

### Spotify App Setup
1. Go to <https://developer.spotify.com/dashboard> and create an application.
2. Note the **Client ID** and **Client Secret**.
3. Add a Redirect URI: `http://localhost:8501/` (or the URL where you will host Streamlit).

### Environment variables
Create a `.env` file in the project root (copy `.env.example` as a starting point):

```ini
SPOTIPY_CLIENT_ID="your_client_id"
SPOTIPY_CLIENT_SECRET="your_client_secret"
SPOTIPY_REDIRECT_URI="http://localhost:8501/"
OPENAI_API_KEY="sk-..."
```

> ❗ **Never commit real credentials to version control.**

## 2. Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Running the app

```bash
streamlit run app.py
```
Your browser will open automatically. Follow the on-screen instructions to authenticate with Spotify. Once authorised you can start chatting and creating playlists.

---

## 4. Features

### Chat about your music
The AI analyses your playlists, top tracks and recently played songs to identify trends (genres, moods, decades, etc.). Use natural language to ask questions like:

* "What genres do I listen to most?"
* "Recommend some 80s synth-pop based on my taste."
* "How energetic is my workout playlist?"

### Create new playlists
Enter a prompt such as "Chill acoustic coffeehouse vibes (30 tracks)" and the assistant will build a playlist for you, adding it directly to your Spotify account.

---

## 5. Troubleshooting

* If authentication fails, ensure your redirect URI in the Spotify dashboard **exactly** matches the one in `.env`.
* Remove the `.cache` file if you want to force re-authentication.

---

## 6. Licence

MIT