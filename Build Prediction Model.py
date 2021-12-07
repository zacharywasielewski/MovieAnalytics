import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn import metrics
import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt
pd.options.display.max_columns = None
pd.options.display.max_rows = None

reg = linear_model.Ridge(alpha=.5)

#train test split (bringing in movie_dataframe3 from Movie DF Clean)
X = df_final[[col for col in df_final.columns if col != 'Rating']]
y = df_final[['Rating']]
X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=2021)


#fit model
reg.fit(X_train, y_train)

#predict!
predictions = reg.predict(X_test)
#predictions = (predictions / predictions.max()) * 10 ## scale predictions to have max as 10
predictions[predictions > 10] = 10 ## ceiling the predictions at 10
predictions[predictions < 0] = 0 ## floor the predictions at 0
predictions = predictions.round(0)
y_test['pred'] = predictions

    
#accuracy measure
y_true = y_test['Rating']
y_pred = y_test['pred']
cm = metrics.confusion_matrix(y_true, y_pred)
df_cm = pd.DataFrame(cm, index = [i for i in "1234567890"],
                  columns = [i for i in "1234567890"])
plt.figure(figsize = (10,7))
sn.heatmap(df_cm, annot=True)
