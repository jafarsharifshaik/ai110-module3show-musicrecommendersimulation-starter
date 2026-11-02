"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main
Options:
  --mode {genre-first,mood-first,energy-focused}   choose a scoring strategy
  --diverse                                       penalize repeated artists/genres
  --profile TEXT                                  only run profiles whose name contains TEXT
"""

import argparse

from src.recommender import load_songs, recommend_songs, max_score, SCORING_MODES, DEFAULT_MODE

PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    # Edge cases: profiles designed to trick the scoring logic
    "Sad Raver (conflict: sad mood, high energy)": {
        "favorite_genre": "edm",
        "favorite_mood": "sad",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    "Acoustic Metalhead (conflict: metal + acoustic)": {
        "favorite_genre": "metal",
        "favorite_mood": "angry",
        "target_energy": 0.95,
        "likes_acoustic": True,
    },
    "K-Pop Fan (genre not in catalog)": {
        "favorite_genre": "k-pop",
        "favorite_mood": "happy",
        "target_energy": 0.70,
        "likes_acoustic": False,
    },
    # Uses the advanced song attributes (mood tags, decade, instrumentalness, popularity, liveness)
    "Throwback Night Owl": {
        "favorite_genre": "synthwave",
        "favorite_mood": "moody",
        "target_energy": 0.60,
        "likes_acoustic": False,
        "desired_tags": ["nostalgic", "nocturnal", "dreamy"],
        "preferred_decade": 1980,
        "likes_instrumental": True,
        "prefers_popular": False,
        "likes_live": False,
    },
}


def format_table(headers: list, rows: list) -> str:
    """Render rows as an ASCII table; each cell is a list of lines so reasons can stack."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], *(len(line) for line in cell))
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def render(cells):
        height = max(len(c) for c in cells)
        lines = []
        for n in range(height):
            parts = [(c[n] if n < len(c) else "").ljust(w) for c, w in zip(cells, widths)]
            lines.append("| " + " | ".join(parts) + " |")
        return lines

    out = [border, *render([[h] for h in headers]), border]
    for row in rows:
        out += render(row)
        out.append(border)
    return "\n".join(out)


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int, mode: str, diverse: bool) -> None:
    """Print a ranked, explained table of recommendations for one profile."""
    prefs_text = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print(f"{name}  [mode: {mode}{', diverse' if diverse else ''}]")
    print(f"  {prefs_text}")
    rows = []
    for rank, (song, score, explanation) in enumerate(
            recommend_songs(user_prefs, songs, k, mode=mode, diverse=diverse), start=1):
        rows.append([
            [str(rank)],
            [song["title"], f"by {song['artist']}"],
            [song["genre"], song["mood"]],
            [f"{score:.2f}", f"/ {max_score(user_prefs, mode):.2f}"],
            explanation.split("; "),
        ])
    print(format_table(["#", "Song", "Genre / Mood", "Score", "Reasons"], rows))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=sorted(SCORING_MODES), default=DEFAULT_MODE)
    parser.add_argument("--diverse", action="store_true")
    parser.add_argument("--profile", default="")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for name, user_prefs in PROFILES.items():
        if args.profile.lower() in name.lower():
            print_recommendations(name, user_prefs, songs, args.k, args.mode, args.diverse)


if __name__ == "__main__":
    main()
