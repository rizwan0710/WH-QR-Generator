import sqlite3
import re
import sys  
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import qrcode
from datetime import datetime
import label_outer_designer as lod
import form_outer_packing_logic as fopl
import database_manager as dbm  # 🌟 Integrasi Pengurus Pangkalan Data Pusat NAS 🌟

def dapatkan_qty_inner_live(inner_seq):
    """Mengambil kuantiti stiker murni dari database pusat NAS secara live."""
    try:
        # ✅ DIBAIKI: Menggunakan sambungan berpusat dbm.get_db_connection()
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError: pass
                
            cursor.execute(f"SELECT quantity FROM rekod_qr WHERE UPPER(TRIM({lajur_seq})) = ?", (str(inner_seq).strip().upper(),))
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
    except Exception as e: 
        print(f"Error live quantity fetch: {e}")
    return "100 PCS" # Fallback standard bungkusan inner stiker WP anda

def proses_pratonton_outer(baris_data, root):
    """Membina tetingkap pop-up pratinjau re-print visual grafik bagi rekod Outer Box (VERSI NAS PUSAT)."""
    try:
        # Ekstrak elemen data baris pertama dari list
        data_flat = list(baris_data[0]) if isinstance(baris_data, (list, tuple)) and len(baris_data) > 0 else list(baris_data)
        if data_flat and str(data_flat[0]) in ("☐", "☑"):
            data_flat = data_flat[1:]
            
        # 🛠️ SEPADAN LAJUR JADUAL: Mengikut susunan tepat 9 lajur central database utama
        # [0:ID, 1:Date, 2:Customer, 3:Quantity, 4:Box Type, 5:Linked Inners, 6:Operation, 7:Outer Sequence]
        qty_text_live  = str(data_flat[3]).replace('PCS','').strip()  # Lajur Box Quantity (Contoh: 395)
        raw_inner_text = str(data_flat[5]).strip()                    # Lajur Linked Inners (WP)
        seq_outer      = str(data_flat[7]).strip()                    # Lajur Outer Sequence (B%)
        cust_name      = str(data_flat[2]).strip()                    # Lajur Customer Name
    except Exception as e_map:
        messagebox.showerror("ERROR MAP", f"The column layout of the outer database does not match:\n{str(e_map)}")
        return

    if not seq_outer or seq_outer == "" or seq_outer.startswith("☐"):
        messagebox.showerror("ERROR DATA", "S/N NOT VALID!")
        return

    tingkap_preview = tk.Toplevel(root)
    tingkap_preview.title(f"REPRINT PREVIEW PANEL - {seq_outer}")
    tingkap_preview.geometry("480x420+450+100")
    tingkap_preview.configure(bg="#F8F9FA")
    tingkap_preview.grab_set()

    tk.Label(tingkap_preview, text="OUTER LABEL SINGLE PREVIEW", font=("Segoe UI", 12, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=(15, 2))
    tk.Label(tingkap_preview, text=f"Sequence: {seq_outer}", font=("Segoe UI", 9, "italic"), fg="#64748B", bg="#F8F9FA").pack(pady=(0, 10))

    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(seq_outer)
    qr.make(fit=True)
    img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    senarai_inner_bersih = [s.strip() for s in re.split(r'[,\n]', raw_inner_text) if s.strip() and s.strip() != "None"]
    
    data_gabungan_final = []
    for s_clean in senarai_inner_bersih:
        if s_clean:
            # Mengambil nilai kuantiti live murni untuk setiap kod WP langsung dari database pusat
            info_inner = fopl.dapatkan_maklumat_inner(s_clean)
            if isinstance(info_inner, dict) and "qty" in info_inner:
                q_val = info_inner.get("qty", "100 PCS")
            else:
                q_val = dapatkan_qty_inner_live(s_clean)
                
            data_gabungan_final.append((s_clean, f"{str(q_val).upper().replace('PCS','').strip()} PCS"))

    # ✅ DIBAIKI: Menggunakan enjin lakaran grafik designer rasmi lod.create_outer_label_image
    img_gabung = lod.create_outer_label_image(
        seq_outer, "OHTA PRECISION", cust_name, "COMBINED", "CONSOLIDATED", 
        f"{qty_text_live} PCS", "M/C-01", datetime.now().strftime("%d/%m/%Y"), img_qr_mentah, data_gabungan_final
    )

    frame_canvas = tk.Frame(tingkap_preview, bg="white", bd=1, relief="groove")
    frame_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    lbl_visual = tk.Label(frame_canvas, bg="white")
    lbl_visual.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    img_resize = img_gabung.resize((400, 190), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img_resize)
    lbl_visual.config(image=img_tk)
    lbl_visual.image = img_tk

    frame_btn = tk.Frame(tingkap_preview, bg="#F8F9FA")
    frame_btn.pack(side=tk.BOTTOM, pady=15, fill=tk.X, padx=20)

    btn_style = {"font": ("Segoe UI", 10, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

    # Pautan butang aksi kawalan yang selamat ke fungsi utama fopl
    tk.Button(frame_btn, text="🖨️ PRINT", command=lambda: fopl.cetak_qr(img_gabung), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
    tk.Button(frame_btn, text="💾 SAVE", command=lambda: fopl.simpan_qr_manual_outer_single(img_gabung, seq_outer) if hasattr(fopl, 'simpan_qr_manual_outer_single') else fopl.simpan_qr_manual(img_gabung, seq_outer), bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_preview.destroy, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
