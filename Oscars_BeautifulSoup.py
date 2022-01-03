# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 14:36:40 2021

@author: G672594
"""

import urllib
import re
from bs4 import BeautifulSoup
import pandas as pd
from Movie_Scrape import end_time, create_df, fill_df
import time
import numpy as np
#from multiprocessing import Pool

def create_oscars_df(start_year=1929, end_year=2030):
    awards_df = pd.DataFrame(columns=['Title', 'Year', 'Award', 'Winner'])
    title_keep = ['Actor', 'Actress', 'Actor in a Supporting Role',
                  'Actress in a Supporting Role', 'Actor in a Leading Role', 
                  'Actress in a Leading Role'
                  ]
    for i in range(start_year, end_year+1):
        source = urllib.request.urlopen('https://www.oscars.org/oscars/ceremonies/{}'.format(i)).read()
        soup = BeautifulSoup(source,'lxml')
        text_scrape = soup.find_all('div', class_= "view-grouping")
        for section in text_scrape:
            award = section.find_all('div', class_= "view-grouping-header")[0].get_text()
            if len(award) <= 3: #breaks when entering a new section -- all movies scraped
                break
            nominees = section.find_all('div', class_= re.compile("views-row.*"))
            first = 0
            for nominee in nominees:
                first += 1
                if first == 1:
                    winner = 1
                else:
                    winner = 0
                title = nominee.find_all('div', class_= "views-field views-field-title")[0].get_text().strip()
                name = nominee.find_all('div', class_= "views-field views-field-field-actor-name")[0].get_text()
                if award == 'Music (Original Song)' and 'from' in title:
                    awards_df.loc[len(awards_df)] = [title.split(';')[0].split('from ')[1], i, award, winner]
                elif title.strip() != '' and award in title_keep:
                    awards_df.loc[len(awards_df)] = [title.strip(), i, award, winner]
                elif name.strip() != '':
                    awards_df.loc[len(awards_df)] = [name.strip(), i, award, winner]
    awards_df_mapped = merge_awards(awards_df)
    return(awards_df_mapped)
                    
def merge_awards(df, col="Award"):
    
    awards_dict = {
            #Acting
            "Actor in a Leading Role":"Actor", 
            "Actor in a Supporting Role":"Actor",
            "Actress in a Supporting Role":"Actress", 
            "Actress in a Leading Role":"Actress",
            #Animated
            "Animated Feature Film":"Animated",
            #Production Design
            "Art Direction (Black-and-White)":	"Production Design", 
            "Art Direction (Color)":"Production Design", 
            "Unique and Artistic Picture":"Production Design", 
            "Art Direction":"Production Design",
            #Directing
            "Assistant Director":"Directing", 
            "Directing (Comedy Picture)":"Directing", 
            "Directing (Dramatic Picture)":"Directing", 
            #Best Picture
            "Best Motion Picture":"Best Picture", 
            "Outstanding Motion Picture":"Best Picture", 
            "Outstanding Picture":"Best Picture", 
            "Outstanding Production":"Best Picture", 
            #Cinematography
            "Cinematography (Black-and-White)":"Cinematography", 
            "Cinematography (Color)":"Cinematography",
            #Costume
            "Costume Design (Black-and-White)"	:"Costume Design", 
            "Costume Design (Color)":"Costume Design", 
            #Documentary
            "Documentary (Feature)": "Documentary",
            "Documentary (Short Subject)": "Documentary",
            #Visual Effects
            "Engineering Effects":"Visual Effects", 
            "Special Effects":"Visual Effects", 
            "Special Visual Effects":"Visual Effects", 
            #International Film
            "Foreign Language Film":"International Feature Film", 
            "Special Foreign Language Film Award":"International Feature Film", 
            #Honorary Award
            "Honorary Foreign Language Film Award":"Honorary Award",
            #Music (Score)
            "Music (Adaptation Score)":"Music (Score)",
            "Music (Music Score of a Dramatic or Comedy Picture)":"Music (Score)", 
            "Music (Music Score of a Dramatic Picture)":"Music (Score)", 
            "Music (Music Score--substantially original)":"Music (Score)", 
            "Music (Original Dramatic Score)":"Music (Score)", 
            "Music (Original Music Score)":"Music (Score)", 
            "Music (Original Musical or Comedy Score)":"Music (Score)", 
            "Music (Original Score)":"Music (Score)", 
            "Music (Original Score--for a motion picture [not a musical])":"Music (Score)", 
            "Music (Original Song Score and Its Adaptation or Adaptation Score)":"Music (Score)", 
            "Music (Original Song Score and Its Adaptation -or- Adaptation Score)":"Music (Score)", 
            "Music (Original Song Score or Adaptation Score)":"Music (Score)", 
            "Music (Original Song Score)":"Music (Score)", 
            "Music (Original Dramatic Score)":"Music (Score)", 
            "Music (Original Music Score)":"Music (Score)", 
            "Music (Original Musical or Comedy Score)":"Music (Score)", 
            "Music (Original Score)":"Music (Score)", 
            "Music (Original Score--for a motion picture [not a musical])":"Music (Score)", 
            "Music (Original Song Score and Its Adaptation or Adaptation Score)":"Music (Score)", 
            "Music (Original Song Score and Its Adaptation -or- Adaptation Score)":"Music (Score)", 
            "Music (Original Song Score or Adaptation Score)":"Music (Score)", 
            "Music (Original Song Score)":"Music (Score)", 
            "Music (Score of a Musical Picture--original or adaptation)":"Music (Score)", 
            "Music (Scoring of a Musical Picture)":"Music (Score)", 
            "Music (Scoring of Music--adaptation or treatment)":"Music (Score)", 
            "Music (Scoring)":"Music (Score)", 
            "Music (Scoring: Adaptation and Original Song Score)":"Music (Score)", 
            "Music (Scoring: Original Song Score and Adaptation -or- Scoring: Adaptation)":"Music (Score)", 
            #Music (Song)
            "Music (Original Song)":"Music (Song)", 
            "Music (Song--Original for the Picture)":"Music (Song)", 
            #Makeup
            "Makeup":"Makeup and Hairstyling",
            #Short Film
            "Short Film (Animated)":"Short Film", 
            "Short Film (Dramatic Live Action)":"Short Film",
            "Short Film (Live Action)":"Short Film",
            "Short Subject (Animated)":"Short Film", 
            "Short Subject (Cartoon)":"Short Film", 
            "Short Subject (Color)":"Short Film", 
            "Short Subject (Comedy)":"Short Film", 
            "Short Subject (Live Action)":"Short Film", 
            "Short Subject (Novelty)":"Short Film", 
            "Short Subject (One-reel)":"Short Film", 
            "Short Subject (Two-reel)":"Short Film", 
            #Sound
            "Sound Editing":"Sound", "Sound Effects Editing":"Sound", 
            "Sound Effects":"Sound", "Sound Mixing":"Sound", 
            "Sound Recording":"Sound", 
            #Special Achievement
            "Special Achievement Award (Sound Editing)":"Special Achievement", 
            "Special Achievement Award (Sound Effects Editing)":"Special Achievement", 
            "Special Achievement Award (Sound Effects)":"Special Achievement", 
            "Special Achievement Award (Visual Effects)":"Special Achievement", 
            "Special Achievement Award":"Special Achievement", 
            "Special Award":"Special Achievement", 
            #Writing (Adapted)
            "Writing (Adaptation)":"Writing (Adapted)", 
            "Writing (Adapted Screenplay)":"Writing (Adapted)", 
            "Writing (Screenplay Adapted from Other Material)":"Writing (Adapted)", 
            "Writing (Screenplay Based on Material from Another Medium)":"Writing (Adapted)", 
            "Writing (Screenplay Based on Material Previously Produced or Published)":"Writing (Adapted)", 
            "Writing (Screenplay--Adapted)":"Writing (Adapted)", 
            "Writing (Screenplay--based on material from another medium)":"Writing (Adapted)", 
            #Writing (Original)
            "Writing (Original Motion Picture Story)":"Writing (Original)", 
            "Writing (Original Screenplay)":"Writing (Original)", 
            "Writing (Original Story)":"Writing (Original)", 
            "Writing (Motion Picture Story)":"Writing (Original)", 
            "Writing (Screenplay Written Directly for the Screen)":"Writing (Original)", 
            "Writing (Screenplay Written Directly for the Screen--based on factual material or on story material not previously published or produced)":"Writing (Original)", 
            "Writing (Screenplay)":"Writing (Original)", 
            "Writing (Screenplay--Original)":"Writing (Original)", 
            "Writing (Story and Screenplay)":"Writing (Original)", 
            "Writing (Story and Screenplay--based on factual material or material not previously published or produced)":"Writing (Original)", 
            "Writing (Story and Screenplay--based on material not previously published or produced)":"Writing (Original)", 
            "Writing (Story and Screenplay--written directly for the screen)":"Writing (Original)", 
            "Writing (Title Writing)":"Writing (Original)", 
            "Writing":"Writing (Original)"
            }
    
    df2 = df.replace(awards_dict)
    return(df2)
    
def create_wide_df(df):
    df2 = pd.get_dummies(df, prefix='', prefix_sep='', columns=['Award'])
    cols = [x for x in list(df.Award.unique())]
    df2.loc[df2['Winner'] == 1, cols] = df2.loc[df2['Winner'] == 1, [x for x in list(df.Award.unique())]]*2
    df3 = df2[[x for x in df2.columns if x != 'Winner']].groupby(['Title','Year'], as_index=False).max()
    return(df3)
    
#def parallelize_df(df, func, n_cores=4):
#    df_split = np.array_split(df, n_cores)
#    pool = Pool(n_cores)
#    df = pd.concat(pool.map(func, df_split))
#    pool.close()
#    pool.join()
#    return(df)

if __name__ == "__main__":
    print("Scraping oscars movies from Oscars.org")
    start_time = time.time()
    awards_df = create_oscars_df()
    unique_df = awards_df[['Title','Year']].drop_duplicates()
    oscars_dummied_df = create_wide_df(awards_df)
    end_time(start_time, oscars_dummied_df, movie_count=False)
    
    ##straight path
    print("Compiling TMDB movie data from oscars movies")
    start_time = time.time()
    oscars_test = create_df(oscars_dummied_df, input_name='oscars')
    oscars_test = fill_df(oscars_test)
    oscars_test = oscars_test.loc[np.invert(oscars_test['Movie_ID'].isna())]
    end_time(start_time, oscars_test)
    ##4988 Movies in 0:40:16.947360
    ##try parallelized code!
    
    ##join Movie_ID to oscars award data
    ##duplicate issue!!
    oscars_awards = oscars_dummied_df.merge(oscars_test[['Movie','search_year','Movie_ID']], left_on=['Title', 'Year'], right_on=['Movie','search_year'], how='left')
    oscars_awards = oscars_awards.loc[np.invert(oscars_awards.Movie_ID.isna())]
    oscars_test = oscars_test.merge(oscars_awards[[x for x in oscars_awards.columns if x not in ['Title', 'Year', 'Movie']]], on=['Movie_ID', 'search_year'], how='left')