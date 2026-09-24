import json

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

def search_kw(*kws):
    print(f"\n--- Cautare cuvinte: {kws} ---")
    for item in NOMENCLATOR:
        den = item["denumire"].upper()
        if all(k.upper() in den for k in kws):
            print(f"  {item['denumire']} | Cod: {item['cod_extern']}")

search_kw("RAMIFICATIE", "50", "45")
search_kw("PARDOSEALA", "16")
search_kw("SIFON", "SPALAT")
