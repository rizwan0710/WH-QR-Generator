import tkinter as tk
from tkinter import ttk, messagebox
import database_manager as dbm

try:
    import central_tab_inner as cti  
    import central_tab_outer as cto  
    import central_tab_invoice as ctiv  
except ImportError: pass  

def panggil_pratonton_dari_db(jadual):
    import database_preview_logic as dpl
    if hasattr(dpl, 'laksanakan_preview_stiker'): dpl.laksanakan_preview_stiker(jadual)

def padam_terpilih(jadual, entry_search, is_outer=False, is_invoice=False):
    import sqlite3
    semua_item = jadual.get_children()
    item_ditanda_id, item_ditanda_row = [], []
    for i in semua_item:
        nilai = jadual.item(i)['values']
        if nilai and len(nilai) > 0 and "☑" in str(nilai):
            item_ditanda_id.append(nilai[1])
            item_ditanda_row.append(i)
    win = entry_search.winfo_toplevel()
    if not item_ditanda_id: return messagebox.showwarning("Peringatan", "Sila tanda kotak!", parent=win)
    if messagebox.askyesno("CONFIRMATION", f"DELETE {len(item_ditanda_id)} RECORD?", parent=win):
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            for n in item_ditanda_id: conn.cursor().execute("DELETE FROM rekod_qr WHERE id = ?", (n,))
            conn.commit()
        for row_ui in item_ditanda_row: jadual.delete(row_ui)

def buka_tetingkap_database(root):
    tingkap = tk.Toplevel(root)
    tingkap.title("CENTRAL DATABASE CONTROL PANEL - OHTA PRECISION")
    tingkap.geometry("1300x680+50+20")
    notebook = ttk.Notebook(tingkap)
    notebook.pack(fill=tk.BOTH, expand=True)

    for mod, fungsi in [(cti, 'bina_tab_inner'), (cto, 'bina_tab_outer'), (ctiv, 'bina_tab_invoice')]:
        if 'mod' in locals() and hasattr(mod, fungsi):
            try: getattr(mod, fungsi)(notebook, tingkap, panggil_pratonton_dari_db, padam_terpilih)
            except TypeError: getattr(mod, fungsi)(tingkap, panggil_pratonton_dari_db, padam_terpilih)
