import pandas as pd

if __name__ == "__main__":
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
    
    #subset encoded columns to only columns where sum >= 3
    df_sum = df_dummy.sum(numeric_only = True)
    df_rem_list = list(df_sum[df_sum < 3].index) 
    df_dummy_sub = df_dummy[[x for x in df_dummy.columns if x not in df_rem_list]]
    
    #remove genders 'list' columns
    df_dummy_sub = df_dummy_sub[[x for x in df_dummy_sub.columns if x[-8:] != '_Genders']]
    
    #remove misc vars (unused for now!)
    df_dummy_sub = df_dummy_sub[[x for x in df_dummy_sub.columns if x not in ['Release_Date','Watch_Date','Overview']]]
    
    #assign index as Movie
    df_dummy_sub = df_dummy_sub.set_index('Movie')
    
    #fill nulls
    df_final = df_dummy_sub.fillna(0)
