import sqlite3
import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# 1. LOCAL DYNAMIC ENVIRONMENT PATH RESOLUTION
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOCAL_DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(LOCAL_DATA_DIR, "warehouse_data.db")

STICKER_FOLDERS = [
    os.path.join(BASE_DIR, "INNER_STICKER"),
    os.path.join(BASE_DIR, "OUTER_STICKER"),
    os.path.join(BASE_DIR, "INVOICE_STICKER")
]

def get_db_connection():
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH, timeout=10)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except sqlite3.OperationalError:
        pass
    return conn

def siapkan_database():
    for folder in STICKER_FOLDERS:
        if not os.path.exists(folder): 
            os.makedirs(folder, exist_ok=True)
            
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)
    
    with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rekod_qr (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                tarikh TEXT, 
                customer TEXT, 
                drawing_no TEXT, 
                part_no TEXT, 
                quantity TEXT, 
                mfg_date TEXT, 
                machine TEXT, 
                lotcard_no TEXT, 
                sequence_no TEXT UNIQUE
            )
        """)
        conn.commit()

def initialize_database_schema():
    siapkan_database()

def laksanakan_auto_clean_orphaned_logs():
    """
    🧹 ENJIN PEMBERSIHAN BERANTAI SEMASA REFRESH (BULLETPROOF CONTEXT) 🧹
    Memastikan jika data asal (Inner) dipadam, data Outer & Invoice terkait dibuang dari database semasa refresh!
    """
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            
            # 1. Dapatkan senarai semua sequence_no Inner (WP) yang masih wujud
            cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'WP%'")
            wujud_inner = [r[0] for r in cursor.fetchall() if r[0]]
            
            # 2. Ambil semua data Outer (B) untuk disemak pautannya
            cursor.execute("SELECT id, machine, sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%'")
            semua_outer = cursor.fetchall()
            
            for id_db, mach, seq in semua_outer:
                pautan_inner_wujud = False
                # Pecahkan string senarai WP di lajur machine untuk semakan tegar
                for wp_code in [s.strip() for s in str(mach).replace('\n', ',').split(',') if s.strip()]:
                    if wp_code in wujud_inner:
                        pautan_inner_wujud = True
                        break
                # Jika kod WP asal tidak dijumpai di database, padam Outer ini
                if not pautan_inner_wujud:
                    cursor.execute("DELETE FROM rekod_qr WHERE id = ?", (id_db,))
            
            # 3. Ambil semua data Invoice (INV) untuk disemak pautannya pula
            cursor.execute("SELECT id, machine FROM rekod_qr WHERE sequence_no LIKE 'INV%'")
            semua_invoice = cursor.fetchall()
            
            cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%'")
            wujud_outer = [r[0] for r in cursor.fetchall() if r[0]]
            
            for id_db, mach in semua_invoice:
                pautan_outer_wujud = False
                for b_code in [s.strip() for s in str(mach).replace('\n', ',').split(',') if s.strip()]:
                    if b_code in wujud_outer:
                        pautan_outer_wujud = True
                        break
                if not pautan_outer_wujud:
                    cursor.execute("DELETE FROM rekod_qr WHERE id = ?", (id_db,))
            
            conn.commit()
    except Exception as e:
        print(f"[REFRESH CLEAN ERROR] Gagal bersihkan data yatim: {str(e)}")

def kosongkan_seluruh_database_sekarang(win, root):
    if messagebox.askyesno("AMARAN", "Padam KESEMUA DATA secara kekal?", parent=win):
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn: 
            conn.cursor().execute("DELETE FROM rekod_qr")
            conn.commit()
        siapkan_database()
        if root and hasattr(root, 'kemaskini_dashboard'): root.kemaskini_dashboard()
        messagebox.showinfo("Berjaya", "Sistem dibersihkan!", parent=win); win.destroy()
def padam_terpilih(jadual, entry):
    """Memadam baris rekod terpilih berdasarkan tanda checkbox dengan simpanan kekal (COMMIT FIXED)."""
    tanda = [i for i in jadual.get_children() if "☑" in str(jadual.item(i)['values'])]
    if not tanda: 
        return messagebox.showwarning("Peringatan", "Sila tanda ☑ data!", parent=entry.winfo_toplevel())
        
    if messagebox.askyesno("Pengesahan", f"Padam {len(tanda)} rekod terpilih?", parent=entry.winfo_toplevel()):
        try:
            # Imbas kedua-dua laluan database (folder dalam /data dan folder luar) untuk keselamatan penuh
            laluan_database_senarai = [DATABASE_PATH, "warehouse_data.db"]
            
            for path_db in laluan_database_senarai:
                try:
                    with sqlite3.connect(path_db, timeout=10) as conn:
                        cursor = conn.cursor()
                        for i in tanda: 
                            nilai_baris = jadual.item(i)['values']
                            if nilai_baris and len(nilai_baris) > 1:
                                # 🌟 MUKTAMAD: Ekstrak secara tepat indeks ke-1 dari tuple row jadual Treeview anda!
                                # Indeks 0 = Kotak tanda "☑", Indeks 1 = ID Sebenar pangkalan data (Contoh: 597, 596)
                                id_sasaran = int(nilai_baris[1])
                                
                                # Jalankan perintah pemadaman menggunakan integer ID tulen
                                cursor.execute("DELETE FROM rekod_qr WHERE id = ?", (id_sasaran,))
                        conn.commit()
                except Exception as e_sub:
                    print(f"[PATH NOTICE] Bypassed check on {path_db}: {str(e_sub)}")
                
            # Padamkan baris dari paparan skrin UI
            for i in tanda: 
                jadual.delete(i)
                
            # Kemaskini live produksi dashboard portal
            try:
                import main_dashboard_binder as mdb
                mdb.kemaskini_angka_dashboard_live()
            except Exception:
                pass
                
            laksanakan_auto_clean_orphaned_logs()
            
            messagebox.showinfo("Berjaya", f"Berjaya memadam {len(tanda)} rekod dari sistem!", parent=entry.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("DATABASE ERROR", f"Gagal mendelete rekod: {str(e)}", parent=entry.winfo_toplevel())





def gate_pratonton_seragam(jadual, root, is_outer=False, is_invoice=False):
    if is_invoice:
        import invoice_tab_logic  
        return invoice_tab_logic.papar_pratonton_invoice_terpilih(jadual, jadual.winfo_toplevel())
    tanda_id = [i for i in jadual.get_children() if "☑" in str(jadual.set(i, "#1"))]
    if not tanda_id and jadual.selection(): tanda_id = list(jadual.selection())
    if not tanda_id: return messagebox.showwarning("Peringatan", "Sila tanda ☑ data!", parent=jadual.winfo_toplevel())
    
    if len(tanda_id) > 1:
        img_m_list = []
        if is_outer:
            import central_tab_outer_logic as cto_l
            img_m_list = [cto_l.jana_grafik_outer_dari_row(jadual.item(i)['values']) for i in tanda_id]
        else:
            import central_tab_inner_logic as cti_l
            img_m_list = [cti_l.jana_grafik_label_dari_row(jadual.item(i)['values']) for i in tanda_id]
        if img_m_list:
            import database_batch_preview
            return database_batch_preview.buka_popup_database_pukal_seragam(jadual.winfo_toplevel(), img_m_list, is_outer, is_invoice)

    if is_outer and __import__("central_tab_outer_wizard"): 
        __import__("central_tab_outer_wizard").buka_popup_pukal_outer_1by1([jadual.item(tanda_id)['values']], jadual.winfo_toplevel())
    elif __import__("central_tab_inner_wizard"): 
        __import__("central_tab_inner_wizard").buka_popup_pukal_inner_1by1([jadual.item(tanda_id)['values']], jadual.winfo_toplevel())



def buka_tetingkap_database(root):
    win = tk.Toplevel(root); win.title("SYSTEM DATABASE MANAGEMENT PANEL"); win.geometry("1300x680+50+20"); win.transient(root)
    tutup = lambda: [win.grab_release(), tk.Toplevel.destroy(win)]
    win.protocol("WM_DELETE_WINDOW", tutup)
    win.destroy = tutup

    fr = tk.Frame(win); fr.pack(fill="x", padx=10, pady=5)
    tk.Button(fr, text="💥 FACTORY RESET", command=lambda: kosongkan_seluruh_database_sekarang(win, root), bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)
    
    nb = ttk.Notebook(win); nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    def buat_tab(md, nm, f):
        t = tk.Frame(nb); nb.add(t, text=nm); f_tp = tk.Frame(t); f_tp.pack(fill="x", padx=15, pady=5); f_tb = tk.Frame(t); f_tb.pack(fill=tk.BOTH, expand=True)
        if __import__(md) and hasattr(__import__(md), f): 
            getattr(__import__(md), f)(f_tb, f_tp, win, gate_pratonton_seragam, lambda j, e, **k: padam_terpilih(j, e))
    
    buat_tab("central_tab_inner", " INNER CODES ", "bina_tab_inner")
    buat_tab("central_tab_outer", " OUTER BOXES ", "bina_tab_outer")
    buat_tab("central_tab_invoice", " INVOICES SHIPPED ", "bina_tab_invoice")
    
    import database_audit_logger
    database_audit_logger.suntik_tab_audit_logs_ke_notebook(nb, win)
