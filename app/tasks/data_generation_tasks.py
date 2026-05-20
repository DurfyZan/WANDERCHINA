from celery import Task
from app.core.celery_app import celery_app
from app.database.base import AsyncSessionLocal
from app.services.data_generation import DataGenerationService
from app.services.prompt_manager import AgentType
from app.schemas.map import GenerateDataRequest, DataType, Language, UserRole
from typing import List, Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name="app.tasks.data_generation_tasks.generate_single_task")
def generate_single_task(
    self: Task,
    location: str,
    data_type: str,
    language: str,
    user_role: str,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    async def _generate():
        async with AsyncSessionLocal() as db:
            service = DataGenerationService(db)
            request = GenerateDataRequest(
                location=location,
                data_type=DataType(data_type),
                language=Language(language),
                user_role=UserRole(user_role),
                metadata=metadata,
            )
            result = await service.generate_single(request)
            return {
                "id": result.id,
                "content": result.content,
                "agent_type": result.agent_type,
                "quality_score": result.quality_score,
            }
    
    return run_async(_generate())


@celery_app.task(bind=True, name="app.tasks.data_generation_tasks.batch_generate_task")
def batch_generate_task(
    self: Task,
    location: str,
    data_type: str,
    language: str,
    user_role: str,
    quantity: int,
    agent_types: List[str] = None,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    task_id = self.request.id
    logger.info(f"Starting batch generation task {task_id}")
    
    results = []
    errors = []
    
    async def _batch_generate():
        nonlocal results, errors
        
        async with AsyncSessionLocal() as db:
            service = DataGenerationService(db)
            
            for i in range(quantity):
                try:
                    agent_type = None
                    if agent_types:
                        agent_type = agent_types[i % len(agent_types)]
                    
                    request = GenerateDataRequest(
                        location=location,
                        data_type=DataType(data_type),
                        language=Language(language),
                        user_role=UserRole(user_role),
                        agent_type=agent_type,
                        metadata=metadata,
                    )
                    
                    result = await service.generate_single(request)
                    results.append({
                        "id": result.id,
                        "content": result.content,
                        "agent_type": result.agent_type,
                        "quality_score": result.quality_score,
                    })
                    
                    if (i + 1) % 10 == 0:
                        self.update_state(
                            state="PROGRESS",
                            meta={"current": i + 1, "total": quantity}
                        )
                        
                except Exception as e:
                    logger.error(f"Generation failed for item {i}: {str(e)}")
                    errors.append({
                        "index": i,
                        "error": str(e),
                    })
    
    run_async(_batch_generate())
    
    return {
        "task_id": task_id,
        "status": "completed",
        "total": quantity,
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors,
    }


@celery_app.task(bind=True, name="app.tasks.data_generation_tasks.generate_multi_language_task")
def generate_multi_language_task(
    self: Task,
    location: str,
    data_type: str,
    base_language: str,
    target_languages: List[str],
    user_role: str,
    metadata: Dict[str, Any] = None,
) -> Dict[str, Any]:
    async def _generate():
        async with AsyncSessionLocal() as db:
            service = DataGenerationService(db)
            
            base_request = GenerateDataRequest(
                location=location,
                data_type=DataType(data_type),
                language=Language(base_language),
                user_role=UserRole(user_role),
                metadata=metadata,
            )
            
            base_result = await service.generate_single(base_request)
            
            translations = []
            for lang in target_languages:
                trans_request = GenerateDataRequest(
                    location=location,
                    data_type=DataType(data_type),
                    language=Language(lang),
                    user_role=UserRole(user_role),
                    custom_prompt=f"将以下内容翻译成{lang}：\n{base_result.content}",
                    metadata={"source_language": base_language, "translation": True},
                )
                
                try:
                    trans_result = await service.generate_single(trans_request)
                    translations.append({
                        "language": lang,
                        "content": trans_result.content,
                        "id": trans_result.id,
                    })
                except Exception as e:
                    logger.error(f"Translation to {lang} failed: {str(e)}")
                    translations.append({
                        "language": lang,
                        "error": str(e),
                    })
            
            return {
                "base_content": base_result.content,
                "base_id": base_result.id,
                "translations": translations,
            }
    
    return run_async(_generate())


@celery_app.task(name="app.tasks.data_generation_tasks.cleanup_failed_tasks")
def cleanup_failed_tasks():
    logger.info("Cleaning up failed generation tasks")
    
    async def _cleanup():
        pass
    
    run_async(_cleanup())
    
    return {"status": "completed"}
