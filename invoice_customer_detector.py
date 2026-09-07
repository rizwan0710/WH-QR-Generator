import sqlite3

def dapatkan_customer_dari_outer(seq_outer):
    """
    FUNGSI DIPERKUKUH TOTAL: Mengesan nama customer berdasarkan Outer Box.
    Ia membaca data tuple pangkalan data dengan tepat dan mengekstrak siri WP pertama.
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
            # Ambil nilai string tulen dari elemen pertama tuple sqlite (elakkan guna str(res))
            text_raw = str(res[0]).strip()
            
            # Buang sebarang karakter sisa pembungkus string jika ada
            for char in ["[", "]", "'", '"', "(", ")"]:
                text_raw = text_raw.replace(char, "")
                
            # Pecahkan string berasaskan tanda koma
            linked_inners = text_raw.split(",")
            
            if linked_inners and len(linked_inners) > 0:
                # Ambil kotak Inner pertama (Contoh: WP26/08/200001)
                inner_pertama = linked_inners[0].strip()
                
                # 2. Cari siapakah nama Customer asal bagi Inner Box tersebut
                cursor.execute("SELECT customer FROM rekod_qr WHERE sequence_no = ?", (inner_pertama,))
                res_cust = cursor.fetchone()
                
                if res_cust and res_cust[0] and str(res_cust[0]).strip() != "None" and str(res_cust[0]).strip() != "":
                    return str(res_cust[0]).strip().upper()
                    
        return "INTERNAL/COMBINED"
    except Exception as e:
        print(f"Customer detection system error: {str(e)}")
        return "INTERNAL/COMBINED"
    finally:
        if conn:
            conn.close()
