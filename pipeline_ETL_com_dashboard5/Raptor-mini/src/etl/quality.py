from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class DataQualityReport:
    entity: str
    processed_records: int
    invalid_records: int
    duplicates_removed: int
    missing_values: int

    @property
    def missing_percentage(self) -> float:
        if self.processed_records == 0:
            return 0.0
        return round(self.missing_values / (self.processed_records * 1), 4) * 100


def build_quality_report(metrics: dict[str, int], entity: str) -> DataQualityReport:
    return DataQualityReport(
        entity=entity,
        processed_records=metrics.get("processed_records", 0),
        invalid_records=metrics.get("invalid_records", 0),
        duplicates_removed=metrics.get("duplicates_removed", 0),
        missing_values=metrics.get("missing_values", 0),
    )


def summarize_reports(reports: list[DataQualityReport]) -> dict[str, Any]:
    return {
        "total_processed": sum(report.processed_records for report in reports),
        "total_invalid": sum(report.invalid_records for report in reports),
        "total_duplicates": sum(report.duplicates_removed for report in reports),
        "total_missing": sum(report.missing_values for report in reports),
        "reports": [report.__dict__ for report in reports],
    }
