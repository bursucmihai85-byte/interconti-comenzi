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
QTY_REGEX = r'(\b\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?)\b)'

def parse_multi_item_dictation(text: str) -> list[str]:
    t = text.strip()
    t = re.sub(r'\b(cam\s+at[aâ]t|at[aâ]t|gata|mul[tț]umesc)\b.*$', '', t, flags=re.IGNORECASE).strip()
    
    # 1. Separare inițială pe virgule și conjuncții clare ("și", "apoi", "plus")
    t = re.sub(r'\s*,\s*', '\n', t)
    t = re.sub(r'\s+\b(și|si|apoi|plus)\b\s+', '\n', t, flags=re.IGNORECASE)
    
    initial_segments = [s.strip() for s in t.split('\n') if s.strip()]
    
    # 2. Pentru fiecare segment, separăm dacă există cantitate urmată de un nou produs
    # E.g. "țeavă pardoseală 16 120 m niplu kalde 3 bucăți" -> se taie după 120 m
    stage2_segments = []
    for s in initial_segments:
        # Căutăm [CuvinteProdus ... cantitate] urmat de un nou produs
        sub_s = re.sub(
            r'(' + PROD_REGEX + r'.*?\s+' + QTY_REGEX + r')\s+(?=(?:\d+\s*(?:buc|m|ml|set|rol|cut)?\s+)?' + PROD_REGEX + ')',
            r'\1\n',
            s,
            flags=re.IGNORECASE
        )
        for part in sub_s.split('\n'):
            if part.strip():
                stage2_segments.append(part.strip())

    # 3. În fiecare segment, dacă au mai rămas mai multe cuvinte de produse fără cantitate între ele
    final_items = []
    for s in stage2_segments:
        matches = list(re.finditer(PROD_REGEX, s, flags=re.IGNORECASE))
        if len(matches) <= 1:
            final_items.append(s)
        else:
            split_indices = []
            for i in range(1, len(matches)):
                idx = matches[i].start()
                prefix = s[:idx]
                qty_match = re.search(r'(\b\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?)?\s*)$', prefix)
                if qty_match:
                    idx -= len(qty_match.group(1))
                split_indices.append(idx)
            
            last = 0
            for idx in split_indices:
                sub = s[last:idx].strip()
                if sub:
                    final_items.append(sub)
                last = idx
            sub = s[last:].strip()
            if sub:
                final_items.append(sub)
                
    return [r for r in final_items if len(r) > 1]

t1 = "Ramificații pvc de 50-45 ° țeavă de pardoseală pe experienta de 16 120 m niplu de unu p 2 de la cal de 3 bucăți șefu în mașina de spălat aparent 2 bucăți cam atât"
print("Test 1:")
for idx, it in enumerate(parse_multi_item_dictation(t1), 1):
    print(f"  {idx}. {it}")

t2 = "3 bucăți niplu de unu p 2 de la kalde și 10 metri țeavă purmo de 16 plus 2 sifoane mașină de spălat"
print("\nTest 2:")
for idx, it in enumerate(parse_multi_item_dictation(t2), 1):
    print(f"  {idx}. {it}")
