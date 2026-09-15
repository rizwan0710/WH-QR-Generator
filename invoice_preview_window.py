# invoice_preview_window.py - FULL INTEGRATED RESOLUTION-SAFE POPUP ENGINE
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import ImageTk, Image
import database_batch_preview
import os

def buka_popup_individual_1by1(parent, senarai_kad_tunggal, inv_no=""):
    """
    🌟 ENGINE PREVIEW DINAMIK INVOICE (FIXED: ANTI-DISTORTION QR PREVIEW) 🌟
    Kalis herot piksel: Menjaga kualiti imej asal semasa cetakan / simpanan fail.
    """
    if not senarai_kad_tunggal:
        return

    # 🛠️ Ekstrak elemen data secara selamat daripada tuple (stk, pg)
    normalized_images = []
    normalized_paging = []
    
    for item in senarai_kad_tunggal:
        if isinstance(item, (list, tuple)) and len(item) > 0:
            # item[0] = objek imej asal (stk), item[1] = teks paging (pg)
            normalized_images.append(item[0]) 
            normalized_paging.append(item[1] if len(item) > 1 else "BOX 1/1")
        else:
            normalized_images.append(item)
            normalized_paging.append("BOX 1/1")

    tingkap_popup = tk.Toplevel(parent)
    tingkap_popup.title(f"INVOICE DATABASE PANEL - {inv_no}")
    tingkap_popup.geometry("560x540+420+120") # 🌟 FIXED: Menggunakan 'x' untuk format lebar x tinggi yang sah
    tingkap_popup.configure(bg="#F8F9FA")
    tingkap_popup.grab_set()

    indeks_halaman = 0
    total_label = len(normalized_images)

    lbl_header = tk.Label(tingkap_popup, text="", font=("Segoe UI", 10, "bold"), fg="#10B981", bg="#F8F9FA")
    lbl_header.pack(pady=12)

    frame_canvas_bg = tk.Frame(tingkap_popup, bg="white", bd=1, relief="groove")
    frame_canvas_bg.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    
    label_gambar = tk.Label(frame_canvas_bg, bg="white")
    label_gambar.pack(padx=15, pady=15, expand=True, fill=tk.BOTH)

    def kemaskini_paparan_selak():
        idx = indeks_halaman
        img_kad = normalized_images[idx]
        box_paging = normalized_paging[idx]
        
        lbl_header.config(text=f"LABEL PREVIEW ({box_paging})  |  BATCH COUNTER: {idx + 1}/{total_label}")
        
        # 🌟 FIX KEKAL NISBAH (420x210): Mengekalkan nisbah aspek 2:1 agar petak grid QR tidak hancur atau bertindih
        img_visual = img_kad.resize((420, 210), Image.Resampling.LANCZOS)
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

    def cetak_halaman_tunggal():
        """🖨️ Mencetak imej menggunakan fail objek asal beresolusi tinggi (Sharpness Preserved)"""
        try:
            img_clean = normalized_images[indeks_halaman]
            database_batch_preview.laksanakan_windows_photo_wizard_tunggal([img_clean])
        except Exception as e:
            messagebox.showerror("PRINT ERROR", f"Failed to print current label:\n{str(e)}", parent=tingkap_popup)

    def cetak_semua_pukal():
        """🖨️ Mencetak kesemua stiker bersiri secara pukal"""
        if messagebox.askyesno("CONFIRMATION MESSAGE", f"PROCEED WITH PRINT ALL {total_label} LABELS?", parent=tingkap_popup):
            try:
                database_batch_preview.laksanakan_windows_photo_wizard_tunggal(normalized_images)
            except Exception as e:
                messagebox.showerror("PRINT ERROR", f"Failed to print all labels:\n{str(e)}", parent=tingkap_popup)

    def simpan_halaman_tunggal():
        """💾 Menyimpan stiker aktif tunggal tanpa herot piksel skrin"""
        try:
            img_kad = normalized_images[indeks_halaman]
            box_paging = normalized_paging[indeks_halaman]
            
            paging_bersih = str(box_paging).replace("/", "-").replace(" ", "_").upper()
            path_fail = filedialog.asksaveasfilename(
                initialfile=f"LABEL_INVOICE_{inv_no}_{paging_bersih}.png", 
                defaultextension=".png", 
                filetypes=[("PNG Image", "*.png")],
                title="SAVE LABEL GRAPHIC",
                parent=tingkap_popup
            )
            if path_fail:
                img_kad.convert("RGB").save(path_fail, "PNG")
                messagebox.showinfo("COMPLETE", "LABEL SUCCESSFULLY SAVED!", parent=tingkap_popup)
        except Exception as e:
            messagebox.showerror("SAVE ERROR", str(e), parent=tingkap_popup)

    def simpan_semua_pukal():
        """💾 Menyimpan keseluruhan imej stiker pukal dalam satu folder"""
        folder_tujuan = filedialog.askdirectory(title="CHOOSE FOLDER TO SAVE ALL IMAGES", parent=tingkap_popup)
        if folder_tujuan:
            try:
                for idx, img_item in enumerate(normalized_images):
                    box_paging = normalized_paging[idx]
                    paging_bersih = str(box_paging).replace("/", "-").replace(" ", "_").upper()
                    img_item.convert("RGB").save(os.path.join(folder_tujuan, f"LABEL_INVOICE_{inv_no}_{paging_bersih}.png"), "PNG")
                messagebox.showinfo("COMPLETE", f"ALL {total_label} LABELS SUCCESSFULLY SAVED!", parent=tingkap_popup)
            except Exception as e:
                messagebox.showerror("SAVE ERROR", str(e), parent=tingkap_popup)

    # ─── NAVIGATION PANEL ───
    frame_nav = tk.Frame(tingkap_popup, bg="#F8F9FA")
    btn_prev = tk.Button(frame_nav, text="◀ PREV", command=halaman_ke_kiri, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_prev.pack(side=tk.LEFT, padx=8)
    btn_next = tk.Button(frame_nav, text="NEXT ▶", command=halaman_ke_kanan, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_next.pack(side=tk.LEFT, padx=8)

    if total_label > 1:
        frame_nav.pack(pady=5)

    # ─── ACTION FOOTER PANEL ───
    frame_btn = tk.Frame(tingkap_popup, bg="#F8F9FA")
    frame_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

    if total_label == 1:
        tk.Button(frame_btn, text="🖨️ PRINT", command=cetak_halaman_tunggal, bg="#2ECC71", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="💾 SAVE", command=simpan_halaman_tunggal, bg="#E65100", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_popup.destroy, bg="#34495E", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)
    else:
        tk.Button(frame_btn, text="🖨️ PRINT CURRENT", command=cetak_halaman_tunggal, bg="#2ECC71", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="🖨️ PRINT ALL", command=cetak_semua_pukal, bg="#10B981", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="💾 SAVE ALL", command=simpan_semua_pukal, bg="#E65100", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_popup.destroy, bg="#34495E", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)

    kemaskini_paparan_selak()
