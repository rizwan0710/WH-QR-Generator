import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import ImageTk, Image
import form_invoice_packing_logic as ipl  
import invoice_print_manager  
import os

def buka_popup_individual_1by1(parent, senarai_kad_tunggal, inv_no=""):
    """
    🌟 ENGINE PREVIEW DINAMIK INVOICE (100% PERFECT VISUAL COLOR MATCH) 🌟
    Applies the exact layout button styles and slider next/prev mechanics.
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

    lbl_header = tk.Label(tingkap_popup, text="", font=("Segoe UI", 10, "bold"), fg="#10B981", bg="#F8F9FA")
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

    def cetak_halaman_tunggal():
        """🖨️ PRINT CURRENT PAGE"""
        item_aktif = senarai_kad_pembungkus_lokal[indeks_halaman]
        img_clean = item_aktif if isinstance(item_aktif, tuple) else item_aktif
        invoice_print_manager.cetak_a4_master(img_clean)

    def cetak_semua_pukal():
        """🖨️ PRINT ALL PAGES BATCH"""
        if messagebox.askyesno("CONFIRMATION MESSAGE", f"PROCEED WITH PRINT ALL {total_label} LABELS?", parent=tingkap_popup):
            imej_bersih_list = [item if isinstance(item, tuple) else item for item in senarai_kad_pembungkus_lokal]
            invoice_print_manager.cetak_a4_batch(imej_bersih_list)

    def simpan_semua_pukal():
        """💾 SAVE ALL IMAGES"""
        folder_tujuan = filedialog.askdirectory(title="CHOOSE FOLDER TO SAVE ALL IMAGES", parent=tingkap_popup)
        if folder_tujuan:
            for img_item, box_paging in senarai_kad_pembungkus_lokal:
                img_clean = img_item if isinstance(img_item, tuple) else img_item
                paging_bersih = str(box_paging).replace("/", "-").replace(" ", "_").upper()
                img_clean.save(os.path.join(folder_tujuan, f"LABEL_INVOICE_{inv_no}_{paging_bersih}.png"), "PNG")
            messagebox.showinfo("COMPLETE", f"ALL {total_label} LABELS SUCCESSFULLY SAVED!", parent=tingkap_popup)

    # ─── 1. PAGE SCROLL NAVIGATION BAR ───
    frame_nav = tk.Frame(tingkap_popup, bg="#F8F9FA")
    btn_prev = tk.Button(frame_nav, text="◀ PREV", command=halaman_ke_kiri, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_prev.pack(side=tk.LEFT, padx=8)
    btn_next = tk.Button(frame_nav, text="NEXT ▶", command=halaman_ke_kanan, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_next.pack(side=tk.LEFT, padx=8)

    if total_label > 1:
        frame_nav.pack(pady=5)

    # ─── 2. STANDARDIZED FLAT ACTION BUTTON FOOTER ───
    frame_btn = tk.Frame(tingkap_popup, bg="#F8F9FA")
    frame_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

    tk.Button(frame_btn, text="🖨️ PRINT CURRENT", command=cetak_halaman_tunggal, bg="#2ECC71", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_btn, text="🖨️ PRINT ALL", command=cetak_semua_pukal, bg="#10B981", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_btn, text="💾 SAVE ALL", command=simpan_semua_pukal, bg="#E65100", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_popup.destroy, bg="#34495E", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)

    kemaskini_paparan_selak()

def buka_popup_pukal_invoice_1by1(jadual, parent_window=None):
    """
    🌟 ALIAS LINKING ENGINE MUKTAMAD 🌟
    Interceptors for existing database log table rows. Generates the new QR payload layout 
    sequence mapping dynamically when viewing single/multiple logs from Central Database view.
    """
    item_terpilih = jadual.selection()
    if not item_terpilih:
        return
        
    nilai_baris = jadual.item(item_terpilih, "values")
    if not nilai_baris:
        return
        
    try:
        # Array positioning maps: index matching row outputs
        id_db = nilai_baris[1]
        customer_name = nilai_baris[3]
        invoice_no = nilai_baris[4]
        so_no = nilai_baris[5]
        clean_qty = nilai_baris[6]
        text_paging = nilai_baris[7]
        outer_box_siri = nilai_baris[8]
        seq_invoice = nilai_baris[10]
    except Exception as e_parse:
        print(f"Error parsing treeview column index: {e_parse}")
        return
        
    # Standardizing structured string formatting sequences matching user criteria
    qr_payload = (
        f"SN: {str(seq_invoice).strip()}\n"
        f"Invoice No: {str(invoice_no).strip()}\n"
        f"SO No: {str(so_no).strip()}\n"
        f"Customer: {str(customer_name).strip()}\n"
        f"Qty: {str(clean_qty).strip()}"
    )
        
    import qrcode
    qr = qrcode.QRCode(version=1, border=1)
    qr.add_data(qr_payload)
    qr.make(fit=True)
    im_qr = qr.make_image().convert("RGB")
    
    import label_invoice_designer as lid
    img_stiker = lid.bina_imej_invoice(
        img_qr=im_qr,
        inv_no=invoice_no,
        so_no=so_no,
        outer_seq=outer_box_siri,
        qty=clean_qty,
        seq_inv=seq_invoice,
        paging=text_paging
    )
    
    # Pack array structure to dynamic list parameters
    import central_tab_invoice_wizard
    central_tab_invoice_wizard.buka_popup_individual_1by1(
        parent_window, 
        [(img_stiker, text_paging)], 
        inv_no=invoice_no
    )
