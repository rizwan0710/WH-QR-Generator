# form_invoice_packing_helper.py - PART 1: 3 RULES HARD LOCK ENGINE
import tkinter as tk
from tkinter import messagebox
import sqlite3

def cuci_isi_borang_invoice(entry_inv_no, entry_so_no, var_customer, entry_total_box, frame_scroll_content, entries_outer, label_counter):
    entry_inv_no.delete(0, tk.END)
    entry_so_no.delete(0, tk.END)
    entry_total_box.delete(0, tk.END)
    entry_total_box.insert(0, "4") 
    var_customer.set("- AUTO DETECT -")
    bina_kotak_imbasan_dinamik(frame_scroll_content, 4, entries_outer, var_customer, label_counter)
    entry_inv_no.focus_set()

def semak_dan_lompat_auto(event, idx, entries_outer, total_maksimum, var_customer, label_counter):
    """[3 RULES STRICT SECURITY] Enjin pengesan customer, alarm duplikasi, dan fungsi auto-jump."""
    val_semasa = entries_outer[idx].get().strip().upper()
    entries_outer[idx].delete(0, tk.END)
    entries_outer[idx].insert(0, val_semasa)
    
    if not val_semasa:
        return

    # 🚨 RULE 1: IF BUKAN OUTERBOX SEQUENCE NUMBER -> ERROR
    if not val_semasa.startswith("B") or len(val_semasa) < 5:
        messagebox.showerror("🚨 INVALID FORMAT", "RULE 1 REJECTED!\n\nPLEASE SCAN A LEGITIMATE OUTER BOX QR (STARTS WITH 'B')!", parent=entries_outer[idx].winfo_toplevel())
        entries_outer[idx].delete(0, tk.END)
        return "break"

    # 🚨 RULE 2: IF OUTERBOX SAMA (DUPLICATE DALAM FORMBORANG AKTIF) -> ERROR
    for i, entry in enumerate(entries_outer):
        if i != idx and entry.get().strip().upper() == val_semasa:
            messagebox.showerror(
                "🚨 SAME BOX SCAN DETECTED",
                f"RULE 2 REJECTED!\n\n"
                f"You have already scanned this box [{val_semasa}] at Slot {i+1}!\n"
                f"Every box entry in this form must be unique.",
                parent=entries_outer[idx].winfo_toplevel()
            )
            entries_outer[idx].delete(0, tk.END)
            return "break"

    # 🚨 RULE 3: IF OUTERBOX DAH PERNAH SCAN / WUJUD DALAM DB INVOICE -> ERROR
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            # Semak jika kod box 'B...' ini sudah dipetakan pada siri Invoice 'INV%' di lajur machine
            cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine = ?", (val_semasa,))
            if cursor.fetchone():
                messagebox.showerror(
                    "🚨 BOX ALREADY USED",
                    f"RULE 3 REJECTED!\n\n"
                    f"Outer Box [{val_semasa}] has ALREADY been scanned and linked to another invoice previously!\n"
                    f"You cannot reuse or re-ship an old box.",
                    parent=entries_outer[idx].winfo_toplevel()
                )
                entries_outer[idx].delete(0, tk.END)
                return "break"
    except Exception as e_db:
        print(f"Database security check error: {str(e_db)}")

    # Logik Pengesan Customer & Cross-reference database (Asal)
    cust_terkesan = "INTERNAL/COMBINED"
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT machine FROM rekod_qr WHERE sequence_no = ?", (val_semasa,))
            res = cursor.fetchone()
            if res and res[0]:
                raw_text = str(res[0]).strip().replace("[","").replace("]","").replace("'","").replace('"','')
                linked_inners = [s.strip() for s in raw_text.split(",") if s.strip()]
                if linked_inners:
                    cursor.execute("SELECT customer FROM rekod_qr WHERE sequence_no = ?", (linked_inners[0],))
                    res_cust = cursor.fetchone()
                    if res_cust and res_cust[0]:
                        cust_terkesan = str(res_cust[0]).strip().upper()
    except Exception:
        cust_terkesan = "INTERNAL/COMBINED"

    customer_semasa_main = var_customer.get()

    if customer_semasa_main == "- AUTO DETECT -" or customer_semasa_main == "":
        var_customer.set(cust_terkesan)
    elif cust_terkesan != customer_semasa_main:
        messagebox.showerror(
            "🚨 ALARM: DIFFERENT CUSTOMER!",
            f"CRITICAL ERROR! OUTER BOX AT THIS SLOT {idx+1} IS FOR:\n👉 [{cust_terkesan}]\n\n"
            f"NOT MATCH WITH THIS CUSTOMER INVOICE REFERENCES:\n👉 [{customer_semasa_main}].\n\n"
            "SYSTEM BLOCKED!",
            parent=entries_outer[idx].winfo_toplevel()
        )
        entries_outer[idx].delete(0, tk.END)
        return "break"

    # Kemaskini label counter statistik imbasan masa nyata
    kira_diisi = sum(1 for e in entries_outer if e.get().strip())
    label_counter.config(text=f"Scanned: {kira_diisi} / {total_maksimum} Boxes")

    # 🚀 AUTOMATIC FOCUS JUMP (Tembak kursor ke kotak bawah tanpa mouse)
    if idx + 1 < total_maksimum:
        entries_outer[idx + 1].focus_set()
        # form_invoice_packing_helper.py - PART 2: DYNAMIC LAYOUT GENERATOR
def bina_kotak_imbasan_dinamik(content_frame, total_box, entries_list, var_customer, label_counter):
    """Penjana senarai kolum baris input berasaskan Canvas Scroll (Had Maksimum 50)"""
    for child in content_frame.winfo_children():
        child.destroy()
        
    entries_list.clear()
    lbl_style = {"font": ("Segoe UI", 9, "bold"), "fg": "#334155", "bg": "white", "width": 20, "anchor": "w"}
    ent_style = {"font": ("Segoe UI", 10), "relief": "groove", "bd": 1, "bg": "#FAFAFA"}
    
    for idx in range(total_box):
        frame_row = tk.Frame(content_frame, bg="white")
        frame_row.pack(fill=tk.X, pady=4)
        
        tk.Label(frame_row, text=f"Outer Box Sequence {idx+1} :", **lbl_style).pack(side=tk.LEFT, padx=(5,2))
        ent = tk.Entry(frame_row, **ent_style)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=5)
        
        entries_list.append(ent)
        ent.bind("<Return>", lambda e, i=idx: semak_dan_lompat_auto(e, i, entries_list, total_box, var_customer, label_counter))

    label_counter.config(text=f"Scanned: 0 / {total_box} Boxes")
    if entries_list:
        entries_list[0].focus_set()

def laksanakan_penjanaan_kotak_pukal(entry_total_box, content_frame, entries_list, var_customer, label_counter):
    val_str = entry_total_box.get().strip()
    if not val_str.isdigit():
        messagebox.showwarning("ERROR", "PLEASE INSERT INTEGER NUMBER ONLY!")
        return
        
    total_val = int(val_str)
    if total_val < 1:
        total_val = 1
    elif total_val > 50:
        messagebox.showwarning("MAXIMUM CAPACITY", "THE SYSTEM SET LIMITS TO ONLY 50 BOXES PER INVOICE")
        total_val = 50
        entry_total_box.delete(0, tk.END)
        entry_total_box.insert(0, "50")
        
    bina_kotak_imbasan_dinamik(content_frame, total_val, entries_list, var_customer, label_counter)

