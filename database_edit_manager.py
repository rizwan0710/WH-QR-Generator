import sqlite3
import re
import tkinter as tk
from tkinter import messagebox
import database_outer_editor as doe  
import database_audit_logger as logger  
import database_manager  # Enjin pusat sambungan database NAS

def siapkan_meja_pending():
    """Membersihkan baki data antrean pending_sync lama agar tiada lagi popup hantu terkeluar."""
    try:
        conn = database_manager.get_db_connection()
        with conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS pending_sync (id INTEGER PRIMARY KEY AUTOINCREMENT, outer_seq TEXT, qty_baru TEXT)")
            cursor.execute("DELETE FROM pending_sync")  # Padam terus semua antrean lama!
    except Exception as e:
        print(f"Pending sync clean failure: {e}")

def buka_popup_edit(root, jadual, entry_search, is_tab_type):
    """🌟 ENGINE PENGURUS EDIT BERPUSAT (100% DIRECT TRIPLE UI AUTO-REFRESH) 🌟"""
    siapkan_meja_pending()
    item_id = jadual.selection()
    if not item_id:
        for i in jadual.get_children():
            if "☑" in str(jadual.item(i)['values']): 
                item_id = (i,)
                break
    if not item_id: 
        return messagebox.showwarning("REMINDER", "PLEASE TICK OR CHOOSE DATA!", parent=root)
    
    target_id = item_id
    record_id = str(jadual.set(target_id, "ID")).strip()

    # REDIRECT TAB 2: OUTER GRID EDITOR (Fail Terasing)
    if is_tab_type == 2:
        return doe.buka_popup_edit_outer_terperinci(root, jadual, entry_search, record_id, target_id)

    win_edit = tk.Toplevel(root)
    win_edit.title(f"EDIT PANEL ID: {record_id}")
    win_edit.geometry("380x380")
    win_edit.grab_set()
    
    fr_in = tk.Frame(win_edit)
    fr_in.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
    entries = {}
    
    # ─── TAB 1: INNER PACKING EDIT ───
    if is_tab_type == 1:
        qty_lama = str(jadual.set(target_id, "Quantity")).strip()
        inner_seq = str(jadual.set(target_id, "Sequence No")).strip()
        lajur = [
            ("Customer Name:", str(jadual.set(target_id, "Customer"))),
            ("Drawing No:", str(jadual.set(target_id, "Drawing No"))),
            ("Part Number:", str(jadual.set(target_id, "Part No"))),
            ("Quantity:", qty_lama),
            ("Machine:", str(jadual.set(target_id, "Machine"))),
            ("Lotcard No:", str(jadual.set(target_id, "Lotcard No")))
        ]
        for idx, (lbl, val) in enumerate(lajur):
            tk.Label(fr_in, text=lbl).grid(row=idx, column=0, padx=5, pady=4, sticky="e")
            ent = tk.Entry(fr_in, width=28)
            ent.insert(0, val)
            ent.grid(row=idx, column=1, padx=5, pady=4)
            entries[lbl] = ent
            
        def simpan_edit_inner():
            cus, drw, prt, qty = [entries[k].get().upper().strip() for k in ["Customer Name:", "Drawing No:", "Part Number:", "Quantity:"]]
            mac, lot = [entries[k].get().upper().strip() for k in ["Machine:", "Lotcard No:"]]
            if not all([cus, drw, prt, qty, mac, lot]): 
                return messagebox.showwarning("WARNING", "FILL ALL!", parent=win_edit)
            try:
                qty_bersih = qty.replace('PCS','').strip()
                qty_format = f"{qty_bersih} PCS"
                
                main_app = root.winfo_toplevel()
                if hasattr(main_app, 'stop_auto_sync'):
                    try: main_app.stop_auto_sync()
                    except: pass
                
                # 1. DIRECT AUTO-UPDATE KEPADA KETIGA-TIGA REKOD DATABASE NAS SERENTAK
                # 1. DIRECT AUTO-UPDATE KEPADA KETIGA-TIGA REKOD DATABASE NAS SERENTAK
                conn_nas = database_manager.get_db_connection()
                with conn_nas:
                    cursor = conn_nas.cursor()
                    
                    # ✅ JARAK DIBAIKI: Diselaraskan rapat mengikut blok `with` induk
                    lajur_seq = "sequence_no"
                    try:
                        cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                        lajur_seq = "[Sequence No]"
                    except sqlite3.OperationalError: 
                        pass
                    
                    # [A] Kemaskini Data Utama Inner Packing Tab
                    cursor.execute(
                        f"UPDATE rekod_qr SET customer=?, drawing_no=?, part_no=?, quantity=?, machine=?, lotcard_no=? WHERE id=?", 
                        (cus, drw, prt, qty_format, mac, lot, record_id)
                    )
                    
                    # Ambil semua data outer menggunakan lajur_seq yang dinamik
                    cursor.execute(f"SELECT id, {lajur_seq}, machine FROM rekod_qr WHERE {lajur_seq} LIKE 'B%'")
                    semua_outer = cursor.fetchall()

                    for o_id, o_seq, o_machine in semua_outer:
                        # Bersihkan string siri bagi mengelakkan kegagalan padanan kes huruf/ruang kosong
                        senarai_wp_terhubung = [s.strip().upper() for s in str(o_machine).replace('\n', ',').split(',') if s.strip()]
                        
                        if inner_seq.strip().upper() in senarai_wp_terhubung:
                            total_baru = 0
                            for wp_code in senarai_wp_terhubung:
                                cursor.execute(f"SELECT quantity FROM rekod_qr WHERE UPPER(TRIM({lajur_seq})) = ?", (wp_code,))
                                row_in = cursor.fetchone()
                                if row_in and row_in[0]:
                                    digits = "".join(filter(str.isdigit, str(row_in[0])))
                                    if digits: 
                                        total_baru += int(digits)
                            
                            qty_outer_baru = f"{total_baru} PCS"
                            
                            # [B] Kemaskini Terus Data Kuantiti Outer Box di Database NAS
                            cursor.execute("UPDATE rekod_qr SET quantity = ? WHERE id = ?", (qty_outer_baru, o_id))
                            
                            # [C] Kemaskini Terus Data Kuantiti Invoice Shipped di Database NAS
                            cursor.execute(
                                f"UPDATE rekod_qr SET quantity = ? WHERE machine = ? AND ({lajur_seq} LIKE 'INV%' OR {lajur_seq} LIKE 'IV%')", 
                                (qty_outer_baru, o_seq)
                            )
                    
                    cursor.execute("DELETE FROM pending_sync")
                    conn_nas.commit()                    
                    # Imbas dan cari Outer Box terhubung
                    cursor.execute(f"SELECT id, {lajur_seq}, machine FROM rekod_qr WHERE {lajur_seq} LIKE 'B%'")
                    semua_outer = cursor.fetchall()
                    
                    for o_id, o_seq, o_machine in semua_outer:
                        linked_text = str(o_machine).strip()
                        senarai_wp_terhubung = [s.strip() for s in linked_text.replace('\n', ',').split(',') if s.strip()]
                        
                        if inner_seq in senarai_wp_terhubung:
                            total_baru = 0
                            for wp_code in senarai_wp_terhubung:
                                cursor.execute(f"SELECT quantity FROM rekod_qr WHERE {lajur_seq} = ?", (wp_code,))
                                row_in = cursor.fetchone()
                                if row_in and row_in:
                                    digits = "".join(filter(str.isdigit, str(row_in)))
                                    if digits: total_baru += int(digits)
                            
                            if total_baru <= 0: 
                                total_baru = int(qty_bersih)
                            qty_outer_baru = f"{total_baru} PCS"
                            
                            # [B] Kemaskini Terus Data Kuantiti Outer Box di Database NAS
                            cursor.execute("UPDATE rekod_qr SET quantity = ? WHERE id = ?", (qty_outer_baru, o_id))
                            
                            # [C] Kemaskini Terus Data Kuantiti Invoice Shipped di Database NAS
                            cursor.execute(
                                f"UPDATE rekod_qr SET quantity = ? WHERE machine = ? AND ({lajur_seq} LIKE 'INV%' OR {lajur_seq} LIKE 'IV%')", 
                                (qty_outer_baru, o_seq)
                            )
                    
                    cursor.execute("DELETE FROM pending_sync")
                    conn_nas.commit()
                
                logger.record_edit_activity("INNER", f"[{inner_seq}] Qty: {qty_lama.replace('PCS','').strip()} -> {qty_bersih}")

                # 2. INTEGRASI DATA EXCEL PUSAT RANGKAIAN NAS (Mengekalkan fungsi asal log anda)
                try:
                    import excel_generator as eg
                    if hasattr(eg, 'kemaskini_laporan_excel_pukal'):
                        eg.kemaskini_laporan_excel_pukal()
                except Exception as e_nas:
                    print(f"[NAS Override] Excel auto-write delayed: {e_nas}")

                # 3. PEMECAT SEKATAN WINDOW VISUAL PREVIEW LAMA (Blok penuh tanpa gantung)
                try:
                    toplevel_windows = []
                    def cari_semua_toplevel(parent):
                        for child in parent.winfo_children():
                            if isinstance(child, tk.Toplevel):
                                toplevel_windows.append(child)
                            if child.winfo_children():
                                cari_semua_toplevel(child)
                    cari_semua_toplevel(main_app)
                    
                    for w in toplevel_windows:
                        title_str = str(w.title()).upper()
                        if "PREVIEW" in title_str or "LABEL" in title_str:
                            w.grab_release()
                            w.destroy()
                except Exception as e_clear:
                    print(f"Clear preview window failure: {e_clear}")

                win_edit.destroy()
                messagebox.showinfo("SUCCESS", f"Data updated successfully on NAS!\nInner, Outer Box & Invoice are fully synchronized!")
                # 4. 🔒 FORCE OVERRIDE & LIVE GRID RELOAD UNTUK SEMUA TAB 🔒
                def kunci_nilai_visual_pada_skrin():
                    try:
                        import central_tab_inner_logic as ctil
                        import central_tab_outer_logic as ctol
                        import invoice_tab_logic as citl  
                        
                        ctil.carian_inner(jadual, entry_search)
                        
                        def paksa_override_grid_view_outer(parent):
                            for widget in parent.winfo_children():
                                name = str(widget.__class__.__name__).lower()
                                if "treeview" in name:
                                    try:
                                        cols = widget.cget("columns")
                                        if "Outer Sequence" in str(cols) or "Linked Inners" in str(cols) or "Box Quantity" in str(cols):
                                            ctol.carian_outer(widget, None)
                                            
                                        if "Invoice No" in str(cols) or "SO No" in str(cols) or "Invoice Sequence No" in str(cols):
                                            citl.carian_invoice(widget, None)
                                    except Exception as e_tree:
                                        print(f"Treeview reload skip channel: {e_tree}")
                                elif widget.winfo_children():
                                    paksa_override_grid_view_outer(widget)
                                    
                        paksa_override_grid_view_outer(main_app)
                    except Exception as e_lock:
                        print(f"UI Visual Lock fully integration failure: {e_lock}")

                main_app.after(50, kunci_nilai_visual_pada_skrin)
                        
            except Exception as e: 
                messagebox.showerror("ERROR", str(e), parent=win_edit)

        tk.Button(win_edit, text="💾 SAVE CHANGES", command=simpan_edit_inner, bg="#E65100", fg="white", font=("Segoe UI", 10, "bold"), width=20).pack(pady=15)
        
    # ─── TAB 3: INVOICE LOGS EDIT ───
    elif is_tab_type == 3:
        win_edit.geometry("380x240")
        
        inv_lama = str(jadual.set(target_id, "Invoice No")).upper().replace("INV:", "").strip()
        so_lama  = str(jadual.set(target_id, "SO No")).upper().replace("SO:", "").strip()
        inv_seq  = str(jadual.set(target_id, "Invoice Sequence No")).strip()
        
        tk.Label(fr_in, text="Invoice Number:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=5, pady=10, sticky="e")
        ent_inv = tk.Entry(fr_in, width=28, font=("Segoe UI", 10))
        ent_inv.insert(0, inv_lama)
        ent_inv.grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(fr_in, text="SO Number:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, padx=5, pady=10, sticky="e")
        ent_so = tk.Entry(fr_in, width=28, font=("Segoe UI", 10))
        ent_so.insert(0, so_lama)
        ent_so.grid(row=1, column=1, padx=5, pady=10)
        
        def simpan_edit_invoice():
            val_inv = ent_inv.get().upper().strip()
            val_so  = ent_so.get().upper().strip()
            
            if not val_inv or not val_so: 
                return messagebox.showwarning("WARNING", "INVOICE AND SO NUMBER FIELDS ARE REQUIRED!", parent=win_edit)
                
            try:
                huraian_log = f"[{inv_seq}] Edited Invoice No: {inv_lama} -> {val_inv} | SO No: {so_lama} -> {val_so}"
                
                conn_inv_nas = database_manager.get_db_connection()
                with conn_inv_nas:
                    cursor = conn_inv_nas.cursor()
                    cursor.execute("UPDATE rekod_qr SET drawing_no = ?, part_no = ? WHERE id = ?", (f"INV:{val_inv}", f"SO:{val_so}", record_id))
                
                logger.record_edit_activity("INVOICE", huraian_log)
                messagebox.showinfo("SUCCESS", "Invoice and SO Numbers updated successfully on NAS!", parent=win_edit)
                win_edit.destroy()
                
                import invoice_tab_logic as ctil
                root.after(150, lambda: ctil.carian_invoice(jadual, entry_search))
            except Exception as e: 
                messagebox.showerror("ERROR", str(e), parent=win_edit)
                
        tk.Button(win_edit, text="💾 SAVE CHANGES", command=simpan_edit_invoice, bg="#E65100", fg="white", font=("Segoe UI", 10, "bold"), width=20).pack(pady=15)
