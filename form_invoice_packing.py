# form_invoice_packing.py - COMPLETED & CONSOLIDATED STABLE REVERSION (100% FIXED)
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import form_invoice_packing_logic as logic 

# Import fail logik pembantu dinamik baru yang telah dipecahkan
import form_invoice_packing_helper as helper

# Import fail logik utama invois untuk mengaktifkan fungsi cetakan pukal (1 Window Pop-Up)
import invoice_packing_logic

def buka_borang_invoice(root):
    """🌟 UPGRADED INVOICE DYNAMIC SCROLL CONTAINER UI (WITH FIXED CALENDAR & FOCUS INDEX) 🌟"""
    win_inv = tk.Toplevel(root)
    win_inv.title("FORM 3: INVOICE LABEL")
    win_inv.geometry("560x720") 
    win_inv.configure(bg="#F8F9FA")
    win_inv.grab_set()
    
    var_customer = tk.StringVar(value="- AUTO DETECT -")
    entries_outer = []
    
    # ─── Pengepala Borang ───
    tk.Label(win_inv, text="INVOICE PACKING FORM", font=("Segoe UI", 13, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=(15, 2))
    tk.Label(win_inv, text="PLEASE ENTER DETAILS BELOW PRECISELY:", font=("Segoe UI", 9, "italic"), fg="#64748B", bg="#F8F9FA").pack(pady=(0, 10))
    
    # ─── Bingkai Data Entry Utama ───
    frame_data_entry = tk.LabelFrame(win_inv, text=" DATA ENTRY ", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="#F8F9FA", padx=20, pady=10)
    frame_data_entry.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 10))
    
    lbl_style = {"font": ("Segoe UI", 9, "bold"), "fg": "#334155", "bg": "#F8F9FA", "width": 18, "anchor": "w"}
    ent_style = {"font": ("Segoe UI", 10), "relief": "groove", "bd": 1}
    
    # Slot 1: Date Created
    frame_row1 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row1.pack(fill=tk.X, pady=3)
    tk.Label(frame_row1, text="Date Created :", **lbl_style).pack(side=tk.LEFT)
    
    entry_date = DateEntry(
        frame_row1, width=32, font=("Segoe UI", 10), 
        background="#0D6EFD", foreground="white", borderwidth=1, 
        date_pattern="dd/mm/yyyy"
    )
    entry_date.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=1)
    entry_date.bind("<Key>", lambda e: "break")
    
        # 🌟 KOREKSI PEMBOLEHUBAH AUTO-POPULATE (PRE-BILLING LINKAGE) 🌟
    var_invoice_no = tk.StringVar()
    var_so_no = tk.StringVar()

        # 🌟 KOREKSI PEMBOLEHUBAH AUTO-POPULATE (PRE-BILLING LINKAGE WITH PLACEHOLDERS) 🌟
    var_invoice_no = tk.StringVar(value="- AUTO DETECT -")
    var_so_no = tk.StringVar(value="- AUTO DETECT -")

    # Fungsi setempat standalone untuk memicu semakan Foreign Key berasaskan nama Customer
    def pemicu_auto_populate_pre_billing(event=None):
        nama_cust = var_customer.get().strip().upper()
        
        if not nama_cust or nama_cust == "- AUTO DETECT -":
            var_invoice_no.set("- AUTO DETECT -")
            var_so_no.set("- AUTO DETECT -")
            return
            
        import sqlite3
        import database_manager as dbm
        try:
            with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as conn:
                cursor = conn.cursor()
                
                # 🌟 UPGRADE CARIAN SEPARA (ANTI-FAIL): Mencari persamaan nama syarikat menggunakan kaedah LIKE 🌟
                query_bijak = """
                    SELECT invoice_no, so_no FROM master_invoice 
                    WHERE ? LIKE '%' || UPPER(TRIM(customer_name)) || '%'
                       OR UPPER(TRIM(customer_name)) LIKE '%' || ? || '%'
                    ORDER BY id DESC LIMIT 1
                """
                cursor.execute(query_bijak, (nama_cust, nama_cust))
                rekod = cursor.fetchone()
                
                if rekod:
                    inv_terdaftar, so_terdaftar = rekod
                    var_invoice_no.set(str(inv_terdaftar).strip())
                    var_so_no.set(str(so_terdaftar).strip())
                    print(f"[FK LINK SUCCESS] Synced {nama_cust} -> INV: {inv_terdaftar} | SO: {so_terdaftar}")
                else:
                    var_invoice_no.set("- NOT REGISTERED -")
                    var_so_no.set("- NOT REGISTERED -")
        except Exception as e:
            print(f"[FK LINK NOTICE] Bypassed check: {e}")
 

    # Mengikat pembolehubah var_customer supaya sentiasa memantau perubahan nama secara live
    var_customer.trace_add("write", lambda *args: win_inv.after(50, pemicu_auto_populate_pre_billing))

    # Slot 2: Invoice Number (Kini Bersama Placeholder Auto Detect)
    frame_row2 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row2.pack(fill=tk.X, pady=3)
    tk.Label(frame_row2, text="Invoice Number :", **lbl_style).pack(side=tk.LEFT)
    entry_inv_no = tk.Entry(frame_row2, textvariable=var_invoice_no, font=("Segoe UI", 10, "bold"), state="readonly", fg="#0D6EFD", relief="flat", bg="#F8F9FA")
    entry_inv_no.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
    
    # Slot 3: SO Number (Kini Bersama Placeholder Auto Detect)
    frame_row3 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row3.pack(fill=tk.X, pady=3)
    tk.Label(frame_row3, text="SO Number :", **lbl_style).pack(side=tk.LEFT)
    entry_so_no = tk.Entry(frame_row3, textvariable=var_so_no, font=("Segoe UI", 10, "bold"), state="readonly", fg="#0D6EFD", relief="flat", bg="#F8F9FA")
    entry_so_no.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

    
    # Slot Baru: Customer Name 
    frame_row_cust = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row_cust.pack(fill=tk.X, pady=3)
    tk.Label(frame_row_cust, text="Customer Name :", **lbl_style).pack(side=tk.LEFT)
    entry_cust_auto = tk.Entry(frame_row_cust, textvariable=var_customer, font=("Segoe UI", 10, "bold"), state="readonly", fg="#0D6EFD", relief="flat", bg="#F8F9FA")
    entry_cust_auto.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
    
    ttk.Separator(frame_data_entry, orient="horizontal").pack(fill="x", pady=6)
    
    # Slot Baru: Dynamic Input Controller Setup
    frame_row_setup = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row_setup.pack(fill=tk.X, pady=4)
    
    # 🟠 TUKAR TEKS TOTAL BOX AMOUNT KEPADA OREN (#FD7E14)
    tk.Label(frame_row_setup, text="Total Box Amount :", font=("Segoe UI", 9, "bold"), fg="#FD7E14", bg="#F8F9FA", width=18, anchor="w").pack(side=tk.LEFT)
    
    entry_total_box = tk.Entry(frame_row_setup, font=("Segoe UI", 10, "bold"), relief="groove", bd=1, width=10, justify="center")
    entry_total_box.insert(0, "4") 
    entry_total_box.pack(side=tk.LEFT, padx=2)
    
       # 🌟 INTEGRASI PARAMETER: Memanggil nama fungsi bina_kotak_imbasan_dinamik yang wujud dalam helper! 🌟
    def aksi_apply_total_box():
        try:
            jumlah_kotak = int(entry_total_box.get().strip())
        except ValueError:
            jumlah_kotak = 4 
            
        helper.bina_kotak_imbasan_dinamik(frame_scroll_content, jumlah_kotak, entries_outer, var_customer, lbl_counter, entry_inv_no, entry_so_no)
        
        if entries_outer and len(entries_outer) > 0:
            entries_outer[0].focus_set()

    # TUKAR WARNA BUTANG APPLY KEPADA OREN (#FD7E14)
    tk.Button(frame_row_setup, text="APPLY", command=aksi_apply_total_box, bg="#FD7E14", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2", padx=10).pack(side=tk.LEFT, padx=5)

  

    # 🟠 TUKAR WARNA BUTANG APPLY KEPADA OREN (#FD7E14)
   # tk.Button(frame_row_setup, text="APPLY", command=aksi_apply_total_box, bg="#FD7E14", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2", padx=10).pack(side=tk.LEFT, padx=5)
    
    lbl_counter = tk.Label(frame_row_setup, text="Scanned: 0 / 4 Boxes", font=("Segoe UI", 9, "bold"), fg="#64748B", bg="#F8F9FA")
    lbl_counter.pack(side=tk.RIGHT, padx=5)

    # PANEL SKROL KANVAS 
    frame_scroll_container = tk.Frame(frame_data_entry, bg="white", bd=1, relief="groove")
    frame_scroll_container.pack(fill=tk.BOTH, expand=True, pady=5)
    
    canvas = tk.Canvas(frame_scroll_container, bg="white", highlightthickness=0)
    scrollbar_y = ttk.Scrollbar(frame_scroll_container, orient=tk.VERTICAL, command=canvas.yview)
    frame_scroll_content = tk.Frame(canvas, bg="white")
    
    canvas.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    id_canvas_window = canvas.create_window((0, 0), window=frame_scroll_content, anchor="nw")
    
    frame_scroll_content.bind(
        "<Configure>", 
        lambda e: [canvas.configure(scrollregion=canvas.bbox("all")), canvas.itemconfig(id_canvas_window, width=canvas.winfo_width())]
    )
    
    # 🌟 INTEGRASI PARAMETER BIL 2: Alirkan objek entry_inv_no dan entry_so_no semasa tetingkap mula-mula dibuka (Default 4 Boxes)
    helper.bina_kotak_imbasan_dinamik(frame_scroll_content, 4, entries_outer, var_customer, lbl_counter, entry_inv_no, entry_so_no)

    # ─── ENJIN LOMPATAN FOKUS ENTER AUTOMATIK ───
    entry_inv_no.bind("<Return>", lambda event: entry_so_no.focus_set())
    entry_so_no.bind("<Return>", lambda event: entry_total_box.focus_set())
    entry_total_box.bind("<Return>", lambda event: aksi_apply_total_box())

    def eksekusi_submit_dan_cetak_pukal():
        logic.proses_submit_invoice(
            win_inv, 
            entry_date, 
            entry_inv_no, 
            entry_so_no, 
            entries_outer, 
            win_inv.children.get("!button")
        )

    # ─── Barisan Butang Kawalan Aksi Bawah ───
    tk.Button(win_inv, text="SUBMIT & PRINT INVOICE QR", command=eksekusi_submit_dan_cetak_pukal, bg="#1E7E34", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").pack(fill="x", padx=25, pady=(0, 4))
    
    frame_action_bar = tk.Frame(win_inv, bg="#F8F9FA")
    frame_action_bar.pack(fill="x", padx=25, pady=(0, 15))
    frame_action_bar.columnconfigure(0, weight=1)
    frame_action_bar.columnconfigure(1, weight=1)
    
    # 🔄 TUKAR WARNA BUTANG RESET KEPADA OREN (#FD7E14)
    tk.Button(frame_action_bar, text="🔄 RESET", command=lambda: helper.cuci_isi_borang_invoice(entry_inv_no, entry_so_no, var_customer, entry_total_box, frame_scroll_content, entries_outer, lbl_counter), bg="#FD7E14", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").grid(row=0, column=0, padx=(0, 3), sticky="ew")
    
    # ◀ KEKALKAN WARNA BUTANG BACK KELABU GELAP (#212529)
    tk.Button(frame_action_bar, text="◀ BACK", command=win_inv.destroy, bg="#212529", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").grid(row=0, column=1, padx=(3, 0), sticky="ew")

    entry_inv_no.focus_set()
