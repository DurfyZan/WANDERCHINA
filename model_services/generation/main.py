"""
数据生成微服务 — 对接 DeepSeek / Qwen 等，可独立扩缩容。
部署: uvicorn model_services.generation.main:app --port 8001
"""
import os
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="WANDERCHINA Generation Service", version="0.1.0")


class GenerateRequest(BaseModel):
    type: str
    scenario: str | None = None
    count: int = 10
    provider: str = "deepseek"
    prompt_config: dict[str, Any] = {}
    humanize: bool = True


@app.post("/generate")
async def generate(req: GenerateRequest):
    # TODO: 调用真实 LLM API（OPENAI_COMPAT_BASE_URL + provider key）
    scenario = req.scenario or "成都宽窄巷子"
    items = []
    templates = {
        "post": f"今天在{scenario}逛了一下午，本地人推荐的茶馆比攻略靠谱多了。",
        "comment": f"同意，{scenario}周末人少一点，早上九点前去最舒服。",
        "qa_pair": f"Q: {scenario}附近有什么不踩雷的小吃？ A: 巷子口那家豆花，别点游客套餐。",
        "recommendation": f"{scenario}步行十分钟有家社区书店，适合躲雨顺便练中文。",
    }
    base = templates.get(req.type, templates["post"])
    for i in range(req.count):
        items.append(
            {
                "text": f"{base} (#{i+1})",
                "category": req.type,
                "sentiment": "positive",
                "topic_tags": [scenario, "travel", "local-tip"],
                "provider": req.provider,
                "humanize": req.humanize,
            }
        )
    return {"items": items, "model_version": os.getenv("MODEL_VERSION", "stub-0.1")}


@app.post("/translate")
async def translate(payload: dict[str, str]):
    return {"translation": f"[{payload.get('target_lang', 'en')}] {payload.get('text', '')}"}
