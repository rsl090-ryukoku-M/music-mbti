from __future__ import annotations

import os
import secrets
import hashlib
from datetime import datetime, timezone

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import SpotifyAccount, DiagnosisResult
from .spotify import (
    exchange_code_for_tokens,
    refresh_access_token,
    get_me,
    get_top_tracks,
    get_audio_features,
)
from .diagnosis import (
    compute_scores,
    scores_to_type_code,
    pick_sample_tracks,
    describe_type,
    pick_sample_tracks_fake,
)


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def seeded_scores(username: str) -> dict[str, float]:
    """
    ユーザー名から決定的にスコアを生成（同じユーザーは常に同じ結果）。
    0.15〜0.85程度に収めて極端さを避ける。
    """
    h = hashlib.sha256(username.encode("utf-8")).digest()
    vals = [h[i] / 255.0 for i in range(4)]
    vals = [0.15 + v * 0.7 for v in vals]
    return {
        "energy_score": round(vals[0], 2),
        "mood_score": round(vals[1], 2),
        "texture_score": round(vals[2], 2),
        "explore_score": round(vals[3], 2),
    }


# -------------------------
# Spotify OAuth
# -------------------------
@require_GET
def spotify_connect_url(request):
    client_id = _env("SPOTIFY_CLIENT_ID")
    redirect_uri = _env("SPOTIFY_REDIRECT_URI")
    if not client_id or not redirect_uri:
        return HttpResponseBadRequest("Missing SPOTIFY_CLIENT_ID or SPOTIFY_REDIRECT_URI")

    state = secrets.token_urlsafe(16)
    request.session["spotify_oauth_state"] = state

    scope = "user-top-read"
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&scope={scope}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )
    return JsonResponse({"auth_url": auth_url})


@require_GET
def spotify_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    saved_state = request.session.get("spotify_oauth_state")
    if not code or not state or state != saved_state:
        return HttpResponseBadRequest("Invalid OAuth state/code")

    client_id = _env("SPOTIFY_CLIENT_ID")
    client_secret = _env("SPOTIFY_CLIENT_SECRET")
    redirect_uri = _env("SPOTIFY_REDIRECT_URI")
    frontend_origin = _env("FRONTEND_ORIGIN", "http://localhost:3000")

    tokens = exchange_code_for_tokens(client_id, client_secret, redirect_uri, code)
    me = get_me(tokens.access_token)

    spotify_user_id = me["id"]
    username = f"sp_{spotify_user_id}"
    display_name = me.get("display_name") or username

    user, _ = User.objects.get_or_create(
        username=username,
        defaults={"first_name": display_name},
    )
    user.set_unusable_password()
    user.save()

    acc, created = SpotifyAccount.objects.get_or_create(
        spotify_user_id=spotify_user_id,
        defaults={
            "user": user,
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_expires_at": tokens.expires_at,
        },
    )

    if not created:
        acc.user = user
        acc.access_token = tokens.access_token
        if tokens.refresh_token:
            acc.refresh_token = tokens.refresh_token
        acc.token_expires_at = tokens.expires_at
        acc.save()

    login(request, user)
    return redirect(f"{frontend_origin}/diagnosis")


def _ensure_fresh_token(acc: SpotifyAccount) -> SpotifyAccount:
    now = datetime.now(timezone.utc)
    if acc.token_expires_at <= now:
        tokens = refresh_access_token(
            _env("SPOTIFY_CLIENT_ID"),
            _env("SPOTIFY_CLIENT_SECRET"),
            acc.refresh_token,
        )
        acc.access_token = tokens.access_token
        acc.token_expires_at = tokens.expires_at
        acc.save()
    return acc


# -------------------------
# Dev login (cookie確保)
# -------------------------
@csrf_exempt
@require_GET
def fake_login(request):
    user, _ = User.objects.get_or_create(
        username="dev_user",
        defaults={"first_name": "Dev User"},
    )
    user.set_unusable_password()
    user.save()
    login(request, user)
    return JsonResponse({"ok": True, "username": user.username})


# -------------------------
# Diagnose (Spotifyが無い時はseedダミーで進める)
# -------------------------
@csrf_exempt
@require_POST
def diagnose(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "unauthorized"}, status=401)

    # Spotify未接続（または停止中）は seed でダミー診断
    try:
        # ※ related_name が "spotify" の前提
        acc = request.user.spotify
        spotify_connected = True
    except SpotifyAccount.DoesNotExist:
        spotify_connected = False
        acc = None

    if not spotify_connected:
        scores = seeded_scores(request.user.username)
        type_code = scores_to_type_code(scores)
        type_info = describe_type(type_code)
        sample_tracks = pick_sample_tracks_fake(type_code)
        sample_ids = [t["title"] for t in sample_tracks]  # DBはとりあえずタイトル

        DiagnosisResult.objects.create(
            user=request.user,
            energy_score=scores["energy_score"],
            mood_score=scores["mood_score"],
            texture_score=scores["texture_score"],
            explore_score=scores["explore_score"],
            type_code=type_code,
            sample_track_ids=sample_ids,
        )

        return JsonResponse(
            {
                "username": request.user.username,
                "type_code": type_code,
                "type_info": type_info,
                "scores": scores,
                "sample_track_ids": sample_ids,
                "sample_tracks": sample_tracks,
                "result_path": f"/result/{request.user.username}",
            }
        )

    # --- ここからSpotify本番（復活したら自動で使われる） ---
    acc = _ensure_fresh_token(acc)

    top = get_top_tracks(acc.access_token, limit=50, time_range="medium_term")
    items = top.get("items", [])
    track_ids = [t["id"] for t in items if t.get("id")]

    feats = get_audio_features(acc.access_token, track_ids).get("audio_features", [])

    scores = compute_scores(items, feats)
    type_code = scores_to_type_code(scores)
    type_info = describe_type(type_code)

    # sample_track_ids は Spotify の track id
    sample_ids = pick_sample_tracks(items, feats, type_code)

    DiagnosisResult.objects.create(
        user=request.user,
        energy_score=scores["energy_score"],
        mood_score=scores["mood_score"],
        texture_score=scores["texture_score"],
        explore_score=scores["explore_score"],
        type_code=type_code,
        sample_track_ids=sample_ids,
    )

    # ここでは “曲詳細” までは返さない（将来拡張）
    return JsonResponse(
        {
            "username": request.user.username,
            "type_code": type_code,
            "type_info": type_info,
            "scores": scores,
            "sample_track_ids": sample_ids,
            "sample_tracks": [],  # 後で Spotify track detail を引いて埋められる
            "result_path": f"/result/{request.user.username}",
        }
    )


# -------------------------
# Result JSON
# -------------------------
@require_GET
def result_json(request, username: str):
    user = User.objects.filter(username=username).first()
    if not user:
        return JsonResponse({"error": "not_found"}, status=404)

    latest = user.diagnoses.order_by("-computed_at").first()
    if not latest:
        return JsonResponse({"error": "no_result"}, status=404)

    return JsonResponse(
        {
            "username": user.username,
            "display_name": user.first_name or user.username,
            "computed_at": latest.computed_at.isoformat(),
            "type_code": latest.type_code,
            "type_info": describe_type(latest.type_code),
            "scores": {
                "energy": latest.energy_score,
                "mood": latest.mood_score,
                "texture": latest.texture_score,
                "explore": latest.explore_score,
            },
            "sample_track_ids": latest.sample_track_ids,
            "sample_tracks": pick_sample_tracks_fake(latest.type_code),
        }
    )
