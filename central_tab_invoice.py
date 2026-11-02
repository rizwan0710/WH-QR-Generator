# ==============================================================================
# central_tab_invoice.py - FULL CLEAN INTEGRATED CODE (100% LIVE AUTO-REFRESH FIXED)
# ==============================================================================
import sqlite3
import csv
import qrcode
import tkinter as tk
from tkinter import messagebox, filedialog
import label_invoice_designer as lid
import invoice_preview_window
import database_manager as dbm  # 🌟 CONNECTS TO THE AUTO-CLEAN REFRESH ENGINE 🌟
from datetime import datetime


baris_hover_terakhir = None

def carian_invoice(jadual, entry_search=None):
    """🌟 LIVE INVOICE REFRESH FIX: Kalis Parameter None & Auto-Refresh Serentak NAS 🌟"""
    # Automated Cadence: Purges broken transaction records instantly when the user clicks REFRESH
    dbm.laksanakan_auto_clean_orphaned_logs()

    # 🚀 LIVE OVERRIDE CHANNEL: Jika entry_search tiada atau None, tetapkan teks sebagai kosong (Menghalang Crash UI)
    if entry_search is not None and hasattr(entry_search, 'get'):
        try:
            teks_carian = entry_search.get().strip().upper()
        except tk.TclError:
            teks_carian = ""
    else:
        teks_carian = ""
        
    for item in jadual.get_children():
        jadual.delete(item)
        
    kata_kunci_senarai = [k.strip() for k in teks_carian.split() if k.strip()]
        
    try:
        # Menggunakan sambungan pusat NAS dari database_manager (dbm)
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            
            # Carian pangkalan data bagi rekod Invoice siri INV%
            base_query = """
                SELECT id, sequence_no, tarikh, drawing_no, part_no, quantity, machine, lotcard_no, customer 
                FROM rekod_qr WHERE sequence_no LIKE 'INV%'
            """
            
            if not kata_kunci_senarai:
                cursor.execute(base_query + " ORDER BY id DESC")
                semua_rekod = cursor.fetchall()
            else:
                sub_queries = []
                parameter_sql = []
                
                for k in kata_kunci_senarai:
                    sub_queries.append("""
                        (sequence_no LIKE ? OR tarikh LIKE ? OR drawing_no LIKE ? OR 
                         part_no LIKE ? OR quantity LIKE ? OR machine LIKE ? OR 
                         lotcard_no LIKE ? OR customer LIKE ?)
                    """)
                    pola = f"%{k}%"
                    parameter_sql.extend([pola] * 8)
                    
                query_final = f"{base_query} AND ({ ' OR '.join(sub_queries) }) ORDER BY id DESC"
                cursor.execute(query_final, parameter_sql)
                semua_rekod = cursor.fetchall()
                
            for r in semua_rekod:
                inv_clean  = str(r[3]).upper().replace("INV:", "").strip()
                so_clean   = str(r[4]).upper().replace("SO:", "").strip()
                cust_clean = str(r[8]).upper().strip() if r[8] else "YAMAHA"
                page_stat  = str(r[7]).upper().strip() if r[7] else "BOX 1/1"
                outer_link = str(r[6]).upper().strip() if r[6] else "NONE"
                qty_clean  = f"{str(r[5]).upper().replace('PCS', '').strip()} PCS"
                
                # Lajur Treeview asal milik abang (Kekal 100% tepat)
                jadual.insert("", tk.END, values=(
                    "☐", r[0], r[2], cust_clean, inv_clean, so_clean, qty_clean, page_stat, outer_link, "INVOICE LOG", r[1]
                ), tags=('normal',))
                
    except sqlite3.Error as e:
        messagebox.showerror("DATA ERROR", f"FAILED TO PREVIEW INVOICE INFORMATION :\n{str(e)}")
        
def papar_pratonton_invoice_terpilih(jadual, win):
    """🌟 BUTANG PREVIEW DATABASE DI TAB INVOICE FIXED (WITH UNIVERSAL QR PAYLOAD) 🌟"""
    item_terpilih = []
    
    # Imbas semua baris dalam Treeview untuk mencari yang telah di-tanda (☑)
    for item_id in jadual.get_children():
        nilai_baris = jadual.item(item_id)['values']
        if nilai_baris and "☑" in str(nilai_baris[0]):
            item_terpilih.append(nilai_baris)
            
    if not item_terpilih:
        messagebox.showwarning("NO SELECTION", "PLEASE TICK (☑) AT LEAST ONE INVOICE RECORD TO PREVIEW!")
        return

    # HARD LOCK: Semak duplikasi "Linked Outer Box" (Indeks 8 dalam Treeview)
    senarai_outer_box = [str(r[8]).strip().upper() for r in item_terpilih if str(r[8]).strip() and str(r[8]).strip().upper() != "NONE"]
    if len(set(senarai_outer_box)) != len(senarai_outer_box):
        return messagebox.showerror(
            "🚨 SAME BOX SCAN ERROR",
            "PREVIEW REJECTED!\n\nYou have selected records that share the SAME Linked Outer Box Sequence Number!",
            parent=win
        )

    inv_no_induk = item_terpilih[0][4]
    senarai_kad_stiker = []

    try:
        for r in item_terpilih:
            cust_name = str(r[3])
            inv_no    = str(r[4])
            so_no     = str(r[5])
            qty_str   = str(r[6])
            page_stat = str(r[7])
            outer_seq = str(r[8])
            seq_inv   = str(r[10]) # Invoice Sequence No (e.g. INV26xxxx)

            qr_payload = (
                f"SERIAL NO  : {seq_inv.strip()}\n"
                f"INVOICE NO : {inv_no.strip()}\n"
                f"SO No      : {so_no.strip()}\n"
                f"CUSTOMER   : {cust_name.strip()}\n"
                f"QUANTITY   : {qty_str.strip()}"
            )

            # Bina Kod QR Universal
            qr = qrcode.QRCode(version=1, border=4, error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(qr_payload)
            qr.make(fit=True)
            im_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            # Hasilkan imej stiker grafik melalui modul label designer
            stk_img = lid.bina_imej_invoice(
                img_qr=im_qr, 
                invoice_no=inv_no, 
                so_no=so_no, 
                outer_seq=outer_seq, 
                outer_qty=qty_str, 
                seq_inv_spesifik=seq_inv, 
                text_paging=page_stat, 
                customer=cust_name
            )
            
            if stk_img:
                senarai_kad_stiker.append((stk_img, page_stat))

        if senarai_kad_stiker:
            invoice_preview_window.buka_popup_individual_1by1(win, senarai_kad_stiker, inv_no_induk)
        else:
            messagebox.showerror("RENDER ERROR", "FAILED TO GENERATE GRAPHICAL IMAGE LABELS FOR PREVIEW.", parent=win)

    except Exception as e:
        messagebox.showerror("PREVIEW EXCEPTION", f"SYSTEM ERROR DURING RENDERING:\n{str(e)}", parent=win)
def on_invoice_click(event, jadual):
    item_id = jadual.identify_row(event.y)
    if item_id:
        semua_nilai = list(jadual.item(item_id)['values'])
        if semua_nilai:
            tanda_baru = "☑" if "☐" in str(semua_nilai[0]) else "☐"
            tag_baru = 'checked' if tanda_baru == "☑" else 'normal'
            semua_nilai[0] = tanda_baru
            jadual.item(item_id, values=semua_nilai, tags=(tag_baru,))

def on_mouse_hover(event, jadual):
    global baris_hover_terakhir
    item_id = jadual.identify_row(event.y)
    if item_id != baris_hover_terakhir:
        if baris_hover_terakhir and jadual.exists(baris_hover_terakhir):
            nilai_lama = jadual.item(baris_hover_terakhir)['values']
            tag_asal = 'checked' if "☑" in str(nilai_lama[0]) else 'normal'
            jadual.item(baris_hover_terakhir, tags=(tag_asal,))
        if item_id:
            nilai_sekarang = jadual.item(item_id)['values']
            if "☐" in str(nilai_sekarang[0]):
                jadual.item(item_id, tags=('hover',))
        baris_hover_terakhir = item_id

def on_mouse_leave(event, jadual):
    global baris_hover_terakhir
    if baris_hover_terakhir and jadual.exists(baris_hover_terakhir):
        nilai_lama = jadual.item(baris_hover_terakhir)['values']
        tag_asal = 'checked' if "☑" in str(nilai_lama[0]) else 'normal'
        jadual.item(baris_hover_terakhir, tags=(tag_asal,))
    baris_hover_terakhir = None

def susun_lajur_treeview(jadual, lajur, menaik):
    pass

def eksport_invoice_excel():
    p = filedialog.asksaveasfilename(
        title="SAVE INVOICE REPORT AS",
        defaultextension=".csv", 
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if not p:
        return
    try:
        # ✅ BENAR: Menggunakan sambungan pusat NAS secara langsung
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            
            # 🛠️ DETEKSI LAJUR DINAMIK: Kalis ralat jika IT menukar nama kolom di db pusat
            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError:
                lajur_seq = "sequence_no"
                
            # Ambil data invoice (INV) dengan urutan lajur yang stabil
            query_sql = f"""
                SELECT id, {lajur_seq}, tarikh, drawing_no, part_no, quantity, machine, lotcard_no, customer 
                FROM rekod_qr 
                WHERE {lajur_seq} LIKE 'INV%' 
                ORDER BY id DESC
            """
            cursor.execute(query_sql)
            rows = cursor.fetchall()
            
            if not rows:
                messagebox.showwarning("WARNING", "NO INVOICE DATA FOUND IN CENTRAL DATABASE!")
                return
                
            # Tulis ke dalam fail CSV murni dengan encoding yang selamat untuk Excel
            with open(p, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                # Header dipastikan selari 100% dengan urutan SELECT di atas
                writer.writerow(["ID", "Sequence No", "Date", "Invoice No", "SO No", "Quantity", "Linked Outer Box", "Page Status", "Customer"])
                writer.writerows(rows)
                
            messagebox.showinfo("SUCCESS", "Invoice report exported successfully from Central NAS!")
            
    except Exception as e:
        messagebox.showerror("SYSTEM ERROR", f"FAILED TO EXPORT INVOICE DATA:\n{str(e)}")
