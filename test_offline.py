from pathlib import Path

from extractor import extract_invoice_data
from readers import read_document


def fake_llm(text):
    return {"invoice_number": "TEST-1", "line_items": [{"description": "Item", "amount": 100}],
            "subtotal": 100, "tax_amount": 18, "total_amount": 118}


for file in sorted(Path("samples").iterdir()):
    text = read_document(str(file))
    print(file.name, "-> characters read:", len(text))
    result = extract_invoice_data(str(file), llm=fake_llm)
    print("   total_matches:", result["checks"]["total_matches"])
