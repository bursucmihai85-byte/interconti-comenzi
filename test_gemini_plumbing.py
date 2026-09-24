import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import json
from google import genai
from google.genai import types

key = open(r"C:\Users\Lucru\Desktop\interconti\.env").read().split("=")[1].strip()
client = genai.Client(api_key=key)

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

# Testăm cum interpretează Gemini fraza utilizatorului
dictated = "ramificații din pvc de 40-45 grade"

# Găsim 15 candidați potențiali din nomenclator cu fuzzy simplu
from rapidfuzz import fuzz
scored = []
for it in NOMENCLATOR:
    score = fuzz.token_set_ratio(dictated.upper(), it["denumire"].upper())
    if score >= 40:
        scored.append((score, it))
scored.sort(key=lambda x: x[0], reverse=True)
top_candidates = [it for sc, it in scored[:15]]

candidates_str = "\n".join([f"- Cod: {c['cod_extern']} | Denumire: {c['denumire']}" for c in top_candidates])

prompt = f"""
Ești un expert în depozitul de instalații sanitare Interconti.
Utilizatorul a dictat următoarea cerință:
"{dictated}"

Iată candidații găsiți în nomenclator:
{candidates_str}

Cerințe:
1. În instalații sanitare, piesele gri de interior numite colocvial "PVC" sunt din "PP" (polipropilenă).
2. Dimensiunile și unghiurile sunt prioritare!
3. Selectează EXACT cel mai bun reper din lista de mai sus.
4. Răspunde strict în format JSON:
{{
  "cod_extern": "...",
  "denumire": "...",
  "cantitate": 1,
  "um": "buc",
  "motivatie": "..."
}}
"""

resp = client.models.generate_content(
    model='gemini-3.5-flash-lite',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)

print("RĂSPUNS GEMINI:")
print(resp.text)
