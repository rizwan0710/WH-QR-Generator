import sqlite3
import re
import sys  # ─── FIX MUTTAMAD: Mengimport modul sys luaran ───
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import qrcode
import label_outer_designer as lod
import form_outer_packing_logic as fopl

def dapatkan_qty_inner_lokal(inner_seq):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM rekod_qr WHERE sequence_no = ?", (inner_seq,))
            row = cursor.fetchone()
            if row: return str(row[0])
    except sqlite3.Error: pass
    return "0"

def proses_pratonton_outer(baris_data, root):
    """Membina tetingkap pop-up pratinjau re-print visual grafik bagi rekod Outer Box (STANDARDIZED)."""
    try:
        seq_outer = str(baris_data[0][8]).strip()       
        raw_inner_text = str(baris_data[0][6]).strip()  
    except IndexError:
        messagebox.showerror("ERROR MAP", "THE COLUMN LAYOUT OF THE OUTER DATABASE DOES NOT MATCH.!")
        return

    if not seq_outer or seq_outer == "" or seq_outer.startswith("☐"):
        messagebox.showerror("ERROR DATA", "S/N NOT VALID!")
        return

    tingkap_preview = tk.Toplevel(root)
    tingkap_preview.title(f"REPRINT PREVIEW PANEL - {seq_outer}")
    tingkap_preview.geometry("480x420+450+100")
    tingkap_preview.configure(bg="#F8F9FA")
    tingkap_preview.grab_set()

    tk.Label(tingkap_preview, text=f"OUTER LABEL SINGLE PREVIEW", font=("Segoe UI", 12, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=(15, 2))
    tk.Label(tingkap_preview, text=f"Sequence: {seq_outer}", font=("Segoe UI", 9, "italic"), fg="#64748B", bg="#F8F9FA").pack(pady=(0, 10))

    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(seq_outer)
    qr.make(fit=True)
    img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    senarai_inner_bersih = [s.strip() for s in re.split(r'[,\n]', raw_inner_text) if s.strip() and s.strip() != "None"]
    
    data_gabungan_final = []
    for s_clean in senarai_inner_bersih:
        if s_clean:
            q_val = dapatkan_qty_inner_lokal(s_clean)
            data_gabungan_final.append((s_clean, q_val))

    img_gabung = lod.bina_imej_gabungan_akses(img_qr_mentah, data_gabungan_final, seq_outer)

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

    # ─── FIX: Menukar fopl.simpan_qr_manual kepada fopl.simpan_qr_manual_lokal ───
    tk.Button(frame_btn, text="🖨️ PRINT", command=lambda: fopl.cetak_qr(img_gabung), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
    tk.Button(frame_btn, text="💾 SAVE", command=lambda: fopl.simpan_qr_manual_lokal(img_gabung, seq_outer), bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_preview.destroy, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
