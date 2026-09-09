import sqlite3
import datetime
import qrcode
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import label_invoice_designer as lid
import invoice_print_manager
import central_tab_invoice_wizard  # 🌟 SINKRONISASI MUTTAMAD: Memanggil fail wizard pratinjau yang betul

btn_submit_ref = None

def bersihkan_nama_folder(n): 
    """Removes prohibited operational filesystem characters from directory naming strings."""
    return "".join([c for c in n if c not in ['\\','/',':','*','?','"','<','>','|']]).strip()

def dapatkan_maklumat_outer(s):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as c: 
            return c.cursor().execute("SELECT customer, part_no, quantity FROM rekod_qr WHERE sequence_no = ?", (str(s).strip(),)).fetchone()
    except: 
        return None

def cetak_qr(target):
    """🖨️ ENJIN CETAK DIRECT MUTTAMAD (EXTRACTS INDEX FROM TUPLE) 🖨️"""
    try:
        im = None
        if isinstance(target, tuple) and len(target) > 0:
            im = target[0]
        elif isinstance(target, list) and len(target) > 0:
            item = target[0]
            im = item[0] if isinstance(item, tuple) else item
        else:
            im = target
        
        if im is None or not hasattr(im, "save"):
            print("Ralat: Gagal mengekstrak objek imej bersih.")
            return

        temp = "temp_print_invoice.png"
        im.save(temp)
        if sys.platform == "win32": 
            os.startfile(temp, "print")
    except Exception as e: 
        print(f"Invoice logic file printing error: {str(e)}")

def simpan_qr_manual(target, inv):
    """💾 ENJIN SIMPAN DIRECT MUTTAMAD (EXTRACTS INDEX FROM TUPLE) 💾"""
    try:
        im = None
        if isinstance(target, tuple) and len(target) > 0:
            im = target[0]
        elif isinstance(target, list) and len(target) > 0:
            item = target[0]
            im = item[0] if isinstance(item, tuple) else item
        else:
            im = target
        
        if im is None or not hasattr(im, "save"):
            print("Ralat: Gagal mengekstrak imej untuk simpanan.")
            return
            
        p = filedialog.asksaveasfilename(initialfile=f"INVOICE_{str(inv).replace('/','-')}.png", defaultextension=".png")
        if p: 
            im.convert("RGB").save(p, "PNG")
            messagebox.showinfo("Success", "Saved!")
    except Exception as e: 
        print(str(e))

def proses_submit_invoice(win, e_dt, e_inv, e_so, e_out, btn=None):
    """⚡ ENJIN SUBMIT DATA INVOICE OHTA PRECISION WITH AUTOMATIC FOLDER CREATION ⚡"""
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
        return messagebox.showerror("ERROR", f"Box {out[0]} Not Found!")
    customer_utama, part_utama, qty_pcs_str = d1
    total_box, sk = len(out), []
    pola = datetime.datetime.now().strftime("%y%m%d")
    
    # 🌟 STEP 1: AUTOMATIC BACKGROUND DIRECTORY GENERATION LAYER 🌟
    # Generates a standardized path structural link: INVOICE_STICKER / DATE / CUSTOMER_NAME
    try:
        clean_date_folder = dt.replace("/", "-")
        clean_customer_folder = bersihkan_nama_folder(customer_utama)
        
        # Staging the folder path layer string configurations
        target_save_directory = os.path.join("INVOICE_STICKER", clean_date_folder, clean_customer_folder)
        
        if not os.path.exists(target_save_directory):
            os.makedirs(target_save_directory)
            
    except Exception as e_folder:
        print(f"Silent warning: Folder path generation layer skipped - {str(e_folder)}")

    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as cs:
            cur = cs.cursor()
            for i, c in enumerate(out, start=1):
                res = dapatkan_maklumat_outer(c)
                q_cl = str(res[2]).upper().replace("PCS","").strip() if res else "0"
                qty = int(q_cl) if q_cl.isdigit() else 0
                
                cur.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"INV{pola}%",))
                max_r = cur.fetchone()
                bil = (int(str(max_r[0])[-4:]) + 1) if (max_r and max_r[0]) else 1
                seq = f"INV{pola}{bil:04d}"
                pg = f"BOX {i}/{total_box}"
                
                cur.execute("INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no) VALUES (?,?,?,?,?,?,?,?,?)",
                            (dt, customer_utama, f"INV:{inv}", f"SO:{so}", f"{qty} PCS", datetime.datetime.now().strftime("%I:%M:%S %p"), c, pg, seq))
                
                # FORMAT DATA QR BARU (MUTTAMAD & STRUCTURED)
                qr_payload = (
                    f"SN: {seq.strip()}\n"
                    f"Invoice No: {inv.strip()}\n"
                    f"SO No: {so.strip()}\n"
                    f"Customer: {customer_utama.strip()}\n"
                    f"Qty: {qty} PCS"
                )

                qr = qrcode.QRCode(version=1, border=1)
                qr.add_data(qr_payload)  
                qr.make(fit=True)
                im_qr = qr.make_image().convert("RGB")
                
                try:
                    stk = lid.bina_imej_invoice(img_qr=im_qr, invoice_no=inv, so_no=so, outer_seq=c, outer_qty=f"{qty} PCS", seq_inv_spesifik=seq, text_paging=pg, customer=customer_utama)
                    if stk: 
                        sk.append((stk, pg))
                        
                        # 🌟 STEP 2: AUTOMATIC STICKER ASSET AUTO-SAVE SEQUENCE 🌟
                        # Silently writes the output artifact file straight into the target save directory
                        clean_seq_name = str(seq).strip()
                        clean_page_name = pg.replace("/", "-").replace(" ", "_")
                        file_save_destination = os.path.join(target_save_directory, f"LABEL_{clean_seq_name}_{clean_page_name}.png")
                        stk.convert("RGB").save(file_save_destination, "PNG")
                        
                except Exception as e_design: 
                    return messagebox.showerror("DESIGNER ERROR", str(e_design))
            cs.commit()
            
        # Standard dynamic batch window load framework launcher sequence 
        central_tab_invoice_wizard.buka_popup_individual_1by1(win, sk, inv)
        
    except Exception as e: 
        messagebox.showerror("DB ERROR", str(e))

def buka_window_preview_database_nas(win):
    """⚡ LIVE PREVIEW JADUAL DATABASE NAS ⚡"""
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
        messagebox.showerror("ERROR", str(e))
