import fitz
import re
import math

# YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

NUMERIC_PATTERN = re.compile(r"^\d+(\.\d+)?$")


def is_numeric(text):
    return bool(NUMERIC_PATTERN.match(text.strip()))


def extract_axis_labels(page):
    """
    Extract numeric Y-axis ticks and X-axis year labels.
    Hardened against noisy text like '2022 EDITION'.
    """
    text_dict = page.get_text("dict")
    y_ticks = []
    x_years = []

    for block in text_dict["blocks"]:
        if block["type"] != 0:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                raw_text = span["text"]
                text = raw_text.strip()

                if not text:
                    continue

                # =========================
                # 1️⃣ YEAR EXTRACTION (SAFE)
                # =========================
                year_match = YEAR_PATTERN.fullmatch(text)

                if year_match:
                    year = int(year_match.group(0))

                    # Optional safety window
                    if 1990 <= year <= 2035:
                        x_years.append({
                            "year": year,
                            "x": span["bbox"][0],
                            "y": span["bbox"][1]
                        })
                    continue

                # =========================
                # 2️⃣ NUMERIC Y-TICKS (SAFE)
                # =========================
                if is_numeric(text):
                    try:
                        value = float(text.replace(",", ""))
                        y_ticks.append({
                            "value": value,
                            "x": span["bbox"][0],
                            "y": span["bbox"][1]
                        })
                    except ValueError:
                        # Skip invalid numeric formats silently
                        continue

    return y_ticks, x_years

# def extract_axis_labels(page):
#     """
#     Extract numeric Y-axis ticks and X-axis year labels.
#     """
#     text_dict = page.get_text("dict")
#     y_ticks = []
#     x_years = []

#     for block in text_dict["blocks"]:
#         if block["type"] != 0:
#             continue

#         for line in block["lines"]:
#             for span in line["spans"]:
#                 text = span["text"].strip()

#                 if YEAR_PATTERN.match(text):
#                     x_years.append({
#                         "year": int(text),
#                         "x": span["bbox"][0],
#                         "y": span["bbox"][1]
#                     })

#                 elif is_numeric(text):
#                     y_ticks.append({
#                         "value": float(text.replace(",", "")),
#                         "x": span["bbox"][0],
#                         "y": span["bbox"][1]
#                     })

#     return y_ticks, x_years


def detect_bars(page):
    """
    Detect rectangles that likely represent bars.
    """
    bars = []
    drawings = page.get_drawings()

    for drawing in drawings:
        for item in drawing["items"]:
            if item[0] == "re":
                rect = item[1]
                width = abs(rect.x1 - rect.x0)
                height = abs(rect.y1 - rect.y0)

                # Ignore thin lines
                if width < 5 or height < 10:
                    continue

                bars.append({
                    "x_center": (rect.x0 + rect.x1) / 2,
                    "y_top": min(rect.y0, rect.y1),
                    "y_bottom": max(rect.y0, rect.y1),
                    "height": height
                })

    return bars


def infer_scale(y_ticks):
    """
    Infer pixel-to-value scale from Y-axis tick labels.
    """
    if len(y_ticks) < 2:
        return None

    # Sort by vertical position
    y_ticks_sorted = sorted(y_ticks, key=lambda t: t["y"])

    top = y_ticks_sorted[0]
    bottom = y_ticks_sorted[-1]

    pixel_range = abs(bottom["y"] - top["y"])
    value_range = abs(bottom["value"] - top["value"])

    if pixel_range == 0:
        return None

    scale = value_range / pixel_range
    return scale, bottom["value"], bottom["y"]


def extract_charts(pdf_path, document_id):

    doc = fitz.open(pdf_path)
    metrics = []

    for page_number, page in enumerate(doc, start=1):

        y_ticks, x_years = extract_axis_labels(page)
        bars = detect_bars(page)

        if not bars or not y_ticks:
            continue

        scale_data = infer_scale(y_ticks)

        if not scale_data:
            continue

        scale, base_value, base_pixel = scale_data

        # Sort bars by X position (left to right)
        bars_sorted = sorted(bars, key=lambda b: b["x_center"])

        for index, bar in enumerate(bars_sorted):

            # Map bar height to value
            value = base_value - (bar["y_bottom"] - base_pixel) * scale

            year = None
            if index < len(x_years):
                year = x_years[index]["year"]

            metrics.append({
                "document_id": document_id,
                "metric_key": "chart_metric",
                "value": round(value, 2),
                "unit": "inferred",
                "year": year,
                "source_type": "chart_vector",
                "page_number": page_number,
                "confidence_score": 0.85,
                "raw_text": "vector_bar_extracted"
            })

    return metrics
