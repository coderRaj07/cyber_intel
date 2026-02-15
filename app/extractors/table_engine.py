import pdfplumber
import re
from app.schema.taxonomy import CANONICAL_TAXONOMY


YEAR_PATTERN = re.compile(r"20\d{2}")
NUMERIC_PATTERN = re.compile(r"^-?\d[\d,]*\.?\d*$")


def is_numeric(value: str):
    if not value:
        return False
    value = value.replace(",", "").strip()
    return bool(NUMERIC_PATTERN.match(value))


def detect_header_rows(table):
    """
    Detect header rows until first mostly-numeric row.
    """
    header_rows = []
    for row in table:
        numeric_count = sum(is_numeric(str(cell)) for cell in row if cell)
        if numeric_count > len(row) / 2:
            break
        header_rows.append(row)

    return header_rows


def merge_headers(header_rows):
    """
    Merge multi-line headers column-wise.
    """
    if not header_rows:
        return []

    merged = []
    num_cols = max(len(r) for r in header_rows)

    for col_index in range(num_cols):
        parts = []
        for row in header_rows:
            if col_index < len(row) and row[col_index]:
                parts.append(str(row[col_index]).strip())
        merged.append(" ".join(parts))

    return merged


def normalize_header(header):
    if not header:
        return ""
    return header.lower().replace("\n", " ").strip()


def infer_metric_key(header_text):
    lower = header_text.lower()

    if "employment" in lower or "employees" in lower:
        return "employment"

    if "firm" in lower or "company" in lower:
        return "company_count"

    if "revenue" in lower:
        return "revenue_eur"

    if "gva" in lower or "gross value" in lower:
        return "gross_value_added"

    if "investment" in lower:
        return "investment"

    if "growth" in lower or "%" in lower:
        return "growth_rate"

    return "table_metric"


def extract_tables(pdf_path, document_id):

    metrics = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            tables = page.extract_tables()

            if not tables:
                continue

            for table in tables:

                if not table or len(table) < 2:
                    continue

                header_rows = detect_header_rows(table)
                headers = merge_headers(header_rows)

                data_rows = table[len(header_rows):]

                for row in data_rows:

                    for col_index, cell in enumerate(row):

                        if not cell:
                            continue

                        value = str(cell).replace(",", "").strip()

                        if not is_numeric(value):
                            continue

                        numeric_value = float(value)

                        header_text = ""
                        if col_index < len(headers):
                            header_text = normalize_header(headers[col_index])

                        metric_key = infer_metric_key(header_text)

                        year_match = YEAR_PATTERN.search(header_text)
                        year = int(year_match.group()) if year_match else None

                        unit = CANONICAL_TAXONOMY.get(
                            metric_key,
                            {"unit": "unknown"}
                        )["unit"]

                        metrics.append({
                            "document_id": document_id,
                            "metric_key": metric_key,
                            "value": numeric_value,
                            "unit": unit,
                            "year": year,
                            "source_type": "table",
                            "page_number": page_number,
                            "confidence_score": 0.9,
                            "raw_text": str(row)
                        })

    return metrics
