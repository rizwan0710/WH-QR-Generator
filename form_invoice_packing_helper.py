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
    """[KEPERLUAN 1 & 3] Enjin pengesan customer, alarm percampuran data, dan fungsi auto-jump kursor."""
    val_semasa = entries_outer[idx].get().strip().upper()
    entries_outer[idx].delete(0, tk.END)
    entries_outer[idx].insert(0, val_semasa)
    
    if not val_semasa.startswith("B"):
        messagebox.showwarning("ERROR FORMAT", "PLEASE SCAN LEGIMATE OUTER BOX QR!", parent=entries_outer[idx].winfo_toplevel())
        return "break"

    # Jalankan pemeriksaan silang pangkalan data (Cross-reference lookup database)
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
        # 🚨 WARNING ALARM: MENYEKAT PERCAMPURAN CUSTOMER LAIN PADA INVOICE SAMA
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

def bina_kotak_imbasan_dinamik(content_frame, total_box, entries_list, var_customer, label_counter):
    """[KEPERLUAN 2] Penjana senarai kolum baris input berasaskan Canvas Scroll (Had Maksimum 50)"""
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
        # [KEPERLUAN 2] Sekatan tegas maksima 50 kotak input untuk kestabilan memori
        messagebox.showwarning("MAXIMUM CAPACITY", "THE SYSTEM SET LIMITS TO ONLY 50 BOXES PER INVOICE")
        total_val = 50
        entry_total_box.delete(0, tk.END)
        entry_total_box.insert(0, "50")
        
    bina_kotak_imbasan_dinamik(content_frame, total_val, entries_list, var_customer, label_counter)
