import re
import json

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

from rapidfuzz import fuzz

def test_score(query, cand_name):
    q = query.lower()
    den = cand_name.upper()
    
    # Numere din query
    q_nums = set(re.findall(r'(?:\d+\/\d+|\d+\*|\b\d+\b)', q))
    # Numere din denumire
    den_nums = set(re.findall(r'(?:\d+\/\d+|\d+\*|\b\d+\b)', den))
    
    score = fuzz.token_set_ratio(q.upper(), den)
    
    # Penalizare severă pentru numere mari suplimentare din produs necerute de utilizator (ex: 110, 160)
    extra_nums = den_nums - q_nums
    for n in extra_nums:
        if n in {'110', '160', '200', '125', '75', '32'}:
            score -= 35
            
    # Penalizare pentru atribute speciale necerute
    for attr in ['DUBLA', 'REGLABILA', 'REGL', 'FONO', 'REDUCTIE']:
        if attr in den and attr not in q.upper():
            score -= 25
            
    # Bonus dacă are toate numerele cerute
    if q_nums.issubset(den_nums):
        score += 20
        
    return score

candidates = [
    'ARMAKAN RAMIFICATIE PP 110-50-45',
    'ARMAKAN RAMIFICATIE PP 50-32-45',
    'ARMAKAN RAMIFICATIE PP 50-50-45',
    'RAMIFICATIE PVC DUBLA REGL110-50/45/88 GR CN15',
    'ROZMA RAMIFICATIE PP 50-50-45',
    'VALROM RAMIFICATIE FONO 110-50-45'
]

q = "ramificatii pvc de 50-45 grade"
print(f"Scoruri pentru: '{q}'")
for c in candidates:
    print(f" -> {test_score(q, c):.1f} : {c}")
