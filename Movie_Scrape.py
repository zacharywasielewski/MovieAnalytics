import pandas as pd
pd.options.display.max_columns = None
pd.options.display.max_rows = None
import numpy as np
import time
import datetime as dt
#parallelizing
#import multiprocessing as mp
#import pandas.util.testing as pdt

from tmdbv3api import TMDb, Movie, Person, Genre
tmdb = TMDb()
tmdb.api_key = 'c1d4f524f44bb186d370d13f856915d5'

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
    
def g(var, n=1):
    return(len([x for x in var if x == n]))
    
def g_null(var):
    return(len([x for x in var if x != 1 and x != 2]))
    
def end_time(start_time, df, movie_count=True):
    end_time = time.time()
    run_time = dt.timedelta(seconds=end_time - start_time)
    if movie_count==True:
        print("{} Movies in {}".format(len(df), run_time))
    else:
        print("Run time so far: {}".format(run_time))
    
def process(df):
    res = df.apply(fill_df, axis=1)
    return res

def create_df(input_df, input_name='ratings', cast_n=10):
    #is there a better way to do this?
    df = pd.DataFrame(columns = [
            #misc
            'Movie', 'Movie_ID', 'search_year', 'Release_Date', 
            'Watch_Date', 
            'Rating', 'Genres', 'Languages', 'Overview', 
            'Popularity', 'Vote_Avg', 'Prod_Company', 'Budget', 'Revenue', 
            'RunTime', 'Keywords',
            #directors
            'Directors', 'Director_Males', 
            'Director_Females', 'Director_UnknownGender', 
            'Director_Popularity_Avg', 'Director_Genders', 
            #producers
            'Producers', 'Producer_Males', 'Producer_Females', 
            'Producer_UnknownGender', 'Producer_Popularity_Avg', 
            'Producer_Genders', 'Executive_Producers', 
            #writers
            'Writers', 
            'Writer_Males', 'Writer_Females', 'Writer_UnknownGender', 
            'Writer_Popularity_Avg', 'Writer_Genders', 
            'Novel_Adapted', 
            #sound
            'Composers', 'Composer_Males', 
            'Composer_Females', 'Composer_UnknownGender', 
            'Composer_Popularity_Avg', 'Composer_Genders', 
            #cinematography
            'Cinematographers', 'Cinematographer_Males', 
            'Cinematographer_Females', 'Cinematographer_UnknownGender', 
            'Cinematographer_Popularity_Avg', 'Cinematographer_Genders',
            #cast
            'Top_{}_Cast'.format(cast_n), 'Top_Cast_Popularity_Avg', 'Top_Cast_Males', 
            'Top_Cast_Females', 'Top_Cast_UnknownGender', 'Top_Cast_Genders'
            ])
    
    if input_name == 'ratings':
        df['Movie'] = input_df['Name']
        df['search_year'] = input_df['Year']
        df['Watch_Date'] = input_df['Date']
        df['Rating'] = input_df['Rating']*2
    elif input_name == 'oscars':
        df['Movie'] = input_df['Title']
        df['search_year'] = input_df['Year']
    else:
        print("create_df function requires input_name='ratings' or input_name='oscars'")
#    df = df.set_index('Movie')
    return(df)
    
def fill_df(df, cast_n=10):
    genre_dict = genre_dict_create()
    not_found = []

    for i in range(len(df)):
        search_title = df.iloc[i]['Movie']
        search_year = df.iloc[i]['search_year']
        
        #remove tv show because they fail --need a more sophisticated fix
        if search_title == 'Squid Game': 
            continue
            
        else:
            if search_title in movie_title_map.keys():
                search_title = movie_title_map[search_title]
#            print(search_title, search_year)
            
        
        search = movie.search(search_title) #search for movies by title
        #find the first movie in the search that matches the release year
        res = None
        #search through all search results for the correct movie (by title and year)
        for result in search:
            try: #this release date may fail if the movie object doesn't have a release date -- hence the try/except
                ##adding and subtracting 1 year for weird issues like film festivals causing mismatches in release year
                if int(result.release_date[0:4]) == int(search_year) or int(result.release_date[0:4]) == int(search_year)+1 \
                or int(result.release_date[0:4]) == int(search_year)-1:
                    #if found, return the match for data extraction
                    res = result
                    break #exit search loop
                else:
                    continue
            except:
                continue
        
        #sometimes the movie still isn't found..
        if res == None:
            not_found.append(search_title)
        
        #extract all information
        else:   
            #movie information
            genres = res.genre_ids
            mapped_genres = list(map(genre_dict.get, genres))
            searchmovie_id = res.id
            language = res.original_language
#            title = res.title
            overview = Movie(searchmovie_id).details(movie_id=searchmovie_id).overview
            popularity = Movie(searchmovie_id).details(movie_id=searchmovie_id).popularity
            release_date = Movie(searchmovie_id).details(movie_id=searchmovie_id).release_date
            vote_average = Movie(searchmovie_id).details(movie_id=searchmovie_id).vote_average
            
            #added
            prod_companies = [prod_co['name'] for prod_co in Movie(searchmovie_id).details(movie_id=searchmovie_id).production_companies]
            budget = Movie(searchmovie_id).details(movie_id=searchmovie_id).budget
            rev = Movie(searchmovie_id).details(movie_id=searchmovie_id).revenue
            runtime = Movie(searchmovie_id).details(movie_id=searchmovie_id).runtime
            keywords = [x.name for x in Movie(searchmovie_id).details(movie_id=searchmovie_id).keywords.keywords]
            
            #Search for people from movie
            movie_credits = Movie(searchmovie_id).credits(movie_id=searchmovie_id)
            
            #directors information
            directors = [credit for credit in movie_credits.crew if credit['job'] == 'Director']
            dir_list, dir_gender, dir_pop, dir_pop_avg = [], [], [], None
            for director in directors:
                director_gender = director.gender
                director_name = director.name
                director_popularity = director.popularity
                #append info to lists
                dir_list.append(director_name)
                dir_gender.append(director_gender)
                dir_pop.append(director_popularity)
            dir_pop_avg = np.sum(dir_pop)/len(dir_pop) if len(dir_pop) else None
            
            #producers information
            producers = [credit for credit in movie_credits.crew if credit['job'] == 'Producer' 
                         or credit['job'] == 'Executive Producer']
            prod_list, exec_prod_list, prod_gender, prod_pop, prod_pop_avg = [], [], [], [], None
            for producer in producers:
                producer_name = producer.name
                producer_gender = producer.gender
                producer_popularity = producer.popularity
                #append info to lists
                if producer_name not in prod_list:
                    prod_list.append(producer_name)
                    prod_gender.append(producer_gender)
                    prod_pop.append(producer_popularity)
                #also, save executive producers
                if producer.job == 'Executive Producer':
                    exec_prod_list.append(producer_name)
            prod_pop_avg = np.sum(prod_pop)/len(prod_pop) if len(prod_pop) else None
            
            
            #writer information
            writers = [credit for credit in movie_credits.crew if credit['department'] == 'Writing']
            writers_list, writers_gender, writers_pop, novel_adapted, writers_pop_avg = [], [], [], 0, None
            for writer in writers:
                #flag if adapted from novel
                if writer.job == 'Novel':
                    novel_adapted = 1
                    
                writer_name = writer.name
                if writer_name not in writers_list:
                    writer_gender = writer.gender
                    writer_popularity = writer.popularity
                    #append info to lists
                    writers_list.append(writer_name)
                    writers_gender.append(writer_gender)
                    writers_pop.append(writer_popularity)
            writers_pop_avg = np.sum(writers_pop)/len(writers_pop) if len(writers_pop) else None
            
            #sound information
            sound_crew = [credit for credit in movie_credits.crew if credit['job'] == 'Music Producer' 
                          or credit['job'] == 'Original Music Composer']
            sound_list, sounds_gender, sound_pop, sound_pop_avg = [], [], [], None
            for sound in sound_crew:
                sound_name = sound.name
                if sound_name not in sound_list:
                    sound_gender = sound.gender
                    sound_popularity = sound.popularity
                    #append info to lists
                    sound_list.append(sound_name)
                    sounds_gender.append(sound_gender)
                    sound_pop.append(sound_popularity)
            sound_pop_avg = np.sum(sound_pop)/len(sound_pop) if len(sound_pop) else None
            
            #cinematography information
            cin_crew = [credit for credit in movie_credits.crew if credit['job'] == 'Director of Photography' 
                        or credit['job'] == 'Cinematographer']
            cin_list, cins_gender, cin_pop, cin_pop_avg = [], [], [], None
            for cin in cin_crew:
                cin_name = cin.name
                if cin_name not in cin_list:
                    cin_gender = cin.gender
                    cin_popularity = cin.popularity
                    #append info to lists
                    cin_list.append(cin_name)
                    cins_gender.append(cin_gender)
                    cin_pop.append(cin_popularity)
            cin_pop_avg = np.sum(cin_pop)/len(cin_pop) if len(cin_pop) else None
            
            #actors information
            cast = [credit for credit in movie_credits.cast]
            cast_list, cast_gender_list, cast_pop, cast_pop_avg = [], [], [], None
            for member in cast[0:cast_n]:
                cast_gender = member.gender
#                cast_character = member.character
                cast_name = member.name
                cast_popularity = member.popularity
#                cast_order = member.order
                cast_list.append(cast_name)
                cast_gender_list.append(cast_gender)
                cast_pop.append(cast_popularity)
            cast_pop_avg = np.sum(cast_pop)/len(cast_pop) if len(cast_pop) else None
            
            #fill row
            #misc
            df.at[df.index[i], 'Movie_ID'] = searchmovie_id
            df.at[df.index[i], 'Release_Date'] = release_date
            df.at[df.index[i], 'Genres'] = mapped_genres
            df.at[df.index[i], 'Languages'] = language
            df.at[df.index[i], 'Overview'] = overview
            df.at[df.index[i], 'Popularity'] = popularity
            df.at[df.index[i], 'Vote_Avg'] = vote_average
            df.at[df.index[i], 'Prod_Company'] = prod_companies
            df.at[df.index[i], 'Budget'] = budget
            df.at[df.index[i], 'Revenue'] = rev
            df.at[df.index[i], 'RunTime'] = runtime
            df.at[df.index[i], 'Keywords'] = keywords
            #directing
            df.at[df.index[i], 'Directors'] = dir_list
            df.at[df.index[i], 'Director_Males'] = g(dir_gender, n=2)
            df.at[df.index[i], 'Director_Females'] = g(dir_gender, n=1)
            df.at[df.index[i], 'Director_UnknownGender'] = g_null(dir_gender)
            df.at[df.index[i], 'Director_Popularity_Avg'] = dir_pop_avg
            df.at[df.index[i], 'Director_Genders'] = dir_gender
            #producing
            df.at[df.index[i], 'Producers'] = prod_list
            df.at[df.index[i], 'Producer_Males'] = g(prod_gender, n=2)
            df.at[df.index[i], 'Producer_Females'] = g(prod_gender, n=1)
            df.at[df.index[i], 'Producer_UnknownGender'] = g_null(prod_gender)
            df.at[df.index[i], 'Producer_Popularity_Avg'] = prod_pop_avg
            df.at[df.index[i], 'Producer_Genders'] = prod_gender
            df.at[df.index[i], 'Executive_Producers'] = exec_prod_list
            #writing
            df.at[df.index[i], 'Writers'] = writers_list
            df.at[df.index[i], 'Writer_Males'] = g(writers_gender, n=2)
            df.at[df.index[i], 'Writer_Females'] = g(writers_gender, n=1)
            df.at[df.index[i], 'Writer_UnknownGender'] = g_null(writers_gender)
            df.at[df.index[i], 'Writer_Popularity_Avg'] = writers_pop_avg
            df.at[df.index[i], 'Writer_Genders'] = writers_gender
            df.at[df.index[i], 'Novel_Adapted'] = novel_adapted
            #sound
            df.at[df.index[i], 'Composers'] = sound_list
            df.at[df.index[i], 'Composer_Males'] = g(sounds_gender, n=2)
            df.at[df.index[i], 'Composer_Females'] = g(sounds_gender, n=1)
            df.at[df.index[i], 'Composer_UnknownGender'] = g_null(sounds_gender)
            df.at[df.index[i], 'Composer_Popularity_Avg'] = sound_pop_avg
            df.at[df.index[i], 'Composer_Genders'] = sounds_gender
            #cinematography
            df.at[df.index[i], 'Cinematographers'] = cin_list
            df.at[df.index[i], 'Cinematographer_Males'] = g(cins_gender, n=2)
            df.at[df.index[i], 'Cinematographer_Females'] = g(cins_gender, n=1)
            df.at[df.index[i], 'Cinematographer_UnknownGender'] = g_null(cins_gender)
            df.at[df.index[i], 'Cinematographer_Popularity_Avg'] = cin_pop_avg
            df.at[df.index[i], 'Cinematographer_Genders'] = cins_gender
            #cast
            df.at[df.index[i], 'Top_{}_Cast'.format(cast_n)] = cast_list
            df.at[df.index[i], 'Top_Cast_Popularity_Avg'] = cast_pop_avg
            df.at[df.index[i], 'Top_Cast_Males'] = g(cast_gender_list, n=1)
            df.at[df.index[i], 'Top_Cast_Females'] = g(cast_gender_list, n=2)
            df.at[df.index[i], 'Top_Cast_UnknownGender'] = g_null(cast_gender_list)
            df.at[df.index[i], 'Top_Cast_Genders'] = cast_gender
            
            #print to confirm finished -- delete
#            print("   Scraped {}".format(df.index[i]))
            
    print("\n\nMovies Not Found: {}".format(not_found))
    return(df)

if __name__ == "__main__":
    #single path
    print('Importing and compiling LetterBoxd movie data')
    start_time = time.time()
    ratings = pd.read_csv('C:\\Users\\G672594\\Downloads\\letterboxd-zachwazowski\\ratings.csv')
    df = create_df(ratings)
    df = fill_df(df)
    end_time(start_time, df)
    
#    #parallelize code -- slower?
#    start_time = time.time()
#    ratings = pd.read_csv('C:\\Users\\G672594\\Downloads\\letterboxd-zachwazowski\\ratings.csv')
#    df = create_df(ratings)
#    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)" ##weird
#    p = mp.Pool(processes=4)
#    split_dfs = np.array_split(df,4)
#    start_time = time.time()
#    pool_results = p.map(fill_df, split_dfs)
#    p.close()
#    p.join()
#    df = pd.concat(pool_results, axis=0)
#    end_time(start_time, df)