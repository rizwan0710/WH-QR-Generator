# invoice_customer_detector.py - FULL FIXED INVOICE NAME AUTOMATIC TRANSLATOR
import sqlite3

def dapatkan_customer_dari_outer(seq_outer):
    """
    FUNGSI DIPERKUKUH TOTAL (IDEA USER): Mengesan nama customer berdasarkan Outer Box.
    🌟 DIBAIKI: Menggunakan logik "A4 == B4" -> Jika Kod diimbas sama dengan customer_code,
    sistem terus memulangkan customer_name (Nama Penuh dari Excel) ke skrin UI.
    """
    if not seq_outer or seq_outer == "--- PILIH DATA ---":
        return ""
        
    conn = None
    try:
        conn = sqlite3.connect("warehouse_data.db")
        cursor = conn.cursor()
        
        # 1. Cari siri linked inner box dari rekod Outer Box (B...)
        cursor.execute("SELECT machine FROM rekod_qr WHERE sequence_no = ?", (seq_outer.strip(),))
        res = cursor.fetchone()
        
        if res and res[0]:
            text_raw = str(res[0]).strip()
            
            # Buang sebarang karakter sisa pembungkus string jika ada
            for char in ["[", "]", "'", '"', "(", ")"]:
                text_raw = text_raw.replace(char, "")
                
            # Pecahkan string berasaskan tanda koma
            linked_inners = text_raw.split(",")
            
            if linked_inners and len(linked_inners) > 0:
                # Ambil kotak Inner pertama (Contoh: WP2609240001)
                inner_pertama = linked_inners[0].strip()
                
                # 2. Cari siapakah nama Customer asal (Kod Ringkas, cth: CEPHEID) bagi Inner Box tersebut
                cursor.execute("SELECT customer FROM rekod_qr WHERE sequence_no = ?", (inner_pertama,))
                res_cust = cursor.fetchone()
                
                if res_cust and res_cust[0] and str(res_cust[0]).strip() != "None" and str(res_cust[0]).strip() != "":
                    kod_imbas = str(res_cust[0]).strip().upper()
                    
                    # 3. 🌟 IDEA ANDA: JIKA KOD SAMA, AMBIL NAMA PENUH KORPORAT LANGSUNG 🌟
                    query_idea_user = """
                        SELECT DISTINCT customer_name 
                        FROM master_produk 
                        WHERE TRIM(UPPER(customer_code)) = ? 
                           OR TRIM(UPPER(customer_name)) = ?
                        LIMIT 1
                    """
                    cursor.execute(query_idea_user, (kod_imbas, kod_imbas))
                    row_master = cursor.fetchone()
                    
                    if row_master and row_master[0]:
                        # Sistem memulangkan NAMA PENUH KORPORAT daripada Kolum B Excel!
                        return str(row_master[0]).strip().upper()
                        
                    # Fallback fleksibel sekiranya ada ruang kosong tersembunyi
                    cursor.execute("SELECT DISTINCT customer_name FROM master_produk WHERE customer_code LIKE ?", (f"%{kod_imbas}%",))
                    row_like = cursor.fetchone()
                    if row_like and row_like[0]:
                        return str(row_like[0]).strip().upper()
                    
                    # Pulangkan kod asal jika maklumat tiada langsung di dalam database master Excel
                    return kod_imbas
                    
        return "INTERNAL/COMBINED"
    except Exception as e:
        print(f"Customer detection system error: {str(e)}")
        return "INTERNAL/COMBINED"
    finally:
        if conn:
            conn.close()
