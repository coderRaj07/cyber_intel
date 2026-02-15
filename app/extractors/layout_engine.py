import fitz

def build_ast(pdf_path):

    doc = fitz.open(pdf_path)
    ast = []

    for page_number, page in enumerate(doc, start=1):

        blocks = page.get_text("dict")["blocks"]
        elements = []

        for block in blocks:

            if block["type"] == 0:
                text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        text += span["text"] + " "

                text = text.strip()

                if text:
                    elements.append({
                        "type": "paragraph",
                        "text": text
                    })

        ast.append({
            "page": page_number,
            "elements": elements
        })

    return ast
