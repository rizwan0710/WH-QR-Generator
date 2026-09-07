 import sqlite3
import csv
import tkinter as tk
from tkinter import messagebox, filedialog

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
                # r[0]=id, r[1]=sequence_no, r[2]=tarikh, r[3]=drawing_no (Invoice No)
                # r[4]=part_no (SO No), r[5]=quantity, r[6]=machine (Linked Outer)
                # r[7]=lotcard_no (Page Status), r[8]=customer
                
                inv_clean  = str(r[3]).upper().replace("INV:", "").strip()
                so_clean   = str(r[4]).upper().replace("SO:", "").strip()
                cust_clean = str(r[8]).upper().strip() if r[8] else "YAMAHA"
                page_stat  = str(r[7]).upper().strip() if r[7] else "BOX 1/1"
                outer_link = str(r[6]).upper().strip() if r[6] else "NONE"
                
                # 🌟 KUNCI REFRESH INVOICE: Ambil nilai kuantiti segar dari lajur quantity database (r[5])
                qty_clean  = f"{str(r[5]).upper().replace('PCS', '').strip()} PCS"
                
                # Susunan lajur Treeview Invoice:
                # ("Select", "ID", "Date", "Customer", "Invoice No", "SO No", "Quantity", "Page Status", "Linked Outer Box", "Box Type", "Invoice Sequence No")
                jadual.insert("", tk.END, values=(
                    "☐", r[0], r[2], cust_clean, inv_clean, so_clean, qty_clean, page_stat, outer_link, "INVOICE LOG", r[1]
                ), tags=('normal',))
                
    except sqlite3.Error as e:
        messagebox.showerror("DATA ERROR", f"FAILED TO PREVIEW INVOICE INFORMATION :\n{str(e)}")

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
                writer.writerow(["ID", "Invoice Sequence No", "Date", "Invoice No", "SO No", "Quantity (Pcs)", "Linked Outer Box", "Customer"])
                for r in semua_data:
                    writer.writerow([r[0], r[1], r[2], str(r[3]).replace("INV:","").strip(), str(r[4]).replace("SO:","").strip(), r[5], r[6], r[7]])
            messagebox.showinfo("SUCCESS", "Invoice Packing Report successfully saved!")
    except Exception as e:
        messagebox.showerror("Ralat Sistem", str(e))
