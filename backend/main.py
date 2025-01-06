import joblib
from database import DatabaseManager
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import joblib
import re
from nlp_utils import predict_sentiment, preprocess_text

def main():
    db = DatabaseManager()
    
    # Example: Add a restaurant
    try:
        restaurant_id = db.add_restaurant(
            name="Nitty Gritty", 
            address="223 N Frances St, Madison"
        )
        print(f"Added restaurant with ID: {restaurant_id}")
        
        # Example: Add a review
        review_text = "Great birthday special!"
        sentiment_score = predict_sentiment(review_text)
        review_id = db.add_review("", Nitty Gritty, sentiment_score)
        print(f"Added review with ID: {review_id}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()