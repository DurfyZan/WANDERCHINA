
import os
import re
import httpx
from typing import Dict, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class LLMSettings(BaseSettings):
    deepseek_api_key: str = Field(default="")
    deepseek_base_url: str = Field(default="https://api.deepseek.com")
    deepseek_model: str = Field(default="deepseek-chat")
    qwen_api_key: str = Field(default="")
    qwen_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1")
    qwen_model: str = Field(default="qwen3-max")
    judge_api_key: str = Field(default="")
    judge_base_url: str = Field(default="https://api.deepseek.com")
    judge_model: str = Field(default="deepseek-chat")
    mongodb_uri: str = Field(default="mongodb://localhost:27017")
    mongodb_db_name: str = Field(default="social_agent_data")
    output_dir: str = Field(default="./output")
    max_retry_times: int = Field(default=3)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = LLMSettings()


class LLMResponse:
    def __init__(self, thinking_process: Optional[str], final_reply: str, raw_response: str):
        self.thinking_process = thinking_process
        self.final_reply = final_reply
        self.raw_response = raw_response


class LLMRouter:
    THINK_TAG_PATTERN = re.compile(r"<think>(.*?)</think>", re.DOTALL)

    def __init__(self, provider: str = "deepseek"):
        self.provider = provider.lower()
        self._setup_provider()

    def _setup_provider(self):
        if self.provider == "deepseek":
            self.api_key = settings.deepseek_api_key
            self.base_url = settings.deepseek_base_url
            self.model = settings.deepseek_model
        elif self.provider == "qwen":
            self.api_key = settings.qwen_api_key
            self.base_url = settings.qwen_base_url
            self.model = settings.qwen_model
        elif self.provider == "judge":
            self.api_key = settings.judge_api_key
            self.base_url = settings.judge_base_url
            self.model = settings.judge_model
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _extract_thinking_and_content(self, text: str) -> Tuple[Optional[str], str]:
        match = self.THINK_TAG_PATTERN.search(text)
        if match:
            thinking_process = match.group(1).strip()
            final_reply = self.THINK_TAG_PATTERN.sub("", text).strip()
            return thinking_process, final_reply
        return None, text.strip()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError))
    )
    async def agenerate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        enable_thinking: bool = False
    ) -> LLMResponse:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            raw_response = result["choices"][0]["message"]["content"]

        thinking_process, final_reply = self._extract_thinking_and_content(raw_response)
        return LLMResponse(
            thinking_process=thinking_process,
            final_reply=final_reply,
            raw_response=raw_response
        )

    async def agenerate_simple(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        resp = await self.agenerate(
            system_prompt="你是一个有用的助手。",
            user_prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return resp.final_reply
