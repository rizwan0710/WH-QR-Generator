# form_pre_billing.py - PART 1: IMPORTS & DATABASE LOGIC (100% KALIS EXE)
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import sqlite3
import os
import sys
from datetime import datetime
import database_manager as dbm
import custom_dropdown as cd

def simpan_data_pre_billing(win, invoice_ent, so_ent, customer_ent):
    """Menyimpan data pendaftaran awal invois dan SO ke dalam jadual master_invoice kilang."""
    inv_no = invoice_ent.get().strip().upper()
    so_no = so_ent.get().strip().upper()
    cust_name = customer_ent.get().strip().upper()

    # Semakan validasi isian wajib lantai kilang
    if not inv_no or not so_no or not cust_name:
        return messagebox.showwarning("INCOMPLETE", "PLEASE FILL ALL FIELDS BEFORE SUBMITTING!", parent=win)

    tarikh_sekarang = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    try:
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            
            # Memasukkan rekod invois secara parameterized query untuk jaminan integriti data
            cursor.execute("""
                INSERT INTO master_invoice (invoice_no, so_no, customer_name, tarikh_masuk)
                VALUES (?, ?, ?, ?)
            """, (inv_no, so_no, cust_name, tarikh_sekarang))
            
            conn.commit()
            
        # Log pergerakan perubahan data ke dalam sistem audit logs utama secara automatik
        try:
            import database_audit_logger
            database_audit_logger.record_edit_activity("PRE-BILLING FORM", f"ADDED PRE-REGISTRATION: INV: {inv_no} | SO: {so_no} | CUST: {cust_name}")
        except Exception:
            pass

        messagebox.showinfo("SUCCESS", f"Pre-Billing Data successfully registered!\n\n🔹 Invoice No: {inv_no}\n🔹 SO No: {so_no}\n🔹 Customer: {cust_name}", parent=win)
        
        # Kosongkan isian borang untuk persediaan data kemasukan seterusnya
        invoice_ent.delete(0, tk.END)
        so_ent.delete(0, tk.END)
        customer_ent.delete(0, tk.END)
        invoice_ent.focus_set()

    except sqlite3.IntegrityError:
        messagebox.showerror("DUPLICATE ERROR", f"Invoice No '{inv_no}' already exists in the system master list!", parent=win)
    except Exception as e:
        messagebox.showerror("DATABASE ERROR", f"Failed to record information context:\n{str(e)}", parent=win)

def ambil_senarai_customer_dari_master_db():
    """Mengambil senarai unik nama customer yang telah diimport dalam pangkalan data untuk drop-down."""
    try:
        with sqlite3.connect(dbm.DATABASE_PATH, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT TRIM(customer_name) FROM master_produk WHERE customer_name IS NOT NULL AND customer_name != ''")
            rekod = cursor.fetchall()
            return sorted(list(set([r[0].upper() for r in rekod if r[0]])))
    except Exception:
        return []
    # form_pre_billing.py - PART 2: GUI INITIALIZATION & CONTROL PANEL LAYOUT
# form_pre_billing.py - PART 2: GUI INITIALIZATION & SIDE-BY-SIDE BUTTONS LAYOUT
def buka_borang_pre_billing(root):
    """Membuka tetingkap Form 4 dengan susunan butang sebaris secara kiri dan kanan standard kilang OHTA."""
    win_pre = tk.Toplevel(root)
    win_pre.title("FORM 4: PRE-BILLING DOCUMENT ENTRY")
    win_pre.geometry("540x330+450+100") # Dikurangkan ketinggian canvas (-40) kerana butang sudah sebaris
    win_pre.configure(bg="#F8F9FA")
    win_pre.resizable(False, False)
    win_pre.grab_set()
    
    win_pre.bind("<Button-1>", lambda e: cd.tutup_dropdown() if e.widget.winfo_class() not in ["Entry", "Button"] else None)
    
    tk.Label(win_pre, text="PRE-BILLING ENTRY FORM", font=("Segoe UI", 13, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=(20, 2))
    tk.Label(win_pre, text="PRE-REGISTER INVOICE DETAILS FOR AUTO-LINKAGE:", font=("Segoe UI", 9, "italic"), fg="#64748B", bg="#F8F9FA").pack(pady=(0, 15))
    
    frame_entry = tk.LabelFrame(win_pre, text=" DOCUMENTS INPUT ", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="#F8F9FA", padx=25, pady=15)
    frame_entry.pack(fill=tk.X, expand=False, padx=30, pady=5)
    
    lbl_style = {"font": ("Segoe UI", 9, "bold"), "fg": "#334155", "bg": "#F8F9FA", "width": 18, "anchor": "w"}
    
    # Medan 1: Invoice No
    frame_row1 = tk.Frame(frame_entry, bg="#F8F9FA")
    frame_row1.pack(fill=tk.X, pady=6)
    tk.Label(frame_row1, text="Invoice No :", **lbl_style).pack(side=tk.LEFT)
    ent_invoice = tk.Entry(frame_row1, font=("Segoe UI", 10), relief="groove", bd=1)
    ent_invoice.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
    ent_invoice.focus_set()

    # Medan 2: SO No
    frame_row2 = tk.Frame(frame_entry, bg="#F8F9FA")
    frame_row2.pack(fill=tk.X, pady=6)
    tk.Label(frame_row2, text="SO No :", **lbl_style).pack(side=tk.LEFT)
    ent_so = tk.Entry(frame_row2, font=("Segoe UI", 10), relief="groove", bd=1)
    ent_so.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)

    # Medan 3: Customer Name Dropdown
    frame_row3 = tk.Frame(frame_entry, bg="#F8F9FA")
    frame_row3.pack(fill=tk.X, pady=6)
    tk.Label(frame_row3, text="Customer Name :", **lbl_style).pack(side=tk.LEFT)
    frame_cust_mix = tk.Frame(frame_row3, bg="#F8F9FA")
    frame_cust_mix.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    ent_customer = tk.Entry(frame_cust_mix, font=("Segoe UI", 10), relief="groove", bd=1)
    ent_customer.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
    
    btn_drop = tk.Button(frame_cust_mix, text="▼", font=("Segoe UI", 7), bg="#E2E8F0", relief="groove", width=3, 
                         command=lambda: cd.aksi_butang_dropdown_pukal(ent_customer, win_pre, ambil_senarai_customer_dari_master_db()))
    btn_drop.pack(side=tk.RIGHT, padx=(2, 0))

    ent_customer.bind("<KeyRelease>", lambda e: cd.kendalikan_taipan_dropdown(ent_customer, win_pre, ambil_senarai_customer_dari_master_db()) if e.keysym not in ["Up", "Down", "Return", "Escape"] else None)

    ent_invoice.bind("<Return>", lambda e: ent_so.focus_set())
    ent_so.bind("<Return>", lambda e: ent_customer.focus_set())

    # ─── 🌟 ACTION BAR KAWALAN BUTTONS (SUSUNAN KIRI & KANAN SERAGAM) ───
    btn_frame = tk.Frame(win_pre, bg="#F8F9FA")
    btn_frame.pack(fill=tk.X, padx=30, pady=15)
    
    gaya_butang_seragam = {
        "font": ("Segoe UI", 9, "bold"), # Dikecilkan sikit kepada saiz 9 supaya muat cantik sebaris
        "fg": "white",
        "bd": 0,
        "height": 2,          
        "relief": "flat",
        "cursor": "hand2"
    }
    
    # 💾 Butang Kiri: Register Invoice Data (Ditolak rapat ke kiri)
    tk.Button(btn_frame, text="💾 REGISTER ", bg="#1E3A8A",
              command=lambda: simpan_data_pre_billing(win_pre, ent_invoice, ent_so, ent_customer),
              **gaya_butang_seragam).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    # ◀ Butang Kanan: Back To Dashboard (Ditolak rapat ke kanan)
    tk.Button(btn_frame, text="◀ BACK ", bg="#64748B",
              command=win_pre.destroy,
              **gaya_butang_seragam).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))


