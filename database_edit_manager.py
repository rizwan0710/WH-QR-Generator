import sqlite3
import tkinter as tk
from tkinter import messagebox
import database_outer_editor as doe  
import database_audit_logger as logger  

def siapkan_meja_pending():
    """Build the pending synchronization table structure if it does not exist."""
    with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
        conn.cursor().execute("CREATE TABLE IF NOT EXISTS pending_sync (id INTEGER PRIMARY KEY AUTOINCREMENT, outer_seq TEXT, qty_baru TEXT)")
        conn.commit()

def buka_popup_edit(root, jadual, entry_search, is_tab_type):
    """🌟 ENGINE PENGURUS EDIT BERPUSAT (STANDARDIZED INVOICE NO & SO NO ONLY) 🌟"""
    siapkan_meja_pending()
    item_id = jadual.selection()
    if not item_id:
        for i in jadual.get_children():
            if "☑" in str(jadual.item(i)['values']): item_id = (i,); break
    if not item_id: return messagebox.showwarning("REMINDER", "PLEASE TICK OR CHOOSE DATA!", parent=root)
    
    target_id = item_id
    record_id = str(jadual.set(target_id, "ID")).strip()

    # REDIRECT TAB 2: OUTER GRID EDITOR (Fail Terasing - Logs Fixed)
    if is_tab_type == 2:
        return doe.buka_popup_edit_outer_terperinci(root, jadual, entry_search, record_id, target_id)

    win_edit = tk.Toplevel(root); win_edit.title(f"EDIT PANEL ID: {record_id}"); win_edit.geometry("380x380"); win_edit.grab_set()
    fr_in = tk.Frame(win_edit); fr_in.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
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
            ent = tk.Entry(fr_in, width=28); ent.insert(0, val); ent.grid(row=idx, column=1, padx=5, pady=4)
            entries[lbl] = ent
            
        def simpan_edit_inner():
            cus, drw, prt, qty = [entries[k].get().upper().strip() for k in ["Customer Name:", "Drawing No:", "Part Number:", "Quantity:"]]
            mac, lot = [entries[k].get().upper().strip() for k in ["Machine:", "Lotcard No:"]]
            if not all([cus, drw, prt, qty, mac, lot]): return messagebox.showwarning("WARNING", "FILL ALL!", parent=win_edit)
            try:
                qty_format = f"{qty.replace('PCS','').strip()} PCS"
                with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE rekod_qr SET customer=?, drawing_no=?, part_no=?, quantity=?, machine=?, lotcard_no=? WHERE id=?", (cus, drw, prt, qty_format, mac, lot, record_id))
                    conn.commit() 
                    
                    cursor.execute("SELECT sequence_no, machine FROM rekod_qr WHERE sequence_no LIKE 'B%' AND machine LIKE ?", (f"%{inner_seq}%",))
                    outer_rows = cursor.fetchall()
                    for o_seq, o_machine in outer_rows:
                        import central_tab_outer_logic as ctol_calc
                        total_baru = ctol_calc.hitung_live_total_qty_dari_db(o_machine)
                        if total_baru > 0:
                            qty_outer_baru = f"{total_baru} PCS"
                            cursor.execute("UPDATE rekod_qr SET quantity = ? WHERE sequence_no = ?", (qty_outer_baru, o_seq))
                            cursor.execute("INSERT INTO pending_sync (outer_seq, qty_baru) VALUES (?, ?)", (o_seq, qty_outer_baru))
                    conn.commit()
                
                logger.record_edit_activity("INNER", f"[{inner_seq}] Qty: {qty_lama.replace('PCS','').strip()} -> {qty.replace('PCS','').strip()}")
                messagebox.showinfo("SUCCESS", "Saved! Notification queued for Outer Tab.", parent=win_edit); win_edit.destroy()
                __import__("central_tab_inner_logic").carian_inner(jadual, entry_search)
            except Exception as e: messagebox.showerror("ERROR", str(e), parent=win_edit)
        tk.Button(win_edit, text="💾 SAVE CHANGES", command=simpan_edit_inner, bg="#E65100", fg="white", font=("Segoe UI", 10, "bold"), width=20).pack(pady=15)

    # ─── 🚀 TAB 3: INVOICE LOGS EDIT (FIXED: INVOICE NO & SO NO ONLY) 🚀 ───
    elif is_tab_type == 3:
        win_edit.geometry("380x240")
        
        # Ekstrak data sedia ada dari baris Treeview
        inv_lama = str(jadual.set(target_id, "Invoice No")).upper().replace("INV:", "").strip()
        so_lama  = str(jadual.set(target_id, "SO No")).upper().replace("SO:", "").strip()
        inv_seq  = str(jadual.set(target_id, "Invoice Sequence No")).strip()
        
        # Rekabentuk visual borang yang seragam (Standardized English Layout)
        tk.Label(fr_in, text="Invoice Number:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=5, pady=10, sticky="e")
        ent_inv = tk.Entry(fr_in, width=28, font=("Segoe UI", 10)); ent_inv.insert(0, inv_lama); ent_inv.grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(fr_in, text="SO Number:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, padx=5, pady=10, sticky="e")
        ent_so = tk.Entry(fr_in, width=28, font=("Segoe UI", 10)); ent_so.insert(0, so_lama); ent_so.grid(row=1, column=1, padx=5, pady=10)
        
        def simpan_edit_invoice():
            val_inv = ent_inv.get().upper().strip()
            val_so  = ent_so.get().upper().strip()
            
            if not val_inv or not val_so: 
                return messagebox.showwarning("WARNING", "INVOICE AND SO NUMBER FIELDS ARE REQUIRED!", parent=win_edit)
                
            try:
                # Format penulisan logs yang direct dan padat mengikut kehendak anda
                huraian_log = f"[{inv_seq}] Edited Invoice No: {inv_lama} -> {val_inv} | SO No: {so_lama} -> {val_so}"
                
                with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
                    cursor = conn.cursor()
                    # Hanya kemaskini lajur drawing_no (Invoice No) dan part_no (SO No) sahaja. Lajur kuantiti tidak diusik!
                    cursor.execute("UPDATE rekod_qr SET drawing_no = ?, part_no = ? WHERE id = ?", (f"INV:{val_inv}", f"SO:{val_so}", record_id))
                    conn.commit()
                
                logger.record_edit_activity("INVOICE", huraian_log)
                messagebox.showinfo("SUCCESS", "Invoice and SO Numbers updated successfully!", parent=win_edit)
                win_edit.destroy()
                
                import invoice_tab_logic as ctil
                root.after(150, lambda: ctil.carian_invoice(jadual, entry_search))
            except Exception as e: 
                messagebox.showerror("ERROR", str(e), parent=win_edit)
                
        tk.Button(win_edit, text="💾 SAVE CHANGES", command=simpan_edit_invoice, bg="#E65100", fg="white", font=("Segoe UI", 10, "bold"), width=20).pack(pady=15)
