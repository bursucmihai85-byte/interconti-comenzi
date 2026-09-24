import os
import sqlite3
import openpyxl
import time

excel_path = r"C:\Users\Lucru\Desktop\interconti\Nomenclator-Interconti-2026.09.23.xlsx"
db_path = r"C:\Users\Lucru\Desktop\interconti\nomenclator.db"

print("Începem încărcarea nomenclatorului din Excel...")
t0 = time.time()

wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
sheet = wb.active

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS produse")
cur.execute("DROP TABLE IF EXISTS produse_fts")

cur.execute("""
CREATE TABLE produse (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    denumire TEXT,
    cod TEXT,
    cod_extern TEXT
)
""")

cur.execute("""
CREATE VIRTUAL TABLE produse_fts USING fts5(
    denumire,
    cod,
    cod_extern,
    content='produse',
    content_rowid='id'
)
""")

rows_to_insert = []
header = True
count = 0

for row in sheet.iter_rows(values_only=True):
    if header:
        header = False
        continue
    denumire = str(row[0]).strip() if row[0] is not None else ""
    cod = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ""
    cod_extern = str(row[2]).strip() if len(row) > 2 and row[2] is not None else ""
    
    if denumire:
        rows_to_insert.append((denumire, cod, cod_extern))
        count += 1

cur.executemany("INSERT INTO produse (denumire, cod, cod_extern) VALUES (?, ?, ?)", rows_to_insert)
cur.execute("INSERT INTO produse_fts(produse_fts) VALUES('rebuild')")

conn.commit()
conn.close()
wb.close()

print(f"Gata! {count} produse au fost indexate cu succes în {time.time() - t0:.2f} secunde.")
