from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import base64
import requests
from datetime import datetime, timedelta, timezone

SPOTIFY_ACCOUNTS_BASE = "https://accounts.spotify.com"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

@dataclass
class SpotifyTokens:
    access_token: str
    refresh_token: str
    expires_at: datetime  # UTC

def _basic_auth_header(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")

def exchange_code_for_tokens(client_id: str, client_secret: str, redirect_uri: str, code: str) -> SpotifyTokens:
    url = f"{SPOTIFY_ACCOUNTS_BASE}/api/token"
    headers = {"Authorization": _basic_auth_header(client_id, client_secret)}
    data = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri}
    r = requests.post(url, headers=headers, data=data, timeout=15)
    r.raise_for_status()
    j = r.json()

    expires_in = int(j["expires_in"])
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 30)

    return SpotifyTokens(
        access_token=j["access_token"],
        refresh_token=j.get("refresh_token", ""),
        expires_at=expires_at,
    )

def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> SpotifyTokens:
    url = f"{SPOTIFY_ACCOUNTS_BASE}/api/token"
    headers = {"Authorization": _basic_auth_header(client_id, client_secret)}
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    r = requests.post(url, headers=headers, data=data, timeout=15)
    r.raise_for_status()
    j = r.json()

    expires_in = int(j["expires_in"])
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 30)

    return SpotifyTokens(
        access_token=j["access_token"],
        refresh_token=refresh_token,
        expires_at=expires_at,
    )

def api_get(access_token: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{SPOTIFY_API_BASE}{path}"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def get_me(access_token: str) -> Dict[str, Any]:
    return api_get(access_token, "/me")

def get_top_tracks(access_token: str, limit: int = 50, time_range: str = "medium_term") -> Dict[str, Any]:
    return api_get(access_token, "/me/top/tracks", params={"limit": limit, "time_range": time_range})

def get_audio_features(access_token: str, track_ids: List[str]) -> Dict[str, Any]:
    ids = ",".join(track_ids)  # 最大100
    return api_get(access_token, "/audio-features", params={"ids": ids})

