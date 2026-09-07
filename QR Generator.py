import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# Import subsistem logistik OHTA Precision
import database_manager as dbm 
import innerbox_form_ui as ifu
import form_outer_packing as fop
import form_invoice_packing as fip 
import dashboard_logic as dl
import main_dashboard_binder as mdb  # Fail pembantu pengurus logik RAM

# Bingkai Utama Perisian (Kompak & Ringan)
root = tk.Tk()
root.title("OHTA PRECISION - BARCODE & QR CODE GENERATOR")
root.geometry("700x710+380+10")  
root.configure(bg="#F1F5F9")
root.resizable(False, False)

# Setup pangkalan data automatik pada permulaan sistem
dbm.siapkan_database()

def laksanakan_shutdown_system_selamat():
    """🌟 SYSTEM SAFE SHUTDOWN: Memastikan penutupan perisian yang bersih gred industri 🌟"""
    if messagebox.askyesno("CONFIRM SHUTDOWN", "Are you sure you want to securely close and exit the OHTA Precision System?", parent=root):
        try:
            root.grab_release()
        except:
            pass
        root.quit()
        root.destroy()

# Header Utama Penjenamaan Korporat
tk.Label(root, text="OHTA PRECISION (M) SDN BHD", font=("Segoe UI", 14, "bold"), fg="#1E3A8A", bg="#F1F5F9").pack(pady=(12, 2))
tk.Label(root, text="AUTOMATED BARCODE & QR CODE GENERATOR", font=("Segoe UI", 9, "bold"), fg="#64748B", bg="#F1F5F9").pack(pady=(0, 6))

# ─── SECTION 1: OPERATIONAL FORM CONTROL ───
frame_control = tk.LabelFrame(root, text=" OPERATIONAL FORM CONTROL ", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="white", padx=20, pady=8)
frame_control.pack(fill="x", padx=25, pady=4)

btn_form_style = {"font": ("Segoe UI", 10, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

tk.Button(frame_control, text="📦 FORM 1: INNER PACKING", 
          command=lambda: [ifu.buka_borang_warehouse(root), root.after(600, mdb.kemaskini_angka_dashboard_live)], 
          bg="#0284C7", **btn_form_style).pack(fill="x", pady=3)

tk.Button(frame_control, text="🏢 FORM 2: OUTER PACKING", 
          command=lambda: [fop.buka_borang_outer(root), root.after(600, mdb.kemaskini_angka_dashboard_live)], 
          bg="#2563EB", **btn_form_style).pack(fill="x", pady=3)

tk.Button(frame_control, text="📄 FORM 3: INVOICE LOGS", 
          command=lambda: [fip.buka_borang_invoice(root), root.after(600, mdb.kemaskini_angka_dashboard_live)], 
          bg="#8B5CF6", **btn_form_style).pack(fill="x", pady=3)

frame_db_row = tk.Frame(frame_control, bg="white")
frame_db_row.pack(fill="x", pady=(6, 0))

# 🌟 KOREKSI UTAMA: Agihkan tapak saiz lebar bagi ketiga-tiga lajur secara adil dan seimbang! 🌟
frame_db_row.columnconfigure(0, weight=2)
frame_db_row.columnconfigure(1, weight=2)
frame_db_row.columnconfigure(2, weight=1)

btn_db_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

# Tiga Butang Kawalan Di-gridkan Secara Teratur (Standardized UI Blueprint)
tk.Button(frame_db_row, text="📋 CENTRAL DATABASE PANEL", command=lambda: [dbm.buka_tetingkap_database(root), root.after(600, mdb.kemaskini_angka_dashboard_live)], bg="#DC2626", **btn_db_style).grid(row=0, column=0, padx=(0, 3), sticky="ew")
tk.Button(frame_db_row, text="💾 BACKUP DB", command=lambda: dl.laksanakan_manual_backup_PC(root), bg="#16A34A", **btn_db_style).grid(row=0, column=1, padx=3, sticky="ew")
tk.Button(frame_db_row, text="🛑 SHUTDOWN", command=laksanakan_shutdown_system_selamat, bg="#374151", **btn_db_style).grid(row=0, column=2, padx=(3, 0), sticky="ew")

# ─── SECTION 2: LIVE PRODUCTION DASHBOARD ───
frame_dash = tk.LabelFrame(root, text=" LIVE PRODUCTION DASHBOARD ", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="white", padx=20, pady=8)
frame_dash.pack(fill="both", expand=True, padx=25, pady=(4, 15))

frame_nav = tk.Frame(frame_dash, bg="white")
frame_nav.pack(fill="x", pady=(2, 6))

tk.Button(frame_nav, text="◀ PREV DAY", command=mdb.aksi_butang_prev_day, font=("Segoe UI", 9, "bold"), bg="#E2E8F0", fg="#334155", relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT)
tk.Button(frame_nav, text="NEXT DAY ▶", command=mdb.aksi_butang_next_day, font=("Segoe UI", 9, "bold"), bg="#E2E8F0", fg="#334155", relief="flat", padx=10, cursor="hand2").pack(side=tk.RIGHT)

# True Centering Container
frame_center_container = tk.Frame(frame_nav, bg="white")
frame_center_container.pack(expand=True)  

tk.Button(frame_center_container, text="📅 TODAY", command=mdb.aksi_butang_today, font=("Segoe UI", 9, "bold"), bg="#0284C7", fg="white", relief="flat", padx=12, cursor="hand2").pack(side=tk.LEFT, padx=(0, 5))

# Label Paparan Tarikh Kalendar Dashboard
lbl_tarikh = tk.Label(frame_center_container, text="", font=("Segoe UI", 10, "bold"), fg="#0F172A", bg="white")
lbl_tarikh.pack(side=tk.LEFT, padx=3)

# Butang REFRESH Real-Time Live Dashboard
tk.Button(frame_center_container, text="🔄 REFRESH", command=mdb.kemaskini_angka_dashboard_live, font=("Segoe UI", 8, "bold"), bg="#0D9488", fg="white", relief="flat", padx=6, cursor="hand2").pack(side=tk.LEFT, padx=(5, 0))

# Grid Kuantiti Tiga Kotak Putih Dashboard
frame_grid = tk.Frame(frame_dash, bg="white")
frame_grid.pack(fill="x", pady=6)
frame_grid.columnconfigure(0, weight=1)
frame_grid.columnconfigure(1, weight=1)
frame_grid.columnconfigure(2, weight=1)

box_style = {"bg": "white", "bd": 1, "relief": "solid", "highlightbackground": "#CBD5E1"}
box_inner = tk.Frame(frame_grid, **box_style); box_inner.grid(row=0, column=0, padx=3, sticky="ew")
tk.Label(box_inner, text="INNER STICKERS GENERATED", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="white").pack(pady=(10, 2))
lbl_inner_val = tk.Label(box_inner, text="", font=("Segoe UI", 15, "bold"), bg="white"); lbl_inner_val.pack(pady=(0, 10))

box_outer = tk.Frame(frame_grid, **box_style); box_outer.grid(row=0, column=1, padx=3, sticky="ew")
tk.Label(box_outer, text="OUTER PACKED", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="white").pack(pady=(10, 2))
lbl_outer_boxes_val = tk.Label(box_outer, text="", font=("Segoe UI", 15, "bold"), bg="white"); lbl_outer_boxes_val.pack(pady=(0, 10))

box_invoice = tk.Frame(frame_grid, **box_style); box_invoice.grid(row=0, column=2, padx=3, sticky="ew")
tk.Label(box_invoice, text="INVOICE SHIPPED", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="white").pack(pady=(10, 2))
lbl_invoice_val = tk.Label(box_invoice, text="", font=("Segoe UI", 15, "bold"), bg="white"); lbl_invoice_val.pack(pady=(0, 10))

# ─── SECTION 3: RINGKASAN AKTIVITI LOG HARIAN ───
frame_list_box = tk.Frame(frame_dash, bg="white")
frame_list_box.pack(fill=tk.BOTH, expand=True, pady=(8, 2))

tk.Label(frame_list_box, text="📋  LOGS SUMMARY FOR THE SELECTED DAY:", font=("Segoe UI", 8, "bold"), fg="#475569", bg="white").pack(anchor="w", pady=(0, 5))

gaya_list = ttk.Style()
gaya_list.theme_use('clam') 
gaya_list.configure("SummaryDash.Treeview", rowheight=24, font=("Segoe UI", 9), background="white", fieldbackground="white", borderwidth=0)
gaya_list.configure("SummaryDash.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#1E3A8A", foreground="white", relief="flat")
gaya_list.map("SummaryDash.Treeview.Heading", background=[('active', '#1E40AF')])

lajur_log = ("Time", "Operation Module", "Sequence Number", "Customer Name")
jadual_log_aktiviti = ttk.Treeview(frame_list_box, columns=lajur_log, show="headings", style="SummaryDash.Treeview", height=3)

jadual_log_aktiviti.heading("Time", text="Time")
jadual_log_aktiviti.column("Time", width=95, anchor="center")
jadual_log_aktiviti.heading("Operation Module", text="Operation")
jadual_log_aktiviti.column("Operation Module", width=120, anchor="center")
jadual_log_aktiviti.heading("Sequence Number", text="Sequence No")
jadual_log_aktiviti.column("Sequence Number", width=130, anchor="center")
jadual_log_aktiviti.heading("Customer Name", text="Customer")
jadual_log_aktiviti.column("Customer Name", width=180, anchor="w")

sb_list = ttk.Scrollbar(frame_list_box, orient=tk.VERTICAL, command=jadual_log_aktiviti.yview)
jadual_log_aktiviti.configure(yscrollcommand=sb_list.set)

jadual_log_aktiviti.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
sb_list.pack(side=tk.RIGHT, fill=tk.Y)

# Pautkan elemen visual ke dalam memori fail binder luaran
mdb.siapkan_rujukan_visual_dashboard(lbl_tarikh, lbl_inner_val, lbl_outer_boxes_val, lbl_invoice_val, jadual_log_aktiviti)

# Jalankan kemas kini pertama kali sebaik sahaja sistem dibuka
mdb.kemaskini_angka_dashboard_live()

root.mainloop()
