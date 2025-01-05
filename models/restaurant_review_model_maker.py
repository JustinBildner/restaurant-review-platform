
import pandas as pd
import numpy as np
import warnings
import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

warnings.filterwarnings('ignore')

# Load dataset
data = pd.read_csv('./data/yelp_labeled.tsv', sep='\t')

# Text preprocessing
nltk.download('stopwords')
custom_stopwords = {'don', "don't", 'ain', 'aren', "aren't", 'couldn', "couldn't",
                    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
                    'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
                    'needn', "needn't", 'shan', "shan't", 'no', 'nor', 'not', 'shouldn', "shouldn't",
                    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}
stop_words = set(stopwords.words('english')) - custom_stopwords
ps = PorterStemmer()

def preprocess(review):
    review = re.sub('[^a-zA-Z]', ' ', review).lower().split()
    review = [ps.stem(word) for word in review if word not in stop_words]
    return ' '.join(review)

data['Processed_Review'] = data['Review'].apply(preprocess)

# Feature extraction and model training
cv = CountVectorizer(max_features=1500)
X = cv.fit_transform(data['Processed_Review']).toarray()
y = data['Liked']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save model and vectorizer
joblib.dump(model, 'models/restaurant_review_model.pkl')
joblib.dump(cv, 'models/count_vectorizer.pkl')
