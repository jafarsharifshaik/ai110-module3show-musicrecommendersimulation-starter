import csv
from typing import Callable, List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2010
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    liveness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    desired_tags: Optional[List[str]] = None
    preferred_decade: Optional[int] = None
    likes_instrumental: Optional[bool] = None
    prefers_popular: Optional[bool] = None
    likes_live: Optional[bool] = None

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, mode: str = "genre-first") -> List[Song]:
        """Return the top k Song objects for the user, highest score first."""
        prefs = asdict(user)
        return sorted(self.songs, key=lambda song: score_song(prefs, asdict(song), mode)[0], reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = "genre-first") -> str:
        """Return a one-line explanation of why the song scored the way it did."""
        _, reasons = score_song(asdict(user), asdict(song), mode)
        return "; ".join(reasons)

# ---------------------------------------------------------------------------
# Feature scorers: each returns (fit from 0 to 1, reason label), or None for no points.
# A scorer only runs when the user has set its preference key.
# ---------------------------------------------------------------------------

def _closeness(a: float, b: float) -> float:
    """Return 1.0 when a == b, falling linearly to 0.0 as they move apart."""
    return max(0.0, 1 - abs(a - b))

def _bool_fit(likes: bool, value: float) -> float:
    """Return value if the user likes the trait, otherwise 1 - value."""
    return value if likes else 1 - value

def _score_genre(prefs: Dict, song: Dict):
    if song["genre"] == prefs["favorite_genre"]:
        return 1.0, f"genre match: {song['genre']}"
    return None

def _score_mood(prefs: Dict, song: Dict):
    if song["mood"] == prefs["favorite_mood"]:
        return 1.0, f"mood match: {song['mood']}"
    return None

def _score_energy(prefs: Dict, song: Dict):
    # Closeness, not "higher is better": full points when energy equals the target
    target = prefs["target_energy"]
    return _closeness(song["energy"], target), f"energy {song['energy']:.2f} vs target {target:.2f}"

def _score_acoustic(prefs: Dict, song: Dict):
    label = "acoustic" if prefs["likes_acoustic"] else "produced"
    return _bool_fit(prefs["likes_acoustic"], song["acousticness"]), f"{label} sound fit"

def _score_tags(prefs: Dict, song: Dict):
    # Partial credit: fraction of the user's desired tags this song carries
    matched = [tag for tag in prefs["desired_tags"] if tag in song["mood_tags"]]
    if not matched:
        return None
    return len(matched) / len(prefs["desired_tags"]), f"mood tags: {', '.join(matched)}"

def _score_decade(prefs: Dict, song: Dict):
    gap = abs(song["release_decade"] - prefs["preferred_decade"])
    if gap == 0:
        return 1.0, f"from the {song['release_decade']}s"
    if gap == 10:
        return 0.5, f"near your decade ({song['release_decade']}s)"
    return None

def _score_instrumental(prefs: Dict, song: Dict):
    label = "instrumental" if prefs["likes_instrumental"] else "vocal"
    return _bool_fit(prefs["likes_instrumental"], song["instrumentalness"]), f"{label} fit"

def _score_popularity(prefs: Dict, song: Dict):
    label = "mainstream" if prefs["prefers_popular"] else "hidden-gem"
    return _bool_fit(prefs["prefers_popular"], song["popularity"] / 100), f"{label} fit (popularity {song['popularity']})"

def _score_liveness(prefs: Dict, song: Dict):
    label = "live feel" if prefs["likes_live"] else "studio feel"
    return _bool_fit(prefs["likes_live"], song["liveness"]), label

# (feature name, user preference key it needs, scorer)
FEATURES: List[Tuple[str, str, Callable]] = [
    ("genre", "favorite_genre", _score_genre),
    ("mood", "favorite_mood", _score_mood),
    ("energy", "target_energy", _score_energy),
    ("acoustic", "likes_acoustic", _score_acoustic),
    ("tags", "desired_tags", _score_tags),
    ("decade", "preferred_decade", _score_decade),
    ("instrumental", "likes_instrumental", _score_instrumental),
    ("popularity", "prefers_popular", _score_popularity),
    ("liveness", "likes_live", _score_liveness),
]

# ---------------------------------------------------------------------------
# Scoring modes (Strategy pattern): each mode is a weight table over FEATURES.
# Adding a mode means adding a table here; the scoring code does not change.
# ---------------------------------------------------------------------------

SCORING_MODES: Dict[str, Dict[str, float]] = {
    "genre-first": {
        "genre": 2.0, "mood": 1.0, "energy": 1.5, "acoustic": 0.5,
        "tags": 0.75, "decade": 0.5, "instrumental": 0.5, "popularity": 0.25, "liveness": 0.25,
    },
    "mood-first": {
        "genre": 0.75, "mood": 2.0, "energy": 1.0, "acoustic": 0.5,
        "tags": 1.5, "decade": 0.5, "instrumental": 0.5, "popularity": 0.25, "liveness": 0.25,
    },
    "energy-focused": {
        "genre": 0.75, "mood": 0.75, "energy": 3.0, "acoustic": 0.75,
        "tags": 0.5, "decade": 0.25, "instrumental": 0.5, "popularity": 0.25, "liveness": 0.25,
    },
}
DEFAULT_MODE = "genre-first"

# Diversity penalty, applied per song already picked with the same artist / genre
ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5

def _active_features(user_prefs: Dict) -> List[Tuple[str, str, Callable]]:
    """Return the features whose preference the user has actually set."""
    return [f for f in FEATURES if user_prefs.get(f[1]) is not None]

def max_score(user_prefs: Optional[Dict] = None, mode: str = DEFAULT_MODE) -> float:
    """Return the highest score a song can earn for this user under the given mode."""
    weights = SCORING_MODES[mode]
    features = FEATURES if user_prefs is None else _active_features(user_prefs)
    return sum(weights[name] for name, _, _ in features)

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv into a list of dicts, converting numeric columns to int/float."""
    int_fields = {"id", "popularity", "release_decade"}
    float_fields = {"energy", "tempo_bpm", "valence", "danceability", "acousticness",
                    "instrumentalness", "liveness"}
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field_name in int_fields:
                row[field_name] = int(row[field_name])
            for field_name in float_fields:
                row[field_name] = float(row[field_name])
            row["mood_tags"] = row["mood_tags"].split(";") if row["mood_tags"] else []
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict, mode: str = DEFAULT_MODE) -> Tuple[float, List[str]]:
    """Score one song against user_prefs under a scoring mode and return (score, list of reasons)."""
    weights = SCORING_MODES[mode]
    score = 0.0
    reasons = []
    for name, _, scorer in _active_features(user_prefs):
        result = scorer(user_prefs, song)
        if result is None:
            continue
        fit, label = result
        points = weights[name] * fit
        score += points
        reasons.append(f"{label} (+{points:.2f})")
    return score, reasons

def _diversify(scored: List[Tuple[Dict, float, List[str]]], k: int) -> List[Tuple[Dict, float, List[str]]]:
    """Greedily pick k songs, penalizing each one whose artist or genre is already picked."""
    remaining = list(scored)
    picked = []

    def adjusted(item):
        song, score, reasons = item
        same_artist = sum(1 for p, _, _ in picked if p["artist"] == song["artist"])
        same_genre = sum(1 for p, _, _ in picked if p["genre"] == song["genre"])
        penalty_reasons = []
        if same_artist:
            penalty_reasons.append(f"diversity: artist {song['artist']} already listed (-{ARTIST_PENALTY * same_artist:.2f})")
        if same_genre:
            penalty_reasons.append(f"diversity: genre {song['genre']} already listed (-{GENRE_PENALTY * same_genre:.2f})")
        penalty = ARTIST_PENALTY * same_artist + GENRE_PENALTY * same_genre
        return song, score - penalty, reasons + penalty_reasons

    while remaining and len(picked) < k:
        best_index = max(range(len(remaining)), key=lambda i: adjusted(remaining[i])[1])
        picked.append(adjusted(remaining.pop(best_index)))
    return picked

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5,
                    mode: str = DEFAULT_MODE, diverse: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation), highest first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        scored.append((song, score, reasons))
    scored.sort(key=lambda item: item[1], reverse=True)
    top = _diversify(scored, k) if diverse else scored[:k]
    return [(song, score, "; ".join(reasons)) for song, score, reasons in top]
