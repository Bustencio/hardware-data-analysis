import spacy
import json
import string
import pickle
import pandas as pd
 
from sklearn import metrics
from spacy.tokens import Span
from spacy.lang.es import Spanish
from sklearn.pipeline import Pipeline
from sklearn.base import TransformerMixin
from sklearn.metrics import classification_report
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer    

punctuations = string.punctuation
spacy_stopwords = spacy.lang.es.stop_words.STOP_WORDS

parser = Spanish()

def spacyTokenizer(sentence):
    
    tokens = parser(sentence)
    
    # Extraemos el lema de cada palabra y la convertimos a minúscula
    tokens = [ word.text.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in tokens ]

    # Eliminamos los signos de puntuación y las stop-words
    tokens = [ word for word in tokens if word not in punctuations and word not in spacy_stopwords]

    return tokens

def clean_text(text):
    return text.strip()


class predictors(TransformerMixin):
    def transform(self, X, **transform_params):

        # Cleaning Text
        return [clean_text(text) for text in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}


df = pd.read_csv('./taggedArticles.csv', names=['article', 'category'], sep=',')
df.head() 


category_codes = {
    'tarjetas gráficas': 0,
    'procesadores': 1,
    'placas': 2,
    'memoria RAM': 3,
    'discos duros': 4,
    'otros': 5
}

df['category_code'] = df['category']
df['category_code'].replace(category_codes, inplace=True)
df.head()

tfidf_vector = TfidfVectorizer(tokenizer = spacyTokenizer, min_df=5, max_df=0.5, max_features=100, ngram_range=(1, 2))


X = df['article'] # Los titulares a analizar
Y = df['category_code'] # Las etiquetas que serán probadas

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1)


# Create the parameter grid based on the results of random search 
max_depth = [40]
max_features = ['auto']
min_samples_leaf = [2]
min_samples_split = [30, 50]
n_estimators = [200, 800]
learning_rate = [.1, .5]
subsample = [1.]

param_grid = {
    'max_depth': max_depth,
    'max_features': max_features,
    'min_samples_leaf': min_samples_leaf,
    'min_samples_split': min_samples_split,
    'n_estimators': n_estimators,
    'learning_rate': learning_rate,
    'subsample': subsample
}

print('Comenzando entrenamiento')

# Create a base model
gbc = GradientBoostingClassifier()


# Instantiate the grid search model
grid_search = GridSearchCV(estimator=gbc, 
                           param_grid=param_grid,
                           scoring='accuracy',cv=2, n_jobs=-1, verbose=1)

pipe = Pipeline([("cleaner", predictors()),
                ('tfidf', tfidf_vector),
                ('clf', grid_search)])


pipe.fit(X_train, Y_train)

classifier = grid_search.best_estimator_

pipe = Pipeline([("cleaner", predictors()),
                ('tfidf', tfidf_vector),
                ('clf', classifier)])
predictionCV = pipe.predict(X_test)

""" print("Accuracy Train:",metrics.accuracy_score(Y_train, pipe.predict(X_train)))
print("Accuracy Test:",metrics.accuracy_score(Y_test, predictionCV))
print("Precision:",metrics.precision_score(Y_test, predictionCV,average='micro'))
print("Recall:",metrics.recall_score(Y_test, predictionCV,average='micro'))
print("Classification Report:")
print(classification_report(Y_test,predictionCV)) """



# Load real article list
df_articles = pd.read_csv('./articles.csv', names=['article_date','article_link','article_source','article_title'], sep=',')

articles = df_articles['article_title']

# Predict 
print('Realizando predicción')
result = pipe.predict(articles)

df_articles['article_category'] = result

# Replace codes for each category
reverse_category_codes = {
    0: 'Tarjetas Gráficas',
    1: 'Procesadores',
    2: 'Placas',
    3: 'Memoria RAM',
    4: 'Discos Duros',
    5: 'Otros'
}
df_articles['article_category'].replace(reverse_category_codes, inplace=True)

# Save final file
df_articles.to_csv('./resultArticles.csv', index = False)

print('Artículos procesados')