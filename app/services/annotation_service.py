from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.database import GeneratedData, Annotation, POI, Sentiment, DataType, Language, UserRole
from app.schemas.map import AnnotationRequest, AnnotationResponse
import re
import logging

logger = logging.getLogger(__name__)


class AnnotationService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def auto_annotate(self, generated_data_id: str) -> List[Annotation]:
        result = await self.db.execute(
            select(GeneratedData).where(GeneratedData.id == generated_data_id)
        )
        generated_data = result.scalar_one_or_none()
        
        if not generated_data:
            raise ValueError(f"Generated data not found: {generated_data_id}")
        
        annotations = []
        
        poi_annotation = await self._annotate_poi(generated_data)
        if poi_annotation:
            annotations.append(poi_annotation)
        
        sentiment_annotation = await self._annotate_sentiment(generated_data)
        if sentiment_annotation:
            annotations.append(sentiment_annotation)
        
        data_type_annotation = await self._annotate_data_type(generated_data)
        if data_type_annotation:
            annotations.append(data_type_annotation)
        
        language_annotation = await self._annotate_language(generated_data)
        if language_annotation:
            annotations.append(language_annotation)
        
        user_role_annotation = await self._annotate_user_role(generated_data)
        if user_role_annotation:
            annotations.append(user_role_annotation)
        
        for annotation in annotations:
            self.db.add(annotation)
        
        await self.db.flush()
        
        return annotations
    
    async def _annotate_poi(self, data: GeneratedData) -> Optional[Annotation]:
        if data.location_context:
            result = await self.db.execute(
                select(POI).where(
                    and_(
                        POI.city == data.location_context,
                        POI.is_active == True,
                    )
                ).limit(1)
            )
            poi = result.scalar_one_or_none()
            
            if poi:
                return Annotation(
                    id=str(uuid4()),
                    generated_data_id=data.id,
                    annotation_type="poi",
                    label=poi.id,
                    confidence=0.8,
                    is_auto=True,
                )
        
        return None
    
    async def _annotate_sentiment(self, data: GeneratedData) -> Optional[Annotation]:
        content = data.content.lower()
        
        positive_words = ["推荐", "好吃", "棒", "赞", "不错", "好", "喜欢", "推荐", "recommend", "great", "good", "love", "nice"]
        negative_words = ["差", "糟糕", "不推荐", "难吃", "脏", "失望", "bad", "terrible", "awful", "disappointing", "avoid"]
        
        pos_count = sum(1 for word in positive_words if word in content)
        neg_count = sum(1 for word in negative_words if word in content)
        
        if pos_count > neg_count:
            sentiment = Sentiment.POSITIVE
            confidence = min(0.9, 0.5 + pos_count * 0.1)
        elif neg_count > pos_count:
            sentiment = Sentiment.NEGATIVE
            confidence = min(0.9, 0.5 + neg_count * 0.1)
        else:
            sentiment = Sentiment.NEUTRAL
            confidence = 0.5
        
        return Annotation(
            id=str(uuid4()),
            generated_data_id=data.id,
            annotation_type="sentiment",
            label=sentiment.value,
            confidence=confidence,
            is_auto=True,
        )
    
    async def _annotate_data_type(self, data: GeneratedData) -> Optional[Annotation]:
        content = data.content
        
        if "?" in content or "吗" in content or "怎么" in content or "哪里" in content:
            data_type = DataType.Q_A
            confidence = 0.7
        elif "推荐" in content or "建议" in content:
            data_type = DataType.RECOMMENDATION
            confidence = 0.7
        elif "体验" in content or "去过" in content or "感觉" in content:
            data_type = DataType.REVIEW
            confidence = 0.6
        elif len(content) > 200 and not "?" in content:
            data_type = DataType.COMMENTARY
            confidence = 0.6
        else:
            data_type = DataType.CONVERSATION
            confidence = 0.5
        
        return Annotation(
            id=str(uuid4()),
            generated_data_id=data.id,
            annotation_type="data_type",
            label=data_type.value,
            confidence=confidence,
            is_auto=True,
        )
    
    async def _annotate_language(self, data: GeneratedData) -> Optional[Annotation]:
        content = data.content
        
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_chars = len(re.findall(r'[a-zA-Z]', content))
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', content))
        korean_chars = len(re.findall(r'[\uac00-\ud7af]', content))
        
        total_chars = chinese_chars + english_chars + japanese_chars + korean_chars
        
        if total_chars == 0:
            return None
        
        chinese_ratio = chinese_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if chinese_ratio > 0.7:
            language = Language.ZH
        elif english_ratio > 0.7:
            language = Language.EN
        elif japanese_ratio > 0.3:
            language = Language.JA
        elif korean_ratio > 0.3:
            language = Language.KO
        else:
            language = Language.MULTI
        
        confidence = max(chinese_ratio, english_ratio, japanese_ratio / total_chars, korean_ratio / total_chars)
        
        return Annotation(
            id=str(uuid4()),
            generated_data_id=data.id,
            annotation_type="language",
            label=language.value,
            confidence=confidence,
            is_auto=True,
        )
    
    async def _annotate_user_role(self, data: GeneratedData) -> Optional[Annotation]:
        content = data.content
        
        if "导游" in content or "历史" in content or "文化" in content:
            role = UserRole.GUIDE
            confidence = 0.7
        elif "留学" in content or "国外" in content or "foreign" in content.lower():
            role = UserRole.STUDENT
            confidence = 0.6
        elif "本地" in content or "地道" in content:
            role = UserRole.LOCAL
            confidence = 0.6
        else:
            role = UserRole.TOURIST
            confidence = 0.5
        
        return Annotation(
            id=str(uuid4()),
            generated_data_id=data.id,
            annotation_type="user_role",
            label=role.value,
            confidence=confidence,
            is_auto=True,
        )
    
    async def add_annotation(
        self,
        request: AnnotationRequest
    ) -> AnnotationResponse:
        annotations = []
        
        for ann_data in request.annotations:
            annotation = Annotation(
                id=str(uuid4()),
                generated_data_id=request.generated_data_id,
                annotation_type=ann_data.get("annotation_type", "manual"),
                label=ann_data.get("label", ""),
                confidence=ann_data.get("confidence"),
                annotator=request.annotator,
                is_auto=False,
                notes=ann_data.get("notes"),
            )
            
            self.db.add(annotation)
            annotations.append(annotation)
        
        await self.db.flush()
        
        if annotations:
            await self.db.refresh(annotations[0])
            return AnnotationResponse(
                id=annotations[0].id,
                generated_data_id=annotations[0].generated_data_id,
                annotation_type=annotations[0].annotation_type,
                label=annotations[0].label,
                confidence=annotations[0].confidence,
                is_auto=annotations[0].is_auto,
                created_at=annotations[0].created_at,
            )
        
        raise ValueError("No annotations provided")
    
    async def get_annotations(
        self,
        generated_data_id: str
    ) -> List[Annotation]:
        result = await self.db.execute(
            select(Annotation).where(Annotation.generated_data_id == generated_data_id)
        )
        return result.scalars().all()
    
    async def batch_annotate(
        self,
        generated_data_ids: List[str]
    ) -> Dict[str, List[Annotation]]:
        results = {}
        
        for data_id in generated_data_ids:
            try:
                annotations = await self.auto_annotate(data_id)
                results[data_id] = annotations
            except Exception as e:
                logger.error(f"Failed to annotate {data_id}: {str(e)}")
                results[data_id] = []
        
        return results
    
    async def verify_annotation(
        self,
        annotation_id: str,
        verified: bool,
        notes: Optional[str] = None
    ) -> Optional[Annotation]:
        result = await self.db.execute(
            select(Annotation).where(Annotation.id == annotation_id)
        )
        annotation = result.scalar_one_or_none()
        
        if not annotation:
            return None
        
        annotation.is_auto = False
        if notes:
            annotation.notes = notes
        
        await self.db.flush()
        await self.db.refresh(annotation)
        
        return annotation
