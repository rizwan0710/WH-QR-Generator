import tkinter as tk
from tkinter import messagebox, filedialog
import qrcode
import re
import os
import sys  
import sqlite3
from PIL import Image, ImageTk

# Standard gaya butang korporat OHTA Precision
BTN_STYLE = {"font": ("Segoe UI", 10, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

def bina_single_invoice_preview(baris, root):
    """
    🌟 ENGINE INVOICE DYNAMIC PAGING MATRIX (FULLY SYNCHRONIZED) 🌟
    Mengendalikan pengekstrakan flat list dan nested list secara pintar gred industri
    serta membetulkan pemanggilan fungsi backend ke cetak_qr dan simpan_qr_manual.
    """
    try:
        import label_invoice_designer as lid
        import invoice_packing_logic as ipl_inv  
        
        # Memeriksa jika data yang dihantar ialah nested list [[...]] atau flat list [...]
        if isinstance(baris, list) and len(baris) > 0:
            if isinstance(baris[0], (list, tuple)):
                senarai_baris = baris
            else:
                senarai_baris = [baris]
        else:
            senarai_baris = [baris]
            
        total_pilihan_box = len(senarai_baris)

        # ─── JALANKAN GELUNG PENGHASILAN TETINGKAP BERDASARKAN BILANGAN PILIHAN BOX ───
        for indeks_semasa, data_flat in enumerate(senarai_baris, start=1):
            
            # Peta indeks lajur Treeview Invoice (Code 11)
            inv_no = str(data_flat[4]).strip().upper().replace("INV:", "").strip()
            so_no  = str(data_flat[5]).strip().upper().replace("SO:", "").strip()
            qty    = str(data_flat[6]).strip().upper().replace("PCS", "").strip()
            outer  = str(data_flat[8]).strip().replace("\n", ",")
            cust   = str(data_flat[3]).strip()
            seq    = str(data_flat[10]).strip()
            
            # Menjana teks pembahagian halaman dinamik (Contoh: BOX 1/2)
            teks_page_dinamik = f"BOX {indeks_semasa}/{total_pilihan_box}"
            
            # Bina Kod QR berasaskan RAM
            qr = qrcode.QRCode(version=1, box_size=10, border=1)
            qr.add_data(seq)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            
            # Hantar teks_page_dinamik ke dalam enjin grafik Pillow Canvas Drawing
            img_gabung = lid.bina_imej_invoice(img_qr, inv_no, so_no, outer, f"{qty} PCS", seq, teks_page_dinamik, cust)
            
            # Paparkan tetingkap popup Tkinter UI
            tingkap = tk.Toplevel(root)
            tingkap.title(f"PREVIEW INVOICE - {seq} ({teks_page_dinamik})")
            tingkap.geometry("460x390+450+120")
            tingkap.configure(bg="#F8F9FA")
            tingkap.grab_set()
            
            tk.Label(tingkap, text="INVOICE LABEL SINGLE PREVIEW", font=("Segoe UI", 11, "bold"), fg="#EA580C", bg="#F8F9FA").pack(pady=10)
            f_canvas = tk.Frame(tingkap, bg="white", bd=1, relief="groove")
            f_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            
            img_resize = img_gabung.resize((400, 200), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_resize)
            lbl = tk.Label(f_canvas, image=img_tk, bg="white")
            lbl.image = img_tk; lbl.pack(expand=True)
            
            f_btn = tk.Frame(tingkap, bg="#F8F9FA")
            f_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
            
            # 🌟 FIX MUTTAMAD: Mengubah cetak_kad_tunggal -> ipl_inv.cetak_qr dan simpan_kad_tunggal -> ipl_inv.simpan_qr_manual 🌟
            tk.Button(f_btn, text="🖨️ PRINT", command=lambda im=img_gabung: ipl_inv.cetak_qr(im), bg="#22C55E", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
            tk.Button(f_btn, text="💾 SAVE", command=lambda im=img_gabung, iv=inv_no: ipl_inv.simpan_qr_manual(im, iv), bg="#F59E0B", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
            tk.Button(f_btn, text="❌ CLOSE", command=tingkap.destroy, bg="#374151", **BTN_STYLE).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
            
    except Exception as e:
        messagebox.showerror("INVOICE RENDER ERROR", f"FAILED TO TRANSLATE THE ORIGINAL FUNCTION NAME:\n{str(e)}")

def bina_single_outer_preview(baris, root):
    """Memanggil pembantu luaran untuk memproses kemasukan data Part No pada label Outer Box."""
    import database_outer_render_helper as dorh
    dorh.proses_render_outer_single(baris, root, BTN_STYLE)

def bina_single_inner_preview(baris, root):
    """Melakar grafik Potrait Inner Box secara RAM-based."""
    try:
        import label_designer as ld
        import inner_packing_logic as ipl
        
        data_flat = baris if isinstance(baris, (list, tuple)) else baris
        
        # Indeks Map Tab Inner: 2=Tarikh, 3=Customer, 4=Drawing, 5=Part, 6=Qty, 7=Mfg, 8=Machine, 10=Sequence
        tarikh   = str(data_flat[2]).strip()
        customer = str(data_flat[3]).strip()
        drawing  = str(data_flat[4]).strip()
        part     = str(data_flat[5]).strip()
        qty      = str(data_flat[6]).strip()
        mfg      = str(data_flat[7]).strip()
        mac      = str(data_flat[8]).strip()
        seq_no   = str(data_flat[10]).strip()
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_no)
        img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img_gabung = ld.bina_imej_gabungan(img_qr, tarikh, drawing, part, qty, mfg, mac, seq_no, customer)
        
        tingkap = tk.Toplevel(root)
        tingkap.title(f"REPRINT INNER - {seq_no}")
        tingkap.geometry("440x670+450+30")
        tingkap.configure(bg="#F8F9FA")
        tingkap.grab_set()
        
        tk.Label(tingkap, text="INNERBOX LABEL PREVIEW", font=("Segoe UI", 12, "bold"), fg="#2E7D32", bg="#F8F9FA").pack(pady=12)
        f_canvas = tk.Frame(tingkap, bg="white", bd=1, relief="groove")
        f_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        img_tk = ImageTk.PhotoImage(img_gabung)
        lbl = tk.Label(f_canvas, image=img_tk, bg="white")
        lbl.image = img_tk; lbl.pack(expand=True)
        
        f_btn = tk.Frame(tingkap, bg="#F8F9FA")
        f_btn.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
        
        tk.Button(f_btn, text="🖨️ PRINT", command=lambda: ipl.cetak_qr(img_gabung), bg="#22C55E", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Button(f_btn, text="💾 SAVE", command=lambda: ipl.simpan_qr_manual(img_gabung, seq_no), bg="#F59E0B", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(f_btn, text="❌ CLOSE", command=tingkap.destroy, bg="#374151", **BTN_STYLE).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
    except Exception as e:
        messagebox.showerror("Ralat Inner Mapping", str(e))
