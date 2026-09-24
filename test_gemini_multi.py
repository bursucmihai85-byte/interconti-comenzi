import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
from google import genai
from google.genai import types

key = open(r"C:\Users\Lucru\Desktop\interconti\.env").read().split("=")[1].strip()
client = genai.Client(api_key=key)

with open(r"C:\Users\Lucru\Desktop\interconti\nomenclator.json", "r", encoding="utf-8") as f:
    NOMENCLATOR = json.load(f)

prompt = """Ești un asistent inteligent pentru un depozit de instalații sanitare (Interconti).
Utilizatorul dictează pe telefon produse dorite (poate fi un singur produs sau mai multe produse într-o singură frază).
În limbajul vorbit de șantier/depozit:
- 'pvc' gri de interior înseamnă de fapt fitinguri de scurgere interioară din 'PP' (polipropilenă) sau PVC.
- 'pex-penta' / 'pex penta' / 'purmo' = țeavă încălzire în pardoseală Purmo PexPenta.
- 'kalde' = fitinguri / robineți PPR Kalde.
- 'jumătate' = 1/2, 'trei sferturi' = 3/4, 'un țol' = 1*.

Fraza dictată:
"vreau și eu 10 ramificații din pvc de 40 la 45 de grade și 2 colaci de țeavă purmo pexpenta de 16 la 240 m și 5 nipluri de jumătate"

Identifică fiecare produs individual menționat, cantitatea și unitatea de măsură, și extrage cuvintele cheie de căutare tehnice.
Răspunde STRICT JSON sub formă de listă:
[
  {
    "termen_cautare": "RAMIFICATIE PP 40 45",
    "cantitate": 10,
    "um": "buc",
    "detalii": "ramificație 40 la 45 grade"
  }
]
"""

resp = client.models.generate_content(
    model='gemini-3.5-flash-lite',
    contents=prompt,
    config=types.GenerateContentConfig(response_mime_type='application/json')
)
print(resp.text)
