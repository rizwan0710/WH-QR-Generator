import sqlite3
import qrcode
import tkinter as tk
from tkinter import messagebox
import label_invoice_designer as lid
import invoice_preview_window as ipw

def proses_pratonton_invoice(item_ditanda, root):
    """
    🌟 FIX MUTTAMAD TOTAL: LIVE DATA REFETCH ENGINE (COLUMN NAME TRACKER) 🌟
    Membaca data terus mengikut nama lajur visual Treeview untuk mengelakkan ralat heretan indeks array.
    """
    # Dapatkan rujukan jadual Treeview Invoice secara langsung dari root parent
    # Kita cari widget Treeview yang sedang aktif untuk membaca data paling segar
    try:
        # Cari widget jadual Treeview di dalam tetingkap
        jadual = None
        for widget in root.winfo_children():
            if isinstance(widget, ttk.Notebook):
                for tab in widget.winfo_children():
                    for sub_w in tab.winfo_children():
                        if isinstance(sub_w, ttk.Treeview):
                            jadual = sub_w
                            break
    except:
        jadual = None

    # Mengambil item yang sedang di-highlight biru oleh operator (Paling Tepat & Segar)
    try:
        if jadual and jadual.selection():
            target_item_id = jadual.selection()[0]
            inv_no_raw = str(jadual.set(target_item_id, "Invoice No")).upper().replace("INV:", "").strip()
            so_no_raw  = str(jadual.set(target_item_id, "SO No")).upper().replace("SO:", "").strip()
        else:
            # Fallback keselamatan jika rujukan jadual tidak ditemui
            baris_pilihan = item_ditanda[0] if isinstance(item_ditanda, list) else item_ditanda
            inv_no_raw = str(baris_pilihan[4]).upper().replace("INV:", "").strip()
            so_no_raw  = str(baris_pilihan[5]).upper().replace("SO:", "").strip()
    except Exception:
        # Pelindung akhir jika susunan array berubah
        baris_pilihan = item_ditanda[0] if isinstance(item_ditanda, list) else item_ditanda
        inv_no_raw = str(baris_pilihan[4]).upper().replace("INV:", "").strip()
        so_no_raw  = str(baris_pilihan[5]).upper().replace("SO:", "").strip()
    
    semua_batch = []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            
            # 🌟 LIVE REFETCH LOCK: Tarik kuantiti paling segar murni dari SQLite menggunakan operator LIKE 🌟
            query_cari = """
                SELECT id, drawing_no, part_no, quantity, machine, lotcard_no, sequence_no, customer 
                FROM rekod_qr 
                WHERE drawing_no LIKE ? 
                  AND part_no LIKE ? 
                  AND sequence_no LIKE 'INV%' 
                ORDER BY sequence_no ASC
            """
            cursor.execute(query_cari, (f"%{inv_no_raw}%", f"%{so_no_raw}%"))
            semua_batch = cursor.fetchall()
            
    except sqlite3.Error as e:
        messagebox.showerror("DATABASE ERROR", f"FAILED TO READ DATABASE:\n{str(e)}", parent=root)
        return
        
    if not semua_batch:
        messagebox.showwarning("REMINDER", f"No INVOICE GROUP DATA WAS FOUND IN THE SYSTEM FOR INVOICE NO: {inv_no_raw}!", parent=root)
        return
        
    senarai_kad_tunggal_db = []
    total_halaman = len(semua_batch)
    
    # 🚀 ENJIN RE-GENERATION GRAFIK SEGAR MURNI REAL-TIME
    for idx, (r_id, dr_val, pt_val, qty_val, mac_val, lot_val, seq_val, cust_val) in enumerate(semua_batch):
        halaman_semasa = idx + 1
        text_paging = f"BOX {halaman_semasa}/{total_halaman}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_val)
        qr.make(fit=True)
        img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        
        # 🌟 FORCE REFETCH: Paksa bacaan data kuantiti terkini yang di-save dari database (qty_val) 🌟
        clean_qty = str(qty_val).upper().replace("PCS", "").strip()
        clean_inv = str(dr_val).upper().replace("INV:", "").strip()
        clean_so  = str(pt_val).upper().replace("SO:", "").strip()
        
        # Jana grafik imej stiker baharu dengan data murni yang segar
        img_kad_tunggal = lid.bina_imej_invoice(img_qr_mentah, clean_inv, clean_so, mac_val, clean_qty, seq_val, text_paging, cust_val)
        senarai_kad_tunggal_db.append((img_kad_tunggal, text_paging))
        
    # Buka tetingkap premium slider tunggal lengkap dengan kawalan butang PREVIOUS & NEXT
    ipw.buka_popup_individual_1by1(root, senarai_kad_tunggal_db, inv_no_raw)
