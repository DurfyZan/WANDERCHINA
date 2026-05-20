from datetime import datetime
from typing import Optional, Any, Dict
import json


def format_datetime(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    if dt is None:
        return ""
    return dt.strftime(format)


def parse_datetime(dt_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    try:
        return datetime.strptime(dt_str, format)
    except (ValueError, TypeError):
        return None


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default


def validate_coordinates(lat: float, lng: float) -> bool:
    return -90 <= lat <= 90 and -180 <= lng <= 180


def calculate_bounding_box(
    lat: float,
    lng: float,
    radius_meters: float
) -> Dict[str, float]:
    lat_delta = radius_meters / 111000
    lng_delta = radius_meters / (111000 * abs(lat) if lat != 0 else 111000)
    
    return {
        "min_lat": lat - lat_delta,
        "max_lat": lat + lat_delta,
        "min_lng": lng - lng_delta,
        "max_lng": lng + lng_delta,
    }


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def normalize_language_code(lang: str) -> str:
    lang_map = {
        "zh": "zh",
        "zh-cn": "zh",
        "zh_tw": "zh",
        "en": "en",
        "eng": "en",
        "ja": "ja",
        "jpn": "ja",
        "ko": "ko",
        "kor": "ko",
    }
    return lang_map.get(lang.lower(), "zh")


def generate_cache_key(*args, **kwargs) -> str:
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)


class PaginationHelper:
    @staticmethod
    def paginate(items: list, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            "items": items[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
