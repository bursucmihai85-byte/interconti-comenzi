import re
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PRODUCT_TYPES = [
    r'ramifica[tț]i[ie]', r'ramifica[tț]ii',
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
    r'clapet', r'clapete',
    r'distribuitor', r'distribuitoare',
    r'olandez', r'olandezi',
    r'ventil', r'garnitur[aă]', r'garnituri'
]

PROD_REGEX = r'(?:\b(?:' + '|'.join(PRODUCT_TYPES) + r')\b)'
QTY_REGEX = r'(\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?))'

def split_dictated_speech(text: str) -> list[str]:
    t = text.strip()
    t = re.sub(r'\b(cam\s+at[aâ]t|at[aâ]t|gata|mul[tț]umesc)\b.*$', '', t, flags=re.IGNORECASE).strip()
    
    # Înlocuim virgule și conjuncții de legătură
    t = re.sub(r'\s*,\s*', ' ||| ', t)
    t = re.sub(r'\s+\b(și|si|apoi|plus)\b\s+', ' ||| ', t, flags=re.IGNORECASE)
    
    # Caz 1: [Produs A ... Cantitate A] urmat de [Produs B sau Cantitate B ...]
    # E.g. "120 m niplu" -> split după 120 m
    # E.g. "3 bucăți sifon" -> split după 3 bucăți
    # Regula: un număr + unitate, dacă înaintea lui a fost un cuvânt de produs, iar după el vine un alt produs sau o cantitate
    pattern_split_after_qty = r'(' + PROD_REGEX + r'.*?' + QTY_REGEX + r')\s+(?=(?:\d+\s*(?:buc|m|ml|set|rol|cut)?\s+)?' + PROD_REGEX + r')'
    t = re.sub(pattern_split_after_qty, r'\1 ||| ', t, flags=re.IGNORECASE)

    parts = [p.strip() for p in t.split('|||') if p.strip()]
    
    # Caz 2: Dacă într-o bucată au rămas 2 produse (fără cantitate între ele, ex: "ramificație 50 45 țeavă pardoseală 16")
    final_items = []
    for p in parts:
        matches = list(re.finditer(PROD_REGEX, p, flags=re.IGNORECASE))
        if len(matches) > 1:
            # tăiem la fiecare început de produs
            for i in range(len(matches)):
                start = matches[i].start()
                # verificăm dacă înaintea cuvântului de produs există o cantitate (ex: "3 bucăți ")
                prefix = p[:start]
                m_num = re.search(r'(\b\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?)?\s*)$', prefix)
                if m_num:
                    start -= len(m_num.group(1))
                
                if i + 1 < len(matches):
                    next_start = matches[i+1].start()
                    next_prefix = p[:next_start]
                    next_num = re.search(r'(\b\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?)?\s*)$', next_prefix)
                    if next_num:
                        end = next_start - len(next_num.group(1))
                    else:
                        end = next_start
                else:
                    end = len(p)
                
                chunk = p[start:end].strip()
                if chunk and chunk not in final_items:
                    final_items.append(chunk)
        else:
            final_items.append(p)

    return final_items

t1 = "Ramificații pvc de 50-45 ° țeavă de pardoseală pe experienta de 16 120 m niplu de unu p 2 de la cal de 3 bucăți șefu în mașina de spălat aparent 2 bucăți cam atât"
print("Test 1 (Fraza ta lungă):")
for idx, it in enumerate(split_dictated_speech(t1), 1):
    print(f"  {idx}. {it}")

t2 = "3 bucăți niplu de unu p 2 de la kalde și 10 metri țeavă purmo de 16 plus 2 sifoane mașină de spălat"
print("\nTest 2 (Cu 'și' și 'plus'):")
for idx, it in enumerate(split_dictated_speech(t2), 1):
    print(f"  {idx}. {it}")
