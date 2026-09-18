import sqlite3
import os
import shutil
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, filedialog
import excel_generator  # Connects cleanly to external 3-tab engine

def dapatkan_statistik_dashboard_harian(tarikh_obj):
    tarikh_sempang = tarikh_obj.strftime("%d-%m-%Y")  
    tarikh_condong = tarikh_obj.strftime("%d/%m/%Y")  
    stats = {"inner_stickers": 0, "outer_boxes": 0, "invoice_logs": 0}
    db_path = "warehouse_data.db"
    if not os.path.exists(db_path): return stats
    try:
        with sqlite3.connect(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            
            # 🌟 KOREKSI UTAMA: Ditambah indeks [0] di hujung fetchone() untuk mengekstrak hanya nilai integer bersih dari tuple!
            cursor.execute("SELECT COUNT(*) FROM rekod_qr WHERE (tarikh = ? OR tarikh = ?) AND sequence_no LIKE 'WP%'", (tarikh_sempang, tarikh_condong))
            r_in = cursor.fetchone()
            stats["inner_stickers"] = r_in[0] if (r_in and r_in[0] is not None) else 0
            
            cursor.execute("SELECT COUNT(*) FROM rekod_qr WHERE (tarikh = ? OR tarikh = ?) AND sequence_no LIKE 'B%'", (tarikh_sempang, tarikh_condong))
            r_out = cursor.fetchone()
            stats["outer_boxes"] = r_out[0] if (r_out and r_out[0] is not None) else 0
            
            cursor.execute("SELECT COUNT(*) FROM rekod_qr WHERE (tarikh = ? OR tarikh = ?) AND sequence_no LIKE 'INV%'", (tarikh_sempang, tarikh_condong))
            r_inv = cursor.fetchone()
            stats["invoice_logs"] = r_inv[0] if (r_inv and r_inv[0] is not None) else 0
    except Exception as e: 
        print(f"Error stats: {e}")
    return stats

def dapatkan_senarai_aktiviti_harian(tarikh_obj):
    tarikh_sempang = tarikh_obj.strftime("%d-%m-%Y")  
    tarikh_condong = tarikh_obj.strftime("%d/%m/%Y")  
    senarai_aktiviti = []
    if not os.path.exists("warehouse_data.db"): return senarai_aktiviti
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, mfg_date, customer, sequence_no FROM rekod_qr WHERE (tarikh = ? OR tarikh = ?) ORDER BY id DESC LIMIT 50", (tarikh_sempang, tarikh_condong))
            for r in cursor.fetchall():
                id_db, mfg_val, cust, seq = r
                seq_str = str(seq).upper().strip()
                modul = "INNER PACKING" if seq_str.startswith("WP") else "OUTER PACKING" if seq_str.startswith("B") else "INVOICE LOGS" if seq_str.startswith("INV") else "SYSTEM REC"
                waktu_final_str = str(mfg_val).strip() if ("AM" in str(mfg_val) or "PM" in str(mfg_val) or ":" in str(mfg_val)) else datetime.now().strftime("%I:%M:%S %p")
                senarai_aktiviti.append((waktu_final_str, modul, seq_str, str(cust).upper().strip()))
    except Exception as e: print(f"Error log: {e}")
    return senarai_aktiviti

def laksanakan_manual_backup_PC(parent_win):
    pass

def laksanakan_auto_backup_NAS(parent_win=None, mod_manual=False):
    """Routes backup signal based on automatic startup execution or manual button click."""
    if mod_manual:
        _proses_generate_report_manual_save_as(parent_win)
    else:
        t = threading.Thread(target=_proses_salinan_fizikal_nas_silent, daemon=True)
        t.start()

def _proses_salinan_fizikal_nas_silent():
    LALUAN_NAS_SERVER = r"Z:\IT\IT\QR_SYS_Backup(DB)"
    db_asal = "warehouse_data.db"
    if not os.path.exists(db_asal): return
    try:
        if not os.path.exists(LALUAN_NAS_SERVER): os.makedirs(LALUAN_NAS_SERVER)
        tarikh_hari_ini = datetime.now().strftime("%Y-%m-%d")
        nama_backup_nas = f"QR System Backup DB_{tarikh_hari_ini}.db"
        shutil.copy(db_asal, os.path.join(LALUAN_NAS_SERVER, nama_backup_nas))
        
        nama_excel_nas = f"LAPORAN_STICKER_QR_{tarikh_hari_ini}.xlsx"
        excel_generator.jana_laporan_excel_tiga_tab(db_asal, os.path.join(LALUAN_NAS_SERVER, nama_excel_nas))
        _laksanakan_auto_clean_fail_lama_nas(LALUAN_NAS_SERVER)
    except: pass

def _proses_generate_report_manual_save_as(parent_win):
    """Launches the native Windows File Explorer to let users choose their custom export directory."""
    db_asal = "warehouse_data.db"
    if not os.path.exists(db_asal):
        return messagebox.showerror("ERROR", "Local Database file not found!", parent=parent_win)
        
    tarikh_hari_ini = datetime.now().strftime("%Y-%m-%d")
    nama_fail_cadangan = f"COMPILATION_LOGISTICS_REPORT_{tarikh_hari_ini}.xlsx"
    
    path_pilihan_user = filedialog.asksaveasfilename(
        title="CHOOSE WHERE TO SAVE COMPILATION REPORT",
        initialfile=nama_fail_cadangan,
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
        parent=parent_win
    )
    
    if not path_pilihan_user:
        return

    try:
        excel_generator.jana_laporan_excel_tiga_tab(db_asal, path_pilihan_user)
        messagebox.showinfo(
            "REPORT EXPORTED", 
            f"Excel Compilation Report successfully created and saved!\n\n"
            f"📂 Location: {path_pilihan_user}\n\n"
            f"Your 3-sheet premium logistics report is ready for viewing.", 
            parent=parent_win
        )
    except Exception as e:
        messagebox.showerror("SAVE FAILED", f"Failed to save Excel file at chosen location!\n\nError: {str(e)}", parent=parent_win)

def _laksanakan_auto_clean_fail_lama_nas(folder_nas):
    try:
        had_masa = datetime.now() - timedelta(days=30)
        for nama_fail in os.listdir(folder_nas):
            if (nama_fail.startswith("QR System Backup DB_") or nama_fail.startswith("LAPORAN_STICKER_QR_")) and (nama_fail.endswith(".db") or nama_fail.endswith(".xlsx") or nama_fail.endswith(".csv")):
                laluan = os.path.join(folder_nas, nama_fail)
                if datetime.fromtimestamp(os.path.getmtime(laluan)) < had_masa: os.remove(laluan)
    except: pass
