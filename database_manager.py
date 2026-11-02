# ==============================================================================
# database_manager.py - PART 1: PENGURUSAN PUSAT DATABASE NAS & ENJIN AUDIT
# ==============================================================================
import sys
import os
import sqlite3
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
# 🚀 GANTI IMPORT KEPADA FAIL PILIHAN KAU
import invoice_tab_logic


# ❌ PENTING: Import statik fail tab di baris atas DIBUANG untuk elak circular import!

# 1. LOCAL DYNAMIC ENVIRONMENT PATH RESOLUTION (Wajib di atas sekali)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🌟 PAKSA LALUAN NAS drive Z: Menghala tepat ke fail .db tulen bersaiz 148 KB
DATABASE_PATH = r"Z:\IT\IT\QR_SYS_Backup(DB)\warehouse_data.db"

try:
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
except Exception:
    pass

STICKER_FOLDERS = [
    os.path.join(BASE_DIR, "INNER_STICKER"),
    os.path.join(BASE_DIR, "OUTER_STICKER"),
    os.path.join(BASE_DIR, "INVOICE_STICKER")
]

# 2. FUNGSI SAMBUNGAN PUSAT (Kalis Ralat Rangkaian)
def get_db_connection():
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
        
        # Jadual 1: Utama Rekod QR
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
        
        try:
            cursor.execute("ALTER TABLE rekod_qr ADD COLUMN tarikh TEXT")
        except sqlite3.OperationalError: pass
        try:
            cursor.execute("ALTER TABLE rekod_qr ADD COLUMN date_created TEXT")
        except sqlite3.OperationalError: pass
        
        # Jadual 2: Log Aktiviti (Audit Logs)
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
        
        # Jadual 3: Master Invoice untuk Form 4 Pre-Billing
        # 🌟 KEMASKINI UTAMA: Menambah customer_code ke dalam struktur binaan asal jadual
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_invoice (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT UNIQUE,
                so_no TEXT,
                customer_name TEXT,
                customer_code TEXT,
                tarikh_masuk TEXT,
                status TEXT DEFAULT 'Pending'
            )
        """)
        
        # 🌟 MIGRASI AUTOMATIK: Menambah kolum customer_code pada DB sedia ada di PC anda
        try:
            cursor.execute("ALTER TABLE master_invoice ADD COLUMN customer_code TEXT")
        except sqlite3.OperationalError: 
            pass # Abaikan jika kolum sudah wujud
            
        try:
            cursor.execute("ALTER TABLE master_invoice ADD COLUMN status TEXT DEFAULT 'Pending'")
        except sqlite3.OperationalError: pass
            
        conn.commit()


def initialize_database_schema():
    siapkan_database()

def laksanakan_auto_clean_orphaned_logs():
    """Enjin pembersihan automatik bagi membersihkan log sekiranya data asal dipadam."""
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'WP%'")
            wujud_inner = [r[0] for r in cursor.fetchall() if r[0]]
            
            cursor.execute("SELECT id, machine, sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%'")
            semua_outer = cursor.fetchall()
            
            for id_db, mach, seq in semua_outer:
                pautan_inner_wujud = False
                for wp_code in [s.strip() for s in str(mach).replace('\n', ',').split(',') if s.strip()]:
                    if wp_code in wujud_inner:
                        pautan_inner_wujud = True
                        break
                if not pautan_inner_wujud:
                    cursor.execute("DELETE FROM rekod_qr WHERE id = ?", (id_db,))
            
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

def ambil_semua_master_invoice(keyword=""):
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            if keyword:
                pola = f"%{keyword}%"
                cursor.execute("""
                    SELECT id, invoice_no, so_no, customer_name, customer_code, tarikh_masuk, status 
                    FROM master_invoice 
                    WHERE invoice_no LIKE ? OR so_no LIKE ? OR customer_name LIKE ? 
                    ORDER BY id DESC
                """, (pola, pola, pola))
            else:
                cursor.execute("""
                    SELECT id, invoice_no, so_no, customer_name, customer_code, tarikh_masuk, status 
                    FROM master_invoice 
                    ORDER BY id DESC
                """)
            return cursor.fetchall()
    except Exception as e:
        print(f"[DB ERROR] Failed to retrieve data: {str(e)}")
        return []



def kemaskini_status_master_invoice(invoice_id, status_baru):
    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE master_invoice SET status = ? WHERE id = ?", (status_baru, invoice_id))
            conn.commit()
            return True
    except Exception as e:
        print(f"[DB ERROR] Failed updated invoice ID {invoice_id}: {str(e)}")
        return False

def padam_master_invoice_terpilih(tree_table):
    tanda = [i for i in tree_table.get_children() if "☑" in str(tree_table.item(i)['values'])]
    
    if not tanda and tree_table.selection():
        tanda = list(tree_table.selection())
        
    if not tanda:
        return messagebox.showwarning("Warning", "Please select or check ☑ the invoice data!", parent=tree_table.winfo_toplevel())
        
    if messagebox.askyesno("Confirmation", f"Delete {len(tanda)} registered invoice(s) from the system?", parent=tree_table.winfo_toplevel()):
        try:
            with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
                cursor = conn.cursor()
                for i in tanda:
                    nilai_baris = tree_table.item(i)['values']
                    if nilai_baris and len(nilai_baris) > 1:
                        id_db = int(nilai_baris[1])
                        cursor.execute("DELETE FROM master_invoice WHERE id = ?", (id_db,))
                conn.commit()
                
            for i in tanda:
                tree_table.delete(i)
            messagebox.showinfo("Success", "Registered invoice records successfully deleted!", parent=tree_table.winfo_toplevel())
            
        except Exception as e:
            messagebox.showerror("DATABASE ERROR", f"Failed to delete invoice: {str(e)}", parent=tree_table.winfo_toplevel())

            
# ==============================================================================
# database_manager.py - PART 2: UTILITI KAWALAN DATA & ENJIN JEJAKAN SEJARAH (CHAIN)
# ==============================================================================


def kosongkan_seluruh_database_sekarang(win, root):
    if messagebox.askyesno("WARNING", "PERMANENTLY DELETE ALL DATA?", parent=win):
        import os
        
        # 1. PATH ENFORCEMENT VERIFICATION
        if not os.path.exists(DATABASE_PATH):
            messagebox.showerror("DATABASE ERROR", f"Active database file not found at path:\n{DATABASE_PATH}\n\nPlease ensure Network Drive Z: is properly connected!", parent=win)
            return

        try:
            with sqlite3.connect(DATABASE_PATH, timeout=15) as conn: 
                cursor = conn.cursor()
                
                # Matikan sekatan foreign key secara sementara supaya proses pembersihan lancar
                cursor.execute("PRAGMA foreign_keys = OFF;")
                
                # Automatically extract all table names present in your network database file
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                
                # 🌟 PEMBETULAN UTAMA: Ekstrak string daripada tuple (row[0])
                all_tables = [row[0] for row in cursor.fetchall()]
                
                cleared_tables = []
                
                # 2. TARGETED DATA PURGE LOOP
                for table_name in all_tables:
                    # Protect system configurations and master product listings
                    if table_name not in ['master_produk', 'sqlite_sequence']:
                        # Bersihkan data dalam jadual transaksi
                        cursor.execute(f"DELETE FROM {table_name}")
                        cleared_tables.append(table_name)
                        
                        # 🌟 KEMASKINI KAEDAH AMPOH: Padam baris pembilang untuk memaksa reset ID ke 1 sepenuhnya
                        try:
                            cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table_name,))
                        except sqlite3.OperationalError:
                            pass
                
                # Aktifkan semula sekatan foreign key untuk keselamatan struktur data
                cursor.execute("PRAGMA foreign_keys = ON;")
                conn.commit()
                
            # 3. INITIALIZE FRESH SCHEMA CLEANUP
            siapkan_database()
            
            # 4. FORCED WINDOW TREEVIEW GUI REFRESH 
            if root:
                if hasattr(root, 'kemaskini_dashboard'): 
                    root.kemaskini_dashboard()
                if hasattr(root, 'load_data'):
                    root.load_data()
                if hasattr(root, 'refresh_data'):
                    root.refresh_data()
            
            # Displays exactly which active database structures were cleared out
            success_msg = f"System data purged successfully!\n\nCleared Tables: {', '.join(cleared_tables)}\n\nID counter forced reset to 1!"
            messagebox.showinfo("Success", success_msg, parent=win)
            win.destroy()
            
        except sqlite3.Error as e:
            messagebox.showerror("SQLite Error", f"Failed to perform data wipe operation:\n{str(e)}", parent=win)

def padam_terpilih(jadual, entry):
    """Memadam baris rekod terpilih berdasarkan tanda checkbox dengan simpanan kekal (COMMIT FIXED)."""
    tanda = [i for i in jadual.get_children() if "☑" in str(jadual.item(i)['values'])]
    if not tanda: 
        return messagebox.showwarning("Reminder", "Select ☑ data!", parent=entry.winfo_toplevel())
        
    if messagebox.askyesno("Confirmation", f"Delete {len(tanda)} selected record?", parent=entry.winfo_toplevel()):
        try:
            # Imbas laluan database pusat Z-Drive NAS secara mutlak
            try:
                with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
                    cursor = conn.cursor()
                    for i in tanda: 
                        nilai_baris = jadual.item(i)['values']
                        if nilai_baris and len(nilai_baris) > 1:
                            id_sasaran = int(nilai_baris[1])
                            cursor.execute("DELETE FROM rekod_qr WHERE id = ?", (id_sasaran,))
                    conn.commit()
            except Exception as e_sub:
                print(f"[PATH NOTICE] Error executing delete on NAS: {str(e_sub)}")
                
            for i in tanda: 
                jadual.delete(i)
                
            try:
                import main_dashboard_binder as mdb
                mdb.kemaskini_angka_dashboard_live()
            except Exception:
                pass
                
            laksanakan_auto_clean_orphaned_logs()
            messagebox.showinfo("Success", f"Compele Delete{len(tanda)} record from system!", parent=entry.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("DATABASE ERROR", f"failed to delete record: {str(e)}", parent=entry.winfo_toplevel())

            

def gate_pratonton_seragam(jadual, root, is_outer=False, is_invoice=False):
    if is_invoice:
        import invoice_tab_logic  
        return invoice_tab_logic.papar_pratonton_invoice_terpilih(jadual, jadual.winfo_toplevel())
        
    tanda_id = [i for i in jadual.get_children() if "☑" in str(jadual.set(i, "#1"))]
    if not tanda_id and jadual.selection(): 
        tanda_id = list(jadual.selection())
        
    if not tanda_id: 
        return messagebox.showwarning("Reminder", "Please Tick ☑ to choose data!", parent=jadual.winfo_toplevel())

    # ─── MOD 1: JIKA PILIH BANYAK ITEM (BATCH PREVIEW) ───
    if len(tanda_id) > 1:
        if is_outer:
            try:
                # 🌟 PEMBETULAN UTAMA: Ambil semua data baris bertanda & hantar terus ke enjin wizard pukal yang sama
                senarai_data_baris = [jadual.item(i)['values'] for i in tanda_id]
                import central_tab_outer_wizard
                return central_tab_outer_wizard.buka_popup_pukal_outer_1by1(senarai_data_baris, jadual.winfo_toplevel())
            except Exception as e_pukal:
                messagebox.showerror("BATCH ERROR", f"Outer Batch Preview failed:\n{str(e_pukal)}", parent=jadual.winfo_toplevel())
                return
        else:
            img_m_list = []
            import central_tab_inner_logic as cti_l
            img_m_list = [cti_l.jana_grafik_label_dari_row(jadual.item(i)['values']) for i in tanda_id]
            
            if img_m_list:
                import database_batch_preview
                return database_batch_preview.buka_popup_database_pukal_seragam(jadual.winfo_toplevel(), img_m_list, is_outer, is_invoice)

    # ─── MOD 2: JIKA PILIH SATU ITEM SAHAJA (SINGLE PREVIEW) ───
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
            import central_tab_inner_wizard
            central_tab_inner_wizard.buka_popup_pukal_inner_1by1([data_baris], jadual.winfo_toplevel())
        except Exception as e_wiz:
            messagebox.showerror("WIZARD ERROR", f"Inner Wizard missing context:\n{str(e_wiz)}", parent=jadual.winfo_toplevel())

            

def bina_menu_klik_kanan_history(event, tree_history, root_win):
    item_id = tree_history.identify_row(event.y)
    if not item_id: return
        
    tree_history.selection_set(item_id)
    nilai_baris = tree_history.item(item_id)['values']
    
    if not nilai_baris or "tidak dijumpai" in str(nilai_baris) or "Tiada rekod" in str(nilai_baris):
        return

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

def jejak_sejarah_label(entry_search, tree_history):
    keyword = entry_search.get().strip().upper()
    for item in tree_history.get_children(): 
        tree_history.delete(item)
        
    if not keyword:
        messagebox.showwarning("Reminder", "Input:(WP/B/INV)!")
        return

    try:
        with sqlite3.connect(DATABASE_PATH, timeout=10) as conn:
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
                outer_box, invoice_no = "Not Registered", "BELUM DI-INVOICE"
                
                cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%' AND machine LIKE ?", (f"%{siri_wp_bersih}%",))
                res_out = cursor.fetchone()
                if res_out:
                    outer_box = res_out[0]
                    cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine LIKE ?", (f"%{outer_box}%",))
                    res_inv = cursor.fetchone()
                    if res_inv: invoice_no = res_inv[0]
                        
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
                
                cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine LIKE ?", (f"%{siri_b_bersih}%",))
                res_inv = cursor.fetchone()
                if res_inv: invoice_no = res_inv[0]
                    
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

            # ─── CARIAN ALTERNATIF KATA KUNCI AM (FALLBACK) ───
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
# ==============================================================================
# database_manager.py - PART 3: ANTARAMUKA PANEL UTAMA 6 TAB (BEBAS SYNTAX ERROR)
# ==============================================================================

def buka_tetingkap_database(root):
    """
    Tetingkap pengurusan database utama.
    Menjamin kesemua 6 tab (Inner, Outer, Shipped, Registered, Edit Logs, History)
    muncul serentak tanpa ada yang tercicir.
    """
    # 🌟 SUNTIKAN INTEGRASI MULTI-MODULE (Bebas Circular Import & Menjamin Butang Muncul Dalam .exe)
    import central_tab_inner
    import central_tab_outer
    import central_tab_invoice
    import central_tab_inner_wizard
    import invoice_tab_logic

    win = tk.Toplevel(root)
    win.title("SYSTEM DATABASE MANAGEMENT PANEL")
    win.geometry("1300x680+50+20")
    win.transient(root)
    
    tutup = lambda: [win.grab_release(), tk.Toplevel.destroy(win)]
    win.protocol("WM_DELETE_WINDOW", tutup)
    win.destroy = tutup

    fr = tk.Frame(win)
    fr.pack(fill="x", padx=10, pady=5)
    
    tk.Button(fr, text="💥 FACTORY RESET", 
              command=lambda: kosongkan_seluruh_database_sekarang(win, root), 
              bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)
    
    nb = ttk.Notebook(win)
    nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # ─── TAB 1: INNER CODES ───
    t1 = tk.Frame(nb)
    nb.add(t1, text=" INNER CODES ")
    f_tp1 = tk.Frame(t1)
    f_tp1.pack(fill="x", padx=15, pady=5)
    f_tb1 = tk.Frame(t1)
    f_tb1.pack(fill=tk.BOTH, expand=True)
    central_tab_inner.bina_tab_inner(f_tb1, f_tp1, win, gate_pratonton_seragam, lambda j, e, **k: padam_terpilih(j, e))

    # ─── TAB 2: OUTER BOXES ───
    t2 = tk.Frame(nb)
    nb.add(t2, text=" OUTER BOXES ")
    f_tp2 = tk.Frame(t2)
    f_tp2.pack(fill="x", padx=15, pady=5)
    f_tb2 = tk.Frame(t2)
    f_tb2.pack(fill=tk.BOTH, expand=True)
    central_tab_outer.bina_tab_outer(f_tb2, f_tp2, win, gate_pratonton_seragam, lambda j, e, **k: padam_terpilih(j, e))

    # ─── TAB 3: INVOICES SHIPPED ───
    t3 = tk.Frame(nb)
    nb.add(t3, text=" INVOICES SHIPPED ")
    f_tp3 = tk.Frame(t3)
    f_tp3.pack(fill="x", padx=15, pady=5)
    f_tb3 = tk.Frame(t3)
    f_tb3.pack(fill=tk.BOTH, expand=True)
    invoice_tab_logic.bina_tab_invoice(f_tb3, f_tp3, win, gate_pratonton_seragam, lambda j, e, **k: padam_terpilih(j, e))

    # ─── TAB 4: INVOICES REGISTERED (KOTAK STATUS BERWARNA ASINGAN) ───
    t_reg = tk.Frame(nb)
    nb.add(t_reg, text=" 📑 INVOICES REGISTERED ")
    
    fr_ctrl_reg = tk.Frame(t_reg, bg="#F1F5F9", pady=6, padx=10)
    fr_ctrl_reg.pack(fill="x")
    
    tk.Label(fr_ctrl_reg, text="Search Invoice/SO/Customer:", font=("Segoe UI", 9, "bold"), bg="#F1F5F9").pack(side="left", padx=5)
    ent_search_reg = tk.Entry(fr_ctrl_reg, font=("Segoe UI", 10), width=25)
    ent_search_reg.pack(side="left", padx=5)
    
    # Konfigurasi Lajur Jadual Visual (Read-Only)
    lajur_reg = ("Select", "ID", "Invoice Number", "SO Number", "Customer Name", "Customer Code", "Registration Date", "Status Tracking")
    tree_reg = ttk.Treeview(t_reg, columns=lajur_reg, show="headings", selectmode="browse")
    tree_reg.pack(fill="both", expand=True, padx=10, pady=5)
    
    for col in lajur_reg:
        tree_reg.heading(col, text=col, anchor="center")
        tree_reg.column(col, width=130, anchor="center")
    tree_reg.column("Select", width=60, anchor="center")
    tree_reg.column("ID", width=50, anchor="center")
    tree_reg.column("Customer Name", width=250, anchor="w")
    tree_reg.column("Customer Code", width=100, anchor="center")
    tree_reg.column("Status Tracking", width=140, anchor="center")
    
    status_label_widgets = []

    # Enjin Suntikan Grafik Kotak Warna Lajur Dinamik
    def muat_data_invoice_registered():
        # Bersihkan widget grafik label lama bagi mengelakkan pertindihan rendering
        for lbl in status_label_widgets:
            try: lbl.destroy()
            except: pass
        status_label_widgets.clear()
        
        for item in tree_reg.get_children():
            tree_reg.delete(item)
            
        keyword = ent_search_reg.get().strip()
        rekod = ambil_semua_master_invoice(keyword)
        
        if not rekod:
            return
            
        baris_berjaya_dilukis = 0
        
        for r in rekod:
            db_id, inv_no, so_no, cust, cust_code, tkh, status_semasa = r
            
            # Pengalihan nama visual: "Pending" ditukar menjadi "On Going"
            status_paparan = "On Going" if str(status_semasa).strip().lower() == "pending" else "Complete"
            
            # Masukkan baris data (Semua lajur lain putih bersih secara standard)
            item_id = tree_reg.insert("", "end", values=("☐", db_id, inv_no, so_no, cust, cust_code, tkh, status_paparan))
            tree_reg.update_idletasks()
            
            # Dapatkan kedudukan koordinat fizikal lajur Status Tracking
            bbox = tree_reg.bbox(item_id, "Status Tracking")
            if bbox:
                x, y, w, h = bbox
                baris_berjaya_dilukis += 1
                
                # Tentukan warna penuh bagi kotak lajur status
                if status_paparan == "Complete":
                    bg_kotak = "#DCFCE7"  # Latar hijau lembut penuh
                    fg_text  = "#15803D"  # Teks hijau pekat tebal
                else:
                    bg_kotak = "#FEF9C3"  # Latar kuning lembut penuh
                    fg_text  = "#A16207"  # Teks kuning pekat tebal (On Going)
                
                # Bina kotak label grafik tepat di atas kedudukan sel
                lbl_status = tk.Label(
                    tree_reg, 
                    text=status_paparan.upper(), 
                    bg=bg_kotak, 
                    fg=fg_text, 
                    font=("Segoe UI", 9, "bold"),
                    relief="flat"
                )
                lbl_status.place(x=x + 2, y=y + 2, width=w - 4, height=h - 4)
                
                # Logik hantaran klik menembusi label ke baris Treeview di belakang
                def passing_click_to_treeview(event, i_id=item_id):
                    tree_reg.selection_set(i_id)
                    tree_reg.focus(i_id)
                    
                def passing_double_click(event):
                    import invoice_status_popup
                    invoice_status_popup.tukar_status_tetingkap_popup(event, tree_reg, win)

                lbl_status.bind("<Button-1>", passing_click_to_treeview)
                lbl_status.bind("<Double-1>", passing_double_click)
                status_label_widgets.append(lbl_status)

        # 🌟 AUTOMATIC RETRY ENGINE: Jika koordinat bbox bernilai kosong disebabkan tetingkap belum bersedia penuh,
        # sistem akan cuba memanggil semula fungsi ini selepas 50ms sehingga berjaya muncul!
        if baris_berjaya_dilukis == 0 and len(tree_reg.get_children()) > 0:
            win.after(50, muat_data_invoice_registered)

    def klik_sel_tanda_invoice(event):
        item_click = tree_reg.identify_row(event.y)
        col_click = tree_reg.identify_column(event.x)
        if item_click and col_click == "#1":
            nilai_baris = list(tree_reg.item(item_click)['values'])
            if nilai_baris and len(nilai_baris) > 0:
                tanda_asal = str(nilai_baris[0]).strip()
                tanda_baru = "☑" if tanda_asal == "☐" else "☐"
                tree_reg.set(item_click, "Select", tanda_baru)

    # ─── IKATAN EVENT (BINDINGS) & MOUSE CONTROLS ───
    tree_reg.bind("<Button-1>", klik_sel_tanda_invoice)
    
    import invoice_status_popup
    tree_reg.bind("<Double-1>", lambda event: invoice_status_popup.tukar_status_tetingkap_popup(event, tree_reg, win))
    
    ent_search_reg.bind("<Return>", lambda event: muat_data_invoice_registered())

    gaya_btn = {
        "font": ("Segoe UI", 9, "bold"), 
        "fg": "white", 
        "relief": "flat", 
        "bd": 0, 
        "height": 1, 
        "padx": 15, 
        "cursor": "hand2"
    }

    # Pembentukan tunggal bagi barisan panel kawalan butang atas
    tk.Button(fr_ctrl_reg, text="SEARCH", command=muat_data_invoice_registered, bg="#007BFF", **gaya_btn).pack(side=tk.LEFT, padx=3)
    tk.Button(fr_ctrl_reg, text="RESET", command=lambda: [ent_search_reg.delete(0, tk.END), muat_data_invoice_registered()], bg="#6C757D", **gaya_btn).pack(side=tk.LEFT, padx=3)
    tk.Button(fr_ctrl_reg, text="DELETE", command=lambda: [padam_master_invoice_terpilih(tree_reg), muat_data_invoice_registered()], bg="#DC3545", **gaya_btn).pack(side=tk.LEFT, padx=3)
    
    tk.Button(fr_ctrl_reg, text="REFRESH", command=muat_data_invoice_registered, bg="#0D9488", **gaya_btn).pack(side=tk.RIGHT, padx=3)
    tk.Button(fr_ctrl_reg, text="BACK TO MAIN", command=lambda: win.destroy(), bg="#6C757D", **gaya_btn).pack(side=tk.RIGHT, padx=3)

    # 🚀 LIVE RUN LOCK: Picu percubaan pertama memuatkan kotak warna sejurus selepas panel database terbuka
    win.after(100, muat_data_invoice_registered)

    # ─── TAB 5: EDIT LOGS (AUDIT) ───
    # ─── TAB 5: EDIT LOGS (AUDIT) ───
    try:
        # Memastikan sistem menyemak laluan folder aktif sebelum memanggil modul luar
        import sys, os
        direktori_utama = os.path.dirname(os.path.abspath(__file__))
        if direktori_utama not in sys.path: sys.path.insert(0, direktori_utama)
        
        import database_audit_logger
        database_audit_logger.suntik_tab_audit_logs_ke_notebook(nb, win)
    except Exception as e: 
        print(f"⚠️ Nota: Gagal memuatkan Tab 5 Audit Logs: {str(e)}")
        
    # ─── TAB 6: LABEL HISTORY ───
    tab_history = tk.Frame(nb)
    nb.add(tab_history, text=" 🔍 LABEL HISTORY ")
    
    fr_ctrl_hist = tk.Frame(tab_history, bg="#F1F5F9", pady=8, padx=10)
    fr_ctrl_hist.pack(fill="x")
    
    tk.Label(fr_ctrl_hist, text="Insert Sequence No (WP / B / INV):", font=("Segoe UI", 9, "bold"), bg="#F1F5F9").pack(side="left", padx=5)
    ent_search_hist = tk.Entry(fr_ctrl_hist, font=("Segoe UI", 10, "bold"), width=30, fg="#1E3A8A")
    ent_search_hist.pack(side="left", padx=5)
    
    # TAMBAHAN: Butang Search Fizikal (Memicu fungsi jejak_sejarah_label)
    tk.Button(fr_ctrl_hist, text="🔍 TRACE SEQUENCE", command=lambda: jejak_sejarah_label(ent_search_hist, tree_history), bg="#1E3A8A", **gaya_btn).pack(side=tk.LEFT, padx=3)
    
    lajur_hist = ("Inner Sequence", "Label Type", "Outer Sequence", "Invoice Number", "Description of Connections", "Quantity")
    tree_history = ttk.Treeview(tab_history, columns=lajur_hist, show="headings", selectmode="browse")
    tree_history.pack(fill="both", expand=True, padx=10, pady=5)
    
    for col in lajur_hist:
        tree_history.heading(col, text=col, anchor="center")
        tree_history.column(col, width=130, anchor="center")

    tree_history.column("Description of Connections", width=420, anchor="w")
    tree_history.column("Inner Sequence", width=120, anchor="center")
    
    # Ikatan menu klik kanan tetikus (Mouse Right-Click)
    tree_history.bind("<Button-3>", lambda event: bina_menu_klik_kanan_history(event, tree_history, win))
    
    tk.Button(fr_ctrl_hist, text="🔄 RESET", command=lambda: [ent_search_hist.delete(0, tk.END), [tree_history.delete(x) for x in tree_history.get_children()]], bg="#64748B", **gaya_btn).pack(side=tk.LEFT, padx=3)
    tk.Button(fr_ctrl_hist, text="◀ BACK ", command=win.destroy, bg="#6C757D", **gaya_btn).pack(side=tk.RIGHT, padx=5)

    # Ikatan butang papan kekunci Enter (Return Key)
    ent_search_hist.bind("<Return>", lambda event: jejak_sejarah_label(ent_search_hist, tree_history))
    
    return nb
