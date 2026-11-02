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
| `id`, `title`, `artist` | identifiers | Display only (artist is used by the diversity penalty) |
| `popularity` | 0–100 | Yes – matched to `prefers_popular` (stretch) |
| `release_decade` | e.g. 1980 | Yes – exact decade full points, ±10 years half (stretch) |
| `mood_tags` | detailed tags, e.g. nostalgic; euphoric | Yes – share of `desired_tags` matched (stretch) |
| `instrumentalness` | 0.0–1.0 | Yes – matched to `likes_instrumental` (stretch) |
| `liveness` | 0.0–1.0 | Yes – matched to `likes_live` (stretch) |

**`UserProfile`**

- `favorite_genre` – the genre the user wants most
- `favorite_mood` – the mood the user is in
- `target_energy` – the energy level (0.0–1.0) they want, not "more is better"
- `likes_acoustic` – whether they prefer acoustic/organic sound over produced/electronic
- *Optional (stretch):* `desired_tags`, `preferred_decade`, `likes_instrumental`, `prefers_popular`, `likes_live`. A preference that isn't set isn't scored, so the original profiles score exactly as before.

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
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main                                   # all profiles, genre-first mode
python -m src.main --mode mood-first                 # or energy-focused
python -m src.main --diverse                         # penalize repeated artists/genres
python -m src.main --profile "lofi" --mode mood-first --diverse
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main`. It runs three normal profiles, three edge-case profiles designed to trick the scoring, and one profile that uses the advanced attributes (default mode `genre-first`: genre 2.0, mood 1.0, energy 1.5, acoustic 0.5):

```
Loaded songs: 18

High-Energy Pop  [mode: genre-first]
  favorite_genre=pop, favorite_mood=happy, target_energy=0.8, likes_acoustic=False
+---+------------------+--------------+--------+------------------------------------+
| # | Song             | Genre / Mood | Score  | Reasons                            |
+---+------------------+--------------+--------+------------------------------------+
| 1 | Sunrise City     | pop          | 4.88   | genre match: pop (+2.00)           |
|   | by Neon Echo     | happy        | / 5.00 | mood match: happy (+1.00)          |
|   |                  |              |        | energy 0.82 vs target 0.80 (+1.47) |
|   |                  |              |        | produced sound fit (+0.41)         |
+---+------------------+--------------+--------+------------------------------------+
| 2 | Gym Hero         | pop          | 3.78   | genre match: pop (+2.00)           |
|   | by Max Pulse     | intense      | / 5.00 | energy 0.93 vs target 0.80 (+1.30) |
|   |                  |              |        | produced sound fit (+0.47)         |
+---+------------------+--------------+--------+------------------------------------+
| 3 | Rooftop Lights   | indie pop    | 2.77   | mood match: happy (+1.00)          |
|   | by Indigo Parade | happy        | / 5.00 | energy 0.76 vs target 0.80 (+1.44) |
|   |                  |              |        | produced sound fit (+0.33)         |
+---+------------------+--------------+--------+------------------------------------+
| 4 | Concrete Crown   | hip hop      | 1.91   | energy 0.78 vs target 0.80 (+1.47) |
|   | by Block Theory  | confident    | / 5.00 | produced sound fit (+0.44)         |
+---+------------------+--------------+--------+------------------------------------+
| 5 | Night Drive Loop | synthwave    | 1.81   | energy 0.75 vs target 0.80 (+1.42) |
|   | by Neon Echo     | moody        | / 5.00 | produced sound fit (+0.39)         |
+---+------------------+--------------+--------+------------------------------------+

Chill Lofi  [mode: genre-first]
  favorite_genre=lofi, favorite_mood=chill, target_energy=0.4, likes_acoustic=True
+---+---------------------+--------------+--------+------------------------------------+
| # | Song                | Genre / Mood | Score  | Reasons                            |
+---+---------------------+--------------+--------+------------------------------------+
| 1 | Library Rain        | lofi         | 4.85   | genre match: lofi (+2.00)          |
|   | by Paper Lanterns   | chill        | / 5.00 | mood match: chill (+1.00)          |
|   |                     |              |        | energy 0.35 vs target 0.40 (+1.42) |
|   |                     |              |        | acoustic sound fit (+0.43)         |
+---+---------------------+--------------+--------+------------------------------------+
| 2 | Midnight Coding     | lofi         | 4.82   | genre match: lofi (+2.00)          |
|   | by LoRoom           | chill        | / 5.00 | mood match: chill (+1.00)          |
|   |                     |              |        | energy 0.42 vs target 0.40 (+1.47) |
|   |                     |              |        | acoustic sound fit (+0.35)         |
+---+---------------------+--------------+--------+------------------------------------+
| 3 | Focus Flow          | lofi         | 3.89   | genre match: lofi (+2.00)          |
|   | by LoRoom           | focused      | / 5.00 | energy 0.40 vs target 0.40 (+1.50) |
|   |                     |              |        | acoustic sound fit (+0.39)         |
+---+---------------------+--------------+--------+------------------------------------+
| 4 | Spacewalk Thoughts  | ambient      | 2.78   | mood match: chill (+1.00)          |
|   | by Orbit Bloom      | chill        | / 5.00 | energy 0.28 vs target 0.40 (+1.32) |
|   |                     |              |        | acoustic sound fit (+0.46)         |
+---+---------------------+--------------+--------+------------------------------------+
| 5 | Coffee Shop Stories | jazz         | 1.90   | energy 0.37 vs target 0.40 (+1.46) |
|   | by Slow Stereo      | relaxed      | / 5.00 | acoustic sound fit (+0.45)         |
+---+---------------------+--------------+--------+------------------------------------+

Deep Intense Rock  [mode: genre-first]
  favorite_genre=rock, favorite_mood=intense, target_energy=0.9, likes_acoustic=False
+---+------------------+--------------+--------+------------------------------------+
| # | Song             | Genre / Mood | Score  | Reasons                            |
+---+------------------+--------------+--------+------------------------------------+
| 1 | Storm Runner     | rock         | 4.93   | genre match: rock (+2.00)          |
|   | by Voltline      | intense      | / 5.00 | mood match: intense (+1.00)        |
|   |                  |              |        | energy 0.91 vs target 0.90 (+1.48) |
|   |                  |              |        | produced sound fit (+0.45)         |
+---+------------------+--------------+--------+------------------------------------+
| 2 | Gym Hero         | pop          | 2.93   | mood match: intense (+1.00)        |
|   | by Max Pulse     | intense      | / 5.00 | energy 0.93 vs target 0.90 (+1.46) |
|   |                  |              |        | produced sound fit (+0.47)         |
+---+------------------+--------------+--------+------------------------------------+
| 3 | Pulse Reactor    | edm          | 1.91   | energy 0.95 vs target 0.90 (+1.43) |
|   | by Kilowatt Kids | energetic    | / 5.00 | produced sound fit (+0.48)         |
+---+------------------+--------------+--------+------------------------------------+
| 4 | Ironclad         | metal        | 1.88   | energy 0.97 vs target 0.90 (+1.40) |
|   | by Rust Prophet  | angry        | / 5.00 | produced sound fit (+0.48)         |
+---+------------------+--------------+--------+------------------------------------+
| 5 | Sunrise City     | pop          | 1.79   | energy 0.82 vs target 0.90 (+1.38) |
|   | by Neon Echo     | happy        | / 5.00 | produced sound fit (+0.41)         |
+---+------------------+--------------+--------+------------------------------------+

Sad Raver (conflict: sad mood, high energy)  [mode: genre-first]
  favorite_genre=edm, favorite_mood=sad, target_energy=0.9, likes_acoustic=False
+---+------------------+--------------+--------+------------------------------------+
| # | Song             | Genre / Mood | Score  | Reasons                            |
+---+------------------+--------------+--------+------------------------------------+
| 1 | Pulse Reactor    | edm          | 3.90   | genre match: edm (+2.00)           |
|   | by Kilowatt Kids | energetic    | / 5.00 | energy 0.95 vs target 0.90 (+1.43) |
|   |                  |              |        | produced sound fit (+0.48)         |
+---+------------------+--------------+--------+------------------------------------+
| 2 | Storm Runner     | rock         | 1.93   | energy 0.91 vs target 0.90 (+1.48) |
|   | by Voltline      | intense      | / 5.00 | produced sound fit (+0.45)         |
+---+------------------+--------------+--------+------------------------------------+
| 3 | Gym Hero         | pop          | 1.93   | energy 0.93 vs target 0.90 (+1.46) |
|   | by Max Pulse     | intense      | / 5.00 | produced sound fit (+0.47)         |
+---+------------------+--------------+--------+------------------------------------+
| 4 | Ironclad         | metal        | 1.88   | energy 0.97 vs target 0.90 (+1.40) |
|   | by Rust Prophet  | angry        | / 5.00 | produced sound fit (+0.48)         |
+---+------------------+--------------+--------+------------------------------------+
| 5 | Sunrise City     | pop          | 1.79   | energy 0.82 vs target 0.90 (+1.38) |
|   | by Neon Echo     | happy        | / 5.00 | produced sound fit (+0.41)         |
+---+------------------+--------------+--------+------------------------------------+

Acoustic Metalhead (conflict: metal + acoustic)  [mode: genre-first]
  favorite_genre=metal, favorite_mood=angry, target_energy=0.95, likes_acoustic=True
+---+------------------+--------------+--------+------------------------------------+
| # | Song             | Genre / Mood | Score  | Reasons                            |
+---+------------------+--------------+--------+------------------------------------+
| 1 | Ironclad         | metal        | 4.48   | genre match: metal (+2.00)         |
|   | by Rust Prophet  | angry        | / 5.00 | mood match: angry (+1.00)          |
|   |                  |              |        | energy 0.97 vs target 0.95 (+1.47) |
|   |                  |              |        | acoustic sound fit (+0.01)         |
+---+------------------+--------------+--------+------------------------------------+
| 2 | Pulse Reactor    | edm          | 1.52   | energy 0.95 vs target 0.95 (+1.50) |
|   | by Kilowatt Kids | energetic    | / 5.00 | acoustic sound fit (+0.02)         |
+---+------------------+--------------+--------+------------------------------------+
| 3 | Gym Hero         | pop          | 1.50   | energy 0.93 vs target 0.95 (+1.47) |
|   | by Max Pulse     | intense      | / 5.00 | acoustic sound fit (+0.03)         |
+---+------------------+--------------+--------+------------------------------------+
| 4 | Storm Runner     | rock         | 1.49   | energy 0.91 vs target 0.95 (+1.44) |
|   | by Voltline      | intense      | / 5.00 | acoustic sound fit (+0.05)         |
+---+------------------+--------------+--------+------------------------------------+
| 5 | Sunrise City     | pop          | 1.40   | energy 0.82 vs target 0.95 (+1.30) |
|   | by Neon Echo     | happy        | / 5.00 | acoustic sound fit (+0.09)         |
+---+------------------+--------------+--------+------------------------------------+

K-Pop Fan (genre not in catalog)  [mode: genre-first]
  favorite_genre=k-pop, favorite_mood=happy, target_energy=0.7, likes_acoustic=False
+---+------------------+--------------+--------+------------------------------------+
| # | Song             | Genre / Mood | Score  | Reasons                            |
+---+------------------+--------------+--------+------------------------------------+
| 1 | Rooftop Lights   | indie pop    | 2.74   | mood match: happy (+1.00)          |
|   | by Indigo Parade | happy        | / 5.00 | energy 0.76 vs target 0.70 (+1.41) |
|   |                  |              |        | produced sound fit (+0.33)         |
+---+------------------+--------------+--------+------------------------------------+
| 2 | Sunrise City     | pop          | 2.73   | mood match: happy (+1.00)          |
|   | by Neon Echo     | happy        | / 5.00 | energy 0.82 vs target 0.70 (+1.32) |
|   |                  |              |        | produced sound fit (+0.41)         |
+---+------------------+--------------+--------+------------------------------------+
| 3 | Concrete Crown   | hip hop      | 1.82   | energy 0.78 vs target 0.70 (+1.38) |
|   | by Block Theory  | confident    | / 5.00 | produced sound fit (+0.44)         |
+---+------------------+--------------+--------+------------------------------------+
| 4 | Night Drive Loop | synthwave    | 1.81   | energy 0.75 vs target 0.70 (+1.42) |
|   | by Neon Echo     | moody        | / 5.00 | produced sound fit (+0.39)         |
+---+------------------+--------------+--------+------------------------------------+
| 5 | Storm Runner     | rock         | 1.63   | energy 0.91 vs target 0.70 (+1.18) |
|   | by Voltline      | intense      | / 5.00 | produced sound fit (+0.45)         |
+---+------------------+--------------+--------+------------------------------------+

Throwback Night Owl  [mode: genre-first]
  favorite_genre=synthwave, favorite_mood=moody, target_energy=0.6, likes_acoustic=False, desired_tags=['nostalgic', 'nocturnal', 'dreamy'], preferred_decade=1980, likes_instrumental=True, prefers_popular=False, likes_live=False
+---+---------------------+--------------+--------+-------------------------------------------------+
| # | Song                | Genre / Mood | Score  | Reasons                                         |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 1 | Night Drive Loop    | synthwave    | 6.58   | genre match: synthwave (+2.00)                  |
|   | by Neon Echo        | moody        | / 7.25 | mood match: moody (+1.00)                       |
|   |                     |              |        | energy 0.75 vs target 0.60 (+1.27)              |
|   |                     |              |        | produced sound fit (+0.39)                      |
|   |                     |              |        | mood tags: nostalgic, nocturnal, dreamy (+0.75) |
|   |                     |              |        | from the 1980s (+0.50)                          |
|   |                     |              |        | instrumental fit (+0.35)                        |
|   |                     |              |        | hidden-gem fit (popularity 63) (+0.09)          |
|   |                     |              |        | studio feel (+0.23)                             |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 2 | Midnight Coding     | lofi         | 2.64   | energy 0.42 vs target 0.60 (+1.23)              |
|   | by LoRoom           | chill        | / 7.25 | produced sound fit (+0.15)                      |
|   |                     |              |        | mood tags: nocturnal, dreamy (+0.50)            |
|   |                     |              |        | instrumental fit (+0.44)                        |
|   |                     |              |        | hidden-gem fit (popularity 61) (+0.10)          |
|   |                     |              |        | studio feel (+0.23)                             |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 3 | Coffee Shop Stories | jazz         | 2.33   | energy 0.37 vs target 0.60 (+1.16)              |
|   | by Slow Stereo      | relaxed      | / 7.25 | produced sound fit (+0.05)                      |
|   |                     |              |        | mood tags: nostalgic (+0.25)                    |
|   |                     |              |        | near your decade (1990s) (+0.25)                |
|   |                     |              |        | instrumental fit (+0.33)                        |
|   |                     |              |        | hidden-gem fit (popularity 44) (+0.14)          |
|   |                     |              |        | studio feel (+0.15)                             |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 4 | Dusty Porch Swing   | country      | 2.32   | energy 0.52 vs target 0.60 (+1.38)              |
|   | by The Wheelwrights | nostalgic    | / 7.25 | produced sound fit (+0.13)                      |
|   |                     |              |        | mood tags: nostalgic (+0.25)                    |
|   |                     |              |        | near your decade (1970s) (+0.25)                |
|   |                     |              |        | instrumental fit (+0.05)                        |
|   |                     |              |        | hidden-gem fit (popularity 52) (+0.12)          |
|   |                     |              |        | studio feel (+0.14)                             |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 5 | Island Breeze       | reggae       | 2.29   | energy 0.60 vs target 0.60 (+1.50)              |
|   | by Sol Roots        | uplifting    | / 7.25 | produced sound fit (+0.28)                      |
|   |                     |              |        | near your decade (1970s) (+0.25)                |
|   |                     |              |        | instrumental fit (+0.06)                        |
|   |                     |              |        | hidden-gem fit (popularity 57) (+0.11)          |
|   |                     |              |        | studio feel (+0.10)                             |
+---+---------------------+--------------+--------+-------------------------------------------------+
```

The High-Energy Pop results mostly match what I expected. Sunrise City is a near-perfect fit. Gym Hero comes second only because of its genre match, even though it's "intense", and it beats Rooftop Lights, which is happy with the right energy but labeled "indie pop". This is the genre-overweighting bias predicted above. See [model_card.md](model_card.md#7-evaluation) for the full evaluation.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

**Weight shift: energy doubled (1.5 → 3.0), genre halved (2.0 → 1.0).** The highest possible score goes from 5.0 to 5.5, and every score stays within it, so the math is still valid. I ran it by overriding the weights for one run. The code still uses the original weights.

| Profile | Before (top 3) | After (top 3) | Verdict |
|---|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights | Sunrise City, **Rooftop Lights**, Gym Hero | More accurate: the happy song now beats the intense one |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow | Midnight Coding, Library Rain, Focus Flow | Different, not better. Spacewalk Thoughts (ambient/chill) closes the gap from 2.78 to 4.10 but stays 4th |
| Deep Intense Rock | Storm Runner, Gym Hero, Pulse Reactor | same | No change |
| Sad Raver | Pulse Reactor, Storm Runner, Gym Hero | same | Still wrong: the only sad song stays out of the top 5 |
| K-Pop Fan | Rooftop Lights, Sunrise City, Concrete Crown | Rooftop Lights, Sunrise City, Night Drive Loop | Different: Island Breeze (reggae) enters at #5 and Storm Runner drops out |

Conclusion: lowering the genre weight helps when the genre label is too strict (pop vs. indie pop). It doesn't fix the deeper problem, which is that energy already outweighs mood, and the shift makes that worse.

## Stretch Features

**1. Advanced song features.** `songs.csv` has 5 new columns: `popularity`, `release_decade`, `mood_tags`, `instrumentalness` and `liveness`. Each has a matching optional user preference and its own scorer in `recommender.py` (see the feature table above). The "Throwback Night Owl" profile uses all of them.

**2. Scoring modes (Strategy pattern).** Each mode is a weight table over the same feature scorers. Switch modes with `--mode`.

| Feature | genre-first (default) | mood-first | energy-focused |
|---|---|---|---|
| genre | **2.0** | 0.75 | 0.75 |
| mood | 1.0 | **2.0** | 0.75 |
| mood tags | 0.75 | **1.5** | 0.5 |
| energy | 1.5 | 1.0 | **3.0** |
| acoustic | 0.5 | 0.5 | 0.75 |
| decade / instrumental | 0.5 / 0.5 | 0.5 / 0.5 | 0.25 / 0.5 |
| popularity / liveness | 0.25 / 0.25 | 0.25 / 0.25 | 0.25 / 0.25 |

Mood-first fixes the Sad Raver problem from my evaluation. The catalog's only sad song moves from 9th to 1st:

```
Loaded songs: 18

Sad Raver (conflict: sad mood, high energy)  [mode: mood-first]
  favorite_genre=edm, favorite_mood=sad, target_energy=0.9, likes_acoustic=False
+---+------------------+--------------+--------+------------------------------------+
| # | Song             | Genre / Mood | Score  | Reasons                            |
+---+------------------+--------------+--------+------------------------------------+
| 1 | Empty Platform   | folk         | 2.41   | mood match: sad (+2.00)            |
|   | by Hollow Pines  | sad          | / 4.25 | energy 0.25 vs target 0.90 (+0.35) |
|   |                  |              |        | produced sound fit (+0.06)         |
+---+------------------+--------------+--------+------------------------------------+
| 2 | Pulse Reactor    | edm          | 2.18   | genre match: edm (+0.75)           |
|   | by Kilowatt Kids | energetic    | / 4.25 | energy 0.95 vs target 0.90 (+0.95) |
|   |                  |              |        | produced sound fit (+0.48)         |
+---+------------------+--------------+--------+------------------------------------+
| 3 | Gym Hero         | pop          | 1.44   | energy 0.93 vs target 0.90 (+0.97) |
|   | by Max Pulse     | intense      | / 4.25 | produced sound fit (+0.47)         |
+---+------------------+--------------+--------+------------------------------------+
| 4 | Storm Runner     | rock         | 1.44   | energy 0.91 vs target 0.90 (+0.99) |
|   | by Voltline      | intense      | / 4.25 | produced sound fit (+0.45)         |
+---+------------------+--------------+--------+------------------------------------+
| 5 | Ironclad         | metal        | 1.42   | energy 0.97 vs target 0.90 (+0.93) |
|   | by Rust Prophet  | angry        | / 4.25 | produced sound fit (+0.48)         |
+---+------------------+--------------+--------+------------------------------------+
```

**3. Diversity penalty (`--diverse`).** Songs are picked one at a time. Each candidate loses 1.0 point for every song by the same artist already in the list, and 0.5 for every song in the same genre. For Chill Lofi, LoRoom's second song (Focus Flow) drops from #3 to #5, and the penalty shows up in the reasons:

```
Loaded songs: 18

Chill Lofi  [mode: genre-first, diverse]
  favorite_genre=lofi, favorite_mood=chill, target_energy=0.4, likes_acoustic=True
+---+---------------------+--------------+--------+-------------------------------------------------+
| # | Song                | Genre / Mood | Score  | Reasons                                         |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 1 | Library Rain        | lofi         | 4.85   | genre match: lofi (+2.00)                       |
|   | by Paper Lanterns   | chill        | / 5.00 | mood match: chill (+1.00)                       |
|   |                     |              |        | energy 0.35 vs target 0.40 (+1.42)              |
|   |                     |              |        | acoustic sound fit (+0.43)                      |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 2 | Midnight Coding     | lofi         | 4.32   | genre match: lofi (+2.00)                       |
|   | by LoRoom           | chill        | / 5.00 | mood match: chill (+1.00)                       |
|   |                     |              |        | energy 0.42 vs target 0.40 (+1.47)              |
|   |                     |              |        | acoustic sound fit (+0.35)                      |
|   |                     |              |        | diversity: genre lofi already listed (-0.50)    |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 3 | Spacewalk Thoughts  | ambient      | 2.78   | mood match: chill (+1.00)                       |
|   | by Orbit Bloom      | chill        | / 5.00 | energy 0.28 vs target 0.40 (+1.32)              |
|   |                     |              |        | acoustic sound fit (+0.46)                      |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 4 | Coffee Shop Stories | jazz         | 1.90   | energy 0.37 vs target 0.40 (+1.46)              |
|   | by Slow Stereo      | relaxed      | / 5.00 | acoustic sound fit (+0.45)                      |
+---+---------------------+--------------+--------+-------------------------------------------------+
| 5 | Focus Flow          | lofi         | 1.89   | genre match: lofi (+2.00)                       |
|   | by LoRoom           | focused      | / 5.00 | energy 0.40 vs target 0.40 (+1.50)              |
|   |                     |              |        | acoustic sound fit (+0.39)                      |
|   |                     |              |        | diversity: artist LoRoom already listed (-1.00) |
|   |                     |              |        | diversity: genre lofi already listed (-1.00)    |
+---+---------------------+--------------+--------+-------------------------------------------------+
```

**4. Summary table.** The output is a plain ASCII table, so no extra library is needed. Each row shows rank, title and artist, genre and mood, the score out of the maximum possible *for that profile*, and every reason on its own line.

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



