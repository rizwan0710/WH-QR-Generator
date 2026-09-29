# invoice_packing_logic.py - PART 1: IMPORTS & CUSTOMER NAME LOOKUP ENGINES
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
        with sqlite3.connect("warehouse_data.db", timeout=10) as c: 
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
                    # Jika nama penuh dijumpai, pulangkan nama penuh bersama part dan qty asal
                    return (str(row_master[0]).strip().upper(), part_no, kuantiti)
                
                # 3. Jika tiada di master, cuba cari menggunakan kaedah partial carian LIKE
                cursor.execute("SELECT DISTINCT customer_name FROM master_produk WHERE customer_code LIKE ? LIMIT 1", (f"%{kod_pendek_bersih}%",))
                row_like = cursor.fetchone()
                if row_like and row_like[0]:
                    return (str(row_like[0]).strip().upper(), part_no, kuantiti)
                    
                # Pasang nama asal jika master list langsung tidak mengandungi kod tersebut
                return (kod_pendek_bersih, part_no, kuantiti)
                
            return None
    except Exception as e:
        print(f"Ralat kritikal dapatkan_maklumat_outer: {e}")
        return None

def dapatkan_nama_penuh_customer(cust_indicator):
    """
    🌟 ENGINE TRANSLATOR ANTI-FAIL (KALIS RUANG KOSONG & KESALAHAN DATA MASTER) 🌟
    Mencari nama syarikat panjang dengan memotong sebarang ruang kosong tersembunyi.
    """
    if not cust_indicator:
        return "INTERNAL/COMBINED"
        
    # Bersihkan string pencarian input secara menyeluruh
    kod_bersih = str(cust_indicator).strip().upper()
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as c:
            cursor = c.cursor()
            
            # Strategi 1: Carian tegar membuang semua ruang kosong (Spaces Strip Lookup)
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
                
            # Strategi 2: Carian separa fleksibel (Partial Wildcard Carian)
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
        
    # Sekiranya database master tidak mengandungi rekod kod ini, pulangkan string asal borang
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
    
# invoice_packing_logic.py - PART 2: CORE PROCESS SUBMIT INVOICE LOGIC
# invoice_packing_logic.py - PART 2: CORE PROCESS SUBMIT INVOICE LOGIC (FIXED RES INDEX TUPLE)

# invoice_packing_logic.py - PART 2: CORE PROCESS SUBMIT INVOICE LOGIC (DIRECT EXCEL MAP)
def proses_submit_invoice(win, e_dt, e_inv, e_so, e_out, btn=None):
    """⚡ ENJIN SUBMIT DATA INVOICE OHTA PRECISION (VERSI PENCURI TEKS SKRIN KIRI 100% SUCCESS) ⚡"""
    dt = e_dt.get_date().strftime("%d/%m/%Y") if hasattr(e_dt, 'get_date') else str(e_dt)
    inv, so = e_inv.get().strip().upper(), e_so.get().strip().upper()
    
    out = []
    for e in e_out:
        if hasattr(e, 'get'):
            val = e.get().strip().upper()
            if val: out.append(val)
        elif isinstance(e, str) and e.strip():
            out.append(e.strip().upper())
            
    if not inv or not so or not out: 
        return messagebox.showwarning("INCOMPLETE", "PLEASE FILL ALL FORMS COMPLETELY!", parent=win)
    
    # 🚨 [RULE 1]: SEKAT JIKA BUKAN NOMBOR SIRI OUTER BOX YANG SAH (MESTI BERMULA 'B')
    for idx, c_val in enumerate(out):
        if not c_val.startswith("B") or len(c_val) < 5:
            return messagebox.showerror(
                "🚨 INVALID SEQUENCE NUMBER",
                f"SUBMIT REJECTED!\n\nThe value [{c_val}] is NOT a valid Outer Box Sequence Number!",
                parent=win
            )

    # 🚨 [RULE 2]: SEKATAN MUTLAK KOTAK YANG SAMA
    if len(set(out)) != len(out):
        seen_values = set()
        for e in e_out:
            if hasattr(e, 'get'):
                v = e.get().strip().upper()
                if v in seen_values: e.delete(0, tk.END)
                else:
                    if v: seen_values.add(v)
                    
        return messagebox.showerror("🚨 SAME BOX SCAN ERROR", "You cannot submit the SAME Outer Box Sequence Number multiple times!", parent=win)
    
    # 🚨 [RULE 3]: SEKAT JIKA OUTERBOX DAHPUN PERNAH DIGUNAKAN DALAM REKOD LEPAS (DB CHECK)
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as cc:
            cursor_check = cc.cursor()
            for c in out:
                cursor_check.execute("SELECT drawing_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine = ?", (c,))
                if cursor_check.fetchone(): 
                    return messagebox.showerror("🚨 BOX ALREADY USED DETECTED", f"Outer Box [{c}] has ALREADY been used previously!", parent=win)
    except Exception as e: 
        return messagebox.showerror("ERROR", f"Database Verification Fail: {str(e)}", parent=win)

    # 🌟 LANGKAH EMAS: GELEDAH DAN AMBIL TEKS PANJANG TERUS DARI SKRIN BORANG KIRI SECARA PAKSA 🌟
    nama_pelanggan_penuh = ""
    
    def cari_teks_dari_widget(parent_widget):
        """Fungsi rekursif menyelami lapisan frame GUI untuk memetik teks nama penuh skrin kiri."""
        nonlocal nama_pelanggan_penuh
        if nama_pelanggan_penuh: 
            return
        try:
            for child in parent_widget.winfo_children():
                if isinstance(child, tk.Entry):
                    # Check jika widget tersebut adalah kotak readonly yang memegang teks biru alamat penuh anda
                    if str(child.cget("state")) == "readonly" or str(child.cget("fg")) == "#0D6EFD":
                        txt = str(child.get()).strip().upper()
                        if txt and txt != "- AUTO DETECT -" and not txt.isdigit() and len(txt) > 10:
                            nama_pelanggan_penuh = txt
                            return
                # Jika ada lapisan frame di dalam frame, selami ke dalam secara mendalam
                if child.winfo_children():
                    cari_teks_dari_widget(child)
        except Exception:
            pass

    # Jalankan operasi penggeledahan teks skrin
    cari_teks_dari_widget(win)
    
    # Fallback Keselamatan sekiranya widget gagal diimbas (Ambil dari carian biasa)
    if not nama_pelanggan_penuh or nama_pelanggan_penuh == "":
        d1 = dapatkan_maklumat_outer(out[0])
        if d1:
            nama_pelanggan_penuh = dapatkan_nama_penuh_customer(d1[0])
        else:
            nama_pelanggan_penuh = "INTERNAL/COMBINED"

    # Bersihkan nama daripada sisa teks placeholder
    if "- AUTO DETECT -" in nama_pelanggan_penuh:
        nama_pelanggan_penuh = nama_pelanggan_penuh.replace("- AUTO DETECT -", "").strip()

    total_box, sk = len(out), []
    pola = datetime.datetime.now().strftime("%y%m%d")
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as cs:
            cur = cs.cursor()
            for i, c in enumerate(out, start=1):
                res = dapatkan_maklumat_outer(c)
                
                if res and len(res) >= 3:
                    raw_qty_str = str(res[2]).upper().replace("PCS", "").strip()
                    qty = int(raw_qty_str) if raw_qty_str.isdigit() else 0
                else:
                    qty = 0
                
                cur.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"INV{pola}%",))
                max_r = cur.fetchone()
                
                if max_r and max_r[0]:
                    raw_seq = str(max_r[0]).strip()
                    try:
                        bil = int(raw_seq[-4:]) + 1
                    except (ValueError, IndexError):
                        bil = 1
                else:
                    bil = 1
                    
                seq = f"INV{pola}{bil:04d}"
                pg = f"BOX {i}/{total_box}"
                
                # Simpan rekod transaksi ke pangkalan data menggunakan Nama Penuh Pelanggan dari Skrin Utama
                cur.execute("INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no) VALUES (?,?,?,?,?,?,?,?,?)",
                            (dt, nama_pelanggan_penuh, f"INV:{inv}", f"SO:{so}", f"{qty} PCS", datetime.datetime.now().strftime("%I:%M:%S %p"), c, pg, seq))
                
                universal_payload = (
                    f"SERIAL NO  : {seq.strip()}\n"
                    f"INVOICE NO : {inv.strip()}\n"
                    f"SO No      : {so.strip()}\n"
                    f"CUSTOMER   : {nama_pelanggan_penuh.strip()}\n"
                    f"QUANTITY   : {qty} PCS"
                )
                
                qr = qrcode.QRCode(version=1, border=4, error_correction=qrcode.constants.ERROR_CORRECT_M)
                qr.add_data(universal_payload) 
                qr.make(fit=True)
                im_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                
                try:
                    # Menghantar teks suci alamat panjang skrin utama terus ke enjin reka bentuk stiker
                    stk = lid.bina_imej_invoice(img_qr=im_qr, invoice_no=inv, so_no=so, outer_seq=c, outer_qty=f"{qty} PCS", seq_inv_spesifik=seq, text_paging=pg, customer=nama_pelanggan_penuh)
                    if stk: 
                        sk.append((stk, pg))
                except Exception as e: 
                    return messagebox.showerror("DESIGNER ERROR", str(e), parent=win)
            cs.commit()
            
        invoice_preview_window.buka_popup_individual_1by1(win, sk, inv)
        
    except Exception as e: 
        messagebox.showerror("DB ERROR", str(e), parent=win)
