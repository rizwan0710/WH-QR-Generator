# invoice_tab_logic.py - FULL CLEAN INTEGRATED CODE (NO PACKING DISPLAY IN QR FOR EXISTING DATA)
import sqlite3
import csv
import qrcode
import tkinter as tk
from tkinter import messagebox, filedialog
import label_invoice_designer as lid
import invoice_preview_window

baris_hover_terakhir = None

def carian_invoice(jadual, entry_search):
    """🌟 LIVE INVOICE REFRESH FIX: Membaca kuantiti murni terkini terus dari SQLite 🌟"""
    teks_carian = entry_search.get().strip().upper()
    for item in jadual.get_children():
        jadual.delete(item)
        
    kata_kunci_senarai = [k.strip() for k in teks_carian.split() if k.strip()]
        
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
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
                
                # Lajur Treeview: ("Select", "ID", "Date", "Customer", "Invoice No", "SO No", "Quantity", "Page Status", "Linked Outer Box", "Box Type", "Invoice Sequence No")
                jadual.insert("", tk.END, values=(
                    "☐", r[0], r[2], cust_clean, inv_clean, so_clean, qty_clean, page_stat, outer_link, "INVOICE LOG", r[1]
                ), tags=('normal',))
                
    except sqlite3.Error as e:
        messagebox.showerror("DATA ERROR", f"FAILED TO PREVIEW INVOICE INFORMATION :\n{str(e)}")

def papar_pratonton_invoice_terpilih(jadual, win):
    """🌟 BUTANG PREVIEW DATABASE DI TAB INVOICE FIXED (WITH UNIVERSAL QR PAYLOAD - NO PACKING) 🌟"""
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

    # Ambil Invoice No daripada item pertama untuk tajuk tetingkap popup
    inv_no_induk = item_terpilih[0][4]
    senarai_kad_stiker = []

    try:
        for r in item_terpilih:
            # Pengekstrakan nilai mengikut susunan indeks lajur Treeview
            cust_name = str(r[3])
            inv_no    = str(r[4])
            so_no     = str(r[5])
            qty_str   = str(r[6])
            page_stat = str(r[7])
            outer_seq = str(r[8])
            seq_inv   = str(r[10]) # Invoice Sequence No (e.g. INV26xxxx)

            # 🌟 KINI DIUBAH KEPADA PAYLOAD UNIVERSAL TERPIAWAI BAGI REKOD SEDIA ADA (TANPA PACKING DISPLAY) 🌟
            qr_payload = (
                f"SERIAL NO  : {seq_inv.strip()}\n"
                f"INVOICE NO : {inv_no.strip()}\n"
                f"SO No      : {so_no.strip()}\n"
                f"CUSTOMER   : {cust_name.strip()}\n"
                f"QUANTITY   : {qty_str.strip()}"
            )

            # 1. Bina semula Kod QR Universal secara on-the-fly untuk data lama
            qr = qrcode.QRCode(version=1, border=1)
            qr.add_data(qr_payload)
            qr.make(fit=True)
            im_qr = qr.make_image().convert("RGB")

            # 2. Hasilkan semula imej stiker grafik melalui modul label designer
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
                # Masukkan ke dalam format tuple yang diperlukan oleh panel pratonton (Image, Text_Paging)
                senarai_kad_stiker.append((stk_img, page_stat))

        if senarai_kad_stiker:
            # 3. Lancarkan tetingkap popup pengurus paparan dan cetakan
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
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, sequence_no, tarikh, drawing_no, part_no, quantity, machine, customer FROM rekod_qr WHERE sequence_no LIKE 'INV%' ORDER BY id DESC")
            semua_data = cursor.fetchall()
        if not semua_data:
            messagebox.showwarning("WARNING", "NO INVOICE DATA TO BE EXPORT!")
            return
        path_excel = filedialog.asksaveasfilename(initialfile="Laporan_Form3_Invoice_Packing.csv", defaultextension=".csv")
        if path_excel:
            with open(path_excel, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Invoice Sequence No", "Date", "Invoice No", "SO No", "Quantity", "Linked Outer Box", "Customer"])
                writer.writerows(semua_data)
            messagebox.showinfo("SUCCESS", "Invoice packing export report saved successfully!")
    except Exception as e:
        messagebox.showerror("EXPORT ERROR", str(e))
