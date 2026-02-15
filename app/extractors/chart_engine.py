import fitz
import re
import logging

logger = logging.getLogger(__name__)

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
NUMERIC_PATTERN = re.compile(r"^\d+(\.\d+)?$")


def is_numeric(text):
    return bool(NUMERIC_PATTERN.match(text.strip()))


# ---------------------------------------------------
# CHART TITLE / CONTEXT
# ---------------------------------------------------

def extract_chart_context(page):
    blocks = page.get_text("blocks")
    page_height = page.rect.height
    context = []

    for block in blocks:
        y_top = block[1]
        text = block[4]

        # Middle-upper region only (avoid headers & footers)
        if page_height * 0.15 < y_top < page_height * 0.40:
            context.append(text)

    return " ".join(context)


# ---------------------------------------------------
# AXIS EXTRACTION
# ---------------------------------------------------

def extract_axis_labels(page):

    text_dict = page.get_text("dict")
    y_ticks = []
    x_years = []

    for block in text_dict["blocks"]:
        if block["type"] != 0:
            continue

        for line in block["lines"]:
            for span in line["spans"]:

                text = span["text"].strip()
                if not text:
                    continue

                # -------- YEAR EXTRACTION --------
                if YEAR_PATTERN.fullmatch(text):
                    year = int(text)
                    if 1990 <= year <= 2035:
                        x_years.append({
                            "year": year,
                            "x": span["bbox"][0],
                            "y": span["bbox"][1]
                        })
                    continue

                # -------- Y TICK EXTRACTION --------
                if is_numeric(text):

                        # Only left margin
                        if span["bbox"][0] > page.rect.width * 0.15:
                            continue

                        value = float(text.replace(",", ""))

                        # 🚨 Remove page numbers (usually top of page)
                        if span["bbox"][1] < page.rect.height * 0.08:
                            continue

                        # 🚨 Remove extreme large values (like 58, 59 page numbers)
                        if value > 1000:
                            continue

                        y_ticks.append({
                            "value": value,
                            "x": span["bbox"][0],
                            "y": span["bbox"][1]
                        })


    # 🔥 SORT & FILTER MONOTONIC TICKS
    y_ticks = sorted(y_ticks, key=lambda t: t["y"])

    filtered_ticks = []
    for tick in y_ticks:
        if not filtered_ticks:
            filtered_ticks.append(tick)
            continue

        # Only keep realistic incremental ticks
        if abs(tick["value"] - filtered_ticks[-1]["value"]) <= 50:
            filtered_ticks.append(tick)

    return filtered_ticks, x_years


# ---------------------------------------------------
# BAR DETECTION
# ---------------------------------------------------

def detect_bars(page):

    bars = []
    drawings = page.get_drawings()
    page_height = page.rect.height
    page_width = page.rect.width

    for drawing in drawings:
        for item in drawing["items"]:

            if item[0] != "re":
                continue

            rect = item[1]
            width = abs(rect.x1 - rect.x0)
            height = abs(rect.y1 - rect.y0)

            # 🔥 Ignore tiny shapes
            if width < page_width * 0.01:
                continue

            if height < page_height * 0.05:
                continue

            # 🔥 Ignore full-page background rectangles
            if height > page_height * 0.8:
                continue

            bars.append({
                "x_center": (rect.x0 + rect.x1) / 2,
                "y_top": min(rect.y0, rect.y1),
                "y_bottom": max(rect.y0, rect.y1),
                "height": height
            })

    return bars


# ---------------------------------------------------
# SCALE INFERENCE
# ---------------------------------------------------

def infer_scale(y_ticks):
    """
    Production-grade axis detection:
    - Remove page numbers
    - Keep only proper monotonic sequence
    - Require minimum 4 ticks
    """

    if len(y_ticks) < 4:
        return None

    # 1️⃣ Remove duplicates
    unique = {}
    for tick in y_ticks:
        val = tick["value"]
        if val not in unique or tick["y"] > unique[val]["y"]:
            unique[val] = tick

    ticks = list(unique.values())

    # 2️⃣ Sort by pixel position (top → bottom)
    ticks.sort(key=lambda t: t["y"])

    # 3️⃣ Extract numeric sequence
    values = [t["value"] for t in ticks]

    # 4️⃣ Detect dominant step size
    diffs = []
    for i in range(1, len(values)):
        diffs.append(abs(values[i] - values[i - 1]))

    if not diffs:
        return None

    # Most common difference
    step = max(set(diffs), key=diffs.count)

    # 5️⃣ Keep only values matching that step
    filtered = [ticks[0]]

    for i in range(1, len(ticks)):
        if abs(ticks[i]["value"] - filtered[-1]["value"]) == step:
            filtered.append(ticks[i])

    if len(filtered) < 4:
        return None

    top_tick = filtered[0]
    bottom_tick = filtered[-1]

    pixel_range = bottom_tick["y"] - top_tick["y"]
    value_range = bottom_tick["value"] - top_tick["value"]

    if pixel_range == 0:
        return None

    scale = value_range / pixel_range

    return scale, top_tick["value"], top_tick["y"]

# ---------------------------------------------------
# MATCH YEAR TO BAR
# ---------------------------------------------------

def match_year(bar_x, x_years):
    if not x_years:
        return None

    closest = min(
        x_years,
        key=lambda y: abs(y["x"] - bar_x)
    )
    return closest["year"]


# ---------------------------------------------------
# MAIN CHART EXTRACTION
# ---------------------------------------------------

def extract_charts(pdf_path, document_id):

    doc = fitz.open(pdf_path)
    metrics = []

    for page_number, page in enumerate(doc, start=1):

        page_text = extract_chart_context(page)

        y_ticks, x_years = extract_axis_labels(page)
        bars = detect_bars(page)

        if not bars or not y_ticks:
            continue

        logger.warning(f"\n--- PAGE {page_number} ---")
        logger.warning(f"Y TICKS: {y_ticks}")
        logger.warning(f"X YEARS: {x_years}")
        logger.warning(f"BARS: {bars}")

        scale_data = infer_scale(y_ticks)
        if not scale_data:
            continue

        scale, top_tick_value, top_tick_pixel = scale_data

        # 🔥 SORT & REMOVE DUPLICATE BARS
        bars_sorted = sorted(bars, key=lambda b: b["x_center"])

        unique_bars = []
        for bar in bars_sorted:
            if not unique_bars:
                unique_bars.append(bar)
                continue

            if abs(bar["x_center"] - unique_bars[-1]["x_center"]) > 3:
                unique_bars.append(bar)

        bars_sorted = unique_bars

        for bar in bars_sorted:

            pixel_delta = bar["y_top"] - top_tick_pixel
            value = top_tick_value + (pixel_delta * scale)

            # 🔥 Sanity Filtering
            if value < 0:
                continue

            if abs(value) > 1_000_000_000:
                continue

            year = match_year(bar["x_center"], x_years)


            metrics.append({
                "document_id": document_id,
                "metric_key": None,
                "value": round(value, 2),
                "unit": "inferred",
                "year": year,
                "source_type": "chart_vector",
                "page_number": page_number,
                "confidence_score": 0.75,
                "raw_text": page_text
            })

    doc.close()
    return metrics
