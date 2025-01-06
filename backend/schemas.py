from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):
    restaurant_name: str
    review_text: str

class ReviewResponse(BaseModel):
    id: int
    restaurant_name: str
    review_text: str
    sentiment_score: float

class RestaurantCreate(BaseModel):
    name: str
    address: str

class RestaurantResponse(BaseModel):
    id: int
    name: str
    address: str
    average_sentiment: float = Field(default=0.0)