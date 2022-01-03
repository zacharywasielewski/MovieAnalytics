# Movie Analytics - Requirements:
- Python
  - pandas
  - numpy
  - time
  - datetime
  - urllib
  - re
  - bs4
  - sklearn
  - seaborn
  - matplotlib
  - tmdbv3api (the movie database API)
- The Movie DataBase (TMDB) API key
  - https://developers.themoviedb.org/3/getting-started/introduction
- Letterboxd Ratings CSV Export
  - https://letterboxd.com/settings/data/

# Movie Analytics - How to:
1. Download your Letterboxd ratings zip file and extract the ratings CSV.
- This will be the training set of the model building, so the more ratings you have the better.
- This ratings.csv path will go into the if \_\_name__ == "\_\_main__" section at the bottom of Movie_Scrape.py

2. Acquire a TMDB api key and insert into the Movie_Scrape.py file
- This will be what is used to acquire information about all of the train/test/application movies, so if you don't do this, keep mine. :)

3. Run Movie_Scrape.py
- This script will pull in your Letterboxd csv and create a wide dataset of all of the information extracted from TMDB.
- Depending on how many movies you have rated, timing can vary. 400 movies takes a few minutes, 4000 takes nearly an hour.
- This will output a pandas dataframe, df, which has all of the movies that the TMDB scraper could find. This will be your training dataset.

4. Once Movie_Scrape.py has finished running, run Oscars_BeautifulSoup.py
- This script scrapes Oscars.org to pull in all movies that have ever been nominated or won an Academy Award.
- After cleaning this nomination/winning data {0:not nominated, 1:nominated/didn't win, 2: won}, the script will import Movie_Scrape.py functions to exctract the same TMDB information.
- This will take roughly 40 minutes to run mostly due to the TMDB API data fill (parallelization in task queue).
- The important output of this script is two pandas dataframes, oscars_awards and oscars_test.
  - oscars_awards: Oscar nominated movie dataframe where the movie_id is appended to the movie name, year, and award information (used to add awards information to the training dataset)
  - oscars_test:Oscar nominated movie dataframe with TMDB data AND awards information

5. Finally, run Build_Prediction_Model.py
- This script adds the awards information to the training df, cleans/encodes the categorical variables for both df and oscars_test, and subsets encoded vars to only include binary vars present in >2% of training movies.
- The model built is a ridge regression model using 80/20 split of the training df.
- This model is then applied to the oscars df to create predictions (ceiling=10, floor=0) and sort them from highest rating to lowest rating.
- Code takes ~1 minute to run
