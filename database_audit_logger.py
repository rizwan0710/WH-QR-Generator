import sys
import os
import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# 🚨 TETAPAN UTAMA: Daftarkan folder aplikasi ke dalam laluan Python selepas import asas
direktori_utama = os.path.dirname(os.path.abspath(__file__))
if direktori_utama not in sys.path:
    sys.path.insert(0, direktori_utama)

# Jika dijalankan sebagai aplikasi .exe (PyInstaller environment)
if getattr(sys, 'frozen', False):
    direktori_exe = os.path.dirname(sys.executable)
    if direktori_exe not in sys.path:
        sys.path.insert(0, direktori_exe)

try:
    import database_manager as dbm  # 🌟 Dynamic central connection path router 
except ModuleNotFoundError:
    # Pelan sandaran jika fail database_manager berada di folder induk atas
    direktori_induk = os.path.dirname(direktori_utama)
    if direktori_induk not in sys.path:
        sys.path.insert(0, direktori_induk)
    import database_manager as dbm

def jejak_sejarah_label(ent_search, tree_widget):
    """
    🔍 GLOBAL UNIFIED DATABASE TRACE ENGINE FOR LABEL HISTORY
    Cross-references and scans historical package sequence matches seamlessly across active tables.
    """
    # 🚨 TYPE MISMATCH SAFEGUARD: Ensure correct conversion from Tkinter input fields safely
    try:
        if hasattr(ent_search, "get"):
            txt = str(ent_search.get()).strip().upper()
        else:
            txt = str(ent_search).strip().upper()
    except Exception as e:
        messagebox.showerror("INPUT FIELD ERROR", f"System failed to parse text from the search input box:\n\nDetails: {str(e)}")
        return

    # Flush legacy visual nodes inside the table view before displaying new search queries
    for item in tree_widget.get_children():
        tree_widget.delete(item)
        
    if not txt:
        messagebox.showwarning("INPUT REQUIRED", "Please enter or scan a valid Sequence Number (WP / B / INV) to proceed!")
        return

    # Map relational wildcards for generalized SQL LIKE execution passes
    p = f"%{txt}%"
    data_found = []

    try:
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            
            # Fetch all existing database tables dynamically to isolate logistical assets safely
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            # Dynamic matching adapters to parse structured schemas without layout conflicts
            tbl_inner = next((t for t in existing_tables if "inner" in t.lower()), None)
            tbl_outer = next((t for t in existing_tables if "outer" in t.lower() or "box" in t.lower()), None)
            tbl_invoice = next((t for t in existing_tables if "invoice" in t.lower() or "invois" in t.lower()), None)
            
            # 1. RETRIEVE INNER BOX / UNIT RECONCILIATION DATA
            if tbl_inner:
                try:
                    cursor.execute(f"PRAGMA table_info({tbl_inner})")
                    columns = [c[1] for c in cursor.fetchall()]
                    c_inner = next((c for c in columns if "inner" in c.lower() or "wp" in c.lower()), columns[0])
                    c_outer = next((c for c in columns if "outer" in c.lower() or "box" in c.lower() or "sekuens" in c.lower()), columns[1] if len(columns)>1 else columns[0])
                    c_inv = next((c for c in columns if "inv" in c.lower() or "no" in c.lower() or "num" in c.lower()), columns[2] if len(columns)>2 else columns[0])
                    c_desc = next((c for c in columns if "desc" in c.lower() or "conn" in c.lower() or "nama" in c.lower()), columns[3] if len(columns)>3 else columns[0])
                    c_qty = next((c for c in columns if "qty" in c.lower() or "kuantiti" in c.lower() or "quant" in c.lower()), columns[-1])
                    
                    cursor.execute(f"SELECT {c_inner}, 'INNER UNIT', {c_outer}, {c_inv}, {c_desc}, {c_qty} FROM {tbl_inner} WHERE ({c_inner} LIKE ? OR {c_outer} LIKE ? OR {c_inv} LIKE ?)", (p, p, p))
                    data_found.extend(cursor.fetchall())
                except Exception: pass

            # 2. RETRIEVE OUTER MASTER CARTON TRANSACTIONAL RECORDS
            if tbl_outer:
                try:
                    cursor.execute(f"PRAGMA table_info({tbl_outer})")
                    columns = [c[1] for c in cursor.fetchall()]
                    c_inner = next((c for c in columns if "inner" in c.lower() or "wp" in c.lower()), columns[0])
                    c_outer = next((c for c in columns if "outer" in c.lower() or "box" in c.lower() or "sekuens" in c.lower()), columns[1] if len(columns)>1 else columns[0])
                    c_inv = next((c for c in columns if "inv" in c.lower() or "no" in c.lower() or "num" in c.lower()), columns[2] if len(columns)>2 else columns[0])
                    c_desc = next((c for c in columns if "desc" in c.lower() or "conn" in c.lower() or "nama" in c.lower()), columns[3] if len(columns)>3 else columns[0])
                    c_qty = next((c for c in columns if "qty" in c.lower() or "kuantiti" in c.lower() or "quant" in c.lower()), columns[-1])
                    
                    cursor.execute(f"SELECT {c_inner}, 'MASTER CARTON', {c_outer}, {c_inv}, {c_desc}, {c_qty} FROM {tbl_outer} WHERE ({c_inner} LIKE ? OR {c_outer} LIKE ? OR {c_inv} LIKE ?)", (p, p, p))
                    data_found.extend(cursor.fetchall())
                except Exception: pass

            # 3. RETRIEVE DISPATCH INVOICE & ORDER ROUTING TRACES
            if tbl_invoice:
                try:
                    cursor.execute(f"PRAGMA table_info({tbl_invoice})")
                    columns = [c[1] for c in cursor.fetchall()]
                    c_inner = next((c for c in columns if "inner" in c.lower() or "wp" in c.lower()), columns[0])
                    c_outer = next((c for c in columns if "outer" in c.lower() or "box" in c.lower() or "sekuens" in c.lower()), columns[1] if len(columns)>1 else columns[0])
                    c_inv = next((c for c in columns if "inv" in c.lower() or "no" in c.lower() or "num" in c.lower()), columns[2] if len(columns)>2 else columns[0])
                    c_desc = next((c for c in columns if "desc" in c.lower() or "conn" in c.lower() or "nama" in c.lower()), columns[3] if len(columns)>3 else columns[0])
                    c_qty = next((c for c in columns if "qty" in c.lower() or "kuantiti" in c.lower() or "quant" in c.lower()), columns[-1])
                    
                    cursor.execute(f"SELECT {c_inner}, 'INVOICE DOC', {c_outer}, {c_inv}, {c_desc}, {c_qty} FROM {tbl_invoice} WHERE ({c_inner} LIKE ? OR {c_outer} LIKE ? OR {c_inv} LIKE ?)", (p, p, p))
                    data_found.extend(cursor.fetchall())
                except Exception: pass

        # Abort processing gracefully if search queries return completely empty arrays
        if not data_found:
            messagebox.showinfo("NO RESULTS FOUND", f"No historic warehouse sequence entry matches found for query string: '{txt}'")
            return

        # Strip duplicated records cleanly to keep table rows structured uniformly
        unique_dataset = list(set(tuple(row) for row in data_found))
        
        for row in unique_dataset:
            cleaned_row = ["" if item is None else item for item in row]
            tree_widget.insert("", tk.END, values=cleaned_row)

    except Exception as e:
        messagebox.showerror("CRITICAL DATABASE FAULT", f"An operational framework exception occurred during lookup:\n\nDetails: {str(e)}")



def record_edit_activity(jenis_tab, description):
    """
    ⚡ AUTOMATED TRANSACTION AUDIT LOG ENGINE ⚡
    Registers modifications, adjustments, and override edits directly into the central database.
    """
    try:
        sekarang = datetime.datetime.now()
        tarikh_str = sekarang.strftime("%d/%m/%Y")
        masa_str = sekarang.strftime("%I:%M:%S %p")
        
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_aktiviti (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarikh TEXT,
                    masa TEXT,
                    jenis_tab TEXT,
                    description TEXT
                )
            """)
            
            cursor.execute(
                "INSERT INTO log_aktiviti (tarikh, masa, jenis_tab, description) VALUES (?, ?, ?, ?)",
                (tarikh_str, masa_str, str(jenis_tab).strip().upper(), str(description).strip())
            )
            conn.commit()
            print(f"✔️ Audit Trace Successfully Recorded: [{jenis_tab}] {description}")
            return True
    except Exception as e:
        print(f"❌ Critical Fault: Failed to register trace into log_aktiviti: {str(e)}")
        return False

    
def load_edit_logs_data(tree, ent):
    """🌟 GLOBAL COMPILATION DATA ADAPTER LAYOUT FOR EDIT LOGS 🌟"""
    txt = ent.get().strip().upper()
    for i in tree.get_children(): 
        tree.delete(i)
        
    try:
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(log_aktiviti)")
            senarai_lajur = [col[1] for col in cursor.fetchall()]
            
            if "tarikh" not in senarai_lajur:
                try:
                    cursor.execute("ALTER TABLE log_aktiviti ADD COLUMN tarikh TEXT")
                    cursor.execute("ALTER TABLE log_aktiviti ADD COLUMN masa TEXT")
                    cursor.execute("ALTER TABLE log_aktiviti ADD COLUMN jenis_tab TEXT")
                    cursor.execute("ALTER TABLE log_aktiviti ADD COLUMN description TEXT")
                    conn.commit()
                except sqlite3.OperationalError:
                    pass
            
            if not txt:
                cursor.execute("SELECT id, tarikh, masa, jenis_tab, description FROM log_aktiviti ORDER BY id DESC")
            else:
                p = f"%{txt}%"
                cursor.execute("""
                    SELECT id, tarikh, masa, jenis_tab, description FROM log_aktiviti 
                    WHERE (id LIKE ? OR tarikh LIKE ? OR masa LIKE ? OR jenis_tab LIKE ? OR description LIKE ?) 
                    ORDER BY id DESC
                """, (p, p, p, p, p))
                
            for row in cursor.fetchall(): 
                isi_baris = ["" if x is None else x for x in row]
                tree.insert("", tk.END, values=isi_baris)
    except Exception as e: 
        messagebox.showerror("CRITICAL DATABASE LOADING ERROR", f"CRITICAL SYSTEM RECOVERY FAULT:\n\nFAILED TO RETRIEVE AUDIT LOG ENTRIES!\n\nDetails: {str(e)}")

def show_right_click_menu(event, tree):
    """📋 RIGHT-CLICK SUB-MENU COPY RECOVERY TRACE ENGINE 📋"""
    r_id, c_id = tree.identify_row(event.y), tree.identify_column(event.x)
    if r_id and c_id:
        tree.selection_set(r_id); tree.focus(r_id)
        val = tree.item(r_id, "values")
        if val:
            try:
                idx = int(c_id.replace("#", "")) - 1
                cell = str(val[idx]).strip()
                m = tk.Menu(tree, tearoff=0, bg="white", fg="black")
                m.add_command(label=f"📋 Copy: {cell[:20]}..." if len(cell)>20 else f"📋 Copy: {cell}", command=lambda: [tree.clipboard_clear(), tree.clipboard_append(cell), tree.update()])
                m.post(event.x_root, event.y_root)
            except (ValueError, IndexError):
                pass
            
def show_right_click_paste_menu(event, ent):
    """📋 RIGHT-CLICK SUB-MENU PASTE RECOVERY TRACE ENGINE 📋"""
    try: cb = ent.clipboard_get().strip()
    except: cb = ""
    m = tk.Menu(ent, tearoff=0, bg="white", fg="black")
    if cb: m.add_command(label=f"📋 Paste: {cb[:15]}..." if len(cb)>15 else f"📋 Paste: {cb}", command=lambda: [ent.delete(0, tk.END), ent.insert(0, cb), ent.focus_set()])
    else: m.add_command(label="📋 Paste (Clipboard Empty)", state="disabled")
    m.post(event.x_root, event.y_root)

def suntik_tab_audit_logs_ke_notebook(nb, win):
    """🌟 MAIN NOTEBOOK INTEGRATION INTERFACE INJECTION SEQUENCE 🌟"""
    tab = tk.Frame(nb, bg="white"); nb.add(tab, text=" 📋 EDIT LOGS ")
    f_t = tk.Frame(tab, bg="white"); f_t.pack(fill="x", padx=15, pady=5)
    f_b = tk.Frame(tab, bg="white"); f_b.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    tk.Label(f_t, text="Search Log:", font=("Segoe UI", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=5)
    ent = tk.Entry(f_t, width=30, font=("Segoe UI", 10), relief="groove"); ent.pack(side=tk.LEFT, padx=5, ipady=2)
    ent.bind("<Button-3>", lambda e: show_right_click_paste_menu(e, ent))
    
    cols = ("Log ID", "Date", "Time", "Tab Category", "Description of Changes")
    tree = ttk.Treeview(f_b, columns=cols, show="headings")
    for c in cols: tree.heading(c, text=c); tree.column(c, width=105, anchor="center")
    tree.column("Description of Changes", width=630, anchor="w"); tree.column("Log ID", width=65)
    
    sb = ttk.Scrollbar(f_b, orient=tk.VERTICAL, command=tree.yview); tree.configure(yscrollcommand=sb.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); sb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.bind("<Button-3>", lambda e: show_right_click_menu(e, tree))
    
    tk.Button(f_t, text="SEARCH", command=lambda: load_edit_logs_data(tree, ent), bg="#0D6EFD", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat").pack(side=tk.LEFT, padx=2)
    tk.Button(f_t, text="RESET", command=lambda: [ent.delete(0, tk.END), load_edit_logs_data(tree, ent)], bg="#6C757D", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat").pack(side=tk.LEFT, padx=2)
    tk.Button(f_t, text="◀ BACK", command=win.destroy, bg="#6C757D", fg="white", font=("Segoe UI", 9, "bold"), width=12, relief="flat").pack(side=tk.RIGHT, padx=5)
    tk.Button(f_t, text="🔄 REFRESH", command=lambda: load_edit_logs_data(tree, ent), bg="#0D9488", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat").pack(side=tk.RIGHT, padx=2)
    
    ent.bind("<Return>", lambda e: load_edit_logs_data(tree, ent))
    load_edit_logs_data(tree, ent)
