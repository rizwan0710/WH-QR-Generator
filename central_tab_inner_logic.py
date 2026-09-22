import sqlite3
import csv
import os
import qrcode
import re
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import label_designer as ld
import invoice_print_manager  # Triggers the newly added 1-bit crisp binary printer engine

baris_hover_terakhir = None

def carian_inner(jadual, entry_search):
    """Extracts dynamic inner box tracking information filtered via standard SQL fields."""
    try:
        teks_carian = entry_search.get().strip().upper()
    except tk.TclError:
        return
        
    for item in jadual.get_children():
        jadual.delete(item)
        
    kata_kunci_senarai = [k.strip() for k in teks_carian.split() if k.strip()]
        
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            
            if not kata_kunci_senarai:
                cursor.execute("""
                    SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no 
                    FROM rekod_qr WHERE sequence_no LIKE 'WP%' ORDER BY id DESC
                """)
                semua_rekod = cursor.fetchall()
            else:
                sub_queries = []
                parameter_sql = []
                
                for k in kata_kunci_senarai:
                    sub_queries.append("""
                        (tarikh LIKE ? OR customer LIKE ? OR drawing_no LIKE ? OR 
                         part_no LIKE ? OR quantity LIKE ? OR mfg_date LIKE ? OR 
                         machine LIKE ? OR lotcard_no LIKE ? OR sequence_no LIKE ?)
                    """)
                    pola = f"%{k}%"
                    parameter_sql.extend([pola] * 9)
                    
                query_final = f"""
                    SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no 
                    FROM rekod_qr 
                    WHERE sequence_no LIKE 'WP%' AND ({ " OR ".join(sub_queries) })
                    ORDER BY id DESC
                """
                cursor.execute(query_final, parameter_sql)
                semua_rekod = cursor.fetchall()
                
            for r in semua_rekod:
                jadual.insert("", tk.END, values=(
                    "☐", r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]
                ), tags=('normal',))
    except sqlite3.Error as e:
        messagebox.showerror("DATABASE ERROR", f"FAILED TO UPLOAD INNER DATA:\n{str(e)}")
def on_inner_click(event, jadual):
    item_id = jadual.identify_row(event.y)
    if item_id:  
        semua_nilai = list(jadual.item(item_id)['values'])
        if semua_nilai:
            if "☐" in str(semua_nilai[0]):
                tanda_baru = "☑"
                tag_baru = 'checked'
            else:
                tanda_baru = "☐"
                tag_baru = 'normal'
                
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

def bina_menu_klik_kanan_global(event, jadual, root):
    item_id = jadual.identify_row(event.y)
    column_id = jadual.identify_column(event.x)
    if not item_id: return
    jadual.selection_set(item_id)
    semua_nilai = jadual.item(item_id)['values']
    try:
        col_idx = int(column_id.replace("#", "")) - 1
        nilai_sel = str(semua_nilai[col_idx]).strip()
    except (ValueError, IndexError):
        nilai_sel = ""
    menu_popup = tk.Menu(root, tearoff=0)
    if nilai_sel and col_idx > 0:
        menu_popup.add_command(label=f"📋 Copy : '{nilai_sel}'", command=lambda: [root.clipboard_clear(), root.clipboard_append(nilai_sel), messagebox.showinfo("Copied", f"Copied to clipboard:\n{nilai_sel}", parent=root)])
        menu_popup.add_separator()
    teks_baris_penuh = " | ".join([str(v) for idx, v in enumerate(semua_nilai) if idx > 0])
    menu_popup.add_command(label="📄 Copy Row ", command=lambda: [root.clipboard_clear(), root.clipboard_append(teks_baris_penuh), messagebox.showinfo("Copied", "Full row successfully copied!", parent=root)])
    menu_popup.post(event.x_root, event.y_root)

def bina_menu_paste_search_global(event, entry_widget, root):
    menu_paste = tk.Menu(root, tearoff=0)
    try: teks_clipboard = root.clipboard_get().strip()
    except tk.TclError: teks_clipboard = ""
    if teks_clipboard:
        menu_paste.add_command(label="📋 Paste Text ", command=lambda: [entry_widget.insert(tk.END, teks_clipboard if not entry_widget.get() else f" {teks_clipboard}")])
    else:
        menu_paste.add_command(label="[ Clipboard Empty ]", state="disabled")
    menu_paste.post(event.x_root, event.y_root)
def jana_grafik_label_dari_row(r):
    """
    🌟 ENJIN EKSTRAKSI INDEKS TREEVIEW MUTLAK (TREEVIEW STRICT INDEX MAPPING) 🌟
    Menjamin pemetaan lajur yang tepat berdasarkan data baris tuple jadual utama.
    """
    try:
        elemen = [str(x).strip() for x in r]
        
        if elemen and (elemen[0] in ("☐", "☑") or len(elemen[0]) == 1):
            elemen = elemen[1:]
            
        # Susunan elemen pangkalan data selepas dibuang checkbox:
        # [0:id, 1:tarikh, 2:customer, 3:drawing_no, 4:part_no, 5:quantity, 6:mfg_date, 7:machine, 8:lotcard_no, 9:sequence_no]
        if len(elemen) >= 10:
            tarikh   = elemen[1]
            customer = elemen[2]
            drawing  = elemen[3]
            part     = elemen[4]
            qty      = elemen[5]
            mfg      = elemen[6]
            mac      = elemen[7]
            lot_no   = elemen[8]  # Indeks 8 memegang data Lotcard No tulen
            seq_no   = elemen[9]  # Indeks 9 memegang data Sequence No tulen (WP...)
        else:
            tarikh = customer = drawing = part = qty = mfg = mac = lot_no = seq_no = ""
            for item in elemen:
                if item.startswith("WP"):
                    seq_no = item
            calon_lot = [x for x in elemen if x and not x.startswith("WP") and len(x) > 2]
            lot_no = calon_lot[-1] if calon_lot else "N/A"
            
    except Exception as e:
        tarikh = customer = drawing = part = qty = mfg = mac = lot_no = seq_no = "Error"

    # Pembersihan paparan Lot No
    if not lot_no or lot_no.upper() in ("NONE", "N/A", "", "☐", "☑") or lot_no.startswith("WP"):
        lot_no = "N/A"

    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(seq_no)
    qr.make(fit=True)
    img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    
    return ld.bina_imej_gabungan(img_qr_mentah, tarikh, drawing, part, qty, mfg, mac, seq_no, customer, lot_no), seq_no

def padam_rekod_inner_terpilih(jadual, entry_search):
    """
    🗑️ ENJIN PEMADAMAN PUKAL MUKTAMAD (DATABASE COMMIT FIX) 🗑️
    Memadamkan data terpilih (☑) daripada fail warehouse_data.db secara kekal
    menggunakan SQL commit rasmi dan menyegarkan semula Treeview UI secara automatik.
    """
    item_dipilih = []
    
    for item_id in jadual.get_children():
        nilai = jadual.item(item_id)['values']
        if nilai and "☑" in str(nilai[0]):
            item_dipilih.append((item_id, nilai[1]))  # nilai[1] memegang 'id' unik rekod database

    if not item_dipilih:
        messagebox.showwarning("SYSTEM WARNING", "SILA TANDA (☑) PADA REKOD YANG MAHU DIPADAM!")
        return

    msg_tanya = f"Adakah anda pasti mahu memadam {len(item_dipilih)} rekod terpilih daripada sistem secara KEKAL?"
    if messagebox.askyesno("CONFIRM DELETE", msg_tanya):
        try:
            with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
                cursor = conn.cursor()
                
                for item_id, db_id in item_dipilih:
                    cursor.execute("DELETE FROM rekod_qr WHERE id = ?", (db_id,))
                
                # 🌟 KUNCI UTAMA: Wajib commit untuk menulis perubahan kekal ke dalam disk piring keras! 🌟
                conn.commit()
                
            messagebox.showinfo("SUCCESS", f"Berjaya memadam {len(item_dipilih)} rekod daripada sistem!")
            carian_inner(jadual, entry_search)
            
        except sqlite3.Error as e:
            messagebox.showerror("DATABASE ERROR", f"GAGAL MEMADAM REKOD KILANG:\n{str(e)}")

def eksport_inner_excel():
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no FROM rekod_qr WHERE sequence_no LIKE 'WP%' ORDER BY id DESC")
            semua_data = cursor.fetchall()
        if not semua_data:
            messagebox.showwarning("WARNING", "NO DATA TO EXPORT!")
            return
        path_excel = filedialog.asksaveasfilename(initialfile="Laporan_Form1_Inner_Packing.csv", defaultextension=".csv")
        if path_excel:
            with open(path_excel, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["ID", "Date", "Customer Name", "Drawing No", "Part Number", "Quantity", "Mnfd Date", "Machine", "Lotcard No", "Sequence Number"])
                writer.writerows(semua_data)
            messagebox.showinfo("SUCCESS", "The Inner Packing report has been successfully saved!")
    except Exception as e: 
        messagebox.showerror("SYSTEM ERROR", str(e))

def susun_lajur_treeview(jadual, lajur, menaik):
    pass
