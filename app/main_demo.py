from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import List, Dict, Any
from datetime import datetime
from uuid import uuid4

app = FastAPI(
    title="WanderChina Map Backend (Demo Mode)",
    version="0.1.0",
    description="智能地图 + 多智能体数据生成系统（演示模式）",
)

MOCK_POI_DATA = [
    {
        "id": str(uuid4()),
        "name": "外滩",
        "name_en": "The Bund",
        "poi_type": "attraction",
        "latitude": 31.2405,
        "longitude": 121.4903,
        "rating": 4.8,
        "city": "上海",
        "address": "上海市黄浦区中山东一路",
        "price_level": 1,
        "tags": ["景点", "夜景", "历史"],
    },
    {
        "id": str(uuid4()),
        "name": "小杨生煎",
        "name_en": "Xiaoyang Shengjian",
        "poi_type": "restaurant",
        "latitude": 31.2304,
        "longitude": 121.4737,
        "rating": 4.5,
        "city": "上海",
        "address": "上海市黄浦区南京东路步行街",
        "price_level": 2,
        "tags": ["美食", "生煎", "上海特色"],
    },
    {
        "id": str(uuid4()),
        "name": "上海中心大厦",
        "name_en": "Shanghai Tower",
        "poi_type": "attraction",
        "latitude": 31.2354,
        "longitude": 121.5012,
        "rating": 4.7,
        "city": "上海",
        "address": "上海市浦东新区银城中路501号",
        "price_level": 3,
        "tags": ["地标", "观光", "高层建筑"],
    },
    {
        "id": str(uuid4()),
        "name": "上海华山医院",
        "name_en": "Huashan Hospital",
        "poi_type": "hospital",
        "latitude": 31.2253,
        "longitude": 121.4585,
        "rating": 4.6,
        "city": "上海",
        "address": "上海市静安区乌鲁木齐中路12号",
        "price_level": 4,
        "tags": ["医院", "医疗", "三甲医院"],
    },
    {
        "id": str(uuid4()),
        "name": "豫园",
        "name_en": "Yu Garden",
        "poi_type": "attraction",
        "latitude": 31.2276,
        "longitude": 121.4852,
        "rating": 4.6,
        "city": "上海",
        "address": "上海市黄浦区豫园路1号",
        "price_level": 2,
        "tags": ["园林", "古建筑", "传统文化"],
    },
]

MOCK_GENERATED_DATA = [
    {
        "id": str(uuid4()),
        "agent_type": "tourist",
        "data_type": "recommendation",
        "content": "强烈推荐外滩！夜景超美，可以看到浦东的璀璨灯光。建议晚上8点左右去，可以看到灯光秀。",
        "language": "zh",
        "quality_score": 0.85,
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": str(uuid4()),
        "agent_type": "local",
        "data_type": "recommendation",
        "content": "小杨生煎是上海本地人最爱的生煎包之一。皮薄汁多，底部酥脆。建议早点去，排队的人很多。",
        "language": "zh",
        "quality_score": 0.88,
        "created_at": datetime.utcnow().isoformat(),
    },
    {
        "id": str(uuid4()),
        "agent_type": "student",
        "data_type": "review",
        "content": "As an international student, Shanghai Tower is definitely worth visiting! The view from the 118th floor is breathtaking. Make sure to book tickets in advance.",
        "language": "en",
        "quality_score": 0.82,
        "created_at": datetime.utcnow().isoformat(),
    },
]


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import radians, sin, cos, sqrt, atan2
    R = 6371000
    lat1_rad, lat2_rad = radians(lat1), radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting WanderChina Map Backend (Demo Mode)...")
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


@app.get("/")
async def root():
    return {
        "name": "WanderChina Map Backend (Demo Mode)",
        "version": "0.1.0",
        "status": "running",
        "mode": "demo",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "WanderChina Map Backend (Demo Mode)"}


@app.get("/api/map/nearby")
async def get_nearby_places(
    lat: float,
    lng: float,
    radius: float = 1000,
    poi_type: str = None,
    limit: int = 20,
):
    results = []
    for poi in MOCK_POI_DATA:
        distance = calculate_distance(lat, lng, poi["latitude"], poi["longitude"])
        if distance <= radius:
            if poi_type is None or poi["poi_type"] == poi_type:
                results.append({**poi, "distance": round(distance, 0)})
    
    results.sort(key=lambda x: x["distance"])
    return {"results": results[:limit], "total": len(results), "mode": "demo"}


@app.get("/api/map/search")
async def search_pois(keyword: str, city: str = None, limit: int = 20):
    results = [
        poi for poi in MOCK_POI_DATA
        if keyword.lower() in poi["name"].lower() or keyword.lower() in " ".join(poi.get("tags", [])).lower()
    ]
    if city:
        results = [poi for poi in results if poi["city"] == city]
    return {"results": results[:limit], "total": len(results), "mode": "demo"}


@app.get("/api/map/poi/{poi_id}")
async def get_poi(poi_id: str):
    for poi in MOCK_POI_DATA:
        if poi["id"] == poi_id:
            return {"data": poi, "mode": "demo"}
    return {"error": "POI not found"}, 404


@app.get("/api/map/recommendations")
async def get_recommendations(lat: float, lng: float, limit: int = 10):
    recommendations = []
    for poi in MOCK_POI_DATA:
        distance = calculate_distance(lat, lng, poi["latitude"], poi["longitude"])
        score = poi["rating"] * 0.7 + max(0, 1 - distance / 5000) * 0.3
        recommendations.append({
            "poi": poi,
            "distance": round(distance, 0),
            "score": round(score, 2),
        })
    
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return {"recommendations": recommendations[:limit], "mode": "demo"}


@app.post("/api/map/generate")
async def generate_data(request: Dict[str, Any]):
    location = request.get("location", "未知地点")
    data_type = request.get("data_type", "recommendation")
    language = request.get("language", "zh")
    
    templates = {
        "recommendation": f"作为本地人，为您推荐{location}附近的好去处。",
        "review": f"分享您在{location}的体验和感受。",
        "qa": f"回答关于{location}的各种问题。",
        "commentary": f"为您介绍{location}的文化和历史。",
    }
    
    content = templates.get(data_type, f"关于{location}的内容")
    
    return {
        "id": str(uuid4()),
        "content": content + " [演示模式：实际生成需要配置API密钥和数据库]",
        "agent_type": request.get("user_role", "tourist"),
        "data_type": data_type,
        "language": language,
        "mode": "demo",
        "note": "这是演示数据，实际生成需要配置AI模型API密钥",
    }


@app.get("/api/map/export/files")
async def get_export_files():
    return {
        "files": [
            {"name": "demo_data.jsonl", "size": "1.2 KB", "created_at": datetime.utcnow().isoformat()},
        ],
        "mode": "demo",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
