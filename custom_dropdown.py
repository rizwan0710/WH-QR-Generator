# custom_dropdown.py - VERSI PENUH RINGKAS (ANTI-CACHE, DIRECT FLOATING & SYSTEM FOCUS FIX)
import tkinter as tk
import sqlite3

tingkap_cadangan_global = None
_ikatan_configure_id = None
_parent_terikat = None

def ambil_senarai_customer_dari_db():
    senarai_customer = []
    try:
        conn = sqlite3.connect("warehouse_data.db", timeout=10)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DISTINCT TRIM(customer_code) FROM rekod_qr WHERE customer_code IS NOT NULL AND customer_code != ''")
        except sqlite3.OperationalError:
            cursor.execute("SELECT DISTINCT TRIM(customer) FROM rekod_qr WHERE customer IS NOT NULL AND customer != ''")
            
        for row in cursor.fetchall():
            if row and row[0]:
                senarai_customer.append(row[0].upper())
        conn.close()
    except Exception:
        pass
    return sorted(list(set(senarai_customer)))

def papar_senarai_toplevel(widget_entry, win_induk, senarai_untuk_dipapar):
    global tingkap_cadangan_global, _ikatan_configure_id, _parent_terikat
    
    tutup_dropdown()
    
    if not senarai_untuk_dipapar:
        senarai_untuk_dipapar = ["No Data"]

    _parent_terikat = win_induk
    
    try:
        win_induk.grab_release()
    except Exception:
        pass

    tingkap_cadangan_global = tk.Toplevel(win_induk)
    tingkap_cadangan_global.wm_overrideredirect(True)  
    tingkap_cadangan_global.configure(bg="#CBD5E1")
    tingkap_cadangan_global.wm_attributes("-topmost", True)
    
    def kemas_kini_posisi(event=None):
        global tingkap_cadangan_global
        if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists() and widget_entry.winfo_exists():
            x = widget_entry.winfo_rootx()
            y = widget_entry.winfo_rooty() + widget_entry.winfo_height()
            lebar = widget_entry.winfo_width()
            tingkap_cadangan_global.geometry(f"{lebar}x120+{x}+{y}")

    widget_entry.update_idletasks()
    kemas_kini_posisi()
    
    _ikatan_configure_id = win_induk.bind("<Configure>", kemas_kini_posisi, add="+")
    
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
                if pilihan != "No Data":
                    widget_entry.delete(0, tk.END)
                    widget_entry.insert(0, str(pilihan).strip())
                    tutup_dropdown()
                    widget_entry.focus_set()
                    widget_entry.event_generate("<<Modified>>")
        except Exception:
            pass
            
    listbox.bind("<Return>", on_select)

    # 🌟 KEMAS KINI STRUKTUR PENGIKATAN: ANTI-FREEZE APABILA BERALIH KE CHROME 🌟
    tingkap_cadangan_global.bind("<Escape>", lambda e: tutup_dropdown())
    
    def semak_dan_tutup_fokus_hanyut(event=None):
        """Memastikan dropdown ditutup jika fokus beralih ke luar aplikasi sepenuhnya."""
        global tingkap_cadangan_global
        if not tingkap_cadangan_global or not tingkap_cadangan_global.winfo_exists():
            return
        try:
            fokus_aktif = win_induk.focus_get()
            if fokus_aktif not in [widget_entry, listbox, frame_list, tingkap_cadangan_global]:
                tutup_dropdown()
        except Exception:
            pass

    listbox.bind("<FocusOut>", lambda e: win_induk.after(100, semak_dan_tutup_fokus_hanyut))
    
    # ─── PENGESAN UTAMA APABILA TUKAR WINDOWS/CHROME ───
    id_unmap = win_induk.bind("<Unmap>", lambda e: tutup_dropdown(), add="+")
    id_deactivate = win_induk.bind("<Deactivate>", lambda e: tutup_dropdown(), add="+")
    id_parent_focusout = win_induk.bind("<FocusOut>", lambda e: win_induk.after(100, semak_dan_tutup_fokus_hanyut), add="+")
    
    try:
        win_induk.wm_protocol("WM_TAKE_FOCUS", lambda: tutup_dropdown())
    except Exception:
        pass
    
    # Memintas fungsi penutupan untuk membersihkan sisa unbind
    fungsi_tutup_asal = tutup_dropdown
    def tutup_dropdown_bersih():
        try:
            win_induk.unbind("<Unmap>", id_unmap)
            win_induk.unbind("<Deactivate>", id_deactivate)
            win_induk.unbind("<FocusOut>", id_parent_focusout)
        except Exception:
            pass
        fungsi_tutup_asal()
        
    listbox.bind("<<ListboxSelect>>", on_select)

def kendalikan_taipan_dropdown(widget_entry, win_induk, senarai_asal):
    teks_ditaip = widget_entry.get().strip().upper()
    if not teks_ditaip:
        papar_senarai_toplevel(widget_entry, win_induk, senarai_asal)
        return
    senarai_ditapis = [item for item in senarai_asal if teks_ditaip in str(item).upper()]
    if senarai_ditapis:
        papar_senarai_toplevel(widget_entry, win_induk, senarai_ditapis)
    else:
        papar_senarai_toplevel(widget_entry, win_induk, [])

def aksi_butang_dropdown_pukal(widget_entry, win_induk, senarai_asal=None):
    global tingkap_cadangan_global
    if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
        tutup_dropdown()
        return
    papar_senarai_toplevel(widget_entry, win_induk, senarai_asal)

def tutup_dropdown():
    global tingkap_cadangan_global, _ikatan_configure_id, _parent_terikat
    
    if _parent_terikat and _parent_terikat.winfo_exists() and _ikatan_configure_id:
        try:
            _parent_terikat.unbind("<Configure>", _ikatan_configure_id)
        except Exception:
            pass
            
        try:
            _parent_terikat.grab_set()
        except Exception:
            pass
            
        _ikatan_configure_id = None
        _parent_terikat = None

    if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
        tingkap_cadangan_global.destroy()
    tingkap_cadangan_global = None

# =====================================================================
# DATA LOOKUP QUERIES
# =====================================================================
def ambil_senarai_customer_master():
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            query = "SELECT DISTINCT customer_code FROM master_produk WHERE customer_code IS NOT NULL AND customer_code != ''"
            return sorted(list(set([str(r[0]).upper().strip() for r in conn.cursor().execute(query).fetchall() if r and r[0]])))
    except: 
        return []

def ambil_drawing_terikat(cust_code):
    if not cust_code: return []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            query = "SELECT DISTINCT drawing_no FROM master_produk WHERE customer_code = ?"
            return sorted(list(set([str(r[0]).upper().strip() for r in conn.cursor().execute(query, (cust_code.upper().strip(),)).fetchall() if r and r[0]])))
    except: 
        return []

def ambil_part_terikat(cust_code, draw):
    if not cust_code or not draw: return []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            query = "SELECT DISTINCT part_number FROM master_produk WHERE customer_code = ? AND drawing_no = ?"
            return sorted(list(set([str(r[0]).upper().strip() for r in conn.cursor().execute(query, (cust_code.upper().strip(), draw.upper().strip())).fetchall() if r and r[0]])))
    except: 
        return []

def ambil_machine_terikat(part_no):
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
