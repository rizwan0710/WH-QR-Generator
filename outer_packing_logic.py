import os
import sys
import time
import sqlite3
import qrcode
import re
import threading
from datetime import datetime
from tkinter import messagebox, filedialog
import label_outer_designer as lod
import win32print

def cetak_qr(img_label):
    """🖨️ ENJIN VISUAL AUTO-SIZING OUTER (KUNCI 40x80mm + PAPAR POP-UP WINDOWS) 🖨️"""
    try:
        temp_file = "temp_print_outer.png"
        img_bersaiz_tepat = img_label.resize((1510, 3020), Image.Resampling.LANCZOS)
        img_bersaiz_tepat.save(temp_file)
        
        if sys.platform == "win32":
            try:
                nama_printer = win32print.GetDefaultPrinter()
                hprinter = win32print.OpenPrinter(nama_printer)
                info_pemacu = win32print.GetPrinter(hprinter, 2)
                devmode = info_pemacu["pDevMode"]
                devmode.Fields |= 0x4 | 0x8
                devmode.PaperWidth = 400     
                devmode.PaperLength = 800    
                win32print.SetPrinter(hprinter, 2, info_pemacu, 0)
                win32print.ClosePrinter(hprinter)
            except: pass
            os.startfile(temp_file, "print")
            threading.Thread(target=lambda: [time.sleep(20), os.remove(temp_file) if os.path.exists(temp_file) else None], daemon=True).start()
    except Exception as e:
        messagebox.showerror("WARNING", f"FAILED TO PRINT: {str(e)}")

def simpan_qr_manual(img_gabung, seq_outer):
    if img_gabung is None: return
    fail_bersih = str(seq_outer).replace("/", "-").replace(":", "-").strip()
    path_fail = filedialog.asksaveasfilename(initialfile=f"OUTER_{fail_bersih}.png", defaultextension=".png", filetypes=[("PNG Image", "*.png")])
    if path_fail:
        img_gabung.convert("RGB").save(path_fail, "PNG", quality=100)
        messagebox.showinfo("SUCCESS", "Outer Box Label Image Successfully saved!")

def dapatkan_maklumat_inner(seq_no):
    """Mengambil data Kuantiti dan Customer bagi siri WP% dari database dengan SEKATA KEPALA KOD WP."""
    kod_bersih = str(seq_no).strip().upper()
    
    # 🌟 KUNCI SEKATAN UTAMA: Tolak jika kod bar yang diimbas bukan bermula dengan kepala 'WP' (Inner Label)
    if not kod_bersih.startswith("WP"):
        return {"error": "❌ SEKATAN JENIS KOD BAR!\n\nBorang Outer Packing INI hanya boleh mengimbas stiker dari jenis INNER LABEL (WP%) sahaja!\n\nKod bar Outer (B%) dan Invoice (INV%) ditolak secara mutlak!"}
        
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity, customer FROM rekod_qr WHERE sequence_no = ?", (kod_bersih,))
            res = cursor.fetchone()
            if res:
                return {"qty": str(res[0]).strip(), "customer": str(res[1]).strip().upper()}
            return None
    except sqlite3.Error:
        return None

def semak_adakah_inner_sudah_digunakan(seq_no):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%' AND machine LIKE ?", (f"%{str(seq_no).strip().upper()}%",))
            res = cursor.fetchone()
            return True if res else False
    except sqlite3.Error:
        return False

def jana_nombor_siri_outer(tarikh_pola):
    pola_carian = f"B{tarikh_pola}%"
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (pola_carian,))
            max_seq = cursor.fetchone()
            if max_seq and max_seq[0]:
                nombor_akhir = re.findall(r'\d+', str(max_seq[0]))
                if nombor_akhir:
                    return int(str(nombor_akhir[-1])[-4:]) + 1
        return 1
    except Exception:
        return 1

def simpan_dan_jana_grafik(senarai_wp_terpilih, customer_name):
    waktu_kini = datetime.now()
    tarikh_pola = waktu_kini.strftime("%y%m%d")
    bil_hari_ini = jana_nombor_siri_outer(tarikh_pola)
    
    seq_outer = f"B{tarikh_pola}{bil_hari_ini:04d}"
    tarikh_kini = waktu_kini.strftime("%d/%m/%Y")
    rujukan_inner_gabung = ",".join(senarai_wp_terpilih).upper()
    
    data_gabungan_final = []
    total_qty_all = 0
    
    for s in senarai_wp_terpilih:
        info = dapatkan_maklumat_inner(s)
        if info and "qty" in info:
            q_val = info["qty"]
            data_gabungan_final.append((s.upper(), q_val))
            try: 
                clean_qty = str(q_val).upper().replace("PCS", "").strip()
                total_qty_all += int(float(clean_qty))
            except ValueError: pass
        
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tarikh_kini, customer_name, "COMBINED", "CONSOLIDATED", f"{total_qty_all} PCS", tarikh_kini, rujukan_inner_gabung, "OUTER BOX", seq_outer))
            conn.commit()
    except sqlite3.Error as e:
        raise Exception(f"FAILED TO SAVE AT DATABASE: {str(e)}")
        
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(seq_outer)
    qr.make(fit=True)
    img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    img_gabung = lod.bina_imej_gabungan_akses(img_qr_mentah, data_gabungan_final, seq_outer)
    return img_gabung, seq_outer
