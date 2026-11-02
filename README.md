# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube mix two ideas: **collaborative filtering** ("people who liked what you liked also liked this") and **content-based filtering** ("this song sounds like the songs you already like"). Collaborative filtering needs lots of users' listening history, which we don't have, so this simulation is purely **content-based**. Each song is described by its attributes, the user describes their taste with the same attributes, and the system recommends songs whose attributes are *closest* to that taste. My version prioritizes the overall **vibe** of a song: genre and mood act as the main labels, and energy is the most important number because it best captures how "chill" or "intense" a song feels.

### Features used

**`Song`**

| Feature | Type | Used in scoring? |
|---|---|---|
| `genre` | category (pop, lofi, rock, ...) | Yes – exact match |
| `mood` | category (happy, chill, intense, ...) | Yes – exact match |
| `energy` | 0.0–1.0 | Yes – closeness to target |
| `acousticness` | 0.0–1.0 | Yes – matched to `likes_acoustic` |
| `valence` | 0.0–1.0 (sad → happy) | Not scored in v1 (candidate for a later experiment) |
| `tempo_bpm`, `danceability` | numbers | Not scored (they track energy closely in this dataset) |
| `id`, `title`, `artist` | identifiers | Display only |

**`UserProfile`**

- `favorite_genre` – the genre the user wants most
- `favorite_mood` – the mood the user is in
- `target_energy` – the energy level (0.0–1.0) they want, not "more is better"
- `likes_acoustic` – whether they prefer acoustic/organic sound over produced/electronic

### Dataset

`data/songs.csv` has 18 songs. The 10 starter songs (pop, lofi, rock, ambient, jazz, synthwave, indie pop) were expanded with 8 songs in new genres and moods: hip hop/confident, classical/peaceful, metal/angry, country/nostalgic, r&b/romantic, edm/energetic, reggae/uplifting and folk/sad. Energy now ranges from 0.18 to 0.97 and valence from 0.18 to 0.88.

### Test user profile

```python
user_prefs = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.40,
    "likes_acoustic": True,
}
```

A late-night study listener. `src/main.py` runs this profile and the default pop/happy profile (`pop / happy / 0.80 / not acoustic`). A dry run of the recipe below ranks Library Rain (4.85) and Midnight Coding (4.82) first and Ironclad (metal) last. A rock/intense/0.90 profile puts Storm Runner first, so the profile clearly separates "chill lofi" from "intense rock".

### Algorithm Recipe (final)

**Scoring Rule (one song):**

```
score = 2.0 × (genre matches)              # +2.0 or 0
      + 1.0 × (mood matches)               # +1.0 or 0
      + 1.5 × (1 − |song.energy − target_energy|)
      + 0.5 × (acousticness if likes_acoustic else 1 − acousticness)
```

- Energy uses **closeness**, `1 − |difference|`, so a song with energy 0.40 scores best for a user who wants 0.40. A higher energy does not automatically win.
- Genre is weighted above mood because genre describes the overall sound. Mood changes from day to day, so a lofi fan in an "intense" mood still probably doesn't want heavy rock.
- The maximum score is 5.0. Each part also adds a short reason (for example, "genre match: lofi") so every recommendation can explain itself.

**Ranking Rule (the whole list):** score every song in the catalog, sort from highest to lowest score, and return the top `k`.

We need both rules because they answer different questions. The scoring rule decides *how good one song is for this user*. The ranking rule decides *which songs to show, and in what order*. A score alone can't tell you whether 3.2 is good. It only means something compared with the other songs. Keeping the two rules separate also means you can change the ranking later (for example, to add variety by limiting one song per artist) without touching the scoring math.

### Data flow

```
INPUT                     PROCESS (loop over every song)            OUTPUT
user_prefs  ─┐
             ├─► for song in songs.csv:                       ─► sort by score (high → low)
songs.csv   ─┘      score, reasons = score_song(prefs, song)       take top k
                    collect (song, score, reasons)                 print title, score, "because ..."
```

Example: with the profile `lofi / chill / energy 0.40 / likes acoustic`, Library Rain scores 4.85 (genre + mood + near-exact energy + very acoustic), while Ironclad (metal / angry / 0.97) lands last.

### Expected biases

- **Genre over-prioritized.** A genre match (+2.0) is worth more than mood and acoustic preference combined. Any lofi song will outrank a non-lofi song that fits the vibe perfectly. For example, Spacewalk Thoughts (ambient/chill) only scores 2.78 for the lofi profile.
- **Exact string matching is brittle.** "indie pop" gets no credit for "pop", and "chill" gets none for "relaxed" or "peaceful", even though people hear them as close.
- **Small catalog means a thin genre pool.** Most genres have only 1–3 songs. After the single rock song, a rock fan's list falls back to energy alone and fills up with pop and edm.
- **One genre and one mood per user.** Real listeners like several genres and change mood often. This profile can't express "lofi *or* jazz".
- **Energy dominates the numeric side.** Tempo and danceability aren't scored, and they move with energy anyway. A slow but danceable track has no way to stand out.
- **The catalog reflects its author's taste.** I chose the genres, moods and feature numbers, so they carry my assumptions about what, for example, "sad folk" or "angry metal" sounds like.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default pop/happy profile and the lofi/chill test profile:

```
Loaded songs: 18

============================================================
Happy pop fan
  favorite_genre=pop, favorite_mood=happy, target_energy=0.8, likes_acoustic=False
============================================================
1. Sunrise City by Neon Echo  (pop / happy)
   Score: 4.88 / 5.00
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs target 0.80 (+1.47)
     - produced sound fit (+0.41)
2. Gym Hero by Max Pulse  (pop / intense)
   Score: 3.78 / 5.00
     - genre match: pop (+2.0)
     - energy 0.93 vs target 0.80 (+1.30)
     - produced sound fit (+0.47)
3. Rooftop Lights by Indigo Parade  (indie pop / happy)
   Score: 2.77 / 5.00
     - mood match: happy (+1.0)
     - energy 0.76 vs target 0.80 (+1.44)
     - produced sound fit (+0.33)
4. Concrete Crown by Block Theory  (hip hop / confident)
   Score: 1.91 / 5.00
     - energy 0.78 vs target 0.80 (+1.47)
     - produced sound fit (+0.44)
5. Night Drive Loop by Neon Echo  (synthwave / moody)
   Score: 1.81 / 5.00
     - energy 0.75 vs target 0.80 (+1.42)
     - produced sound fit (+0.39)

============================================================
Late-night lofi studier
  favorite_genre=lofi, favorite_mood=chill, target_energy=0.4, likes_acoustic=True
============================================================
1. Library Rain by Paper Lanterns  (lofi / chill)
   Score: 4.85 / 5.00
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.35 vs target 0.40 (+1.42)
     - acoustic sound fit (+0.43)
2. Midnight Coding by LoRoom  (lofi / chill)
   Score: 4.82 / 5.00
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.42 vs target 0.40 (+1.47)
     - acoustic sound fit (+0.35)
3. Focus Flow by LoRoom  (lofi / focused)
   Score: 3.89 / 5.00
     - genre match: lofi (+2.0)
     - energy 0.40 vs target 0.40 (+1.50)
     - acoustic sound fit (+0.39)
4. Spacewalk Thoughts by Orbit Bloom  (ambient / chill)
   Score: 2.78 / 5.00
     - mood match: chill (+1.0)
     - energy 0.28 vs target 0.40 (+1.32)
     - acoustic sound fit (+0.46)
5. Coffee Shop Stories by Slow Stereo  (jazz / relaxed)
   Score: 1.90 / 5.00
     - energy 0.37 vs target 0.40 (+1.46)
     - acoustic sound fit (+0.45)
```

The pop/happy results match what I expected. Sunrise City is a near-perfect fit. Gym Hero comes second only because of its genre match, even though it's "intense", and it beats Rooftop Lights, which is happy with the right energy but labeled "indie pop". This is the genre-overweighting bias predicted above.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



