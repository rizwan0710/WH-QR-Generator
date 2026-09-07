import tkinter as tk
from tkinter import ttk

def bina_input_header(parent, var_customer):
    """Membina kawasan input Invoice No, SO No, dan Customer Auto Detect."""
    frame = tk.Frame(parent, bg="#F8F9FA")
    frame.pack(pady=5, padx=25, fill="x")
    
    # 1. Invoice Number Input
    tk.Label(frame, text="Invoice No:", font=("Segoe UI", 9, "bold"), fg="#495057", bg="#F8F9FA").grid(row=0, column=0, padx=10, pady=6, sticky="e")
    ent_inv = tk.Entry(frame, width=28, font=("Segoe UI", 10), relief="groove")
    ent_inv.grid(row=0, column=1, padx=5, pady=6, sticky="w")
    
    # 2. SO Number Input
    tk.Label(frame, text="SO No:", font=("Segoe UI", 9, "bold"), fg="#495057", bg="#F8F9FA").grid(row=1, column=0, padx=10, pady=6, sticky="e")
    ent_so = tk.Entry(frame, width=28, font=("Segoe UI", 10), relief="groove")
    ent_so.grid(row=1, column=1, padx=5, pady=6, sticky="w")
    
    # 3. Customer Auto-Detect Field
    tk.Label(frame, text="Customer Name (Auto):", font=("Segoe UI", 9, "bold"), fg="#495057", bg="#F8F9FA").grid(row=2, column=0, padx=10, pady=6, sticky="e")
    ent_cust = tk.Entry(frame, textvariable=var_customer, width=28, state="readonly", fg="#0D6EFD", font=("Segoe UI", 9, "bold"), relief="flat")
    ent_cust.grid(row=2, column=1, padx=5, pady=6, sticky="w")
    
    return ent_inv, ent_so

def bina_selector_amount(parent, var_amount):
    """Membina combobox bagi pemilihan jumlah kotak Outer Box."""
    frame = tk.Frame(parent, bg="#F8F9FA")
    frame.pack(pady=8)
    
    tk.Label(frame, text="Amount of Boxes:", font=("Segoe UI", 10, "bold"), fg="#212529", bg="#F8F9FA").pack(side=tk.LEFT, padx=5)
    cb_amount = ttk.Combobox(frame, textvariable=var_amount, values=[str(i) for i in range(1, 11)], width=6, state="readonly", font=("Segoe UI", 10))
    cb_amount.pack(side=tk.LEFT, padx=5)
    return cb_amount

def bina_input_scanner(parent):
    """Membina kotak input putih khusus untuk menangkap laser laser scanner."""
    frame = tk.Frame(parent, bg="#F8F9FA")
    frame.pack(pady=8, padx=35, fill="x")
    
    tk.Label(frame, text="SCANNER INPUT (OUTER QR):", font=("Segoe UI", 9, "bold"), fg="#E65100", bg="#F8F9FA").pack(anchor="w", pady=2)
    ent_scan = tk.Entry(frame, width=35, font=("Segoe UI", 11), bg="#FFFFFF", fg="#000000", relief="groove", bd=2)
    ent_scan.pack(fill="x", ipady=3)
    return ent_scan
