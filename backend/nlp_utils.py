import joblib
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re

# Load the trained model and vectorizer
model = joblib.load('models/restaurant_review_model.pkl')
vectorizer = joblib.load('models/count_vectorizer.pkl')

def preprocess_text(text):
    # Preprocesses the text preparing to remove insignificant stopwords leaving only those below
    custom_stopwords = {'don', "don't", 'ain', 'aren', "aren't", 'couldn', "couldn't",
                        'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
                        'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
                        'needn', "needn't", 'shan', "shan't", 'no', 'nor', 'not', 'shouldn', "shouldn't",
                        'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}
    ps = PorterStemmer()
    stop_words = set(stopwords.words("english")) - custom_stopwords

    # Standardizes the text so that it is all letters and all lowercase
    review = re.sub('[^a-zA-Z]', ' ', text).lower().split()
    
    # Removes insignificant stop words
    review = [ps.stem(word) for word in review if word not in stop_words]
    return " ".join(review)

def predict_sentiment(user_input):
    processed_input = preprocess_text(user_input)
    # Transform the processed_input using the CountVectorizer
    processed_input_vectorized = vectorizer.transform([processed_input])
    # Predict sentiment
    prediction = model.predict(processed_input_vectorized)[0]
    return 1 if prediction == 1 else 0
