# 🌟 KOD BAHARU YANG BETUL (DITAMBAH filedialog) 🌟
import os 
import sys
import socket 
import tkinter as tk
from tkinter import messagebox, filedialog, ttk  # <-- Sila selit filedialog di sini!
from datetime import datetime

# Import OHTA Precision Logistics Subsystems
import database_manager as dbm 
import innerbox_form_ui as ifu
import form_outer_packing as fop 
import form_invoice_packing as fip 
import main_dashboard_binder as mdb 

# 1. LOCAL DYNAMIC ENVIRONMENT PATH RESOLUTION
if getattr(sys, 'frozen', False):
    # Running compiled inside a PyInstaller standalone .exe bundle
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running natively from Python source script files environment
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Fetch current hostname profile to map network subfolders dynamically 
try:
    COMPUTER_NAME = socket.gethostname().upper().replace(" ", "_")
except Exception:
    COMPUTER_NAME = "UNKNOWN_STATION"

# Main Application Window Structural Canvas Configuration
root = tk.Tk()
root.title(f"OHTA PRECISION - BARCODE & QR CODE GENERATOR [{COMPUTER_NAME}]")
root.geometry("700x710+380+10")  
root.configure(bg="#F1F5F9")
root.resizable(False, False)

# Initialize local dynamic isolated database system arrays on startup
dbm.siapkan_database()

# AUTOMATIC BACKGROUND STARTUP NAS BACKUP: Runs safely 1 second after UI stabilizes
def trigger_startup_backup():
    try:
        import nas_backup_manager
        nas_backup_manager.laksanakan_backup_ke_nas_async()
    except Exception as e:
        print(f"[STARTUP SYNC NOTICE] System bypassed automated check routine: {e}")

root.after(1000, trigger_startup_backup)

def laksanakan_shutdown_system_selamat():
    """SYSTEM SAFE SHUTDOWN: Ensures clean operational software closure actions."""
    if messagebox.askyesno("CONFIRM SHUTDOWN", "Are you sure you want to securely close and exit the OHTA Precision System?", parent=root):
        try: 
            root.grab_release()
        except:
            pass
        root.quit()
        root.destroy()

def handle_manual_report_generation():
    """
    📊 ENJIN PENJANAAN LAPORAN EXCEL AUTOMATIK (EXCEL REPORT ROUTINE FIX) 100% KALIS RALAT 📊
    Membuka dialog Windows Save As secara automatik untuk mendapatkan laluan fail (laluan_output_excel) 
    sebelum menghantarnya ke enjin excel_generator bagi mengelakkan ralat kekurangan argumen posisi.
    """
    try:
        import excel_generator
        
        # 🌟 PEMBETULAN UTAMA: Buka Windows File Dialog untuk operator pilih lokasi simpanan fail spreadsheet 🌟
        laluan_simpanan_excel = filedialog.asksaveasfilename(
            title="choose file",
            initialfile="data_report.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
            parent=root
        )
        
        # Jika operator menekan butang 'Cancel', batalkan proses pemuatan secara senyap
        if not laluan_simpanan_excel:
            return
            
        # 🚀 Hantar kedua-dua parameter wajib (Laluan Database Asal & Laluan Output Simpanan Pilihan Operator)
        excel_generator.jana_laporan_excel_tiga_tab(dbm.DATABASE_PATH, laluan_simpanan_excel)
        
        # Tunjukkan mesej kejayaan mutlak kepada pihak pengurusan kilang 
        messagebox.showinfo("Export Success", f"Report downloaded at:\n{laluan_simpanan_excel}", parent=root)
        
    except Exception as e:
        messagebox.showerror("Export Failed", f"System reporting engine encountered an operation error context:\n{str(e)}", parent=root)

# Main Corporate Branding Header Panel
tk.Label(root, text="OHTA PRECISION (M) SDN BHD", font=("Segoe UI", 14, "bold"), fg="#1E3A8A", bg="#F1F5F9").pack(pady=(12, 2))
tk.Label(root, text=f"AUTOMATED BARCODE & QR CODE GENERATOR - STATION: {COMPUTER_NAME}", font=("Segoe UI", 9, "bold"), fg="#64748B", bg="#F1F5F9").pack(pady=(0, 6))

# ─── SECTION 1: OPERATIONAL FORM CONTROL PANEL ───
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

frame_db_row.columnconfigure(0, weight=2)
frame_db_row.columnconfigure(1, weight=2)
frame_db_row.columnconfigure(2, weight=1)

btn_db_style = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

# Grid Control Rows Setup Management
tk.Button(frame_db_row, text="📋 CENTRAL DATABASE PANEL", command=lambda: [dbm.buka_tetingkap_database(root), root.after(600, mdb.kemaskini_angka_dashboard_live)], bg="#DC2626", **btn_db_style).grid(row=0, column=0, padx=(0, 3), sticky="ew")

# INTERACTIVE GENERATE REPORT CONTROL BUTTON
tk.Button(frame_db_row, text="📊 GENERATE REPORT", command=handle_manual_report_generation, bg="#16A34A", **btn_db_style).grid(row=0, column=1, padx=3, sticky="ew")

tk.Button(frame_db_row, text="🛑 SHUTDOWN", command=laksanakan_shutdown_system_selamat, bg="#374151", **btn_db_style).grid(row=0, column=2, padx=(3, 0), sticky="ew")

# ─── SECTION 2: LIVE PRODUCTION SUMMARY METRICS DASHBOARD ───
frame_dash = tk.LabelFrame(root, text=" LIVE PRODUCTION DASHBOARD ", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="white", padx=20, pady=8)
frame_dash.pack(fill="both", expand=True, padx=25, pady=(4, 15))

frame_nav = tk.Frame(frame_dash, bg="white")
frame_nav.pack(fill="x", pady=(2, 6))

tk.Button(frame_nav, text="◀ PREV DAY", command=mdb.aksi_butang_prev_day, font=("Segoe UI", 9, "bold"), bg="#E2E8F0", fg="#334155", relief="flat", padx=10, cursor="hand2").pack(side=tk.LEFT)
tk.Button(frame_nav, text="NEXT DAY ▶", command=mdb.aksi_butang_next_day, font=("Segoe UI", 9, "bold"), bg="#E2E8F0", fg="#334155", relief="flat", padx=10, cursor="hand2").pack(side=tk.RIGHT)

frame_center_container = tk.Frame(frame_nav, bg="white")
frame_center_container.pack(expand=True)  

tk.Button(frame_center_container, text="📅 TODAY", command=mdb.aksi_butang_today, font=("Segoe UI", 9, "bold"), bg="#0284C7", fg="white", relief="flat", padx=12, cursor="hand2").pack(side=tk.LEFT, padx=(0, 5))

lbl_tarikh = tk.Label(frame_center_container, text="", font=("Segoe UI", 10, "bold"), fg="#0F172A", bg="white")
lbl_tarikh.pack(side=tk.LEFT, padx=3)

tk.Button(frame_center_container, text="🔄 REFRESH", command=mdb.kemaskini_angka_dashboard_live, font=("Segoe UI", 8, "bold"), bg="#0D9488", fg="white", relief="flat", padx=6, cursor="hand2").pack(side=tk.LEFT, padx=(5, 0))

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

# ─── SECTION 3: REAL-TIME OPERATION LOGS CHRONOLOGY SUMMARY ───
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

# Map visual panel elements reference pointers safely into binder modules memory
mdb.siapkan_rujukan_visual_dashboard(lbl_tarikh, lbl_inner_val, lbl_outer_boxes_val, lbl_invoice_val, jadual_log_aktiviti)
mdb.kemaskini_angka_dashboard_live()

if __name__ == "__main__":
    root.mainloop()
