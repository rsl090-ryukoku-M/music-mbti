from __future__ import annotations
from typing import Dict, Any

TYPE_META: Dict[str, Dict[str, Any]] = {
    "ABCD": {"name": "フェス先頭列タイプ", "tagline": "明るく速くて生音も好き。しかも新規開拓派。"},
    "ABcD": {"name": "ネオン疾走タイプ", "tagline": "明るく速くて電子寄り。新しい曲を探すのが好き。"},
    "AbcD": {"name": "夜更かしドライブタイプ", "tagline": "暗めで速い。電子寄りで探索好き。"},
    "abCd": {"name": "部屋で浸るタイプ", "tagline": "静かで暗め。生音寄りで定番を大事にする。"},
}

def _axis_labels(type_code: str) -> Dict[str, str]:
    return {
        "energy": "動" if type_code[0] == "A" else "静",
        "mood": "明" if type_code[1] == "B" else "影",
        "texture": "生" if type_code[2] == "C" else "電",
        "explore": "探索" if type_code[3] == "D" else "定番",
    }

# --- 16タイプの表示プリセット（A/a, B/b, C/c, D/d の大小で16通り） ---

TYPE_PRESETS: dict[str, dict] = {
    # 動(高Energy) × 光(明るめ) × 生(オーガニック) × 探索
    "ABCD": {"name": "フェス日和タイプ", "tagline": "明るく前のめり。歌と熱量で押し切る。"},
    # 動 × 光 × 生 × 安定
    "ABCd": {"name": "王道ポップタイプ", "tagline": "みんなで口ずさむ。安心感のある主役。"},
    # 動 × 光 × 電(エレクトロ) × 探索
    "ABcD": {"name": "ネオンランナータイプ", "tagline": "光るビートで走る。新曲探索が止まらない。"},
    # 動 × 光 × 電 × 安定
    "ABcd": {"name": "クラブ常連タイプ", "tagline": "テンポ良く気分UP。踊れる定番が好き。"},

    # 動 × 影(暗め) × 生 × 探索
    "AbCD": {"name": "夜更かしドライブタイプ", "tagline": "暗めで速い。余韻とスピードの両取り。"},
    # 動 × 影 × 生 × 安定
    "AbCd": {"name": "雨上がりロックタイプ", "tagline": "少し切ない。でも芯は強い。定番で沁みる。"},
    # 動 × 影 × 電 × 探索
    "AbcD": {"name": "深夜探索タイプ", "tagline": "暗め電子で世界観に潜る。未知の沼へ。"},
    # 動 × 影 × 電 × 安定
    "Abcd": {"name": "ダークグルーヴタイプ", "tagline": "低音で整う。お気に入りを深掘りする。"},


    # 静(低Energy) × 光 × 生 × 探索
    "aBCD": {"name": "昼下がり散歩タイプ", "tagline": "やさしく軽やか。気分転換に新しい道。"},
    # 静 × 光 × 生 × 安定
    "aBCd": {"name": "カフェBGMタイプ", "tagline": "落ち着くのに明るい。毎日に馴染む。"},
    # 静 × 光 × 電 × 探索
    "aBcD": {"name": "ゆるネオンタイプ", "tagline": "ふわっと電子。静かに新しい音を拾う。"},
    # 静 × 光 × 電 × 安定
    "aBcd": {"name": "チルポップタイプ", "tagline": "明るいチル。気分を軽く保つ名人。"},


    # 静 × 影 × 生 × 探索
    "abCD": {"name": "読書の余韻タイプ", "tagline": "静かに沁みる。アルバムで旅する。"},
    # 静 × 影 × 生 × 安定
    "abCd": {"name": "やさしいブルースタイプ", "tagline": "穏やかな陰影。馴染みの音で整う。"},
    # 静 × 影 × 電 × 探索
    "abcD": {"name": "夜の作業タイプ", "tagline": "暗め電子で集中。知らない曲を掘る。"},
    # 静 × 影 × 電 × 安定
    "abcd": {"name": "深呼吸アンビエントタイプ", "tagline": "静寂と低音。空間ごと落ち着く。"},
}

def _axes_from_code(type_code: str) -> dict:
    """
    小文字/大文字で4軸のラベルを作る（フロントのチップ表示用）
    A/a: 動/静, B/b: 光/影, C/c: 生/電, D/d: 探索/安定
    """
    return {
        "energy": "動" if type_code[:1].isupper() else "静",
        "mood": "光" if len(type_code) > 1 and type_code[1:2].isupper() else "影",
        "texture": "生" if len(type_code) > 2 and type_code[2:3].isupper() else "電",
        "explore": "探索" if len(type_code) > 3 and type_code[3:4].isupper() else "安定",
    }

def describe_type(type_code: str) -> dict:
    preset = TYPE_PRESETS.get(type_code)
    if not preset:
        # 未定義でも落とさない（保険）
        preset = {"name": f"Type {type_code}", "tagline": "あなたの音楽の傾向を表すタイプ。"}
    return {
        "name": preset["name"],
        "tagline": preset["tagline"],
        "axes": _axes_from_code(type_code),
    }


# --- 代表曲（仮）3曲：タイプごとに固定（シェアでブレない） ---

TYPE_TRACKS: dict[str, list[dict]] = {
    "ABCD": [
        {"title": "Sunburst Chorus", "artist": "Bright Parade", "note": "サビで勝つ。熱量が上がる。"},
        {"title": "Open Air", "artist": "Weekend Bloom", "note": "屋外が似合うポップ。"},
        {"title": "All Hands", "artist": "The Rallies", "note": "みんなで跳ねる系。"},
    ],
    "ABCd": [
        {"title": "Standard Smile", "artist": "City Radio", "note": "安心して聴ける王道。"},
        {"title": "Favorite Line", "artist": "Mellow Days", "note": "毎日の相棒。"},
        {"title": "Sing Along", "artist": "June Avenue", "note": "口ずさみ最強。"},
    ],
    "ABcD": [
        {"title": "Neon Sprint", "artist": "Pulse Arcade", "note": "光るビートで加速。"},
        {"title": "Glitter Mode", "artist": "Night Circuit", "note": "新しい音が欲しい時。"},
        {"title": "Fast Forward", "artist": "Skyline DJ", "note": "探索が止まらない。"},
    ],
    "ABcd": [
        {"title": "Club Habit", "artist": "Glow Room", "note": "定番で気分UP。"},
        {"title": "Easy Bounce", "artist": "Disco Kit", "note": "踊れる安定感。"},
        {"title": "Repeat Tonight", "artist": "Floor Friends", "note": "ループしたくなる。"},
    ],

    "AbCD": [
        {"title": "Midnight Loop", "artist": "Neon Taxi", "note": "夜の高速、低音が気持ちいい。"},
        {"title": "Shadow Sprint", "artist": "City Pulse", "note": "暗め×速め、集中スイッチ。"},
        {"title": "Analog Rain", "artist": "Blue Static", "note": "冷たい空気、ドライブ向け。"},
    ],
    "AbCd": [
        {"title": "After Rain", "artist": "Stone Avenue", "note": "沁みるのに前向き。"},
        {"title": "Guitar Glow", "artist": "Small Torch", "note": "静かな熱。"},
        {"title": "Old Jacket", "artist": "Room Band", "note": "馴染むロック。"},
    ],
    "AbcD": [
        {"title": "Tunnel Lights", "artist": "Noon Runner", "note": "世界観に潜る。"},
        {"title": "Low Frequency", "artist": "Dark Bloom", "note": "新曲沼へようこそ。"},
        {"title": "Quiet Accel", "artist": "Soda Wave", "note": "静かに加速する。"},
    ],
    "Abcd": [
        {"title": "Night Groove", "artist": "Bass Clinic", "note": "低音で整う。"},
        {"title": "Same Corner", "artist": "Deep Routine", "note": "お気に入りを深掘り。"},
        {"title": "Dim Light", "artist": "Mono Room", "note": "ダーク寄りの安定。"},
    ],

    "aBCD": [
        {"title": "Sunny Walk", "artist": "Day Canvas", "note": "軽やか散歩BGM。"},
        {"title": "New Alley", "artist": "Fresh Steps", "note": "ちょい探索。"},
        {"title": "Soft Breeze", "artist": "Picnic Notes", "note": "やさしい光。"},
    ],
    "aBCd": [
        {"title": "Cafe Window", "artist": "Latte Club", "note": "明るく落ち着く。"},
        {"title": "Daily Blend", "artist": "Routine Radio", "note": "日常に馴染む。"},
        {"title": "Warm Cup", "artist": "Sugar Spoon", "note": "安心のBGM。"},
    ],
    "aBcD": [
        {"title": "Pastel Signal", "artist": "Soft Circuit", "note": "ふわ電子で探索。"},
        {"title": "Light Pulse", "artist": "Slow Neon", "note": "静かに新しい音。"},
        {"title": "Cloud Synth", "artist": "Air Mode", "note": "気分が軽い。"},
    ],
    "aBcd": [
        {"title": "Chill Pop", "artist": "Calm Parade", "note": "明るいチル。"},
        {"title": "Easy Wave", "artist": "Room FM", "note": "作業にちょうどいい。"},
        {"title": "Lazy Noon", "artist": "Sun Sofa", "note": "ゆるい安定感。"},
    ],

    "abCD": [
        {"title": "Paper Pages", "artist": "Quiet Shelf", "note": "読書の余韻。"},
        {"title": "Long Album", "artist": "Storyline", "note": "アルバム旅。"},
        {"title": "Soft Strings", "artist": "Lamp Band", "note": "静かに沁みる。"},
    ],
    "abCd": [
        {"title": "Gentle Blue", "artist": "Old Porch", "note": "穏やかな陰影。"},
        {"title": "Slow Jam", "artist": "Evening Tea", "note": "落ち着く定番。"},
        {"title": "Familiar Road", "artist": "Home Notes", "note": "馴染みで整う。"},
    ],
    "abcD": [
        {"title": "Night Work", "artist": "Focus Room", "note": "暗め電子で集中。"},
        {"title": "Deep Search", "artist": "Hidden Finds", "note": "掘るのが好き。"},
        {"title": "Low Light", "artist": "Silent Sync", "note": "静かに刺さる。"},
    ],
    "abcd": [
        {"title": "Breath", "artist": "Ambient Field", "note": "空間ごと落ち着く。"},
        {"title": "Still Water", "artist": "Slow Current", "note": "静寂と低音。"},
        {"title": "Afterglow", "artist": "Glass Hour", "note": "余韻が残る。"},
    ],
}

def pick_sample_tracks_fake(type_code: str) -> list[dict]:
    # 未定義でも落とさない保険（どのタイプでも3曲返す）
    fallback = [
        {"title": "Daydream Pop", "artist": "Paper Sun", "note": "軽くて聴きやすい"},
        {"title": "Stereo Breeze", "artist": "Room Radio", "note": "作業BGMにちょうどいい"},
        {"title": "Afterglow", "artist": "Glass Hour", "note": "余韻が残る、落ち着く"},
    ]
    return TYPE_TRACKS.get(type_code, fallback)


def pick_sample_tracks_fake(type_code: str) -> list[dict]:
    """
    Spotifyが無い時の“それっぽい代表曲”を返す。
    type_codeごとに固定なので、シェアしてもブレない。
    """
    catalog = {
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

    # 未定義タイプは共通の3曲（仮）
    fallback = [
        {"title": "Daydream Pop", "artist": "Paper Sun", "note": "軽くて聴きやすい"},
        {"title": "Stereo Breeze", "artist": "Room Radio", "note": "作業BGMにちょうどいい"},
        {"title": "Afterglow", "artist": "Glass Hour", "note": "余韻が残る、落ち着く"},
    ]

    return catalog.get(type_code, fallback)

def _clamp01(x: float) -> float:
    try:
        v = float(x)
    except Exception:
        return 0.0
    if v < 0:
        return 0.0
    if v > 1:
        return 1.0
    return v


def compute_scores_from_selected_tracks(tracks: list[dict]) -> dict:
    """
    フロントから送られる各曲の特徴量(0..1)を平均して、4スコアにする。
    入力例：
      {"tempo":0.8,"bright":0.2,"electro":0.7,"explore":0.6}
    """
    if not tracks:
        return {"energy_score": 0.5, "mood_score": 0.5, "texture_score": 0.5, "explore_score": 0.5}

    tempos = []
    brights = []
    electros = []
    explores = []

    for t in tracks:
        tempos.append(_clamp01(t.get("tempo", 0.5)))
        brights.append(_clamp01(t.get("bright", 0.5)))
        electros.append(_clamp01(t.get("electro", 0.5)))
        explores.append(_clamp01(t.get("explore", 0.5)))

    n = max(1, len(tracks))
    return {
        "energy_score": sum(tempos) / n,     # tempo → energy
        "mood_score": sum(brights) / n,     # bright → mood
        "texture_score": sum(electros) / n, # electro → texture（生↔電）
        "explore_score": sum(explores) / n, # explore → explore
    }


