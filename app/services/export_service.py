from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.database import GeneratedData, DataType, Language
from app.schemas.map import ExportRequest, ExportResponse
import logging

logger = logging.getLogger(__name__)


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    async def export_data(self, request: ExportRequest) -> ExportResponse:
        query = select(GeneratedData)
        
        if request.data_type:
            query = query.where(GeneratedData.data_type == request.data_type)
        
        if request.language:
            query = query.where(GeneratedData.language == request.language)
        
        if request.quality_threshold is not None:
            query = query.where(GeneratedData.quality_score >= request.quality_threshold)
        
        if request.limit:
            query = query.limit(request.limit)
        
        result = await self.db.execute(query)
        data_records = result.scalars().all()
        
        if request.format == "jsonl":
            file_path, file_size = await self._export_jsonl(data_records, request.include_metadata)
        elif request.format == "chat":
            file_path, file_size = await self._export_chat(data_records, request.include_metadata)
        elif request.format == "alpaca":
            file_path, file_size = await self._export_alpaca(data_records, request.include_metadata)
        else:
            raise ValueError(f"Unsupported format: {request.format}")
        
        download_url = f"/api/map/export/download/{os.path.basename(file_path)}"
        
        return ExportResponse(
            download_url=download_url,
            format=request.format,
            total_records=len(data_records),
            file_size=self._format_file_size(file_size),
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
    
    async def _export_jsonl(
        self,
        records: List[GeneratedData],
        include_metadata: bool
    ) -> tuple[str, int]:
        file_name = f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"
        file_path = os.path.join(self.export_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            for record in records:
                output_data = {
                    "instruction": self._generate_instruction(record),
                    "input": "",
                    "output": record.content,
                }
                
                if include_metadata:
                    output_data["metadata"] = {
                        "id": record.id,
                        "agent_type": record.agent_type,
                        "data_type": record.data_type.value,
                        "language": record.language.value,
                        "location": record.location_context,
                        "quality_score": record.quality_score,
                        "created_at": record.created_at.isoformat(),
                    }
                
                f.write(json.dumps(output_data, ensure_ascii=False) + "\n")
        
        file_size = os.path.getsize(file_path)
        return file_path, file_size
    
    async def _export_chat(
        self,
        records: List[GeneratedData],
        include_metadata: bool
    ) -> tuple[str, int]:
        file_name = f"export_chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"
        file_path = os.path.join(self.export_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            for record in records:
                output_data = {
                    "messages": [
                        {"role": "user", "content": self._generate_instruction(record)},
                        {"role": "assistant", "content": record.content},
                    ],
                }
                
                if include_metadata:
                    output_data["metadata"] = {
                        "id": record.id,
                        "agent_type": record.agent_type,
                        "data_type": record.data_type.value,
                        "language": record.language.value,
                        "location": record.location_context,
                        "quality_score": record.quality_score,
                        "created_at": record.created_at.isoformat(),
                    }
                
                f.write(json.dumps(output_data, ensure_ascii=False) + "\n")
        
        file_size = os.path.getsize(file_path)
        return file_path, file_size
    
    async def _export_alpaca(
        self,
        records: List[GeneratedData],
        include_metadata: bool
    ) -> tuple[str, int]:
        file_name = f"export_alpaca_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jsonl"
        file_path = os.path.join(self.export_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            for record in records:
                output_data = {
                    "instruction": self._generate_instruction(record),
                    "input": "",
                    "output": record.content,
                    "system": self._generate_system_prompt(record),
                }
                
                if include_metadata:
                    output_data["metadata"] = {
                        "id": record.id,
                        "agent_type": record.agent_type,
                        "data_type": record.data_type.value,
                        "language": record.language.value,
                        "location": record.location_context,
                        "quality_score": record.quality_score,
                        "created_at": record.created_at.isoformat(),
                    }
                
                f.write(json.dumps(output_data, ensure_ascii=False) + "\n")
        
        file_size = os.path.getsize(file_path)
        return file_path, file_size
    
    def _generate_instruction(self, record: GeneratedData) -> str:
        location = record.location_context or "未知地点"
        
        instruction_templates = {
            DataType.RECOMMENDATION: f"推荐{location}附近的好去处",
            DataType.REVIEW: f"分享你在{location}的体验",
            DataType.Q_A: f"回答关于{location}的问题",
            DataType.COMMENTARY: f"介绍{location}的文化和历史",
            DataType.CONVERSATION: f"模拟关于{location}的对话",
        }
        
        return instruction_templates.get(record.data_type, f"关于{location}的内容")
    
    def _generate_system_prompt(self, record: GeneratedData) -> str:
        agent_prompts = {
            "tourist": "你是一个热爱旅行的游客，分享真实的旅行体验。",
            "local": "你是一个了解当地生活的本地人，给出地道的建议。",
            "student": "你是一个在中国留学的国际学生，用中英双语交流。",
            "guide": "你是一个专业的导游，知识渊博，讲解生动有趣。",
            "reviewer": "你是一个内容审核员，负责评估内容质量。",
        }
        
        return agent_prompts.get(record.agent_type, "你是一个有帮助的AI助手。")
    
    def _format_file_size(self, size_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    async def get_export_files(self) -> List[Dict[str, Any]]:
        files = []
        
        if not os.path.exists(self.export_dir):
            return files
        
        for file_name in os.listdir(self.export_dir):
            if file_name.endswith((".jsonl", ".json")):
                file_path = os.path.join(self.export_dir, file_name)
                stat = os.stat(file_path)
                
                files.append({
                    "name": file_name,
                    "size": self._format_file_size(stat.st_size),
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "download_url": f"/api/map/export/download/{file_name}",
                })
        
        return sorted(files, key=lambda x: x["created_at"], reverse=True)
    
    async def delete_export_file(self, file_name: str) -> bool:
        file_path = os.path.join(self.export_dir, file_name)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
