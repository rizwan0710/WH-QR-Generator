import sqlite3, csv, qrcode, re, os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import label_outer_designer as lod
import database_batch_preview

baris_hover_terakhir = None

def semak_dan_pencetus_popup_gatekeeper(parent_win):
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, outer_seq, qty_baru FROM pending_sync LIMIT 1")
            row = cursor.fetchone()
            if row:
                pending_id, outer_code, qty_baru_str = row[0], str(row[1]).strip(), str(row[2]).strip()
                if messagebox.askyesno("⚠️ PENDING DATA SYNC", f"Sync changes for [{outer_code}] to Invoice Logs?", parent=parent_win):
                    cursor.execute("UPDATE rekod_qr SET quantity = ? WHERE sequence_no LIKE 'INV%' AND machine = ?", (qty_baru_str, outer_code))
                    cursor.execute("DELETE FROM pending_sync WHERE id = ?", (pending_id,))
                    conn.commit()
                    messagebox.showinfo("COMPLETE", "Synchronized!")
                else:
                    cursor.execute("DELETE FROM pending_sync WHERE id = ?", (pending_id,))
                    conn.commit()
    except Exception as e: print(f"Gatekeeper error: {e}")

def hitung_live_total_qty_dari_db(linked_text):
    if not linked_text: return 0
    t_clean = str(linked_text[0]).strip() if isinstance(linked_text, (tuple, list)) else str(linked_text).strip()
    if t_clean == "None" or not t_clean: return 0
    total = 0
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            for wp in [s.strip() for s in re.split(r'[,\n]', t_clean) if s.strip()]:
                cursor.execute("SELECT quantity FROM rekod_qr WHERE sequence_no = ?", (wp,))
                row = cursor.fetchone()
                if row and row[0]:
                    digits = "".join(filter(str.isdigit, str(row[0])))
                    if digits: total += int(digits)
    except: pass
    return total

def carian_outer(jadual, entry_search):
    semak_dan_pencetus_popup_gatekeeper(jadual.winfo_toplevel())
    teks = entry_search.get().strip().upper()
    for item in jadual.get_children(): jadual.delete(item)
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            base = "SELECT id, sequence_no, tarikh, quantity, machine, lotcard_no, customer FROM rekod_qr WHERE sequence_no LIKE 'B%'"
            if not teks:
                cursor.execute(base + " ORDER BY id DESC")
            else:
                query_penapis = base + " AND (sequence_no LIKE ? OR customer LIKE ? OR machine LIKE ?) ORDER BY id DESC"
                cursor.execute(query_penapis, (f"%{teks}%", f"%{teks}%", f"%{teks}%"))
                
            for r in cursor.fetchall():
                jadual.insert("", tk.END, values=("☐", r[0], r[2], str(r[6]).upper(), f"{str(r[3]).replace('PCS','').strip()} PCS", str(r[5]), str(r[4]).replace(",","\n"), "OUTER BOX", r[1]), tags=('normal',))
    except Exception as e: messagebox.showerror("ERROR", str(e))

def on_outer_click(event, jadual):
    item_id = jadual.identify_row(event.y)
    if item_id:
        v = list(jadual.item(item_id)['values'])
        t = "☑" if "☐" in str(v[0]) else "☐"
        v[0] = t
        jadual.item(item_id, values=v, tags=('checked' if t == "☑" else 'normal',))

def on_mouse_hover(event, jadual):
    global baris_hover_terakhir
    item_id = jadual.identify_row(event.y)
    if item_id != baris_hover_terakhir:
        if baris_hover_terakhir and jadual.exists(baris_hover_terakhir):
            v = jadual.item(baris_hover_terakhir)['values']
            jadual.item(baris_hover_terakhir, tags=('checked' if "☑" in str(v[0]) else 'normal',))
        if item_id and "☐" in str(jadual.item(item_id)['values'][0]): jadual.item(item_id, tags=('hover',))
        baris_hover_terakhir = item_id

def on_mouse_leave(event, jadual):
    global baris_hover_terakhir
    if baris_hover_terakhir and jadual.exists(baris_hover_terakhir):
        v = jadual.item(baris_hover_terakhir)['values']
        jadual.item(baris_hover_terakhir, tags=('checked' if "☑" in str(v[0]) else 'normal',))
    baris_hover_terakhir = None

def jana_grafik_outer_dari_row(r):
    seq, raw_in = str(r[8]).strip(), str(r[6]).strip()
    qr = qrcode.QRCode(version=1, border=1); qr.add_data(seq); qr.make(fit=True)
    im_qr = qr.make_image().convert("RGB")
    data_g = []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            for s in [x.strip() for x in re.split(r'[,\n]', raw_in) if x.strip()]:
                cursor.execute("SELECT quantity FROM rekod_qr WHERE sequence_no = ?", (s,))
                row = cursor.fetchone()
                data_g.append((s, str(row[0]) if row else "0"))
    except: pass
    return lod.bina_imej_gabungan_akses(im_qr, data_g, seq), seq

def papar_pratonton_outer_terpilih(jadual, win):
    sel = [jadual.item(i)['values'] for i in jadual.get_children() if "☑" in str(jadual.item(i)['values'][0])]
    if not sel: return messagebox.showwarning("WARNING", "TICK (☑) RECORD TO PREVIEW!", parent=win)
    imgs = [jana_grafik_outer_dari_row(r)[0] for r in sel if r]
    if imgs: database_batch_preview.buka_popup_database_pukal_seragam(win, imgs, is_outer=True)

def eksport_outer_excel():
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, quantity, lotcard_no, machine, sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%' ORDER BY id DESC")
            data = cursor.fetchall()
        if not data: return messagebox.showwarning("WARNING", "NO RECORD FOUND!")
        path = filedialog.asksaveasfilename(initialfile="Laporan_Outer_Packing.csv", defaultextension=".csv")
        if path:
            with open(path, mode='w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(["ID", "Date", "Customer", "Quantity", "Box Type", "Linked Inners", "Outer Sequence"])
                w.writerows(data)
            messagebox.showinfo("SUCCESS", "Saved successfully!")
    except Exception as e: messagebox.showerror("ERROR", str(e))

def susun_lajur_treeview(jadual, lajur, menaik): pass

# 🌟 🟢 PENYATUAN STRUKTUR PENGURUS UI TAB DATABASE YANG HILANG 🌟
def bina_tab_outer(f_tb, f_tp, win, gate_pratonton_seragam, fungsi_padam):
    """Membina elemen susunan visual grid jadual tab Outer di dalam notebook panel."""
    # Top Control Panel
    tk.Label(f_tp, text="Search Outer:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)
    e_s = tk.Entry(f_tp, width=22, font=("Segoe UI", 10))
    e_s.pack(side=tk.LEFT, padx=5)
    
    # Ikatan kekunci pintas Enter untuk mulakan carian
    e_s.bind("<Return>", lambda e: carian_outer(jad_out, e_s))
    
    tk.Button(f_tp, text="SEARCH", command=lambda: carian_outer(jad_out, e_s), bg="#007BFF", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="RESET", command=lambda: [e_s.delete(0, tk.END), carian_outer(jad_out, e_s)], bg="#6C757D", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="PREVIEW SELECTED", command=lambda: gate_pratonton_seragam(jad_out, win, is_outer=True), bg="#28A745", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="DELETE SELECTED", command=lambda: fungsi_padam(jad_out, e_s), bg="#DC3545", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="EXPORT CSV", command=eksport_outer_excel, bg="#343A40", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="REFRESH", command=lambda: carian_outer(jad_out, e_s), bg="#17A2B8", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.RIGHT, padx=2)
    tk.Button(f_tp, text="◀ BACK TO MAIN", command=win.destroy, bg="#6C757D", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.RIGHT, padx=2)

    # Grid Jadual Data Treeview
    kolums = ("Select", "ID", "Date", "Customer", "Quantity", "Box Type", "Linked Inners", "Module", "Sequence No")
    jad_out = ttk.Treeview(f_tb, columns=kolums, show="headings", selectmode="extended")
    jad_out.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Penggayaan saiz lebar kolum
    lebar_lajur = {"Select": 45, "ID": 50, "Date": 85, "Customer": 160, "Quantity": 90, "Box Type": 90, "Linked Inners": 150, "Module": 85, "Sequence No": 110}
    for col in kolums:
        jad_out.heading(col, text=col)
        jad_out.column(col, width=lebar_lajur.get(col, 100), anchor="center" if col != "Customer" else "w")
        
    sb = ttk.Scrollbar(f_tb, orient=tk.VERTICAL, command=jad_out.yview)
    jad_out.configure(yscrollcommand=sb.set)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Pautan aksi tetikus (Events binding)
    jad_out.bind("<Button-1>", lambda e: on_outer_click(e, jad_out))
    jad_out.bind("<Motion>", lambda e: on_mouse_hover(e, jad_out))
    jad_out.bind("<Leave>", lambda e: on_mouse_leave(e, jad_out))
    
    # Penggayaan warna tag baris grid
    jad_out.tag_configure('normal', background='white')
    jad_out.tag_configure('checked', background='#E2F0D9')
    jad_out.tag_configure('hover', background='#F2F2F2')
    
    # Jalankan carian data automatik semasa tetingkap pertama kali dibuka
    carian_outer(jad_out, e_s)
