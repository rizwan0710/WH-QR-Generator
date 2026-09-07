import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import ImageTk, Image
import form_invoice_packing_logic as ipl  # Menggunakan rujukan fail logik invois utama abang
import invoice_print_manager  # Menyambungkan enjin cantuman 1 tetingkap cetak berkelompok
import os

def buka_popup_individual_1by1(parent, senarai_kad_tunggal, inv_no=""):
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
        """🔥 ENJIN BATCH PRINT INVOICE: Menggabungkan semua stiker ke dalam 1 pop-up tingkap printer Windows 🔥"""
        if messagebox.askyesno("CONFIRMATION MESSAGE", f"PROCEED WITH PRINT ALL {total_label} THIS LABEL IN ONE WINDOW?", parent=tingkap_popup):
            # Ekstrak senarai imej bersih (PIL Image) sahaja daripada gandingan tuple
            imej_bersih_list = [img for img, _ in senarai_kad_pembungkus_lokal]
            
            # Panggil enjin cantuman menegak bersatu dari print manager
            berjaya = invoice_print_manager.cetak_a4_batch(imej_bersih_list)
            if berjaya:
                messagebox.showinfo("SUCCESS", f"ALL {total_label} LABEL MANAGE TO SEND TO ONE PRINT WINDOW!", parent=tingkap_popup)

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

    # ─── 2. BARIS BUTANG KAWALAN FLAT STYLE SERAGAM (DINAMIK & KALIS TUPLE ERROR) ───
    frame_btn = tk.Frame(tingkap_popup, bg="#F8F9FA")
    frame_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

    if total_label == 1:
        # 🌟 FIXED INDEX TUNGGAL: Mengambil elemen imej bersih daripada tuple untuk kes 1 stiker tunggal
        tk.Button(frame_btn, text="🖨️ PRINT ", command=lambda: ipl.cetak_qr(senarai_kad_pembungkus_lokal), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="💾 SAVE ", command=simpan_tunggal_sahaja, bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_popup.destroy, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)
    else:
        # 🌟 FIXED INDEX CURRENT: Mengambil elemen imej bersih pada indeks halaman yang aktif untuk cetakan batch
        tk.Button(frame_btn, text="🖨️ PRINT CURRENT", command=lambda: ipl.cetak_qr(senarai_kad_pembungkus_lokal[indeks_halaman]), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(frame_btn, text="🔥 PRINT ALL (1 WINDOW)", command=cetak_semua_pukal, bg="#10B981", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(frame_btn, text="💾 SAVE CURRENT", command=simpan_tunggal_sahaja, bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(frame_btn, text="📦 SAVE ALL", command=simpan_semua_pukal, bg="#EA580C", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_popup.destroy, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

    kemaskini_paparan_selak()

# ─── SECTION ALIAS PROJEK (SINKRONISASI CENTRAL DATABASE PANEL) ───
def buka_popup_pukal_invoice_1by1(jadual, parent_window=None):
    """
    🌟 ALIAS LINKING ENGINE: Menyambungkan panggilan database_manager.py baris 64 🌟
    Membaca baris terpilih dari Treeview Central Database, membina tuple data imej PIL murni, 
    dan melancarkan jendela pratinjau utama secara selamat tanpa ralat AttributeError.
    """
    item_terpilih = jadual.selection()
    if not item_terpilih:
        return
        
    nilai_baris = jadual.item(item_terpilih, "values")
    if not nilai_baris:
        return
        
    # Ekstrak parameter mengikut struktur rekod_qr database abang
    # cols = (id, tarikh, customer, drawing_no, part_no, quantity, machine, lotcard_no, sequence_no)
    try:
        id_db, tarikh, cust, dwg, part, qty, machine, lot, seq = nilai_baris
    except ValueError:
        # Jika kolum berbeza, gunakan perlindungan fallback data
        return
        
    import qrcode
    qr = qrcode.QRCode(version=1, border=1)
    qr.add_data(str(seq).strip())
    qr.make(fit=True)
    im_qr = qr.make_image()
    
    import label_invoice_designer as lid
    img_stiker = lid.bina_imej_invoice(
        img_qr=im_qr,
        invoice_no=str(dwg).replace("INV:", "").strip(),
        so_no=str(part).replace("SO:", "").strip(),
        outer_seq=str(machine).strip(),
        outer_qty=str(qty).strip(),
        seq_inv_spesifik=str(seq).strip(),
        text_paging=str(lot).strip(),
        customer=str(cust).strip()
    )
    
    if img_stiker:
        # Formatkan semula data ke dalam rantaian list tuple [(Image, Text)] sepadan enjin preview
        gandingan_kad = [(img_stiker, str(lot).strip())]
        buka_popup_individual_1by1(parent_window if parent_window else jadual.winfo_toplevel(), gandingan_kad, str(dwg).replace("INV:", "").strip())
