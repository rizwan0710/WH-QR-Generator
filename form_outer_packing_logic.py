import sqlite3
import datetime
import qrcode
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import label_outer_designer as lod

# Penjejak rujukan butang submit utama borang luar untuk logik kunci keselamatan
btn_submit_ref = None 

def bersihkan_nama_folder(nama):
    """Membuang aksara yang dilarang dalam sistem fail Windows/OS untuk folder"""
    for a in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']: 
        nama = nama.replace(a, '_')
    return nama.strip()

def dapatkan_maklumat_inner(inner_seq):
    """Mengekstrak maklumat rekod kotak dalaman (WP%) dari pangkalan data pusat."""
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            return conn.cursor().execute("SELECT tarikh, customer, drawing_no, part_no, quantity FROM rekod_qr WHERE sequence_no = ?", (inner_seq,)).fetchone()
    except: 
        return None

def semak_adakah_inner_sudah_digunakan(inner_seq):
    """Menyemak status silang sekiranya kod siri WP% telah didaftarkan pada kotak luar lain."""
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            res = conn.cursor().execute("SELECT sequence_no FROM rekod_qr WHERE lotcard_no = 'OUTER BOX' AND machine LIKE ?", (f"%{inner_seq}%",)).fetchone()
            return res[0] if res else None
    except: 
        return None

def cetak_qr(img_label):
    """Menghantar imej label Outer Box terus ke gilir pencetak thermal Windows."""
    try:
        temp = "temp_print_outer.png"
        img_label.save(temp)
        if sys.platform == "win32": 
            os.startfile(temp, "print")
    except Exception as e: 
        print(e)

def simpan_qr_manual(img, seq):
    """Menyimpan fail imej stiker luar secara manual ke komputer."""
    p = filedialog.asksaveasfilename(initialfile=f"OUTER_STICKER_{seq}.png", defaultextension=".png", title="Save")
    if p: 
        img.convert("RGB").save(p, "PNG")
        messagebox.showinfo("Success", "Saved!")

def paparkan_pop_up_imej_label(win_outer, entries, img_label, title_text, seq_no):
    """🌟 BATCH POPUP VIEW (STANDARDIZED WITH AUTOMATIC UNLOCK ENGINE) 🌟"""
    tp = tk.Toplevel(win_outer.master)
    tp.title(f"PREVIEW - {seq_no}")
    tp.geometry("540x510+420+120") # Dimensi diseragamkan dengan modul Invois & Inner
    tp.configure(bg="#F8F9FA")
    tp.grab_set()
    
    tk.Label(tp, text=title_text, font=("Segoe UI", 11, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=12)
    
    frame_canvas_bg = tk.Frame(tp, bg="white", bd=1, relief="groove")
    frame_canvas_bg.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    
    lbl = tk.Label(frame_canvas_bg, bg="white")
    lbl.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    itk = ImageTk.PhotoImage(img_label.resize((420, 200), Image.Resampling.LANCZOS))
    lbl.config(image=itk)
    lbl.image = itk
    
    def tutup_dan_reset_borang():
        """🌟 AUTOMATIC UNLOCKER: Membuka kunci borang dan mengosongkan entri selepas popup ditutup 🌟"""
        global btn_submit_ref
        
        # 1. Buka semula kunci akses kesemua medan input
        for e in entries: 
            e.config(state="normal")
            e.delete(0, tk.END)
            
        # 2. Kembalikan fungsi dan gaya asal butang submit utama borang
        if btn_submit_ref and btn_submit_ref.winfo_exists():
            btn_submit_ref.config(state="normal", text="SUBMIT & GENERATE OUTER QR", bg="#0284C7")
            
        if entries and len(entries) > 0: 
            entries[0].focus_set()
            
        tp.destroy()
        
    f_btn = tk.Frame(tp, bg="#F8F9FA")
    f_btn.pack(side=tk.BOTTOM, pady=15, fill=tk.X, padx=20)
    
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}
    
    tk.Button(f_btn, text="🖨️ PRINT", command=lambda: cetak_qr(img_label), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    tk.Button(f_btn, text="💾 SAVE", command=lambda: simpan_qr_manual(img_label, seq_no), bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    tk.Button(f_btn, text="❌ CLOSE", command=tutup_dan_reset_borang, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

def proses_submit_outer(win_outer, entry_date, entries_inner, btn_submit_widget=None):
    """🌟 FUNGSI UTAMA SUBMIT DENGAN INTEGRASI ANTI-DUPLICATE SAFETY LOCK 🌟"""
    global btn_submit_ref
    
    # Pegang rujukan widget butang dari UI induk jika dihantar
    if btn_submit_widget:
        btn_submit_ref = btn_submit_widget

    tarikh_str = entry_date.get() if hasattr(entry_date, 'get') else str(entry_date)
    senarai_inner = [e.get().strip().upper() for e in entries_inner if e.get().strip()]
    if not senarai_inner: 
        return messagebox.showwarning("INCOMPLETE", "PLEASE SCAN OR ENTER THE SERIEL NUMBER!", parent=win_outer)

    # 1. SEKSYEN PENAPISAN BORANG SEMASA (Same Form Duplicate Filter)
    if len(senarai_inner) != len(set(senarai_inner)):
        return messagebox.showerror(
            "SAME FORM DUPLICATE ERROR", 
            "❌ FORM RE-SCAN RESTRICTION!\n\n"
            "THIS NUMBER ALREADY SCANNED!\n\n"
            "PLEASE REMOVE DUPLICATE BEFORE REGISTER.", 
            parent=win_outer
        )

    # 2. SEKSYEN SEMAKAN SEKATAN TERHADAP PANGKALAN DATA LAMA (Database Duplicate Filter)
    for idx, seq in enumerate(senarai_inner, start=1):
        outer_id = semak_adakah_inner_sudah_digunakan(seq)
        if outer_id: 
            return messagebox.showerror("DUPLICATE", f"❌ ERROR SLOT {idx}!\nSN [{seq}] ALREADY SCANNED AT OUTER BOX: {outer_id}", parent=win_outer)

    data_1 = dapatkan_maklumat_inner(senarai_inner[0])
    if not data_1: 
        return messagebox.showerror("ERROR", f" [{senarai_inner[0]}] Slot 1 NOT IN DATABASE!", parent=win_outer)
        
    _, customer_utama, drw_utama, part_utama, _ = data_1
    total_qty, data_final = 0, []
    
    for idx, seq in enumerate(senarai_inner, start=1):
        res = dapatkan_maklumat_inner(seq)
        if not res: 
            return messagebox.showerror("ERROR", f" [{seq}] SLOT {idx} NOT EXIST!", parent=win_outer)
        _, cust, _, part_no_asli, qty = res
        
        # Validasi percampuran nama pelanggan lantai kilang
        if cust != customer_utama:
            return messagebox.showerror("MIXED CUSTOMER", f"❌ !\n\n• SLOT 1: {customer_utama}\n• SLOT {idx} (WRONG): {cust} (SN: {seq})", parent=win_outer)
            
        qty_c = str(qty).upper().replace("PCS", "").strip()
        if qty_c.isdigit(): 
            total_qty += int(qty_c)
        data_final.append((part_no_asli, str(qty)))

    prefix = f"B{datetime.datetime.now().strftime('%d%m%Y')}"
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            last = cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",)).fetchone()
            run_no = int(str(last[0])[-4:]) + 1 if last else 1
            seq_outer = f"{prefix}{run_no:04d}"
            
            cursor.execute("""
                INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no) 
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (tarikh_str, customer_utama, drw_utama, part_utama, f"{total_qty} PCS", tarikh_str, ",".join(senarai_inner), "OUTER BOX", seq_outer))
            conn.commit()
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_outer)
        qr.make(fit=True)
        img_label = lod.bina_imej_gabungan_akses(qr.make_image().convert("RGB"), data_final, seq_outer)
        
        try:
            folder = os.path.join("OUTER_STICKER", datetime.datetime.now().strftime("%d-%m-%Y"), bersihkan_nama_folder(customer_utama))
            if not os.path.exists(folder): 
                os.makedirs(folder)
            img_label.convert("RGB").save(os.path.join(folder, f"OUTER_STICKER_{seq_outer}.png"), "PNG")
        except: 
            pass

        # 🌟 3. AUTOMATIC SAFETY LOCK ACTIVATE: Mengunci borang di belakang sertamerta 🌟
        if btn_submit_ref and btn_submit_ref.winfo_exists():
            btn_submit_ref.config(state="disabled", text="🔒 REGISTRATION LOCKED (COMPLETED)", bg="#64748B")
            
        for e in entries_inner:
            e.config(state="disabled")

        # Paparkan tetingkap anak untuk pratonton imej stiker
        paparkan_pop_up_imej_label(win_outer, entries_inner, img_label, "OUTER PACKING LABEL GENERATED", seq_outer)
        
    except Exception as e: 
        messagebox.showerror("Database Error", str(e), parent=win_outer)
