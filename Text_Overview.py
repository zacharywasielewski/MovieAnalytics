import numpy as np
import pandas as pd
import re, nltk, spacy, gensim
import gensim.corpora as corpora
import os

# Sklearn
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from pprint import pprint
#Stop Words
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
#Stemming
nlp = spacy.load("en_core_web_sm")
#Visualization
import pyLDAvis.gensim
import pickle 
import pyLDAvis

def tokenize(words):
    #tokenizing
    words = re.sub('[^A-Za-z0-9 ]+', '', str(words)).lower().split()
    words = [word for word in words if word not in stop_words]
    return(words)
    
### trying to subset all words down to only words that are infrequent but not rare
def subset_tokens(words):
    #keeping words > 1 freq and <15%
    word_lookup = []
    for word in words:
        word_lookup += word
    freqdist = nltk.FreqDist(word_lookup)
    d = pd.DataFrame(columns=['token', 'freq'])
    for k, v in freqdist.items():
        d.loc[len(d)] = k, v
    top_remove = d.loc[d.freq >= top_num]['token']
    bottom_remove = d.loc[d.freq <= bottom_num]['token']
    words = [word for word in words if word not in top_remove and word not in bottom_remove]
    return words

def topic_model(df, col='Overview', num_topics=10):
    print('Gathering movie topics for rated movies...')
    #text preprocessing
    token_col = df.assign(tokens=df['Overview'].apply(tokenize))['tokens']
    id2word = corpora.Dictionary(token_col)
    corpus = [id2word.doc2bow(text) for text in token_col]
    #topic modeling
    num_topics = 15
    lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=num_topics)
    return(token_col, id2word, corpus, lda_model, num_topics)

def visualize_topics(id2word, corpus, lda_model, path='./', num_topics=10):
    print('Creating visualization html at {}'.format(path))
    #visualizing topics
    pyLDAvis.enable_notebook()
    LDAvis_data_filepath = os.path.join('{}ldavis_prepared_{}topics'.format(path, str(num_topics)))
    #this is a bit time consuming
    LDAvis_prepared = pyLDAvis.gensim.prepare(lda_model, corpus, id2word)
    with open(LDAvis_data_filepath, 'wb') as f:
        pickle.dump(LDAvis_prepared, f)
    #load the pre-prepared pyLDAvis data from disk
    with open(LDAvis_data_filepath, 'rb') as f:
        LDAvis_prepared = pickle.load(f)
    pyLDAvis.save_html(LDAvis_prepared, '{}ldavis_prepared_{}topics{}'.format(path, str(num_topics), '.html'))
    LDAvis_prepared


if __name__ == "__main__":
    token_col, id2word, corpus, lda_model, num_topics = topic_model(df, col='Overview', num_topics=15)
#    visualize_topics(id2word, corpus, lda_model, path='C:/Users/G672594/Work/Work - Local/Other/NLP/', num_topics=num_topics)