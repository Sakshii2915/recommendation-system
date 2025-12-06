"""
Collaborative Filtering Recommendation Engine
Implements user-based and item-based collaborative filtering
"""
import logging
import numpy as np
from typing import List, Dict, Optional
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Collaborative filtering recommendation engine"""
    
    def __init__(self, dynamodb_client, cache_manager):
        self.dynamodb_client = dynamodb_client
        self.cache_manager = cache_manager
        self.similarity_cache = {}
        self.similarity_cache_ttl = 3600  # 1 hour
    
    async def get_recommendations(
        self, 
        user_id: str, 
        limit: int = 10,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Generate personalized recommendations using collaborative filtering
        
        Args:
            user_id: User identifier
            limit: Number of recommendations to return
            context: Optional contextual information
        
        Returns:
            List of recommended items with scores
        """
        start_time = time.time()
        
        try:
            # Get user's interaction history
            user_events = await self.dynamodb_client.get_user_events(user_id, limit=1000)
            
            if not user_events:
                # Cold start: return popular items
                return await self._get_popular_items(limit)
            
            # Build user-item interaction matrix
            user_item_matrix = await self._build_interaction_matrix(user_id)
            
            # Calculate user similarities
            user_similarities = await self._calculate_user_similarities(user_id, user_item_matrix)
            
            # Generate recommendations using collaborative filtering
            recommendations = await self._generate_cf_recommendations(
                user_id=user_id,
                user_item_matrix=user_item_matrix,
                user_similarities=user_similarities,
                limit=limit,
                context=context
            )
            
            # Format recommendations
            formatted_recs = [
                {
                    "item_id": item_id,
                    "score": float(score),
                    "reason": self._generate_reason(item_id, score, user_similarities)
                }
                for item_id, score in recommendations[:limit]
            ]
            
            logger.info(f"Generated {len(formatted_recs)} recommendations in {(time.time() - start_time)*1000:.2f}ms")
            
            return formatted_recs
        
        except Exception as e:
            logger.error(f"Error in recommendation engine: {e}")
            # Fallback to popular items
            return await self._get_popular_items(limit)
    
    async def _build_interaction_matrix(self, target_user_id: str) -> Dict:
        """Build user-item interaction matrix"""
        # Get target user's items
        target_user_events = await self.dynamodb_client.get_user_events(target_user_id, limit=1000)
        target_user_items = {
            event['item_id']: self._event_weight(event['event_type'])
            for event in target_user_events
        }
        
        # Get similar users (users who interacted with same items)
        similar_users = await self.dynamodb_client.get_users_by_items(
            list(target_user_items.keys())
        )
        
        # Build matrix
        matrix = {
            target_user_id: target_user_items
        }
        
        for user_id in similar_users[:100]:  # Limit to top 100 similar users
            if user_id != target_user_id:
                user_events = await self.dynamodb_client.get_user_events(user_id, limit=500)
                matrix[user_id] = {
                    event['item_id']: self._event_weight(event['event_type'])
                    for event in user_events
                }
        
        return matrix
    
    async def _calculate_user_similarities(
        self, 
        target_user_id: str, 
        user_item_matrix: Dict
    ) -> Dict[str, float]:
        """Calculate cosine similarity between target user and other users"""
        cache_key = f"similarity:{target_user_id}"
        cached = self.cache_manager.get(cache_key)
        if cached:
            return cached
        
        if target_user_id not in user_item_matrix:
            return {}
        
        target_user_vector = user_item_matrix[target_user_id]
        similarities = {}
        
        for user_id, user_vector in user_item_matrix.items():
            if user_id == target_user_id:
                continue
            
            similarity = self._cosine_similarity(target_user_vector, user_vector)
            if similarity > 0:
                similarities[user_id] = similarity
        
        # Cache similarities
        self.cache_manager.set(cache_key, similarities, ttl=self.similarity_cache_ttl)
        
        return similarities
    
    def _cosine_similarity(self, vec1: Dict, vec2: Dict) -> float:
        """Calculate cosine similarity between two vectors"""
        # Get common items
        common_items = set(vec1.keys()) & set(vec2.keys())
        
        if not common_items:
            return 0.0
        
        # Calculate dot product and magnitudes
        dot_product = sum(vec1[item] * vec2[item] for item in common_items)
        magnitude1 = np.sqrt(sum(v ** 2 for v in vec1.values()))
        magnitude2 = np.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    async def _generate_cf_recommendations(
        self,
        user_id: str,
        user_item_matrix: Dict,
        user_similarities: Dict[str, float],
        limit: int,
        context: Optional[Dict]
    ) -> List[tuple]:
        """Generate recommendations using collaborative filtering"""
        # Get items the user hasn't interacted with
        user_items = set(user_item_matrix.get(user_id, {}).keys())
        candidate_items = defaultdict(float)
        
        # Weighted sum of similar users' preferences
        for similar_user_id, similarity in sorted(
            user_similarities.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:50]:  # Top 50 similar users
            similar_user_items = user_item_matrix.get(similar_user_id, {})
            
            for item_id, weight in similar_user_items.items():
                if item_id not in user_items:
                    candidate_items[item_id] += similarity * weight
        
        # Sort by score
        recommendations = sorted(
            candidate_items.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return recommendations
    
    def _event_weight(self, event_type: str) -> float:
        """Assign weights to different event types"""
        weights = {
            'purchase': 5.0,
            'add_to_cart': 3.0,
            'like': 2.0,
            'click': 1.5,
            'view': 1.0,
            'share': 2.5,
            'rating_5': 4.0,
            'rating_4': 3.0,
            'rating_3': 2.0,
            'rating_2': 1.0,
            'rating_1': 0.5
        }
        return weights.get(event_type.lower(), 1.0)
    
    async def _get_popular_items(self, limit: int) -> List[Dict]:
        """Get popular items as fallback (cold start problem)"""
        try:
            popular_items = await self.dynamodb_client.get_popular_items(limit)
            return [
                {
                    "item_id": item['item_id'],
                    "score": float(item['popularity_score']),
                    "reason": "Popular item"
                }
                for item in popular_items
            ]
        except Exception as e:
            logger.warning(f"Error getting popular items: {e}")
            # Return dummy recommendations
            return [
                {
                    "item_id": f"item_{i}",
                    "score": 1.0 - (i * 0.1),
                    "reason": "Default recommendation"
                }
                for i in range(limit)
            ]
    
    def _generate_reason(self, item_id: str, score: float, similarities: Dict) -> str:
        """Generate human-readable reason for recommendation"""
        if score > 0.8:
            return "Highly recommended based on similar users"
        elif score > 0.5:
            return "Recommended based on user preferences"
        else:
            return "You might like this"


