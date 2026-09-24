import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import re

PRODUCT_KEYWORDS = [
    r'ramifica[tț]ie', r'ramifica[tț]ii',
    r'[tț]eav[aă]', r'[tț]evi',
    r'niplu', r'nipluri',
    r'cot', r'coturi',
    r'teu', r'teuri',
    r'muf[aă]', r'mufe',
    r'robinet', r'robine[tț]i',
    r'sifon', r'[sș]ifoane', r'[sș]efu(\s*[\-]?\s*[iî]n)?',
    r'aerisitor', r'aerisitoare',
    r'filtru', r'filtre',
    r'colier', r'coliere',
    r'reduc[tț]ie', r'reduc[tț]ii',
    r'dop', r'dopuri',
    r'capac', r'capace',
    r'calorifer', r'calorifere',
    r'radiator', r'radiatoare',
    r'pomp[aă]', r'pompe',
    r'racord', r'racorduri',
    r'supap[aă]', r'supape',
    r'distribuitor', r'distribuitoare'
]

SPLIT_PATTERN = r'\b(?:' + '|'.join(PRODUCT_KEYWORDS) + r')\b'

def split_items(text: str) -> list[str]:
    t = re.sub(r'\b(cam\s+at[aâ]t|at[aâ]t|gata)\b.*$', '', text, flags=re.IGNORECASE).strip()
    
    t_mod = re.sub(r'\s*,\s*', ' | ', t)
    t_mod = re.sub(r'\s+\b(și|si|apoi|plus)\b\s+', ' | ', t_mod, flags=re.IGNORECASE)
    
    qty_before_kw = r'(\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?))\s+(' + SPLIT_PATTERN + ')'
    t_mod = re.sub(qty_before_kw, r'\1 | \2', t_mod, flags=re.IGNORECASE)
    
    parts = [p.strip() for p in t_mod.split('|') if p.strip()]
    
    if len(parts) <= 1:
        matches = list(re.finditer(SPLIT_PATTERN, t, flags=re.IGNORECASE))
        if len(matches) > 1:
            parts = []
            for i in range(len(matches)):
                start = matches[i].start()
                prefix = t[:start]
                qty_m = re.search(r'(\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?)?\s*)$', prefix, flags=re.IGNORECASE)
                if qty_m and qty_m.group(0).strip():
                    start = start - len(qty_m.group(0))
                
                end = matches[i+1].start() if i + 1 < len(matches) else len(t)
                if i + 1 < len(matches):
                    next_start = matches[i+1].start()
                    next_prefix = t[:next_start]
                    next_qty = re.search(r'(\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?)?\s*)$', next_prefix, flags=re.IGNORECASE)
                    if next_qty and next_qty.group(0).strip():
                        end = next_start - len(next_qty.group(0))
                
                chunk = t[start:end].strip()
                if chunk:
                    parts.append(chunk)

    return parts

phrase1 = "Ramificații pvc de 50-45 ° țeavă de pardoseală pe experienta de 16 120 m niplu de unu p 2 de la cal de 3 bucăți șefu în mașina de spălat aparent 2 bucăți cam atât"
print("Rezultat tăiere frază 1:")
for p in split_items(phrase1):
    print(" ->", p)

phrase2 = "10 m teava purmo si un robinet purmo"
print("\nRezultat tăiere frază 2:")
for p in split_items(phrase2):
    print(" ->", p)
