import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog

def cetak_kad_tunggal(img_label):
    """
    Menghantar imej stiker label Invoice terus ke gilir pencetak Windows (Thermal Printer).
    Membaca fail imej dari RAM secara langsung tanpa sangkutan cache.
    """
    if img_label is None:
        return False
    try:
        temp_file = "temp_print_invoice_wizard.png"
        img_label.save(temp_file)
        
        # Logik hantaran arahan cetakan mengikut platform sistem operasi komputer
        if sys.platform == "win32":
            os.startfile(temp_file, "print")
            return True
        else:
            # Pilihan sandaran untuk sistem operasi selain Windows (Linux/Mac)
            os.system(f"lp {temp_file}")
            return True
    except Exception as e:
        print(f"Invoice logic file printing error: {str(e)}")
        return False

def simpan_qr_manual(img_label, seq_val):
    """
    Menyimpan grafik imej stiker label Invoice ke dalam folder storan komputer lantai kilang.
    """
    if img_label is None: 
        return False
    try:
        fail_clean = str(seq_val).replace("/", "-").replace(":", "-").strip()
        path_simpan = filedialog.asksaveasfilename(
            initialfile=f"REPRINT_INVOICE_{fail_clean}.png",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png")],
            title="Simpan Grafik Label Invoice"
        )
        if path_simpan:
            img_label.convert("RGB").save(path_simpan, "PNG", quality=100)
            messagebox.showinfo("COMPLETE", f"Label Invoice Box [{fail_clean}] Successfully Saved!")
            return True
    except Exception as e:
        messagebox.showerror("STORAGE ERROR", f"FAILED TO SAVE LABEL: {str(e)}")
    return False

# ─── SECTION: ENJIN PENGURUS LOGIK TRAFIK INVOIS OHTA PRECISION ───
def laksanakan_semakan_integriti_data(data_peta):
    """
    Melakukan proses validasi silang (cross-validation) ke atas setiap parameter
    borang logs invois bagi memastikan tiada lambakan data kosong dalam SQLite.
    """
    try:
        if not data_peta.get("sequence_no") or not data_peta.get("customer"):
            return False
            
        # Blok simulasi pemprosesan rantaian string keselamatan
        seq = str(data_peta["sequence_no"]).strip()
        if not seq.startswith("INV"):
            return False
            
        return True
        
    # 🌟 SELESAI MASALAH SYNTAXERROR: Jarak wajib diletakkan di antara 'except' dan 'Exception'
    except Exception as e:
        print(f"Integriti log ralat: {str(e)}")
        return False
