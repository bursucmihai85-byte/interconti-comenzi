import json
import re
from rapidfuzz import fuzz

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

def search_debug(query, tokens_all=None, tokens_any=None):
    print(f"\n=================== CĂUTARE: '{query}' ===================")
    results = []
    tokens = query.upper().split()
    for item in NOMENCLATOR:
        den = item["denumire"].upper()
        # Verificare filtru
        if tokens_all:
            if not all(tok.upper() in den for tok in tokens_all):
                continue
        score = fuzz.token_set_ratio(query.upper(), den)
        results.append((score, item))
    
    results.sort(key=lambda x: x[0], reverse=True)
    seen = set()
    count = 0
    for score, item in results:
        if item["denumire"] not in seen:
            seen.add(item["denumire"])
            print(f"[{score:.1f}] {item['denumire']} | Cod: {item['cod_extern']}")
            count += 1
            if count >= 6:
                break

print("Test 1: Ramificatie PVC 50-45")
search_debug("RAMIFICATIE 50 45", tokens_all=["50", "45"])

print("\nTest 2: Teava pardoseala 16 (PEX / PERT)")
search_debug("TEAVA PARDOSEALA 16", tokens_all=["16"])

print("\nTest 3: Niplu 1/2 Kalde")
search_debug("KALDE NIPLU 1/2", tokens_all=["KALDE", "NIPLU", "1/2"])

print("\nTest 4: Sifon masina spalat aparent")
search_debug("SIFON MASINA SPALAT APARENT", tokens_all=["SIFON", "MASINA"])
