import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
import sqlite3
from PIL import Image, ImageTk
import label_designer as ld
import label_outer_designer as lod
import label_invoice_designer as lid
import form_outer_packing as fop
import form_invoice_packing as fip

def cipta_popup_preview(root, tarikh, drawing, part, qty, mfg, mac, seq_no):
    """Generates the layout configuration and initial single preview structure for boxes."""
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(seq_no)
    qr.make(fit=True)
    img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    if str(seq_no).startswith("B"):
        raw_string = str(mac)
        senarai_raw = raw_string.split(",") if "," in raw_string else raw_string.split("\n")
        data_gabungan_final = []
        for s in senarai_raw:
            s_clean = s.strip()
            if s_clean.startswith("WP"):
                q_val = fop.dapatkan_qty_inner(s_clean)
                data_gabungan_final.append((s_clean, q_val))
        img_gabung = lod.bina_imej_gabungan_akses(img_qr_mentah, data_gabungan_final, seq_no)
        warna_tema = "#198754"
        tajuk_kad = "OHTA OUTER LABEL PREVIEW"
        w_box, h_box = 460, 360  
    else:
        img_gabung = ld.bina_imej_gabungan(img_qr_mentah, str(tarikh), str(drawing), str(part), str(qty), str(mfg), str(mac), seq_no)
        warna_tema = "#198754"
        tajuk_kad = "OHTA INNER LABEL PREVIEW"
        w_box, h_box = 390, 520  
    
    bina_tetingkap_kanvas(root, img_gabung, tajuk_kad, warna_tema, w_box, h_box, seq_no, is_outer=True, is_invoice=False)

def cipta_popup_preview_invoice(root, seq_invoice, invoice_no, so_no, outer_box_siri, clean_qty, text_paging):
    """
    Generates individual single invoice canvas dimensions with standardized structured QR payload data.
    Ensures upcoming newly generated invoices match the requested format sequence.
    """
    # Fallback to dynamic assignment or extraction layer if customer parameter is appended from logic fields
    customer_name = "HONDA MY"  
    
    # Exact requested structural metadata generation layout block
    qr_payload = (
        f"SN: {str(seq_invoice).strip()}\n"
        f"Invoice No: {str(invoice_no).strip()}\n"
        f"SO No: {str(so_no).strip()}\n"
        f"Customer: {customer_name}\n"
        f"Qty: {str(clean_qty).strip()}"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(qr_payload)  
    qr.make(fit=True)
    img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    img_gabung = lid.bina_imej_invoice(img_qr_mentah, invoice_no, so_no, outer_box_siri, clean_qty, seq_invoice, text_paging)
    bina_tetingkap_kanvas(root, img_gabung, f"OHTA INVOICE LABEL ({text_paging})", "#198754", 460, 360, seq_invoice, is_outer=False, is_invoice=True)

def bina_tetingkap_kanvas(root, img_gabung, tajuk_kad, warna_tema, w_box, h_box, seq_rujukan, is_outer=False, is_invoice=False):
    """Builds the single frame preview canvas view and standardized operational action footer."""
    tingkap_popup = tk.Toplevel(root)
    tingkap_popup.title(f"LABEL PREVIEW PANEL - {seq_rujukan}")
    tingkap_popup.geometry(f"{w_box}x{h_box}")
    tingkap_popup.configure(bg="#F8F9FA")
    
    tk.Label(tingkap_popup, text=tajuk_kad, font=("Segoe UI", 11, "bold"), fg=warna_tema, bg="#F8F9FA").pack(pady=8)
    
    frame_skrol = tk.Frame(tingkap_popup, bg="white", bd=1, relief="groove")
    frame_skrol.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    kanvas = tk.Canvas(frame_skrol, highlightthickness=0, bg="white")
    scrollbar_y = ttk.Scrollbar(frame_skrol, orient=tk.VERTICAL, command=kanvas.yview)
    frame_imej = tk.Frame(kanvas, bg="white")
    
    kanvas.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    kanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    kanvas.create_window((10, 0), window=frame_imej, anchor="nw")
    
    cache_file = "temp_preview_cache.png"
    img_gabung.save(cache_file)
    img_buka = Image.open(cache_file)
    img_tk = ImageTk.PhotoImage(img_buka)
    
    label_gambar = tk.Label(frame_imej, image=img_tk, bg="white")
    label_gambar.image = img_tk  
    label_gambar.pack(padx=5, pady=5)
    
    frame_imej.update_idletasks()
    kanvas.config(scrollregion=kanvas.bbox("all"))
    
    frame_btn = tk.Frame(tingkap_popup, bg="#F8F9FA")
    frame_btn.pack(pady=12, fill=tk.X, padx=15)
    
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}
    
    if is_invoice:
        tk.Button(frame_btn, text="PRINT CURRENT", command=lambda: fip.cetak_qr(img_gabung), bg="#198754", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="SAVE CURRENT", command=lambda: fip.simpan_qr_manual(img_gabung, seq_rujukan), bg="#FD7E14", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    else:
        tk.Button(frame_btn, text="PRINT CURRENT", command=lambda: fop.cetak_qr(img_gabung) if is_outer else ld.cetak_qr(img_gabung), bg="#198754", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="SAVE CURRENT", command=lambda: fop.simpan_qr_manual(img_gabung, seq_rujukan) if is_outer else ld.simpan_qr_manual(img_gabung, seq_rujukan), bg="#FD7E14", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        
    tk.Button(frame_btn, text="CLOSE", command=tingkap_popup.destroy, bg="#34495E", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)
