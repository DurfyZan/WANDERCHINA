from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.enums import GenerationType, LLMProvider


class GenerationJobCreate(BaseModel):
    generation_type: GenerationType
    scenario: str | None = Field(default=None, description="景点、餐饮、文化活动等场景")
    count: int = Field(default=10, ge=1, le=500)
    llm_provider: LLMProvider = LLMProvider.DEEPSEEK
    prompt_config: dict[str, Any] | None = None
    humanize: bool = True


class GenerationJobRead(BaseModel):
    id: int
    generation_type: str
    scenario: str | None
    llm_provider: str
    status: str
    output_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AnnotationRequest(BaseModel):
    texts: list[str]
    job_id: int | None = None
    interactive_round: int = 1
    categories: list[str] | None = None


class AnnotationResult(BaseModel):
    text: str
    category: str | None
    sentiment: str | None
    topic_tags: list[str]


class QualityEvalRequest(BaseModel):
    job_id: int
    references: list[str] | None = None
    eval_profile: str = "default"
    custom_metrics: list[str] | None = Field(
        default=None,
        description="bleu, rouge, meteor, bertscore, perplexity, diversity",
    )


class QualityEvalResult(BaseModel):
    job_id: int
    overall_score: float
    metrics: dict[str, float]
    eval_profile: str


class DatasetExportRequest(BaseModel):
    job_id: int
    format: str = Field(pattern="^(jsonl|csv|tsv)$")
    label_schema: str = Field(default="classification", description="classification | sentiment | qa_pair")
