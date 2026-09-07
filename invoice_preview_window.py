import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import ImageTk, Image
import invoice_packing_logic as ipl
import os

def buka_popup_individual_1by1(parent, senarai_kad_tunggal, inv_no):
    """
    🌟 ENGINE PREVIEW DINAMIK INVOICE (MUTTAMAD & STANDARDIZED UI) 🌟
    Jika 1 data: Keluar 3 butang bersih (PRINT, SAVE, CLOSE) tanpa navigasi.
    Jika >1 data: Keluar 5 butang batch beserta butang selak PREVIOUS/NEXT.
    """
    if not senarai_kad_tunggal:
        return

    tingkap_popup = tk.Toplevel(parent)
    tingkap_popup.title(f"INVOICE BATCH PANEL - {inv_no}")
    tingkap_popup.geometry("540x510+420+120")
    tingkap_popup.configure(bg="#F8F9FA")
    tingkap_popup.grab_set()

    indeks_halaman = 0
    senarai_kad_pembungkus_lokal = senarai_kad_tunggal
    total_label = len(senarai_kad_pembungkus_lokal)

    lbl_header = tk.Label(tingkap_popup, text="", font=("Segoe UI", 10, "bold"), fg="#EA580C", bg="#F8F9FA")
    lbl_header.pack(pady=12)

    frame_canvas_bg = tk.Frame(tingkap_popup, bg="white", bd=1, relief="groove")
    frame_canvas_bg.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    
    label_gambar = tk.Label(frame_canvas_bg, bg="white")
    label_gambar.pack(padx=15, pady=15, expand=True, fill=tk.BOTH)

    def kemaskini_paparan_selak():
        idx = indeks_halaman
        img_kad, box_paging = senarai_kad_pembungkus_lokal[idx]
        
        lbl_header.config(text=f"LABEL PREVIEW ({box_paging})  |  BATCH COUNTER: {idx + 1}/{total_label}")
        
        img_visual = img_kad.resize((420, 200), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_visual)
        label_gambar.config(image=img_tk)
        label_gambar.image = img_tk 
        
        if total_label > 1:
            btn_prev.config(state="normal" if idx > 0 else "disabled")
            btn_next.config(state="normal" if idx < total_label - 1 else "disabled")

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
        if messagebox.askyesno("CONFIRMATION MESSAGE", f"PROCEED WITH PRINT ALL {total_label} THIS LABEL?", parent=tingkap_popup):
            for img_kad, _ in senarai_kad_pembungkus_lokal:
                ipl.cetak_kad_tunggal(img_kad)
            messagebox.showinfo("SUCCESS", f"ALL {total_label} LABEL MANAGE TO PRINT !", parent=tingkap_popup)

    def simpan_semua_pukal():
        folder_tujuan = filedialog.askdirectory(title="CHOOSE FOLDER TO SAVE ALL", parent=tingkap_popup)
        if folder_tujuan:
            for img_kad, box_paging in senarai_kad_pembungkus_lokal:
                paging_bersih = str(box_paging).replace("/", "-").replace(" ", "_").upper()
                img_kad.save(os.path.join(folder_tujuan, f"LABEL_INVOICE_{inv_no}_{paging_bersih}.png"), "PNG")
            messagebox.showinfo("COMPLETE", f"ALL {total_label} LABEL SUCCESSFULLY SAVED!", parent=tingkap_popup)

    def simpan_tunggal_sahaja():
        img_kad, box_paging = senarai_kad_pembungkus_lokal[indeks_halaman]
        paging_bersih = str(box_paging).replace("/", "-").replace(" ", "_").upper()
        path_fail = filedialog.asksaveasfilename(
            initialfile=f"LABEL_INVOICE_{inv_no}_{paging_bersih}.png", 
            defaultextension=".png", 
            filetypes=[("PNG Image", "*.png")],
            title="SIMPAN GRAFIK LABEL"
        )
        if path_fail:
            img_kad.save(path_fail, "PNG")
            messagebox.showinfo("COMPLETE", "LABEL SUCCESSFULLY SAVED!", parent=tingkap_popup)

    # ─── 1. BAR NAVIGASI SELAK HALAMAN STANDARDIZED (Hanya pack jika data > 1) ───
    frame_nav = tk.Frame(tingkap_popup, bg="#F8F9FA")
    btn_prev = tk.Button(frame_nav, text="◀ PREVIOUS", command=halaman_ke_kiri, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_prev.pack(side=tk.LEFT, padx=8)
    btn_next = tk.Button(frame_nav, text="NEXT ▶", command=halaman_ke_kanan, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_next.pack(side=tk.LEFT, padx=8)

    if total_label > 1:
        frame_nav.pack(pady=5)

    # ─── 2. BARIS BUTANG KAWALAN FLAT STYLE SERAGAM (DINAMIK) ───
    frame_btn = tk.Frame(tingkap_popup, bg="#F8F9FA")
    frame_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

    if total_label == 1:
        # 🌟 FIXED MEMORY COUPLING: Memanggil flat array indeks [0][0] dengan selamat ke objek imej murni
        tk.Button(frame_btn, text="🖨️ PRINT ", command=lambda: ipl.cetak_kad_tunggal(senarai_kad_pembungkus_lokal[0][0]), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="💾 SAVE ", command=simpan_tunggal_sahaja, bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_popup.destroy, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)
    else:
        tk.Button(frame_btn, text="🖨️ PRINT CURRENT", command=lambda: ipl.cetak_kad_tunggal(senarai_kad_pembungkus_lokal[indeks_halaman][0]), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(frame_btn, text="🔥 PRINT ALL", command=cetak_semua_pukal, bg="#10B981", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(frame_btn, text="💾 SAVE CURRENT", command=simpan_tunggal_sahaja, bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(frame_btn, text="📦 SAVE ALL", command=simpan_semua_pukal, bg="#EA580C", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_popup.destroy, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

    kemaskini_paparan_selak()
