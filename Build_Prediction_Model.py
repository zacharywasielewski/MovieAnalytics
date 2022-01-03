import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn import metrics
import seaborn as sn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.options.display.float_format = '{:,.0f}'.format

def encode_categorical(df):
    #encode categorical variables
    dummy_cols = ['Languages','Genres','Directors','Producers','Executive_Producers',
                  'Writers','Composers','Cinematographers','Top_10_Cast', 'Keywords',
                  'Prod_Company']
    df_dummy = df #pull movie_dataframe from other script
    for col in dummy_cols:
        s = df_dummy[col]
        temp = pd.get_dummies(s.apply(pd.Series).stack(), prefix=col).sum(level=0)
        df_dummy = pd.concat([df_dummy, temp], axis=1)
        df_dummy = df_dummy[[x for x in df_dummy.columns if x != col]]
    
    return(df_dummy)

def subset_encoded_cols(df, n=3): # n is minimum count of column to keep it
    df_sum = df.sum(numeric_only = True)
    df_rem_list = list(df_sum[df_sum < n].index) 
    df_sub = df[[x for x in df.columns if x not in df_rem_list]]
    return(df_sub)
    
def subset_from_df(df_full, df_sub):
    sub_cols = [x for x in df_sub.columns if x not in ['Watch_Date','Rating']]
    df_full_sub = df_full.reindex(columns=sub_cols)
    return(df_full_sub)
    
def avg_impute_by_year(df, avg_df, col='Budget', scale=0.75):
    #may be important to remove upper outliers or maybe scaled based on movie types?
    temp_df = avg_df[['search_year',col]]
    avg_df_group = temp_df.loc[temp_df[col]>=30000].groupby('search_year', as_index=False).mean()
    avg_df_group = avg_df_group.rename(columns={col:'{}_Avg'.format(col)})
    avg_df_group['{}_Avg'.format(col)] = [round(int(x * scale), -3)  for x in avg_df_group['{}_Avg'.format(col)]]
    
    df2 = df.reset_index().merge(avg_df_group, how='left', on='search_year').set_index('Movie')
    df2.loc[df2[col] < 30000, col] = df2.loc[df2[col] < 30000]['{}_Avg'.format(col)]
#    df2 = df2[[x for x in df2.columns if x != '{}_Avg'.format(col)]]
    
    return(temp_df)
    
def linear_impute(df, var_impute, var_dep, scale=0.50):
    m = np.linalg.lstsq(np.array(df[var_dep]).reshape(-1,1), np.array(df[var_impute]))[0][0]
    df.loc[(df[var_impute] < 30000) | (df[var_impute] < df[var_dep]), var_impute] = [round(int(x * m * scale), -3) for x in df.loc[(df[var_impute] < 30000) | (df[var_impute] < df[var_dep])][var_dep]]
    return(df)

if __name__ == "__main__":
######## Data Prep #######
    #encode categorical variables
    print("Encoding LetterBoxd movies")
    df_dummy = encode_categorical(df) #df from Movie_Scrape output
    print("Encoding Oscars movies")
    oscars_test_dummy = encode_categorical(oscars_test) #oscars_df from Oscars_BeautifulSoup
    
    #subset encoded columns to only keep categories >2% presence
    print("Subsetting columns for both datasets")
    n_col_sum = np.ceil(len(df_dummy)*0.02) #making sure the categorical kept make up at least 2% of watched movies
    df_dummy_sub = subset_encoded_cols(df_dummy, n=n_col_sum)
    
    #merge Oscars data (add vars to df && drop matching movie rows from oscars)
    print("Merging Oscars data into Letterboxd df\nDropping matching rows from Oscars df")
    df_dummy_sub = df_dummy_sub.merge(oscars_awards[[x for x in oscars_awards.columns if x not in ['Movie','search_year']]], on='Movie_ID', how='left')
    movie_ids = list(df_dummy.Movie_ID.unique())
    oscars_test_dummy = oscars_test_dummy.loc[np.invert(oscars_test_dummy.Movie_ID.isin(movie_ids))]
    
    #remove genders 'list' columns
    print("Performing final misc drops/calculations")
    df_dummy_sub = df_dummy_sub[[x for x in df_dummy_sub.columns if x[-8:] != '_Genders']]
    
    #remove misc vars (unused for now!)
    df_dummy_sub = df_dummy_sub[[x for x in df_dummy_sub.columns if x not in ['Movie_ID','Release_Date','Watch_Date','Overview', 'Title']]]
    
    #make oscars df columns match training df
    oscars_df_dummy_sub = subset_from_df(oscars_test_dummy, df_dummy_sub)
    
    #assign index as Movie
    df_dummy_sub = df_dummy_sub.set_index('Movie')
    oscars_df_dummy_sub = oscars_df_dummy_sub.set_index('Movie')
    
    #fill nulls
    df_dummy_sub = df_dummy_sub.fillna(0)
    oscars_df_dummy_sub = oscars_df_dummy_sub.fillna(0)
    
    #impute low budget and revenue variables
    df_final = avg_impute_by_year(df_dummy_sub, oscars_df_dummy_sub, col='Budget', scale=0.75)
    oscars_final = avg_impute_by_year(oscars_df_dummy_sub, oscars_df_dummy_sub, col='Budget', scale=0.75)
    df_final = linear_impute(df_final, 'Revenue', 'Budget', scale=0.5)
    oscars_final = linear_impute(oscars_final, 'Revenue', 'Budget', scale=0.5)
    
    #drop duplicates ##need to find where they're being created
    df_final = df_final.drop_duplicates()
    oscars_final = oscars_final.drop_duplicates()

######## Model Building #######

    reg = linear_model.Ridge(alpha=.5)
    
    #train test split (bringing in movie_dataframe3 from Movie DF Clean)
    X = df_final[[col for col in df_final.columns if col != 'Rating']]
    y = df_final[['Rating']]
    X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=2021)
    
    #fit model
    reg.fit(X_train, y_train)
    
    #Test predict!
    predictions = reg.predict(X_test)
    #predictions = (predictions / predictions.max()) * 10 ## scale predictions to have max as 10
    predictions[predictions > 10] = 10 ## ceiling the predictions at 10
    predictions[predictions < 0] = 0 ## floor the predictions at 0
    predictions = predictions.round(0)
    y_test['pred'] = predictions
    
        
    #accuracy measure
#    y_true = y_test['Rating']
#    y_pred = y_test['pred']
#    cm = metrics.confusion_matrix(y_true, y_pred)
#    df_cm = pd.DataFrame(cm, index = [i for i in "123456789"],
#                      columns = [i for i in "123456789"])
#    plt.figure(figsize = (10,7))
#    sn.heatmap(df_cm, annot=True)
    
    #Apply to oscars set and sort by highest rating
    oscar_pred = pd.DataFrame(columns=['Movie','Predicted_Rating'])
    oscar_pred['Movie'] = oscars_final.index.values
    oscar_pred['Predicted_Rating'] = reg.predict(oscars_final)
    oscar_pred = oscar_pred.sort_values(by='Predicted_Rating', ascending=False)
    oscar_pred.loc[oscar_pred.Predicted_Rating>10, 'Predicted_Rating']=10
    oscar_pred.loc[oscar_pred.Predicted_Rating<0,'Predicted_Rating']=0