from typing import Dict
from .logger import logger


def generate_quality_report(report: Dict) -> Dict:
    # Simple pass-through formatting and percentages
    total = report.get('processed_records', 0)
    missing = report.get('missing_values', {})
    missing_count = sum(missing.values()) if isinstance(missing, dict) else 0
    invalid = report.get('invalid_records', 0)
    duplicates = report.get('duplicates_removed', 0)

    return {
        'processed_records': total,
        'invalid_records': invalid,
        'duplicates_removed': duplicates,
        'missing_values_count': missing_count,
        'missing_values_percent': (missing_count / (total or 1)) * 100,
    }
