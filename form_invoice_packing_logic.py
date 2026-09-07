import sqlite3
import datetime
import qrcode
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import label_invoice_designer as lid
import invoice_print_manager  # Membawa masuk pengurus gabungan 1 tetingkap cetak

btn_submit_ref = None

def bersihkan_nama_folder(nama):
    for a in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']: 
        nama = nama.replace(a, '_')
    return nama.strip()

def dapatkan_maklumat_outer(outer_seq):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            return conn.cursor().execute("SELECT customer, part_no, quantity FROM rekod_qr WHERE sequence_no = ?", (str(outer_seq).strip(),)).fetchone()
    except: 
        return None

def cetak_qr(img_label):
    try:
        temp = "temp_print_invoice.png"
        img_label.save(temp)
        if sys.platform == "win32": 
            os.startfile(temp, "print")
    except Exception as e: 
        print(str(e))

def simpan_qr_manual(img_label, inv_no):
    p = filedialog.asksaveasfilename(initialfile=f"INVOICE_STICKER_{str(inv_no).replace('/','-')}.png", defaultextension=".png")
    if p: 
        img_label.convert("RGB").save(p, "PNG")
        messagebox.showinfo("Success", "Saved!")

def paparkan_pop_up_invoice_pukal(win_inv, entry_inv, entry_so, entries_outer, senarai_kad, inv_no, customer=""):
    """🌟 PANEL PREVIEW INVOICE SETELAH SUBMIT FORM (FIXED NAVIGASI ENGINE) 🌟"""
    tp = tk.Toplevel(win_inv.master)
    tp.title(f"INVOICE BATCH PANEL - {inv_no}")
    tp.geometry("540x510+420+120")
    tp.configure(bg="#F8F9FA")
    tp.grab_set()
    
    indeks_halaman = 0
    total_label = len(senarai_kad)

    lbl_h = tk.Label(tp, text="", font=("Segoe UI", 10, "bold"), fg="#EA580C", bg="#F8F9FA")
    lbl_h.pack(pady=12)
    
    fr_bg = tk.Frame(tp, bg="white", bd=1, relief="groove")
    fr_bg.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    
    lbl_i = tk.Label(fr_bg, bg="white")
    lbl_i.pack(padx=15, pady=15, expand=True, fill=tk.BOTH)

    def kemaskini_selak_borang():
        img, paging = senarai_kad[indeks_halaman]
        lbl_h.config(text=f"LABEL PREVIEW ({paging})  |  TOTAL BATCH: {total_label} BOXES")
        
        img_visual = img.resize((420, 200), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_visual)
        lbl_i.config(image=img_tk)
        lbl_i.image = img_tk
        
        if total_label > 1:
            btn_p.config(state="normal" if indeks_halaman > 0 else "disabled")
            btn_n.config(state="normal" if indeks_halaman < total_label - 1 else "disabled")

    def halaman_ke_kiri():
        nonlocal indeks_halaman
        if indeks_halaman > 0:
            indeks_halaman -= 1
            kemaskini_selak_borang()

    def halaman_ke_kanan():
        nonlocal indeks_halaman
        if indeks_halaman < total_label - 1:
            indeks_halaman += 1
            kemaskini_selak_borang()

    def reset_dan_tutup():
        global btn_submit_ref
        for e in [entry_inv, entry_so] + entries_outer: 
            e.config(state="normal")
            e.delete(0, tk.END)
        if btn_submit_ref and btn_submit_ref.winfo_exists(): 
            btn_submit_ref.config(state="normal", text="SUBMIT & PRINT INVOICE QR", bg="#007ACC")
        entry_inv.focus_set()
        tp.destroy()

    # Baris Navigasi Selak Halaman
    fr_nav = tk.Frame(tp, bg="#F8F9FA")
    btn_p = tk.Button(fr_nav, text="◀ PREV", command=halaman_ke_kiri, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_n = tk.Button(fr_nav, text="NEXT ▶", command=halaman_ke_kanan, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    
    if total_label > 1: 
        fr_nav.pack(pady=5)
        btn_p.pack(side=tk.LEFT, padx=8)
        btn_n.pack(side=tk.LEFT, padx=8)

    fr_btn = tk.Frame(tp, bg="#F8F9FA")
    fr_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    b_st = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}
    
    if total_label == 1:
        tk.Button(fr_btn, text="🖨️ PRINT ", command=lambda: cetak_qr(senarai_kad[0][0]), bg="#22C55E", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(fr_btn, text="💾 SAVE ", command=lambda: simpan_qr_manual(senarai_kad[0][0], inv_no), bg="#F59E0B", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    else:
        tk.Button(fr_btn, text="🖨️ PRINT CURRENT", command=lambda: cetak_qr(senarai_kad[indeks_halaman][0]), bg="#22C55E", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        # 🌟 PRINT ALL memanggil enjin gabungan kelompok 1 pop-up tingkap printer Windows
        tk.Button(fr_btn, text="🔥 PRINT ALL (1 WINDOW)", command=lambda: invoice_print_manager.cetak_a4_batch([k for k, _ in senarai_kad]), bg="#10B981", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
    tk.Button(fr_btn, text="❌ CLOSE", command=reset_dan_tutup, bg="#374151", **b_st).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)
    
    kemaskini_selak_borang()

def proses_submit_invoice(win_inv, entry_date, entry_inv, entry_so, entries_outer, btn_submit_widget=None):
    global btn_submit_ref
    if btn_submit_widget: 
        btn_submit_ref = btn_submit_widget
    tarikh_str = entry_date.get_date().strftime("%d/%m/%Y") if hasattr(entry_date, 'get_date') else str(entry_date)
    inv_no, so_no = entry_inv.get().strip().upper(), entry_so.get().strip().upper()
    senarai_outer = [e.get().strip().upper() for e in entries_outer if e.get().strip()]

    if not inv_no or not so_no or not senarai_outer: 
        return messagebox.showwarning("INCOMPLETE", "PLEASE COMPLETE THE FORM!", parent=win_inv)
    if len(senarai_outer) != len(set(senarai_outer)): 
        return messagebox.showerror("FORM ERROR", "SAME OUTER BOX SN DETECTED!", parent=win_inv)

    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn_check:
            for code in senarai_outer:
                if conn_check.cursor().execute("SELECT drawing_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine = ?", (code,)).fetchone():
                    return messagebox.showerror("LINKED BOX DUPLICATE ERROR", f"❌ DUPLICATE RESTRICTION!\nOUTER BOX[{code}] ALREADY SCANNED AT OTHER INVOICE!", parent=win_inv)
    except Exception as e: 
        return messagebox.showerror("ERROR", str(e), parent=win_inv)

    data_1 = dapatkan_maklumat_outer(senarai_outer[0])
    if not data_1: 
        return messagebox.showerror("ERROR", f"OUTER BOX [{senarai_outer[0]}] Slot 1 CANNOT BE FOUND!", parent=win_inv)
    customer_utama, part_utama, qty_pcs_str = data_1
    total_qty, total_box, senarai_kad = 0, len(senarai_outer), []

    tarikh_pola = datetime.datetime.now().strftime("%y%m%d")
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn_save:
            cursor = conn_save.cursor()
            for idx, code in enumerate(senarai_outer, start=1):
                res = dapatkan_maklumat_outer(code)
                if not res: 
                    return messagebox.showerror("ERROR", f"OUTER BOX[{code}] CANNOT BE FOUND!", parent=win_inv)
                
                qty_clean = str(res[2]).upper().replace("PCS","").strip()
                if qty_clean.isdigit(): 
                    total_qty = int(qty_clean)
                else:
                    try: total_qty = int(float(qty_clean))
                    except: total_qty = 0
                
                cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"INV{tarikh_pola}%",))
                max_r = cursor.fetchone()
                
                bil = int(str(max_r[0])[-4:]) if (max_r and max_r[0]) else 0
                bil += 1
                seq = f"INV{tarikh_pola}{bil:04d}"
                paging = f"BOX {idx}/{total_box}"
                
                cursor.execute("INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no) VALUES (?,?,?,?,?,?,?,?,?)",
                               (tarikh_str, customer_utama, f"INV:{inv_no}", f"SO:{so_no}", f"{total_qty} PCS", datetime.datetime.now().strftime("%I:%M:%S %p"), code, paging, seq))
                
                # 🌟 KOREKSI UTAMA ISU 1: Menjana QR Code dan menghantar 8 parameter yang sepadan dengan fungsi 'bina_imej_invoice'
                qr = qrcode.QRCode(version=1, box_size=10, border=1)
                qr.add_data(seq)
                qr.make(fit=True)
                img_qr = qr.make_image(fill_color="black", back_color="white")
                
                try:
                    # Memanggil fungsi reka bentuk stiker yang betul dari label_invoice_designer.py
                    img_stiker = lid.bina_imej_invoice(
                        img_qr=img_qr,
                        invoice_no=inv_no,
                        so_no=so_no,
                        outer_seq=code,
                        outer_qty=f"{total_qty} PCS",
                        seq_inv_spesifik=seq,
                        text_paging=paging,
                        customer=customer_utama
                    )
                    if img_stiker:
                        senarai_kad.append((img_stiker, paging))
                except AttributeError:
                    return messagebox.showerror("DESIGNER ERROR", "Fungsi 'bina_imej_invoice' gagal dipanggil dari fail label_invoice_designer.py", parent=win_inv)
            
            conn_save.commit()
            
        paparkan_pop_up_invoice_pukal(win_inv, entry_inv, entry_so, entries_outer, senarai_kad, inv_no, customer_utama)
        
    except Exception as e:
        messagebox.showerror("DATABASE TRANSACTION ERROR", f"Gagal memproses transaksi: {str(e)}", parent=win_inv)
