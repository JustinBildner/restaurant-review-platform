from fastapi import FastAPI, HTTPException
from database import DatabaseManager
from redis_manager import RedisManager
from schemas import ReviewCreate, ReviewResponse, RestaurantResponse
from typing import List
from nlp_utils import predict_sentiment, preprocess_text

app = FastAPI()
db = DatabaseManager()
redis_manager = RedisManager()

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