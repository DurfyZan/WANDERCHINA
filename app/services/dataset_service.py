import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import AnnotationRecord, DatasetExport, GenerationJob, QualityReport
from app.models.user import User
from app.schemas.dataset import (
    AnnotationRequest,
    DatasetExportRequest,
    GenerationJobCreate,
    QualityEvalRequest,
)
from app.services.export_service import export_dataset
from app.services.model_client import ModelServiceClient
from app.services.quality_evaluator import evaluate_batch


class DatasetService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.models = ModelServiceClient()

    async def create_generation_job(self, user: User | None, data: GenerationJobCreate) -> GenerationJob:
        job = GenerationJob(
            created_by=user.id if user else None,
            generation_type=data.generation_type.value,
            scenario=data.scenario,
            llm_provider=data.llm_provider.value,
            prompt_config=json.dumps(data.prompt_config) if data.prompt_config else None,
            status="queued",
        )
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)

        from app.tasks.generation import run_generation_job

        run_generation_job.delay(job.id, data.count, data.humanize)
        return job

    async def get_job(self, job_id: int) -> GenerationJob | None:
        result = await self.db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
        return result.scalar_one_or_none()

    async def annotate(self, req: AnnotationRequest) -> list[AnnotationRecord]:
        auto = await self.models.annotate(req.texts, req.categories)
        records = []
        for i, text in enumerate(req.texts):
            ann = auto[i] if i < len(auto) else {}
            record = AnnotationRecord(
                job_id=req.job_id,
                text=text,
                category=ann.get("category"),
                sentiment=ann.get("sentiment"),
                topic_tags=",".join(ann.get("topic_tags", [])),
                annotation_round=req.interactive_round,
                annotator="auto",
                metadata_json=json.dumps(ann),
            )
            self.db.add(record)
            records.append(record)
        await self.db.flush()
        for r in records:
            await self.db.refresh(r)
        return records

    async def evaluate_quality(self, req: QualityEvalRequest) -> QualityReport:
        result = await self.db.execute(
            select(AnnotationRecord).where(AnnotationRecord.job_id == req.job_id)
        )
        records = list(result.scalars().all())
        candidates = [r.text for r in records]
        metrics_list = req.custom_metrics or ["bleu", "rouge", "diversity", "perplexity"]

        try:
            remote_scores = await self.models.evaluate_quality(candidates, req.references, metrics_list)
        except Exception:
            remote_scores = {}

        local_scores = evaluate_batch(candidates, req.references, metrics_list)
        scores = {**local_scores, **remote_scores}
        overall = scores.get("overall", sum(scores.values()) / max(len(scores), 1))

        report = QualityReport(
            job_id=req.job_id,
            metrics_json=json.dumps(scores),
            overall_score=overall,
            eval_profile=req.eval_profile,
        )
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        return report

    async def export(self, req: DatasetExportRequest) -> DatasetExport:
        result = await self.db.execute(
            select(AnnotationRecord).where(AnnotationRecord.job_id == req.job_id)
        )
        records = [
            {
                "text": r.text,
                "category": r.category,
                "sentiment": r.sentiment,
                "topic_tags": r.topic_tags,
                "metadata_json": r.metadata_json,
            }
            for r in result.scalars().all()
        ]
        path, count = export_dataset(records, req.job_id, req.format, req.label_schema)
        export = DatasetExport(
            job_id=req.job_id,
            format=req.format,
            file_path=path,
            record_count=count,
        )
        self.db.add(export)
        await self.db.flush()
        await self.db.refresh(export)
        return export
