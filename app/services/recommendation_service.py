from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional, Dict, Any
from app.models.database import POI, User, UserInteraction, Review
from app.schemas.map import UserRole, Language
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        latitude: float,
        longitude: float,
        limit: int = 10,
        language: Language = Language.ZH
    ) -> List[Dict[str, Any]]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return await self.get_popular_recommendations(latitude, longitude, limit)
        
        user_preferences = user.preferences or {}
        user_role = user.user_role or UserRole.TOURIST
        
        query = select(POI).where(POI.is_active == True)
        
        if user_preferences.get("poi_types"):
            query = query.where(POI.poi_type.in_(user_preferences["poi_types"]))
        
        result = await self.db.execute(query.limit(50))
        pois = result.scalars().all()
        
        recommendations = []
        for poi in pois:
            score = self._calculate_recommendation_score(poi, user, latitude, longitude)
            recommendations.append({
                "poi": poi,
                "score": score,
                "reasons": self._get_recommendation_reasons(poi, user),
            })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:limit]
    
    def _calculate_recommendation_score(
        self,
        poi: POI,
        user: User,
        lat: float,
        lng: float
    ) -> float:
        from app.services.map_service import MapService
        
        distance = MapService.calculate_distance(lat, lng, poi.latitude, poi.longitude)
        distance_score = max(0, 1 - distance / 10000)
        
        rating_score = poi.rating / 5.0
        
        user_prefs = user.preferences or {}
        price_preference = user_prefs.get("price_level")
        price_score = 1.0
        if price_preference:
            price_score = 1.0 - abs(poi.price_level - price_preference) * 0.2
        
        base_score = distance_score * 0.3 + rating_score * 0.4 + price_score * 0.3
        
        return min(1.0, base_score)
    
    def _get_recommendation_reasons(self, poi: POI, user: User) -> List[str]:
        reasons = []
        
        if poi.rating >= 4.5:
            reasons.append("评分很高")
        elif poi.rating >= 4.0:
            reasons.append("评分不错")
        
        user_prefs = user.preferences or {}
        if poi.price_level <= 2 and user_prefs.get("budget_friendly"):
            reasons.append("性价比高")
        
        if poi.tags:
            user_tags = user_prefs.get("interests", [])
            matching_tags = set(poi.tags) & set(user_tags)
            if matching_tags:
                reasons.append(f"符合你的{','.join(list(matching_tags)[:2])}偏好")
        
        return reasons
    
    async def get_popular_recommendations(
        self,
        latitude: float,
        longitude: float,
        limit: int = 10,
        poi_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = select(POI).where(POI.is_active == True)
        
        if poi_type:
            query = query.where(POI.poi_type == poi_type)
        
        result = await self.db.execute(query.order_by(POI.rating.desc()).limit(50))
        pois = result.scalars().all()
        
        from app.services.map_service import MapService
        
        recommendations = []
        for poi in pois:
            distance = MapService.calculate_distance(
                latitude, longitude, poi.latitude, poi.longitude
            )
            recommendations.append({
                "poi": poi,
                "distance": round(distance, 0),
                "score": poi.rating * 0.7 + max(0, 1 - distance / 5000) * 0.3,
            })
        
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:limit]
    
    async def get_similar_pois(
        self,
        poi_id: str,
        limit: int = 5
    ) -> List[POI]:
        poi = await self.db.execute(
            select(POI).where(and_(POI.id == poi_id, POI.is_active == True))
        )
        poi = poi.scalar_one_or_none()
        
        if not poi:
            return []
        
        query = select(POI).where(
            and_(
                POI.id != poi_id,
                POI.is_active == True,
                POI.poi_type == poi.poi_type,
            )
        )
        
        result = await self.db.execute(query.limit(limit * 2))
        all_pois = result.scalars().all()
        
        similarities = []
        for other_poi in all_pois:
            similarity = self._calculate_similarity(poi, other_poi)
            similarities.append((other_poi, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [poi for poi, _ in similarities[:limit]]
    
    def _calculate_similarity(self, poi1: POI, poi2: POI) -> float:
        score = 0.0
        
        if poi1.price_level == poi2.price_level:
            score += 0.3
        
        if poi1.tags and poi2.tags:
            common_tags = set(poi1.tags) & set(poi2.tags)
            if common_tags:
                score += min(0.4, len(common_tags) * 0.1)
        
        rating_diff = abs(poi1.rating - poi2.rating)
        score += max(0, 0.3 - rating_diff * 0.1)
        
        return score
    
    async def record_interaction(
        self,
        user_id: str,
        interaction_type: str,
        target_id: Optional[str] = None,
        target_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        from uuid import uuid4
        
        interaction = UserInteraction(
            id=str(uuid4()),
            user_id=user_id,
            interaction_type=interaction_type,
            target_id=target_id,
            target_type=target_type,
            metadata=metadata,
        )
        
        self.db.add(interaction)
        await self.db.flush()
    
    async def get_trending_pois(
        self,
        city: str,
        limit: int = 10,
        time_window_hours: int = 24
    ) -> List[Dict[str, Any]]:
        query = select(
            UserInteraction.target_id,
            func.count(UserInteraction.id).label("interaction_count")
        ).where(
            and_(
                UserInteraction.target_type == "poi",
                UserInteraction.created_at >= func.now() - func.cast(
                    f"{time_window_hours} hours", type_=None
                ),
            )
        ).group_by(UserInteraction.target_id).order_by(func.count(UserInteraction.id).desc()).limit(limit)
        
        result = await self.db.execute(query)
        trending = result.all()
        
        trending_pois = []
        for target_id, count in trending:
            poi = await self.db.execute(
                select(POI).where(and_(POI.id == target_id, POI.is_active == True))
            )
            poi = poi.scalar_one_or_none()
            if poi:
                trending_pois.append({
                    "poi": poi,
                    "interaction_count": count,
                })
        
        return trending_pois
