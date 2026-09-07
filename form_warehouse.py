import sqlite3
import os
import math
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import ImageTk, Image
import qrcode
import label_designer as ld
import inner_packing_logic as ipl
import database_batch_preview  # Menghubungkan enjin letusan 1 dialog pencetak
from datetime import datetime

def proses_submit_data_pukal(win_wh, kamus):
    """Memproses kemasukan borang produksi dan menjana siri WP% automatik secara pukal."""
    data = {k: v.get().upper().strip() if hasattr(v, 'get') else v for k, v in kamus.items()}
    if not all(data.values()): 
        return messagebox.showwarning("INCOMPLETE", "PLEASE FILL ALL FIELDS!", parent=win_wh)

    total_qty = int("".join(filter(str.isdigit, data["qty"])))
    pck_qty = int("".join(filter(str.isdigit, data["packing_qty"])))
    
    if total_qty <= 0 or pck_qty <= 0:
        return messagebox.showerror("ERROR", "QUANTITY VALUES MUST BE GREATER THAN 0!", parent=win_wh)

    pecahan_qty = [pck_qty] * (total_qty // pck_qty) + ([total_qty % pck_qty] if total_qty % pck_qty else [])
    tarikh_pola, senarai_kad = datetime.now().strftime("%y%m%d"), []
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            for idx, qty in enumerate(pecahan_qty, start=1):
                cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"WP{tarikh_pola}%",))
                max_r = cursor.fetchone()
                
                # 🌟 KOREKSI UTAMA TUPLE INDEXING: Mengunci pembacaan rentetan siri 'WP' secara tepat gred industri 🌟
                if max_r and max_r[0]:
                    string_siri = str(max_r[0]).strip()
                    bil = int(string_siri[-4:]) + 1
                else:
                    bil = 1
                    
                seq = f"WP{tarikh_pola}{bil:04d}"
                
                cursor.execute("""
                    INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (kamus["date"].get(), data["customer"], data["drawing"], data["part"], f"{qty} PCS", data["mfg"], data["machine"], data["lot"], seq))
                
                qr = qrcode.QRCode(version=1, box_size=10, border=1)
                qr.add_data(seq)
                qr.make(fit=True)
                img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
                
                img = ld.bina_imej_gabungan(img_qr, kamus["date"].get(), data["drawing"], data["part"], f"{qty} PCS", data["mfg"], data["machine"], seq, data["customer"])
                senarai_kad.append((img, seq))
                
                path_sub = os.path.join("INNER_STICKER", datetime.now().strftime("%d-%m-%Y"), "".join([c for c in data["customer"] if c.isalnum() or c in " _-"]))
                if not os.path.exists(path_sub): 
                    os.makedirs(path_sub)
                img.save(os.path.join(path_sub, f"INNER_STICKER_{seq}.png"), "PNG")
                
            try:
                cursor.execute("SELECT DISTINCT TRIM(customer) FROM rekod_qr WHERE customer IS NOT NULL AND customer != ''")
                kamus["customer"]['values'] = sorted(list(set([row[0].upper() for row in cursor.fetchall() if row[0]])))
            except Exception: 
                pass
            
            conn.commit()

        buka_popup_pukal_slider_inner(win_wh, senarai_kad)
    except Exception as e:
        messagebox.showerror("DATABASE ERROR", f"FAILED TO PROCESS DATA:\n{str(e)}", parent=win_wh)

def buka_popup_pukal_slider_inner(parent, senarai_kad):
    """Enjin meluncur dinamik dengan pengiraan aspek ratio kod QR asli kilang."""
    win = tk.Toplevel(parent)
    win.title("PRODUCTION INNER BATCH STICKER")
    win.geometry("540x670+450+30")
    win.configure(bg="#F8F9FA")
    win.grab_set()
    
    indeks_halaman = 0
    total_label = len(senarai_kad)

    lbl = tk.Label(win, text="", font=("Segoe UI", 10, "bold"), fg="#2E7D32", bg="#F8F9FA")
    lbl.pack(pady=12)
    
    fr_bg = tk.Frame(win, bg="white", bd=1, relief="groove")
    fr_bg.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    
    lbl_img = tk.Label(fr_bg, bg="white")
    lbl_img.pack(padx=15, pady=15, expand=True, fill=tk.BOTH)

    def kemaskini_selak():
        nonlocal indeks_halaman
        img, seq = senarai_kad[indeks_halaman]
        lbl.config(text=f"STICKER GENERATED ({seq})  |  BATCH: {indeks_halaman + 1}/{total_label}")
        
        lebar_had, tinggi_had = 340, 440
        img_visual = img.resize((lebar_had, tinggi_had), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_visual)
        lbl_img.config(image=img_tk)
        lbl_img.image = img_tk
        
        if total_label > 1:
            btn_prev.config(state="normal" if indeks_halaman > 0 else "disabled")
            btn_next.config(state="normal" if indeks_halaman < total_label - 1 else "disabled")

    def halaman_ke_kiri():
        nonlocal indeks_halaman
        if indeks_halaman > 0:
            indeks_halaman -= 1
            kemaskini_selak()

    def halaman_ke_kanan():
        nonlocal indeks_halaman
        if indeks_halaman < total_label - 1:
            indeks_halaman += 1
            kemaskini_selak()

    def simpan_semua_pukal():
        folder_tujuan = filedialog.askdirectory(title="Select Save Folder", parent=win)
        if folder_tujuan:
            for img_kad, seq_no in senarai_kad:
                img_kad.convert("RGB").save(os.path.join(folder_tujuan, f"INNER_STICKER_{seq_no}.png"), "PNG")
            messagebox.showinfo("Success", "All batch stickers saved successfully!", parent=win)

    def simpan_tunggal_sahaja():
        img_kad, seq_no = senarai_kad[indeks_halaman]
        ipl.simpan_qr_manual(img_kad, seq_no)

    # Baris Navigasi Selak Halaman
    fr_nav = tk.Frame(win, bg="#F8F9FA")
    btn_prev = tk.Button(fr_nav, text="◀ PREV", command=halaman_ke_kiri, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_next = tk.Button(fr_nav, text="NEXT ▶", command=halaman_ke_kanan, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    
    if total_label > 1: 
        fr_nav.pack(pady=5)
        btn_prev.pack(side=tk.LEFT, padx=8)
        btn_next.pack(side=tk.LEFT, padx=8)

    # Barisan Butang Kawalan Output Bawah Flat Style Seragam (English Labels)
    fr_btn = tk.Frame(win, bg="#F8F9FA")
    fr_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    b_st = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}
    
    if total_label == 1:
        # Pautan murni imej RAM tunggal terus ke enjin letusan dialog gambar Windows Explorer
        tk.Button(fr_btn, text="🖨️ PRINT ", command=lambda: database_batch_preview.laksanakan_windows_photo_wizard_tunggal([senarai_kad[0][0]]), bg="#22C55E", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(fr_btn, text="💾 SAVE ", command=simpan_tunggal_sahaja, bg="#F59E0B", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    else:
        # Pautan murni senarai imej batch RAM terus ke enjin letusan dialog gambar Windows Explorer
        tk.Button(fr_btn, text="📦 PRINT CURRENT", command=lambda: database_batch_preview.laksanakan_windows_photo_wizard_tunggal([senarai_kad[indeks_halaman][0]]), bg="#22C55E", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(fr_btn, text="🔥 PRINT ALL", command=lambda: database_batch_preview.laksanakan_windows_photo_wizard_tunggal([k[0] for k in senarai_kad]), bg="#10B981", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(fr_btn, text="💾 SAVE ALL", command=simpan_semua_pukal, bg="#EA580C", **b_st).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
    tk.Button(fr_btn, text="❌ CLOSE", command=win.destroy, bg="#374151", **b_st).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)
    
    kemaskini_selak()
