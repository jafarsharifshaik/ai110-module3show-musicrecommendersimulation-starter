# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

It's a small music recommender that matches songs to your "vibe": your favorite genre, your mood, how much energy you want, and whether you like acoustic sound.

---

## 2. Intended Use  

**Goal / task:** given one listener's taste, VibeFinder suggests the 5 songs from its catalog that fit best, with a short reason for each pick. It doesn't predict whether you'll *like* a song. It ranks songs by how closely they match what you said you want.

**Assumptions about the user:**
- They can describe their taste with one genre, one mood, a target energy (0 to 1) and a yes/no for acoustic.
- Their taste stays the same for the whole session.

**Intended use:**
- Classroom exploration of how content-based recommenders work.
- Trying out weights and profiles to see how the rankings shift.
- Learning where bias can come from in a simple scoring rule.

**Not intended for:**
- Real users or a real music app. The catalog is 18 made-up songs.
- Judging what music is "good". The score only measures fit to one profile.
- Making decisions about people, such as guessing someone's personality or mood from what they listen to.
- Any large catalog without retesting. The weights were tuned by eye on 18 songs.

---

## 3. How the Model Works  

Think of the recommender as a judge holding a scorecard. It looks at every song in the catalog, one at a time, and asks four questions about how well that song fits you:

1. **Is it your favorite genre?** If yes, the song gets 2 points. This is the biggest prize, because genre sets the overall sound.
2. **Is it the mood you're in?** If yes, it gets 1 point.
3. **Is its energy close to the energy you want?** Up to 1.5 points. A song that matches your target energy exactly gets all 1.5. The further away it is, too calm or too intense, the fewer points it gets. A louder or faster song doesn't win just for being louder or faster. It wins for being *closest* to what you asked for.
4. **Does it have the kind of sound you like?** Up to 0.5 points. If you like acoustic music, more acoustic songs earn more. If you don't, more produced, electronic-sounding songs earn more.

A perfect song scores 5 points. Every time a song earns points, the judge writes down a short reason, such as "genre match: pop (+2.0)", so you can see why it was picked.

After every song has a score, the recommender sorts them from highest to lowest and shows you the top five. It doesn't use other people's listening history, song lyrics, or popularity. It only compares each song's own attributes to your stated taste.

**Changes from the starter logic:** the starter returned the first five songs in the file, no matter who was asking. Now every song gets a real score, and the list comes back ranked with an explanation for each pick. I also added 8 songs in new genres and moods to the catalog.

---

## 4. Data  

- **Size:** 18 songs in `data/songs.csv`. The starter file had 10, and I added 8.
- **Features per song:** genre, mood, energy, tempo (bpm), valence (sad to happy), danceability and acousticness. All the numbers except tempo are on a 0 to 1 scale.
- **Genres (15):** pop, indie pop, lofi, rock, metal, ambient, jazz, synthwave, hip hop, classical, country, r&b, edm, reggae, folk.
- **Moods (14):** happy, chill, intense, relaxed, moody, focused, confident, peaceful, angry, nostalgic, romantic, energetic, uplifting, sad.
- **What I added:** 8 songs, each with a genre and mood that wasn't in the starter file, so the catalog now covers sad, angry, romantic and very calm music.

**Limits:**
- Most genres have only 1 song. Lofi has 3 and pop has 2.
- All songs, artists and numbers are made up. I picked the values, so they reflect my idea of what each genre sounds like.
- There are no lyrics, language, release year, popularity or listening history.
- Each song has only one genre and one mood label, but real songs often mix several.

---

## 5. Strengths  

- **It clearly separates opposite tastes.** High-Energy Pop and Chill Lofi share no songs at all. Neither do Chill Lofi and Deep Intense Rock.
- **Users whose genre is in the catalog get a good #1.** Sunrise City for pop, Library Rain for lofi and Storm Runner for rock all match my own intuition.
- **Energy closeness works well.** A calm listener never gets metal, and an intense listener never gets classical. Songs aren't rewarded just for being louder.
- **Every pick explains itself.** Each recommendation lists exactly where its points came from, such as "genre match: pop (+2.0)", so it's easy to see why something ranked high.
- **It still copes when the genre is missing.** The K-Pop Fan got a sensible happy, mid-energy list from mood and energy alone.

---

## 6. Limitations and Bias 

**Weakness found: high-energy users all get the same handful of songs.** The catalog has only five songs with energy above 0.8 (Sunrise City, Gym Hero, Storm Runner, Pulse Reactor, Ironclad), and most genres have just one song. So once a user's genre match is used up, the rest of their list is decided almost entirely by energy closeness. That means anyone who asks for high energy, whether they like rock, edm, metal or pop, gets the same five songs in a slightly different order. Sunrise City appeared in 5 of my 6 test profiles' top fives, and Gym Hero appeared in 4. This is a filter bubble created by a small catalog plus a scoring rule where energy is the strongest number. Mood can't break it either. A mood match is only worth 1 point, so the "Sad Raver" profile (sad mood, high energy) ranked the catalog's only sad song 9th out of 18.

Other limitations I noticed:

- **Exact text matching.** "indie pop" gets no genre credit from a "pop" fan, and a "k-pop" fan gets no genre points at all because no song uses that label.
- **Impossible preferences fail silently.** The "Acoustic Metalhead" profile wants acoustic, high-energy metal. No such song exists, so the acoustic preference just stops mattering, and the user is never told that.
- **One genre and one mood per user.** Real listeners have several favorites and change moods.

---

## 7. Evaluation  

**Profiles tested.** I tested three normal profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) and three edge cases designed to trick the scoring:

- **Sad Raver:** edm, sad mood, energy 0.9. The preferences conflict, because sad songs are usually calm.
- **Acoustic Metalhead:** metal, angry, energy 0.95, likes acoustic. The combination doesn't exist in the catalog.
- **K-Pop Fan:** a genre that no song in the catalog has.

I looked at each top 5 and asked whether it "felt" right. The full terminal output is in the README under *Sample Recommendation Output*.

**Why a song ranked first, for example Sunrise City for High-Energy Pop (4.88 / 5):** it earns all three big rewards at once. It's pop (+2.0), it's happy (+1.0), and its energy of 0.82 is almost exactly the 0.80 target (+1.47). It also adds +0.41 for being a produced, non-acoustic track. No other song gets both the genre and the mood points.

**Why Gym Hero keeps showing up for people who just want "Happy Pop":** the recommender doesn't really know what "happy" sounds like. It only checks whether the label matches. Gym Hero is labeled pop, and that alone is worth 2 points, which is twice what a mood match is worth. Its energy is also close to what a pop fan asks for. So Gym Hero, a workout song labeled "intense", gets 3.78 points. Rooftop Lights, a genuinely happy song, gets 2.77, because it's labeled "indie pop" and the computer treats that as a completely different genre. To a listener the two are close cousins. To the scoring rule they're strangers.

**What surprised me:**

- The edge cases didn't break anything loudly. They failed quietly. Each one got a confident-looking list that ignored part of what the user asked for.
- The Sad Raver got upbeat, intense songs. The one sad song (Empty Platform) ranked 9th. Its +1 mood point couldn't make up for being far too calm.
- The K-Pop Fan got a reasonable list (Rooftop Lights, Sunrise City). Mood and energy still worked as a backup when genre found nothing.

**Comparing pairs of profiles:**

- **High-Energy Pop vs. Chill Lofi:** no overlap at all. Pop gets bright, produced songs around energy 0.8. Lofi gets quiet, acoustic songs around 0.4. This makes sense because the profiles disagree on every feature, so the system clearly separates "pump-up" from "study music".
- **High-Energy Pop vs. Deep Intense Rock:** both lists share Gym Hero and Sunrise City. Rock puts Storm Runner first because it's the only rock song, then fills the list with other high-energy tracks. This makes sense, but it shows the small catalog: rock fans get pop songs because there's no more rock.
- **Chill Lofi vs. Deep Intense Rock:** opposite ends of the catalog with zero overlap. Lofi's list stays low-energy all the way down (Spacewalk Thoughts, Coffee Shop Stories), and rock's stays high-energy (Pulse Reactor, Ironclad). Energy closeness is working as intended. It pulls each user toward their own "volume level".
- **Deep Intense Rock vs. Sad Raver:** the exact same five songs (Storm Runner, Gym Hero, Pulse Reactor, Ironclad, Sunrise City), just reordered. The Sad Raver's edm genre lifts Pulse Reactor to first, but the "sad" mood changes nothing. That's the clearest sign that energy outweighs mood.
- **Sad Raver vs. Acoustic Metalhead:** the exact same five songs in a different order. Each profile has one preference that can't be satisfied (sad + high energy, acoustic + metal). Once that preference fails, both profiles reduce to "wants high energy", so they converge.
- **High-Energy Pop vs. K-Pop Fan:** both lists contain Sunrise City and Rooftop Lights, but Gym Hero, which is in the pop list only because of its genre, disappears for the K-Pop Fan. Without a genre match, the K-Pop Fan's mood (happy) and energy (0.7) carry the ranking, and Rooftop Lights edges ahead because its energy of 0.76 is closer to 0.7. This makes sense: removing the genre bonus lets the vibe features decide.

**Experiment: energy doubled, genre halved.** For High-Energy Pop, Rooftop Lights jumped above Gym Hero, which is more accurate. For Chill Lofi, the ambient chill song got much closer to the lofi songs but didn't pass them. For Sad Raver nothing improved, because a higher energy weight only drowns out mood even more. Overall the change made results *different* more often than *better*. See the README *Experiments You Tried* section for the table.

---

## 8. Future Work  

1. **Give partial credit for similar genres and moods.** For example, "indie pop" should count partly toward "pop", and "relaxed" partly toward "chill". This fixes the Gym Hero vs. Rooftop Lights problem.
2. **Add variety to the top 5.** Limit each artist (or each very-similar song) to one slot, so high-energy users don't all get the same five songs.
3. **Let users pick more than one genre or mood, and score valence too.** Valence would let "sad" actually pull in sad-sounding songs, instead of being drowned out by energy.

Also: warn the user when part of their profile can't be matched, such as acoustic metal or a genre that isn't in the catalog.

---

## 9. Personal Reflection  

**Biggest learning moment.** I thought the weights would be the hard part. But the Gym Hero result showed me that the *labels* matter just as much. One song called "indie pop" instead of "pop" lost 2 points and fell below a workout song for a happy-pop fan. The math was doing exactly what I told it to. The data just didn't say what I assumed it said.

**How AI tools helped, and when I double-checked.** The AI assistant was fast at the boring parts: reading the CSV, converting numbers, sorting, formatting the terminal output, and suggesting edge-case profiles I wouldn't have thought of, like "acoustic metal". I still had to check it:
- The first version of `main.py` crashed on `python -m src.main` because of an import path.
- Some of the written comparisons between profiles needed fixing, for example "almost the same list" when the two lists actually had the exact same five songs.
- I checked every claim against the real terminal output before keeping it.

**What surprised me.** It's just four additions per song and a sort, but the output *feels* like a real recommendation. That's mostly because each pick comes with a reason. The reasons make the list feel thoughtful, even when the ranking is wrong (the Sad Raver got a confident list with no sad songs). Explanations build trust, and that can be good or misleading.

**What I'd try next.**
- Partial credit for similar genres and moods.
- Using valence so that mood actually changes the results.
- A variety rule so the same few high-energy songs don't fill every list.

I'd also like to try a tiny bit of collaborative filtering with fake listening histories, to compare it with this purely content-based approach.
