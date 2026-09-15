# invoice_packing_logic.py - FULL PRODUCTION CODE (100% FIXED QUANTITY EXTRACTION & QR MATCHING)
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
    """Membaca kod box tunggal secara bersih untuk carian pangkalan data"""
    try:
        if not s:
            return None
        with sqlite3.connect("warehouse_data.db", timeout=10) as c: 
            return c.cursor().execute("SELECT customer, part_no, quantity FROM rekod_qr WHERE sequence_no = ?", (str(s).strip(),)).fetchone()
    except Exception as e:
        print(f"Ralat dapatkan_maklumat_outer: {e}")
        return None

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

def proses_submit_invoice(win, e_dt, e_inv, e_so, e_out, btn=None):
    """⚡ ENJIN SUBMIT DATA INVOICE OHTA PRECISION (3 RULES HARD LOCK + TUPLE INDEX FIX) ⚡"""
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

    # Ambil maklumat pelanggan daripada elemen senarai imbasan kotak pertama
    d1 = dapatkan_maklumat_outer(out[0])
    if not d1: 
        return messagebox.showerror("ERROR", "Box Reference Data Not Found in System Database!", parent=win)
        
    customer_utama, part_utama, qty_pcs_str = d1
    total_box, sk = len(out), []
    pola = datetime.datetime.now().strftime("%y%m%d")
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as cs:
            cur = cs.cursor()
            for i, c in enumerate(out, start=1):
                res = dapatkan_maklumat_outer(c)
                
                # 🌟 [CRITICAL FIX]: Hanya baca elemen indeks [2] daripada tuple untuk dapatkan kuantiti tulen
                if res and len(res) >= 3:
                    raw_qty_str = str(res[2]).upper().replace("PCS", "").strip()
                    qty = int(raw_qty_str) if raw_qty_str.isdigit() else 0
                else:
                    qty = 0
                
                cur.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"INV{pola}%",))
                max_r = cur.fetchone()
                
                # Ekstrak data string daripada objek sel tuple pangkalan data secara bersih
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
                
                cur.execute("INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no) VALUES (?,?,?,?,?,?,?,?,?)",
                            (dt, customer_utama, f"INV:{inv}", f"SO:{so}", f"{qty} PCS", datetime.datetime.now().strftime("%I:%M:%S %p"), c, pg, seq))
                
                # 🌟 FORMAT TEKS DATA QR DITETAPKAN SAMA TEPAT SEPERTI PREVIEW DATABASE 🌟
                universal_payload = (
                    f"SERIAL NO  : {seq.strip()}\n"
                    f"INVOICE NO : {inv.strip()}\n"
                    f"SO No      : {so.strip()}\n"
                    f"CUSTOMER   : {customer_utama.strip()}\n"
                    f"QUANTITY   : {qty} PCS"
                )
                
                qr = qrcode.QRCode(version=1, border=4, error_correction=qrcode.constants.ERROR_CORRECT_M)
                qr.add_data(universal_payload) 
                qr.make(fit=True)
                im_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                
                try:
                    stk = lid.bina_imej_invoice(img_qr=im_qr, invoice_no=inv, so_no=so, outer_seq=c, outer_qty=f"{qty} PCS", seq_inv_spesifik=seq, text_paging=pg, customer=customer_utama)
                    if stk: 
                        sk.append((stk, pg))
                except Exception as e: 
                    return messagebox.showerror("DESIGNER ERROR", str(e), parent=win)
            cs.commit()
            
        invoice_preview_window.buka_popup_individual_1by1(win, sk, inv)
        
    except Exception as e: 
        messagebox.showerror("DB ERROR", str(e), parent=win)

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
            for r in conn.cursor().execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, sequence_no FROM rekod_qr ORDER BY id DESC LIMIT 100").fetchall(): 
                tree.insert("", tk.END, values=r)
    except Exception as e: 
        messagebox.showerror("ERROR", str(e), parent=win)
