import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# Import fail render yang baru anda kongsikan secara selamat
try:
    import database_preview_render as dpr
except ImportError:
    dpr = None

def dapatkan_rekod_terperinci_dari_db(id_rekod):
    """Mengambil data penuh daripada pangkalan data SQLite."""
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rekod_qr WHERE id = ?", (id_rekod,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Ralat bacaan database: {str(e)}")
        return None

def buka_pratonton_gate(jadual, root, is_outer=False, is_invoice=False):
    """
    🌟 JAMBATAN PINTAR: Membaca ID, mengambil baris SQLite, dan membina semula 
    array senarai lajur (values) untuk dihantar ke proses_pratonton_inner.
    """
    item_terpilih = jadual.selection()
    if not item_terpilih:
        messagebox.showwarning("REMINDER", "PLEASE SELECT A RECORD ROW FROM THE TABLE FIRST.!", parent=jadual.winfo_toplevel())
        return
        
    nilai_baris = jadual.item(item_terpilih)['values']
    if not nilai_baris or len(nilai_baris) < 2:
        messagebox.showwarning("WARNING", "INVALID ROW DATA.", parent=jadual.winfo_toplevel())
        return

    # Ambil ID unik daripada lajur kedua (indeks 1)
    id_rekod = nilai_baris[1]

    # 1. Tarik baris asal dari SQLite
    row = dapatkan_rekod_terperinci_dari_db(id_rekod)
    if not row:
        messagebox.showerror("ERROR", f"FAILED TO FIND SOURCE DATA FOR ID: {id_rekod}", parent=jadual.winfo_toplevel())
        return

    # Susunan tuple SQLite: (id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no)
    # 2. Bina semula array lajur ikut standard sebiji macam Treeview Inner UI anda
    array_lajur_inner = [
        "☐",              # 0. Select Box Dummy
        str(row[0]),      # 1. ID
        str(row[1]),      # 2. Date
        str(row[2]),      # 3. Customer
        str(row[3]),      # 4. Drawing No
        str(row[4]),      # 5. Part No
        str(row[5]),      # 6. Quantity
        str(row[6]),      # 7. Mfg Date
        str(row[7]),      # 8. Machine
        str(row[8]),      # 9. Lotcard No
        str(row[9])       # 10. Sequence No (Mengandungi WP%)
    ]

    # 3. Hantar ke fungsi render baru anda (proses_pratonton_inner)
    if is_outer:
        # Jika tab outer ditekan, panggil fungsi outer jika ada dalam dpr
        if dpr and hasattr(dpr, 'proses_pratonton_outer'):
            dpr.proses_pratonton_outer(array_lajur_inner, jadual.winfo_toplevel())
        else:
            bina_fallback_window(array_lajur_inner, "OUTER PACKING", jadual.winfo_toplevel())
    elif is_invoice:
        # Jika tab invoice ditekan, panggil fungsi invoice jika ada dalam dpr
        if dpr and hasattr(dpr, 'proses_pratonton_invoice'):
            dpr.proses_pratonton_invoice(array_lajur_inner, jadual.winfo_toplevel())
        else:
            bina_fallback_window(array_lajur_inner, "INVOICE LOGS", jadual.winfo_toplevel())
    else:
        # DEFAULT: Tab Inner Packing
        if dpr and hasattr(dpr, 'proses_pratonton_inner'):
            dpr.proses_pratonton_inner(array_lajur_inner, jadual.winfo_toplevel())
        elif dpr and hasattr(dpr, 'buka_pratonton'): # Fleksibiliti jika tersalah nama fungsi
            dpr.buka_pratonton(array_lajur_inner, jadual.winfo_toplevel())
        else:
            bina_fallback_window(array_lajur_inner, "INNER PACKING", jadual.winfo_toplevel())

def bina_fallback_window(data, jenis, tingkap_induk):
    """Paparan kecemasan jika fungsi spesifik tiada di dpr."""
    win = tk.Toplevel(tingkap_induk)
    win.title(f"PRATONTON REPRINT - [{jenis}]")
    win.geometry("400x450")
    win.configure(bg="white")
    win.transient(tingkap_induk)
    win.grab_set()
    
    tk.Label(win, text=f"{jenis} DATA LOG", font=("Segoe UI", 11, "bold"), fg="white", bg="#198754", pady=8).pack(fill="x")
    f = tk.Frame(win, bg="white", padx=20, pady=15)
    f.pack(fill="both", expand=True)
    
    fields = ["Select", "ID", "Date", "Customer", "Drawing No", "Part No", "Quantity", "Mfg Date", "Machine", "Lotcard No", "Sequence No"]
    for idx, val in enumerate(data):
        if idx == 0: continue
        r_f = tk.Frame(f, bg="white")
        r_f.pack(fill="x", pady=2)
        tk.Label(r_f, text=f"{fields[idx]}:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="white", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Label(r_f, text=str(val), font=("Segoe UI", 9), fg="#0F172A", bg="white").pack(side=tk.LEFT)
        
    tk.Button(f, text="❌ TUTUP", command=win.destroy, bg="#DC2626", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", pady=5).pack(pady=15)
