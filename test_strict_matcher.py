import re
import json
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

from rapidfuzz import fuzz

def smart_search(query: str):
    q = query.lower()
    
    # 1. În instalații canalizare, PVC se referă aproape mereu la PP (polipropilenă) sau PVC
    # Dacă utilizatorul zice "pvc", e valabil și pentru "pp"
    is_pvc_pp = bool(re.search(r'\b(pvc|pp)\b', q))
    
    # 2. Extragem toate cotele/numerele tehnice (dimensiuni, diametre, unghiuri, fracții)
    # Ex: 40, 50, 110, 32, 16, 20, 25, 32, 40, 45, 67, 87, 90, 1/2, 3/4, 3/8, 1/4, 1*, 2* etc.
    # Fracții:
    q = re.sub(r'\b(unu|un|o)\s+p\s+2\b', '1/2', q)
    q = re.sub(r'\btrei\s+p\s+4\b', '3/4', q)
    q = re.sub(r'\b40[\s\-]*45\b', '40 45', q)
    q = re.sub(r'\b50[\s\-]*45\b', '50 45', q)
    q = re.sub(r'\b110[\s\-]*45\b', '110 45', q)
    q = re.sub(r'\b40[\s\-]*87\b', '40 87', q)
    q = re.sub(r'\b50[\s\-]*87\b', '50 87', q)
    q = re.sub(r'\b110[\s\-]*87\b', '110 87', q)
    
    # Găsim toate numerele/fracțiile tehnice din query
    tech_numbers = re.findall(r'(?:\d+\/\d+|\d+\*|\b\d+\b)', q)
    # Excludem cuvinte gen cantități izolate la final dacă sunt evidente
    # Dar dimensiunile 40, 45, 50, 87, 16, 110, 1/2 sunt numere tehnice
    
    # Cuvinte de bază (non-numere)
    words = re.findall(r'[a-zA-Zăîșțâ]{3,}', q)
    # Eliminăm cuvinte de umplutură
    stop_words = {'din', 'de', 'la', 'cu', 'pentru', 'grade', 'grad', 'gr', 'si', 'pe'}
    key_words = [w.upper() for w in words if w not in stop_words and w not in ('pvc', 'pp')]
    
    print(f"\n--- CĂUTARE: '{query}' ---")
    print(f"Numere tehnice obligatorii: {tech_numbers}")
    print(f"Cuvinte cheie: {key_words}")
    
    candidates = []
    for item in NOMENCLATOR:
        den = item["denumire"].upper()
        
        # Regula 1: Dacă query are numere tehnice (ex: 40 și 45), produsul TREBUIE să le conțină!
        # Căutăm numerele în denumire cu delimitatori (nu doar substring aleatoriu)
        missing_numbers = 0
        for num in tech_numbers:
            # căutăm numărul ca token sau cu cratime/slash
            # ex: "40" în "40-40-45" sau " 40 " sau " 40MM"
            pat = r'(?:^|[^\d])' + re.escape(num) + r'(?:[^\d]|$)'
            if not re.search(pat, den):
                missing_numbers += 1
        
        # Dacă lipsesc numere tehnice specificate clar (cum ar fi 40 sau 45), penalizare severă!
        if missing_numbers > 0:
            continue  # Excludem complet produsele care nu au dimensiunile cerute!
            
        # Regula 2: Verificăm cuvintele cheie (ex: RAMIFICATIE)
        matched_kw = sum(1 for kw in key_words if kw in den)
        if key_words and matched_kw == 0:
            continue
            
        # Scor de bază
        score = fuzz.token_set_ratio(query.upper(), den)
        
        # Bonus dacă are toate cuvintele cheie
        if key_words and matched_kw == len(key_words):
            score += 20
            
        # Dacă e PVC/PP și produsul are PP sau PVC
        if is_pvc_pp and ('PP' in den or 'PVC' in den):
            score += 15
            
        candidates.append((score, item))
        
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    if not candidates:
        print("Niciun candidat cu filtre stricte, se încearcă căutare relaxată...")
        # fallback
        for item in NOMENCLATOR:
            den = item["denumire"].upper()
            if any(kw in den for kw in key_words):
                candidates.append((fuzz.token_set_ratio(query.upper(), den), item))
        candidates.sort(key=lambda x: x[0], reverse=True)

    print(f"Top 3 rezultate:")
    seen = set()
    count = 0
    for sc, it in candidates:
        if it["denumire"] not in seen:
            seen.add(it["denumire"])
            print(f"  [{sc:.1f}] {it['denumire']} | Cod: {it['cod_extern']}")
            count += 1
            if count >= 3:
                break

smart_search("ramificatii din pvc de 40-45 grade")
smart_search("ramificatii pvc de 50-45 grade")
smart_search("teava purmo pexpenta de 16 120 metri")
smart_search("niplu de 1/2 de la kalde")
smart_search("sifon masina de spalat aparent")
