# salin_master_produk.py
import sqlite3
import csv
import os

def bina_dan_isi_master_produk(fail_csv):
    if not os.path.exists(fail_csv):
        print(f"❌ Error: {fail_csv} file not found!")
        return

    conn = sqlite3.connect("warehouse_data.db")
    cursor = conn.cursor()
    
    # Create the reference matrix map table
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
        with open(fail_csv, mode='r', encoding='utf-8-sig') as f:
            pembaca = csv.reader(f)
            next(pembaca)  # Skip the CSV header row
            
            kira = 0
            for row in pembaca:
                if len(row) >= 3:
                    # Strips whitespace while saving data columns cleanly
                    cursor.execute(query, (row[0].strip().upper(), row[1].strip().upper(), row[2].strip().upper()))
                    kira += 1
            conn.commit()
            print(f"🟩 SUCCESS: {kira} product data records linked into database master matrix!")
    except Exception as e:
        conn.rollback()
        print(f"❌ Database execution failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    bina_dan_isi_master_produk("master_produk.csv")
