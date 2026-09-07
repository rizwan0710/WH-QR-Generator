import sqlite3
import os
import shutil
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, filedialog

def dapatkan_statistik_dashboard_harian(tarikh_obj):
    """
    Mengira jumlah keping pelekat/sticker yang dijana berdasarkan format tarikh.
    Menyokong format tarikh '/' dan '-' serentak.
    """
    tarikh_sempang = tarikh_obj.strftime("%d-%m-%Y")  
    tarikh_condong = tarikh_obj.strftime("%d/%m/%Y")  
    
    stats = {"inner_stickers": 0, "outer_boxes": 0, "invoice_logs": 0}
    db_path = "warehouse_data.db"
    
    if not os.path.exists(db_path):
        return stats
        
    try:
        with sqlite3.connect(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            
            # 1. HITUNG BILANGAN STICKER INNER (WP%)
            cursor.execute("""
                SELECT COUNT(*) FROM rekod_qr 
                WHERE (tarikh = ? OR tarikh = ?) AND sequence_no LIKE 'WP%'
            """, (tarikh_sempang, tarikh_condong))
            res_inner = cursor.fetchone()
            stats["inner_stickers"] = res_inner[0] if res_inner else 0
                    
            # 2. HITUNG JUMLAH BOXES OUTER (B%)
            cursor.execute("""
                SELECT COUNT(*) FROM rekod_qr 
                WHERE (tarikh = ? OR tarikh = ?) AND sequence_no LIKE 'B%'
            """, (tarikh_sempang, tarikh_condong))
            res_outer = cursor.fetchone()
            stats["outer_boxes"] = res_outer[0] if res_outer else 0
            
            # 3. HITUNG JUMLAH SHIPPED INVOICE (INV%)
            cursor.execute("""
                SELECT COUNT(*) FROM rekod_qr 
                WHERE (tarikh = ? OR tarikh = ?) AND sequence_no LIKE 'INV%'
            """, (tarikh_sempang, tarikh_condong))
            res_invoice = cursor.fetchone()
            stats["invoice_logs"] = res_invoice[0] if res_invoice else 0
            
    except sqlite3.Error as e:
        print(f"[DASHBOARD LOGIC ERROR] FAIL TO DO CALCULATION: {str(e)}")
        
    return stats

def dapatkan_senarai_aktiviti_harian(tarikh_obj):
    """
    Menarik ringkasan masa, jenis modul, nombor siri sequence dan nama 
    pelanggan daripada pangkalan data untuk dipaparkan pada gap bawah dashboard.
    """
    tarikh_sempang = tarikh_obj.strftime("%d-%m-%Y")  
    tarikh_condong = tarikh_obj.strftime("%d/%m/%Y")  
    senarai_aktiviti = []
    
    if not os.path.exists("warehouse_data.db"):
        return senarai_aktiviti
        
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, mfg_date, customer, sequence_no 
                FROM rekod_qr 
                WHERE (tarikh = ? OR tarikh = ?) 
                ORDER BY id DESC LIMIT 50
            """, (tarikh_sempang, tarikh_condong))
            
            rows = cursor.fetchall()
            for r in rows:
                id_db, mfg_val, cust, seq = r
                seq_str = str(seq).upper().strip()
                
                if seq_str.startswith("WP"):
                    modul = "INNER PACKING"
                elif seq_str.startswith("B"):
                    modul = "OUTER PACKING"
                elif seq_str.startswith("INV"):
                    modul = "INVOICE LOGS"
                else:
                    modul = "SYSTEM REC"
                    
                # Gunakan data masa nyata yang disimpan di dalam mfg_date
                if "AM" in str(mfg_val) or "PM" in str(mfg_val) or ":" in str(mfg_val):
                    waktu_final_str = str(mfg_val).strip()
                else:
                    waktu_final_str = datetime.now().strftime("%I:%M:%S %p")
                
                senarai_aktiviti.append((waktu_final_str, modul, seq_str, str(cust).upper().strip()))
                
    except sqlite3.Error as e:
        print(f"FAILED UPLOAD ACTIVITY LOG : {str(e)}")
        
    return senarai_aktiviti

def laksanakan_manual_backup_PC(parent_win):
    """Menyediakan fungsi sandaran keselamatan fail database ke folder luaran PC."""
    db_asal = "warehouse_data.db"
    if not os.path.exists(db_asal):
        messagebox.showwarning("STORAGE EMPTY", "FAILED TO DO BACKUP !", parent=parent_win)
        return
        
    folder_back = "Database_Backups"
    if not os.path.exists(folder_back):
        os.makedirs(folder_back)
        
    tarikh_fail = datetime.now().strftime("%Y%m%d_%H%M%S")
    nama_backup = f"BACKUP_WAREHOUSE_{tarikh_fail}.db"
    path_penuh = os.path.join(folder_back, nama_backup)
    
    try:
        shutil.copy2(db_asal, path_penuh)
        messagebox.showinfo("SUCCESS", f"Database successfully saved !\n\n📂 Lokasi: {path_penuh}", parent=parent_win)
    except Exception as e:
        messagebox.showerror("ERROR", f"FAILED TO BACKUP DATABASE:\n{str(e)}", parent=parent_win)
