import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from readers import read_document
from schema import Invoice

load_dotenv()
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


SYSTEM_PROMPT = """You are an invoice data extraction engine.
The invoice may be written in ANY language (English, Hindi, Hinglish, etc.).
Return ONLY a JSON object with exactly these keys:
invoice_number, invoice_date (YYYY-MM-DD), vendor_name, customer_name, currency (ISO code like INR),
line_items (list of {description, quantity, unit_price, amount}), subtotal, tax_amount, total_amount,
language (name of the main language of the invoice, in English).
Rules: keep names and item descriptions in their ORIGINAL language/script;
numbers must be plain numbers without commas or currency symbols;
if a field is missing use null. Never invent values."""


def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found. Add it to your .env file.")
    return Groq(api_key=api_key)


def parse_json(raw):
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE)
    return json.loads(raw.strip())


def call_llm(text):
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return parse_json(response.choices[0].message.content)


def check_totals(invoice):
    items_sum = round(sum(i.amount or 0 for i in invoice.line_items), 2)
    base = invoice.subtotal if invoice.subtotal is not None else items_sum
    expected = round(base + (invoice.tax_amount or 0), 2)
    matches = invoice.total_amount is not None and abs(expected - invoice.total_amount) < 0.01
    return {"items_sum": items_sum, "expected_total": expected, "total_matches": matches}


def extract_invoice_data(file_path, llm=call_llm):
    text = read_document(file_path)
    if not text:
        raise ValueError("No text found in the file (scanned PDFs need OCR - future scope).")
    data = llm(text)
    data["line_items"] = data.get("line_items") or []
    invoice = Invoice(**data)
    result = invoice.model_dump()
    result["checks"] = check_totals(invoice)
    result["source_file"] = Path(file_path).name
    return result
