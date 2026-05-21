
import json
import re
from typing import Optional
from src.core.schemas import SocialDataPayload, EvaluationReport
from src.core.llm_router import LLMRouter


class GEvaluator:
    def __init__(self):
        self.llm = LLMRouter(provider="judge")

    def _build_evaluation_prompt(self, payload: SocialDataPayload) -> str:
        context_lines = [f"【主帖】\n{payload.main_content}\n"]
        for i, interaction in enumerate(payload.interactions[1:], 1):
            context_lines.append(f"【回复 {i}】\n{interaction.content}\n")
        full_context = "\n".join(context_lines)

        return f"""你是一个严格的社交媒体内容质量评估专家。请对以下社交媒体对话进行评估。

【评估内容】
{full_context}

【评估维度】
1. 拟人度 (human_likeness): 内容看起来像真实的人写的吗？有没有明显的AI痕迹？
   - 5分: 完全像真人，自然流畅，有个性
   - 3分: 一般，有一些AI感但还能接受
   - 1分: 明显的AI生成，很生硬

2. 上下文连贯性 (coherence): 回复之间是否逻辑连贯，对话是否自然？
   - 5分: 非常连贯，互动自然流畅
   - 3分: 基本连贯，但有些地方不太自然
   - 1分: 不连贯，各说各的

【输出格式】
请严格按照以下JSON格式输出，不要加其他内容：
{{
    "human_likeness_score": 分数,
    "coherence_score": 分数,
    "is_passed": true/false,
    "feedback": "如果未通过，请详细说明具体问题和改进建议；如果通过，可以写'质量良好'"
}}

【通过标准】
只有当两个分数都 >= 4 分时，is_passed 才为 true，否则为 false。"""

    def _parse_evaluation_result(self, text: str) -> EvaluationReport:
        try:
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return EvaluationReport(
                    human_likeness_score=float(data.get("human_likeness_score", 1)),
                    coherence_score=float(data.get("coherence_score", 1)),
                    is_passed=bool(data.get("is_passed", False)),
                    feedback=data.get("feedback", ""),
                    retry_count=0
                )
        except Exception:
            pass
        return EvaluationReport(
            human_likeness_score=1,
            coherence_score=1,
            is_passed=False,
            feedback="评估结果解析失败",
            retry_count=0
        )

    async def aevaluate(self, payload: SocialDataPayload) -> EvaluationReport:
        system_prompt = "你是一个专业的内容质量评估专家，严格按照要求进行评估。"
        user_prompt = self._build_evaluation_prompt(payload)

        response = await self.llm.agenerate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1
        )

        return self._parse_evaluation_result(response.final_reply)


class EvaluationLoop:
    def __init__(self, max_retries: int = 3):
        self.evaluator = GEvaluator()
        self.max_retries = max_retries

    async def arun_with_evaluation(
        self,
        generate_func,
        scenario: str,
        location: str
    ) -> tuple[SocialDataPayload, EvaluationReport]:
        retry_count = 0
        while retry_count <= self.max_retries:
            payload = await generate_func(scenario, location)
            report = await self.evaluator.aevaluate(payload)
            report.retry_count = retry_count

            if report.is_passed:
                return payload, report

            retry_count += 1
            if retry_count > self.max_retries:
                return payload, report

        return payload, report
