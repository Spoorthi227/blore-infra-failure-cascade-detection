"""
Utility functions for data processing and helpers
"""


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude values"""
    return -90 <= lat <= 90 and -180 <= lon <= 180


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates (simplified)"""
    # TODO: Implement proper Haversine distance calculation
    import math
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)


def clean_data(data: list) -> list:
    """Clean and normalize infrastructure data"""
    cleaned = []
    for record in data:
        # Remove None values where appropriate
        cleaned_record = {k: v for k, v in record.items() if v is not None}
        cleaned.append(cleaned_record)
    return cleaned
