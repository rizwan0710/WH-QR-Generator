#part 1
import sqlite3
import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox, ttk
# database_manager.py - FUNCTION: buka_tetingkap_database (PART 1: STATIC TAB INJECTION)
import central_tab_inner    # 🌟 WAJIB: Import statik tegas untuk jaminan bundle .exe
import central_tab_outer    # 🌟 WAJIB: Import statik tegas untuk jaminan bundle .exe
import central_tab_invoice  # 🌟 WAJIB: Import statik tegas untuk jaminan bundle .exe
import central_tab_inner_wizard
# 1. LOCAL DYNAMIC ENVIRONMENT PATH RESOLUTION
# 🌟 KEMASKINI LALUAN RASMI: Letakkan fail database terus di folder utama (sebelah .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tukar ini supaya tidak menggunakan sub-folder "data"
DATABASE_PATH = os.path.join(BASE_DIR, "warehouse_data.db")

STICKER_FOLDERS = [
    os.path.join(BASE_DIR, "INNER_STICKER"),
    os.path.join(BASE_DIR, "OUTER_STICKER"),
    os.path.join(BASE_DIR, "INVOICE_STICKER")
]

def get_db_connection():
    # Sambung terus ke folder utama BASE_DIR
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
            
    # Autocreate database kosong di folder utama jika fail asal tiada
    with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
        cursor = conn.cursor()
        
        # 1. Jadual Utama Rekod QR (Jarak tepi sudah diluruskan rapat ke dalam block)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rekod_qr (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                tarikh TEXT,
                date_created TEXT, 
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
        
        # Jaminan Kolum Tarikh wujud untuk keselamatan sistem carian lama/baru
        try:
            cursor.execute("ALTER TABLE rekod_qr ADD COLUMN tarikh TEXT")
        except sqlite3.OperationalError:
            pass
            
        try:
            cursor.execute("ALTER TABLE rekod_qr ADD COLUMN date_created TEXT")
        except sqlite3.OperationalError:
            pass
        
        # 2. Jadual Log Aktiviti (Audit Logs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_aktiviti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarikh TEXT,
                masa TEXT,
                tarikh_masa TEXT,
                jenis_tab TEXT,
                jenis_borang TEXT,
                tindakan TEXT,
                maklumat_lama TEXT,
                maklumat_baru TEXT,
                description TEXT,
                user_pc TEXT
            )
        """)
        
                # 🌟 3. SUNTIKAN UTAMA: Cipta Jadual Master Invoice dengan Lajur Status 🌟
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_invoice (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE,
                so_no TEXT,
                customer_name TEXT,
                tarikh_masuk TEXT,
                status TEXT DEFAULT 'Pending'
            )
        """)
        
        # Jaminan Struktur: Tambah lajur status jika fail database lama sudah wujud tanpa lajur ini
        try:
            cursor.execute("ALTER TABLE master_invoice ADD COLUMN status TEXT DEFAULT 'Pending'")
        except sqlite3.OperationalError:
            pass

def ambil_semua_master_invoice(keyword=""):
    """Menarik semua data dari jadual master_invoice termasuk SO No untuk dipaparkan pada tab baharu."""
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            if keyword:
                pola = f"%{keyword}%"
                cursor.execute("""
                    SELECT id, invoice_no, so_no, customer_name, tarikh_masuk, status 
                    FROM master_invoice 
                    WHERE invoice_no LIKE ? OR so_no LIKE ? OR customer_name LIKE ? 
                    ORDER BY id DESC
                """, (pola, pola, pola))
            else:
                cursor.execute("SELECT id, invoice_no, so_no, customer_name, tarikh_masuk, status FROM master_invoice ORDER BY id DESC")
            return cursor.fetchall()
    except Exception as e:
        print(f"[DB ERROR] Gagal ambil data master invoice: {str(e)}")
        return []


def kemaskini_status_master_invoice(invoice_id, status_baru):
    """Mengemas kini status invois (Pending/Complete) berdasarkan pilihan Dropdown/Combobox di UI."""
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE master_invoice SET status = ? WHERE id = ?", (status_baru, invoice_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"[DB ERROR] Gagal update status invoice ID {invoice_id}: {str(e)}")
        return False

def padam_master_invoice_terpilih(tree_table):
    """Memadam baris rekod invois terdaftar yang dipilih atau ditanda oleh pengguna."""
    tanda = [i for i in tree_table.get_children() if "☑" in str(tree_table.item(i)['values'])]
    if not tanda and tree_table.selection():
        tanda = list(tree_table.selection())
        
    if not tanda:
        return messagebox.showwarning("Peringatan", "Sila pilih atau tanda ☑ data invoice!", parent=tree_table.winfo_toplevel())
        
    if messagebox.askyesno("Pengesahan", f"Padam {len(tanda)} invoice terdaftar dari sistem?", parent=tree_table.winfo_toplevel()):
        try:
            with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
                cursor = conn.cursor()
                for i in tanda:
                    nilai_baris = tree_table.item(i)['values']
                    if nilai_baris and len(nilai_baris) > 1:
                        # Ambil ID Tulen pangkalan data (Lajur Indeks 1)
                        id_db = int(nilai_baris[1])
                        cursor.execute("DELETE FROM master_invoice WHERE id = ?", (id_db,))
                conn.commit()
                
            for i in tanda:
                tree_table.delete(i)
                
            messagebox.showinfo("Berjaya", "Rekod invoice terdaftar berjaya dipadam!", parent=tree_table.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("DATABASE ERROR", f"Gagal memadam invoice: {str(e)}", parent=tree_table.winfo_toplevel())


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
            
    os.makedirs(BASE_DIR, exist_ok=True)
    
    with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
        cursor = conn.cursor()
        
        # 1. Jadual Utama Rekod QR
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
        
        # 2. Jadual Log Aktiviti (Audit Logs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_aktiviti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarikh_masa TEXT,
                jenis_borang TEXT,
                tindakan TEXT,
                maklumat_lama TEXT,
                maklumat_baru TEXT,
                user_pc TEXT
            )
        """)
        
        # 3. Jadual Master Invoice untuk Form 4 Pre-Billing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_invoice (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE,
                so_no TEXT,
                customer_name TEXT,
                tarikh_masuk TEXT,
                status TEXT DEFAULT 'Pending'
            )
        """)
        
        # 🌟 SUNTIKAN PEMBETULAN TEGAR: Paksa SQLite tambah lajur 'status' jika ia belum wujud dalam db lama anda!
        try:
            cursor.execute("ALTER TABLE master_invoice ADD COLUMN status TEXT DEFAULT 'Pending'")
            conn.commit()
            print("[MIGRATION SUCCESS] Lajur 'status' berjaya disuntik ke database lama!")
        except sqlite3.OperationalError:
            # Lajur sudah wujud, boleh abaikan ralat ini dengan selamat
            pass
            
        conn.commit()





def initialize_database_schema():
    siapkan_database()
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
#part 2
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
    if not tanda_id and jadual.selection(): 
        tanda_id = list(jadual.selection())
        
    if not tanda_id: 
        return messagebox.showwarning("Peringatan", "Sila tanda ☑ atau pilih data!", parent=jadual.winfo_toplevel())
    
    # ─── MOD 1: JIKA PILIH BANYAK ITEM (BATCH PREVIEW) ───
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

    # ─── MOD 2: JIKA PILIH SATU ITEM SAHAJA (SINGLE PREVIEW - KALIS CRASH) ───
    # 🌟 PEMBETULAN UTAMA: Ambil item pertama dari list tanda_id [0] supaya ia menjadi string murni
    id_tunggal = tanda_id[0]
    data_baris = jadual.item(id_tunggal)['values']

    if is_outer:
        try:
            import central_tab_outer_wizard
            central_tab_outer_wizard.buka_popup_pukal_outer_1by1([data_baris], jadual.winfo_toplevel())
        except Exception as e_wiz:
            messagebox.showerror("WIZARD ERROR", f"Outer Wizard missing context:\n{str(e_wiz)}", parent=jadual.winfo_toplevel())
    else:
        try:
            central_tab_inner_wizard.buka_popup_pukal_inner_1by1([data_baris], jadual.winfo_toplevel())
        except Exception as e_wiz:
            messagebox.showerror("WIZARD ERROR", f"Inner Wizard missing context:\n{str(e_wiz)}", parent=jadual.winfo_toplevel())

def bina_menu_klik_kanan_history(event, tree_history, root_win):
    """
    🖱️ SUNTIKAN INTERACTIVE COPY ONLY (TIDAK MENGUBAH KOD ASAL) 🖱️
    Membina menu pop-up klik kanan untuk menyalin data siri murni ke clipboard.
    """
    item_id = tree_history.identify_row(event.y)
    if not item_id:
        return
        
    tree_history.selection_set(item_id)
    nilai_baris = tree_history.item(item_id)['values']
    
    if not nilai_baris or "tidak dijumpai" in str(nilai_baris) or "Tiada rekod" in str(nilai_baris):
        return

    # Ambil nilai skalar mengikut aturan data baris jadual history kau
    inner_val = str(nilai_baris[0]).strip() if len(nilai_baris) > 0 else ""
    outer_val = str(nilai_baris[2]).strip() if len(nilai_baris) > 2 else ""
    inv_val = str(nilai_baris[3]).strip() if len(nilai_baris) > 3 else ""

    def salin_ke_clipboard(teks_sasaran):
        if teks_sasaran and teks_sasaran != "N/A" and "BELUM" not in teks_sasaran and "Not Registered" not in teks_sasaran:
            root_win.clipboard_clear()
            root_win.clipboard_append(teks_sasaran)
            root_win.update()

    menu_popup = tk.Menu(root_win, tearoff=0, font=("Segoe UI", 9))
    
    if inner_val and inner_val != "N/A":
        menu_popup.add_command(label=f"📋 Copy Inner Sequence ({inner_val})", command=lambda: salin_ke_clipboard(inner_val))
    if outer_val and outer_val != "N/A" and "Not Registered" not in outer_val:
        menu_popup.add_command(label=f"📋 Copy Outer Box ({outer_val})", command=lambda: salin_ke_clipboard(outer_val))
    if inv_val and inv_val != "N/A" and "BELUM" not in inv_val:
        menu_popup.add_command(label=f"📋 Copy Invoice No ({inv_val})", command=lambda: salin_ke_clipboard(inv_val))
            
    menu_popup.post(event.x_root, event.y_root)
#part 3
def jejak_sejarah_label(entry_search, tree_history):
    """
    🔍 ENJIN PADANAN SUBSTRING LONGGAR (LOOSE SUBSTRING MATCHING ENGINE) 🔍
    Menggunakan operator LIKE murni untuk mengatasi masalah ruang kosong/sengkang teks 
    pada sequence_no di dalam SQLite, menjamin data salasilah keluar 100%.
    """
    keyword = entry_search.get().strip().upper()
    
    # Bersihkan paparan baris lama pada jadual Treeview UI
    for item in tree_history.get_children():
        tree_history.delete(item)
        
    if not keyword:
        messagebox.showwarning("Reminder", "Input:(WP/B/INV)!")
        return

    # Tentukan fail pangkalan data setempat kilang yang memegang data log aktif
    db_aktif = "warehouse_data.db"
    if os.path.exists("data/warehouse_data.db"):
        try:
            with sqlite3.connect("data/warehouse_data.db") as c_test:
                if c_test.execute("SELECT COUNT(*) FROM rekod_qr").fetchone()[0] > 0:
                    db_aktif = "data/warehouse_data.db"
        except Exception: pass

    try:
        with sqlite3.connect(db_aktif, timeout=10) as conn:
            cursor = conn.cursor()
            pola_keyword = f"%{keyword}%"
            
            # ─── KES A: CARIAN KOD INNER (WP...) ───
            if keyword.startswith("WP"):
                cursor.execute("SELECT customer, part_no, quantity, sequence_no FROM rekod_qr WHERE sequence_no LIKE ?", (pola_keyword,))
                res_in = cursor.fetchone()
                
                if not res_in:
                    tree_history.insert("", "end", values=(keyword, "INNER BOX", "N/A", "N/A", "Siri ini tidak dijumpai di dalam pangkalan data.", "0 PCS"))
                    return
                
                cust, part, qty, siri_wp_bersih = res_in[0], res_in[1], res_in[2], res_in[3]
                outer_box = "Not Registered"
                invoice_no = "BELUM DI-INVOICE"
                
                # Cari boks Outer (B) yang memegang kod WP ini di dalam lajur 'machine'
                cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%' AND machine LIKE ?", (f"%{siri_wp_bersih}%",))
                res_out = cursor.fetchone()
                if res_out:
                    outer_box = res_out[0]
                    
                    # Cari Invoice (INV) yang memegang boks Outer tersebut
                    cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine LIKE ?", (f"%{outer_box}%",))
                    res_inv = cursor.fetchone()
                    if res_inv:
                        invoice_no = res_inv[0]
                        
                tree_history.insert("", "end", values=(siri_wp_bersih, "INNER BOX", outer_box, invoice_no, f"Company: {cust} | Part No: {part}", qty))

            # ─── KES B: CARIAN KOD OUTER (B...) ───
            elif keyword.startswith("B"):
                cursor.execute("SELECT customer, machine, sequence_no FROM rekod_qr WHERE sequence_no LIKE ?", (pola_keyword,))
                res_out = cursor.fetchone()
                
                if not res_out:
                    tree_history.insert("", "end", values=(keyword, "OUTER BOX", "N/A", "N/A", "Boks ini tidak dijumpai di dalam pangkalan data.", "0 PCS"))
                    return
                
                cust, inner_text, siri_b_bersih = res_out[0], res_out[1], res_out[2]
                invoice_no = "Not Registered"
                
                # Cari Invoice terkait
                cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine LIKE ?", (f"%{siri_b_bersih}%",))
                res_inv = cursor.fetchone()
                if res_inv:
                    invoice_no = res_inv[0]
                    
                # Pecahkan senarai boks Inner (WP) yang dikongsi di dalam boks Outer ini
                senarai_wp = [s.strip() for s in str(inner_text).replace('\n', ',').split(',') if s.strip()]
                for wp in senarai_wp:
                    cursor.execute("SELECT part_no, quantity FROM rekod_qr WHERE sequence_no LIKE ?", (f"%{wp}%",))
                    res_wp_info = cursor.fetchone()
                    part_text = res_wp_info[0] if res_wp_info else "N/A"
                    qty_text = res_wp_info[1] if res_wp_info else "N/A"
                    
                    tree_history.insert("", "end", values=(wp, "INNER BOX", siri_b_bersih, invoice_no, f"Company: {cust} | Part No: {part_text} (Shared Box)", qty_text))
                    
                if not senarai_wp:
                    tree_history.insert("", "end", values=("N/A", "OUTER BOX", siri_b_bersih, invoice_no, f"Company: {cust} (Boks kosong tanpa pautan Inner)", "0 PCS"))

            # ─── KES C: CARIAN KOD INVOICE (INV...) ───
            elif keyword.startswith("INV"):
                cursor.execute("SELECT customer, machine, sequence_no FROM rekod_qr WHERE sequence_no LIKE ?", (pola_keyword,))
                res_inv = cursor.fetchone()
                
                if not res_inv:
                    tree_history.insert("", "end", values=(keyword, "INVOICE", "N/A", "N/A", "Rekod Invoice tidak dijumpai di dalam pangkalan data.", "0 PCS"))
                    return
                
                cust, outer_text, siri_inv_bersih = res_inv[0], res_inv[1], res_inv[2]
                senarai_b = [b.strip() for b in str(outer_text).replace('\n', ',').split(',') if b.strip()]
                
                for b_code in senarai_b:
                    cursor.execute("SELECT machine FROM rekod_qr WHERE sequence_no LIKE ?", (f"%{b_code}%",))
                    res_b_info = cursor.fetchone()
                    if res_b_info:
                        senarai_wp = [s.strip() for s in str(res_b_info[0]).replace('\n', ',').split(',') if s.strip()]
                        for wp_code in senarai_wp:
                            cursor.execute("SELECT part_no, quantity FROM rekod_qr WHERE sequence_no LIKE ?", (f"%{wp_code}%",))
                            res_wp_info = cursor.fetchone()
                            part_text = res_wp_info[0] if res_wp_info else "N/A"
                            qty_text = res_wp_info[1] if res_wp_info else "N/A"
                            
                            tree_history.insert("", "end", values=(wp_code, "INNER BOX", b_code, siri_inv_bersih, f"Company: {cust} | Part No: {part_text}", qty_text))
                    else:
                        tree_history.insert("", "end", values=("N/A", "OUTER BOX", b_code, siri_inv_bersih, f"Company: {cust} | Boks Outer ini tiada di dalam log", "N/A"))
                        
                if not senarai_b:
                    tree_history.insert("", "end", values=("N/A", "N/A", "N/A", siri_inv_bersih, f"Company: {cust} (Invoice kosong tanpa pautan boks)", "0 PCS"))

            # ─── CARIAN ALTERNATIF KATA KUNCI AM (CUSTOMER NAME / PART NUMBER) ───
            else:
                cursor.execute("SELECT sequence_no, customer, part_no, quantity FROM rekod_qr WHERE customer LIKE ? OR part_no LIKE ? OR drawing_no LIKE ? LIMIT 20", (pola_keyword, pola_keyword, pola_keyword))
                rows_fallback = cursor.fetchall()
                
                for siri_f, cust_f, part_f, qty_f in rows_fallback:
                    tipe_f = "INNER BOX" if str(siri_f).startswith("WP") else ("OUTER BOX" if str(siri_f).startswith("B") else "INVOICE")
                    tree_history.insert("", "end", values=(siri_f, tipe_f, "Matched", "Search via Code for Chain", f"Company: {cust_f} | Part No: {part_f}", qty_f))
                    
                if not rows_fallback:
                    tree_history.insert("", "end", values=(keyword, "N/A", "N/A", "N/A", "Tiada padanan teks atau siri ditemui.", "0 PCS"))

    except Exception as e:
        messagebox.showerror("TRACKING ERROR", f"No Label History:\n{str(e)}")
    # ─── 🌟 SUNTIKAN TAB BARU: INVOICES REGISTERED (CENTRAL TRACKING HUB) 🌟 ───
    t_reg = tk.Frame(nb)
    nb.add(t_reg, text=" 📑 INVOICES REGISTERED ")
    
    # 1. Barisan Kawalan Carian & Butang Aksi Atas
    fr_ctrl_reg = tk.Frame(t_reg, bg="#F8FAFC", pady=8, padx=10)
    fr_ctrl_reg.pack(fill="x")
    
    tk.Label(fr_ctrl_reg, text="Search Invoice/Customer:", font=("Segoe UI", 9, "bold"), bg="#F8FAFC").pack(side="left", padx=5)
    ent_search_reg = tk.Entry(fr_ctrl_reg, font=("Segoe UI", 10), width=25)
    ent_search_reg.pack(side="left", padx=5)
    
    # 2. Pembinaan Jadual Treeview Utama
    lajur_reg = ("Tanda", "ID", "Invoice Number", "Customer Name", "Registration Date", "Status Tracking")
    tree_reg = ttk.Treeview(t_reg, columns=lajur_reg, show="headings", selectmode="browse")
    tree_reg.pack(fill="both", expand=True, padx=10, pady=5)
    
    for col in lajur_reg:
        tree_reg.heading(col, text=col, anchor="center")
        tree_reg.column(col, width=150, anchor="center")
    tree_reg.column("Tanda", width=60, anchor="center")
    tree_reg.column("ID", width=60, anchor="center") # Untuk rujukan ID Database tersembunyi/kecil
    tree_reg.column("Customer Name", width=250, anchor="w")
    
    # Senarai widget combobox aktif untuk mengelakkan isu memori bertumpuk semasa refresh
    combobox_widgets = []
def muat_data_invoice_registered_global(win, tree_reg, ent_search_reg, combobox_widgets):
    """Mengisi jadual data invois berdaftar dengan suntikan gaya warna flat moden tanpa ralat lekukan."""
    for cb in combobox_widgets:
        try: cb.destroy()
        except: pass
    combobox_widgets.clear()
    
    for item in tree_reg.get_children():
        tree_reg.delete(item)
        
    keyword = ent_search_reg.get().strip()
    rekod = ambil_semua_master_invoice(keyword)
    
    style = ttk.Style()
    style.theme_use('clam')
    
    for r in rekod:
        db_id, inv_no, so_no, cust, tkh, status_semasa = r
        item_id = tree_reg.insert("", "end", values=("☐", db_id, inv_no, so_no, cust, tkh, status_semasa))
        
        win.update_idletasks()
        bbox = tree_reg.bbox(item_id, "Status Tracking")
        if bbox:
            x, y, w, h = bbox
            
            style_name = f"Combo_{db_id}.TCombobox"
            cb = ttk.Combobox(tree_reg, values=["Pending", "Complete"], state="readonly", width=12, style=style_name)
            cb.set(status_semasa)
            cb.place(x=x, y=y, width=w, height=h)
            
            def kemaskini_warna_dropdown(c_box, status, s_name):
                if status == "Complete":
                    style.configure(s_name, fieldbackground="#22C55E", background="#16A34A", foreground="white", arrowcolor="white", borderwidth=0, relief="flat")
                else:
                    style.configure(s_name, fieldbackground="#EAB308", background="#CA8A04", foreground="black", arrowcolor="black", borderwidth=0, relief="flat")

            kemaskini_warna_dropdown(cb, status_semasa, style_name)
            
            def membuat_event_tukar(i_id=db_id, c_box=cb, s_name=style_name, current_item=item_id):
                def event_dalaman(event):
                    status_baru = c_box.get()
                    if kemaskini_status_master_invoice(i_id, status_baru):
                        kemaskini_warna_dropdown(c_box, status_baru, s_name)
                        tree_reg.set(current_item, "Status Tracking", status_baru)
                return event_dalaman
                    
            cb.bind("<<ComboboxSelected>>", membuat_event_tukar())
            combobox_widgets.append(cb)

def klik_sel_tanda_invoice_global(event, tree_reg):
    """Mengendalikan fungsi tanda kotak semak secara global."""
    item_click = tree_reg.identify_row(event.y)
    col_click = tree_reg.identify_column(event.x)
    if item_click and col_click == "#1":
        nilai_baris = list(tree_reg.item(item_click)['values'])
        if nilai_baris and len(nilai_baris) > 0:
            tanda_asal = str(nilai_baris[0]).strip()
            tanda_baru = "☑" if tanda_asal == "☐" else "☐"
            tree_reg.set(item_click, "Select", tanda_baru)


    # Sambungkan Butang-butang Kawalan Tab Baharu
    tk.Button(fr_ctrl_reg, text="🔍 SEARCH", command=muat_data_invoice_registered, bg="#1E3A8A", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(fr_ctrl_reg, text="🔄 REFRESH", command=lambda: [ent_search_reg.delete(0, tk.END), muat_data_invoice_registered()], bg="#0D9488", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(fr_ctrl_reg, text="🗑️ DELETE SELECTED", command=lambda: [padam_master_invoice_terpihal(tree_reg), muat_data_invoice_registered()], bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT, padx=3)
    
    # Butang kembali ke menu utama diletakkan rapat ke bahagian kanan tab
    tk.Button(fr_ctrl_reg, text="◀ BACK ", command=win.destroy, bg="#6C757D", fg="white", font=("Segoe UI", 9, "bold"), width=15, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=5)
    
    # Muat data secara automatik apabila tab pertama kali dibuka
    muat_data_invoice_registered()

#part 4
def buka_tetingkap_database(root):
    """
    Tetingkap pengurusan database utama.
    Menjamin kesemua 6 tab (Inner, Outer, Shipped, Registered, Edit Logs, History)
    muncul serentak tanpa ada yang tercicir.
    """
    win = tk.Toplevel(root); win.title("SYSTEM DATABASE MANAGEMENT PANEL"); win.geometry("1300x680+50+20"); win.transient(root)
    tutup = lambda: [win.grab_release(), tk.Toplevel.destroy(win)]
    win.protocol("WM_DELETE_WINDOW", tutup)
    win.destroy = tutup

    fr = tk.Frame(win); fr.pack(fill="x", padx=10, pady=5)
    tk.Button(fr, text="💥 FACTORY RESET", command=lambda: kosongkan_seluruh_database_sekarang(win, root), bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)
    
    nb = ttk.Notebook(win); nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # ─── TAB 1: INNER CODES ───
    t1 = tk.Frame(nb); nb.add(t1, text=" INNER CODES ")
    f_tp1 = tk.Frame(t1); f_tp1.pack(fill="x", padx=15, pady=5); f_tb1 = tk.Frame(t1); f_tb1.pack(fill=tk.BOTH, expand=True)
    central_tab_inner.bina_tab_inner(f_tb1, f_tp1, win, gate_pratonton_seragam, lambda j, e, **k: padam_terpilih(j, e))

    # ─── TAB 2: OUTER BOXES ───
    t2 = tk.Frame(nb); nb.add(t2, text=" OUTER BOXES ")
    f_tp2 = tk.Frame(t2); f_tp2.pack(fill="x", padx=15, pady=5); f_tb2 = tk.Frame(t2); f_tb2.pack(fill=tk.BOTH, expand=True)
    central_tab_outer.bina_tab_outer(f_tb2, f_tp2, win, gate_pratonton_seragam, lambda j, e, **k: padam_terpilih(j, e))

    # ─── TAB 3: INVOICES SHIPPED ───
    t3 = tk.Frame(nb); nb.add(t3, text=" INVOICES SHIPPED ")
    f_tp3 = tk.Frame(t3); f_tp3.pack(fill="x", padx=15, pady=5); f_tb3 = tk.Frame(t3); f_tb3.pack(fill=tk.BOTH, expand=True)
    central_tab_invoice.bina_tab_invoice(f_tb3, f_tp3, win, gate_pratonton_seragam, lambda j, e, **k: padam_terpilih(j, e))

    # ─── TAB 4: INVOICES REGISTERED ───
    t_reg = tk.Frame(nb)
    nb.add(t_reg, text=" 📑 INVOICES REGISTERED ")
    
    fr_ctrl_reg = tk.Frame(t_reg, bg="#F1F5F9", pady=6, padx=10)
    fr_ctrl_reg.pack(fill="x")
    
    tk.Label(fr_ctrl_reg, text="Search Invoice/SO/Customer:", font=("Segoe UI", 9, "bold"), bg="#F1F5F9").pack(side="left", padx=5)
    ent_search_reg = tk.Entry(fr_ctrl_reg, font=("Segoe UI", 10), width=25)
    ent_search_reg.pack(side="left", padx=5)
    
    lajur_reg = ("Select", "ID", "Invoice Number", "SO Number", "Customer Name", "Registration Date", "Status Tracking")
    tree_reg = ttk.Treeview(t_reg, columns=lajur_reg, show="headings", selectmode="browse")
    tree_reg.pack(fill="both", expand=True, padx=10, pady=5)
    
    for col in lajur_reg:
        tree_reg.heading(col, text=col, anchor="center")
        tree_reg.column(col, width=130, anchor="center")
    tree_reg.column("Select", width=60, anchor="center")
    tree_reg.column("ID", width=50, anchor="center")
    tree_reg.column("Customer Name", width=250, anchor="w")
    tree_reg.column("Status Tracking", width=140, anchor="center")
    
    combobox_widgets = []

    def muat_data_invoice_registered():
        for cb in combobox_widgets:
            try: cb.destroy()
            except: pass
        combobox_widgets.clear()
        
        for item in tree_reg.get_children():
            tree_reg.delete(item)
            
        keyword = ent_search_reg.get().strip()
        rekod = ambil_semua_master_invoice(keyword)
        
        # 🎨 SUNTIKAN ENJIN MODEN ELEMEN COMBOCBOX FLAT
        style = ttk.Style()
        style.theme_use('clam')
        
        for r in rekod:
            db_id, inv_no, so_no, cust, tkh, status_semasa = r
            item_id = tree_reg.insert("", "end", values=("☐", db_id, inv_no, so_no, cust, tkh, status_semasa))
            
            win.update_idletasks()
            bbox = tree_reg.bbox(item_id, "Status Tracking")
            if bbox:
                x, y, w, h = bbox
                
                # Cipta elemen gaya flat unik bagi setiap baris rekod
                style_name = f"Combo_{db_id}.TCombobox"
                cb = ttk.Combobox(tree_reg, values=["Pending", "Complete"], state="readonly", width=12, style=style_name)
                cb.set(status_semasa)
                cb.place(x=x, y=y, width=w, height=h)
                
                # Fungsi menukar warna penuh flat yang sangat kemas
                def kemaskini_warna_dropdown(c_box, status, s_name):
                    if status == "Complete":
                        # Warna Hijau Flat (Teks Putih)
                        style.configure(s_name, 
                                        fieldbackground="#22C55E", 
                                        background="#16A34A", 
                                        foreground="white", 
                                        arrowcolor="white",
                                        borderwidth=0,
                                        relief="flat")
                    else:
                        # Warna Kuning Cerah Flat (Teks Hitam)
                        style.configure(s_name, 
                                        fieldbackground="#EAB308", 
                                        background="#CA8A04", 
                                        foreground="black", 
                                        arrowcolor="black",
                                        borderwidth=0,
                                        relief="flat")

                # Cetus warna flat untuk pusingan pertama
                kemaskini_warna_dropdown(cb, status_semasa, style_name)
                
                # Fungsi penukaran interaktif apabila di-klik
                def membuat_event_tukar(i_id=db_id, c_box=cb, s_name=style_name, current_item=item_id):
                    def event_dalaman(event):
                        status_baru = c_box.get()
                        if kemaskini_status_master_invoice(i_id, status_baru):
                            kemaskini_warna_dropdown(c_box, status_baru, s_name)
                            tree_reg.set(current_item, "Status Tracking", status_baru)
                    return event_dalaman
                
                # Ikatkan event pilihan pertukaran combobox
                cb.bind("<<ComboboxSelected>>", membuat_event_tukar())
                combobox_widgets.append(cb)

    def klik_sel_tanda_invoice(event):
        item_click = tree_reg.identify_row(event.y)
        col_click = tree_reg.identify_column(event.x)
        if item_click and col_click == "#1":
            nilai_baris = list(tree_reg.item(item_click)['values'])
            if nilai_baris and len(nilai_baris) > 0:
                tanda_asal = str(nilai_baris[0]).strip()
                tanda_baru = "☑" if tanda_asal == "☐" else "☐"
                tree_reg.set(item_click, "Select", tanda_baru)

    tree_reg.bind("<Button-1>", klik_sel_tanda_invoice)

    # ─── BUTTONS KAWALAN AKSI STANDARD KILANG OHTA (SAIZ & SUSUNAN LENGKAP SERAGAM) ───
    # Membuang pady piksel teks dan menetapkan height=1 serta bd=0 untuk kesan flat seiras tab lama
    gaya_btn = {
        "font": ("Segoe UI", 9, "bold"), 
        "fg": "white", 
        "relief": "flat", 
        "bd": 0, 
        "height": 1, 
        "padx": 15, 
        "cursor": "hand2"
    }
    
    # Kelompok Kiri: Carian & Pemadaman (Susunan Seragam)
    tk.Button(fr_ctrl_reg, text="SEARCH", command=muat_data_invoice_registered, bg="#007BFF", **gaya_btn).pack(side=tk.LEFT, padx=3)
    tk.Button(fr_ctrl_reg, text="RESET", command=lambda: [ent_search_reg.delete(0, tk.END), muat_data_invoice_registered()], bg="#6C757D", **gaya_btn).pack(side=tk.LEFT, padx=3)
    tk.Button(fr_ctrl_reg, text="DELETE", command=lambda: [padam_master_invoice_terpilih(tree_reg), muat_data_invoice_registered()], bg="#DC3545", **gaya_btn).pack(side=tk.LEFT, padx=3)
    
      # Kelompok Kanan: REFRESH dimasukkan dahulu supaya duduk di paling kanan sekali, diikuti BACK TO MAIN di kirinya
    tk.Button(fr_ctrl_reg, text="REFRESH", command=muat_data_invoice_registered, bg="#0D9488", **gaya_btn).pack(side=tk.RIGHT, padx=3)
    tk.Button(fr_ctrl_reg, text="BACK TO MAIN", command=win.destroy, bg="#6C757D", **gaya_btn).pack(side=tk.RIGHT, padx=3)



    ent_search_reg.bind("<Return>", lambda event: muat_data_invoice_registered())
    muat_data_invoice_registered()





    # ─── TAB 5: EDIT LOGS (AUDIT) ───
    try:
        import database_audit_logger
        database_audit_logger.suntik_tab_audit_logs_ke_notebook(nb, win)
    except Exception:
        pass
        
    # ─── TAB 6: LABEL HISTORY ───
    tab_history = tk.Frame(nb)
    nb.add(tab_history, text=" 🔍 LABEL HISTORY ")
    
    fr_ctrl_hist = tk.Frame(tab_history, bg="#F1F5F9", pady=8, padx=10)
    fr_ctrl_hist.pack(fill="x")
    
    tk.Label(fr_ctrl_hist, text="Insert Sequence No (WP / B / INV):", font=("Segoe UI", 9, "bold"), bg="#F1F5F9").pack(side="left", padx=5)
    ent_search_hist = tk.Entry(fr_ctrl_hist, font=("Segoe UI", 10, "bold"), width=30, fg="#1E3A8A")
    ent_search_hist.pack(side="left", padx=5)
    
    lajur_hist = ("Inner Sequence", "Label Type", "Outer Sequence", "Invoice Number", "Description of Connections", "Quantity")
    tree_history = ttk.Treeview(tab_history, columns=lajur_hist, show="headings", selectmode="browse")
    tree_history.pack(fill="both", expand=True, padx=10, pady=5)
    
    for col in lajur_hist:
        tree_history.heading(col, text=col, anchor="center")
        tree_history.column(col, width=130, anchor="center")
    tree_history.column("Description of Connections", width=420, anchor="w")
    tree_history.column("Inner Sequence", width=120, anchor="center")
    
    tree_history.bind("<Button-3>", lambda event: bina_menu_klik_kanan_history(event, tree_history, win))
    
    tk.Button(fr_ctrl_hist, text="🔍 TRACE SEQUENCE", command=lambda: jejak_sejarah_label(ent_search_hist, tree_history), bg="#1E3A8A", **gaya_btn).pack(side=tk.LEFT, padx=3)
    tk.Button(fr_ctrl_hist, text="🔄 RESET", command=lambda: [ent_search_hist.delete(0, tk.END), [tree_history.delete(x) for x in tree_history.get_children()]], bg="#64748B", **gaya_btn).pack(side=tk.LEFT, padx=3)
    
    tk.Button(fr_ctrl_hist, text="◀ BACK ", command=win.destroy, bg="#6C757D", **gaya_btn).pack(side=tk.RIGHT, padx=5)

    ent_search_hist.bind("<Return>", lambda event: jejak_sejarah_label(ent_search_hist, tree_history))
    
    return nb
