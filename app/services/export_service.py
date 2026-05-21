import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd

EXPORT_DIR = Path("data/exports")


def export_dataset(
    records: list[dict[str, Any]],
    job_id: int,
    fmt: str,
    label_schema: str,
) -> tuple[str, int]:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORT_DIR / f"job_{job_id}.{fmt}"

    rows = [_normalize_record(r, label_schema) for r in records]

    if fmt == "jsonl":
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    elif fmt == "csv":
        pd.DataFrame(rows).to_csv(path, index=False)
    elif fmt == "tsv":
        pd.DataFrame(rows).to_csv(path, sep="\t", index=False)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    return str(path), len(rows)


def _normalize_record(record: dict[str, Any], label_schema: str) -> dict[str, Any]:
    base = {
        "text": record.get("text", ""),
        "metadata": record.get("metadata_json") or {},
    }
    if label_schema == "sentiment":
        base["labels"] = {"sentiment": record.get("sentiment")}
    elif label_schema == "qa_pair":
        base["messages"] = record.get("messages") or [
            {"role": "user", "content": record.get("question", "")},
            {"role": "assistant", "content": record.get("answer", record.get("text", ""))},
        ]
    else:
        base["labels"] = {
            "category": record.get("category"),
            "topic_tags": (record.get("topic_tags") or "").split(",") if record.get("topic_tags") else [],
        }
    return base
