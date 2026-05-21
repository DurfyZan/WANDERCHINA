import json
from typing import Any

import httpx

from app.config import get_settings


class ModelServiceClient:
    """REST client for microservice-style LLM / eval endpoints."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate(
        self,
        generation_type: str,
        scenario: str | None,
        count: int,
        provider: str,
        prompt_config: dict[str, Any] | None,
        humanize: bool,
    ) -> list[dict[str, Any]]:
        payload = {
            "type": generation_type,
            "scenario": scenario,
            "count": count,
            "provider": provider,
            "prompt_config": prompt_config or {},
            "humanize": humanize,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(self.settings.model_generation_url, json=payload)
            resp.raise_for_status()
            return resp.json().get("items", [])

    async def annotate(self, texts: list[str], categories: list[str] | None) -> list[dict[str, Any]]:
        payload = {"texts": texts, "categories": categories}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self.settings.model_annotation_url, json=payload)
            resp.raise_for_status()
            return resp.json().get("annotations", [])

    async def evaluate_quality(
        self,
        candidates: list[str],
        references: list[str] | None,
        metrics: list[str],
    ) -> dict[str, float]:
        payload = {"candidates": candidates, "references": references, "metrics": metrics}
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(self.settings.model_quality_url, json=payload)
            resp.raise_for_status()
            return resp.json().get("scores", {})

    async def moderate(self, text: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                self.settings.model_annotation_url.replace("/annotate", "/moderate"),
                json={"text": text},
            )
            if resp.status_code == 404:
                return {"safe": True, "labels": []}
            resp.raise_for_status()
            return resp.json()

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                self.settings.model_generation_url.replace("/generate", "/translate"),
                json={"text": text, "source_lang": source_lang, "target_lang": target_lang},
            )
            if resp.status_code == 404:
                return text
            resp.raise_for_status()
            return resp.json().get("translation", text)
