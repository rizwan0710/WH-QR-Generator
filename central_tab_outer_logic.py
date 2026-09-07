import sqlite3, csv, qrcode, re, tkinter as tk
from tkinter import messagebox, filedialog

baris_hover_terakhir = None

def semak_dan_pencetus_popup_gatekeeper(parent_win):
    """🌟 STANDARDIZED GATEKEEPER ENGINE: Pop-up request approval for Invoice sync 🌟"""
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, outer_seq, qty_baru FROM pending_sync LIMIT 1")
            row = cursor.fetchone()
            if row:
                pending_id = row[0]
                outer_code = str(row[1]).strip()
                qty_baru_str = str(row[2]).strip()
                
                approve_sync = messagebox.askyesno(
                    "⚠️ PENDING DATA SYNC DETECTED",
                    f"The system has detected a fresh production update from INNER BOX quantities!\n\n"
                    f"Target Outer Box Code: [{outer_code}]\n"
                    f"New Auto-Calculated Quantity: {qty_baru_str}\n\n"
                    f"Do you want to [ACCEPT] and cascade this fresh quantity change directly to the INVOICE LOGS?",
                    parent=parent_win
                )
                if approve_sync:
                    cursor.execute("UPDATE rekod_qr SET quantity = ? WHERE sequence_no LIKE 'INV%' AND machine = ?", (qty_baru_str, outer_code))
                    cursor.execute("DELETE FROM pending_sync WHERE id = ?", (pending_id,))
                    conn.commit()
                    import database_audit_logger as db_logger
                    db_logger.record_edit_activity("GATEKEEPER", f"[{outer_code}] Qty Synced to {qty_baru_str.replace('PCS','').strip()}")
                    messagebox.showinfo("SYNC COMPLETE", "Invoice logs and stickers successfully synchronized!", parent=parent_win)
                else:
                    cursor.execute("DELETE FROM pending_sync WHERE id = ?", (pending_id,))
                    conn.commit()
                    import database_audit_logger as db_logger
                    db_logger.record_edit_activity("GATEKEEPER", f"[{outer_code}] Sync bypassed (Kept static)")
                    messagebox.showwarning("SYNC DECLINED", "Invoice logs synchronization was bypassed and kept static.", parent=parent_win)
    except Exception as e: 
        print(f"Gatekeeper error: {e}")

def hitung_live_total_qty_dari_db(linked_inners_text):
    """🌟 FIX MUTTAK REAL-TIME DATA FETCH: Memaksa bacaan string lajur murni [0] kalis cache 🌟"""
    if not linked_inners_text: 
        return 0
        
    # Unpack tuple jika dihantar murni dari cursor.fetchone()
    if isinstance(linked_inners_text, (tuple, list)):
        text_clean = str(linked_inners_text[0]).strip()
    else:
        text_clean = str(linked_inners_text).strip()
        
    if text_clean == "None" or not text_clean: 
        return 0
        
    # Pecahkan mengikut koma atau pemisah baris menegak \n
    senarai_wp = [s.strip() for s in re.split(r'[,\n]', text_clean) if s.strip()]
    total_calculated = 0
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            for wp_code in senarai_wp:
                if wp_code:
                    cursor.execute("SELECT quantity FROM rekod_qr WHERE sequence_no = ?", (wp_code,))
                    row = cursor.fetchone()
                    
                    # 🌟 KOREKSI TOTAL KESELURUHAN: Ambil indeks [0] secara nyata daripada tuple fetchone 🌟
                    if row and row[0]:
                        raw_qty_val = str(row[0]).upper().replace("PCS", "").strip()
                        # Sedut hanya nombor bulat tulen dari string kuantiti murni
                        digits = "".join(filter(str.isdigit, raw_qty_val))
                        if digits: 
                            total_calculated += int(digits)
    except Exception as e: 
        print(f"Live calculation loop error: {e}")
    return total_calculated

def carian_outer(jadual, entry_search):
    semak_dan_pencetus_popup_gatekeeper(jadual.winfo_toplevel())
    teks_carian = entry_search.get().strip().upper()
    for item in jadual.get_children(): jadual.delete(item)
    kata_kunci_senarai = [k.strip() for k in teks_carian.split() if k.strip()]
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            base_query = "SELECT id, sequence_no, tarikh, quantity, machine, lotcard_no, customer FROM rekod_qr WHERE sequence_no LIKE 'B%'"
            if not kata_kunci_senarai:
                cursor.execute(base_query + " ORDER BY id DESC")
                semua_rekod = cursor.fetchall()
            else:
                sub_queries = []
                parameter_sql = []
                for k in kata_kunci_senarai:
                    sub_queries.append("(sequence_no LIKE ? OR tarikh LIKE ? OR quantity LIKE ? OR machine LIKE ? OR lotcard_no LIKE ? OR customer LIKE ?)")
                    pola = f"%{k}%"; parameter_sql.extend([pola] * 6)
                cursor.execute(f"{base_query} AND ({ ' OR '.join(sub_queries) }) ORDER BY id DESC", parameter_sql)
                semua_rekod = cursor.fetchall()
                
            for r in semua_rekod:
                raw_machine = str(r[4]).strip()
                papar_inner_menegak = raw_machine.replace(",", "\n")
                cust_clean = str(r[6]).upper().strip() if r[6] else "INTERNAL/COMBINED"
                mfg_clean  = str(r[5]).upper().strip() if r[5] else "OUTER LOG"
                qty_clean  = f"{str(r[3]).upper().replace('PCS', '').strip()} PCS"
                jadual.insert("", tk.END, values=("☐", r[0], r[2], cust_clean, qty_clean, mfg_clean, papar_inner_menegak, "OUTER BOX", r[1]), tags=('normal',))
    except sqlite3.Error as e: 
        messagebox.showerror("DATA ERROR", f"FAILED TO PREVIEW OUTER INFORMATION:\n{str(e)}")

def on_outer_click(event, jadual):
    item_id = jadual.identify_row(event.y)
    if item_id:
        semua_nilai = list(jadual.item(item_id)['values'])
        if semua_nilai:
            tanda_baru = "☑" if "☐" in str(semua_nilai[0]) else "☐"
            semua_nilai[0] = tanda_baru
            jadual.item(item_id, values=semua_nilai, tags=('checked' if tanda_baru == "☑" else 'normal',))

def on_mouse_hover(event, jadual):
    global baris_hover_terakhir
    item_id = jadual.identify_row(event.y)
    if item_id != baris_hover_terakhir:
        if baris_hover_terakhir and jadual.exists(baris_hover_terakhir):
            nilai_lama = jadual.item(baris_hover_terakhir)['values']
            jadual.item(baris_hover_terakhir, tags=('checked' if "☑" in str(nilai_lama[0]) else 'normal',))
        if item_id and "☐" in str(jadual.item(item_id)['values'][0]): jadual.item(item_id, tags=('hover',))
        baris_hover_terakhir = item_id

def on_mouse_leave(event, jadual):
    global baris_hover_terakhir
    if baris_hover_terakhir and jadual.exists(baris_hover_terakhir):
        nilai_lama = jadual.item(baris_hover_terakhir)['values']
        jadual.item(baris_hover_terakhir, tags=('checked' if "☑" in str(nilai_lama[0]) else 'normal',))
    baris_hover_terakhir = None

def jana_grafik_outer_dari_row(r):
    seq_outer, raw_inner_text = str(r[8]).strip(), str(r[6]).strip()
    qr = qrcode.QRCode(version=1, box_size=10, border=1); qr.add_data(seq_outer); qr.make(fit=True)
    img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    senarai_inner_res = [s.strip() for s in re.split(r'[,\n]', raw_inner_text) if s.strip() and s.strip() != "None"]
    data_gabungan_final = []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            for s_clean in senarai_inner_res:
                if s_clean:
                    cursor.execute("SELECT quantity FROM rekod_qr WHERE sequence_no = ?", (s_clean,))
                    row_qty = cursor.fetchone()
                    data_gabungan_final.append((s_clean, str(row_qty[0]) if row_qty else "0"))
    except: pass
    import label_outer_designer as lod
    return lod.bina_imej_gabungan_akses(img_qr_mentah, data_gabungan_final, seq_outer), seq_outer

def eksport_outer_excel():
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, sequence_no, tarikh, quantity, machine, customer FROM rekod_qr WHERE sequence_no LIKE 'B%' ORDER BY id DESC")
            semua_data = cursor.fetchall()
        if not semua_data: return messagebox.showwarning("WARNING", "NO OUTER BOX DATA TO BE EXPORT!")
        path_excel = filedialog.asksaveasfilename(initialfile="Laporan_Form2_Outer_Packing.csv", defaultextension=".csv")
        if path_excel:
            with open(path_excel, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Outer Sequence No", "Date", "Customer", "Total Quantity (Pcs)", "Linked Inner Box Sequences"])
                for r in semua_data: writer.writerow([r[0], r[1], r[2], r[5], r[3], str(r[4]).replace(",", " ; ").strip()])
            messagebox.showinfo("SUCCESS", "Outer Packing Report successfully saved!")
    except Exception as e: messagebox.showerror("System Error", str(e))

def susun_lajur_treeview(jadual, lajur, menaik): pass
