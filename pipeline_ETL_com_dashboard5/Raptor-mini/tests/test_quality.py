from __future__ import annotations

from src.etl.quality import DataQualityReport, build_quality_report, summarize_reports


def test_build_quality_report() -> None:
    metrics = {"processed_records": 10, "invalid_records": 2, "duplicates_removed": 1, "missing_values": 5}
    report = build_quality_report(metrics, "sales")
    assert report.entity == "sales"
    assert report.processed_records == 10
    assert report.missing_percentage == 50.0


def test_summarize_reports() -> None:
    reports = [
        DataQualityReport("sales", 10, 1, 1, 2),
        DataQualityReport("customers", 5, 0, 0, 1),
    ]
    result = summarize_reports(reports)
    assert result["total_processed"] == 15
    assert result["total_invalid"] == 1
