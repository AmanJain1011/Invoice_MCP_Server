from pathlib import Path

from mcp.server.fastmcp import FastMCP

from extractor import extract_invoice_data
from readers import READERS

mcp = FastMCP("invoice-extractor")


@mcp.tool()
def extract_invoice(file_path: str) -> dict:
    """Extract structured data (invoice number, date, vendor, items, totals)
    from one invoice file. Supports PDF, TXT, CSV and XLSX in any language."""
    return extract_invoice_data(file_path)


@mcp.tool()
def extract_folder(folder_path: str) -> list:
    """Extract all supported invoice files inside a folder."""
    results = []
    for file in sorted(Path(folder_path).iterdir()):
        if file.suffix.lower() in READERS:
            try:
                results.append(extract_invoice_data(str(file)))
            except Exception as error:
                results.append({"source_file": file.name, "error": str(error)})
    return results


if __name__ == "__main__":
    mcp.run()
