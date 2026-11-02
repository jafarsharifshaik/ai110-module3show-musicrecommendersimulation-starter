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

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

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
