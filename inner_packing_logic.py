import os
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
import win32print
from PIL import Image

def cetak_qr(img_gabung):
    """
    🖨️ ENJIN VISUAL AUTO-SIZING (KUNCI 70x50mm + PAPAR POP-UP WINDOWS) 🖨️
    Memaksa Windows memilih saiz kertas 70x50mm secara automatik sebelum melancarkan 
    tetingkap dialog cetakan gambar rasmi Windows untuk operator semak.
    """
    try:
        temp_file = "temp_print_inner.png"
        
        # 1. Kunci spesifikasi saiz fizikal imej stiker Inner (70 mm x 50 mm)
        img_bersaiz_tepat = img_gabung.resize((826, 590), Image.Resampling.LANCZOS)
        img_bersaiz_tepat.save(temp_file)
        
        if sys.platform == "win32":
            try:
                # 2. 🌟 ENJIN AUTO-SET DEVICE MODE Windows 🌟
                # Dapatkan nama pencetak default yang aktif di PC kilang
                nama_printer = win32print.GetDefaultPrinter()
                hprinter = win32print.OpenPrinter(nama_printer)
                
                # Ekstrak struktur tetapan pDevMode semasa pencetak
                info_pemacu = win32print.GetPrinter(hprinter, 2)
                devmode = info_pemacu["pDevMode"]
                
                # Beritahu Windows kita mahu ubah tetapan saiz custom (Width & Length)
                devmode.Fields |= 0x4 | 0x8  # DM_PAPERLENGTH | DM_PAPERWIDTH
                devmode.PaperWidth = 700     # Paksa set 70 mm
                devmode.PaperLength = 500    # Paksa set 50 mm
                
                # Kemaskini tetapan driver pencetak secara sementara di memori Windows
                win32print.SetPrinter(hprinter, 2, info_pemacu, 0)
                win32print.ClosePrinter(hprinter)
                print("Berjaya auto-set saiz pemacu kertas ke 70x50mm.")
            except Exception as e_driver:
                # Jika driver jenis terkunci (locked permission), abaikan ralat dan teruskan ke paparan
                print(f"Nota pemacu (Sila set saiz manual jika perlu): {str(e_driver)}")

            # 🌟 3. PAPAR POP-UP WINDOWS: Melancarkan tetingkap dialog rasmi Windows untuk operator klik Print
            os.startfile(temp_file, "print")
            
            # Bersihkan fail sisa dalam thread latar belakang selepas 20 saat supaya RAM PC tidak hang
            threading.Thread(target=lambda: [time.sleep(20), os.remove(temp_file) if os.path.exists(temp_file) else None], daemon=True).start()
        else:
            messagebox.showwarning("SYSTEM OPERATION", "PRINTER FUNCTION ONLY SUPPORTS WINDOWS.")
            
    except Exception as e:
        messagebox.showerror("WARNING", f"FAILED TO PRINT: {str(e)}")

def simpan_qr_manual(img_gabung, seq_no):
    """[HD QUALITY] Menyimpan imej label Inner (WP%) secara manual ke dalam pemacu PC."""
    if img_gabung is None:
        messagebox.showerror("FAILED", "DATA LABEL EMPTY OR CANNOT BE FOUND!")
        return

    fail_clean = str(seq_no).replace("/", "-").replace(":", "-").strip()

    path_fail = filedialog.asksaveasfilename(
        initialfile=f"INNER_{fail_clean}.png", 
        defaultextension=".png", 
        filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        title="SIMPAN GRAFIK LABEL INNER BOX"
    )
    
    if path_fail:
        try:
            if img_gabung.mode in ("RGBA", "P"):
                img_untuk_simpan = img_gabung.convert("RGB")
            else:
                img_untuk_simpan = img_gabung

            img_untuk_simpan.save(path_fail, "PNG", quality=100)
            messagebox.showinfo("SUCCESS", f"Label Inner Box [{fail_clean}] SUCCESSFULLY SAVED!")
        except Exception as e:
            messagebox.showerror("ERROR", f"WINDOWS SYSTEM FAILED TO SAVE:\n{str(e)}")
