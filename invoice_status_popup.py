# ==============================================================================
# invoice_status_popup.py - MODUL PENGURUSAN STATUS INVOIS (NORMAL & KALIS ERROR)
# ==============================================================================
import tkinter as tk
from tkinter import ttk, messagebox
import database_manager as dbm

def tukar_status_tetingkap_popup(event, tree_reg, win):
    """Membuka tetingkap popup kecil normal untuk menukar status apabila baris jadual di-klik."""
    item_id = tree_reg.identify_row(event.y)
    
    if item_id:
        nilai_baris = list(tree_reg.item(item_id)['values'])
        if not nilai_baris: 
            return
        
        db_id = nilai_baris[1]
        invoice_no = nilai_baris[2]
        status_sekarang = nilai_baris[7]
        
       # Cipta dialog popup murni
        pop = tk.Toplevel(win)
        pop.title("Update Status")
        pop.geometry("300x150+500+300")
        pop.resizable(False, False)
        pop.transient(win)
        pop.grab_set()
        
        tk.Label(pop, text=f"Invoice: {invoice_no}", font=("Segoe UI", 9, "bold")).pack(pady=10)
        tk.Label(pop, text="Update Status:", font=("Segoe UI", 9)).pack()
        
        cb_status = ttk.Combobox(pop, values=["Pending", "Complete"], state="readonly", width=15)
        cb_status.set(status_sekarang if status_sekarang else "Pending")
        cb_status.pack(pady=5)
        
        def simpan_status_baharu():
            status_baru = cb_status.get()
            if dbm.kemaskini_status_master_invoice(db_id, status_baru):
                tree_reg.set(item_id, "Status Tracking", status_baru)
                pop.destroy()
                messagebox.showinfo("Completed", f"Status Invoice {invoice_no} change to {status_baru}!", parent=win)
        
        tk.Button(pop, text="Submit", command=simpan_status_baharu, bg="#0D9488", fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=10, pady=2).pack(pady=10)
