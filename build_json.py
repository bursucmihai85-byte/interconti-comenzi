import json
import time
import openpyxl

excel_path = r"C:\Users\Lucru\Desktop\interconti\Nomenclator-Interconti-2026.09.23.xlsx"
json_path = r"C:\Users\Lucru\Desktop\interconti\nomenclator.json"

print("Încărcare nomenclator din Excel...")
t0 = time.time()

wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
sheet = wb.active

items = []
header = True

for row in sheet.iter_rows(values_only=True):
    if header:
        header = False
        continue
    denumire = str(row[0]).strip() if row[0] is not None else ""
    cod = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ""
    cod_extern = str(row[2]).strip() if len(row) > 2 and row[2] is not None else ""
    
    if denumire:
        items.append({
            "denumire": denumire,
            "cod": cod,
            "cod_extern": cod_extern
        })

wb.close()

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=None)

print(f"Salvat cu succes {len(items)} repere în {json_path} în {time.time() - t0:.2f} secunde.")
