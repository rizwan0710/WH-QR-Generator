import os
import shutil
import threading
from datetime import datetime

def laksanakan_backup_ke_nas_async():
    """Melancarkan enjin backup ke NAS secara latar belakang (Threaded) supaya UI tidak sangkut/lag."""
    t = threading.Thread(target=_proses_salinan_fizikal_nas, daemon=True)
    t.start()

def _proses_salinan_fizikal_nas():
    """Enjin teras yang melakukan operasi semakan direktori dan salinan fail pangkalan data."""
    # 🌟 HALAMAN ATURAN NAS & FORMAT NAMA KHAS ANDA 🌟
    IP_NAS = "192.168.100.2"
    NAMA_FOLDER_KONGSI = "Warehouse_Backup" # Sila tukar nama folder shared NAS anda jika berbeza
    LALUAN_NAS_SERVER = rf"\\{IP_NAS}\{NAMA_FOLDER_KONGSI}"
    
    fail_lokal_db = "warehouse_data.db"
    
    if not os.path.exists(fail_lokal_db):
        print("[NAS BACKUP] Ralat: Fail database tempatan tidak dijumpai.")
        return
        
    try:
        # Bina direktori folder backup di dalam NAS jika belum wujud
        if not os.path.exists(LALUAN_NAS_SERVER):
            try:
                os.makedirs(LALUAN_NAS_SERVER)
            except Exception:
                # Jika Windows memerlukan kelayakan rangkaian, sekat crash secara selamat
                print("[NAS BACKUP] Amaran: Laluan rangkaian NAS tidak dapat diakses atau memerlukan kebenaran login.")
                return
            
        # 🌟 FORMAT NAMA FAIL: QR System Backup DB (Tarikh Hari Ini) 🌟
        tarikh_hari_ini = datetime.now().strftime("%Y-%m-%d")
        nama_fail_backup = f"QR System Backup DB_{tarikh_hari_ini}.db"
        laluan_penuh_nas = os.path.join(192.168.100.2, QR_System_Backup_DB)
        
        # PROSES AUTO BACKUP EVERY DAY: 
        # Menyalin fail database fizikal berserta timestamp meta-data
        shutil.copy2(fail_lokal_db, laluan_penuh_nas)
        print(f"[NAS BACKUP] Berjaya dihantar ke NAS -> {nama_fail_backup}")
        
    except Exception as e_nas:
        print(f"[NAS BACKUP] Amaran Rangkaian: Kegagalan sambungan backup ke server NAS ({str(e_nas)})")
