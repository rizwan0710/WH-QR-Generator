import sqlite3, os, shutil, sys, time, threading, tkinter as tk
from tkinter import messagebox, ttk
import invoice_tab_logic  # 🌟 Menyambungkan enjin pratinjau invoice murni yang kalis ralat tuple

def siapkan_database():
    for f in ["INNER_STICKER", "OUTER_STICKER", "INVOICE_STICKER"]:
        if not os.path.exists(f): os.makedirs(f)
    with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
        conn.cursor().execute("CREATE TABLE IF NOT EXISTS rekod_qr (id INTEGER PRIMARY KEY AUTOINCREMENT, tarikh TEXT, customer TEXT, drawing_no TEXT, part_no TEXT, quantity TEXT, mfg_date TEXT, machine TEXT, lotcard_no TEXT, sequence_no TEXT)")

def kosongkan_seluruh_database_sekarang(win, root):
    if messagebox.askyesno("AMARAN", "Padam KESEMUA DATA secara kekal?", parent=win):
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn: conn.cursor().execute("DELETE FROM rekod_qr")
        for f in ["INNER_STICKER", "OUTER_STICKER", "INVOICE_STICKER"]:
            if os.path.exists(f): shutil.rmtree(f)
        siapkan_database()
        if root and hasattr(root, 'kemaskini_dashboard'): root.kemaskini_dashboard()
        messagebox.showinfo("Berjaya", "Sistem dibersihkan!", parent=win); win.destroy()

def padam_terpilih(jadual, entry):
    tanda = [i for i in jadual.get_children() if "☑" in str(jadual.item(i)['values'])]
    if not tanda: return messagebox.showwarning("Peringatan", "Sila tanda ☑ data!", parent=entry.winfo_toplevel())
    if messagebox.askyesno("Pengesahan", f"Padam {len(tanda)} rekod terpilih?", parent=entry.winfo_toplevel()):
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            for i in tanda: conn.cursor().execute("DELETE FROM rekod_qr WHERE id = ?", (jadual.set(i, "ID"),))
        for i in tanda: jadual.delete(i)

def gate_pratonton_seragam(jadual, root, is_outer=False, is_invoice=False):
    """
    🎛️ GERBANG PRATONTON SERAGAM DATABASE (MUTTAMAD & KALIS ERROR) 🎛️
    Menguruskan pelencongan fungsi paparan stiker mengikut tab aktif masing-masing.
    """
    # 🌟 KUNCI PENYELESAIAN UTAMA TAB INVOICE:
    # Jika is_invoice dihantar sebagai True, lencongkan aliran data terus ke enjin bersepadu invoice_tab_logic
    if is_invoice:
        return invoice_tab_logic.papar_pratonton_invoice_terpilih(jadual, jadual.winfo_toplevel())

    tanda_id = [i for i in jadual.get_children() if "☑" in str(jadual.set(i, "#1"))]
    if not tanda_id and jadual.selection(): tanda_id = list(jadual.selection())
    if not tanda_id: return messagebox.showwarning("Peringatan", "Sila tanda ☑ data!", parent=jadual.winfo_toplevel())
    
    # ─── BATCH SELECTION (>1 BARIS): GABUNG 1 POP-UP INTERFACE (Hanya untuk Tab Inner & Outer) ───
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

    # ─── REKOD TUNGGAL SELECTION (Hanya untuk Tab Inner & Outer) ───
    if is_outer and __import__("central_tab_outer_wizard"): 
        __import__("central_tab_outer_wizard").buka_popup_pukal_outer_1by1([jadual.item(tanda_id)['values']], jadual.winfo_toplevel())
    elif __import__("central_tab_inner_wizard"): 
        __import__("central_tab_inner_wizard").buka_popup_pukal_inner_1by1([jadual.item(tanda_id)['values']], jadual.winfo_toplevel())

def buka_tetingkap_database(root):
    win = tk.Toplevel(root); win.title("DATABASE PANEL"); win.geometry("1300x680+50+20"); win.transient(root)
    tutup = lambda: [win.grab_release(), tk.Toplevel.destroy(win)]
    win.protocol("WM_DELETE_WINDOW", tutup)
    win.destroy = tutup

    fr = tk.Frame(win); fr.pack(fill="x", padx=10, pady=5)
    tk.Button(fr, text="💥 FACTORY RESET", command=lambda: kosongkan_seluruh_database_sekarang(win, root), bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)
    
    nb = ttk.Notebook(win); nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    def buat_tab(md, nm, f):
        t = tk.Frame(nb); nb.add(t, text=nm); f_tp = tk.Frame(t); f_tp.pack(fill="x", padx=15, pady=5); f_tb = tk.Frame(t); f_tb.pack(fill=tk.BOTH, expand=True)
        if __import__(md) and hasattr(__import__(md), f): getattr(__import__(md), f)(f_tb, f_tp, win, gate_pratonton_seragam, lambda j, e, **k: padam_terpilih(j, e))
    
    buat_tab("central_tab_inner", " INNER ", "bina_tab_inner")
    buat_tab("central_tab_outer", " OUTER ", "bina_tab_outer")
    buat_tab("central_tab_invoice", " INVOICE ", "bina_tab_invoice")
    import database_audit_logger
    database_audit_logger.suntik_tab_audit_logs_ke_notebook(nb, win)
