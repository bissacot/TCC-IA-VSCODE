from __future__ import annotations

import pandas as pd
from fpdf import FPDF
from pathlib import Path


def export_excel(df: pd.DataFrame, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)


def export_pdf_simple(df: pd.DataFrame, path: str, title: str = "Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True)
    # write first 30 rows as simple table
    for i, row in df.head(30).iterrows():
        line = " | ".join([f"{k}:{v}" for k, v in row.items()])
        pdf.multi_cell(0, 5, line)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(path)


if __name__ == "__main__":
    # quick demo
    df = pd.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    export_excel(df, "output/report.xlsx")
    export_pdf_simple(df, "output/report.pdf")
