# invoice_customer_detector.py - FULL AUTOMATED 3-IN-1 POP-UP ENGINE (LINKED FORM 4 & FORM 3)
import sqlite3
import os
import sys
import database_manager as dbm  # 🌟 Hubungan pangkalan data rasmi dinamik kalis .exe

def dapatkan_customer_dari_outer(seq_outer, ent_invoice=None, ent_so=None):
    """
    FUNGSI AUTOMATIK 3-IN-1 (INTEGRASI FORM 4 & FORM 3):
    1. Mengesan Nama Penuh Pelanggan berdasarkan barcode Outer Box (B...) yang diimbas.
    2. Mencari data Invoice No & SO No terkini di jadual master_invoice (Form 4) berpandukan nama pelanggan.
    3. Automatik menyuntik (auto-populate) data billing terus ke skrin UI Form 3.
    """
    if not seq_outer or seq_outer == "--- PILIH DATA ---":
        return ""
        
    conn = None
    try:
        # 🌟 PEMBETULAN UTAMA: Menggunakan DATABASE_PATH dinamik rasmi agar fail tidak terputus semasa jadi .exe
        conn = sqlite3.connect(dbm.DATABASE_PATH, timeout=10)
        cursor = conn.cursor()
        
        # 1. Cari siri linked inner box dari rekod Outer Box (B...)
        cursor.execute("SELECT machine FROM rekod_qr WHERE sequence_no = ?", (seq_outer.strip(),))
        res = cursor.fetchone()
        
        kod_imbas = ""
        nama_penuh_pelanggan = "INTERNAL/COMBINED"
        
        if res and res[0]:
            text_raw = str(res[0]).strip()
            
            # Buang sebarang karakter sisa pembungkus string
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
                    
                    # 3. IDEA ANDA: AMBIL NAMA PENUH KORPORAT LANGSUNG DARIPADA EXCEL LIST
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
                        nama_penuh_pelanggan = str(row_master[0]).strip().upper()
                    else:
                        # Fallback fleksibel sekiranya ada wildcard carian LIKE
                        cursor.execute("SELECT DISTINCT customer_name FROM master_produk WHERE customer_code LIKE ?", (f"%{kod_imbas}%",))
                        row_like = cursor.fetchone()
                        if row_like and row_like[0]:
                            nama_penuh_pelanggan = str(row_like[0]).strip().upper()
                        else:
                            nama_penuh_pelanggan = kod_imbas
                            
        # 🌟 4. ENJIN SUNTIKAN UTAMA: AUTO-POPULATE DATA INVOIS & SO NO (FORM 4 LINKAGE) 🌟
        # Hanya tercetus sekiranya nama pelanggan sah dan entri widget UI dihantar masuk oleh Form 3
        if nama_penuh_pelanggan and nama_penuh_pelanggan != "INTERNAL/COMBINED" and ent_invoice and ent_so:
            try:
                # Cari rekod invois paling terkini (ORDER BY id DESC) bagi syarikat ini
                cursor.execute("""
                    SELECT invoice_no, so_no FROM master_invoice 
                    WHERE TRIM(UPPER(customer_name)) = ? 
                    ORDER BY id DESC LIMIT 1
                """, (nama_penuh_pelanggan,))
                
                rekod_invois = cursor.fetchone()
                
                # Sediakan fungsi tkinter di dalam thread utama secara selamat
                import tkinter as tk
                if rekod_invois:
                    inv_no_auto, so_no_auto = rekod_invois
                    
                    # Bersihkan dan suntik Invoice Number secara automatik
                    if ent_invoice.winfo_exists():
                        ent_invoice.delete(0, tk.END)
                        ent_invoice.insert(0, str(inv_no_auto).strip())
                        
                    # Bersihkan dan suntik SO Number secara automatik
                    if ent_so.winfo_exists():
                        ent_so.delete(0, tk.END)
                        ent_so.insert(0, str(so_no_auto).strip())
                        
                    print(f"[AUTO-LINKAGE SUCCESS] Auto-filled INV: {inv_no_auto} | SO: {so_no_auto} for {nama_penuh_pelanggan}")
                else:
                    # Jika data pendaftaran bil di Form 4 belum diisi, kosongkan kotak entri untuk isian manual
                    if ent_invoice.winfo_exists(): ent_invoice.delete(0, tk.END)
                    if ent_so.winfo_exists(): ent_so.delete(0, tk.END)
                    print(f"[AUTO-LINKAGE NOTICE] Customer '{nama_penuh_pelanggan}' exists but no pre-registered billing docs found.")
            except Exception as e_link:
                print(f"Bypass auto-populate link module execution: {e_link}")

        return nama_penuh_pelanggan

    except Exception as e:
        print(f"Customer detection system error: {str(e)}")
        return "INTERNAL/COMBINED"
    finally:
        if conn:
            conn.close()
