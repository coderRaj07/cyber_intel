import pdfplumber
import re
from app.schema.taxonomy import CANONICAL_TAXONOMY


YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
NUMERIC_PATTERN = re.compile(r"^-?\d[\d,]*\.?\d*$")


def clean_numeric(value: str):
    return value.replace(",", "").strip()


def is_numeric(value: str):
    if not value:
        return False
    return bool(NUMERIC_PATTERN.match(clean_numeric(value)))


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

    num_cols = max(len(r) for r in header_rows)
    merged = []

    for col_index in range(num_cols):
        parts = []
        for row in header_rows:
            if col_index < len(row) and row[col_index]:
                parts.append(str(row[col_index]).strip())
        merged.append(" ".join(parts))

    return merged


def infer_metric_key_from_header(header_text, table_context=""):
    text = (header_text + " " + table_context).lower()

    if "employment" in text or "employees" in text or "jobs" in text:
        return "employment"

    if "firm" in text or "company" in text or "providers" in text:
        return "company_count"

    if "revenue" in text:
        return "revenue_eur"

    if "gva" in text or "gross value" in text:
        return "gross_value_added"

    if "investment" in text:
        return "investment"

    if "growth" in text or "%" in text:
        return "growth_rate"

    return None


def extract_tables(pdf_path, document_id):

    metrics = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=1):

            tables = page.extract_tables()

            if not tables:
                continue

            page_text = page.extract_text() or ""

            for table in tables:

                if not table or len(table) < 2:
                    continue

                header_rows = detect_header_rows(table)
                headers = merge_headers(header_rows)

                data_rows = table[len(header_rows):]

                # Detect if first column is a year column
                first_col_year = False
                for row in data_rows[:3]:
                    if row and YEAR_PATTERN.search(str(row[0])):
                        first_col_year = True
                        break

                for row in data_rows:

                    if not row:
                        continue

                    row_year = None

                    # If first column contains year
                    if first_col_year:
                        year_match = YEAR_PATTERN.search(str(row[0]))
                        if year_match:
                            row_year = int(year_match.group())

                    for col_index, cell in enumerate(row):

                        if not cell:
                            continue

                        cell_str = str(cell).strip()

                        # Skip year column value
                        if first_col_year and col_index == 0:
                            continue

                        if not is_numeric(cell_str):
                            continue

                        numeric_value = float(clean_numeric(cell_str))

                        header_text = ""
                        if col_index < len(headers):
                            header_text = headers[col_index]

                        metric_key = infer_metric_key_from_header(
                            header_text,
                            table_context=page_text
                        )

                        if not metric_key:
                            continue

                        unit = CANONICAL_TAXONOMY.get(
                            metric_key,
                            {"unit": "unknown"}
                        )["unit"]

                        metrics.append({
                            "document_id": document_id,
                            "metric_key": metric_key,
                            "value": numeric_value,
                            "unit": unit,
                            "year": row_year,
                            "source_type": "table",
                            "page_number": page_number,
                            "confidence_score": 0.92,
                            "raw_text": f"{headers} | {row}"
                        })

    return metrics
