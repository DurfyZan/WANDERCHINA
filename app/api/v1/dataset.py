from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_roles
from app.core.enums import UserRole
from app.db.session import get_db
from app.models.user import User
from app.schemas.dataset import (
    AnnotationRequest,
    AnnotationResult,
    DatasetExportRequest,
    GenerationJobCreate,
    GenerationJobRead,
    QualityEvalRequest,
    QualityEvalResult,
)
from app.services.dataset_service import DatasetService

router = APIRouter()


@router.post("/generate", response_model=GenerationJobRead, status_code=202)
async def start_generation(
    data: GenerationJobCreate,
    user: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.STUDENT, UserRole.LOCAL))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await DatasetService(db).create_generation_job(user, data)


@router.get("/jobs/{job_id}", response_model=GenerationJobRead)
async def get_job(
    job_id: int,
    _: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    job = await DatasetService(db).get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/annotate", response_model=list[AnnotationResult])
async def annotate(
    data: AnnotationRequest,
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.STUDENT))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    records = await DatasetService(db).annotate(data)
    return [
        AnnotationResult(
            text=r.text,
            category=r.category,
            sentiment=r.sentiment,
            topic_tags=(r.topic_tags or "").split(",") if r.topic_tags else [],
        )
        for r in records
    ]


@router.post("/quality", response_model=QualityEvalResult)
async def evaluate_quality(
    data: QualityEvalRequest,
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    report = await DatasetService(db).evaluate_quality(data)
    import json

    metrics = json.loads(report.metrics_json)
    return QualityEvalResult(
        job_id=data.job_id,
        overall_score=report.overall_score or 0.0,
        metrics=metrics,
        eval_profile=report.eval_profile,
    )


@router.post("/export", status_code=201)
async def export_dataset(
    data: DatasetExportRequest,
    _: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    export = await DatasetService(db).export(data)
    return {
        "export_id": export.id,
        "file_path": export.file_path,
        "format": export.format,
        "record_count": export.record_count,
    }
