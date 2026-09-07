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
    # Fungsi pembantu untuk butang borang input biasa (Dikekalkan jika dipanggil dari luar)
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
        warna_tema = "#0078D7"
        tajuk_kad = "OHTA OUTER LABEL PREVIEW"
        w_box, h_box = 460, 360  
    else:
        img_gabung = ld.bina_imej_gabungan(img_qr_mentah, str(tarikh), str(drawing), str(part), str(qty), str(mfg), str(mac), seq_no)
        warna_tema = "#2E7D32"
        tajuk_kad = "OHTA INNER LABEL PREVIEW"
        w_box, h_box = 390, 520  
    
    bina_tetingkap_kanvas(root, img_gabung, tajuk_kad, warna_tema, w_box, h_box, seq_no, is_outer=True, is_invoice=False)

def cipta_popup_preview_invoice(root, seq_invoice, invoice_no, so_no, outer_box_siri, clean_qty, text_paging):
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(seq_invoice)
    qr.make(fit=True)
    img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    img_gabung = lid.bina_imej_invoice(img_qr_mentah, invoice_no, so_no, outer_box_siri, clean_qty, seq_invoice, text_paging)
    bina_tetingkap_kanvas(root, img_gabung, f"OHTA INVOICE LABEL ({text_paging})", "#E65100", 460, 360, seq_invoice, is_outer=False, is_invoice=True)

def bina_tetingkap_kanvas(root, img_gabung, tajuk_kad, warna_tema, w_box, h_box, seq_rujukan, is_outer=False, is_invoice=False):
    tingkap_popup = tk.Toplevel(root)
    tingkap_popup.title(f"PREVIEW - {seq_rujukan}")
    tingkap_popup.geometry(f"{w_box}x{h_box}")
    
    tk.Label(tingkap_popup, text=tajuk_kad, font=("Arial", 11, "bold"), fg=warna_tema).pack(pady=5)
    
    frame_skrol = tk.Frame(tingkap_popup)
    frame_skrol.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    kanvas = tk.Canvas(frame_skrol, highlightthickness=0)
    scrollbar_y = ttk.Scrollbar(frame_skrol, orient=tk.VERTICAL, command=kanvas.yview)
    frame_imej = tk.Frame(kanvas)
    
    kanvas.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    kanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    kanvas.create_window((10, 0), window=frame_imej, anchor="nw")
    
    cache_file = f"temp_preview_cache.png"
    img_gabung.save(cache_file)
    img_buka = Image.open(cache_file)
    img_tk = ImageTk.PhotoImage(img_buka)
    
    label_gambar = tk.Label(frame_imej, image=img_tk, bg="white")
    label_gambar.image = img_tk  
    label_gambar.pack()
    
    frame_imej.update_idletasks()
    kanvas.config(scrollregion=kanvas.bbox("all"))
    
    frame_btn = tk.Frame(tingkap_popup)
    frame_btn.pack(pady=10)
    
    if is_invoice:
        tk.Button(frame_btn, text="PRINT", command=lambda: fip.cetak_qr(img_gabung), bg="#28a745", fg="white", font=("Arial", 9, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btn, text="SAVE", command=lambda: fip.simpan_qr_manual(img_gabung, seq_rujukan), bg="#FF9800", fg="white", font=("Arial", 9, "bold"), width=12).pack(side=tk.LEFT, padx=5)
    else:
        tk.Button(frame_btn, text="PRINT LABEL", command=lambda: fop.cetak_qr(img_gabung) if is_outer else ld.cetak_qr(img_gabung), bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=14).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn, text="SAVE LABEL", command=lambda: fop.simpan_qr_manual(img_gabung, seq_rujukan) if is_outer else ld.simpan_qr_manual(img_gabung, seq_rujukan), bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=14).pack(side=tk.LEFT, padx=10)
