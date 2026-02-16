from app.services.tokenizer import count_tokens, MAX_TOKENS
from app.services.extractor import extract_metrics
from app.services.chart_stub import process_chart_block


def recursive_process(block, report_name):
    """
    Token-aware recursive splitting
    """

    content = block["content"]
    page = block["page"]
    block_type = block["type"]

    # Chart handled separately
    if block_type == "chart":
        return process_chart_block(block, report_name)

    tokens = count_tokens(content)

    if tokens <= MAX_TOKENS:
        return extract_metrics(content, page, report_name)

    # Try paragraph split
    paragraphs = content.split("\n\n")

    if len(paragraphs) > 1:
        results = []
        for p in paragraphs:
            if p.strip():
                sub_block = {
                    "page": page,
                    "type": block_type,
                    "content": p
                }
                results.extend(recursive_process(sub_block, report_name))
        return results

    # Fallback: hard split
    mid = len(content) // 2

    first = {
        "page": page,
        "type": block_type,
        "content": content[:mid]
    }

    second = {
        "page": page,
        "type": block_type,
        "content": content[mid:]
    }

    return recursive_process(first, report_name) + \
           recursive_process(second, report_name)


def recursive_parse_blocks(blocks, report_name):
    results = []
    for block in blocks:
        results.extend(recursive_process(block, report_name))
    return results