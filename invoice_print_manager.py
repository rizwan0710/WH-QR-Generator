import os
import sys
import sqlite3
import win32print
from tkinter import messagebox, filedialog

def cetak_a4_master(img_a4):
    """
    🖨️ ENJIN VISUAL AUTO-SIZING INVOICE A4 (KUNCI A4 + PAPAR POP-UP WINDOWS) 🖨️
    Memaksa Windows memilih saiz kertas A4 secara automatik sebelum melancarkan 
    tetingkap dialog cetakan gambar rasmi Windows untuk operator semak.
    """
    try:
        temp_file = "temp_print_invoice_a4.png"
        img_a4.save(temp_file)
        
        if sys.platform == "win32":
            try:
                # 🌟 ENJIN AUTO-SET DEVICE MODE Windows A4 🌟
                # Dapatkan nama pencetak default yang aktif di PC kilang
                nama_printer = win32print.GetDefaultPrinter()
                hprinter = win32print.OpenPrinter(nama_printer)
                
                # Ekstrak struktur tetapan pDevMode semasa pencetak pejabat / thermal
                info_pemacu = win32print.GetPrinter(hprinter, 2)
                devmode = info_pemacu["pDevMode"]
                
                # Beritahu Windows kita mahu menetapkan profil kertas ke saiz standard A4
                devmode.Fields |= 0x2  # DM_PAPERSIZE
                devmode.PaperSize = 1  # 1 melambangkan saiz DMPAPER_A4 rasmi Windows Windows
                
                # Kemaskini tetapan driver pencetak secara sementara di memori Windows
                win32print.SetPrinter(hprinter, 2, info_pemacu, 0)
                win32print.ClosePrinter(hprinter)
                print("Berjaya auto-set pemacu Invoice ke saiz A4.")
            except Exception as e_driver:
                print(f"Nota pemacu Invoice A4 (Sila set saiz manual jika perlu): {str(e_driver)}")

            # 🌟 PAPAR POP-UP WINDOWS: Melancarkan tetingkap dialog rasmi Windows untuk operator klik Print
            os.startfile(temp_file, "print")
            messagebox.showinfo("SUCCESS", "MANAGE TO SEND TO PRINTER!")
        else:
            messagebox.showwarning("SYSTEM OPERATION", "PRINTER FUNCTION ONLY SUPPORTS WINDOWS.")
            
    except Exception as e:
        messagebox.showerror("ERROR", f"FAILED TO PRINT: {str(e)}")

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
