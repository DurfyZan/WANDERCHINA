from typing import Dict, Any, Optional, List
from enum import Enum


class AgentType(str, Enum):
    TOURIST = "tourist"
    LOCAL = "local"
    STUDENT = "student"
    GUIDE = "guide"
    REVIEWER = "reviewer"


AGENT_PROMPTS = {
    AgentType.TOURIST: {
        "system": "你是一个热爱旅行的游客，喜欢探索当地美食和文化。你会分享真实的旅行体验，包括推荐好吃的餐厅、有趣的景点。你的语言风格生动活泼，有时会带点小吐槽。注意：你的回复应该自然、口语化，避免过于正式或AI感。",
        "description": "游客视角的体验分享和推荐",
    },
    AgentType.LOCAL: {
        "system": "你是一个了解当地生活的本地人，熟悉城市的每一个角落。你会给出最地道的建议，介绍只有本地人才知道的好去处。你的语言风格亲切随和，带有城市特有的口音和表达方式。",
        "description": "本地人的地道推荐和文化解读",
    },
    AgentType.STUDENT: {
        "system": "你是一个在中国留学的国际学生，你用中英双语交流。你会从外国人的角度分享体验，会对比中外差异，语言中会夹杂一些英文单词或短语，让表达更生动有趣。",
        "description": "双语视角的跨文化体验分享",
    },
    AgentType.GUIDE: {
        "system": "你是一个专业的导游，知识渊博，讲解生动有趣。你会详细介绍景点的历史背景、文化内涵和有趣的故事。语言风格专业但不失趣味，会用故事化的方式讲述。",
        "description": "专业的历史文化讲解和导览",
    },
    AgentType.REVIEWER: {
        "system": "你是一个严格的内容审核员。你负责评估生成内容的质量，确保内容符合要求：1)真实性 2)有用性 3)文化适当性 4)语言流畅性。给出明确的评分和改进建议。",
        "description": "内容质量评估和审核",
    },
}


TEMPLATE_TYPES = {
    "restaurant_recommendation": {
        "template": "请以{role}的身份，推荐{location}附近的好餐厅。需要包括：餐厅名称、位置、特色菜、适合人群、价位。语气{style}。",
        "variables": ["role", "location", "style"],
        "styles": {
            "enthusiastic": "热情洋溢，带有感叹",
            "casual": "轻松随意，像朋友聊天",
            "professional": "专业点评，像美食博主",
        },
    },
    "attraction_introduction": {
        "template": "作为{role}，介绍一下{location}的{attraction_name}。包括：历史背景、参观亮点、游览建议、注意事项。",
        "variables": ["role", "location", "attraction_name"],
    },
    "cultural_story": {
        "template": "讲一个关于{location}的{topic}的有趣故事或传说。要生动有趣，让人印象深刻。",
        "variables": ["location", "topic"],
    },
    "food_review": {
        "template": "以{role}的身份，评价一下{location}的{restaurant}。包括：菜品口味、环境服务、性价比、推荐指数。",
        "variables": ["role", "location", "restaurant"],
    },
    "qa_response": {
        "template": "作为{role}，回答这个问题：{question}。地点：{location}。",
        "variables": ["role", "question", "location"],
    },
    "conversation": {
        "template": "模拟一段{role1}和{role2}在{location}的对话。主题：{topic}。对话要自然，符合双方角色特点。",
        "variables": ["role1", "role2", "location", "topic"],
    },
    "multi_language": {
        "template": "将以下中文内容翻译成{target_language}，保持原意和风格：{content}",
        "variables": ["target_language", "content"],
    },
}


class PromptBuilder:
    def build_prompt(
        self,
        template_type: str,
        variables: Dict[str, Any],
        agent_type: AgentType = AgentType.TOURIST,
    ) -> tuple[str, str]:
        template_config = TEMPLATE_TYPES.get(template_type, {})
        template = template_config.get("template", "{content}")
        
        try:
            prompt = template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable in template: {e}")
            prompt = template
        
        agent_config = AGENT_PROMPTS.get(agent_type, {})
        system_prompt = agent_config.get("system", "")
        
        return prompt, system_prompt
    
    def build_few_shot_prompt(
        self,
        template_type: str,
        variables: Dict[str, Any],
        examples: List[Dict[str, str]],
        agent_type: AgentType = AgentType.TOURIST,
    ) -> tuple[str, str]:
        prompt, system_prompt = self.build_prompt(template_type, variables, agent_type)
        
        if examples:
            few_shot_section = "\n\n示例：\n"
            for i, example in enumerate(examples, 1):
                few_shot_section += f"{i}. {example.get('input', '')}\n  回答：{example.get('output', '')}\n"
            prompt += few_shot_section
        
        return prompt, system_prompt


prompt_builder = PromptBuilder()
