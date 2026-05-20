from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class POIType(str, Enum):
    RESTAURANT = "restaurant"
    ATTRACTION = "attraction"
    SHOPPING = "shopping"
    HOSPITAL = "hospital"
    POLICE = "police"
    EMBASSY = "embassy"
    HOTEL = "hotel"
    TRANSPORT = "transport"
    OTHER = "other"


class Language(str, Enum):
    ZH = "zh"
    EN = "en"
    JA = "ja"
    KO = "ko"
    MULTI = "multi"


class UserRole(str, Enum):
    TOURIST = "tourist"
    LOCAL = "local"
    STUDENT = "student"
    GUIDE = "guide"


class DataType(str, Enum):
    RECOMMENDATION = "recommendation"
    REVIEW = "review"
    Q_A = "qa"
    COMMENTARY = "commentary"
    CONVERSATION = "conversation"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class POIBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    name_ja: Optional[str] = None
    name_ko: Optional[str] = None
    poi_type: POIType
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    address_en: Optional[str] = None
    city: str
    country: str
    rating: float = Field(default=0.0, ge=0, le=5)
    price_level: int = Field(default=1, ge=1, le=4)
    opening_hours: Optional[Dict[str, Any]] = None
    contact: Optional[str] = None
    website: Optional[str] = None
    tags: Optional[List[str]] = None


class POICreate(POIBase):
    pass


class POIResponse(POIBase):
    id: str
    rating_count: int = 0
    images: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NearbySearchRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius: float = Field(default=1000, ge=100, le=50000)
    poi_type: Optional[POIType] = None
    language: Language = Language.ZH
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="distance", pattern="^(distance|rating|price)$")


class NearbySearchResponse(BaseModel):
    results: List[POIResponse]
    total: int
    query: Dict[str, Any]


class GenerateDataRequest(BaseModel):
    location: str
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    data_type: DataType
    language: Language = Language.ZH
    user_role: UserRole = UserRole.TOURIST
    agent_type: Optional[str] = None
    model_name: Optional[str] = None
    custom_prompt: Optional[str] = None
    few_shot_examples: Optional[List[Dict[str, str]]] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2048, ge=100, le=4096)
    metadata: Optional[Dict[str, Any]] = None


class GenerateDataResponse(BaseModel):
    id: str
    content: str
    agent_type: str
    data_type: DataType
    language: Language
    metadata: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    created_at: datetime


class BatchGenerateRequest(BaseModel):
    location: str
    data_type: DataType
    language: Language = Language.ZH
    user_role: UserRole = UserRole.TOURIST
    quantity: int = Field(default=10, ge=1, le=100)
    agent_types: Optional[List[str]] = None
    model_name: Optional[str] = None


class BatchGenerateResponse(BaseModel):
    task_id: str
    status: str
    total_count: int
    message: str


class AnnotationRequest(BaseModel):
    generated_data_id: str
    annotations: List[Dict[str, Any]]
    annotator: Optional[str] = None


class AnnotationResponse(BaseModel):
    id: str
    generated_data_id: str
    annotation_type: str
    label: str
    confidence: Optional[float] = None
    is_auto: bool
    created_at: datetime


class EvaluateRequest(BaseModel):
    generated_data_ids: List[str]
    metrics: List[str] = Field(
        default=["perplexity", "bert_score", "grammar", "sentiment"]
    )
    reference_texts: Optional[List[str]] = None


class EvaluationMetric(BaseModel):
    metric_name: str
    metric_value: float
    metric_type: str
    details: Optional[Dict[str, Any]] = None


class EvaluateResponse(BaseModel):
    generated_data_id: str
    results: List[EvaluationMetric]
    overall_score: Optional[float] = None
    evaluated_at: datetime


class ExportRequest(BaseModel):
    format: str = Field(default="jsonl", pattern="^(jsonl|chat|alpaca)$")
    data_type: Optional[DataType] = None
    language: Optional[Language] = None
    quality_threshold: Optional[float] = Field(default=None, ge=0, le=1)
    limit: Optional[int] = None
    include_metadata: bool = True


class ExportResponse(BaseModel):
    download_url: str
    format: str
    total_records: int
    file_size: str
    expires_at: datetime


class ReviewCreate(BaseModel):
    poi_id: str
    rating: float = Field(..., ge=0, le=5)
    title: Optional[str] = None
    content: str
    language: Language = Language.ZH
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class ReviewResponse(BaseModel):
    id: str
    user_id: str
    poi_id: str
    rating: float
    title: Optional[str] = None
    content: str
    language: Language
    sentiment: Optional[Sentiment] = None
    upvotes: int = 0
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_verified: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str
