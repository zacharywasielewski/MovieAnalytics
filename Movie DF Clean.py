import pandas as pd


#encode categorical variables
dummy_cols = ['Languages','Genres','Directors','Producers','Executive_Producers',
              'Writers','Composers','Cinematographers','Top_10_Cast']
movie_dataframe2 = movie_dataframe #pull movie_dataframe from other script
for col in dummy_cols:
    s = movie_dataframe2[col]
    temp = pd.get_dummies(s.apply(pd.Series).stack(), prefix=col).sum(level=0)
    movie_dataframe2 = pd.concat([movie_dataframe2, temp], axis=1)
    movie_dataframe2 = movie_dataframe2[[x for x in movie_dataframe2.columns if x != col]]

#subset encoded columns to only columns where sum >= 3
df_sum = movie_dataframe2.sum(numeric_only = True)
df_rem_list = list(df_sum[df_sum < 3].index) 
movie_dataframe3 = movie_dataframe2[[x for x in movie_dataframe2.columns if x not in df_rem_list]]

#remove genders 'list' columns
movie_dataframe3 = movie_dataframe3[[x for x in movie_dataframe3.columns if x[-8:] != '_Genders']]

#remove misc vars (unused for now!)
movie_dataframe3 = movie_dataframe3[[x for x in movie_dataframe3.columns if x not in ['Release_Date','Watch_Date','Overview']]]

#assign index as Movie
movie_dataframe3 = movie_dataframe3.set_index('Movie')

#fill nulls
movie_dataframe3 = movie_dataframe3.fillna(0)



#Hayley code -remove later
#movie_dataframe3.loc[(movie_dataframe3['Genres_Comedy'] == 1) & (movie_dataframe3['Top_Cast_Popularity_Avg']<1000000)][['Rating','Vote_Avg']].describe()

print(movie_dataframe.loc[movie_dataframe['Overview'].str.contains('boo',case=False)][['Overview']])
