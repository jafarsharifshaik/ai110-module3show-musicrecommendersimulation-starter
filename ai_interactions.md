# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked Claude Code (agent mode, in VS Code) to complete four stretch challenges in one multi-step task:
1. Add 5+ advanced song attributes and score them.
2. Add switchable scoring modes.
3. Add a diversity penalty.
4. Show the results as a summary table.

I asked it to work on a separate branch (`experiment/scoring-modes`) so the working genre-first version on `main` stayed safe.

**Prompts used:**

Main prompt (the challenge brief, pasted in full), key parts:

> "Introduce 5 or more complex attributes to your dataset that are not currently present in the baseline data, such as Song Popularity (0-100), Release Decade, or Detailed Mood Tags... Update both data/songs.csv and the scoring logic in src/recommender.py so scoring accounts for the new attributes."

> "Build two or more different ranking strategies (e.g., 'Genre-First,' 'Mood-First,' or 'Energy-Focused') so a user can switch between modes in main.py... brainstorm a design pattern (like a simple 'Strategy' pattern) that keeps your code modular."

> "Implement a 'Diversity Penalty' that prevents the recommender from suggesting too many songs from the same artist or genre... penalize a song's score if its artist is already present in the top recommendations list."

> "Display your top recommendations [in] a formatted table... the table must include the 'reasons' for each score."

**What did the agent generate or change?**

- **Created** the branch `experiment/scoring-modes`.
- **`data/songs.csv`:** added 5 columns: `popularity` (0–100), `release_decade`, `mood_tags` (semicolon-separated, e.g. `nostalgic;nocturnal;dreamy`), `instrumentalness` and `liveness`. The values were filled in for all 18 songs.
- **`src/recommender.py`:**
  - `load_songs` parses the new columns. Tags become a list.
  - Each feature has a small scorer function (`_score_genre`, `_score_tags`, `_score_decade`, ...) listed in `FEATURES`.
  - `SCORING_MODES` holds three weight tables.
  - `score_song` takes a `mode`.
  - `recommend_songs` takes `mode` and `diverse`.
  - `_diversify` applies a −1.0 artist / −0.5 genre penalty for each repeat.
  - `max_score` now counts only the preferences the user set.
  - `Song` and `UserProfile` gained the new fields, with defaults.
- **`src/main.py`:**
  - Added `--mode`, `--diverse`, `--profile` and `-k` flags (argparse).
  - Added a dependency-free ASCII `format_table` with stacked reasons.
  - Added a new "Throwback Night Owl" profile that uses every new attribute.
- **`tests/test_recommender.py`:** 5 new tests covering parsing, advanced-preference scoring, `max_score`, mood-first vs. genre-first, and the diversity penalty.
- **`README.md`:** updated the feature table, sample output and run commands, and added a Stretch Features section. It also fixed an unclosed code block left over from the starter README.
- **Commands run:** `python -m src.main` with each mode and flag, and `pytest`.

**What did you verify or fix manually?**

- **Backward compatibility:** the new preferences are optional, so the 6 original profiles should score exactly as before. The agent diffed every title and score in the top 5 of all six profiles against the earlier output. All 30 matched.
- **A test was wrong, not the code:** the first diversity test expected a penalized lofi song to drop below a jazz song. By hand, the penalized song still scored 3.0 vs. 2.5, so the test's expectation was wrong. The test scenario was fixed, and the penalty math was confirmed by hand: Focus Flow 3.89 − 1.0 (artist) − 1.0 (two lofi songs) = 1.89, which matches the output.
- **Results make sense:** mood-first moved the only sad song from 9th to 1st for the Sad Raver. In mood-first and energy-focused modes, Rooftop Lights beats Gym Hero for the happy-pop fan. Both are the fixes my evaluation asked for.
- **Things I still want to check myself:** whether the tag and decade values I accepted for each song feel right to me, and whether the energy-focused mode is useful or just noisy.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

**Strategy pattern**, in a lightweight, data-driven form. Each scoring mode is a strategy, expressed as a table of weights. The caller picks one by name at runtime (`--mode`).

**How did AI help you brainstorm or implement it?**

The challenge suggested Strategy. The AI compared three options:

1. **One class per mode** (`GenreFirstScorer`, `MoodFirstScorer`, ...), each with a `score()` method. This is the textbook Strategy pattern, but the three modes would repeat almost all of the same logic and differ only in their numbers.
2. **`if mode == ...` branches inside `score_song`.** Quick to write, but every new mode means editing the scoring function. That's not modular.
3. **Separate "what to measure" from "how much it matters".** Each feature is a small scorer function that returns a 0–1 fit and a reason. Each mode is just a dictionary of weights over those features.

We chose option 3. The modes really only differ in weights, so a weight table is the simplest form of the strategy. A new mode is one new dictionary, and a new feature is one function plus one line in `FEATURES`. The same structure also made `max_score` easy, because it just sums the weights of the features the user set.

**How does the pattern appear in your final code?**

- `src/recommender.py`, **`FEATURES`**: the list of `(feature name, preference key, scorer function)`.
- `src/recommender.py`, **`SCORING_MODES`**: the strategies (`genre-first`, `mood-first`, `energy-focused`).
- `src/recommender.py`, **`score_song(user_prefs, song, mode)`**: the context that runs the chosen strategy. It loops over the active features and multiplies each fit by that mode's weight.
- `src/main.py`, **`--mode` flag**: where the user picks the strategy at runtime.
