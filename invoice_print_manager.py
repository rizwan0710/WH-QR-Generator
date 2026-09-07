import os
import sys
import sqlite3
from tkinter import messagebox, filedialog
from PIL import Image

def cetak_a4_master(target_data):
    """
    🖨️ ENJIN CETAK SINGLE DEFAULT (KALIS ERROR TUPLE) 🖨️
    Mengekstrak imej bersih daripada data tunggal atau pasangan tuple,
    lalu dihantar terus ke tetingkap cetakan grafik default Windows.
    """
    try:
        im = None
        # 1. Jika data dihantar dalam bentuk tuple (img, paging)
        if isinstance(target_data, tuple) and len(target_data) > 0:
            im = target_data[0]
        # 2. Jika data dihantar dalam bentuk list bertingkat yang mengandungi tuple
        elif isinstance(target_data, list) and len(target_data) > 0:
            item = target_data[0]
            im = item[0] if isinstance(item, tuple) else item
        # 3. Jika data sudah sedia dalam bentuk PIL Image tulen
        else:
            im = target_data
            
        if im is None or not hasattr(im, "save"):
            print("Ralat: Gagal mengekstrak objek imej murni untuk Single Print.")
            return False

        temp_file = "temp_print_invoice_default.png"
        im.save(temp_file)
        
        if sys.platform == "win32":
            os.startfile(temp_file, "print")
            messagebox.showinfo("SUCCESS", "MANAGE TO SEND TO PRINTER!")
            return True
        else:
            os.system(f"lp {temp_file}")
            return True
            
    except Exception as e:
        messagebox.showerror("ERROR", f"FAILED TO PRINT SINGLE: {str(e)}")
        return False

def cetak_a4_batch(senarai_imej_label):
    """
    🚀 BATCH PRINTING ENGINE DEFAULT (MUTTAMAD 1 TETINGKAP UNTUK SEMUA) 🚀
    Menggabungkan semua stiker secara menegak, membuang teks paging,
    dan membuka HANYA 1 tetingkap dialog cetakan Windows tanpa ralat tuple.
    """
    if not senarai_imej_label:
        messagebox.showwarning("NO DATA", "NO INVOICE LABELS TO PRINT.")
        return False
        
    try:
        # Ekstrak senarai imej bersih (PIL Image) secara eksklusif daripada gandingan tuple di indeks 0
        senarai_bersih = []
        for item in senarai_imej_label:
            img_clean = item[0] if isinstance(item, tuple) else item
            if isinstance(img_clean, Image.Image):
                senarai_bersih.append(img_clean)
                
        if not senarai_bersih:
            messagebox.showerror("ERROR", "No valid PIL Images found in batch list.")
            return False
            
        # Ambil parameter reka bentuk standard daripada stiker pertama yang telah bersih
        img_induk = senarai_bersih[0]
        mod_imej = img_induk.mode
        lebar_standard = img_induk.width
        jumlah_tinggi = sum(img.height for img in senarai_bersih)
        
        # Cipta kanvas master panjang di memori RAM mengikut kelebaran standard stiker asal
        master_img = Image.new(mod_imej, (lebar_standard, jumlah_tinggi), color="white")
        
        # Tampal stiker satu demi satu secara menegak ke bawah dengan koordinat Y yang dinamik
        y_offset = 0
        for img in senarai_bersih:
            if img.width != lebar_standard:
                nisbah = lebar_standard / float(img.width)
                tinggi_baru = int(float(img.height) * nisbah)
                img = img.resize((lebar_standard, tinggi_baru), Image.Resampling.LANCZOS)
            
            master_img.paste(img, (0, y_offset))
            y_offset += img.height
            
        temp_batch_file = "temp_print_invoice_batch.png"
        master_img.save(temp_batch_file)
        
        if sys.platform == "win32":
            os.startfile(temp_batch_file, "print")
            messagebox.showinfo("SUCCESS", f"SUCCESSFULLY SENT BATCH OF {len(senarai_bersih)} INVOICES TO ONE PRINT WINDOW!")
            return True
        else:
            os.system(f"lp {temp_batch_file}")
            return True
            
    except Exception as e:
        messagebox.showerror("BATCH PRINT ERROR", f"FAILED TO GENERATE BATCH PRINT:\n{str(e)}")
        return False

def simpan_a4_master(img_label, invoice_no):
    """Menyimpan helaian grafik stiker ke komputer mengikut saiz asal."""
    try:
        im = img_label[0] if isinstance(img_label, tuple) else img_label
        fail_clean = str(invoice_no).replace("/", "-").replace(":", "-").strip()
        path_fail = filedialog.asksaveasfilename(
            initialfile=f"INVOICE_LABEL_{fail_clean}.png", 
            defaultextension=".png", 
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            title="SIMPAN GRAFIK PELEKAT"
        )
        if path_fail:
            im.convert("RGB").save(path_fail, "PNG", quality=100)
            messagebox.showinfo("SUCCESS", "IMAGE SUCCESSFULLY SAVED!")
    except Exception as e:
        messagebox.showerror("ERROR SAVED", f"FAILED TO SAVE IMAGE:\n{str(e)}")

def dapatkan_qty_outer(seq_no):
    """Mengambil data Kuantiti bagi siri Outer Box dari database."""
    if not seq_no or seq_no == "--- PILIH DATA ---":
        return 0
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM rekod_qr WHERE sequence_no = ?", (str(seq_no).strip(),))
            res = cursor.fetchone()
            if res:
                clean_val = str(res[0]).upper().replace("PCS", "").strip()
                return int(float(clean_val))
            return 0
    except:
        return 0
