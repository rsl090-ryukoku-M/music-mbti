from __future__ import annotations

from typing import Any, Dict, List


# -------------------------
# utils
# -------------------------
def clamp01(x: float) -> float:
    try:
        v = float(x)
    except Exception:
        return 0.0
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


# -------------------------
# Spotify 版（audio_features を使う）
# -------------------------
def compute_scores(
    top_tracks_items: List[Dict[str, Any]],
    audio_features_list: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Spotifyの top_tracks + audio_features から4スコア(0..1)を算出する。
    - energy_score: energy/danceability/tempo
    - mood_score: valence
    - texture_score: acousticness/instrumentalness（生寄りほど高い）
    - explore_score: 人気が低い+アーティスト多様性（探索ほど高い）
    """
    feats_by_id = {f["id"]: f for f in audio_features_list if f and f.get("id")}

    energy_terms: List[float] = []
    mood_terms: List[float] = []
    texture_terms: List[float] = []
    pop_terms: List[float] = []
    artist_ids: List[str] = []

    for t in top_tracks_items:
        tid = t.get("id")
        f = feats_by_id.get(tid)
        if not tid or not f:
            continue

        tempo = float(f.get("tempo") or 0.0)
        # tempo を 60..180 BPM の範囲で 0..1 に正規化（雑でOK）
        tempo_norm = clamp01((tempo - 60.0) / 120.0)

        energy = float(f.get("energy") or 0.0)
        dance = float(f.get("danceability") or 0.0)
        valence = float(f.get("valence") or 0.0)

        acoustic = float(f.get("acousticness") or 0.0)
        instr = float(f.get("instrumentalness") or 0.0)

        popularity = float(t.get("popularity") or 0.0) / 100.0

        energy_terms.append(0.45 * energy + 0.35 * dance + 0.20 * tempo_norm)
        mood_terms.append(valence)
        texture_terms.append(0.60 * acoustic + 0.40 * instr)
        pop_terms.append(popularity)

        for a in t.get("artists", []):
            aid = a.get("id")
            if aid:
                artist_ids.append(aid)

    n = max(1, len(energy_terms))
    energy_score = sum(energy_terms) / n
    mood_score = sum(mood_terms) / n
    texture_score = sum(texture_terms) / n

    # explore: 人気が低いほど探索、＋アーティスト多様性
    explore_base = 1.0 - (sum(pop_terms) / max(1, len(pop_terms)))
    # top_tracks 50件想定
    unique_artists_ratio = len(set(artist_ids)) / 50.0
    explore_score = clamp01(explore_base * 0.8 + unique_artists_ratio * 0.2)

    return {
        "energy_score": float(clamp01(energy_score)),
        "mood_score": float(clamp01(mood_score)),
        "texture_score": float(clamp01(texture_score)),
        "explore_score": float(clamp01(explore_score)),
    }


def scores_to_type_code(s: Dict[str, float]) -> str:
    """
    4スコアからタイプコード（AbcD みたいな 4文字）を作る。
    A/a: 動/静（energy）
    B/b: 明/影（mood）
    C/c: 生/電（texture） ※ texture高い=生寄り
    D/d: 探索/定番（explore）
    """
    A = "A" if s.get("energy_score", 0.0) >= 0.55 else "a"
    B = "B" if s.get("mood_score", 0.0) >= 0.52 else "b"
    C = "C" if s.get("texture_score", 0.0) >= 0.50 else "c"
    D = "D" if s.get("explore_score", 0.0) >= 0.50 else "d"
    return f"{A}{B}{C}{D}"


def pick_sample_tracks(
    top_tracks_items: List[Dict[str, Any]],
    audio_features_list: List[Dict[str, Any]],
    type_code: str,
) -> List[str]:
    """
    Spotifyの曲IDを3曲選ぶ（適当でOK）。
    - 1曲目: energy高め
    - 2曲目: moodに合わせて valence
    - 3曲目: textureに合わせて acousticness
    """
    feats_by_id = {f["id"]: f for f in audio_features_list if f and f.get("id")}

    want_bright = type_code[1] == "B"  # 明るいなら valence 高い曲
    want_acoustic = type_code[2] == "C"  # 生なら acousticness 高い曲

    scored: List[tuple[str, Dict[str, Any]]] = []
    for t in top_tracks_items:
        tid = t.get("id")
        f = feats_by_id.get(tid)
        if tid and f:
            scored.append((tid, f))

    def safe(v: Any) -> float:
        try:
            return float(v or 0.0)
        except Exception:
            return 0.0

    by_energy = sorted(scored, key=lambda x: safe(x[1].get("energy")), reverse=True)

    # want_bright=True => valence高い順（reverse=True）
    by_valence = sorted(scored, key=lambda x: safe(x[1].get("valence")), reverse=want_bright)

    by_acoustic = sorted(scored, key=lambda x: safe(x[1].get("acousticness")), reverse=want_acoustic)

    picks: List[str] = []
    for lst in (by_energy, by_valence, by_acoustic):
        for tid, _ in lst:
            if tid not in picks:
                picks.append(tid)
                break
    return picks[:3]


# -------------------------
# 手動選択版（スライダー値を使う）
# -------------------------
def compute_scores_from_selected_tracks(tracks: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    フロントから送られる各曲の特徴量(0..1)を平均して、4スコアにする。
    入力例（1曲）:
      {"tempo":0.8,"bright":0.2,"electro":0.7,"explore":0.6}

    ここでは、
      tempo   -> energy_score
      bright  -> mood_score
      electro -> texture_score（※electro=電子寄りなので、生寄りに反転したい場合は 1-electro にする）
      explore -> explore_score
    """
    if not tracks:
        return {
            "energy_score": 0.5,
            "mood_score": 0.5,
            "texture_score": 0.5,
            "explore_score": 0.5,
        }

    tempos: List[float] = []
    brights: List[float] = []
    electros: List[float] = []
    explores: List[float] = []

    for t in tracks:
        tempos.append(clamp01(t.get("tempo", 0.5)))
        brights.append(clamp01(t.get("bright", 0.5)))
        electros.append(clamp01(t.get("electro", 0.5)))
        explores.append(clamp01(t.get("explore", 0.5)))

    n = max(1, len(tracks))

    # 重要：type_code の C/c は「texture高い=生寄り」
    # フロントの electro は「電子寄り」なので、生寄りにするなら反転が自然
    texture_score = 1.0 - (sum(electros) / n)

    return {
        "energy_score": sum(tempos) / n,
        "mood_score": sum(brights) / n,
        "texture_score": clamp01(texture_score),
        "explore_score": sum(explores) / n,
    }


# -------------------------
# 表示用（フロント表示/OGP用）
# -------------------------
def describe_type(type_code: str) -> Dict[str, Any]:
    """
    type_code から表示用情報を返す（フロント表示/OGP用）。
    差し替え前提でOK。
    """
    axes = {
        "axis1": "動" if type_code[0] == "A" else "静",
        "axis2": "光" if type_code[1] == "B" else "影",
        "axis3": "生" if type_code[2] == "C" else "電",
        "axis4": "探索" if type_code[3] == "D" else "定番",
    }

    presets = {
        "AbcD": {
            "name": "夜更かしドライブタイプ",
            "tagline": "暗めで速い。電子寄りで探索好き。",
        },
        "AbCD": {
            "name": "夜更かしインディタイプ",
            "tagline": "暗めで速い。生音寄りで探索好き。",
        },
    }

    base = presets.get(
        type_code,
        {"name": f"Type {type_code}", "tagline": "あなたの音楽の傾向を表すタイプ。"},
    )

    return {
        "name": base["name"],
        "tagline": base["tagline"],
        "axes": axes,
    }


def pick_sample_tracks_fake(type_code: str) -> List[Dict[str, str]]:
    """
    Spotifyが無い時の“それっぽい代表曲”を返す。
    type_codeごとに固定なので、シェアしてもブレない。
    """
    catalog: Dict[str, List[Dict[str, str]]] = {
        "AbCD": [
            {"title": "Midnight Loop", "artist": "Neon Taxi", "note": "夜の高速、低音が気持ちいい"},
            {"title": "Shadow Sprint", "artist": "City Pulse", "note": "暗め×速め、集中スイッチ"},
            {"title": "Analog Rain", "artist": "Blue Static", "note": "冷たい空気、ドライブ向け"},
        ],
        "AbcD": [
            {"title": "Late Night Drive", "artist": "Pastel FM", "note": "暗め電子、探索モード"},
            {"title": "Tunnel Lights", "artist": "Noon Runner", "note": "一定のビートが心地いい"},
            {"title": "Quiet Accel", "artist": "Soda Wave", "note": "静かに加速する感じ"},
        ],
    }

    fallback = [
        {"title": "Daydream Pop", "artist": "Paper Sun", "note": "軽くて聴きやすい"},
        {"title": "Stereo Breeze", "artist": "Room Radio", "note": "作業BGMにちょうどいい"},
        {"title": "Afterglow", "artist": "Glass Hour", "note": "余韻が残る、落ち着く"},
    ]

    return catalog.get(type_code, fallback)
