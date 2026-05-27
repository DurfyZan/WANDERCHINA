import asyncio
import json

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.models.dataset import AnnotationRecord, GenerationJob
from app.services.model_client import ModelServiceClient
from app.tasks.celery_app import celery_app


def _sync_session() -> Session:
    settings = get_settings()
    engine = create_engine(settings.database_url_sync)
    return sessionmaker(bind=engine)()


@celery_app.task(name="app.tasks.generation.run_generation_job")
def run_generation_job(job_id: int, count: int, humanize: bool) -> dict:
    session = _sync_session()
    try:
        job = session.get(GenerationJob, job_id)
        if not job:
            return {"error": "job not found"}
        job.status = "running"
        session.commit()

        client = ModelServiceClient()
        items = asyncio.run(
            client.generate(
                job.generation_type,
                job.scenario,
                count,
                job.llm_provider,
                json.loads(job.prompt_config) if job.prompt_config else None,
                humanize,
            )
        )

        for item in items:
            session.add(
                AnnotationRecord(
                    job_id=job_id,
                    text=item.get("text", ""),
                    category=item.get("category"),
                    sentiment=item.get("sentiment"),
                    topic_tags=",".join(item.get("topic_tags", [])),
                    annotator="generator",
                    metadata_json=json.dumps(item),
                )
            )
        job.output_count = len(items)
        job.status = "completed"
        session.commit()
        return {"job_id": job_id, "count": len(items)}
    except Exception as exc:
        job = session.get(GenerationJob, job_id)
        if job:
            job.status = "failed"
            session.commit()
        return {"error": str(exc)}
    finally:
        session.close()
