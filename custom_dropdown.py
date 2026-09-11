# custom_dropdown.py - PART 1: POPUP UI & LIVE TAIPAN ENGINE
import tkinter as tk
import sqlite3

tingkap_cadangan_global = None

def ambil_senarai_customer_dari_db():
    senarai_customer = []
    try:
        conn = sqlite3.connect("warehouse_data.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT TRIM(customer) FROM rekod_qr WHERE customer IS NOT NULL AND customer != ''")
        for row in cursor.fetchall():
            if row and row[0]:
                senarai_customer.append(row[0].upper())
        conn.close()
    except Exception:
        pass
    return sorted(list(set(senarai_customer)))

def papar_senarai_toplevel(widget_entry, win_induk, senarai_untuk_dipapar):
    global tingkap_cadangan_global
    if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
        tingkap_cadangan_global.destroy()
    if not senarai_untuk_dipapar:
        return

    tingkap_cadangan_global = tk.Toplevel(win_induk)
    tingkap_cadangan_global.wm_overrideredirect(True)  
    tingkap_cadangan_global.configure(bg="#CBD5E1")
    tingkap_cadangan_global.wm_attributes("-topmost", True)
    
    def semak_fokus_keluar(event):
        win_induk.after(10, lakukan_semakan_fokus)

    def lakukan_semakan_fokus():
        global tingkap_cadangan_global
        if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
            fokus_sekarang = win_induk.focus_get()
            if fokus_sekarang != widget_entry and fokus_sekarang != listbox:
                tutup_dropdown()

    win_induk.bind("<FocusOut>", semak_fokus_keluar)
    
    x = widget_entry.winfo_rootx()
    y = widget_entry.winfo_rooty() + widget_entry.winfo_height()
    lebar = widget_entry.winfo_width()
    tingkap_cadangan_global.geometry(f"{lebar}x120+{x}+{y}")
    
    frame_list = tk.Frame(tingkap_cadangan_global, bg="white")
    frame_list.pack(fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(frame_list, orient=tk.VERTICAL)
    
    listbox = tk.Listbox(
        frame_list, font=("Segoe UI", 10), bd=1, relief="flat", 
        bg="white", fg="black", selectbackground="#0D6EFD", 
        highlightthickness=0, takefocus=True, yscrollcommand=scrollbar.set
    )
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    for nama in senarai_untuk_dipapar:
        listbox.insert(tk.END, str(nama).strip())
        
    def on_select(event):
        try:
            indeks_pilihan = listbox.curselection()
            if indeks_pilihan:
                pilihan = listbox.get(indeks_pilihan[0])
                widget_entry.delete(0, tk.END)
                widget_entry.insert(0, str(pilihan).strip())
                tutup_dropdown()
                widget_entry.focus_set()
                widget_entry.event_generate("<<Modified>>")
        except Exception as err:
            print(f"Ralat pemilihan dropdown: {str(err)}")
            
    listbox.bind("<<ListboxSelect>>", on_select)
    listbox.bind("<Return>", on_select)

def kendalikan_taipan_dropdown(widget_entry, win_induk, senarai_asal):
    teks_ditaip = widget_entry.get().strip().upper()
    if not teks_ditaip:
        tutup_dropdown()
        papar_senarai_toplevel(widget_entry, win_induk, senarai_asal)
        return
    senarai_ditapis = [item for item in senarai_asal if teks_ditaip in str(item).upper()]
    if senarai_ditapis:
        papar_senarai_toplevel(widget_entry, win_induk, senarai_ditapis)
    else:
        tutup_dropdown()

def aksi_butang_dropdown_pukal(widget_entry, win_induk, senarai_asal=None):
    global tingkap_cadangan_global
    if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
        tutup_dropdown()
        return
    papar_senarai_toplevel(widget_entry, win_induk, senarai_asal)

def tutup_dropdown():
    global tingkap_cadangan_global
    if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
        tingkap_cadangan_global.destroy()
        tingkap_cadangan_global = None

        # custom_dropdown.py - PART 2: DATA LOOKUP QUERIES
def ambil_senarai_customer_master():
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            return sorted(list(set([str(r[0]).upper().strip() for r in conn.cursor().execute("SELECT DISTINCT customer_name FROM master_produk WHERE customer_name IS NOT NULL AND customer_name != ''").fetchall() if r and r[0]])))
    except: return []

def ambil_drawing_terikat(cust):
    if not cust: return []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            return sorted(list(set([str(r[0]).upper().strip() for r in conn.cursor().execute("SELECT DISTINCT drawing_no FROM master_produk WHERE customer_name = ?", (cust.upper().strip(),)).fetchall() if r and r[0]])))
    except: return []

def ambil_part_terikat(cust, draw):
    if not cust or not draw: return []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            return sorted(list(set([str(r[0]).upper().strip() for r in conn.cursor().execute("SELECT DISTINCT part_number FROM master_produk WHERE customer_name = ? AND drawing_no = ?", (cust.upper().strip(), draw.upper().strip())).fetchall() if r and r[0]])))
    except: return []

def ambil_machine_terikat(part_no):
    """🌟 Padanan Dinamik - Memanggil Machine Code milik Part Number terpilih"""
    if not part_no: 
        return []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT TRIM(machine_code) 
                FROM master_machine 
                WHERE part_number = ? AND machine_code IS NOT NULL AND machine_code != ''
            """, (part_no.upper().strip(),))
            return sorted(list(set([str(r[0]).upper().strip() for r in cursor.fetchall() if r and r[0]])))
    except: 
        return []

