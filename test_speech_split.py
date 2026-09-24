import re

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
    r'oalande[sz]', r'olandezi',
    r'ventil', r'garnitur[aă]', r'garnituri'
]

PROD_REGEX = r'(?:\b(?:' + '|'.join(PRODUCT_TYPES) + r')\b)'
QTY_REGEX = r'(\b\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?)\b)'

def split_dictated_speech(text: str) -> list[str]:
    t = text.strip()
    t = re.sub(r'\b(cam\s+at[aâ]t|at[aâ]t|gata|mul[tț]umesc)\b.*$', '', t, flags=re.IGNORECASE).strip()
    
    # 1. Dacă există conjuncții explicite sau virgule: "și", "apoi", "plus", ","
    t = re.sub(r'\s*,\s*', ' ||| ', t)
    t = re.sub(r'\s+\b(și|si|apoi|plus)\b\s+', ' ||| ', t, flags=re.IGNORECASE)
    
    # 2. Căutăm tiparul: [Produs ... cantitate] urmat de [următorul produs sau număr]
    # ex: "120 m niplu" -> "120 m ||| niplu"
    # Dar NU la începutul unui segment!
    def separate_qty_transition(m):
        # m.group(1) e textul anterior, m.group(2) e cantitatea, m.group(3) e următorul produs
        return f"{m.group(1)} {m.group(2)} ||| {m.group(3)}"
    
    t = re.sub(r'(\S+)\s+' + QTY_REGEX + r'\s+(?=(\d+\s*)?' + PROD_REGEX + ')', r'\1 \2 ||| ', t, flags=re.IGNORECASE)
    
    chunks = [c.strip() for c in t.split('|||') if c.strip()]
    
    # 3. În fiecare bucată, dacă conține mai multe produse distincte
    final_items = []
    for c in chunks:
        # Căutăm cuvintele de produs
        matches = list(re.finditer(PROD_REGEX, c, flags=re.IGNORECASE))
        if len(matches) > 1:
            split_points = []
            for i, m in enumerate(matches):
                if i > 0:
                    start_idx = m.start()
                    prefix = c[:start_idx]
                    # verificăm dacă prefixul se termină cu un număr/cantitate (ex: "5 " sau "5 bucăți ")
                    num_m = re.search(r'(\b\d+\s*(?:buc(?:ati|ăți)?|m(?:etri)?|ml|set(?:uri)?|rol(?:e|a)?|cut(?:ii|ie)?)?\s*)$', prefix, flags=re.IGNORECASE)
                    if num_m:
                        start_idx -= len(num_m.group(1))
                    split_points.append(start_idx)
            
            last_idx = 0
            for sp in split_points:
                part = c[last_idx:sp].strip()
                if part:
                    final_items.append(part)
                last_idx = sp
            part = c[last_idx:].strip()
            if part:
                final_items.append(part)
        else:
            final_items.append(c)

    return [it for it in final_items if len(it) > 2]

# Teste
t1 = "Ramificații pvc de 50-45 ° țeavă de pardoseală pe experienta de 16 120 m niplu de unu p 2 de la cal de 3 bucăți șefu în mașina de spălat aparent 2 bucăți cam atât"
print("Test 1:")
for idx, it in enumerate(split_dictated_speech(t1), 1):
    print(f"  {idx}. {it}")

t2 = "3 bucăți niplu de unu p 2 de la kalde și 10 metri țeavă purmo de 16 plus 2 sifoane mașină de spălat"
print("\nTest 2:")
for idx, it in enumerate(split_dictated_speech(t2), 1):
    print(f"  {idx}. {it}")
