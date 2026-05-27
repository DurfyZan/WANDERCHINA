from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database.base import get_db
from app.services.map_service import MapService
from app.services.recommendation_service import RecommendationService
from app.schemas.map import (
    NearbySearchRequest,
    NearbySearchResponse,
    POIResponse,
    POICreate,
    ReviewCreate,
    ReviewResponse,
)
from app.models.database import POI

router = APIRouter(prefix="/api/map", tags=["map"])


@router.get("/nearby", response_model=NearbySearchResponse)
async def get_nearby_places(
    lat: float,
    lng: float,
    radius: float = 1000,
    poi_type: str = None,
    language: str = "zh",
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "distance",
    db: AsyncSession = Depends(get_db),
):
    from app.schemas.map import POIType
    
    request = NearbySearchRequest(
        latitude=lat,
        longitude=lng,
        radius=radius,
        poi_type=POIType(poi_type) if poi_type else None,
        language=language,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
    )
    
    service = MapService(db)
    pois = await service.get_nearby_pois(request)
    
    poi_responses = [
        POIResponse(
            id=poi.id,
            name=poi.name,
            name_en=poi.name_en,
            name_ja=poi.name_ja,
            name_ko=poi.name_ko,
            poi_type=poi.poi_type,
            latitude=poi.latitude,
            longitude=poi.longitude,
            address=poi.address,
            address_en=poi.address_en,
            city=poi.city,
            country=poi.country,
            rating=poi.rating,
            price_level=poi.price_level,
            opening_hours=poi.opening_hours,
            contact=poi.contact,
            website=poi.website,
            tags=poi.tags,
            rating_count=poi.rating_count,
            images=poi.images,
            metadata=poi.metadata,
            is_active=poi.is_active,
            created_at=poi.created_at,
            updated_at=poi.updated_at,
        )
        for poi in pois
    ]
    
    return NearbySearchResponse(
        results=poi_responses,
        total=len(poi_responses),
        query={
            "latitude": lat,
            "longitude": lng,
            "radius": radius,
            "poi_type": poi_type,
        },
    )


@router.get("/poi/{poi_id}", response_model=POIResponse)
async def get_poi(
    poi_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = MapService(db)
    poi = await service.get_poi_by_id(poi_id)
    
    if not poi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="POI not found",
        )
    
    return POIResponse(
        id=poi.id,
        name=poi.name,
        name_en=poi.name_en,
        name_ja=poi.name_ja,
        name_ko=poi.name_ko,
        poi_type=poi.poi_type,
        latitude=poi.latitude,
        longitude=poi.longitude,
        address=poi.address,
        address_en=poi.address_en,
        city=poi.city,
        country=poi.country,
        rating=poi.rating,
        price_level=poi.price_level,
        opening_hours=poi.opening_hours,
        contact=poi.contact,
        website=poi.website,
        tags=poi.tags,
        rating_count=poi.rating_count,
        images=poi.images,
        metadata=poi.metadata,
        is_active=poi.is_active,
        created_at=poi.created_at,
        updated_at=poi.updated_at,
    )


@router.post("/poi", response_model=POIResponse)
async def create_poi(
    poi_data: POICreate,
    db: AsyncSession = Depends(get_db),
):
    from uuid import uuid4
    
    service = MapService(db)
    poi = await service.create_poi({
        "id": str(uuid4()),
        **poi_data.model_dump(),
    })
    
    return POIResponse(
        id=poi.id,
        name=poi.name,
        name_en=poi.name_en,
        name_ja=poi.name_ja,
        name_ko=poi.name_ko,
        poi_type=poi.poi_type,
        latitude=poi.latitude,
        longitude=poi.longitude,
        address=poi.address,
        address_en=poi.address_en,
        city=poi.city,
        country=poi.country,
        rating=poi.rating,
        price_level=poi.price_level,
        opening_hours=poi.opening_hours,
        contact=poi.contact,
        website=poi.website,
        tags=poi.tags,
        rating_count=poi.rating_count,
        images=poi.images,
        metadata=poi.metadata,
        is_active=poi.is_active,
        created_at=poi.created_at,
        updated_at=poi.updated_at,
    )


@router.get("/search")
async def search_pois(
    keyword: str,
    city: str = None,
    poi_type: str = None,
    language: str = "zh",
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    from app.schemas.map import POIType
    
    service = MapService(db)
    pois = await service.search_pois(
        keyword=keyword,
        city=city,
        poi_type=POIType(poi_type) if poi_type else None,
        language=language,
        limit=limit,
    )
    
    return {
        "results": [
            {
                "id": poi.id,
                "name": poi.name,
                "poi_type": poi.poi_type.value,
                "latitude": poi.latitude,
                "longitude": poi.longitude,
                "rating": poi.rating,
                "city": poi.city,
            }
            for poi in pois
        ],
        "total": len(pois),
    }


@router.get("/recommendations")
async def get_recommendations(
    user_id: str,
    lat: float,
    lng: float,
    limit: int = 10,
    language: str = "zh",
    db: AsyncSession = Depends(get_db),
):
    from app.schemas.map import Language
    
    service = RecommendationService(db)
    recommendations = await service.get_personalized_recommendations(
        user_id=user_id,
        latitude=lat,
        longitude=lng,
        limit=limit,
        language=Language(language),
    )
    
    return {
        "recommendations": [
            {
                "poi": {
                    "id": rec["poi"].id,
                    "name": rec["poi"].name,
                    "poi_type": rec["poi"].poi_type.value,
                    "latitude": rec["poi"].latitude,
                    "longitude": rec["poi"].longitude,
                    "rating": rec["poi"].rating,
                    "price_level": rec["poi"].price_level,
                },
                "score": rec["score"],
                "reasons": rec["reasons"],
            }
            for rec in recommendations
        ],
    }


@router.get("/popular")
async def get_popular_places(
    lat: float,
    lng: float,
    poi_type: str = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    service = RecommendationService(db)
    popular = await service.get_popular_recommendations(
        latitude=lat,
        longitude=lng,
        limit=limit,
        poi_type=poi_type,
    )
    
    return {
        "results": [
            {
                "poi": {
                    "id": rec["poi"].id,
                    "name": rec["poi"].name,
                    "rating": rec["poi"].rating,
                },
                "distance": rec["distance"],
            }
            for rec in popular
        ],
    }


@router.get("/trending")
async def get_trending_places(
    city: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    service = RecommendationService(db)
    trending = await service.get_trending_pois(
        city=city,
        limit=limit,
    )
    
    return {
        "results": [
            {
                "poi": {
                    "id": rec["poi"].id,
                    "name": rec["poi"].name,
                    "rating": rec["poi"].rating,
                },
                "interaction_count": rec["interaction_count"],
            }
            for rec in trending
        ],
    }


@router.get("/stats")
async def get_poi_stats(
    city: str = None,
    db: AsyncSession = Depends(get_db),
):
    service = MapService(db)
    stats = await service.get_poi_stats(city=city)
    
    return stats
