import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import form_invoice_packing_logic as logic 

# Import fail logik pembantu dinamik baru yang telah dipecahkan
import form_invoice_packing_helper as helper

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
    
    # Slot 2: Invoice Number
    frame_row2 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row2.pack(fill=tk.X, pady=3)
    tk.Label(frame_row2, text="Invoice Number :", **lbl_style).pack(side=tk.LEFT)
    entry_inv_no = tk.Entry(frame_row2, **ent_style)
    entry_inv_no.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
    
    # Slot 3: Part Number / SO
    frame_row3 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row3.pack(fill=tk.X, pady=3)
    tk.Label(frame_row3, text="SO Number :", **lbl_style).pack(side=tk.LEFT)
    entry_so_no = tk.Entry(frame_row3, **ent_style)
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
    tk.Label(frame_row_setup, text="Total Box Amount :", font=("Segoe UI", 9, "bold"), fg="#E65100", bg="#F8F9FA", width=18, anchor="w").pack(side=tk.LEFT)
    
    entry_total_box = tk.Entry(frame_row_setup, font=("Segoe UI", 10, "bold"), relief="groove", bd=1, width=10, justify="center")
    entry_total_box.insert(0, "4") 
    entry_total_box.pack(side=tk.LEFT, padx=2)
    
    def aksi_apply_total_box():
        helper.laksanakan_penjanaan_kotak_pukal(entry_total_box, frame_scroll_content, entries_outer, var_customer, lbl_counter)
        # 🌟 KOREKSI UTAMA BARIS 82: Memanggil kotak indeks pertama [0] di dalam list untuk menerima focus_set 🌟
        if entries_outer and len(entries_outer) > 0:
            entries_outer[0].focus_set()

    tk.Button(frame_row_setup, text="APPLY", command=aksi_apply_total_box, bg="#E65100", fg="white", font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2", padx=10).pack(side=tk.LEFT, padx=5)
    
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
    
    helper.bina_kotak_imbasan_dinamik(frame_scroll_content, 4, entries_outer, var_customer, lbl_counter)

    # ─── ENJIN LOMPATAN FOKUS ENTER AUTOMATIK ───
    entry_inv_no.bind("<Return>", lambda event: entry_so_no.focus_set())
    entry_so_no.bind("<Return>", lambda event: entry_total_box.focus_set())
    entry_total_box.bind("<Return>", lambda event: aksi_apply_total_box())

    # ─── Barisan Butang Kawalan Aksi Bawah ───
    tk.Button(win_inv, text="SUBMIT & GENERATE INVOICE QR", command=lambda: logic.proses_submit_invoice(win_inv, entry_date, entry_inv_no, entry_so_no, entries_outer, win_inv.children.get("!button")), bg="#007ACC", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").pack(fill="x", padx=25, pady=(0, 4))
    
    frame_action_bar = tk.Frame(win_inv, bg="#F8F9FA")
    frame_action_bar.pack(fill="x", padx=25, pady=(0, 15))
    frame_action_bar.columnconfigure(0, weight=1)
    frame_action_bar.columnconfigure(1, weight=1)
    
    tk.Button(frame_action_bar, text="🔄 RESET", command=lambda: helper.cuci_isi_borang_invoice(entry_inv_no, entry_so_no, var_customer, entry_total_box, frame_scroll_content, entries_outer, lbl_counter), bg="#6C757D", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").grid(row=0, column=0, padx=(0, 3), sticky="ew")
    tk.Button(frame_action_bar, text="◀ BACK", command=win_inv.destroy, bg="#212529", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").grid(row=0, column=1, padx=(3, 0), sticky="ew")

    entry_inv_no.focus_set()
