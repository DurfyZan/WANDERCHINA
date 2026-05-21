
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from src.core.schemas import SocialDataPayload


class DatasetExporter:
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_to_alpaca(self, payloads: List[SocialDataPayload]) -> List[Dict[str, str]]:
        alpaca_data = []
        for payload in payloads:
            instruction = f"根据以下场景，生成一篇社交媒体帖子：\n地点：{payload.location}\n话题：{', '.join(payload.annotations.get('topic_tags', []))}"
            alpaca_data.append({
                "instruction": instruction,
                "input": "",
                "output": payload.main_content
            })

            for i, interaction in enumerate(payload.interactions[1:], 1):
                prev_context = self._build_context_up_to(payload.interactions, i)
                alpaca_data.append({
                    "instruction": "根据上文对话，生成一条符合人设的社交媒体回复",
                    "input": prev_context,
                    "output": interaction.content
                })

        return alpaca_data

    def export_to_sharegpt(self, payloads: List[SocialDataPayload]) -> List[Dict[str, Any]]:
        sharegpt_data = []
        for payload in payloads:
            conversations = []
            for i, interaction in enumerate(payload.interactions):
                role = "user" if i % 2 == 0 else "assistant"
                conversations.append({
                    "from": role,
                    "value": interaction.content
                })

            sharegpt_data.append({
                "id": payload.post_id,
                "conversations": conversations,
                "meta": {
                    "location": payload.location,
                    "annotations": payload.annotations,
                    "created_at": payload.created_at
                }
            })

        return sharegpt_data

    def _build_context_up_to(self, interactions: List, end_idx: int) -> str:
        lines = []
        for i in range(end_idx):
            interaction = interactions[i]
            if i == 0:
                lines.append(f"【主帖】\n{interaction.content}\n")
            else:
                lines.append(f"【回复 {i}】\n{interaction.content}\n")
        return "\n".join(lines)

    async def asave_alpaca(self, payloads: List[SocialDataPayload], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alpaca_{timestamp}.jsonl"

        filepath = os.path.join(self.output_dir, filename)
        alpaca_data = self.export_to_alpaca(payloads)

        with open(filepath, 'w', encoding='utf-8') as f:
            for item in alpaca_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        return filepath

    async def asave_sharegpt(self, payloads: List[SocialDataPayload], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sharegpt_{timestamp}.jsonl"

        filepath = os.path.join(self.output_dir, filename)
        sharegpt_data = self.export_to_sharegpt(payloads)

        with open(filepath, 'w', encoding='utf-8') as f:
            for item in sharegpt_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

        return filepath

    async def asave_raw(self, payloads: List[SocialDataPayload], filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"raw_{timestamp}.jsonl"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            for payload in payloads:
                f.write(payload.model_dump_json() + '\n')

        return filepath
