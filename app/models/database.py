from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.base import Base


class POIType(str, enum.Enum):
    RESTAURANT = "restaurant"
    ATTRACTION = "attraction"
    SHOPPING = "shopping"
    HOSPITAL = "hospital"
    POLICE = "police"
    EMBASSY = "embassy"
    HOTEL = "hotel"
    TRANSPORT = "transport"
    OTHER = "other"


class UserRole(str, enum.Enum):
    TOURIST = "tourist"
    LOCAL = "local"
    STUDENT = "student"
    GUIDE = "guide"


class DataType(str, enum.Enum):
    RECOMMENDATION = "recommendation"
    REVIEW = "review"
    QA = "qa"
    COMMENTARY = "commentary"
    CONVERSATION = "conversation"


class Sentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Language(str, enum.Enum):
    ZH = "zh"
    EN = "en"
    JA = "ja"
    KO = "ko"
    MULTI = "multi"


class POI(Base):
    __tablename__ = "pois"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    name_en = Column(String, nullable=True)
    name_ja = Column(String, nullable=True)
    name_ko = Column(String, nullable=True)
    poi_type = Column(SQLEnum(POIType), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    address_en = Column(String, nullable=True)
    city = Column(String, nullable=False, index=True)
    country = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    price_level = Column(Integer, default=1)
    opening_hours = Column(JSON, nullable=True)
    contact = Column(String, nullable=True)
    website = Column(String, nullable=True)
    images = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reviews = relationship("Review", back_populates="poi")
    generated_data = relationship("GeneratedData", back_populates="poi")


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    user_role = Column(SQLEnum(UserRole), default=UserRole.TOURIST)
    preferred_language = Column(SQLEnum(Language), default=Language.ZH)
    preferences = Column(JSON, nullable=True)
    location_history = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reviews = relationship("Review", back_populates="user")
    interactions = relationship("UserInteraction", back_populates="user")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    poi_id = Column(String, ForeignKey("pois.id"), nullable=False)
    rating = Column(Float, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    language = Column(SQLEnum(Language), default=Language.ZH)
    sentiment = Column(SQLEnum(Sentiment), nullable=True)
    upvotes = Column(Integer, default=0)
    images = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="reviews")
    poi = relationship("POI", back_populates="reviews")


class GeneratedData(Base):
    __tablename__ = "generated_data"
    
    id = Column(String, primary_key=True)
    agent_type = Column(String, nullable=False, index=True)
    data_type = Column(SQLEnum(DataType), nullable=False, index=True)
    content = Column(Text, nullable=False)
    language = Column(SQLEnum(Language), default=Language.ZH)
    user_role = Column(SQLEnum(UserRole), nullable=True)
    location_context = Column(String, nullable=True)
    poi_id = Column(String, ForeignKey("pois.id"), nullable=True)
    meta = Column(JSON, nullable=True)
    quality_score = Column(Float, nullable=True)
    is_approved = Column(Boolean, default=False)
    needs_review = Column(Boolean, default=True)
    review_notes = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    parent_id = Column(String, ForeignKey("generated_data.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    poi = relationship("POI", back_populates="generated_data")
    annotations = relationship("Annotation", back_populates="generated_data")


class Annotation(Base):
    __tablename__ = "annotations"
    
    id = Column(String, primary_key=True)
    generated_data_id = Column(String, ForeignKey("generated_data.id"), nullable=False)
    annotation_type = Column(String, nullable=False)
    label = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    annotator = Column(String, nullable=True)
    is_auto = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    meta = Column(JSON, nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    generated_data = relationship("GeneratedData", back_populates="annotations")


class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(String, nullable=False)
    target_id = Column(String, nullable=True)
    target_type = Column(String, nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="interactions")


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    template_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)
    agent_type = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"
    
    id = Column(String, primary_key=True)
    generated_data_id = Column(String, ForeignKey("generated_data.id"), nullable=False)
    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    model_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
