import fitz
import re
import logging

logger = logging.getLogger(__name__)

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
NUMERIC_PATTERN = re.compile(r"^\d+(\.\d+)?$")


def is_numeric(text):
    return bool(NUMERIC_PATTERN.match(text.strip()))


# -------------------------------------------------
# Extract chart title / context (upper-middle zone)
# -------------------------------------------------
def extract_chart_context(page):
    blocks = page.get_text("blocks")
    page_height = page.rect.height
    context = []

    for block in blocks:
        y_top = block[1]
        text = block[4]

        if page_height * 0.1 < y_top < page_height * 0.35:
            context.append(text)

    return " ".join(context)


# -------------------------------------------------
# Extract Y-axis ticks and X-axis years
# -------------------------------------------------
def extract_axis_labels(page):
    """
    Extract clean Y-axis ticks and X-axis years.
    Removes header/footer contamination.
    """

    text_dict = page.get_text("dict")
    y_ticks = []
    x_years = []

    page_height = page.rect.height
    page_width = page.rect.width

    for block in text_dict["blocks"]:
        if block["type"] != 0:
            continue

        for line in block["lines"]:
            for span in line["spans"]:

                text = span["text"].strip()
                if not text:
                    continue

                x0 = span["bbox"][0]
                y0 = span["bbox"][1]

                # ----------------------------
                # 1️⃣ STRICT YEAR DETECTION
                # ----------------------------
                year_match = YEAR_PATTERN.fullmatch(text)
                if year_match:
                    year = int(year_match.group())
                    if 1990 <= year <= 2035:
                        x_years.append({
                            "year": year,
                            "x": x0,
                            "y": y0
                        })
                    continue

                # ----------------------------
                # 2️⃣ STRICT Y-AXIS TICK FILTER
                # ----------------------------
                if is_numeric(text):

                    # Must be LEFT EDGE (true axis region)
                    if x0 > page_width * 0.10:
                        continue

                    # Must be in middle vertical region (not header/footer)
                    if not (page_height * 0.15 < y0 < page_height * 0.85):
                        continue

                    try:
                        value = float(text.replace(",", ""))
                        y_ticks.append({
                            "value": value,
                            "x": x0,
                            "y": y0
                        })
                    except ValueError:
                        continue
        # Keep only ticks close to leftmost X
        if y_ticks:
            min_x = min(t["x"] for t in y_ticks)
            y_ticks = [t for t in y_ticks if abs(t["x"] - min_x) < 15]


    return y_ticks, x_years

# -------------------------------------------------
# Match bar to nearest year label
# -------------------------------------------------
def match_year(bar_x, x_years):
    if not x_years:
        return None

    closest = min(
        x_years,
        key=lambda y: abs(y["x"] - bar_x)
    )
    return closest["year"]


# -------------------------------------------------
# Detect bars from vector rectangles
# -------------------------------------------------
def detect_bars(page):
    bars = []

    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] != "re":
                continue

            rect = item[1]
            width = abs(rect.x1 - rect.x0)
            height = abs(rect.y1 - rect.y0)

            # Filter tiny shapes
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


# -------------------------------------------------
# Infer pixel-to-value scale
# -------------------------------------------------
def infer_scale(y_ticks, page_height):
    """
    Industrial-grade scale detection.
    Keeps only true vertical axis ticks.
    """

    if len(y_ticks) < 4:
        return None

    # 1️⃣ Keep only left-most ticks (true Y-axis)
    left_axis = sorted(y_ticks, key=lambda t: t["x"])[:8]

    # 2️⃣ Remove header/footer noise by Y clustering
    # Keep ticks that are vertically grouped
    left_axis = sorted(left_axis, key=lambda t: t["y"])

    values = [t["value"] for t in left_axis]

    # 3️⃣ Compute differences
    diffs = [
        round(values[i+1] - values[i], 2)
        for i in range(len(values)-1)
    ]

    if not diffs:
        return None

    # 4️⃣ Detect dominant step
    step = max(set(diffs), key=diffs.count)

    # 5️⃣ Keep only consistent-step ticks
    cleaned = [left_axis[0]]

    for i in range(1, len(left_axis)):
        if round(values[i] - values[i-1], 2) == step:
            cleaned.append(left_axis[i])

    if len(cleaned) < 3:
        return None

    top_tick = cleaned[0]
    bottom_tick = cleaned[-1]

    pixel_range = bottom_tick["y"] - top_tick["y"]
    if pixel_range == 0:
        return None

    value_range = bottom_tick["value"] - top_tick["value"]

    scale = value_range / pixel_range

    return scale, top_tick["value"], top_tick["y"]

# -------------------------------------------------
# MAIN EXTRACTION FUNCTION
# -------------------------------------------------
def extract_charts(pdf_path, document_id):

    doc = fitz.open(pdf_path)
    metrics = []

    for page_number, page in enumerate(doc, start=1):

        page_text = extract_chart_context(page)

        y_ticks, x_years = extract_axis_labels(page)
        bars = detect_bars(page)

        # Skip non-chart pages
        if len(y_ticks) < 5 or len(bars) < 1:
            continue

        logger.warning(f"\n--- PAGE {page_number} ---")
        logger.warning(f"Y TICKS: {y_ticks}")
        logger.warning(f"X YEARS: {x_years}")
        logger.warning(f"BARS: {bars}")

        scale_data = infer_scale(y_ticks, page.rect.height)
        if not scale_data:
            continue

        scale, top_tick_value, top_tick_pixel = scale_data

        # Sort bars left to right
        bars_sorted = sorted(bars, key=lambda b: b["x_center"])

        # Remove near-duplicate bars
        unique_bars = []
        for bar in bars_sorted:
            if not unique_bars:
                unique_bars.append(bar)
                continue

            if abs(bar["x_center"] - unique_bars[-1]["x_center"]) > 3:
                unique_bars.append(bar)

        for bar in unique_bars:

            pixel_delta = bar["y_top"] - top_tick_pixel
            value = top_tick_value + (pixel_delta * scale)

            # Sanity filtering
            if value < 0:
                continue
            if value > 100000:
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
