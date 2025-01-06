from fastapi import FastAPI, HTTPException
from database import DatabaseManager
from redis_manager import RedisManager
from schemas import ReviewCreate, ReviewResponse, RestaurantResponse
import joblist
from typing import List

app = FastAPI()
db = DatabaseManager()
redis_manager = RedisManager()

# Load the trained model and vectorizer
model = joblib.load('models/restaurant_review_model.pkl')
vectorizer = joblib.load('models/count_vectorizer.pkl')

def preprocess_text(text):
    custom_stopwords = {'don', "don't", 'ain', 'aren', "aren't", 'couldn', "couldn't",
                        'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
                        'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
                        'needn', "needn't", 'shan', "shan't", 'no', 'nor', 'not', 'shouldn', "shouldn't",
                        'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}
    ps = PorterStemmer()
    stop_words = set(stopwords.words("english")) - custom_stopwords

    review = re.sub('[^a-zA-Z]', ' ', text)
    review = review.lower()
    review = review.split()
    review = [ps.stem(word) for word in review if word not in stop_words]
    review = " ".join(review)

    return review

def predict_sentiment(user_input):
    processed_input = preprocess_text(user_input)
    # Transform the processed_input using the CountVectorizer
    processed_input_vectorized = vectorizer.transform([processed_input])
    # Predict sentiment
    prediction = model.predict(processed_input_vectorized)[0]
    return 1 if prediction == 1 else -0

@app.post("/reviews/", response_model=ReviewResponse)
async def create_review(review: ReviewCreate):
    try:
        # Predict sentiment
        sentiment_score = predict_sentiment(review.review_text)
        
        # Add review to database
        review_id = db.add_review(
            review.restaurant_name,
            review.review_text,
            sentiment_score
        )
        
        # Update Redis leaderboard
        redis_manager.update_restaurant_score(
            review.restaurant_name,
            sentiment_score
        )
        
        return ReviewResponse(
            id=review_id,
            restaurant_name=review.restaurant_name,
            review_text=review.review_text,
            sentiment_score=sentiment_score
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/restaurants/", response_model=List[RestaurantResponse])
async def get_restaurants():
    restaurants = db.get_all_restaurants()
    return [
        RestaurantResponse(
            id=r[0],
            name=r[1],
            address=r[2],
            average_sentiment=float(r[3])
        ) for r in restaurants
    ]

@app.get("/leaderboard/")
async def get_leaderboard(limit: int = 10):
    leaderboard = redis_manager.get_leaderboard(limit)
    result = []
    
    for restaurant_name, score in leaderboard:
        rank = redis_manager.get_restaurant_rank(restaurant_name)
        restaurant_info = db.get_restaurant_by_name(restaurant_name)
        
        if restaurant_info:
            result.append({
                "rank": rank,
                "name": restaurant_name,
                "address": restaurant_info[0][2],
                "average_sentiment": score
            })
    
    return result

@app.get("/restaurants/{restaurant_name}/rank")
async def get_restaurant_rank(restaurant_name: str):
    rank = redis_manager.get_restaurant_rank(restaurant_name)
    if rank is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return {"restaurant": restaurant_name, "rank": rank}