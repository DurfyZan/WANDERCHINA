from typing import Optional, Dict, Any, List
from app.services.model_clients import MODEL_CLIENTS, BaseModelClient
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class ModelRouter:
    def __init__(self):
        self.clients: Dict[str, BaseModelClient] = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        if settings.deepseek_api_key:
            self.clients["deepseek"] = MODEL_CLIENTS["deepseek"](
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                model_name="deepseek-chat",
            )
        
        if settings.qwen_api_key:
            self.clients["qwen"] = MODEL_CLIENTS["qwen"](
                api_key=settings.qwen_api_key,
                base_url=settings.qwen_base_url,
                model_name="qwen-turbo",
            )
        
        if settings.openai_api_key:
            self.clients["openai"] = MODEL_CLIENTS["openai"](
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                model_name="gpt-4",
            )
        
        if settings.anthropic_api_key:
            self.clients["anthropic"] = MODEL_CLIENTS["anthropic"](
                api_key=settings.anthropic_api_key,
                base_url="https://api.anthropic.com/v1",
                model_name="claude-3-opus-20240229",
            )
    
    def get_client(self, model_type: str) -> Optional[BaseModelClient]:
        return self.clients.get(model_type)
    
    def get_best_client(self, task_type: str) -> Optional[BaseModelClient]:
        if not settings.model_routing_enabled:
            return self.clients.get("deepseek")
        
        routing_rules = {
            "code_generation": ["deepseek", "qwen"],
            "creative_writing": ["openai", "anthropic", "qwen"],
            "translation": ["deepseek", "qwen"],
            "reasoning": ["deepseek", "anthropic"],
            "general": ["deepseek", "qwen", "openai"],
        }
        
        preferred_models = routing_rules.get(task_type, ["deepseek"])
        
        for model_type in preferred_models:
            if model_type in self.clients:
                return self.clients[model_type]
        
        return self.clients.get("deepseek") if self.clients else None
    
    async def generate(
        self,
        prompt: str,
        model_type: Optional[str] = None,
        system_prompt: Optional[str] = None,
        task_type: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        if model_type and model_type in self.clients:
            client = self.clients[model_type]
        else:
            client = self.get_best_client(task_type)
        
        if not client:
            raise ValueError("No available model client")
        
        return await client.generate(prompt, system_prompt, **kwargs)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_type: Optional[str] = None,
        task_type: str = "general",
        **kwargs
    ) -> Dict[str, Any]:
        if model_type and model_type in self.clients:
            client = self.clients[model_type]
        else:
            client = self.get_best_client(task_type)
        
        if not client:
            raise ValueError("No available model client")
        
        return await client.chat(messages, **kwargs)


model_router = ModelRouter()
