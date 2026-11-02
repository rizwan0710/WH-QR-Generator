# ==============================================================================
# invoice_tab_logic.py - FULL STANDARDIZED INTEGRATION CODE (OHTA COUPLING FIX)
# ==============================================================================
import sqlite3
import csv
import qrcode
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import label_invoice_designer as lid
import invoice_preview_window
import database_manager as dbm  # Enjin carian pusat pembasmi log yatim NAS

baris_hover_terakhir = None

def carian_invoice(jadual, entry_search=None):
    """Menguruskan muatan data logs Invoice Shipped secara dinamik terus dari pangkalan data NAS."""
    dbm.laksanakan_auto_clean_orphaned_logs()

    teks_carian = ""
    if entry_search is not None and hasattr(entry_search, 'get'):
        try:
            teks_carian = entry_search.get().strip().upper()
        except:
            teks_carian = ""
        
    for item in jadual.get_children():
        jadual.delete(item)
        
    kata_kunci_senarai = [k.strip() for k in teks_carian.split() if k.strip()]
        
    conn = dbm.get_db_connection()
    cursor = conn.cursor()
    
    # Base query asal memulangkan lajur dari pangkalan data rekod_qr
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
        # 1. PETA ASAL: Ekstrak 9 data dari database rekod_qr secara tersusun
        db_id      = r[0]
        seq_inv    = r[1]  # Menyimpan nilai Invoice Sequence No (Contoh: INV2610210002)
        tarikh     = r[2]  # Menyimpan nilai tarikh
        drawing_no = r[3]  # Menyimpan Invoice No
        part_no    = r[4]  # Menyimpan SO No
        quantity   = r[5]  # Menyimpan Box Quantity
        machine    = r[6]  # Menyimpan maklumat Linked Outer Box (Contoh: B2610200002)
        lotcard_no = r[7]  # Menyimpan Page Status (Contoh: BOX 1/2)
        customer   = r[8]  # Menyimpan Nama Pelanggan
        
        # 2. PEMBERSIHAN DATA
        inv_clean  = str(drawing_no).upper().replace("INV:", "").strip() if drawing_no else ""
        so_clean   = str(part_no).upper().replace("SO:", "").strip() if part_no else ""
        cust_clean = str(customer).upper().strip() if customer else ""
        page_stat  = str(lotcard_no).upper().strip() if lotcard_no else "BOX 1/1"
        qty_clean  = str(quantity).strip() if quantity else "0"
        linked_box = str(machine).upper().strip() if machine else "-"
        
        # 🌟 3. PENJAJARAN BARU: Membuang elemen Box Type dan meletakkan seq_inv sebagai elemen ke-10 (terakhir) 🌟
        jadual.insert("", tk.END, values=(
            "☐",              # 1. Kolum Select Checkbox
            db_id,            # 2. Kolum ID
            tarikh,           # 3. Kolum Date
            cust_clean,       # 4. Kolum Customer Name
            inv_clean,        # 5. Kolum Invoice No
            so_clean,         # 6. Kolum SO No
            qty_clean,        # 7. Kolum Box Quantity
            page_stat,        # 8. Kolum Page Status
            linked_box,       # 9. Kolum Linked Outer Box (`B26102...` akan masuk sini)
            seq_inv           # 10. Kolum Invoice Sequence No (`INV26102...` akan masuk di sini dengan betul!)
        ), tags=('normal',))

    conn.close()




def papar_pratonton_invoice_terpilih(jadual, win):
    """🌟 BUTANG PREVIEW INDEKS FIX: Membaca susunan lajur skrin menggunakan indeks dinamik/negatif selamat 🌟"""
    item_terpilih = []
    
    for item_id in jadual.get_children():
        nilai_baris = jadual.item(item_id)['values']
        if nilai_baris and "☑" in str(nilai_baris):
            item_terpilih.append(nilai_baris)
            
    if not item_terpilih:
        messagebox.showwarning("NO SELECTION", "PLEASE TICK (☑) AT LEAST ONE INVOICE RECORD TO PREVIEW!", parent=win)
        return

    # Menggunakan indeks dinamik berdasarkan panjang array untuk mengelakkan IndexError akibat pembuangan lajur
    senarai_outer_box = []
    for r in item_terpilih:
        if len(r) >= 9:
            # Linked Outer Box berada di kedudukan kedua terakhir (Indeks -2) selepas Box Type dibuang
            idx_outer = -2 if len(r) < 11 else 8
            val_outer = str(r[idx_outer]).strip().upper()
            if val_outer and val_outer != "NONE":
                senarai_outer_box.append(val_outer)

    if len(set(senarai_outer_box)) != len(senarai_outer_box):
        return messagebox.showerror(
            "🚨 SAME BOX SCAN ERROR",
            "PREVIEW REJECTED!\n\nYou have selected records that share the SAME Linked Outer Box Sequence Number!",
            parent=win
        )

    inv_no_induk = item_terpilih[0][4] if item_terpilih and len(item_terpilih[0]) > 4 else "INVOICE"
    senarai_kad_stiker = []

    try:
        for r in item_terpilih:
            # Membaca data menggunakan fallback dinamik mengikut struktur panjang lajur semasa
            panjang_lajur = len(r)
            
            cust_name = str(r[3]).strip()
            inv_no    = str(r[4]).strip()
            so_no     = str(r[5]).strip()
            qty_str   = str(r[6]).strip()
            
            # Pembetulan berantai berasaskan kedudukan lajur dari belakang (Negatif Indeks)
            if panjang_lajur < 11:
                # Jika lajur Box Type (asalnya indeks 9) sudah dibuang:
                page_stat = str(r[-3]).strip()  # Page Status (Box 1/2)
                outer_seq = str(r[-2]).strip()  # Linked Outer Box (B2610...)
                seq_inv   = str(r[-1]).strip()  # Invoice Sequence No (INV26...) -> Lajur paling akhir
            else:
                # Susunan asal jika lajur penuh 11 kolum masih aktif
                page_stat = str(r[7]).strip()
                outer_seq = str(r[8]).strip()
                seq_inv   = str(r[10]).strip()

            qr_payload = (
                f"SERIAL NO  : {seq_inv}\n"
                f"INVOICE NO : {inv_no}\n"
                f"SO No      : {so_no}\n"
                f"CUSTOMER   : {cust_name}\n"
                f"QUANTITY   : {qty_str}"
            )

            qr = qrcode.QRCode(version=1, border=4, error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(qr_payload)
            qr.make(fit=True)
            im_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

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
def eksport_invoice_excel():
    p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not p: return
    try:
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, sequence_no, tarikh, drawing_no, part_no, quantity, machine, lotcard_no, customer FROM rekod_qr WHERE sequence_no LIKE 'INV%' ORDER BY id DESC")
            rows = cursor.fetchall()
            with open(p, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Sequence No", "Date", "Invoice No", "SO No", "Quantity", "Linked Outer Box", "Page Status", "Customer"])
                writer.writerows(rows)
            messagebox.showinfo("SUCCESS", "Invoice report exported successfully!")
    except Exception as e:
        messagebox.showerror("SYSTEM ERROR", str(e))

def bina_tab_invoice(f_tb, f_tp, win, gate_pratonton_seragam, fungsi_padam):
    """Membina susunan visual grid jadual tab Invoice Shipped dengan menu klik kanan menyeluruh."""
    # ─── SECTION 1: KOTAK CARIAN & LABEL ───
    tk.Label(f_tp, text="Search Invoice:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    global e_s
    e_s = tk.Entry(f_tp, width=22, font=("Segoe UI", 10))
    e_s.pack(side=tk.LEFT, padx=5)
    
    e_s.bind("<Return>", lambda e: carian_invoice(jad_inv, e_s))
    
    # 🌟 INTEGRASI UTAMA: Bina menu klik kanan PASTE khusus untuk kotak input carian
    def bina_menu_klik_kanan_input(event, widget_input, win_parent):
        menu_input = tk.Menu(win_parent, tearoff=0, font=("Segoe UI", 10))
        
        def laksanakan_paste_input():
            try:
                # Ambil teks dari clipboard sistem komputer
                teks_clipboard = win_parent.clipboard_get().strip()
                # Padam teks lama dalam kotak input dan masukkan teks baharu
                widget_input.delete(0, tk.END)
                widget_input.insert(0, teks_clipboard)
                widget_input.focus_set()
            except Exception:
                pass
                
        menu_input.add_command(label="📥 PASTE", command=laksanakan_paste_input)
        menu_input.post(event.x_root, event.y_root)

    # Mengikat klik kanan tetikus (Button-3) tepat pada kotak input carian
    e_s.bind("<Button-3>", lambda e: bina_menu_klik_kanan_input(e, e_s, win))
    
    # ─── SECTION 2: BAR KAWALAN SEBELAH KIRI ───
    tk.Button(f_tp, text="SEARCH", command=lambda: carian_invoice(jad_inv, e_s), bg="#0D6EFD", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="RESET", command=lambda: [e_s.delete(0, tk.END), carian_invoice(jad_inv, e_s)], bg="#6C757D", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    
    tk.Button(f_tp, text="PREVIEW SELECTED", command=lambda: papar_pratonton_invoice_terpilih(jad_inv, win), bg="#198754", fg="white", font=("Segoe UI", 9, "bold"), width=18, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=10)
    tk.Button(f_tp, text="DELETE SELECTED", command=lambda: fungsi_padam(jad_inv, e_s), bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold"), width=15, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="📥 EXPORT CSV", command=eksport_invoice_excel, bg="#212529", fg="white", font=("Segoe UI", 9, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    
    # ─── SECTION 3: BAR KAWALAN SEBELAH KANAN ───
    tk.Button(f_tp, text="◀ BACK TO MAIN", command=win.destroy, bg="#374151", fg="white", font=("Segoe UI", 9, "bold"), width=16, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=2)
    tk.Button(f_tp, text="🔄 REFRESH", command=lambda: carian_invoice(jad_inv, e_s), bg="#17A2B8", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=2)

    # ─── SECTION 4: STRUKTUR JADUAL TREEVIEW ───
    lajur_invoice = ("Select", "ID", "Date", "Customer Name", "Invoice No", "SO No", "Box Quantity", "Page Status", "Linked Outer Box",  "Invoice Sequence No")
    
    global jad_inv
    jad_inv = ttk.Treeview(f_tb, columns=lajur_invoice, show="headings", selectmode="browse", style="CentralInner.Treeview")
    
    jad_inv.tag_configure('normal', background='white', foreground='black')
    jad_inv.tag_configure('hover', background='#E8F0FE', foreground='black')
    jad_inv.tag_configure('checked', background='#E8F5E9', foreground='#1B5E20')

    jad_inv.bind("<Button-1>", lambda e: on_invoice_click(e, jad_inv))
    jad_inv.bind("<Motion>", lambda e: on_mouse_hover(e, jad_inv))
    jad_inv.bind("<Leave>", lambda e: on_mouse_leave(e, jad_inv))
    
    # Mengikat klik kanan mouse (Button-3) pada jadual untuk fungsi COPY sahaja
    jad_inv.bind("<Button-3>", lambda e: bina_menu_klik_kanan_invoice(e, jad_inv, win))

    for col in lajur_invoice:
        jad_inv.heading(col, text=col)
        jad_inv.column(col, width=90, anchor="center")
        
    jad_inv.column("Select", width=50)
    jad_inv.column("ID", width=40)
    jad_inv.column("Customer Name", width=140, anchor="w")
    jad_inv.column("Linked Outer Box", width=120)
    jad_inv.column("Invoice Sequence No", width=130)

    sb = ttk.Scrollbar(f_tb, orient=tk.VERTICAL, command=jad_inv.yview)
    jad_inv.configure(yscrollcommand=sb.set)
    jad_inv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    
    carian_invoice(jad_inv, None)
    
def bina_menu_klik_kanan_invoice(event, jadual, win_parent):
    """Membina menu klik kanan jadual visual semata-mata untuk tujuan COPY data sel."""
    item_id = jadual.identify_row(event.y)
    col_id = jadual.identify_column(event.x)
    
    if not item_id or not col_id:
        return
        
    try:
        col_index = int(col_id.replace("#", "")) - 1
        nilai_baris = jadual.item(item_id)['values']
        teks_salin = str(nilai_baris[col_index]).strip()
    except Exception:
        return

    menu_popup = tk.Menu(win_parent, tearoff=0, font=("Segoe UI", 10))
    
    def laksanakan_salin():
        win_parent.clipboard_clear()
        win_parent.clipboard_append(teks_salin)
        win_parent.update()

    # Hanya pilihan COPY disediakan apabila klik kanan di atas sel jadual
    menu_popup.add_command(label=f"📋 COPY: '{teks_salin}'", command=laksanakan_salin)
    menu_popup.post(event.x_root, event.y_root)

