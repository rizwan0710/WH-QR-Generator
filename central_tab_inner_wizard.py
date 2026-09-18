import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import central_tab_inner_logic as logic
import inner_packing_logic as ipl

def buka_popup_pukal_inner_1by1(item_ditanda, root):
    """🌟 BATCH PREVIEW ENGINE (INNER BOX - FIXED CLOSE BUTTON & ASPECT RATIO) 🌟"""
    tingkap_popup = tk.Toplevel(root)
    tingkap_popup.title("INNER BOX BATCH PANEL")
    tingkap_popup.geometry("540x670+450+30")
    tingkap_popup.configure(bg="#F8F9FA")
    tingkap_popup.grab_set()

    senarai_kad_pembungkus = []
    for r in item_ditanda:
        img_kad, seq_no = logic.jana_grafik_label_dari_row(r)
        senarai_kad_pembungkus.append((img_kad, seq_no))

    indeks_halaman = 0
    total_label = len(senarai_kad_pembungkus)

    lbl_header = tk.Label(tingkap_popup, text="", font=("Segoe UI", 10, "bold"), fg="#2E7D32", bg="#F8F9FA")
    lbl_header.pack(pady=12)

    frame_canvas_bg = tk.Frame(tingkap_popup, bg="white", bd=1, relief="groove")
    frame_canvas_bg.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    
    label_gambar = tk.Label(frame_canvas_bg, bg="white")
    label_gambar.pack(padx=15, pady=15, expand=True, fill=tk.BOTH)

    def kemaskini_paparan_selak():
        if total_label == 0: return
        img_kad, seq_no = senarai_kad_pembungkus[indeks_halaman]
        # 🌟 DIKEMASKINI: Menyeragamkan format teks header (LABEL PREVIEW) mengikut format Invoice
        lbl_header.config(text=f"LABEL PREVIEW ({seq_no})  |  BATCH COUNTER: {indeks_halaman + 1}/{total_label}")
        
        lebar_had = 310
        tinggi_had = 420
        lebar_asal, tinggi_asal = img_kad.size
        
        nisbah = min(lebar_had / lebar_asal, tinggi_had / tinggi_asal)
        lebar_baru = int(lebar_asal * nisbah)
        tinggi_baru = int(tinggi_asal * nisbah)
        
        img_visual = img_kad.resize((lebar_baru, tinggi_baru), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_visual)
        label_gambar.config(image=img_tk)
        label_gambar.image = img_tk 
        
        if total_label > 1:
            btn_prev.config(state="normal" if indeks_halaman > 0 else "disabled")
            btn_next.config(state="normal" if indeks_halaman < total_label - 1 else "disabled")

    def halaman_ke_kiri():
        nonlocal indeks_halaman
        if indeks_halaman > 0:
            indeks_halaman -= 1
            kemaskini_paparan_selak()

    def halaman_ke_kanan():
        nonlocal indeks_halaman
        if indeks_halaman < total_label - 1:
            indeks_halaman += 1
            kemaskini_paparan_selak()

    def cetak_semua_pukal():
        if messagebox.askyesno("CONFIRMATION", f"Print ALL {total_label} label?", parent=tingkap_popup):
            for img_kad, _ in senarai_kad_pembungkus: 
                ipl.cetak_qr(img_kad)
            messagebox.showinfo("SUCCESS", "All labels are sent to the printer.!", parent=tingkap_popup)

    def simpan_semua_pukal():
        folder_tujuan = filedialog.askdirectory(title="CHOOSE FOLDER", parent=tingkap_popup)
        if folder_tujuan:
            for img_kad, seq_no in senarai_kad_pembungkus:
                img_kad.convert("RGB").save(os.path.join(folder_tujuan, f"INNER_{seq_no.replace('/', '-')}.png"), "PNG")
            messagebox.showinfo("SUCCESS", "ALL Label successfully saved!", parent=tingkap_popup)

    def simpan_tunggal_sahaja():
        img_kad, seq_no = senarai_kad_pembungkus[indeks_halaman]
        ipl.simpan_qr_manual(img_kad, seq_no)

    # ─── 1. BAR NAVIGASI (Hanya pack jika data > 1) ───
    frame_nav = tk.Frame(tingkap_popup, bg="#F8F9FA")
    btn_prev = tk.Button(frame_nav, text="◀ PREV", command=halaman_ke_kiri, bg="#2C3E50", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_prev.pack(side=tk.LEFT, padx=8)
    btn_next = tk.Button(frame_nav, text="NEXT ▶", command=halaman_ke_kanan, bg="#2C3E50", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_next.pack(side=tk.LEFT, padx=8)

    if total_label > 1:
        frame_nav.pack(pady=5)

    # ─── 2. ACTION BAR KAWALAN FLAT STYLE SERAGAM (INVOICE VERSION) ───
    frame_btn = tk.Frame(tingkap_popup, bg="#F8F9FA")
    frame_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}
    
    if total_label == 1:
        # 🌟 SERAGAM (1 DATA): Menggunakan kod warna, teks, dan susunan ikon baharu
        tk.Button(frame_btn, text="📥  PRINT CURRENT", command=lambda: ipl.cetak_qr(senarai_kad_pembungkus[0][0]), bg="#2ECC71", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="💾  SAVE ALL", command=simpan_tunggal_sahaja, bg="#E67E22", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="✖  CLOSE", command=tingkap_popup.destroy, bg="#2C3E50", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)
    else:
        # 🌟 SERAGAM (BANYAK DATA): Diselaraskan tepat mengikut barisan 4 butang utama Invoice Panel
        tk.Button(frame_btn, text="📥  PRINT CURRENT", command=lambda: ipl.cetak_qr(senarai_kad_pembungkus[indeks_halaman][0]), bg="#2ECC71", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="📥  PRINT ALL", command=cetak_semua_pukal, bg="#27AE60", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="💾  SAVE ALL", command=simpan_semua_pukal, bg="#E67E22", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="✖  CLOSE", command=tingkap_popup.destroy, bg="#2C3E50", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)

    kemaskini_paparan_selak()
