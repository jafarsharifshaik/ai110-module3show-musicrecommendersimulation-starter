# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
