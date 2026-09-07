import os
import sys
import sqlite3
import win32print
from tkinter import messagebox, filedialog
from PIL import Image

def cetak_a4_master(img_a4):
    """
    🖨️ ENJIN VISUAL AUTO-SIZING INVOICE A4 (SINGLE IMAGE) 🖨️
    Memaksa Windows memilih saiz kertas A4 secara automatik sebelum melancarkan 
    tetingkap dialog cetakan gambar rasmi Windows untuk operator semak.
    """
    try:
        temp_file = "temp_print_invoice_a4.png"
        img_a4.save(temp_file)
        
        if sys.platform == "win32":
            try:
                # 🌟 ENJIN AUTO-SET DEVICE MODE Windows A4 🌟
                nama_printer = win32print.GetDefaultPrinter()
                hprinter = win32print.OpenPrinter(nama_printer)
                
                info_pemacu = win32print.GetPrinter(hprinter, 2)
                devmode = info_pemacu["pDevMode"]
                
                devmode.Fields |= 0x2  # DM_PAPERSIZE
                devmode.PaperSize = 1  # DMPAPER_A4 rasmi Windows
                
                win32print.SetPrinter(hprinter, 2, info_pemacu, 0)
                win32print.ClosePrinter(hprinter)
                print("Berjaya auto-set pemacu Invoice ke saiz A4.")
            except Exception as e_driver:
                print(f"Nota pemacu Invoice A4 (Sila set saiz manual jika perlu): {str(e_driver)}")

            # 🌟 PAPAR 1 POP-UP WINDOWS UNTUK 1 FAIL MASTER
            os.startfile(temp_file, "print")
            messagebox.showinfo("SUCCESS", "MANAGE TO SEND TO PRINTER!")
        else:
            messagebox.showwarning("SYSTEM OPERATION", "PRINTER FUNCTION ONLY SUPPORTS WINDOWS.")
            
    except Exception as e:
        messagebox.showerror("ERROR", f"FAILED TO PRINT: {str(e)}")

def cetak_a4_batch(senarai_imej_label):
    """
    🚀 IMPLEMENTASI SILENT SINGLE POP-UP UNTUK BATCH INVOICE 🚀
    Menggabungkan senarai imej label invoice secara menegak ke dalam satu fail imej 
    tunggal sebelum membuka SATU sahaja tetingkap dialog pencetak Windows.
    """
    if not senarai_imej_label:
        messagebox.showwarning("NO DATA", "NO INVOICE LABELS TO PRINT.")
        return False
        
    try:
        # Tentukan mod imej dan kelebaran standard berdasarkan imej pertama
        mod_imej = senarai_imej_label[0].mode
        lebar_standard = senarai_imej_label[0].width
        
        # Kira jumlah ketinggian keseluruhan untuk semua label digabungkan
        jumlah_tinggi = sum(img.height for img in senarai_imej_label)
        
        # Cipta satu kanvas kosong besar (Master Sheet) di memori RAM
        master_img = Image.new(mod_imej, (lebar_standard, jumlah_tinggi), color="white")
        
        # Lakukan cantuman atau tampalan (paste) satu demi satu mengikut koordinat Y
        y_offset = 0
        for img in senarai_imej_label:
            # Jika ada imej yang saiznya lari sedikit, paksa resize mengikut lebar standard
            if img.width != lebar_standard:
                nisbah = lebar_standard / float(img.width)
                tinggi_baru = int(float(img.height) * nisbah)
                img = img.resize((lebar_standard, tinggi_baru), Image.Resampling.LANCZOS)
            
            master_img.paste(img, (0, y_offset))
            y_offset += img.height
            
        # Simpan sementara fail gabungan batch sheet
        temp_batch_file = "temp_print_invoice_batch.png"
        master_img.save(temp_batch_file)
        
        if sys.platform == "win32":
            try:
                # Optimumkan pemacu ke saiz kertas bersesuaian / A4
                nama_printer = win32print.GetDefaultPrinter()
                hprinter = win32print.OpenPrinter(nama_printer)
                info_pemacu = win32print.GetPrinter(hprinter, 2)
                devmode = info_pemacu["pDevMode"]
                devmode.Fields |= 0x2
                devmode.PaperSize = 1
                win32print.SetPrinter(hprinter, 2, info_pemacu, 0)
                win32print.ClosePrinter(hprinter)
            except Exception as e_driver:
                print(f"Driver notice: {str(e_driver)}")
                
            # Memicu HANYA 1 TETINGKAP DIALOG WINDOWS untuk keseluruhan batch
            os.startfile(temp_batch_file, "print")
            messagebox.showinfo("SUCCESS", f"SUCCESSFULLY SENT BATCH OF {len(senarai_imej_label)} INVOICES TO ONE PRINT WINDOW!")
            return True
        else:
            os.system(f"lp {temp_batch_file}")
            return True
            
    except Exception as e:
        messagebox.showerror("BATCH PRINT ERROR", f"FAILED TO GENERATE BATCH PRINT:\n{str(e)}")
        return False

def simpan_a4_master(img_a4, invoice_no):
    """[DIOPTIMUMKAN] Menyimpan helaian susunan stiker A4 Master Sheet ke komputer."""
    fail_clean = str(invoice_no).replace("/", "-").replace(":", "-").strip()
    path_fail = filedialog.asksaveasfilename(
        initialfile=f"A4_INVOICE_{fail_clean}.png", 
        defaultextension=".png", 
        filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        title="SIMPAN GRAFIK BATCH SHEET A4"
    )
    if path_fail:
        try:
            img_a4.convert("RGB").save(path_fail, "PNG", quality=100)
            messagebox.showinfo("SUCCESS", "IMAGE SUCCESSFULLY SAVED!")
        except Exception as e:
            messagebox.showerror("ERROR SAVED", f"FAILED TO SAVE IMAGE:\n{str(e)}")

def dapatkan_qty_outer(seq_no):
    """Mengambil data Kuantiti bagi siri Outer Box dari database untuk pengiraan konsolidasi."""
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
