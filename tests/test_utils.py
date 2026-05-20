from app.utils.helpers import (
    format_datetime,
    validate_coordinates,
    calculate_bounding_box,
    truncate_text,
)


def test_format_datetime():
    from datetime import datetime
    
    dt = datetime(2024, 1, 15, 12, 30, 45)
    result = format_datetime(dt)
    assert "2024-01-15" in result
    assert "12:30:45" in result


def test_validate_coordinates():
    assert validate_coordinates(31.2304, 121.4737) == True
    assert validate_coordinates(91, 0) == False
    assert validate_coordinates(0, 181) == False


def test_calculate_bounding_box():
    lat, lng = 31.2304, 121.4737
    radius = 1000
    
    bbox = calculate_bounding_box(lat, lng, radius)
    
    assert "min_lat" in bbox
    assert "max_lat" in bbox
    assert "min_lng" in bbox
    assert "max_lng" in bbox
    
    assert bbox["min_lat"] < lat < bbox["max_lat"]
    assert bbox["min_lng"] < lng < bbox["max_lng"]


def test_truncate_text():
    text = "这是一段很长的文本，用于测试截断功能" * 10
    
    truncated = truncate_text(text, max_length=50)
    assert len(truncated) <= 53
    assert "..." in truncated
