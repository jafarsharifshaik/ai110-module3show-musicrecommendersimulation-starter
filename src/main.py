"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs, max_score

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
}


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a ranked, explained list of recommendations for one profile."""
    prefs_text = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print("=" * 60)
    print(f"{name}")
    print(f"  {prefs_text}")
    print("=" * 60)
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k), start=1):
        print(f"{rank}. {song['title']} by {song['artist']}  ({song['genre']} / {song['mood']})")
        print(f"   Score: {score:.2f} / {max_score():.2f}")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs, k=5)


if __name__ == "__main__":
    main()
