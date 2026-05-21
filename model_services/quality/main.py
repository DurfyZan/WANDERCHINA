"""数据质量评估微服务 — 可扩展 BERTScore / 外部 Dynabench 等。"""
from fastapi import FastAPI
from pydantic import BaseModel

from app.services.quality_evaluator import evaluate_batch

app = FastAPI(title="WANDERCHINA Quality Service", version="0.1.0")


class EvalRequest(BaseModel):
    candidates: list[str]
    references: list[str] | None = None
    metrics: list[str] = ["bleu", "rouge", "diversity", "perplexity"]


@app.post("/evaluate")
async def evaluate(req: EvalRequest):
    scores = evaluate_batch(req.candidates, req.references, req.metrics)
    return {"scores": scores}
