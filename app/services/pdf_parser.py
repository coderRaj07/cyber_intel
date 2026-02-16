import fitz
import pdfplumber

def parse_pdf(file_path: str):
    """
    Returns structured blocks:
    [
        {
            "page": int,
            "type": "text" | "table" | "chart",
            "content": str
        }
    ]
    """

    blocks = []

    # -------- TEXT + VECTOR --------
    doc = fitz.open(file_path)

    for page_num, page in enumerate(doc, start=1):

        # TEXT BLOCKS
        text = page.get_text("text")
        if text.strip():
            blocks.append({
                "page": page_num,
                "type": "text",
                "content": text
            })

        # VECTOR DRAWINGS (charts)
        drawings = page.get_drawings()
        if drawings:
            svg = page.get_svg_image()
            blocks.append({
                "page": page_num,
                "type": "chart",
                "content": svg
            })

    # -------- TABLES --------
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()

            for table in tables:
                structured_table = "\n".join(
                    [" | ".join(cell if cell else "" for cell in row)
                     for row in table if row]
                )

                blocks.append({
                    "page": page_num,
                    "type": "table",
                    "content": structured_table
                })

    return blocks