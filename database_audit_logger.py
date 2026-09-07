import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

def record_edit_activity(jenis_tab, description):
    """
    ⚡ ENJIN REKOD AUDIT LOG AUTO-TRANSAKSI (FIXED ATTRIBUTE ERROR) ⚡
    Menyimpan data log aktiviti suntingan (Edit) ke dalam pangkalan data secara automatik
    apabila operator menekan butang SAVE CHANGES pada panel edit.
    """
    try:
        # Dapatkan tarikh dan masa semasa secara dinamik mengikut masa sistem kilang
        sekarang = datetime.datetime.now()
        tarikh_str = sekarang.strftime("%d/%m/%Y")
        masa_str = sekarang.strftime("%I:%M:%S %p")
        
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            
            # Memastikan jadual log_aktiviti wujud sekiranya belum dibina dalam SQLite
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_aktiviti (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarikh TEXT,
                    masa TEXT,
                    jenis_tab TEXT,
                    description TEXT
                )
            """)
            
            # Masukkan entri suntingan baharu secara selamat (Parameterized Query)
            cursor.execute(
                "INSERT INTO log_aktiviti (tarikh, masa, jenis_tab, description) VALUES (?, ?, ?, ?)",
                (tarikh_str, masa_str, str(jenis_tab).strip().upper(), str(description).strip())
            )
            conn.commit()
            print(f"✔️ Audit Log Berjaya Direkod: [{jenis_tab}] {description}")
            return True
    except Exception as e:
        # Log ralat ke konsol lantai kilang sekiranya transaksi pangkalan data sibuk
        print(f"❌ Gagal menulis ke log_aktiviti: {str(e)}")
        return False

def load_edit_logs_data(tree, ent):
    """🌟 GLOBAL SEARCH FOR ALL HEADERS (SHORT) 🌟"""
    txt = ent.get().strip().upper()
    for i in tree.get_children(): tree.delete(i)
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            if not txt:
                cursor.execute("SELECT id, tarikh, masa, jenis_tab, description FROM log_aktiviti ORDER BY id DESC")
            else:
                p = f"%{txt}%"
                cursor.execute("SELECT id, tarikh, masa, jenis_tab, description FROM log_aktiviti WHERE (id LIKE ? OR tarikh LIKE ? OR masa LIKE ? OR jenis_tab LIKE ? OR description LIKE ?) ORDER BY id DESC", (p, p, p, p, p))
            for row in cursor.fetchall(): tree.insert("", tk.END, values=row)
    except Exception as e: messagebox.showerror("ERROR", str(e))

def show_right_click_menu(event, tree):
    """📋 RIGHT-CLICK COPY ENGINE 📋"""
    r_id, c_id = tree.identify_row(event.y), tree.identify_column(event.x)
    if r_id and c_id:
        tree.selection_set(r_id); tree.focus(r_id)
        val = tree.item(r_id, "values")
        if val:
            idx = int(c_id.replace("#", "")) - 1
            cell = str(val[idx]).strip()
            m = tk.Menu(tree, tearoff=0, bg="white", fg="black")
            m.add_command(label=f"📋 Copy: {cell[:20]}..." if len(cell)>20 else f"📋 Copy: {cell}", command=lambda: [tree.clipboard_clear(), tree.clipboard_append(cell), tree.update()])
            m.post(event.x_root, event.y_root)

def show_right_click_paste_menu(event, ent):
    """📋 RIGHT-CLICK PASTE ENGINE 📋"""
    try: cb = ent.clipboard_get().strip()
    except: cb = ""
    m = tk.Menu(ent, tearoff=0, bg="white", fg="black")
    if cb: m.add_command(label=f"📋 Paste: {cb[:15]}..." if len(cb)>15 else f"📋 Paste: {cb}", command=lambda: [ent.delete(0, tk.END), ent.insert(0, cb), ent.focus_set()])
    else: m.add_command(label="📋 Paste (Empty)", state="disabled")
    m.post(event.x_root, event.y_root)

def suntik_tab_audit_logs_ke_notebook(nb, win):
    """🌟 MAIN UI INJECTION 🌟"""
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
