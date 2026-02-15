import fitz
import re
import math

# YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

NUMERIC_PATTERN = re.compile(r"^\d+(\.\d+)?$")


def is_numeric(text):
    return bool(NUMERIC_PATTERN.match(text.strip()))

def extract_chart_context(page):
    blocks = page.get_text("blocks")
    page_height = page.rect.height
    context = []

    for block in blocks:
        y_top = block[1]
        text = block[4]

        # Only upper-middle region
        if page_height * 0.1 < y_top < page_height * 0.35:
            context.append(text)

    return " ".join(context)


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
def match_year(bar_x, x_years):
    if not x_years:
        return None

    closest = min(
        x_years,
        key=lambda y: abs(y["x"] - bar_x)
    )
    return closest["year"]


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
                page_height = page.rect.height

                if width < page.rect.width * 0.01:
                    continue

                if height < page.rect.height * 0.05:
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
    Robust scale inference using lowest and highest tick values.
    Handles inverted axes safely.
    """
    if len(y_ticks) < 2:
        return None

    # Sort by pixel Y (top = small y, bottom = large y)
    y_sorted = sorted(y_ticks, key=lambda t: t["y"])

    top_tick = y_sorted[0]
    bottom_tick = y_sorted[-1]

    pixel_range = bottom_tick["y"] - top_tick["y"]

    if pixel_range == 0:
        return None

    value_range = bottom_tick["value"] - top_tick["value"]

    scale = value_range / pixel_range

    return scale, top_tick["value"], top_tick["y"]



def extract_charts(pdf_path, document_id):

    doc = fitz.open(pdf_path)
    metrics = []

    for page_number, page in enumerate(doc, start=1):
        page_text = extract_chart_context(page)

        y_ticks, x_years = extract_axis_labels(page)
        bars = detect_bars(page)

        if not bars or not y_ticks:
            continue

        scale_data = infer_scale(y_ticks)

        if not scale_data:
            continue

        scale, top_tick_value, top_tick_pixel = scale_data

        bars_sorted = sorted(bars, key=lambda b: b["x_center"])

        for index, bar in enumerate(bars_sorted):

            # Distance from top tick to bar top
            pixel_delta = bar["y_top"] - top_tick_pixel

            value = top_tick_value + (pixel_delta * scale)

            
            year = match_year(bar["x_center"], x_years)

            # ---- Sanity Filtering ----
            if value < 0:
                continue

            if value < 1 and scale > 1:
                continue


            metrics.append({
                "document_id": document_id,
                "metric_key": None,  # 🔥 let classifier decide
                "value": round(value, 2),
                "unit": "inferred",
                "year": year,
                "source_type": "chart_vector",
                "page_number": page_number,
                "confidence_score": 0.75,  # slightly lower before classification
                "raw_text": page_text  # 🔥 pass full chart context
            })

    doc.close()
    return metrics