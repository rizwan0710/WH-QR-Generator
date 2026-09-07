import sqlite3
import re

def kemaskini_description_usang_database():
    """🌟 ONE-TIME MIGRATION SCRIPT: Tukar kesemua log lama menjadi [Sequence] Qty: X -> Y 🌟"""
    print("Memulakan proses pembersihan data log lama OHTA Precision...")
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=15) as conn:
            cursor = conn.cursor()
            
            # Ambil kesemua data dari jadual log_aktiviti
            cursor.execute("SELECT id, jenis_tab, description FROM log_aktiviti")
            semua_log = cursor.fetchall()
            
            bil_berjaya = 0
            
            for log_id, jenis_tab, desc_asal in semua_log:
                desc_asal_str = str(desc_asal)
                
                # ─── 🔍 ENJIN EKSTRAK POLA TEXT (REGULAR EXPRESSIONS) ───
                # Pola 1: Ekstrak siri kod bar (WP%, B%, INV%)
                siri_kod = re.search(r'(WP\d+|B\d+|INV\d+)', desc_asal_str)
                # Pola 2: Ekstrak rantaian nombor perubahan kuantiti (Contoh: '60 ➔ 65' atau '400 -> 350')
                angka_qty = re.findall(r'(\d+)\s*(?:➔|->)\s*(\d+)', desc_asal_str)
                
                if siri_kod and angka_qty:
                    kode_sequence = siri_kod.group(1)
                    qty_lama, qty_baru = angka_qty[0]
                    
                    # Bina rentetan teks format baharu bertaraf Standardized English
                    desc_baru_clean = f"[{kode_sequence}] Qty: {qty_lama} -> {qty_baru}"
                    
                    # Kemaskini secara fizikal ke dalam SQLite
                    cursor.execute("UPDATE log_aktiviti SET description = ? WHERE id = ?", (desc_baru_clean, log_id))
                    bil_berjaya += 1
                
                # Fallback jika log lama adalah kes pengeditan banyak medan (Multiple fields)
                elif siri_kod and "MULTIPLE" in desc_asal_str.upper():
                    kode_sequence = siri_kod.group(1)
                    desc_baru_clean = f"[{kode_sequence}] Multiple fields edited"
                    cursor.execute("UPDATE log_aktiviti SET description = ? WHERE id = ?", (desc_baru_clean, log_id))
                    bil_berjaya += 1
            
            conn.commit()
            print(f"🔥 BERJAYA: Sebanyak {bil_berjaya} rekod log lama telah dibersihkan secara mutlak! 🔥")
            
    except sqlite3.Error as e:
        print(f"Ralat semasa proses pembersihan SQLite: {str(e)}")

if __name__ == "__main__":
    kemaskini_description_usang_database()
