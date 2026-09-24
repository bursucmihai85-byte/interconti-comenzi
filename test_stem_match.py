import re
import json

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

from rapidfuzz import fuzz

def normalize_plurals(word: str) -> str:
    w = word.upper()
    # Română: plural -> singular pentru termeni de instalații
    repl = [
        (r'RAMIFICA[TȚ]II$', 'RAMIFICATIE'),
        (r'[TȚ]EVI$', 'TEAVA'),
        (r'NIPLURI$', 'NIPLU'),
        (r'COTURI$', 'COT'),
        (r'TEURI$', 'TEU'),
        (r'MUFE$', 'MUFA'),
        (r'ROBINE[TȚ]I$', 'ROBINET'),
        (r'[SȘ]IFOANE$', 'SIFON'),
        (r'AERISITOARE$', 'AERISITOR'),
        (r'FILTRE$', 'FILTRU'),
        (r'COLIERE$', 'COLIER'),
        (r'REDUC[TȚ]II$', 'REDUCTIE'),
        (r'DOPURI$', 'DOP'),
        (r'CAPACE$', 'CAPAC'),
        (r'CALORIFERE$', 'CALORIFER'),
        (r'RADIATOARE$', 'RADIATOR'),
        (r'POMPE$', 'POMPA'),
        (r'RACORDURI$', 'RACORD'),
        (r'SUPAPE$', 'SUPAPA'),
        (r'OLANDEZI$', 'OLANDEZ'),
        (r'GARNITURI$', 'GARNITURA')
    ]
    for p, r in repl:
        w = re.sub(p, r, w)
    return w

def test_match(q):
    print(f"\nQUERY: '{q}'")
    # normalizare numere tehnice
    q_clean = q.lower()
    q_clean = re.sub(r'\b(\d+)[\s\-]+(\d+)\b', r'\1 \2', q_clean)
    
    # extragere numere
    nums = re.findall(r'(?:\d+\/\d+|\d+\*|\b\d+\b)', q_clean)
    # extragere cuvinte
    raw_words = re.findall(r'[a-zA-Zăîșțâ]{3,}', q_clean)
    stop = {'din', 'de', 'la', 'cu', 'pentru', 'grade', 'grad', 'gr', 'si', 'pe'}
    key_words = [normalize_plurals(w) for w in raw_words if w not in stop and w not in ('pvc', 'pp')]
    
    print("Numere:", nums, "| Cuvinte cheie:", key_words)
    
    candidates = []
    for item in NOMENCLATOR:
        den = item["denumire"].upper()
        
        # 1. Numere tehnice obligatorii
        missing_num = False
        for n in nums:
            # ex: "40" trebuie să apară ca număr delimitat în denumire
            pat = r'(?:^|[^\d])' + re.escape(n) + r'(?:[^\d]|$)'
            if not re.search(pat, den):
                missing_num = True
                break
        if missing_num:
            continue
            
        # 2. Cuvinte cheie
        has_kw = False
        matched_kw_count = 0
        for kw in key_words:
            # verificăm dacă rădăcina cuvântului (primele 4-5 litere) apare în denumire
            root = kw[:min(len(kw), 5)]
            if root in den:
                matched_kw_count += 1
                has_kw = True
        
        if key_words and not has_kw:
            continue
            
        score = fuzz.token_set_ratio(q.upper(), den)
        if matched_kw_count == len(key_words):
            score += 25
            
        candidates.append((score, item))
        
    candidates.sort(key=lambda x: x[0], reverse=True)
    seen = set()
    for sc, it in candidates[:4]:
        if it["denumire"] not in seen:
            seen.add(it["denumire"])
            print(f"  -> [{sc:.1f}] {it['denumire']} | Cod: {it['cod_extern']}")

test_match("ramificatii din pvc de 40-45 grade")
test_match("ramificatii pvc de 50-45 grade")
test_match("ramificatii 110-50-45")
test_match("cot alama 1 tol kalde")
