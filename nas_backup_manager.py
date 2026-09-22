import os
import sqlite3
import shutil
import threading
import socket
from datetime import datetime

def laksanakan_backup_ke_nas_async():
    """Melancarkan enjin backup berkembar (Database + Excel) ke latar belakang secara Threaded."""
    t = threading.Thread(target=_proses_salinan_excel_dan_db_nas, daemon=True)
    t.start()

def _proses_salinan_excel_dan_db_nas():
    """
    🏢 ENJIN SANDARAN LATAR BELAKANG NAS KILANG (THREADED COPIER ENGINE - FULL) 🏢
    Menguruskan kemas kini serentak bagi salinan fizikal fail .db dan laporan 
    formal Excel 4 Sheet (termasuk LABEL HISTORY) terus ke jajaran rangkaian Z:\\.
    """
    # 1. ATURAN LALUAN DISK NETWORK STORAGE OFFICE ANDA
    NAS_SERVER_ROOT = r"Z:\IT\IT\QR_SYS_Backup(DB)"
    db_asal = "warehouse_data.db"
    
    if not os.path.exists(db_asal):
        print("[NAS BACKUP ERROR] Fail pangkalan data 'warehouse_data.db' tidak dijumpai.")
        return
        
    try:
        # Mengesan nama pengenalan hos PC PC operator secara dinamik (Contoh: IT-IZWAN)
        try:
            computer_name = socket.gethostname().upper().replace(" ", "_")
        except Exception:
            computer_name = "UNKNOWN_STATION"
            
        pc_specific_backup_dir = os.path.join(NAS_SERVER_ROOT, computer_name)
        os.makedirs(pc_specific_backup_dir, exist_ok=True)
            
        # Penetapan sebutan nama fail penjepala mengikut standard korporat OHTA
        tarikh_hari_ini = datetime.now().strftime("%Y-%m-%d")
        
        nama_fail_db_backup = f"QR System Backup DB_{tarikh_hari_ini}.db"
        nama_fail_excel_backup = f"LIVE_WAREHOUSE_REPORT_{computer_name}.xlsx"
        
        laluan_db_nas = os.path.join(pc_specific_backup_dir, nama_fail_db_backup)
        laluan_excel_nas = os.path.join(pc_specific_backup_dir, nama_fail_excel_backup)
        
        # =============================================================
        # 🌟 BAHAGIAN A: UPDATE LIVE PHYSICAL DATABASE FILE (.db) 🌟
        # =============================================================
        try:
            shutil.copy(db_asal, laluan_db_nas)
            print(f"[NAS DB SUCCESS] Database copied successfully to: {laluan_db_nas}")
        except Exception as e_db:
            print(f"[NAS DB ERROR] Failed to copy physical database file: {str(e_db)}")

        # =============================================================
        # 🌟 BAHAGIAN B: UPDATE LIVE CORPORATE EXCEL REPORT (.xlsx) 🌟
        # =============================================================
        try:
            # Import enjin excel_generator utama yang telah kita betulkan lajur & teks dunianya
            import excel_generator
            
            # 🚀 SINCRONISASI BIJAK: Panggil fungsi penjanaan 4 Sheet murni ke destinasi folder NAS Z:\ 🚀
            # Fungsi ini automatik menguruskan penukaran nama lajur dan pembetulan teks di dalam file excel!
            excel_generator.jana_laporan_excel_tiga_tab(db_asal, laluan_excel_nas)
            print(f"[NAS EXCEL SUCCESS] Corporate 4-Sheet report updated successfully at: {laluan_excel_nas}")
            
        except Exception as e_excel:
            print(f"[NAS EXCEL ERROR] Failed to update synchronized corporate spreadsheet: {str(e_excel)}")

    except Exception as e_fatal:
        print(f"[NAS CRITICAL FAILURE] Threaded automation context disrupted: {str(e_fatal)}")
