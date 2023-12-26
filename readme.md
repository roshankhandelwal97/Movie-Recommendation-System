# ANIMESUGGEST

## Personalized Anime Recommendations  Based on MyAnimeList.net Data

Data Source : https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database


---

## DESCRIPTION

This is a simple anime recommendation system that uses the collaborative filtering approach with the SVD algorithm from the Surprise library. The recommendation system takes user input for their favorite animes and their corresponding ratings, and then recommends top 10 animes based on their preferences.

---
## REQUIREMENTS

- Python 3.6 or later
- pandas
- matplotlib
- scikit-surprise
- tkinter (for GUI)

---
## INSTALLATION

The following libraries can be installed in the following manner.

```
pip install pandas scikit-surprise tkinter
```

---
## DATASET

- The recommendation system uses two CSV files, `anime.csv` and `rating.csv`, which contain the necessary anime and user rating data. 
- Make sure these files are located in the same directory as the script.


---
## HOW TO RUN

- Make sure you have the required libraries installed and the dataset CSV files are in the same directory as the script.
- Run the script using the following command in the terminal:

```
    python anime_recommendation.py
```

- The tkinter GUI will open. Enter the names and ratings for your three favorite animes.
- Click on the "Submit Ratings" button.
- The progress bar will show the progress of the recommendation process. Once it reaches 100%, the top 10 anime recommendations for you will be displayed.
- You can sort the recommendations by the number of episodes or by the number of members who have seen the anime using the "Sort by Episodes" and "Sort by Members" buttons.
  
---


## HOW TO USE THE AUTOCOMPLETE FEATURE

- The autocomplete feature helps you search for animes by providing a list of suggestions as you type. 
- To use the feature, simply start typing the name of the anime in the input field, and a list of matching animes will appear. 
- You can use the arrow keys to navigate through the suggestions and press Enter or double-click on a suggestion to select it.

---

## TROUBLESHOOTING

If you encounter any issues with the input fields or the recommendations, make sure that the dataset CSV files are located in the same directory as the script and that you have entered valid anime names and ratings.
