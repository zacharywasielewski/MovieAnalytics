import pandas as pd
pd.options.display.max_columns = None
pd.options.display.max_rows = None
import numpy as np
from pprint import pprint

from tmdbv3api import TMDb, Movie, Person, Genre
tmdb = TMDb()
tmdb.api_key = 'c1d4f524f44bb186d370d13f856915d5'

movie = Movie()
person = Person()
genre = Genre()

genre_dict = {}
for i in genre.movie_list():
    genre_dict[i.id] = i.name

ratings = pd.read_csv('C:\\Users\\G672594\\Downloads\\letterboxd-zachwazowski\\ratings.csv')

#is there a better way to do this?
movie_dataframe = pd.DataFrame(columns = ['Movie', 'Release_Date', 'Watch_Date', 'Rating', 'Genres', 'Languages', 'Overview', 'Popularity', 'Vote_Avg',
                                          'Directors', 'Director_Males', 'Director_Females', 'Director_UnknownGender', 'Director_Popularity_Avg', 'Director_Genders', 
                                          'Producers', 'Producer_Males', 'Producer_Females', 'Producer_UnknownGender', 'Producer_Popularity_Avg', 'Producer_Genders', 'Executive_Producers',
                                          'Writers', 'Writer_Males', 'Writer_Females', 'Writer_UnknownGender', 'Writer_Popularity_Avg', 'Writer_Genders', 'Novel_Adapted',
                                          'Composers', 'Composer_Males', 'Composer_Females', 'Composer_UnknownGender', 'Composer_Popularity_Avg', 'Composer_Genders',
                                          'Cinematographers', 'Cinematographer_Males', 'Cinematographer_Females', 'Cinematographer_UnknownGender', 'Cinematographer_Popularity_Avg', 'Cinematographer_Genders',
                                          'Top_10_Cast', 'Top_Cast_Popularity_Avg', 'Top_Cast_Males', 'Top_Cast_Females', 'Top_Cast_UnknownGender', 'Top_Cast_Genders'
                                          ])
    
not_found = []

for i in range(len(ratings)):
    search_title = ratings.iloc[i]['Name']
    search_year = ratings.iloc[i]['Year']
    watch_date = ratings.iloc[i]['Date']
    rating = ratings.iloc[i]['Rating']*2
    
    #remove tv show because they fail --need a more sophisticated fix
    if search_title == 'Squid Game': 
        continue
    
    #Lamb breaks because TMDB stores it as it's icelandic name
    elif search_title == 'Lamb':
        search_title = 'Dýrið'
        print('Lamb (Dýrið)', search_year)
        
    else:
        print(search_title, search_year)
        
    search = movie.search(search_title) #search for movies by title
    
    #find the first movie in the search that matches the release year
    res = None
    
    #search through all search results for the correct movie (by title and year)
    for result in search:
        
        try: #this release date may fail if the movie object doesn't have a release date -- hence the try/except
            
            ##adding and subtracting 1 year for weird issues like film festivals causing mismatches in release year
            if int(result.release_date[0:4]) == int(search_year) or int(result.release_date[0:4]) == int(search_year)+1 or int(result.release_date[0:4]) == int(search_year)-1:
                    
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
        title = res.title
        overview = res.overview
        popularity = res.popularity
        release_date = res.release_date
        vote_average = res.vote_average
        
        #Search for people from movie
        movie_credits = Movie(searchmovie_id).credits(movie_id=searchmovie_id)
        
        #directors information
        directors = [credit for credit in movie_credits.crew if credit['job'] == 'Director']
        dir_list = []
        dir_gender = []
        dir_pop = []
        dir_pop_avg = None
        for director in directors:
            director_gender = director.gender
            director_id = director.id
            director_name = director.name
            director_popularity = director.popularity
            #append info to lists
            dir_list.append(director_name)
            dir_gender.append(director_gender)
            dir_pop.append(director_popularity)
        dir_pop_avg = np.sum(dir_pop)/len(dir_pop)
        
        #producers information
        producers = [credit for credit in movie_credits.crew if credit['job'] == 'Producer' or credit['job'] == 'Executive Producer']
        prod_list = []
        exec_prod_list = []
        prod_gender = []
        prod_pop = []
        prod_pop_avg = None
        for producer in producers:
            producer_name = producer.name
            producer_gender = producer.gender
            producer_id = producer.id
            producer_popularity = producer.popularity
            #append info to lists
            if producer_name not in prod_list:
                prod_list.append(producer_name)
                prod_gender.append(producer_gender)
                prod_pop.append(producer_popularity)
            #also, save executive producers
            if producer.job == 'Executive Producer':
                exec_prod_list.append(producer_name)
        prod_pop_avg = np.sum(prod_pop)/len(prod_pop)

        #writer information
        writers = [credit for credit in movie_credits.crew if credit['department'] == 'Writing']
        writers_list = []
        writers_gender = []
        writers_pop = []
        novel_adapted = 0
        writers_pop_avg = None
        for writer in writers:
            #flag if adapted from novel
            if writer.job == 'Novel':
                novel_adapted = 1
                
            writer_name = writer.name
            if writer_name not in writers_list:
                writer_gender = writer.gender
                writer_id = writer.id
                writer_popularity = writer.popularity
                #append info to lists
                writers_list.append(writer_name)
                writers_gender.append(writer_gender)
                writers_pop.append(writer_popularity)
        writers_pop_avg = np.sum(writers_pop)/len(writers_pop)
        
        #sound information
        sound_crew = [credit for credit in movie_credits.crew if credit['job'] == 'Music Producer' or credit['job'] == 'Original Music Composer']
        sound_list = []
        sounds_gender = []
        sound_pop = []
        sound_pop_avg = None
        for sound in sound_crew:
            sound_name = sound.name
            if sound_name not in sound_list:
                sound_gender = sound.gender
                sound_id = sound.id
                sound_popularity = sound.popularity
                #append info to lists
                sound_list.append(sound_name)
                sounds_gender.append(sound_gender)
                sound_pop.append(sound_popularity)
        sound_pop_avg = np.sum(sound_pop)/len(sound_pop)
        
        #cinematography information
        cin_crew = [credit for credit in movie_credits.crew if credit['job'] == 'Director of Photography' or credit['job'] == 'Cinematographer']
        cin_list = []
        cins_gender = []
        cin_pop = []
        cin_pop_avg = None
        for cin in cin_crew:
            cin_name = cin.name
            if cin_name not in cin_list:
                cin_gender = cin.gender
                cin_id = cin.id
                cin_popularity = cin.popularity
                #append info to lists
                cin_list.append(cin_name)
                cins_gender.append(cin_gender)
                cin_pop.append(cin_popularity)
        cin_pop_avg = np.sum(cin_pop)/len(cin_pop)
        
        #actors information
        cast = [credit for credit in movie_credits.cast]
        cast_list = []
        cast_gender_list = []
        cast_pop = []
        cast_pop_avg = None
        for member in cast[0:10]:
            cast_gender = member.gender
            cast_character = member.character
            cast_name = member.name
            cast_id = member.id
            cast_popularity = member.popularity
            cast_order = member.order
            cast_list.append(cast_name)
            cast_gender_list.append(cast_gender)
            cast_pop.append(cast_popularity)
        cast_pop_avg = np.sum(cast_pop)/len(cast_pop)
        
        ## add in production companies (add budget, etc)
        movie_details = Movie(searchmovie_id).details(movie_id=searchmovie_id).production_companies
        
        #appending the row to our DF
        movie_dataframe.loc[-1] = [search_title, release_date, watch_date, rating, mapped_genres, language, overview, popularity, vote_average,
                               dir_list, len([x for x in dir_gender if x == 2]), len([x for x in dir_gender if x == 1]), len([x for x in dir_gender if x != 1 and x != 2]), dir_pop_avg, dir_gender,
                               prod_list, len([x for x in prod_gender if x == 2]), len([x for x in prod_gender if x == 1]), len([x for x in prod_gender if x != 1 and x != 2]), prod_pop_avg, prod_gender, exec_prod_list,
                               writers_list, len([x for x in writers_gender if x == 2]), len([x for x in writers_gender if x == 1]), len([x for x in writers_gender if x != 1 and x != 2]), writers_pop_avg, writers_gender, novel_adapted, 
                               sound_list, len([x for x in sounds_gender if x == 2]), len([x for x in sounds_gender if x == 1]), len([x for x in sounds_gender if x != 1 and x != 2]), sound_pop_avg, sounds_gender,
                               cin_list, len([x for x in cins_gender if x == 2]), len([x for x in cins_gender if x == 1]), len([x for x in cins_gender if x != 1 and x != 2]), cin_pop_avg, cins_gender,
                               cast_list, cast_pop_avg, len([x for x in cast_gender_list if x == 2]), len([x for x in cast_gender_list if x == 1]), len([x for x in cast_gender_list if x != 1 and x != 2]), cast_gender_list
                              ]
        movie_dataframe.index = movie_dataframe.index + 1  # shifting index
        
        print("   Scraped!")
    

print("\n\nMovies Not Found: {}".format(not_found))