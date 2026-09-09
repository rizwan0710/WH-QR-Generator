import sqlite3
import datetime
import qrcode
import os
import re
from tkinter import messagebox, filedialog
from PIL import Image
import label_outer_designer as lod
import database_batch_preview  # Shared multi-page database grid window framework

def bersihkan_nama_folder(n):
    return "".join([c for c in n if c not in ['\\','/',':','*','?','"','<','>','|']]).strip()

def semak_adakah_inner_sudah_digunakan(seq_inner):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%' AND machine LIKE ?", (f"%{seq_inner}%",))
            res = cursor.fetchone()
            return res if res else None
    except:
        return None

def dapatkan_maklumat_inner(seq_inner):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, customer, drawing_no, part_no, quantity FROM rekod_qr WHERE sequence_no = ?", (str(seq_inner).strip(),))
            return cursor.fetchone()
    except:
        return None

def dapatkan_tarikh_inner_terlewat(senarai_inner):
    dates = []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            for seq in senarai_inner:
                cursor.execute("SELECT tarikh FROM rekod_qr WHERE sequence_no = ?", (seq,))
                row = cursor.fetchone()
                if row and row[0]:
                    try:
                        dt_obj = datetime.datetime.strptime(str(row[0]).strip(), "%d/%m/%Y")
                        dates.append(dt_obj)
                    except: pass
    except: pass
    return max(dates) if dates else None

def proses_submit_outer(win_outer, entry_date, entries_inner):
    tarikh_outer_obj = entry_date.get_date()
    tarikh_outer_str = tarikh_outer_obj.strftime("%d/%m/%Y")
    senarai_inner = [ent.get().strip().upper() for ent in entries_inner if ent.get().strip()]
            
    if not senarai_inner:
        messagebox.showwarning("Incomplete Fields", "Please scan or enter at least one Inner Box QR code!", parent=win_outer)
        return

    for idx, seq in enumerate(senarai_inner, start=1):
        outer_pendaftar = semak_adakah_inner_sudah_digunakan(seq)
        if outer_pendaftar:
            messagebox.showerror(
                "Duplicate Scan Error", 
                f"❌ INTEGRITY ERROR AT SLOT {idx}!\n\n"
                f"Inner Sequence [{seq}] Already Scanned at Outer Box ID: {outer_pendaftar[0]}.\n\n", 
                parent=win_outer
            )
            return

    data_pertama = dapatkan_maklumat_inner(senarai_inner[0])
    if not data_pertama:
        messagebox.showerror("ERROR", f"INNER BOX SEQUENCE [{senarai_inner[0]}] at Slot 1 DOES NOT EXIST!", parent=win_outer)
        return
        
    _, customer_utama, drw_utama, part_utama, _ = data_pertama
    total_qty = 0
    data_gabungan_final = []  
    
    for idx, seq in enumerate(senarai_inner, start=1):
        res = dapatkan_maklumat_inner(seq)
        if not res:
            messagebox.showerror("ERROR", f"SEQUENCE [{seq}] at SLOT {idx} CANNOT BE FOUND!", parent=win_outer)
            return
            
        _, cust, _, part_no_asli, qty = res
        
        if cust != customer_utama:
            messagebox.showerror(
                "MIXED CUSTOMER ERROR", 
                f"❌ CRITICAL CROSS-CUSTOMER WARNING!\n\n"
                f"MIXED DATA AT SLOT {idx}!\n\n"
                f"• SLOT 1 (Main): {customer_utama}\n"
                f"• SLOT {idx} (Error): {cust} (Series: {seq})\n\n"
                f"PLEASE ENSURE THAT ALL SLOTS BELONG TO THE SAME COMPANY!", 
                parent=win_outer
            )
            return
            
        qty_clean = str(qty).upper().replace("PCS", "").strip()
        if qty_clean.isdigit(): total_qty += int(qty_clean)
        data_gabungan_final.append((part_no_asli, str(qty)))

    tarikh_inner_terlewat = dapatkan_tarikh_inner_terlewat(senarai_inner)
    if tarikh_inner_terlewat and tarikh_outer_obj < tarikh_inner_terlewat:
        str_inner_terlewat = tarikh_inner_terlewat.strftime("%d/%m/%Y")
        messagebox.showerror("DATE ERROR", f"OUTER BOX DATE CANNOT BE EARLIER THAN INNER BOX DATE ({str_inner_terlewat})!", parent=win_outer)
        return

    tarikh_kod = datetime.datetime.now().strftime("%d%m%Y")
    prefix_seq = f"B{tarikh_kod}"
    rujukan_inner_gabung = ",".join(senarai_inner)
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix_seq}%",))
            rekod_terakhir = cursor.fetchone()
            nombor_running = int(str(rekod_terakhir[0])[-4:]) if (rekod_terakhir and rekod_terakhir[0]) else 0
            nombor_running += 1
            sequence_outer_final = f"{prefix_seq}{nombor_running:04d}"
            
            cursor.execute("""
                INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tarikh_outer_str, customer_utama, drw_utama, part_utama, f"{total_qty} PCS", tarikh_outer_str, rujukan_inner_gabung, "OUTER BOX", sequence_outer_final))
            conn.commit()
            
        img_qr = qrcode.QRCode(version=1, box_size=10, border=1)
        img_qr.add_data(sequence_outer_final)
        img_qr.make(fit=True)
        img_qr_m = img_qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img_label_final = lod.bina_imej_gabungan_akses(img_qr_m, data_gabungan_final, sequence_outer_final)
        
        # 🌟 SILENT BACKGROUND AUTO-SAVE SEQUENCE (NO POPUPS) 🌟
        try:
            tarikh_folder_nama = datetime.datetime.now().strftime("%d-%m-%Y")
            customer_folder_name = bersihkan_nama_folder(customer_utama)
            path_sub_folder = os.path.join("OUTER_STICKER", tarikh_folder_nama, customer_folder_name)
            if not os.path.exists(path_sub_folder): 
                os.makedirs(path_sub_folder)
            img_label_final.convert("RGB").save(os.path.join(path_sub_folder, f"OUTER_STICKER_{sequence_outer_final}.png"), "PNG", quality=100)
        except Exception: 
            pass

        # Launches the standardized 4-button multiple slider layout preview grid
        database_batch_preview.buka_popup_database_pukal_seragam(win_outer, [img_label_final], is_outer=True)
        
    except Exception as e:
        messagebox.showerror("DATABASE ERROR", f"FAILED TO EXECUTE OUTER BOX REGISTRY:\n{str(e)}", parent=win_outer)
