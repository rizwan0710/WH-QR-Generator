# salin_master_produk.py
import sqlite3
import os
from tkinter import messagebox

# Sila pastikan anda telah memasang modul openpyxl (pip install openpyxl)
try:
    import openpyxl
except ImportError:
    print("❌ Modul 'openpyxl' tidak ditemui! Sila pasang dahulu dengan menaip: pip install openpyxl")

def bina_dan_isi_master_produk_xlsx(nama_fail_excel):
    if not os.path.exists(nama_fail_excel):
        print(f"❌ Ralat: Fail [{nama_fail_excel}] tidak ditemui dalam folder projek!")
        return

    conn = sqlite3.connect("warehouse_data.db")
    cursor = conn.cursor()
    
    # 1. Bina jadual rujukan baharu jika belum wujud
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            drawing_no TEXT,
            part_number TEXT
        )
    """)
    
    query = "INSERT INTO master_produk (customer_name, drawing_no, part_number) VALUES (?, ?, ?)"
    
    try:
        # 2. Buka fail Excel LIST CUSTOMER.xlsx
        wb = openpyxl.load_workbook(nama_fail_excel, data_only=True)
        sheet = wb.active # Mengambil tab sheet pertama yang aktif
        
        kira = 0
        # Membaca baris bermula dari baris ke-2 (melangkah baris pengepala/header)
        for row in sheet.iter_rows(min_row=2, max_col=3, values_only=True):
            # Memastikan baris mempunyai data dan lajur tidak kosong
            if row[0] and row[1] and row[2]:
                cust_val = str(row[0]).strip().upper()
                draw_val = str(row[1]).strip().upper()
                part_val = str(row[2]).strip().upper()
                
                cursor.execute(query, (cust_val, draw_val, part_val))
                kira += 1
                
        conn.commit()
        print(f"🟩 BERJAYA: Sebanyak {kira} rekod data produk dari [{nama_fail_excel}] berjaya diimport!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Ralat semasa pemprosesan Excel: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Jalankan fungsi menggunakan nama fail tepat anda
    bina_dan_isi_master_produk_xlsx("LIST CUSTOMER.xlsx")
