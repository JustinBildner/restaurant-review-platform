from scipy.stats import norm
import redis
from config import Config

class RedisManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.leaderboard_key = "restaurant_leaderboard"
    
    def get_leaderboard(self, limit: int = 10) -> list[tuple[str, float]]:
        """Get top restaurants with their scores"""
        return self.redis_client.zrevrange(
            self.leaderboard_key,
            0,
            limit - 1,
            withscores=True
        )
    
    def get_restaurant_rank(self, restaurant_name: str) -> int:
        """Get restaurant's rank in the leaderboard (0-based)"""
        rank = self.redis_client.zrevrank(self.leaderboard_key, restaurant_name)
        return rank + 1 if rank is not None else None

    def wilson_score(self, pos, n, confidence=0.95):
        """
        Wilson score interval for a Bernoulli parameter, accounting for small sample sizes,
        takes the lower bound of the confidence interval
        """
        if n == 0:
            return 0
            
        z = norm.ppf(1 - (1 - confidence) / 2)
        p = pos / n
        
        numerator = p + z*z/(2*n) - z * ((p*(1-p)/n + z*z/(4*n*n)) ** 0.5)
        denominator = 1 + z*z/n
        
        return numerator/denominator

    def update_restaurant_score(self, restaurant_name: str, new_sentiment: float):
        """
        Uses Wilson score interval - balances success rate with sample size
        """
        stats_key = f"stats:{restaurant_name}"
        pos_reviews = int(self.redis_client.hget(stats_key, "positive_reviews") or 0)
        total_reviews = int(self.redis_client.hget(stats_key, "total_reviews") or 0)
        
        # Update counts
        pos_reviews += new_sentiment
        total_reviews += 1
        
        # Calculate Wilson score
        score = self.wilson_score(pos_reviews, total_reviews)
        
        # Update Redis
        self.redis_client.hset(stats_key, mapping={
            "positive_reviews": pos_reviews,
            "total_reviews": total_reviews
        })
        self.redis_client.zadd(self.leaderboard_key, {restaurant_name: score})

        