#!/usr/bin/env python3
"""Scarica il PDF listino Unoenergy \"Luce Sicuro\" più recente e aggiorna listino.json."""
import re, json, datetime, requests, pdfplumber, pathlib, tempfile

PDF_URL = "https://www.unoenergy.it/wp-content/uploads/luce-sicuro-listino.pdf"  # adatta se cambia
LISTINO_PATH = pathlib.Path("listino.json")

# Scarica PDF
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
open(tmp.name, "wb").write(requests.get(PDF_URL, timeout=20).content)

# Estrai numeri con pdfplumber
text = "\n".join(page.extract_text() for page in pdfplumber.open(tmp.name).pages)
price_mono = float(re.search(r"Monoraria.*?(\d+[\.,]\d+)", text).group(1).replace(',', '.'))
price_f1 = float(re.search(r"F1.*?(\d+[\.,]\d+)", text).group(1).replace(',', '.'))
price_f23 = float(re.search(r"F23.*?(\d+[\.,]\d+)", text).group(1).replace(',', '.'))
quota = float(re.search(r"Quota[\s\w]*annua.*?(\d+[\.,]\d+)", text).group(1).replace(',', '.'))

data = {
    "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "offers": [
        {
            "id": "sicuro_mono",
            "name": "Luce Sicuro Monoraria",
            "type": "mono",
            "price_kwh": price_mono,
            "quota_annua": quota
        },
        {
            "id": "sicuro_bi",
            "name": "Luce Sicuro Bioraria",
            "type": "bi",
            "price_kwh_F1": price_f1,
            "price_kwh_F23": price_f23,
            "quota_annua": quota,
            "mix": {"F1": 0.40, "F23": 0.60}
        }
    ]
}

# Scrivi se diverso
if LISTINO_PATH.exists():
    if json.loads(LISTINO_PATH.read_text()) == data:
        print("Listino invariato, nessun update.")
        exit(0)
LISTINO_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print("Listino aggiornato!")
