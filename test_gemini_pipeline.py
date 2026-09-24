import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import time
from google import genai
from google.genai import types
from rapidfuzz import fuzz

key = open(r"C:\Users\Lucru\Desktop\interconti\.env").read().split("=")[1].strip()
client = genai.Client(api_key=key)

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

def gemini_smart_parse(dictated_text: str):
    t0 = time.time()
    
    # 1. Ask Gemini to interpret the dictation (split into items, normalize plumbing terminology)
    prompt = f"""Ești creierul unui depozit de instalații sanitare (Interconti).
Clientul dictează: "{dictated_text}"

Reguli de domeniu instalații sanitare:
- "PVC" de interior (gri, subțire, scurgere) se referă în catalog la piese de scurgere din "PP" (polipropilenă) sau PVC.
- Păstrează strict dimensiunile (ex: 40, 50, 110) și unghiurile (ex: 45, 67, 87, 90).
- "pex-penta" / "purmo" = țeavă încălzire pardoseală PexPenta Purmo.
- "kalde" = PPR Kalde.
- "jumătate" = 1/2, "trei sferturi" = 3/4, "un tol" = 1*.

Extrage fiecare reper dorit sub formă de listă JSON:
[
  {{
    "query_cautare": "RAMIFICATIE PP 40 45",
    "cantitate": 1,
    "um": "buc"
  }}
]
"""
    try:
        resp = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        parsed_items = json.loads(resp.text)
    except Exception as e:
        print("Gemini error:", e)
        return None

    results = []
    for item in parsed_items:
        q = item.get("query_cautare", "")
        qty = item.get("cantitate", 1)
        um = item.get("um", "buc")
        
        # Căutăm top candidați în nomenclator pentru termenul de căutare
        scored = []
        for it in NOMENCLATOR:
            den = it["denumire"].upper()
            score = fuzz.token_set_ratio(q.upper(), den)
            # Bonus pentru potrivire exactă numere
            nums = set(q.replace("-", " ").split())
            if all(n in den for n in ["40", "45"] if n in q):
                score += 15
            if "110" in den and "110" not in q:
                score -= 30
            if "DUBLA" in den and "DUBLA" not in q.upper():
                score -= 30
            scored.append((score, it))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:5]
        
        best = top[0][1]
        results.append({
            "cod_extern": best["cod_extern"],
            "denumire": best["denumire"],
            "cantitate": qty,
            "um": um,
            "score": top[0][0]
        })
        
    t1 = time.time()
    print(f"Execuție în {t1-t0:.2f} secunde.")
    return results

if __name__ == "__main__":
    test1 = "ramificații din pvc de 40-45 grade"
    print("Test 1:", test1)
    res1 = gemini_smart_parse(test1)
    print(json.dumps(res1, indent=2, ensure_ascii=False))

    test2 = "vreau 10 ramificatii pvc 40 cu 45 si 5 nipluri de jumatate kalde si 2 colaci purmo pexpenta 16"
    print("\nTest 2:", test2)
    res2 = gemini_smart_parse(test2)
    print(json.dumps(res2, indent=2, ensure_ascii=False))
