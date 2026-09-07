import os, tkinter as tk, sqlite3, qrcode, re
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import label_invoice_designer as design_logic  
import invoice_packing_logic as ipl  

def buka_popup_pukal_invoice_1by1(jadual, root):
    """🌟 SMART AUTO-FOCUS ENGINE: Automatically slides to the highlighted box page status on load 🌟"""
    item_terpilih = jadual.selection()
    if not item_terpilih:
        for item_id in jadual.get_children():
            if "☑" in str(jadual.set(item_id, "Select")):
                item_terpilih = (item_id,)
                break

    if not item_terpilih:
        messagebox.showwarning("Peringatan", "Sila pilih atau tanda ☑ rekod Invoice!", parent=root)
        return

    target_id = item_terpilih

    # Ambil nilai kuantiti, status halaman murni, dan nombor siri unik baris yang sedang diklik oleh operator
    live_treeview_qty = str(jadual.set(target_id, "Quantity")).upper().replace("PCS", "").strip()
    live_page_status  = str(jadual.set(target_id, "Page Status")).upper().strip() # Cth: "BOX 4/4"
    live_sequence_no  = str(jadual.set(target_id, "Invoice Sequence No")).strip() # Cth: "INV2609040004"

    inv_no_rujukan = str(jadual.set(target_id, "Invoice No")).strip().replace("INV:", "").strip()
    so_no_rujukan  = str(jadual.set(target_id, "SO No")).strip().replace("SO:", "").strip()
    cust_val       = str(jadual.set(target_id, "Customer")).strip()
    
    semua_batch = []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            # Tarik kesemua 4 baris rekod kumpulan invois ini dari SQLite
            query = """
                SELECT machine, sequence_no, lotcard_no 
                FROM rekod_qr 
                WHERE drawing_no LIKE ? AND part_no LIKE ? AND sequence_no LIKE 'INV%'
                ORDER BY sequence_no ASC
            """
            cursor.execute(query, (f"%{inv_no_rujukan}%", f"%{so_no_rujukan}%"))
            semua_batch = cursor.fetchall()
    except Exception as e:
        messagebox.showerror("DATABASE ERROR", str(e), parent=root)
        return

    if not semua_batch:
        messagebox.showwarning("REMINDER", f"Tiada data ditemui untuk Invoice: {inv_no_rujukan}", parent=root)
        return

    senarai_kad_pembungkus = []
    total_kotak = len(semua_batch)
    
    # 🌟 ENJIN DETEKSI INDEKS HALAMAN: Sediakan pemutus litar fokus halaman permulaan dinamik
    target_start_index = 0

    for idx, (mac_val, seq_val, lot_val) in enumerate(semua_batch):
        # Gunakan format teks paging seragam gred premium
        teks_paging_betul = f"BOX {idx + 1}/{total_kotak}"
        
        # SINKRONISASI COUPLING: Jika nombor siri atau teks status sepadan dengan baris jadual, kunci indeksnya!
        if str(seq_val).strip() == live_sequence_no or teks_paging_betul == live_page_status:
            target_start_index = idx
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_val)
        qr.make(fit=True)
        img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        
        img_kad = design_logic.bina_imej_invoice(img_qr_mentah, inv_no_rujukan, so_no_rujukan, mac_val, f"{live_treeview_qty} PCS", seq_val, teks_paging_betul, cust_val)
        senarai_kad_pembungkus.append((img_kad, teks_paging_betul, inv_no_rujukan))

    tingkap_popup = tk.Toplevel(root)
    tingkap_popup.title(f"INVOICE BATCH PANEL - {inv_no_rujukan}")
    tingkap_popup.geometry("560x540+420+120") 
    tingkap_popup.configure(bg="#F8F9FA")
    tingkap_popup.grab_set()

    # 🌟 SUNTIKAN FOCUS: Tetapkan halaman permulaan mengikut indeks baris yang dipilih oleh operator (cth: indeks ke-3 untuk halaman 4/4)
    indeks_halaman = target_start_index
    total_label = len(senarai_kad_pembungkus)

    lbl_header = tk.Label(tingkap_popup, text="", font=("Segoe UI", 10, "bold"), fg="#EA580C", bg="#F8F9FA")
    lbl_header.pack(pady=12)

    frame_canvas_bg = tk.Frame(tingkap_popup, bg="white", bd=1, relief="groove")
    frame_canvas_bg.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    label_gambar = tk.Label(frame_canvas_bg, bg="white")
    label_gambar.pack(padx=15, pady=15, expand=True, fill=tk.BOTH)

    def kemaskini_paparan_selak():
        if total_label == 0: return
        img_kad, teks_paging_betul, inv_no = senarai_kad_pembungkus[indeks_halaman]
        lbl_header.config(text=f"INVOICE PREVIEW ({inv_no} - {teks_paging_betul})  |  BATCH COUNTER: {indeks_halaman + 1}/{total_label}")
        
        img_visual = img_kad.resize((420, 230), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_visual)
        label_gambar.config(image=img_tk)
        label_gambar.image = img_tk 
        
        if total_label > 1:
            btn_prev.config(state="normal" if indeks_halaman > 0 else "disabled")
            btn_next.config(state="normal" if indeks_halaman < total_label - 1 else "disabled")

    def halaman_ke_kiri():
        nonlocal indeks_halaman
        if indeks_halaman > 0: indeks_halaman -= 1; kemaskini_paparan_selak()
        
    def halaman_ke_kanan():
        nonlocal indeks_halaman
        if indeks_halaman < total_label - 1: indeks_halaman += 1; kemaskini_paparan_selak()

    frame_nav = tk.Frame(tingkap_popup, bg="#F8F9FA")
    btn_prev = tk.Button(frame_nav, text="◀ PREVIOUS", command=halaman_ke_kiri, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_next = tk.Button(frame_nav, text="NEXT ▶", command=halaman_ke_kanan, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    if total_label > 1: frame_nav.pack(pady=5); btn_prev.pack(side=tk.LEFT, padx=8); btn_next.pack(side=tk.LEFT, padx=8)

    def_simpan_tunggal_wizard = lambda: ipl.simpan_qr_manual(senarai_kad_pembungkus[indeks_halaman], senarai_kad_pembungkus[indeks_halaman])

    frame_btn = tk.Frame(tingkap_popup, bg="#F8F9FA")
    frame_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}
    
    tk.Button(frame_btn, text="🖨️ PRINT", command=lambda: ipl.cetak_kad_tunggal(senarai_kad_pembungkus[indeks_halaman]), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_btn, text="💾 SAVE", command=def_simpan_tunggal_wizard, bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_popup.destroy, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)

    # Memuatkan paparan mengikut indeks fokus dinamik sejurus tetingkap dibuka
    kemaskini_paparan_selak()
