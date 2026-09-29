# form_invoice_packing_logic.py - PART 1: IMPORTS & FULL PROHIBITED CHARACTER SANITIZER
import sqlite3
import datetime
import qrcode
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import label_invoice_designer as lid
import invoice_print_manager
import central_tab_invoice_wizard  

btn_submit_ref = None

def bersihkan_nama_folder(n): 
    """
    🌟 ENGINE FIX: Membersihkan nama folder daripada sebarang karakter haram sistem fail.
    Membuang tanda sengkang biasa (/) dan sengkang terbalik (\) supaya folder path tidak pecah.
    """
    if not n:
        return "UNKNOWN_CUSTOMER"
    
    # Tukarkan sebarang newline (\n) kepada ruang kosong biasa terlebih dahulu
    nama_bersih = str(n).replace("\n", " ").replace("\r", " ").strip()
    
    # Senarai karakter haram Windows bagi nama fail dan folder (Termasuk tanda \ dan /)
    karakter_haram = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '\t']
    
    for c in karakter_haram:
        nama_bersih = nama_bersih.replace(c, "")
        
    # Buang ruang kosong berkembar hasil daripada pembersihan
    nama_bersih = " ".join(nama_bersih.split())
    
    # Hadkan panjang nama folder maksimum 40 huruf sahaja supaya tidak melanggar limitasi OS Path
    return nama_bersih[:40].strip()

def dapatkan_maklumat_outer(s):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as c: 
            target_seq = s[0] if isinstance(s, (list, tuple)) and len(s) > 0 else s
            return c.cursor().execute("SELECT customer, part_no, quantity FROM rekod_qr WHERE sequence_no = ?", (str(target_seq).strip(),)).fetchone()
    except Exception as e:
        print(f"Error dapatkan_maklumat_outer: {e}")
        return None

def dapatkan_nama_penuh_customer_direct(cust_indicator):
    if not cust_indicator:
        return "INTERNAL/COMBINED"
    kod_bersih = str(cust_indicator).strip().upper()
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as c:
            cursor = c.cursor()
            query_user_idea = """
                SELECT DISTINCT customer_name 
                FROM master_produk 
                WHERE TRIM(UPPER(customer_code)) = ? OR TRIM(UPPER(customer_name)) = ?
                LIMIT 1
            """
            cursor.execute(query_user_idea, (kod_bersih, kod_bersih))
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip().upper()
                
            cursor.execute("SELECT DISTINCT customer_name FROM master_produk WHERE customer_code LIKE ? LIMIT 1", (f"%{kod_bersih}%",))
            row_like = cursor.fetchone()
            if row_like and row_like[0]:
                return str(row_like[0]).strip().upper()
    except Exception:
        pass
    return kod_bersih


def cetak_qr(target):
    try:
        im = target if isinstance(target, tuple) else target
        if im is None or not hasattr(im, "save"): return
        temp = "temp_print_invoice.png"
        im.save(temp)
        if sys.platform == "win32": 
            os.startfile(temp, "print")
    except Exception as e: 
        print(f"Printing error: {str(e)}")

def simpan_qr_manual(target, inv):
    try:
        im = target if isinstance(target, tuple) else target
        if im is None or not hasattr(im, "save"): return
        p = filedialog.asksaveasfilename(initialfile=f"INVOICE_{str(inv).replace('/','-')}.png", defaultextension=".png")
        if p: 
            im.convert("RGB").save(p, "PNG")
            messagebox.showinfo("Success", "Saved!")
    except Exception as e: 
        print(str(e))

def proses_submit_invoice(win, e_dt, e_inv, e_so, e_out, btn=None):
    """⚡ ENJIN SUBMIT DATA INVOICE OHTA PRECISION - REKA BENTUK FORM FIXED ⚡"""
    dt = e_dt.get_date().strftime("%d/%m/%Y") if hasattr(e_dt, 'get_date') else str(e_dt)
    inv, so = e_inv.get().strip().upper(), e_so.get().strip().upper()
    out = [e.get().strip().upper() for e in e_out if e.get().strip()]
    if not inv or not so or not out: 
        return messagebox.showwarning("INCOMPLETE", "FILL FORM!")
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as cc:
            for c in out:
                if cc.cursor().execute("SELECT drawing_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine = ?", (c,)).fetchone(): 
                    return messagebox.showerror("DUPLICATE", f"Box {c} Used!")
    except Exception as e: 
        return messagebox.showerror("ERROR", str(e))

    d1 = dapatkan_maklumat_outer(out[0])
    if not d1: 
        return messagebox.showerror("ERROR", f"Box {out} Not Found in Database!")
        
    customer_utama, part_utama, qty_pcs_str = d1
    
    # 🌟 KOREKSI UTAMA 1: Tukar kod pendek awal kepada NAMA PENUH KORPORAT dari Excel Master list 🌟
    nama_pelanggan_penuh = dapatkan_nama_penuh_customer_direct(customer_utama)
    
    total_box, sk = len(out), []
    pola = datetime.datetime.now().strftime("%y%m%d")
    
    try:
        clean_date_folder = dt.replace("/", "-")
        clean_customer_folder = bersihkan_nama_folder(nama_pelanggan_penuh[:30]) # Potong sedikit jika nama + alamat terlampau panjang untuk os folder path
        target_save_directory = os.path.join("INVOICE_STICKER", clean_date_folder, clean_customer_folder)
        if not os.path.exists(target_save_directory):
            os.makedirs(target_save_directory)
    except Exception as e_folder:
        print(f"Folder skip: {str(e_folder)}")

    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as cs:
            cur = cs.cursor()
            for i, c in enumerate(out, start=1):
                res = dapatkan_maklumat_outer(c)
                q_cl = str(res[2]).upper().replace("PCS","").strip() if res else "0"
                qty = int(q_cl) if q_cl.isdigit() else 0
                
                # 🌟 KOREKSI UTAMA 2: Tukar kod ringkas kotak harian kepada NAMA PENUH KORPORAT juga 🌟
                customer_kotak_ini = res[0] if res else customer_utama
                nama_pelanggan_penuh_kotak = dapatkan_nama_penuh_customer_direct(customer_kotak_ini)
                
                cur.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"INV{pola}%",))
                max_r = cur.fetchone()
                bil = (int(str(max_r[0])[-4:]) + 1) if (max_r and max_r[0]) else 1
                seq = f"INV{pola}{bil:04d}"
                pg = f"BOX {i}/{total_box}"
                
                # Simpan log transaksi INV menggunakan nama penuh rasmi
                cur.execute("INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no) VALUES (?,?,?,?,?,?,?,?,?)",
                            (dt, nama_pelanggan_penuh_kotak, f"INV:{inv}", f"SO:{so}", f"{qty} PCS", datetime.datetime.now().strftime("%I:%M:%S %p"), c, pg, seq))
                
                qr_payload = (
                    f"SERIAL NO : {seq.strip()} "
                    f"INVOICE NO : {inv.strip()} "
                    f"SO No : {so.strip()} "
                    f"CUSTOMER : {nama_pelanggan_penuh_kotak.strip()} "
                    f"QUANTITY : {qty} PCS"
                )

                qr = qrcode.QRCode(version=1, border=1)
                qr.add_data(qr_payload)  
                qr.make(fit=True)
                im_qr = qr.make_image().convert("RGB")
                
                try:
                    # 🌟 KOREKSI UTAMA 3: Menembak variabel 'nama_pelanggan_penuh_kotak' (Alamat Panjang) ke enjin stiker 🌟
                    stk = lid.bina_imej_invoice(img_qr=im_qr, invoice_no=inv, so_no=so, outer_seq=c, outer_qty=f"{qty} PCS", seq_inv_spesifik=seq, text_paging=pg, customer=nama_pelanggan_penuh_kotak)
                    if stk: 
                        sk.append((stk, pg))
                        clean_seq_name = str(seq).strip()
                        clean_page_name = pg.replace("/", "-").replace(" ", "_")
                        file_save_destination = os.path.join(target_save_directory, f"LABEL_{clean_seq_name}_{clean_page_name}.png")
                        stk.convert("RGB").save(file_save_destination, "PNG")
                        
                except Exception as e_design: 
                    return messagebox.showerror("DESIGNER ERROR", str(e_design))
            cs.commit()
            
            try:
                import dashboard_logic
                dashboard_logic.laksanakan_auto_backup_NAS()
            except:
                pass
            
    except Exception as e: 
        messagebox.showerror("DB ERROR", str(e))
        return

    central_tab_invoice_wizard.buka_popup_individual_1by1(win, sk, inv)

def buka_window_preview_database_nas(win):
    tp = tk.Toplevel(win)
    tp.title("NAS PREVIEW")
    tp.geometry("820x450")
    tp.grab_set()
    fr = tk.Frame(tp)
    fr.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
    cols = ("ID", "Date", "Customer", "Drawing No", "Part No", "Quantity", "Sequence No")
    tree = ttk.Treeview(fr, columns=cols, show="headings")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    for c in cols: 
        tree.heading(c, text=c)
        tree.column(c, width=100, anchor="center")
    sb = ttk.Scrollbar(fr, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, sequence_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' ORDER BY id DESC")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
    except Exception as e:
        messagebox.showerror("PREVIEW ERROR", f"Gagal memuatkan data NAS:\n{str(e)}", parent=tp)
