# form_invoice_packing_logic.py - PART 2: CORE PROCESS SUBMIT INVOICE TRANSACTION ENGINE (MUKTAMAD 100% STABLE)
import sqlite3
import datetime
import qrcode
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import database_manager as dbm

try:
    import label_invoice_designer as lid
except ImportError:
    pass

def bersihkan_nama_folder(n): 
    return "".join([c for c in n if c not in ['\\','/',':','*','?','"','<','>','|']]).strip()

def dapatkan_maklumat_outer(s):
    """Membaca kod box tunggal secara bersih untuk carian pangkalan data."""
    try:
        if not s: return None
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as c: 
            cursor = c.cursor()
            cursor.execute("SELECT customer, part_no, quantity FROM rekod_qr WHERE sequence_no = ?", (str(s).strip(),))
            rekod_asal = cursor.fetchone()
            if rekod_asal:
                kod_pendek, part_no, kuantiti = rekod_asal
                kod_pendek_bersih = str(kod_pendek).strip().upper()
                
                query_master = "SELECT DISTINCT customer_name FROM master_produk WHERE TRIM(UPPER(customer_code)) = ? OR TRIM(UPPER(customer_name)) = ? LIMIT 1"
                cursor.execute(query_master, (kod_pendek_bersih, kod_pendek_bersih))
                row_master = cursor.fetchone()
                if row_master and row_master:
                    return (str(row_master[0]).strip().upper(), part_no, kuantiti)
                return (kod_pendek_bersih, part_no, kuantiti)
            return None
    except Exception:
        return None

def dapatkan_nama_penuh_customer_direct(cust_indicator):
    """Mencari nama syarikat panjang dengan memotong sebarang ruang kosong tersembunyi."""
    if not cust_indicator: return "INTERNAL/COMBINED"
    kod_bersih = str(cust_indicator).strip().upper()
    try:
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as c:
            cursor = c.cursor()
            query_tepat = "SELECT DISTINCT customer_name FROM master_produk WHERE REPLACE(UPPER(customer_code), ' ', '') = REPLACE(?, ' ', '') LIMIT 1"
            cursor.execute(query_tepat, (kod_bersih,))
            row = cursor.fetchone()
            if row and row: return str(row[0]).strip().upper()
    except Exception:
        pass
    return kod_bersih

def proses_submit_invoice(win, e_dt, e_inv, e_so, e_out, btn=None):
    """⚡ ENJIN SUBMIT DATA INVOICE OHTA PRECISION - REKA BENTUK FORM FIXED ⚡"""
    dt = e_dt.get_date().strftime("%d/%m/%Y") if hasattr(e_dt, 'get_date') else str(e_dt)
    inv, so = e_inv.get().strip().upper(), e_so.get().strip().upper()
    out = [e.get().strip().upper() for e in e_out if e.get().strip()]
    if not inv or not so or not out: 
        return messagebox.showwarning("INCOMPLETE", "FILL FORM!")
    
    laluan_utama_db = dbm.DATABASE_PATH
    
    try:
        # 1. Semak duplicate box secara awal di database utama
        with sqlite3.connect(laluan_utama_db, timeout=10) as cc:
            for c in out:
                if cc.cursor().execute("SELECT drawing_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine = ?", (c,)).fetchone(): 
                    return messagebox.showerror("DUPLICATE", f"Box {c} Used!")
    except Exception as e: 
        return messagebox.showerror("ERROR", str(e))

    # Ambil maklumat kotak pertama untuk rujukan data produk
    d1 = dapatkan_maklumat_outer(out[0])
    if not d1: 
        return messagebox.showerror("ERROR", f"Box {out[0]} Not Found in Database!")
        
    customer_utama, part_utama, qty_pcs_str = d1
    nama_pelanggan_penuh = dapatkan_nama_penuh_customer_direct(customer_utama)
    
    total_box, sk = len(out), []
    pola = datetime.datetime.now().strftime("%y%m%d")
    
    try:
        clean_date_folder = dt.replace("/", "-")
        clean_customer_folder = bersihkan_nama_folder(nama_pelanggan_penuh[:30]) 
        target_save_directory = os.path.join("INVOICE_STICKER", clean_date_folder, clean_customer_folder)
        if not os.path.exists(target_save_directory):
            os.makedirs(target_save_directory)
    except Exception as e_folder:
        print(f"Folder skip: {str(e_folder)}")

    # =========================================================================
    # 🌟 LANGKAH A: JANA DATA & MASUK DATABASE (HANYA PURE 2 BARIS SAHAJA) 🌟
    # =========================================================================
    senarai_data_mentah_insert = []
    
    try:
        with sqlite3.connect(laluan_utama_db, timeout=10) as cs:
            cur = cs.cursor()
            
            # Cari nombor bil permulaan terbaharu daripada database
            cur.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"INV{pola}%",))
            max_r = cur.fetchone()
            bil_mula = (int(str(max_r[0])[-4:]) + 1) if (max_r and max_r[0]) else 1
            
            for i, c in enumerate(out, start=1):
                res = dapatkan_maklumat_outer(c)
                q_cl = str(res[2]).upper().replace("PCS","").strip() if res else "0"
                qty = int(q_cl) if q_cl.isdigit() else 0
                
                customer_kotak_ini = res[0] if res else customer_utama
                nama_pelanggan_penuh_kotak = dapatkan_nama_penuh_customer_direct(customer_kotak_ini)
                
                # Bina urutan nombor siri INV yang unik
                seq = f"INV{pola}{(bil_mula + i - 1):04d}"
                pg = f"BOX {i}/{total_box}"
                
                # INSERT SECARA BERSIH ke SQLite database utama
                cur.execute("""
                    INSERT INTO rekod_qr 
                    (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no) 
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (dt, nama_pelanggan_penuh_kotak, f"INV:{inv}", f"SO:{so}", f"{qty} PCS", datetime.datetime.now().strftime("%I:%M:%S %p"), c, pg, seq))
                
                row_id = cur.lastrowid
                
                # Simpan struktur baris data ke dalam list memori (Format sebati Treeview Panel)
                row_tuple = ("☐", row_id, dt, nama_pelanggan_penuh_kotak, inv, so, f"{qty} PCS", pg, c, "INVOICE LOG", seq)
                senarai_data_mentah_insert.append(row_tuple)
                
                # Penjanaan grafik imej QR & Label PNG
                qr_payload = f"SERIAL NO : {seq.strip()} INVOICE NO : {inv.strip()} SO No : {so.strip()} CUSTOMER : {nama_pelanggan_penuh_kotak.strip()} QUANTITY : {qty} PCS"
                qr = qrcode.QRCode(version=1, border=1)
                qr.add_data(qr_payload)  
                qr.make(fit=True)
                im_qr = qr.make_image().convert("RGB")
                
                try:
                    stk = lid.bina_imej_invoice(img_qr=im_qr, invoice_no=inv, so_no=so, outer_seq=c, outer_qty=f"{qty} PCS", seq_inv_spesifik=seq, text_paging=pg, customer=nama_pelanggan_penuh_kotak)
                    if stk: 
                        sk.append((stk, pg))
                        clean_seq_name = str(seq).strip()
                        clean_page_name = pg.replace("/", "-").replace(" ", "_")
                        file_save_destination = os.path.join(target_save_directory, f"LABEL_{clean_seq_name}_{clean_page_name}.png")
                        stk.save(file_save_destination, "PNG")
                except Exception as e_label:
                    print(f"Designer skip: {str(e_label)}")
            
            cs.commit()
            
        # 🌟 KALIS GERAKAN LOG: Bungkus logger audit dengan perlindungan tegar supaya tidak mengganggu preview 🌟
        try:
            import database_audit_logger
            msg_log = f"SUBMITTED INVOICE: {str(inv)} | SO: {str(so)} | TOTAL BOX: {str(total_box)}"
            database_audit_logger.record_edit_activity("INVOICE PACKING FORM", msg_log)
        except Exception as e_log_skip:
            print(f"[LOG NOT NOTICE] Dilepaskan demi kelancaran rendering: {str(e_log_skip)}")

        # =========================================================================
        # 🌟 LANGKAH B: PAPARAN WIZARD PRATONTON FIZIKAL (100% GAMBAR 2) 🌟
        # =========================================================================
        senarai_fail_imej_fizikal = []
        if senarai_data_mentah_insert:
            for data_row in senarai_data_mentah_insert:
                seq_specific = data_row[-1]  
                pg_status = data_row[-4]     
                
                clean_seq_name = str(seq_specific).strip()
                clean_page_name = pg_status.replace("/", "-").replace(" ", "_")
                file_path = os.path.join(target_save_directory, f"LABEL_{clean_seq_name}_{clean_page_name}.png")
                
                if os.path.exists(file_path):
                    senarai_fail_imej_fizikal.append(file_path)

        # Hantar fail fizikal melintang asli terus ke dalam database_batch_preview
        if senarai_fail_imej_fizikal:
            import database_batch_preview
            database_batch_preview.buka_popup_database_pukal_seragam(win, senarai_fail_imej_fizikal)
        else:
            import database_batch_preview
            database_batch_preview.buka_popup_database_pukal_seragam(win, senarai_data_mentah_insert)
                
        messagebox.showinfo("SUCCESS", f"Invoice {inv} successfully registered!", parent=win)
        win.destroy()
        
    except Exception as e_main:
        messagebox.showerror("DATABASE ERROR", f"Transaction aborted context:\n{str(e_main)}", parent=win)
