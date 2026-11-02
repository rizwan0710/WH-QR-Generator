import tkinter as tk
from tkinter import ttk

# ==============================================================================
# KONFIGURASI STYLE COMBOBOX MODEN (FLAT & CLEAN BAR)
# ==============================================================================
style = ttk.Style()
style.theme_use('clam')

style.configure(
    "TCombobox",
    fieldbackground="white",   # Dalam kotak putih bersih
    background="#E2E8F0",      # Anak panah kelabu moden
    arrowcolor="#334155",      # Ikon panah gelap
    bordercolor="#CBD5E1",     # Sempadan nipis rata
    relief="flat",
    borderwidth=1
)

style.map(
    "TCombobox",
    fieldbackground=[("readonly", "white")],
    foreground=[("readonly", "#334155")]
)

def bina_input_header(parent, var_customer, var_invoice_no, var_so_no):
    """Builds the combobox dropdown fields for Invoice No, SO No, and Customer Auto Detect."""
    frame = tk.Frame(parent, bg="#F8F9FA")
    frame.pack(pady=5, padx=25, fill="x")
    
    # 1. Invoice Number Input (Kini menggunakan Dropdown Clean Bar)
    tk.Label(frame, text="Invoice No:", font=("Segoe UI", 9, "bold"), fg="#495057", bg="#F8F9FA").grid(row=0, column=0, padx=10, pady=6, sticky="e")
    ent_inv = ttk.Combobox(frame, textvariable=var_invoice_no, width=26, font=("Segoe UI", 10, "bold"), state="readonly", style="TCombobox")
    ent_inv.grid(row=0, column=1, padx=5, pady=6, sticky="w")
    
    # 2. SO Number Input (Kini menggunakan Dropdown Clean Bar)
    tk.Label(frame, text="SO No:", font=("Segoe UI", 9, "bold"), fg="#495057", bg="#F8F9FA").grid(row=1, column=0, padx=10, pady=6, sticky="e")
    ent_so = ttk.Combobox(frame, textvariable=var_so_no, width=26, font=("Segoe UI", 10, "bold"), state="readonly", style="TCombobox")
    ent_so.grid(row=1, column=1, padx=5, pady=6, sticky="w")
    
    # 3. Customer Auto-Detect Field
    tk.Label(frame, text="Customer Name (Auto):", font=("Segoe UI", 9, "bold"), fg="#495057", bg="#F8F9FA").grid(row=2, column=0, padx=10, pady=6, sticky="e")
    ent_cust = tk.Entry(frame, textvariable=var_customer, width=28, state="readonly", fg="#0D6EFD", font=("Segoe UI", 9, "bold"), relief="flat")
    ent_cust.grid(row=2, column=1, padx=5, pady=6, sticky="w")
    
    return ent_inv, ent_so
def bina_selector_amount(parent, var_amount):
    """Builds the combobox selector for Outer Box quantity."""
    frame = tk.Frame(parent, bg="#F8F9FA")
    frame.pack(pady=8)
    
    tk.Label(frame, text="Amount of Boxes:", font=("Segoe UI", 10, "bold"), fg="#212529", bg="#F8F9FA").pack(side=tk.LEFT, padx=5)
    cb_amount = ttk.Combobox(frame, textvariable=var_amount, values=[str(i) for i in range(1, 11)], width=6, state="readonly", font=("Segoe UI", 10))
    cb_amount.pack(side=tk.LEFT, padx=5)
    return cb_amount

def bina_input_scanner(parent):
    """Builds a white input target entry specifically mapped for high-speed laser scanner input."""
    frame = tk.Frame(parent, bg="#F8F9FA")
    frame.pack(pady=8, padx=35, fill="x")
    
    # 🟠 Menukar label tulisan scanner input supaya mengikut ton warna oren standard (#FD7E14)
    tk.Label(frame, text="SCANNER INPUT (OUTER QR):", font=("Segoe UI", 9, "bold"), fg="#FD7E14", bg="#F8F9FA").pack(anchor="w", pady=2)
    ent_scan = tk.Entry(frame, width=35, font=("Segoe UI", 11), bg="#FFFFFF", fg="#000000", relief="groove", bd=2)
    ent_scan.pack(fill="x", ipady=3)
    return ent_scan

