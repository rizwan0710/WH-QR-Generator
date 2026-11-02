import tkinter as tk
from tkinter import messagebox, filedialog
import qrcode
import re
import os
import sys
import sqlite3
from PIL import Image, ImageTk
from datetime import datetime

# 🌟 IMPORT PENGURUS DATABASE PUSAT NAS 🌟
import database_manager as dbm

def dapatkan_qty_inner_direct(inner_seq):
    """Mengambil kuantiti stiker murni dari database pusat NAS sekiranya semakan struktur lari."""
    try:
        # ✅ DIBAIKI: Menggunakan sambungan berpusat dbm.get_db_connection()
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError: pass
                
            cursor.execute(f"SELECT quantity FROM rekod_qr WHERE UPPER(TRIM({lajur_seq})) = ?", (str(inner_seq).strip().upper(),))
            row = cursor.fetchone()
            if row and row:
                return str(row).strip()
    except Exception as e: 
        print(f"Error direct quantity fetch: {e}")
    return "100 PCS" # Fallback standard industri lantai kilang anda

def cetak_qr_outer_single(img_label):
    try:
        temp_file = "temp_print_outer_single.png"
        img_label.save(temp_file)
        if sys.platform == "win32":
            os.startfile(temp_file, "print")
    except Exception as e:
        print(f"Print error: {str(e)}")

def simpan_qr_manual_outer_single(img_label, seq_outer):
    if img_label is None: return
    fail_bersih = str(seq_outer).replace("/", "-").replace(":", "-").strip()
    path_simpan = filedialog.asksaveasfilename(
        initialfile=f"REPRINT_OUTER_{fail_bersih}.png",
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png")],
        title="Save Outer Box Label"
    )
    if path_simpan:
        try:
            img_label.convert("RGB").save(path_simpan, "PNG")
            messagebox.showinfo("SUCCESS", "LABEL OUTER SUCCESSFULLY SAVED!")
        except Exception as e:
            messagebox.showerror("ERROR", f"FAILED TO SAVE LABEL:\n{str(e)}")

def proses_render_outer_single(baris, root, BTN_STYLE):
    """🌟 ENJIN UTAMA REPRINT: Mengambil nilai live murni dari database dan UI pusat NAS 🌟"""
    try:
        import label_outer_designer as lod
        import form_outer_packing_logic as fopl
        
        data_flat = list(baris) if isinstance(baris, (list, tuple)) else baris
        if data_flat and str(data_flat[0]) in ("☐", "☑"):
            data_flat = data_flat[1:]
            
        # 🛠️ SEPADAN LAJUR JADUAL: Mengikut ketetapan 9 lajur central database utama
        # [0:ID, 1:Date, 2:Customer, 3:Quantity, 4:Box Type, 5:Linked Inners, 6:Operation, 7:Outer Sequence]
        qty_text_live  = str(data_flat[3]).replace('PCS','').strip()  # Lajur Box Quantity (Contoh: 395)
        raw_inner_text = str(data_flat[5]).strip()                    # Lajur Linked Inners
        seq_outer      = str(data_flat[7]).strip()                    # Lajur Outer Sequence (B%)
        cust_name      = str(data_flat[2]).strip()                    # Lajur Customer Name

        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_outer)
        img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        senarai_inner_bersih = [s.strip() for s in re.split(r'[,\n]', raw_inner_text) if s.strip() and s.strip() != "None"]
        
        data_gabungan_final = []
        for s_clean in senarai_inner_bersih:
            if s_clean:
                info_inner = fopl.dapatkan_maklumat_inner(s_clean)
                
                # ✅ DIBAIKI: Mengeluarkan data secara selamat daripada format Kamus (Dict)
                if isinstance(info_inner, dict) and "qty" in info_inner:
                    q_val = info_inner.get("qty", "100 PCS")
                else:
                    # Ambil baki murni database jika struktur Dictionary terlepas larian
                    q_val = dapatkan_qty_inner_direct(s_clean)
                
                # Masukkan nombor siri stiker WP bersama nilai kuantitinya yang bersih
                data_gabungan_final.append((s_clean, f"{str(q_val).upper().replace('PCS','').strip()} PCS"))

        # Menjana reka bentuk imej menggunakan enjin lakaran grafik designer rasmi anda
        img_gabung = lod.create_outer_label_image(
            seq_outer, "OHTA PRECISION", cust_name, "COMBINED", "CONSOLIDATED", 
            f"{qty_text_live} PCS", "M/C-01", datetime.now().strftime("%d/%m/%Y"), img_qr_mentah, data_gabungan_final
        )

        tingkap_preview = tk.Toplevel(root)
        tingkap_preview.title(f"REPRINT OUTER - {seq_outer}")
        tingkap_preview.geometry("480x420+450+100")
        tingkap_preview.configure(bg="#F8F9FA")
        tingkap_preview.grab_set()

        tk.Label(tingkap_preview, text="OUTER LABEL SINGLE PREVIEW", font=("Segoe UI", 12, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=(15, 2))
        frame_canvas = tk.Frame(tingkap_preview, bg="white", bd=1, relief="groove")
        frame_canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        lbl_visual = tk.Label(frame_canvas, bg="white")
        lbl_visual.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        img_resize = img_gabung.resize((400, 190), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_resize)
        lbl_visual.config(image=img_tk)
        lbl_visual.image = img_tk

        frame_btn = tk.Frame(tingkap_preview, bg="#F8F9FA")
        frame_btn.pack(side=tk.BOTTOM, pady=15, fill=tk.X, padx=20)

        tk.Button(frame_btn, text="🖨️ PRINT", command=lambda: cetak_qr_outer_single(img_gabung), bg="#22C55E", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        tk.Button(frame_btn, text="💾 SAVE", command=lambda: simpan_qr_manual_outer_single(img_gabung, seq_outer), bg="#F59E0B", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        tk.Button(frame_btn, text="❌ CLOSE", command=tingkap_preview.destroy, bg="#374151", **BTN_STYLE).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0))
        
    except Exception as e:
        messagebox.showerror("ERROR OUTER MAPPING", f"FAILED TO PROCESS REPRINT DATA:\n{str(e)}", parent=root)
