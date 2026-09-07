import tkinter as tk
from tkinter import messagebox, filedialog
import qrcode
import re
import os
import sys
import sqlite3
from PIL import Image, ImageTk

def dapatkan_qty_inner_direct(inner_seq):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM rekod_qr WHERE sequence_no = ?", (inner_seq,))
            row = cursor.fetchone()
            if row: return str(row[0])
    except Exception: pass
    return "0"

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
        title="Simpan Label Outer Box"
    )
    if path_simpan:
        try:
            img_label.convert("RGB").save(path_simpan, "PNG")
            messagebox.showinfo("SUCCESS", "LABEL OUTER SUCCESSFULLY SAVED!")
        except Exception as e:
            messagebox.showerror("ERROR", f"FAILED TO SAVE LABEL:\n{str(e)}")

def proses_render_outer_single(baris, root, BTN_STYLE):
    """🌟 ENJIN UTAMA: Memecah siri imbasan dan menterjemah teks kepada Part No secara RAM-based 🌟"""
    try:
        import label_outer_designer as lod
        import form_outer_packing_logic as fopl
        
        data_flat = baris if isinstance(baris, (list, tuple)) else baris
        
        seq_outer      = str(data_flat[8]).strip() 
        raw_inner_text = str(data_flat[6]).strip() 
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_outer)
        img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        senarai_inner_bersih = [s.strip() for s in re.split(r'[,\n]', raw_inner_text) if s.strip() and s.strip() != "None"]
        
        data_gabungan_final = []
        for s_clean in senarai_inner_bersih:
            if s_clean:
                info_inner = fopl.dapatkan_maklumat_inner(s_clean)
                if info_inner and len(info_inner) >= 4:
                    part_no_asli = str(info_inner[3]).strip() # Mengambil lajur part_no asli
                    q_val = str(info_inner[4]).strip()        # Mengambil lajur kuantiti asli
                else:
                    part_no_asli = s_clean
                    q_val = dapatkan_qty_inner_direct(s_clean)
                
                data_gabungan_final.append((part_no_asli, str(q_val)))

        img_gabung = lod.bina_imej_gabungan_akses(img_qr_mentah, data_gabungan_final, seq_outer)

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
        messagebox.showerror("ERROR OUTER MAPPING", f"FAILED TO PROCESS DATA:\n{str(e)}")
