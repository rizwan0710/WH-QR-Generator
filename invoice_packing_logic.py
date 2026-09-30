# invoice_packing_logic.py - COMPREHENSIVE CONSOLIDATED TRANSACTIONS ENGINE (100% KALIS EXE)
import sqlite3
import datetime
import qrcode
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import label_invoice_designer as lid
import invoice_print_manager
import invoice_preview_window
import database_manager as dbm

btn_submit_ref = None

def bersihkan_nama_folder(n): 
    return "".join([c for c in n if c not in ['\\','/',':','*','?','"','<','>','|']]).strip()

def dapatkan_maklumat_outer(s):
    """
    Membaca kod box tunggal secara bersih untuk carian pangkalan data.
    🌟 SELESAI TOTAL: Mencari Nama Penuh secara langsung dari master_produk 
    berpandukan Kod Pelanggan tanpa kekangan drawing/part number yang rumit.
    """
    try:
        if not s:
            return None
        # 🌟 PEMBETULAN UTAMA: Hubungan dinamik rasmi dbm.DATABASE_PATH kalis .exe
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as c: 
            cursor = c.cursor()
            
            # 1. Ambil data asal dari log produksi (Mendapatkan kod pelanggan, part, dan qty)
            cursor.execute("SELECT customer, part_no, quantity FROM rekod_qr WHERE sequence_no = ?", (str(s).strip(),))
            rekod_asal = cursor.fetchone()
            
            if rekod_asal:
                kod_pendek, part_no, kuantiti = rekod_asal
                kod_pendek_bersih = str(kod_pendek).strip().upper()
                
                # 2. Cari nama penuh korporat di jadual master menggunakan Kod Pelanggan tadi
                query_master = """
                    SELECT DISTINCT customer_name 
                    FROM master_produk 
                    WHERE TRIM(UPPER(customer_code)) = ? OR TRIM(UPPER(customer_name)) = ? 
                    LIMIT 1
                """
                cursor.execute(query_master, (kod_pendek_bersih, kod_pendek_bersih))
                row_master = cursor.fetchone()
                
                if row_master and row_master[0] and str(row_master[0]).strip() != "":
                    return (str(row_master[0]).strip().upper(), part_no, kuantiti)
                
                # 3. Jika tiada di master, cuba cari menggunakan kaedah carian LIKE
                cursor.execute("SELECT DISTINCT customer_name FROM master_produk WHERE customer_code LIKE ? LIMIT 1", (f"%{kod_pendek_bersih}%",))
                row_like = cursor.fetchone()
                if row_like and row_like[0]:
                    return (str(row_like[0]).strip().upper(), part_no, kuantiti)
                    
                return (kod_pendek_bersih, part_no, kuantiti)
                
            return None
    except Exception as e:
        print(f"Ralat kritikal dapatkan_maklumat_outer: {e}")
        return None

def kendalikan_imbasan_sequence_auto_populate(sequence_no_input, ent_customer_name, ent_invoice_no, ent_so_no):
    """
    🔍 AUTOMATED DYNAMIC DATABASE LOOKUP ENGINE (FORM 4 LINKAGE) 🔍
    Triggered instantly when a sequence is scanned. Resolves Customer Name 
    from the QR record, then pulls pre-registered Invoice & SO numbers automatically.
    """
    seq_scanned = str(sequence_no_input).strip().upper()
    
    try:
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            
            # Step 1: Search for the Customer Name associated with this scanned sequence
            cursor.execute("SELECT customer FROM rekod_qr WHERE sequence_no = ?", (seq_scanned,))
            result_qr = cursor.fetchone()
            
            if result_qr and result_qr[0]:
                customer_mapped = str(result_qr[0]).strip().upper()
                
                # Update the Customer Name entry field on the GUI screen
                ent_customer_name.delete(0, tk.END)
                ent_customer_name.insert(0, customer_mapped)
                
                # Step 2: Query the master_invoice table built via Form 4 using the resolved Customer Name
                cursor.execute("""
                    SELECT invoice_no, so_no FROM master_invoice 
                    WHERE customer_name = ? 
                    ORDER BY id DESC LIMIT 1
                """, (customer_mapped,))
                
                result_invoice = cursor.fetchone()
                
                if result_invoice:
                    inv_auto, so_auto = result_invoice
                    
                    # 🚀 AUTOMATIC POP-UP LINKAGE ACTIVATED!
                    ent_invoice_no.delete(0, tk.END)
                    ent_invoice_no.insert(0, str(inv_auto).strip())
                    
                    ent_so_no.delete(0, tk.END)
                    ent_so_no.insert(0, str(so_auto).strip())
                    
                    print(f"✔️ Auto-Linkage Success: Synced {customer_mapped} to {inv_auto}/{so_auto}")
    except Exception as e:
        print(f"❌ Auto-populate lookup bypassed or encountered an index notice: {e}")

def dapatkan_nama_penuh_customer(cust_indicator):
    """
    🌟 ENGINE TRANSLATOR ANTI-FAIL (KALIS RUANG KOSONG & KESALAHAN DATA MASTER) 🌟
    Mencari nama syarikat panjang dengan memotong sebarang ruang kosong tersembunyi.
    """
    if not cust_indicator:
        return "INTERNAL/COMBINED"
        
    kod_bersih = str(cust_indicator).strip().upper()
    
    try:
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as c:
            cursor = c.cursor()
            
            query_tepat = """
                SELECT DISTINCT customer_name 
                FROM master_produk 
                WHERE REPLACE(UPPER(customer_code), ' ', '') = REPLACE(?, ' ', '')
                   OR REPLACE(UPPER(customer_name), ' ', '') = REPLACE(?, ' ', '')
                LIMIT 1
            """
            cursor.execute(query_tepat, (kod_bersih, kod_bersih))
            row = cursor.fetchone()
            if row and row[0] and str(row[0]).strip() != "":
                return str(row[0]).strip().upper()
                
            query_separa = """
                SELECT DISTINCT customer_name 
                FROM master_produk 
                WHERE customer_code LIKE ? OR customer_name LIKE ?
                LIMIT 1
            """
            pola = f"%{kod_bersih}%"
            cursor.execute(query_separa, (pola, pola))
            row_s = cursor.fetchone()
            if row_s and row_s[0] and str(row_s[0]).strip() != "":
                return str(row_s[0]).strip().upper()
                
    except Exception as e:
        print(f"Ralat kritikal penterjemah nama: {e}")
        
    return kod_bersih

def cetak_qr(target):
    try:
        im = target if isinstance(target, tuple) else target
        if im is None or not hasattr(im, "save"): return
        temp = "temp_print_invoice.png"
        im.save(temp)
        if sys.platform == "win32": os.startfile(temp, "print")
    except Exception as e: print(str(e))

def simpan_qr_manual(target, inv):
    try:
        im = target if isinstance(target, tuple) else target
        if im is None or not hasattr(im, "save"): return
        p = filedialog.asksaveasfilename(initialfile=f"INVOICE_{str(inv).replace('/','-')}.png", defaultextension=".png")
        if p: 
            im.convert("RGB").save(p, "PNG")
            messagebox.showinfo("Success", "Saved!")
    except Exception as e: print(str(e))
