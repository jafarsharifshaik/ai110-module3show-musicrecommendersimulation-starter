from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


from src.recommender import load_songs, score_song, recommend_songs, max_score


def make_song(id, title, artist, genre, mood, energy, **extra):
    song = dict(id=id, title=title, artist=artist, genre=genre, mood=mood, energy=energy,
                tempo_bpm=100.0, valence=0.5, danceability=0.5, acousticness=0.5,
                popularity=50, release_decade=2010, mood_tags=[], instrumentalness=0.0, liveness=0.0)
    song.update(extra)
    return song


def test_load_songs_parses_advanced_attributes():
    songs = load_songs("data/songs.csv")
    first = songs[0]
    assert isinstance(first["popularity"], int)
    assert isinstance(first["release_decade"], int)
    assert isinstance(first["instrumentalness"], float)
    assert isinstance(first["mood_tags"], list) and first["mood_tags"]


def test_advanced_preferences_add_points_with_reasons():
    prefs = {"favorite_genre": "x", "favorite_mood": "x", "target_energy": 0.5,
             "desired_tags": ["nostalgic", "dreamy"], "preferred_decade": 1980}
    song = make_song(1, "Retro", "A", "synthwave", "moody", 0.5,
                     mood_tags=["nostalgic", "dreamy"], release_decade=1980)
    score, reasons = score_song(prefs, song)
    # energy 1.5 + tags 0.75 + decade 0.5 in genre-first mode
    assert abs(score - 2.75) < 1e-9
    assert any("mood tags" in r for r in reasons)
    assert any("1980s" in r for r in reasons)


def test_max_score_only_counts_preferences_the_user_set():
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}
    assert max_score(prefs, "genre-first") == 5.0


def test_mood_first_mode_prefers_mood_over_genre():
    prefs = {"favorite_genre": "edm", "favorite_mood": "sad", "target_energy": 0.5}
    genre_match = make_song(1, "Genre Match", "A", "edm", "happy", 0.5)
    mood_match = make_song(2, "Mood Match", "B", "folk", "sad", 0.5)
    songs = [genre_match, mood_match]
    assert recommend_songs(prefs, songs, k=1, mode="genre-first")[0][0]["title"] == "Genre Match"
    assert recommend_songs(prefs, songs, k=1, mode="mood-first")[0][0]["title"] == "Mood Match"


def test_diversity_penalty_pushes_down_repeated_artist():
    # No genre match, so scores are: Top 2.5, Second 2.5, Other 2.35
    prefs = {"favorite_genre": "none", "favorite_mood": "chill", "target_energy": 0.4}
    songs = [
        make_song(1, "Top", "Same Artist", "lofi", "chill", 0.4),
        make_song(2, "Second", "Same Artist", "lofi", "chill", 0.4),
        make_song(3, "Other", "Other Artist", "jazz", "chill", 0.3),
    ]
    plain = [s["title"] for s, _, _ in recommend_songs(prefs, songs, k=3)]
    diverse = recommend_songs(prefs, songs, k=3, diverse=True)
    assert plain == ["Top", "Second", "Other"]
    assert [s["title"] for s, _, _ in diverse] == ["Top", "Other", "Second"]
    assert "diversity" in diverse[2][2]
