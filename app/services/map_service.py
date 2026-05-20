from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from app.models.database import POI, POIType
from app.schemas.map import NearbySearchRequest, POIResponse
from math import radians, sin, cos, sqrt, atan2
import logging

logger = logging.getLogger(__name__)


class MapService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371000
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    async def get_nearby_pois(self, request: NearbySearchRequest) -> List[POI]:
        lat = request.latitude
        lng = request.longitude
        radius = request.radius
        
        max_lat = lat + (radius / 111000)
        min_lat = lat - (radius / 111000)
        max_lng = lng + (radius / (111000 * cos(radians(lat))))
        min_lng = lng - (radius / (111000 * cos(radians(lat))))
        
        query = select(POI).where(
            and_(
                POI.is_active == True,
                POI.latitude >= min_lat,
                POI.latitude <= max_lat,
                POI.longitude >= min_lng,
                POI.longitude <= max_lng,
            )
        )
        
        if request.poi_type:
            query = query.where(POI.poi_type == request.poi_type)
        
        result = await self.db.execute(query)
        all_pois = result.scalars().all()
        
        pois_with_distance = []
        for poi in all_pois:
            distance = self.calculate_distance(lat, lng, poi.latitude, poi.longitude)
            if distance <= radius:
                pois_with_distance.append((poi, distance))
        
        if request.sort_by == "distance":
            pois_with_distance.sort(key=lambda x: x[1])
        elif request.sort_by == "rating":
            pois_with_distance.sort(key=lambda x: x[0].rating, reverse=True)
        elif request.sort_by == "price":
            pois_with_distance.sort(key=lambda x: x[0].price_level)
        
        total = len(pois_with_distance)
        start = request.offset
        end = start + request.limit
        
        return [poi for poi, _ in pois_with_distance[start:end]]
    
    async def get_poi_by_id(self, poi_id: str) -> Optional[POI]:
        result = await self.db.execute(
            select(POI).where(and_(POI.id == poi_id, POI.is_active == True))
        )
        return result.scalar_one_or_none()
    
    async def search_pois(
        self,
        keyword: str,
        city: Optional[str] = None,
        poi_type: Optional[POIType] = None,
        language: str = "zh",
        limit: int = 20
    ) -> List[POI]:
        query = select(POI).where(POI.is_active == True)
        
        if language == "en":
            search_field = POI.name_en
        elif language == "ja":
            search_field = POI.name_ja
        elif language == "ko":
            search_field = POI.name_ko
        else:
            search_field = POI.name
        
        query = query.where(search_field.ilike(f"%{keyword}%"))
        
        if city:
            query = query.where(POI.city == city)
        
        if poi_type:
            query = query.where(POI.poi_type == poi_type)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_poi(self, poi_data: dict) -> POI:
        poi = POI(**poi_data)
        self.db.add(poi)
        await self.db.flush()
        await self.db.refresh(poi)
        return poi
    
    async def update_poi(self, poi_id: str, poi_data: dict) -> Optional[POI]:
        poi = await self.get_poi_by_id(poi_id)
        if not poi:
            return None
        
        for key, value in poi_data.items():
            if hasattr(poi, key):
                setattr(poi, key, value)
        
        await self.db.flush()
        await self.db.refresh(poi)
        return poi
    
    async def delete_poi(self, poi_id: str) -> bool:
        poi = await self.get_poi_by_id(poi_id)
        if not poi:
            return False
        
        poi.is_active = False
        await self.db.flush()
        return True
    
    async def get_poi_stats(self, city: Optional[str] = None) -> dict:
        query = select(POI).where(POI.is_active == True)
        
        if city:
            query = query.where(POI.city == city)
        
        result = await self.db.execute(query)
        pois = result.scalars().all()
        
        stats = {
            "total": len(pois),
            "by_type": {},
        }
        
        for poi in pois:
            poi_type = poi.poi_type.value
            if poi_type not in stats["by_type"]:
                stats["by_type"][poi_type] = 0
            stats["by_type"][poi_type] += 1
        
        return stats
