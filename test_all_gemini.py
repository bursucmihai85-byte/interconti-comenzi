import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import re
from google import genai
from google.genai import types
from rapidfuzz import fuzz

ENV_PATH = r"C:\Users\Lucru\Desktop\interconti\.env"
API_KEY = ""
if os.path.exists(ENV_PATH):
    for line in open(ENV_PATH, "r", encoding="utf-8"):
        if line.startswith("GEMINI_API_KEY="):
            API_KEY = line.split("=", 1)[1].strip()

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

client = genai.Client(api_key=API_KEY) if API_KEY else None

def search_candidate_in_nomenclator(clean_query: str, original_seg: str = ""):
    clean_query_spaced = re.sub(r'\b(\d+)[\s\-]+(\d+)\b', r'\1 \2', clean_query)
    tech_numbers = set(re.findall(r'(?:\d+\/\d+|\d+\*|\b\d+\b)', clean_query_spaced))
    
    words = re.findall(r'[a-zA-Zăîșțâ]{3,}', clean_query)
    stop_words = {'din', 'de', 'la', 'cu', 'pentru', 'grade', 'grad', 'gr', 'si', 'pe'}
    key_words = [w.upper() for w in words if w.lower() not in stop_words and w.lower() not in ('pvc', 'pp')]
    
    candidates = []
    
    for item in NOMENCLATOR:
        den = item["denumire"].upper()
        den_nums = set(re.findall(r'(?:\d+\/\d+|\d+\*|\b\d+\b)', den))
        
        # Filtru strict pentru numere tehnice cerute
        missing_num = False
        for n in tech_numbers:
            pat = r'(?:^|[^\d])' + re.escape(n) + r'(?:[^\d]|$)'
            if not re.search(pat, den):
                missing_num = True
                break
        if missing_num and len(tech_numbers) > 0:
            continue
            
        matched_kw = 0
        for kw in key_words:
            root = kw[:min(len(kw), 5)]
            if root in den:
                matched_kw += 1
        
        if key_words and matched_kw == 0:
            continue
            
        score = fuzz.token_set_ratio(clean_query.upper(), den)
        
        if key_words and matched_kw == len(key_words):
            score += 25
            
        extra_nums = den_nums - tech_numbers
        for n in extra_nums:
            if n in {'110', '160', '200', '125', '75', '32'}:
                score -= 40

        for attr in ['DUBLA', 'REGLABILA', 'REGL', 'FONO', 'REDUCTIE']:
            if attr in den and attr not in clean_query.upper():
                score -= 30
            
        candidates.append({
            "denumire": item["denumire"],
            "cod": item["cod"],
            "cod_extern": item["cod_extern"],
            "score": score
        })

    # Fallback dacă nu a găsit cu filtre stricte
    if not candidates:
        for item in NOMENCLATOR:
            den = item["denumire"].upper()
            matched = sum(1 for kw in key_words if kw[:min(len(kw), 5)] in den)
            if matched > 0:
                score = fuzz.token_set_ratio(clean_query.upper(), den)
                if score >= 55:
                    candidates.append({
                        "denumire": item["denumire"],
                        "cod": item["cod"],
                        "cod_extern": item["cod_extern"],
                        "score": score
                    })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    seen = set()
    unique = []
    for c in candidates:
        if c["denumire"] not in seen:
            seen.add(c["denumire"])
            unique.append(c)
        if len(unique) >= 4:
            break

    if not unique:
        return None, []

    best = unique[0]
    second_score = unique[1]["score"] if len(unique) > 1 else 0
    is_ambiguous = False
    if len(unique) > 1:
        if (best["score"] - second_score < 10) or (best["score"] < 75):
            is_ambiguous = True

    return best, unique, is_ambiguous

def parse_with_gemini(text: str):
    if not client:
        return None
    prompt = f"""Ești asistentul tehnic expert pentru un depozit de instalații sanitare (Interconti).
Clientul sau instalatorul a dictat prin voce următoarea cerință (poate fi un singur produs sau o listă lungă cu mai multe produse):
"{text}"

Context tehnic de depozit sanitar:
- "PVC" de interior (gri, de scurgere) se referă în nomenclatorul de depozit la piese de scurgere "PP" (polipropilenă) sau PVC.
- Respectă cu strictețe diametrele (ex: 40, 50, 110) și unghiurile (ex: 45, 67, 87, 90). Nu adăuga 'dublă' sau 'reglabilă' dacă nu a fost cerut.
- "pex-penta" / "purmo" = TEAVA PEX-PENTA PURMO.
- "kalde" = KALDE (fitinguri alamă sau PPR).
- "jumătate" = 1/2, "trei sferturi" = 3/4, "un tol" = 1*.
- Recunoaște cantitățile (ex: 10 bucăți, 2 colaci, 120 metri) și unitatea de măsură (buc, m, colac, set, cutie). Dacă nu se precizează, cantitatea e 1 buc.

Pentru fiecare produs dictat, extrage:
- "termen_nomenclator": expresia de căutare optimă pentru denumirea din catalog (ex: "RAMIFICATIE PP 40 45", "TEAVA PEX-PENTA PURMO 16", "KALDE NIPLU 1/2")
- "cantitate": număr întreg sau zecimal
- "um": unitatea de măsură ("buc", "m", "colac", "set", etc.)

Răspunde STRICT sub formă de listă JSON validă:
[
  {{
    "termen_nomenclator": "RAMIFICATIE PP 40 45",
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
        return json.loads(resp.text)
    except Exception as e:
        print("Eroare Gemini:", e)
        return None

test_cases = [
    "ramificații din pvc de 40-45 grade",
    "țeavă purmo pexpenta 16 120 metri",
    "niplu 1/2 kalde 3 bucăți",
    "5 sifoane de pardoseala cu gratar inox",
    "vreau 10 ramificatii pvc 40 cu 45 si 5 nipluri de jumatate kalde si 2 colaci purmo pexpenta 16"
]

print("=== TESTARE GEMINI + CATALOG INTERCONTI ===")
for tc in test_cases:
    print(f"\n--- DICTAT: '{tc}' ---")
    parsed = parse_with_gemini(tc)
    if parsed:
        for p in parsed:
            q = p.get("termen_nomenclator", "")
            qty = p.get("cantitate", 1)
            um = p.get("um", "buc")
            best, unique, is_ambig = search_candidate_in_nomenclator(q, tc)
            if best:
                warn = " [ ! ] VERIFICA" if is_ambig else ""
                print(f" -> {best['denumire']} | Cant: {qty} {um} | Cod: {best['cod_extern']}{warn}")
            else:
                print(f" -> NEGĂSIT pentru '{q}'")
    else:
        print(" -> Eroare la parsarea cu Gemini")
