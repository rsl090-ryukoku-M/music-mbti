from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .diagnosis import compute_scores_from_selected_tracks, scores_to_type_code, describe_type, pick_sample_tracks_fake
from .models import DiagnosisResult


def _clamp_str(s: Any, max_len: int = 200) -> str:
    if s is None:
        return ""
    x = str(s)
    return x[:max_len]


def _itunes_search(term: str, limit: int = 20, country: str = "JP") -> List[Dict[str, Any]]:
    """
    iTunes Search API で楽曲検索して、フロントで使う形に整形して返す。
    """
    q = (term or "").strip()
    if not q:
        q = "J-POP"  # 空のときはおすすめとしてこれを返す（好みで変えてOK）

    params = {
        "term": q,
        "entity": "song",
        "limit": str(int(limit)),
        "country": country,
        "media": "music",
    }
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(params)

    with urllib.request.urlopen(url, timeout=10) as r:
        raw = r.read().decode("utf-8", errors="ignore")
    data = json.loads(raw)

    items: List[Dict[str, Any]] = []
    for it in data.get("results", []):
        track_id = it.get("trackId")
        title = it.get("trackName")
        artist = it.get("artistName")
        artwork = it.get("artworkUrl100")
        preview_url = it.get("previewUrl")
        external_url = it.get("trackViewUrl")

        if not track_id or not title or not artist:
            continue

        items.append(
            {
                "id": str(track_id),
                "title": _clamp_str(title, 120),
                "artist": _clamp_str(artist, 120),
                "artwork": _clamp_str(artwork, 300),
                "preview_url": _clamp_str(preview_url, 300),
                "external_url": _clamp_str(external_url, 300),
            }
        )
    return items


@require_GET
def tracks_search(request):
    """
    GET /api/tracks/search?q=...
    -> { items: Track[] }
    """
    q = request.GET.get("q", "")
    try:
        items = _itunes_search(q, limit=20, country="JP")
        return JsonResponse({"items": items})
    except Exception as e:
        return JsonResponse({"error": "search_failed", "detail": str(e)}, status=500)


@csrf_exempt
@require_POST
def diagnose_from_tracks(request):
    """
    POST /api/diagnose_from_tracks
    body: { tracks: [{id,title,artist,tempo,bright,electro,explore}, ...] }
    """
    if not request.user.is_authenticated:
        return JsonResponse({"error": "unauthorized"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "bad_json"}, status=400)

    tracks = payload.get("tracks")
    if not isinstance(tracks, list) or len(tracks) == 0:
        return JsonResponse({"error": "no_tracks"}, status=400)

    # 0..1 の特徴量を平均してスコア算出
    scores = compute_scores_from_selected_tracks(tracks)
    type_code = scores_to_type_code(scores)
    type_info = describe_type(type_code)

    # 代表曲（ダミーでもOK。将来 Spotify の track id に差し替えられる）
    sample_tracks = pick_sample_tracks_fake(type_code)
    sample_ids = [t["title"] for t in sample_tracks]

    # DB保存
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
