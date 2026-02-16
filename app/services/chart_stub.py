import re
from app.services.extractor import extract_metrics
from app.services.tokenizer import count_tokens, MAX_TOKENS


def extract_text_from_svg(svg_content: str):
    """
    Extract only visible text nodes from SVG.
    Ignore vector path data.
    """

    # Extract text between <text> tags
    texts = re.findall(r">([^<>]+)<", svg_content)

    # Keep only strings that contain digits
    numeric_texts = [t.strip() for t in texts if re.search(r"\d", t)]

    return "\n".join(numeric_texts)


def process_chart_block(block, report_name):

    svg_content = block["content"]
    page = block["page"]

    structured_text = extract_text_from_svg(svg_content)

    # Token-safe check
    if count_tokens(structured_text) > MAX_TOKENS:
        # If still too large, skip chart (avoid crash)
        return []

    return extract_metrics(structured_text, page, report_name)