import os
import tkinter as tk
from tkinter import messagebox, filedialog
import win32print
import win32ui
from PIL import Image, ImageWin

def cetak_a4_master(imej_a4_master):
    """
    🌟 ENJIN CETAKAN SENYAP A4 MASTER SHEET (ANTI-HANG & SILENT PRINT) 🌟
    Menghantar helaian susunan stiker A4 terus ke printer default tanpa pop-up dialog.
    """
    try:
        # 1. Mengesan nama pencetak (printer) default yang aktif di Windows lantai kilang
        nama_printer = win32print.GetDefaultPrinter()
        
        # 2. Buka aliran rujukan cetakan sistem Windows (Device Context)
        hprinter = win32print.OpenPrinter(nama_printer)
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(nama_printer)
        
        # 3. Mulakan dokumen tugasan cetakan latar belakang (Spooling Background Job)
        hdc.StartDoc("OHTA_PRECISION_A4_BATCH_LABEL")
        hdc.StartPage()
        
        # 4. Tukar imej PIL A4 Master Sheet kepada objek grafik murni Windows (DIB)
        dib = ImageWin.Dib(imej_a4_master)
        
        # Dapatkan had maksimum keupayaan saiz fizikal kertas daripada pencetak
        lebar_had_kertas = hdc.GetDeviceCaps(110)   # PHYSICALWIDTH
        tinggi_had_kertas = hdc.GetDeviceCaps(111)  # PHYSICALHEIGHT
        
        # 5. Lukis imej A4 penuh terus ke dalam memori printer (Tajam, Kalis Herot & Tanpa UI Popup)
        dib.draw(hdc.GetHandleOutput(), (0, 0, lebar_had_kertas, tinggi_had_kertas))
        
        # 6. Lepaskan kertas dan tutup sesi cetakan dengan selamat
        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()
        win32print.ClosePrinter(hprinter)
        
        messagebox.showinfo("PRINT SUCCESS", "All batch labels successfully sent to printer queue!", parent=None)
        
    except Exception as e:
        # Fallback keselamatan jika pywin32 tiada: Guna kaedah os.startfile tetapi beri amaran
        messagebox.showwarning("Peringatan Sistem", f"Sistem cetakan senyap gagal. Menghantar ke Windows Spooler manual.\nRalat: {str(e)}")
        try:
            temp_path = "temp_fallback_print.png"
            imej_a4_master.save(temp_path)
            if sys.platform == "win32":
                os.startfile(temp_path, "print")
        except Exception as err:
            messagebox.showerror("CRITICAL ERROR", f"Gagal mencetak: {str(err)}")

def simpan_a4_master(imej_a4_master, inv_no_rujukan):
    """Fungsi pembantu asal untuk menyimpan fail imej kertas A4 ke komputer."""
    fail_clean = str(inv_no_rujukan).replace("/", "-").replace(":", "-").strip()
    path_fail = filedialog.asksaveasfilename(
        initialfile=f"BATCH_A4_INVOICE_{fail_clean}.png",
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        title="SIMPAN GRAFIK BATCH SHEET A4"
    )
    if path_fail:
        imej_a4_master.convert("RGB").save(path_fail, "PNG", quality=100)
        messagebox.showinfo("COMPLETE", "BATCH SHEET SUCCESSFULLY SAVED!")
