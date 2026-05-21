
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class AgentPersona(BaseModel):
    agent_id: str
    role_type: str = Field(description="角色类型: Tourist, Local, Expat")
    nationality: str
    language_style: str = Field(description="如: 带有美式口音的中文, 地道成都话, 极简英语")
    catchphrases: List[str] = Field(description="口头禅或常用网络词汇")
    age: Optional[int] = None
    personality: Optional[str] = None


class InteractionNode(BaseModel):
    node_id: str
    parent_id: Optional[str] = None
    agent_id: str
    content: str = Field(description="剥离了&lt;think&gt;标签后的纯净社交媒体文本")
    raw_thinking: Optional[str] = Field(description="保留的推理模型思考链内容", default=None)
    timestamp: str


class SocialDataPayload(BaseModel):
    post_id: str
    title: Optional[str] = None
    main_content: str
    location: str
    author_persona: AgentPersona
    interactions: List[InteractionNode] = Field(default_factory=list)
    annotations: Dict[str, Any] = Field(default_factory=dict, description="包含情感、意图、标签等自动化标注")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class EvaluationReport(BaseModel):
    human_likeness_score: float = Field(description="拟人度得分 1-5", ge=1, le=5)
    coherence_score: float = Field(description="连贯性得分 1-5", ge=1, le=5)
    is_passed: bool
    feedback: Optional[str] = Field(description="未通过时的具体修改意见", default=None)
    retry_count: int = Field(default=0)
