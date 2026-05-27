from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.database import GeneratedData, EvaluationResult
from app.schemas.map import EvaluateRequest, EvaluateResponse, EvaluationMetric
import logging

logger = logging.getLogger(__name__)


class EvaluationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        self.supported_metrics = {
            "perplexity": self._evaluate_perplexity,
            "bert_score": self._evaluate_bert_score,
            "grammar": self._evaluate_grammar,
            "sentiment": self._evaluate_sentiment,
            "length": self._evaluate_length,
            "diversity": self._evaluate_diversity,
            "coherence": self._evaluate_coherence,
        }
    
    async def evaluate_single(
        self,
        generated_data_id: str,
        metrics: List[str]
    ) -> EvaluateResponse:
        result = await self.db.execute(
            select(GeneratedData).where(GeneratedData.id == generated_data_id)
        )
        generated_data = result.scalar_one_or_none()
        
        if not generated_data:
            raise ValueError(f"Generated data not found: {generated_data_id}")
        
        evaluation_results = []
        
        for metric_name in metrics:
            if metric_name not in self.supported_metrics:
                logger.warning(f"Unsupported metric: {metric_name}")
                continue
            
            try:
                metric_func = self.supported_metrics[metric_name]
                metric_result = await metric_func(generated_data.content)
                
                evaluation_results.append(metric_result)
                
                eval_result = EvaluationResult(
                    id=str(uuid4()),
                    generated_data_id=generated_data_id,
                    metric_name=metric_name,
                    metric_value=metric_result.metric_value,
                    metric_type=metric_result.metric_type,
                    details=metric_result.details,
                )
                self.db.add(eval_result)
                
            except Exception as e:
                logger.error(f"Metric {metric_name} failed: {str(e)}")
        
        await self.db.flush()
        
        overall_score = self._calculate_overall_score(evaluation_results)
        
        return EvaluateResponse(
            generated_data_id=generated_data_id,
            results=evaluation_results,
            overall_score=overall_score,
            evaluated_at=datetime.utcnow(),
        )
    
    async def _evaluate_perplexity(self, content: str) -> EvaluationMetric:
        words = content.split()
        if len(words) < 2:
            return EvaluationMetric(
                metric_name="perplexity",
                metric_value=0.5,
                metric_type="fluency",
                details={"reason": "Content too short"},
            )
        
        avg_word_length = sum(len(w) for w in words) / len(words)
        
        score = min(1.0, avg_word_length / 5.0)
        
        return EvaluationMetric(
            metric_name="perplexity",
            metric_value=score,
            metric_type="fluency",
            details={
                "word_count": len(words),
                "avg_word_length": avg_word_length,
            },
        )
    
    async def _evaluate_bert_score(self, content: str) -> EvaluationMetric:
        chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
        total_chars = len(content)
        
        if total_chars == 0:
            return EvaluationMetric(
                metric_name="bert_score",
                metric_value=0.0,
                metric_type="semantic",
            )
        
        score = chinese_chars / total_chars * 0.5 + 0.3
        
        return EvaluationMetric(
            metric_name="bert_score",
            metric_value=score,
            metric_type="semantic",
            details={
                "chinese_ratio": chinese_chars / total_chars,
                "total_chars": total_chars,
            },
        )
    
    async def _evaluate_grammar(self, content: str) -> EvaluationMetric:
        chinese_count = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
        english_count = sum(1 for c in content if c.isalpha() and c.isascii())
        
        if chinese_count == 0 and english_count == 0:
            return EvaluationMetric(
                metric_name="grammar",
                metric_value=0.5,
                metric_type="quality",
                details={"reason": "No text content"},
            )
        
        has_punctuation = any(p in content for p in '，。！？、：；""''（）')
        has_ending = content.strip()[-1] in '。！？.!?'
        
        score = 0.5
        if has_punctuation:
            score += 0.2
        if has_ending:
            score += 0.2
        
        return EvaluationMetric(
            metric_name="grammar",
            metric_value=min(1.0, score),
            metric_type="quality",
            details={
                "has_punctuation": has_punctuation,
                "has_ending": has_ending,
            },
        )
    
    async def _evaluate_sentiment(self, content: str) -> EvaluationMetric:
        content_lower = content.lower()
        
        positive_words = ["好", "棒", "赞", "推荐", "喜欢", "不错", "great", "good", "love", "nice", "recommend"]
        negative_words = ["差", "糟糕", "不推荐", "难吃", "脏", "失望", "bad", "terrible", "avoid", "disappointing"]
        
        pos_count = sum(1 for w in positive_words if w in content_lower)
        neg_count = sum(1 for w in negative_words if w in content_lower)
        
        if pos_count > neg_count:
            sentiment_score = 0.7 + min(0.3, pos_count * 0.05)
        elif neg_count > pos_count:
            sentiment_score = 0.3 - min(0.3, neg_count * 0.05)
        else:
            sentiment_score = 0.5
        
        return EvaluationMetric(
            metric_name="sentiment",
            metric_value=sentiment_score,
            metric_type="quality",
            details={
                "positive_count": pos_count,
                "negative_count": neg_count,
            },
        )
    
    async def _evaluate_length(self, content: str) -> EvaluationMetric:
        word_count = len(content.split())
        
        if word_count < 10:
            score = 0.3
            reason = "Too short"
        elif word_count < 50:
            score = 0.6
            reason = "Short but acceptable"
        elif word_count < 200:
            score = 0.9
            reason = "Good length"
        else:
            score = 0.7
            reason = "Possibly too long"
        
        return EvaluationMetric(
            metric_name="length",
            metric_value=score,
            metric_type="quality",
            details={
                "word_count": word_count,
                "reason": reason,
            },
        )
    
    async def _evaluate_diversity(self, content: str) -> EvaluationMetric:
        words = content.split()
        if len(words) < 2:
            return EvaluationMetric(
                metric_name="diversity",
                metric_value=0.0,
                metric_type="quality",
            )
        
        unique_words = set(words)
        diversity_ratio = len(unique_words) / len(words)
        
        return EvaluationMetric(
            metric_name="diversity",
            metric_value=diversity_ratio,
            metric_type="quality",
            details={
                "unique_words": len(unique_words),
                "total_words": len(words),
                "diversity_ratio": diversity_ratio,
            },
        )
    
    async def _evaluate_coherence(self, content: str) -> EvaluationMetric:
        sentences = content.replace('！', '。').replace('？', '。').split('。')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return EvaluationMetric(
                metric_name="coherence",
                metric_value=0.5,
                metric_type="quality",
                details={"reason": "Single sentence"},
            )
        
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
        
        if avg_sentence_length < 5:
            score = 0.4
        elif avg_sentence_length < 30:
            score = 0.8
        else:
            score = 0.6
        
        return EvaluationMetric(
            metric_name="coherence",
            metric_value=score,
            metric_type="quality",
            details={
                "sentence_count": len(sentences),
                "avg_sentence_length": avg_sentence_length,
            },
        )
    
    def _calculate_overall_score(self, metrics: List[EvaluationMetric]) -> float:
        if not metrics:
            return 0.0
        
        weights = {
            "perplexity": 0.2,
            "bert_score": 0.15,
            "grammar": 0.2,
            "sentiment": 0.15,
            "length": 0.1,
            "diversity": 0.1,
            "coherence": 0.1,
        }
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for metric in metrics:
            weight = weights.get(metric.metric_name, 0.1)
            weighted_sum += metric.metric_value * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    async def batch_evaluate(
        self,
        request: EvaluateRequest
    ) -> List[EvaluateResponse]:
        results = []
        
        for data_id in request.generated_data_ids:
            try:
                result = await self.evaluate_single(data_id, request.metrics)
                results.append(result)
            except Exception as e:
                logger.error(f"Evaluation failed for {data_id}: {str(e)}")
        
        return results
    
    async def get_evaluation_history(
        self,
        generated_data_id: str,
        limit: int = 10
    ) -> List[EvaluationResult]:
        result = await self.db.execute(
            select(EvaluationResult)
            .where(EvaluationResult.generated_data_id == generated_data_id)
            .order_by(EvaluationResult.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
