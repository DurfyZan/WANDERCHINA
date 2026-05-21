from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database.base import get_db
from app.services.data_generation import DataGenerationService
from app.services.annotation_service import AnnotationService
from app.services.evaluation_service import EvaluationService
from app.services.export_service import ExportService
from app.schemas.map import (
    GenerateDataRequest,
    GenerateDataResponse,
    BatchGenerateRequest,
    BatchGenerateResponse,
    AnnotationRequest,
    AnnotationResponse,
    EvaluateRequest,
    EvaluateResponse,
    ExportRequest,
    ExportResponse,
)
from app.tasks.data_generation_tasks import batch_generate_task
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/map", tags=["data_generation"])


@router.post("/generate", response_model=GenerateDataResponse)
async def generate_data(
    request: GenerateDataRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        service = DataGenerationService(db)
        result = await service.generate_single(request)
        return result
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}",
        )


@router.post("/generate/batch", response_model=BatchGenerateResponse)
async def batch_generate(
    request: BatchGenerateRequest,
    background_tasks: BackgroundTasks,
):
    task = batch_generate_task.delay(
        location=request.location,
        data_type=request.data_type.value,
        language=request.language.value,
        user_role=request.user_role.value,
        quantity=request.quantity,
        agent_types=request.agent_types,
    )
    
    return BatchGenerateResponse(
        task_id=task.id,
        status="pending",
        total_count=request.quantity,
        message=f"Batch generation task created. Quantity: {request.quantity}",
    )


@router.get("/generate/batch/{task_id}")
async def get_batch_status(task_id: str):
    from app.core.celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    if task.state == "PENDING":
        response = {
            "task_id": task_id,
            "status": "pending",
            "message": "Task is pending",
        }
    elif task.state == "PROGRESS":
        response = {
            "task_id": task_id,
            "status": "in_progress",
            "message": "Task is in progress",
            "progress": task.info,
        }
    elif task.state == "SUCCESS":
        response = {
            "task_id": task_id,
            "status": "completed",
            "result": task.result,
        }
    else:
        response = {
            "task_id": task_id,
            "status": "failed",
            "message": str(task.info),
        }
    
    return response


@router.post("/annotate")
async def annotate_data(
    request: AnnotationRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AnnotationService(db)
    result = await service.add_annotation(request)
    return {"status": "success", "annotation": result}


@router.post("/annotate/auto/{generated_data_id}")
async def auto_annotate(
    generated_data_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = AnnotationService(db)
    annotations = await service.auto_annotate(generated_data_id)
    
    return {
        "status": "success",
        "annotations": [
            {
                "id": ann.id,
                "annotation_type": ann.annotation_type,
                "label": ann.label,
                "confidence": ann.confidence,
                "is_auto": ann.is_auto,
            }
            for ann in annotations
        ],
    }


@router.get("/annotations/{generated_data_id}")
async def get_annotations(
    generated_data_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = AnnotationService(db)
    annotations = await service.get_annotations(generated_data_id)
    
    return {
        "annotations": [
            {
                "id": ann.id,
                "annotation_type": ann.annotation_type,
                "label": ann.label,
                "confidence": ann.confidence,
                "is_auto": ann.is_auto,
                "created_at": ann.created_at.isoformat(),
            }
            for ann in annotations
        ],
    }


@router.post("/evaluate", response_model=List[EvaluateResponse])
async def evaluate_data(
    request: EvaluateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = EvaluationService(db)
    results = await service.batch_evaluate(request)
    return results


@router.get("/evaluate/{generated_data_id}")
async def get_evaluation(
    generated_data_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = EvaluationService(db)
    history = await service.get_evaluation_history(generated_data_id)
    
    return {
        "evaluations": [
            {
                "id": eval.id,
                "metric_name": eval.metric_name,
                "metric_value": eval.metric_value,
                "metric_type": eval.metric_type,
                "details": eval.details,
                "created_at": eval.created_at.isoformat(),
            }
            for eval in history
        ],
    }


@router.post("/export", response_model=ExportResponse)
async def export_data(
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    service = ExportService(db)
    result = await service.export_data(request)
    return result


@router.get("/export/files")
async def get_export_files(db: AsyncSession = Depends(get_db)):
    service = ExportService(db)
    files = await service.get_export_files()
    return {"files": files}


@router.get("/export/download/{file_name}")
async def download_export(file_name: str, db: AsyncSession = Depends(get_db)):
    import os
    from fastapi.responses import FileResponse
    
    export_dir = "exports"
    file_path = os.path.join(export_dir, file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/json",
    )


@router.delete("/export/files/{file_name}")
async def delete_export_file(
    file_name: str,
    db: AsyncSession = Depends(get_db),
):
    service = ExportService(db)
    success = await service.delete_export_file(file_name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    return {"status": "success", "message": "File deleted"}
