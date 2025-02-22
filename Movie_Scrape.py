import pandas as pd
import dotenv
import numpy as np
import time
import datetime as dt
import os
import asyncio
from tmdbv3api import TMDb, Movie, Person, Genre
from tqdm.asyncio import tqdm

dotenv.load_dotenv()
tmdb = TMDb()
tmdb.api_key = os.environ.get("TMDB_API_KEY")

pd.options.display.max_columns = None
pd.options.display.max_rows = None

movie = Movie()
person = Person()
genre = Genre()

movie_title_map = {
        'Lamb':'Dýrið',
        'Raw':'Grave',
        'Star Wars':'Star Wars ' ## TEMPORARY BUG?
        }

def genre_dict_create():
    genre_dict = {}
    for i in genre.movie_list():
        genre_dict[i.id] = i.name
    return(genre_dict)

def valid_year(result, year):
    """Helper to validate release year with a +/- 1 tolerance."""
    try:
        release_year = int(getattr(result, 'release_date', '')[:4]) if getattr(result, 'release_date', None) else None
        return release_year in {year, year - 1, year + 1}
    except (TypeError, ValueError):
        return False

def process_crew(crew):
    """Process director, producer, writer, and other crew details."""
    def crew_info(job):
        return [c for c in crew if c['job'] == job]

    directors = crew_info('Director')
    producers = crew_info('Producer')

    return {
        'Directors': [d.name for d in directors],
        'Producers': [p.name for p in producers],
    }

def process_cast(cast, cast_n):
    """Process the top N cast members."""
    cast_info = list(cast)[:cast_n]
    return {
        'Top_Cast': [c.name for c in cast_info],
        'Top_Cast_Popularity_Avg': np.mean([c.popularity for c in cast_info]) if cast_info else None,
    }

async def movie_search_async(title, year, genres, cast_n=10):
    """
    Async parallelized version of movie search.
    """
    not_found = []
    search = await asyncio.to_thread(movie.search, title)

    res = next((result for result in search if valid_year(result, year)), None)

    if res is None:
        not_found.append(title)
        return not_found

    return await extract_movie_data_async(res, genres, cast_n)

async def extract_movie_data_async(res, genres, cast_n):
    """Extract movie data using async tasks."""
    movie_id = res.id

    details_task = asyncio.to_thread(Movie(movie_id).details, movie_id)
    credits_task = asyncio.to_thread(Movie(movie_id).credits, movie_id)

    movie_details, credits = await asyncio.gather(details_task, credits_task)

    data = {
        'Movie_ID': movie_id,
        'Title': res.title,
        'Genres': [genres.get(g) for g in res.genre_ids],
        'Language': res.original_language,
        'Overview': movie_details.overview,
        'Popularity': movie_details.popularity,
        'Release_Date': movie_details.release_date,
        'Vote_Avg': movie_details.vote_average,
        'Budget': movie_details.budget,
        'Revenue': movie_details.revenue,
        'Runtime': movie_details.runtime,
        'Keywords': [k.name for k in movie_details.keywords.keywords],
    }

    data.update(process_crew(credits.crew))
    data.update(process_cast(credits.cast, cast_n))

    return data

async def fill_df_async(df, genres):
    """Async function to process multiple movies in parallel."""
    tasks = [movie_search_async(row['Name'], row['Year'], genres) for _, row in df.iterrows()]
    results = []
    for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Processing Movies"):
        results.append(await task)
    return results

if __name__ == '__main__':

    print("Downloading Ratings...")
    ratings = pd.read_csv(os.environ.get('RATINGS_PATH'))
    parallel_results = asyncio.run(fill_df_async(ratings, genre_dict_create()))

    print(len(parallel_results))
