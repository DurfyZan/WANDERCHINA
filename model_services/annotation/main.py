"""自动标注微服务 — 文本类别、情感、话题标签。"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="WANDERCHINA Annotation Service", version="0.1.0")


class AnnotateRequest(BaseModel):
    texts: list[str]
    categories: list[str] | None = None


@app.post("/annotate")
async def annotate(req: AnnotateRequest):
    annotations = []
    for text in req.texts:
        lower = text.lower()
        sentiment = "negative" if any(w in lower for w in ("bad", "差", "踩雷")) else "positive"
        category = "qa_pair" if text.strip().startswith(("Q:", "问")) else "post"
        tags = []
        for kw in ("成都", "北京", "上海", "food", "小吃", "地铁"):
            if kw in text:
                tags.append(kw)
        annotations.append(
            {"category": category, "sentiment": sentiment, "topic_tags": tags or ["general"]}
        )
    return {"annotations": annotations}


@app.post("/moderate")
async def moderate(payload: dict):
    text = payload.get("text", "")
    blocked = any(w in text for w in ("违禁词示例",))
    return {"safe": not blocked, "labels": [] if not blocked else ["sensitive"]}
