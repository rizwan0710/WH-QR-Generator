import sqlite3
import re
import tkinter as tk
from tkinter import messagebox
import database_audit_logger as logger  # 🌟 IMPORT ENJIN EDIT LOGS TUNGGAL 🌟

def buka_popup_edit_outer_terperinci(root, jadual, entry_search, record_id, target_item_id):
    """🏢 ENJIN GRID TERPERINCI OUTER BOX (WITH TOTAL LIVE LOG CAPTURE FIX) 🏢"""
    win_edit = tk.Toplevel(root)
    win_edit.title(f"DETAILED PART EDITOR (ID: {record_id})")
    win_edit.geometry("450x420")
    win_edit.configure(bg="#F8F9FA")
    win_edit.grab_set()

    tk.Label(win_edit, text="OUTER BOX DETAILED PART EDITOR", font=("Segoe UI", 11, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=10)
    
    frame_container = tk.Frame(win_edit, bg="#F8F9FA")
    frame_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
    
    linked_inners_raw = str(jadual.set(target_item_id, "Linked Inner Sequences")).strip()
    outer_sequence_code = str(jadual.set(target_item_id, "Outer Sequence No")).strip()
    qty_outer_lama = str(jadual.set(target_item_id, "Quantity")).upper().replace("PCS", "").strip()
    
    senarai_wp_codes = [s.strip() for s in re.split(r'[,\n]', linked_inners_raw) if s.strip() and s.strip() != "None"]
    
    data_pecahan_parts = []
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            for wp_code in senarai_wp_codes:
                cursor.execute("SELECT part_no, quantity, id FROM rekod_qr WHERE sequence_no = ?", (wp_code,))
                row_part = cursor.fetchone()
                if row_part:
                    data_pecahan_parts.append({
                        "wp_code": wp_code, 
                        "part_no": str(row_part[0]).strip(), 
                        "qty": str(row_part[1]).upper().replace("PCS","").strip(), 
                        "inner_id": row_part[2]
                    })
    except Exception as e:
        print(f"Ralat bacaan pecahan parts: {str(e)}")

    if not data_pecahan_parts:
        messagebox.showwarning("Peringatan", "Tiada data pecahan siri Inner (WP%) ditemui dalam pangkalan data untuk rekod ini!", parent=win_edit)
        win_edit.destroy()
        return

    frame_header = tk.Frame(frame_container, bg="#E2E8F0", height=26); frame_header.pack(fill=tk.X, pady=2)
    tk.Label(frame_header, text="No. Siri Inner", font=("Segoe UI", 9, "bold"), bg="#E2E8F0", width=14, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(frame_header, text="Part Number", font=("Segoe UI", 9, "bold"), bg="#E2E8F0", width=16, anchor="w").pack(side=tk.LEFT, padx=5)
    tk.Label(frame_header, text="Quantity (Pcs)", font=("Segoe UI", 9, "bold"), bg="#E2E8F0", width=12, anchor="w").pack(side=tk.LEFT, padx=5)

    list_input_widgets = []
    for item in data_pecahan_parts:
        frame_row = tk.Frame(frame_container, bg="white", bd=1, relief="groove"); frame_row.pack(fill=tk.X, pady=2)
        tk.Label(frame_row, text=item["wp_code"], font=("Segoe UI", 9), bg="white", width=14, anchor="w").pack(side=tk.LEFT, padx=5)
        tk.Label(frame_row, text=item["part_no"], font=("Segoe UI", 9, "bold"), fg="#334155", bg="white", width=16, anchor="w").pack(side=tk.LEFT, padx=5)
        
        ent_part_qty = tk.Entry(frame_row, width=10, font=("Segoe UI", 10), relief="flat", highlightthickness=1, highlightbackground="#CBD5E1")
        ent_part_qty.insert(0, item["qty"])
        ent_part_qty.pack(side=tk.LEFT, padx=5, ipady=2)
        list_input_widgets.append({"ent_widget": ent_part_qty, "inner_id": item["inner_id"], "wp_code": item["wp_code"]})

    def laksanakan_simpan_detailed_outer():
        total_sum_baru = 0
        senarai_update_data = []
        
        for obj in list_input_widgets:
            val_text = obj["ent_widget"].get().strip()
            if not val_text.isdigit():
                return messagebox.showerror("VALIDATION ERROR", "QUANTITY MUST BE DIGIT NUMBER ONLY!", parent=win_edit)
            qty_integer = int(val_text)
            total_sum_baru += qty_integer
            senarai_update_data.append((f"{qty_integer} PCS", obj["inner_id"]))

        try:
            qty_format_final = f"{total_sum_baru} PCS"
            with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
                cursor = conn.cursor()
                for qty_str, inner_id in senarai_update_data:
                    cursor.execute("UPDATE rekod_qr SET quantity = ? WHERE id = ?", (qty_str, inner_id))
                cursor.execute("UPDATE rekod_qr SET quantity = ? WHERE id = ?", (qty_format_final, record_id))
                conn.commit()
            
            # 🌟 SUNTIKAN UTAMA LOG TAB OUTER: Kunci format ringkas mengikut spesifikasi kegemaran anda 🌟
            huraian_log_outer = f"[{outer_sequence_code}] Qty: {qty_outer_lama} -> {total_sum_baru}"
            logger.record_edit_activity("OUTER", huraian_log_outer)
            
            messagebox.showinfo("SUCCESS", f"All parts updated! New auto-calculated total: {qty_format_final}", parent=win_edit)
            win_edit.destroy()
            
            if entry_search and hasattr(entry_search, 'delete'): 
                entry_search.delete(0, tk.END)
                
            import central_tab_outer_logic as ctol
            root.after(150, lambda: ctol.carian_outer(jadual, entry_search))
            
        except Exception as e:
            messagebox.showerror("ERROR", f"FAILED TO SAVE DETAILS:\n{str(e)}", parent=win_edit)

    tk.Button(win_edit, text="💾 SAVE CHANGES & AUTO-SUM", command=laksanakan_simpan_detailed_outer, bg="#007ACC", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").pack(pady=15, fill=tk.X, padx=30)
