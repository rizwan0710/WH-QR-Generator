import tkinter as tk
import sqlite3

tingkap_cadangan_global = None

def ambil_senarai_customer_dari_db():
    """🌟 DYNAMIC LOOKUP - Menarik nama customer unik dari database 🌟"""
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
    """🌟 WINDOWS COMPATIBLE CUSTOM POP-UP DROPDOWN WITH DYNAMIC BINDING LOCK 🌟"""
    global tingkap_cadangan_global
    
    if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
        tingkap_cadangan_global.destroy()
        
    if not senarai_untuk_dipapar:
        return

    tingkap_cadangan_global = tk.Toplevel(win_induk)
    tingkap_cadangan_global.wm_overrideredirect(True)  
    tingkap_cadangan_global.configure(bg="#CBD5E1")
    tingkap_cadangan_global.wm_attributes("-topmost", True)
    
    # 🌟 KOREKSI 1 FOCUS-OUT: Hanya tutup dropdown jika fokus beralih ke tetingkap yang bukan milik dropdown 🌟
    def semak_fokus_keluar(event):
        win_induk.after(10, lakukan_semakan_fokus)

    def lakukan_semakan_fokus():
        global tingkap_cadangan_global
        if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
            fokus_sekarang = win_induk.focus_get()
            # Jika fokus sekarang bukan pada entry dan bukan pada listbox cadangan, tutup dropdown
            if fokus_sekarang != widget_entry and fokus_sekarang != listbox:
                tutup_dropdown()

    win_induk.bind("<FocusOut>", semak_fokus_keluar)
    
    x = widget_entry.winfo_rootx()
    y = widget_entry.winfo_rooty() + widget_entry.winfo_height()
    lebar = widget_entry.winfo_width()
    
    tingkap_cadangan_global.geometry(f"{lebar}x75+{x}+{y}")
    
    frame_list = tk.Frame(tingkap_cadangan_global, bg="white")
    frame_list.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(frame_list, orient=tk.VERTICAL)
    
    # Tukar takefocus=True supaya listbox boleh memegang fokus sementara pilihan mouse dibaca
    listbox = tk.Listbox(
        frame_list, font=("Segoe UI", 10), bd=1, relief="flat", 
        bg="white", fg="black", selectbackground="#0D6EFD", 
        highlightthickness=0, takefocus=True, yscrollcommand=scrollbar.set
    )
    
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    for nama in senarai_untuk_dipapar:
        listbox.insert(tk.END, nama)
        
    # 🌟 KOREKSI 2 EVENT CLICK: Menggunakan standard <<ListboxSelect>> murni Tkinter 🌟
    def on_select(event):
        try:
            indeks_pilihan = listbox.curselection()
            if indeks_pilihan:
                pilihan = listbox.get(indeks_pilihan[0])
                widget_entry.delete(0, tk.END)
                widget_entry.insert(0, pilihan)
                tutup_dropdown()
                widget_entry.focus_set()
        except Exception as err:
            print(f"Ralat pemilihan dropdown: {str(err)}")
            
    listbox.bind("<<ListboxSelect>>", on_select)
    
    # Sokongan pemilihan papan kekunci (Keyboard Enter key)
    listbox.bind("<Return>", on_select)
    
    # Kembalikan fokus input utama ke kotak entry dalam milisaat hantu Windows
    win_induk.after(1, lambda: widget_entry.focus_set())

def penapis_auto_suggest_safe(event, widget_entry, win_induk, senarai_asal=None):
    """🌟 MODE 1: MENAIP AUTOMATIK SUGGESTION (DENGAN RE-FETCH DATABASES) 🌟"""
    global tingkap_cadangan_global
    
    if event.keysym in ["Up", "Down", "Return", "Escape", "Tab", "Shift_L", "Shift_R"]:
        return

    teks_ditaip = widget_entry.get().upper()
    if teks_ditaip.strip() == "":
        tutup_dropdown()
        return

    senarai_segar = ambil_senarai_customer_dari_db()
    senarai_ditapis = [nama for nama in senarai_segar if teks_ditaip in nama]
    
    if senarai_ditapis:
        papar_senarai_toplevel(widget_entry, win_induk, senarai_ditapis)
    else:
        tutup_dropdown()

def aksi_butang_dropdown_pukal(widget_entry, win_induk, senarai_asal=None):
    """🌟 MODE 2: SKROL PENUH MANUAL VIA BUTTON ▼ (DENGAN RE-FETCH DATABASES) 🌟"""
    global tingkap_cadangan_global
    if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
        tutup_dropdown()
        return
        
    senarai_segar = ambil_senarai_customer_dari_db()
    papar_senarai_toplevel(widget_entry, win_induk, senarai_segar)

def tutup_dropdown():
    """Fungsi pembantu untuk menutup pop-up dari luar secara selamat"""
    global tingkap_cadangan_global
    if tingkap_cadangan_global and tingkap_cadangan_global.winfo_exists():
        tingkap_cadangan_global.destroy()
        tingkap_cadangan_global = None
