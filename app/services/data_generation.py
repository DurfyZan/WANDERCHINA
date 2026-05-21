from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import GeneratedData, DataType, Language, UserRole
from app.services.model_router import model_router
from app.services.prompt_manager import PromptBuilder, AgentType
from app.schemas.map import GenerateDataRequest, GenerateDataResponse
import logging

logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(
        self,
        agent_type: AgentType,
        db: AsyncSession,
    ):
        self.agent_type = agent_type
        self.db = db
        self.prompt_builder = PromptBuilder()
    
    async def generate(
        self,
        location: str,
        data_type: DataType,
        language: Language,
        variables: Dict[str, Any],
        model_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        prompt, system_prompt = self.prompt_builder.build_prompt(
            template_type=data_type.value,
            variables=variables,
            agent_type=self.agent_type,
        )
        
        try:
            response = await model_router.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                model_type=model_name,
                task_type=self._get_task_type(data_type),
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
            )
            
            return {
                "content": response["content"],
                "success": True,
                "model": response.get("model"),
                "usage": response.get("usage"),
            }
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            return {
                "content": "",
                "success": False,
                "error": str(e),
            }
    
    def _get_task_type(self, data_type: DataType) -> str:
        mapping = {
            DataType.RECOMMENDATION: "creative_writing",
            DataType.REVIEW: "creative_writing",
            DataType.Q_A: "reasoning",
            DataType.COMMENTARY: "creative_writing",
            DataType.CONVERSATION: "creative_writing",
        }
        return mapping.get(data_type, "general")


class TouristAgent(BaseAgent):
    def __init__(self, db: AsyncSession):
        super().__init__(AgentType.TOURIST, db)
    
    async def generate_experience_sharing(
        self,
        location: str,
        poi_name: Optional[str] = None,
        language: Language = Language.ZH,
        **kwargs
    ) -> Dict[str, Any]:
        variables = {
            "role": "游客",
            "location": location,
            "poi_name": poi_name or location,
        }
        
        return await self.generate(
            location=location,
            data_type=DataType.REVIEW,
            language=language,
            variables=variables,
            **kwargs
        )
    
    async def generate_question(
        self,
        location: str,
        topic: str,
        language: Language = Language.ZH,
        **kwargs
    ) -> Dict[str, Any]:
        variables = {
            "role": "游客",
            "question": f"{topic}怎么样？",
            "location": location,
        }
        
        return await self.generate(
            location=location,
            data_type=DataType.Q_A,
            language=language,
            variables=variables,
            **kwargs
        )


class LocalAgent(BaseAgent):
    def __init__(self, db: AsyncSession):
        super().__init__(AgentType.LOCAL, db)
    
    async def generate_recommendation(
        self,
        location: str,
        poi_type: str = "餐厅",
        language: Language = Language.ZH,
        **kwargs
    ) -> Dict[str, Any]:
        variables = {
            "role": "本地人",
            "location": location,
            "style": "热情",
            "poi_type": poi_type,
        }
        
        return await self.generate(
            location=location,
            data_type=DataType.RECOMMENDATION,
            language=language,
            variables=variables,
            **kwargs
        )
    
    async def generate_cultural_explanation(
        self,
        location: str,
        topic: str,
        language: Language = Language.ZH,
        **kwargs
    ) -> Dict[str, Any]:
        variables = {
            "role": "本地人",
            "location": location,
            "topic": topic,
        }
        
        return await self.generate(
            location=location,
            data_type=DataType.COMMENTARY,
            language=language,
            variables=variables,
            **kwargs
        )


class StudentAgent(BaseAgent):
    def __init__(self, db: AsyncSession):
        super().__init__(AgentType.STUDENT, db)
    
    async def generate_bilingual_review(
        self,
        location: str,
        poi_name: Optional[str] = None,
        language: Language = Language.MULTI,
        **kwargs
    ) -> Dict[str, Any]:
        variables = {
            "role": "留学生",
            "location": location,
            "poi_name": poi_name or location,
        }
        
        return await self.generate(
            location=location,
            data_type=DataType.REVIEW,
            language=language,
            variables=variables,
            **kwargs
        )
    
    async def generate_cross_cultural_comparison(
        self,
        location: str,
        topic: str,
        language: Language = Language.MULTI,
        **kwargs
    ) -> Dict[str, Any]:
        variables = {
            "role": "留学生",
            "location": location,
            "topic": topic,
        }
        
        return await self.generate(
            location=location,
            data_type=DataType.COMMENTARY,
            language=language,
            variables=variables,
            **kwargs
        )


class GuideAgent(BaseAgent):
    def __init__(self, db: AsyncSession):
        super().__init__(AgentType.GUIDE, db)
    
    async def generate_commentary(
        self,
        location: str,
        attraction_name: str,
        language: Language = Language.ZH,
        **kwargs
    ) -> Dict[str, Any]:
        variables = {
            "role": "导游",
            "location": location,
            "attraction_name": attraction_name,
        }
        
        return await self.generate(
            location=location,
            data_type=DataType.COMMENTARY,
            language=language,
            variables=variables,
            **kwargs
        )
    
    async def generate_historical_story(
        self,
        location: str,
        topic: str,
        language: Language = Language.ZH,
        **kwargs
    ) -> Dict[str, Any]:
        variables = {
            "role": "导游",
            "location": location,
            "topic": topic,
        }
        
        return await self.generate(
            location=location,
            data_type=DataType.COMMENTARY,
            language=language,
            variables=variables,
            **kwargs
        )


class ReviewerAgent(BaseAgent):
    def __init__(self, db: AsyncSession):
        super().__init__(AgentType.REVIEWER, db)
    
    async def evaluate_content(
        self,
        content: str,
        criteria: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        evaluation_prompt = f"""请评估以下内容的质量：

{content}

评估标准：
1. 真实性（内容是否真实可信）
2. 有用性（对读者是否有帮助）
3. 文化适当性（是否符合文化规范）
4. 语言流畅性（语言表达是否流畅自然）
5. 避免AI感（是否自然，不像是模板生成）

请给出0-10的评分和简要评语。"""
        
        try:
            response = await model_router.generate(
                prompt=evaluation_prompt,
                model_type="deepseek",
                task_type="reasoning",
                temperature=0.3,
                max_tokens=500,
            )
            
            evaluation_text = response["content"]
            
            score = self._parse_score(evaluation_text)
            
            return {
                "score": score,
                "evaluation": evaluation_text,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return {
                "score": 0,
                "evaluation": "",
                "success": False,
                "error": str(e),
            }
    
    def _parse_score(self, evaluation_text: str) -> float:
        import re
        
        patterns = [
            r"综合评分[：:]\s*(\d+\.?\d*)",
            r"总分[：:]\s*(\d+\.?\d*)",
            r"评分[：:]\s*(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*/\s*10",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, evaluation_text)
            if match:
                try:
                    return float(match.group(1)) / 10.0
                except ValueError:
                    continue
        
        return 0.5


AGENT_REGISTRY = {
    AgentType.TOURIST: TouristAgent,
    AgentType.LOCAL: LocalAgent,
    AgentType.STUDENT: StudentAgent,
    AgentType.GUIDE: GuideAgent,
    AgentType.REVIEWER: ReviewerAgent,
}


class DataGenerationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.agents = {}
        for agent_type, agent_class in AGENT_REGISTRY.items():
            self.agents[agent_type] = agent_class(db)
    
    def get_agent(self, agent_type: AgentType) -> BaseAgent:
        return self.agents.get(agent_type)
    
    async def generate_single(
        self,
        request: GenerateDataRequest
    ) -> GenerateDataResponse:
        agent_type = self._get_agent_type(request.agent_type, request.user_role)
        agent = self.get_agent(agent_type)
        
        if not agent:
            raise ValueError(f"Invalid agent type: {agent_type}")
        
        variables = {
            "role": agent_type.value,
            "location": request.location,
            **(request.metadata or {}),
        }
        
        result = await agent.generate(
            location=request.location,
            data_type=request.data_type,
            language=request.language,
            variables=variables,
            model_name=request.model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        if not result["success"]:
            raise RuntimeError(f"Generation failed: {result.get('error')}")
        
        quality_score = None
        reviewer = self.get_agent(AgentType.REVIEWER)
        if reviewer:
            eval_result = await reviewer.evaluate_content(result["content"])
            if eval_result["success"]:
                quality_score = eval_result["score"]
        
        generated_data = GeneratedData(
            id=str(uuid4()),
            agent_type=agent_type.value,
            data_type=request.data_type,
            content=result["content"],
            language=request.language,
            user_role=request.user_role,
            location_context=request.location,
            metadata={
                "model": result.get("model"),
                "usage": result.get("usage"),
                **(request.metadata or {}),
            },
            quality_score=quality_score,
            needs_review=quality_score is None or quality_score < 0.7,
        )
        
        self.db.add(generated_data)
        await self.db.flush()
        await self.db.refresh(generated_data)
        
        return GenerateDataResponse(
            id=generated_data.id,
            content=generated_data.content,
            agent_type=generated_data.agent_type,
            data_type=generated_data.data_type,
            language=generated_data.language,
            metadata=generated_data.metadata,
            quality_score=quality_score,
            created_at=generated_data.created_at,
        )
    
    def _get_agent_type(
        self,
        agent_type: Optional[str],
        user_role: UserRole
    ) -> AgentType:
        if agent_type:
            try:
                return AgentType(agent_type)
            except ValueError:
                pass
        
        role_to_agent = {
            UserRole.TOURIST: AgentType.TOURIST,
            UserRole.LOCAL: AgentType.LOCAL,
            UserRole.STUDENT: AgentType.STUDENT,
            UserRole.GUIDE: AgentType.GUIDE,
        }
        
        return role_to_agent.get(user_role, AgentType.TOURIST)
