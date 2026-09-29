# innerbox_form_ui.py - PART 1: IMPORTS & DUAL EXCEL ENGINE (APPEND MODE)
import tkinter as tk
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
import form_warehouse as backend
import custom_dropdown as cd  
import sqlite3
import os

try:
    import openpyxl
except ImportError:
    pass

def alih_fokus(event, input_seterusnya):
    input_seterusnya.focus_set()
    return "break"  

def laksanakan_import_excel_langsung(win_induk):
    path_fail = filedialog.askopenfilename(
        title="Select Customer Master List Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")],
        parent=win_induk
    )
    if not path_fail:
        return
        
    conn = sqlite3.connect("warehouse_data.db")
    cursor = conn.cursor()
    
    # 🌟 KOREKSI SCHEMA UTAMA: Menambah lajur customer_code ke dalam jadual master 🌟
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_code TEXT,
            customer_name TEXT,
            drawing_no TEXT,
            part_number TEXT
        )
    """)
    
    try:
        cursor.execute("SELECT customer_code FROM master_produk LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE master_produk ADD COLUMN customer_code TEXT")
    
    # 🔔 TANYA PENGGUNA SAMA ADA MAHU PADAM DATA LAMA ATAU TIDAK
    pilihan = messagebox.askyesnocancel(
        "IMPORT OPTION", 
        "Do you want to DELETE ALL existing records and perform a fresh import?\n\n"
        "👉 Click [YES] to Delete All & Overwrite.\n"
        "👉 Click [NO] to Keep Existing Data (Append/Update Mode).\n"
        "👉 Click [CANCEL] to Abort.",
        parent=win_induk
    )
    
    if pilihan is None:  # Pengguna tekan Cancel
        conn.close()
        return
        
    if pilihan is True:  # Pengguna tekan Yes (Padam semua data lama)
        cursor.execute("DELETE FROM master_produk")
        conn.commit()
    
    insert_query = "INSERT INTO master_produk (customer_code, customer_name, drawing_no, part_number) VALUES (?, ?, ?, ?)"
    update_query = "UPDATE master_produk SET customer_code = ? WHERE customer_name = ? AND drawing_no = ? AND part_number = ?"
    
    try:
        wb = openpyxl.load_workbook(path_fail, data_only=True)
        sheet = wb.active
        kira_baru = 0
        kira_kemaskini = 0
        
        for row in sheet.iter_rows(min_row=2, max_col=4, values_only=True):
            if row and len(row) >= 4:
                code_val = str(row[0]).strip().upper() if row[0] is not None else ""
                cust_val = str(row[1]).strip().upper() if row[1] is not None else ""
                draw_val = str(row[2]).strip().upper() if row[2] is not None else ""
                part_val = str(row[3]).strip().upper() if row[3] is not None else ""
                
                if cust_val and cust_val != "NONE" and cust_val != "":
                    # Jika pengguna pilih 'Yes' (data dah kosong), terus insert tanpa check duplicate untuk lajukan proses
                    if pilihan is True:
                        cursor.execute(insert_query, (code_val, cust_val, draw_val, part_val))
                        kira_baru += 1
                    else:
                        # Jika pilih 'No', jalankan logik asal (semak duplicate)
                        cursor.execute("""
                            SELECT id, customer_code FROM master_produk 
                            WHERE customer_name = ? AND drawing_no = ? AND part_number = ?
                        """, (cust_val, draw_val, part_val))
                        
                        rekod_wujud = cursor.fetchone()
                        
                        if rekod_wujud:
                            id_asal, kod_asal = rekod_wujud
                            if str(kod_asal).strip().upper() != code_val:
                                cursor.execute(update_query, (code_val, cust_val, draw_val, part_val))
                                kira_kemaskini += 1
                        else:
                            cursor.execute(insert_query, (code_val, cust_val, draw_val, part_val))
                            kira_baru += 1
                    
        conn.commit()
        
        status_msg = "Database cleared and fresh records loaded!\n\n" if pilihan is True else "Process completed successfully!\n\n"
        status_msg += f"🔹 New records added: {kira_baru}\n"
        if pilihan is False:
            status_msg += f"🔹 Existing records updated with Codes: {kira_kemaskini}"
            
        messagebox.showinfo("SUCCESS", status_msg, parent=win_induk)
    except Exception as e:
        conn.rollback()
        messagebox.showerror("IMPORT ERROR", f"Failed to read Product Excel file:\n{str(e)}", parent=win_induk)
    finally:
        conn.close()
        
def laksanakan_import_excel_machine(win_induk):
    path_fail = filedialog.askopenfilename(
        title="Select Machine Master Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")],
        parent=win_induk
    )
    if not path_fail:
        return
        
    conn = sqlite3.connect("warehouse_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master_machine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_number TEXT,
            machine_code TEXT
        )
    """)
    
    # 🔔 TANYA PENGGUNA SAMA ADA MAHU PADAM DATA LAMA ATAU TIDAK
    pilihan = messagebox.askyesnocancel(
        "IMPORT OPTION", 
        "Do you want to DELETE ALL existing machine mappings and perform a fresh import?\n\n"
        "👉 Click [YES] to Delete All & Overwrite.\n"
        "👉 Click [NO] to Keep Existing Data (Append Mode).\n"
        "👉 Click [CANCEL] to Abort.",
        parent=win_induk
    )
    
    if pilihan is None:  # Pengguna tekan Cancel
        conn.close()
        return
        
    if pilihan is True:  # Pengguna tekan Yes
        cursor.execute("DELETE FROM master_machine")
        conn.commit()
        
    query = "INSERT INTO master_machine (part_number, machine_code) VALUES (?, ?)"
    try:
        wb = openpyxl.load_workbook(path_fail, data_only=True)
        sheet = wb.active
        
        header_row = [str(cell).strip().upper() for cell in next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))]
        
        part_idx = None
        mach_idx = None
        
        for idx, header in enumerate(header_row):
            if "P/N" in header or "PART" in header:
                part_idx = idx
            if "M/C" in header or "MACHINE" in header or "MC" in header:
                mach_idx = idx
                
        if part_idx is None: part_idx = 2
        if mach_idx is None: mach_idx = 3
            
        kira = 0
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row and len(row) > max(part_idx, mach_idx):
                part_val = str(row[part_idx]).strip().upper() if row[part_idx] is not None else ""
                mach_val = str(row[mach_idx]).strip().upper() if row[mach_idx] is not None else ""
                
                if part_val and mach_val and part_val != "NONE" and mach_val != "":
                    if pilihan is True:
                        # Jika fresh import, terus insert tanpa semak duplicate
                        cursor.execute(query, (part_val, mach_val))
                        kira += 1
                    else:
                        # Jika append, kekalkan semakan duplicate asal
                        cursor.execute("SELECT id FROM master_machine WHERE part_number = ? AND machine_code = ?", (part_val, mach_val))
                        if not cursor.fetchone():
                            cursor.execute(query, (part_val, mach_val))
                            kira += 1
                    
        conn.commit()
        
        status_msg = f"Successfully performed a fresh import of {kira} records!" if pilihan is True else f"Successfully added {kira} new Machine Code mapping records!"
        messagebox.showinfo("SUCCESS", status_msg, parent=win_induk)
    except Exception as e:
        conn.rollback()
        messagebox.showerror("IMPORT ERROR", f"Failed to read Machine Excel file:\n{str(e)}", parent=win_induk)
    finally:
        conn.close()

        
# innerbox_form_ui.py - PART 2: FORM INITIALIZATION & FIELDS 1-9
def buka_borang_warehouse(root):
    win_inner = tk.Toplevel(root)
    win_inner.title("FORM 1: INNER BOX PRODUCTION ENTRY")
    win_inner.geometry("540x580+450+30") 
    win_inner.configure(bg="#F8F9FA")
    win_inner.resizable(False, False)
    win_inner.grab_set()
    
    # Menutup dropdown sekiranya klik di luar entry
    win_inner.bind("<Button-1>", lambda e: cd.tutup_dropdown() if e.widget.winfo_class() not in ["Entry", "Button"] else None)
    
    tk.Label(win_inner, text="INNER BOX PRODUCTION FORM", font=("Segoe UI", 13, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=(15, 2))
    tk.Label(win_inner, text="ENTER PRODUCTION DETAILS PRECISELY:", font=("Segoe UI", 9, "italic"), fg="#64748B", bg="#F8F9FA").pack(pady=(0, 10))
    
    frame_data_entry = tk.LabelFrame(win_inner, text=" DATA ENTRY ", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="#F8F9FA", padx=25, pady=10)
    frame_data_entry.pack(fill=tk.X, expand=False, padx=30, pady=(0, 4))
    
    lbl_style = {"font": ("Segoe UI", 9, "bold"), "fg": "#334155", "bg": "#F8F9FA", "width": 20, "anchor": "w"}
    
    kamus_input = {}

    # Field 1: Date Created
    frame_row1 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row1.pack(fill=tk.X, pady=4)
    tk.Label(frame_row1, text="Date Created :", **lbl_style).pack(side=tk.LEFT)
    kamus_input["date"] = DateEntry(frame_row1, width=30, font=("Segoe UI", 10), background="#0D6EFD", foreground="white", borderwidth=1, date_pattern="dd/mm/yyyy")
    kamus_input["date"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
    
    def clear_isian_bawah(event=None):
        for field in ["drawing", "part", "machine"]:
            if field in kamus_input and kamus_input[field].winfo_exists():
                kamus_input[field].delete(0, tk.END)

    def clear_part_dan_machine(event=None):
        for field in ["part", "machine"]:
            if field in kamus_input and kamus_input[field].winfo_exists():
                kamus_input[field].delete(0, tk.END)

       # ─── GANTIKAN MEDAN FIELD 2 (CUSTOMER CODE) LAMA DENGAN VARIABEL STRINGVAR INI ───
    frame_row2 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row2.pack(fill=tk.X, pady=4)
    tk.Label(frame_row2, text="Customer Code :", **lbl_style).pack(side=tk.LEFT)
    frame_cust_mix = tk.Frame(frame_row2, bg="#F8F9FA")
    frame_cust_mix.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Menggunakan StringVar untuk mengesan perubahan teks secara selamat tanpa crash
    sv_customer = tk.StringVar()
    kamus_input["customer"] = tk.Entry(frame_cust_mix, textvariable=sv_customer, font=("Segoe UI", 10), relief="groove", bd=1)
    kamus_input["customer"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)
    
    btn_drop_cust = tk.Button(frame_cust_mix, text="▼", font=("Segoe UI", 7), bg="#E2E8F0", relief="groove", width=3, command=lambda: cd.aksi_butang_dropdown_pukal(kamus_input["customer"], win_inner, cd.ambil_senarai_customer_master()))
    btn_drop_cust.pack(side=tk.RIGHT, padx=(2, 0))

    # ─── GANTIKAN MEDAN FIELD 3 (DRAWING NO) DENGAN VARIABEL STRINGVAR INI ───
    frame_row3 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row3.pack(fill=tk.X, pady=4)
    tk.Label(frame_row3, text="Drawing No :", **lbl_style).pack(side=tk.LEFT)
    frame_draw_mix = tk.Frame(frame_row3, bg="#F8F9FA")
    frame_draw_mix.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    sv_drawing = tk.StringVar()
    kamus_input["drawing"] = tk.Entry(frame_draw_mix, textvariable=sv_drawing, font=("Segoe UI", 10), relief="groove", bd=1)
    kamus_input["drawing"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)
    btn_drop_draw = tk.Button(frame_draw_mix, text="▼", font=("Segoe UI", 7), bg="#E2E8F0", relief="groove", width=3, command=lambda: cd.aksi_butang_dropdown_pukal(kamus_input["drawing"], win_inner, cd.ambil_drawing_terikat(kamus_input["customer"].get())))
    btn_drop_draw.pack(side=tk.RIGHT, padx=(2, 0))

    # ─── GANTIKAN MEDAN FIELD 4 (PART NUMBER) DENGAN VARIABEL STRINGVAR INI ───
    frame_row4 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row4.pack(fill=tk.X, pady=4)
    tk.Label(frame_row4, text="Part Number :", **lbl_style).pack(side=tk.LEFT)
    frame_part_mix = tk.Frame(frame_row4, bg="#F8F9FA")
    frame_part_mix.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    sv_part = tk.StringVar()
    kamus_input["part"] = tk.Entry(frame_part_mix, textvariable=sv_part, font=("Segoe UI", 10), relief="groove", bd=1)
    kamus_input["part"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)
    btn_drop_part = tk.Button(frame_part_mix, text="▼", font=("Segoe UI", 7), bg="#E2E8F0", relief="groove", width=3, command=lambda: cd.aksi_butang_dropdown_pukal(kamus_input["part"], win_inner, cd.ambil_part_terikat(kamus_input["customer"].get(), kamus_input["drawing"].get())))
    btn_drop_part.pack(side=tk.RIGHT, padx=(2, 0))


    # Field 5: Total Quantity
    frame_row5 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row5.pack(fill=tk.X, pady=4)
    tk.Label(frame_row5, text="Total Quantity :", **lbl_style).pack(side=tk.LEFT)
    kamus_input["qty"] = tk.Entry(frame_row5, font=("Segoe UI", 10), relief="groove", bd=1)
    kamus_input["qty"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)

    # Field 6: Packing Qty (Pcs)
    frame_row6 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row6.pack(fill=tk.X, pady=4)
    tk.Label(frame_row6, text="Packing Qty (Pcs) :", **lbl_style).pack(side=tk.LEFT)
    kamus_input["packing_qty"] = tk.Entry(frame_row6, font=("Segoe UI", 10), relief="groove", bd=1)
    kamus_input["packing_qty"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)

    # Field 7: Manufactured Date
    frame_row7 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row7.pack(fill=tk.X, pady=4)
    tk.Label(frame_row7, text="Manufactured Date :", **lbl_style).pack(side=tk.LEFT)
    kamus_input["mfg"] = DateEntry(frame_row7, width=30, font=("Segoe UI", 10), background="#0D6EFD", foreground="white", borderwidth=1, date_pattern="dd/mm/yyyy")
    kamus_input["mfg"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

    # Field 8: Machine Code
    frame_row8 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row8.pack(fill=tk.X, pady=4)
    tk.Label(frame_row8, text="Machine Code :", **lbl_style).pack(side=tk.LEFT)
    frame_mach_mix = tk.Frame(frame_row8, bg="#F8F9FA")
    frame_mach_mix.pack(side=tk.LEFT, fill=tk.X, expand=True)
    kamus_input["machine"] = tk.Entry(frame_mach_mix, font=("Segoe UI", 10), relief="groove", bd=1)
    kamus_input["machine"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)
    btn_drop_mach = tk.Button(frame_mach_mix, text="▼", font=("Segoe UI", 7), bg="#E2E8F0", relief="groove", width=3, command=lambda: cd.aksi_butang_dropdown_pukal(kamus_input["machine"], win_inner, cd.ambil_machine_terikat(kamus_input["part"].get())))
    btn_drop_mach.pack(side=tk.RIGHT, padx=(2, 0))

    # Field 9: Lot Number
    frame_row9 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row9.pack(fill=tk.X, pady=4)
    tk.Label(frame_row9, text="Lot Number :", **lbl_style).pack(side=tk.LEFT)
    kamus_input["lot"] = tk.Entry(frame_row9, font=("Segoe UI", 10), relief="groove", bd=1)
    kamus_input["lot"].pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=2)
    # ─── BINDINGS EVENT UNTUK AUTO-COMPLETE TERAPUNG ───
        # ─── BINDINGS EVENT UNTUK AUTO-COMPLETE TERAPUNG (VERSI STRINGVAR JAMINAN BEBAS CRASH) ───
    kamus_input["customer"].bind("<KeyRelease>", lambda e: cd.kendalikan_taipan_dropdown(kamus_input["customer"], win_inner, cd.ambil_senarai_customer_master()) if e.keysym not in ["Up", "Down", "Return", "Escape"] else None)
    kamus_input["drawing"].bind("<KeyRelease>", lambda e: cd.kendalikan_taipan_dropdown(kamus_input["drawing"], win_inner, cd.ambil_drawing_terikat(kamus_input["customer"].get())) if e.keysym not in ["Up", "Down", "Return", "Escape"] else None)
    kamus_input["part"].bind("<KeyRelease>", lambda e: cd.kendalikan_taipan_dropdown(kamus_input["part"], win_inner, cd.ambil_part_terikat(kamus_input["customer"].get(), kamus_input["drawing"].get())) if e.keysym not in ["Up", "Down", "Return", "Escape"] else None)
    kamus_input["machine"].bind("<KeyRelease>", lambda e: cd.kendalikan_taipan_dropdown(kamus_input["machine"], win_inner, cd.ambil_machine_terikat(kamus_input["part"].get())) if e.keysym not in ["Up", "Down", "Return", "Escape"] else None)

    # 🌟 SISTEM AUTOMATIK PENAPISAN RANTAIAN: Bersih & Padam Isian Bawah jika Pilihan Atas Berubah 🌟
    def on_customer_changed(*args):
        clear_isian_bawah()
    sv_customer.trace_add("write", on_customer_changed)

    def on_drawing_changed(*args):
        clear_part_dan_machine()
    sv_drawing.trace_add("write", on_drawing_changed)

    def auto_isi_machine_dari_part(*args):
        # Dipanggil secara automatik sebaik sahaja nilai pada part number berubah/dipilih
        part_terpilih = kamus_input["part"].get().strip()
        if part_terpilih:
            senarai_mc = cd.ambil_machine_terikat(part_terpilih)
            if senarai_mc:
                item_mc = senarai_mc[0] if isinstance(senarai_mc, list) else senarai_mc
                kamus_input["machine"].delete(0, tk.END)
                kamus_input["machine"].insert(0, str(item_mc).strip())
                
    sv_part.trace_add("write", auto_isi_machine_dari_part)

    # ─── NAVIGATION KEY BINDINGS (RETURN FOCUS REDIRECTION) ───
    susunan_focus = [kamus_input["customer"], kamus_input["drawing"], kamus_input["part"], kamus_input["qty"], kamus_input["packing_qty"], kamus_input["machine"], kamus_input["lot"]]
    for idx, widget in enumerate(susunan_focus[:-1]):
        widget.bind("<Return>", lambda event, nxt=susunan_focus[idx+1]: alih_fokus(event, nxt))
    # ─── ACTION CONTROL BUTTONS BAR (STANDARDIZED COLOR SCHEME) ───
    btn_frame = tk.Frame(win_inner, bg="#F8F9FA")
    btn_frame.pack(fill=tk.X, padx=30, pady=10)
    
    tk.Button(btn_frame, text="SUBMIT DATA", font=("Segoe UI", 10, "bold"), bg="#00A86B", fg="white", bd=0, height=2, command=lambda: backend.proses_submit_data_pukal(win_inner, kamus_input)).pack(fill=tk.X, pady=5)
    
    bottom_row = tk.Frame(btn_frame, bg="#F8F9FA")
    bottom_row.pack(fill=tk.X)
    
    b_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "bd": 0, "width": 11, "height": 2}
    tk.Button(bottom_row, text="Excel Cus", bg="#0076CE", command=lambda: laksanakan_import_excel_langsung(win_inner), **b_style).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
    tk.Button(bottom_row, text="Excel Mach", bg="#6F42C1", command=lambda: laksanakan_import_excel_machine(win_inner), **b_style).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
    
    def reset_borang():
        clear_isian_bawah()
        kamus_input["customer"].delete(0, tk.END)
        kamus_input["qty"].delete(0, tk.END)
        kamus_input["packing_qty"].delete(0, tk.END)
        kamus_input["lot"].delete(0, tk.END)
        
    tk.Button(bottom_row, text="Reset", bg="#E65100", command=reset_borang, **b_style).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
    tk.Button(bottom_row, text="Back", bg="#212529", command=win_inner.destroy, **b_style).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
