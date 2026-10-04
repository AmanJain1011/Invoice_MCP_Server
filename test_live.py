import json
import sys

from extractor import extract_invoice_data

sys.stdout.reconfigure(encoding="utf-8")
result = extract_invoice_data(sys.argv[1])
print(json.dumps(result, indent=2, ensure_ascii=False))
