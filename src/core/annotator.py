
import json
import re
from typing import Dict, Any
from src.core.schemas import SocialDataPayload
from src.core.llm_router import LLMRouter


class AutoAnnotator:
    def __init__(self):
        self.llm = LLMRouter(provider="deepseek")

    def _build_annotation_prompt(self, payload: SocialDataPayload) -> str:
        context_lines = [f"【主帖】\n{payload.main_content}\n"]
        for i, interaction in enumerate(payload.interactions[1:], 1):
            context_lines.append(f"【回复 {i}】\n{interaction.content}\n")
        full_context = "\n".join(context_lines)

        return f"""请对以下社交媒体对话进行自动标注分析。

【对话内容】
{full_context}

【标注任务】
请分析并提取以下信息：
1. sentiment: 整体情感倾向 (positive/negative/neutral/anxious)
2. intent: 用户的主要意图 (ask_for_help/complaint/share_experience/recommendation/discussion)
3. topic_tags: 3-5个相关话题标签，用逗号分隔
4. key_themes: 2-3个核心主题

【输出格式】
请严格按照以下JSON格式输出，不要加其他内容：
{{
    "sentiment": "情感倾向",
    "intent": "用户意图",
    "topic_tags": "标签1,标签2,标签3",
    "key_themes": "主题1,主题2"
}}"""

    def _parse_annotation_result(self, text: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return {
                    "sentiment": data.get("sentiment", "neutral"),
                    "intent": data.get("intent", "discussion"),
                    "topic_tags": [tag.strip() for tag in data.get("topic_tags", "").split(",") if tag.strip()],
                    "key_themes": [theme.strip() for theme in data.get("key_themes", "").split(",") if theme.strip()]
                }
        except Exception:
            pass
        return {
            "sentiment": "neutral",
            "intent": "discussion",
            "topic_tags": [],
            "key_themes": []
        }

    async def aannotate(self, payload: SocialDataPayload) -> SocialDataPayload:
        system_prompt = "你是一个专业的社交媒体内容分析专家，擅长情感分析和内容标注。"
        user_prompt = self._build_annotation_prompt(payload)

        response = await self.llm.agenerate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1
        )

        annotations = self._parse_annotation_result(response.final_reply)
        payload.annotations = annotations
        return payload
