import sqlite3
import re
import datetime
from datetime import datetime
import qrcode
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import label_outer_designer as lod
import database_manager as dbm

# Penjejak rujukan butang submit utama borang luar untuk logik kunci keselamatan
btn_submit_ref = None 

def bersihkan_nama_folder(nama):
    """Membuang aksara yang dilarang dalam sistem fail Windows/OS untuk folder"""
    for a in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']: 
        nama = nama.replace(a, '_')
    return nama.strip()

def dapatkan_maklumat_inner(seq_no):
    """Mengambil data Kuantiti dan Customer bagi siri WP% secara eksplisit menggunakan nama kunci pautan."""
    kod_bersih = str(seq_no).strip().upper()
    
    if not kod_bersih.startswith("WP"):
        return {"error": "❌ SEKATAN JENIS KOD BAR!\n\nBorang Outer Packing hanya menerima INNER LABEL (WP%) sahaja!"}
        
    try:
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            # 🌟 Menyatakan lajur dengan jelas supaya indeks tidak lari
            cursor.execute("SELECT quantity, customer FROM rekod_qr WHERE sequence_no = ?", (kod_bersih,))
            res = cursor.fetchone()
            if res:
                return {
                    "qty": str(res[0]).strip(),       # Contoh: "100 PCS"
                    "customer": str(res[1]).strip()   # Contoh: "ALPSMY"
                }
            return None
    except Exception as e:
        print(f"Error dapatkan_maklumat_inner: {e}")
        return None


def semak_adakah_inner_sudah_digunakan(inner_seq):
    """Menyemak status silang sekiranya kod siri WP% telah didaftarkan pada kotak luar lain di database pusat NAS."""
    if not inner_seq:
        return None
        
    # Bersihkan string siri daripada sebarang ruang kosong tersembunyi
    inner_seq_bersih = str(inner_seq).strip().upper()
    
    try:
        # ✅ DIBAIKI: Menggunakan kaedah sambungan rasmi get_db_connection() pusat rangkaian NAS
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            
            # 🛠️ SEMAKAN LAJUR PINTAR: Sokong sequence_no huruf kecil ATAU [Sequence No] format baru
            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError:
                lajur_seq = "sequence_no"
            
            # ✅ KEMASKINI LOGIK: Menggunakan UPPER(TRIM()) untuk padanan siri murni terpusat
            query = f"""
                SELECT {lajur_seq} 
                FROM rekod_qr 
                WHERE lotcard_no = 'OUTER BOX' 
                  AND UPPER(TRIM(machine)) LIKE ?
            """
            cursor.execute(query, (f"%{inner_seq_bersih}%",))
            
            res = cursor.fetchone()
            return res[0] if res and res[0] is not None else None
            
    except Exception as e:
        print(f"[OUTER LOGIC ERROR] Gagal menyemak penggunaan siri inner di database pusat: {str(e)}")
        return None


def cetak_qr(img_label):
    """Menghantar imej label Outer Box terus ke gilir pencetak thermal Windows."""
    try:
        temp = "temp_print_outer.png"
        img_label.save(temp)
        if sys.platform == "win32": 
            os.startfile(temp, "print")
    except Exception as e: 
        print(e)

def simpan_qr_manual(img, seq):
    """Menyimpan fail imej stiker luar secara manual ke komputer."""
    p = filedialog.asksaveasfilename(initialfile=f"OUTER_STICKER_{seq}.png", defaultextension=".png", title="Save")
    if p: 
        img.convert("RGB").save(p, "PNG")
        messagebox.showinfo("Success", "Saved!")

def paparkan_pop_up_imej_label(win_outer, entries, img_label, title_text, seq_no):
    """🌟 BATCH POPUP VIEW (STANDARDIZED WITH AUTOMATIC UNLOCK ENGINE) 🌟"""
    tp = tk.Toplevel(win_outer.master)
    tp.title(f"PREVIEW - {seq_no}")
    tp.geometry("540x510+420+120") # Dimensi diseragamkan dengan modul Invois & Inner
    tp.configure(bg="#F8F9FA")
    tp.grab_set()
    
    tk.Label(tp, text=title_text, font=("Segoe UI", 11, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=12)
    
    frame_canvas_bg = tk.Frame(tp, bg="white", bd=1, relief="groove")
    frame_canvas_bg.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    
    lbl = tk.Label(frame_canvas_bg, bg="white")
    lbl.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    
    itk = ImageTk.PhotoImage(img_label.resize((420, 200), Image.Resampling.LANCZOS))
    lbl.config(image=itk)
    lbl.image = itk
    
    def tutup_dan_reset_borang():
        """🌟 AUTOMATIC UNLOCKER: Membuka kunci borang dan mengosongkan entri selepas popup ditutup 🌟"""
        global btn_submit_ref
        
        # 1. Buka semula kunci akses kesemua medan input
        for e in entries: 
            e.config(state="normal")
            e.delete(0, tk.END)
            
        # 2. Kembalikan fungsi dan gaya asal butang submit utama borang
        if btn_submit_ref and btn_submit_ref.winfo_exists():
            btn_submit_ref.config(state="normal", text="GENERATE QR", bg="#0284C7")
            
        if entries and len(entries) > 0: 
            entries[0].focus_set()
            
        tp.destroy()
        
    f_btn = tk.Frame(tp, bg="#F8F9FA")
    f_btn.pack(side=tk.BOTTOM, pady=15, fill=tk.X, padx=20)
    
    btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}
    
    tk.Button(f_btn, text="🖨️ PRINT", command=lambda: cetak_qr(img_label), bg="#22C55E", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    #tk.Button(f_btn, text="💾 SAVE", command=lambda: simpan_qr_manual(img_label, seq_no), bg="#F59E0B", **btn_style).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    tk.Button(f_btn, text="❌ CLOSE", command=tutup_dan_reset_borang, bg="#374151", **btn_style).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

def proses_submit_outer(win_outer, entry_date, entries_inner, btn_submit_widget=None):
    """🌟 MAIN SUBMIT LOGIC WITH ANTI-DUPLICATE SAFETY LOCK (CENTRAL NAS & ENGLISH EDITION) 🌟"""
    global btn_submit_ref
    
    # Store references to UI submit buttons across main canvas wrappers
    if btn_submit_widget:
        btn_submit_ref = btn_submit_widget

    tarikh_str = entry_date.get() if hasattr(entry_date, 'get') else str(entry_date)
    senarai_inner = [e.get().strip().upper() for e in entries_inner if e.get().strip()]
    if not senarai_inner: 
        return messagebox.showwarning("INCOMPLETE FORM", "PLEASE SCAN OR ENTER THE SERIAL NUMBER!", parent=win_outer)

    # 1. CURRENT TRANSACTION DUPLICATE FILTER FRAMEWORK
    if len(senarai_inner) != len(set(senarai_inner)):
        return messagebox.showerror(
            "SAME FORM DUPLICATE ERROR", 
            "❌ FORM RE-SCAN RESTRICTION!\n\n"
            "THIS NUMBER HAS ALREADY BEEN SCANNED ON THIS FORM!\n\n"
            "PLEASE REMOVE DUPLICATE ENTRIES BEFORE REGISTERING.", 
            parent=win_outer
        )

    # 2. CENTRAL NAS DATABASE DUPLICATE RECORD PROTECTION TRACE
    for idx, seq in enumerate(senarai_inner, start=1):
        outer_id = semak_adakah_inner_sudah_digunakan(seq)
        if outer_id: 
            return messagebox.showerror(
                "DUPLICATE REGISTRATION DETECTED", 
                f"❌ CRITICAL ERROR AT SLOT {idx}!\n\n"
                f"SERIAL NUMBER [{seq}] HAS ALREADY BEEN SCANNED AT OUTER BOX: {outer_id}", 
                parent=win_outer
            )

    # Extract target values for Slot 1 to establish primary customer references
    data_1 = dapatkan_maklumat_inner(senarai_inner[0])
    
    if isinstance(data_1, dict) and "error" in data_1:
        return messagebox.showerror("DATABASE OPERATION FAILURE", data_1["error"], parent=win_outer)
        
    if not data_1: 
        return messagebox.showerror(
            "DATA NOT FOUND", 
            f"❌ CRITICAL ERROR AT SLOT 1!\n\n"
            f"SERIAL NUMBER [{senarai_inner[0]}] DOES NOT EXIST IN THE CENTRAL MANAGEMENT LOGS DIRECTORY!", 
            parent=win_outer
        )
        
    # Extract structural configuration details cleanly regardless of tuple or dictionary objects
    if isinstance(data_1, dict):
        customer_utama = data_1.get("customer", "").upper()
    else:
        customer_utama = data_1.get("customer", "").upper() if hasattr(data_1, 'get') else str(data_1[1]).strip().upper()
        
    total_qty, data_final = 0, []
    
    for idx, seq in enumerate(senarai_inner, start=1):
        res = dapatkan_maklumat_inner(seq)
        if not res or (isinstance(res, dict) and "error" in res): 
            return messagebox.showerror(
                "DATA NOT FOUND", 
                f"❌ CRITICAL ERROR AT SLOT {idx}!\n\n"
                f"SERIAL NUMBER [{seq}] IS INVALID OR DOES NOT EXIST IN THE CENTRAL MANAGEMENT LOGS DIRECTORY!", 
                parent=win_outer
            )
        
        if isinstance(res, dict):
            cust = res.get("customer", "").upper()
            qty = res.get("qty", "100 PCS")
        elif isinstance(res, (tuple, list)):
            qty = str(res[0]).strip()
            cust = str(res[1]).strip().upper()
        else:
            cust = customer_utama
            qty = "1000_PCS"
        
        # 🌟 LIVE CONVERSION: Pull genuine component Part Number from NAS directory instead of WP prefix codes 🌟
        part_no_sebenar = seq
        try:
            conn_p = dbm.get_db_connection()
            with conn_p:
                cursor_p = conn_p.cursor()
                
                # Check for dynamic Sequence No column layout standard
                lajur_seq_check = "sequence_no"
                try:
                    cursor_p.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                    lajur_seq_check = "[Sequence No]"
                except sqlite3.OperationalError: pass
                
                cursor_p.execute(f"SELECT part_no FROM rekod_qr WHERE {lajur_seq_check} = ?", (seq,))
                row_p = cursor_p.fetchone()
                if row_p and row_p[0]:
                    part_no_sebenar = str(row_p[0]).strip()
        except:
            if isinstance(res, dict) and "part_no" in res:
                part_no_sebenar = str(res.get("part_no", seq)).strip()
        
        # Enforce sanitization limits against accidental transaction corruption traces
        if "/" in qty or "-" in qty or len(qty) > 10:
            qty = "100 PCS"
        
        # Consolidated mixing restriction barrier validation
        if cust != customer_utama:
            return messagebox.showerror(
                "MIXED CUSTOMER TRANSACTION DETECTED", 
                f"❌ CUSTOMER MISMATCH VIOLATION!\n\n"
                f"• SLOT 1 RECOGNIZED AS: {customer_utama}\n"
                f"• SLOT {idx} MISMATCH DETECTED AS: {cust} (SN: {seq})\n\n"
                f"CONSOLIDATED CARGO MIXING IS STRICTLY FORBIDDEN ON THE PRODUCTION FLOOR!", 
                parent=win_outer
            )
            
        qty_c = str(qty).upper().replace("PCS", "").strip()
        try:
            total_qty += int(float(qty_c))
        except ValueError:
            digits = "".join([c for c in qty_c if c.isdigit()])
            if digits: 
                total_qty += int(digits)
            else:
                total_qty += 100
                qty_c = "100"
            
        # Injects genuine part_no token definitions directly onto visual label configurations
        data_final.append((part_no_sebenar, f"{qty_c} PCS"))

    # Time markers formatting
    try:
        waktu_kini = datetime.now()
    except:
        import datetime as dt_module
        waktu_kini = dt_module.datetime.now()
        
    prefix = f"B{waktu_kini.strftime('%y%m%d')}"
    
    try:
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            
            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError:
                lajur_seq = "sequence_no"
                
            last = cursor.execute(f"SELECT {lajur_seq} FROM rekod_qr WHERE {lajur_seq} LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",)).fetchone()
            
            # Extracts running numeric values accurately to avoid tuple breakdown crashes
            run_no = 1
            if last and last[0]:
                import re
                nombor_akhir = re.findall(r'\d+', str(last[0]))
                if nombor_akhir:
                    run_no = int(str(nombor_akhir[-1])[-4:]) + 1
                    
            seq_outer = f"{prefix}{run_no:04d}"
            
            cursor.execute(f"""
                INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, {lajur_seq}) 
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (tarikh_str, customer_utama, "COMBINED", "CONSOLIDATED", f"{total_qty} PCS", tarikh_str, ",".join(senarai_inner), "OUTER BOX", seq_outer))
            conn.commit()
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_outer)
        qr.make(fit=True)
        img_label = lod.bina_imej_gabungan_akses(qr.make_image().convert("RGB"), data_final, seq_outer)
        
        try:
            nama_folder_bersih = "".join([c for c in customer_utama if c.isalnum() or c in (' ', '_', '-')]).strip()
            folder = os.path.join("OUTER_STICKER", waktu_kini.strftime("%d-%m-%Y"), nama_folder_bersih)
            if not os.path.exists(folder): 
                os.makedirs(folder)
            img_label.convert("RGB").save(os.path.join(folder, f"OUTER_STICKER_{seq_outer}.png"), "PNG")
        except: 
            pass

        # 🌟 LOCK FORM INTERACTIVELY UPON SUCCESSFUL REGISTRATION ROUTINES 🌟
        if 'btn_submit_ref' in globals() and btn_submit_ref and btn_submit_ref.winfo_exists():
            btn_submit_ref.config(state="disabled", text="🔒 REGISTRATION LOCKED (COMPLETED)", bg="#64748B")
            
        for e in entries_inner:
            if hasattr(e, 'config'):
                e.config(state="disabled")

        paparkan_pop_up_imej_label(win_outer, entries_inner, img_label, "OUTER PACKING LABEL GENERATED", seq_outer)
        
    except Exception as e: 
        messagebox.showerror(
            "DATABASE CRITICAL FAULT", 
            f"CRITICAL OVERRIDE ENCOUNTERED WHILE COMMITTING TRANSACTION LOGS INTO NAS DIRECTORIES:\n\n{str(e)}", 
            parent=win_outer
        )


