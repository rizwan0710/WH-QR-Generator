import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import form_outer_packing_logic as logic  # Menghubungkan ke logik backend

def buka_borang_outer(root):
    """🌟 OPTIMIZED OUTER FORM UI WITH WP PREFIX VALIDATION LOCK 🌟"""
    win_outer = tk.Toplevel(root)
    win_outer.title("FORM 2: OUTER PACKING ")
    win_outer.geometry("540x640+450+50")
    win_outer.configure(bg="#F8F9FA")
    win_outer.resizable(False, False)
    win_outer.grab_set()

    # Pengepala Borang Visual
    tk.Label(win_outer, text="OUTER PACKING FORM", font=("Segoe UI", 13, "bold"), fg="#1E3A8A", bg="#F8F9FA").pack(pady=(15, 2))
    tk.Label(win_outer, text="ENTER PRODUCTION DETAILS PRECISELY:", font=("Segoe UI", 9, "italic"), fg="#64748B", bg="#F8F9FA").pack(pady=(0, 10))

    # Bingkai Kemasukan Data Utama
    frame_data_entry = tk.LabelFrame(win_outer, text=" DATA ENTRY ", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="#F8F9FA", padx=25, pady=10)
    frame_data_entry.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 15))

    lbl_style = {"font": ("Segoe UI", 9, "bold"), "fg": "#334155", "bg": "#F8F9FA", "width": 20, "anchor": "w"}
    ent_style = {"font": ("Segoe UI", 10), "relief": "groove", "bd": 1}

    # Slot 1: Date Created
    frame_row1 = tk.Frame(frame_data_entry, bg="#F8F9FA")
    frame_row1.pack(fill=tk.X, pady=4)
    tk.Label(frame_row1, text="Date Created :", **lbl_style).pack(side=tk.LEFT)
    entry_date = DateEntry(frame_row1, width=30, font=("Segoe UI", 10), background="#0D6EFD", foreground="white", borderwidth=1, date_pattern="dd/mm/yyyy")
    entry_date.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=1)

    # Membina 4 Slot Kemasukan Sequence Bersiri
    entries_inner = []
    for i in range(1, 5):
        frame_row = tk.Frame(frame_data_entry, bg="#F8F9FA")
        frame_row.pack(fill=tk.X, pady=4)
        tk.Label(frame_row, text=f"Inner Box Sequence {i} :", **lbl_style).pack(side=tk.LEFT)
        ent = tk.Entry(frame_row, **ent_style)
        ent.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        entries_inner.append(ent)

    # ─── 🌟 LOGIK KAWALAN ENJIN ALIH FOKUS DENGAN PENAPIS KEPALA KOD WP 🌟 ───
    def alih_focus_ke_kotak_seterusnya(event, idx):
        """Menguruskan lompatan fokus tetikus secara berperingkat selepas pengesahan prefix WP."""
        kod_imbas = entries_inner[idx].get().strip().upper()
        
        # JIKA KOD BAR KOSONG
        if not kod_imbas:
            return

        # ─── 🔒 LOCK SECURITY: SEKAT KOD BAR SELAIN WP% SECARA AGRESIF 🔒 ───
        if not kod_imbas.startswith("WP"):
            messagebox.showerror(
                "❌ QR CODE RESTRICTION ",
                f"ENTRY DENIED!\n\n"
                f"SCANNED CODE: [{kod_imbas}]\n"
                f"WRONG TYPE OF QR CODE.\n\n"
                f"PLEASE SCANNED CORRECT QR!",
                parent=win_outer
            )
            # Padam input salah serta-merta dan paksa fokus tetap di kotak yang sama
            entries_inner[idx].delete(0, tk.END)
            entries_inner[idx].focus_set()
            return "break"

        # JIKA KOD SAH (BERMULA DENGAN WP), BERIKAN LOMPATAN FOKUS STRATEGIK
        if idx < 3:
            # Jika kotak 1, 2, atau 3 discan, bawa fokus ke kotak di bawahnya
            entries_inner[idx + 1].focus_set()
        else:
            # Jika kotak terakhir (Sequence 4) discan, bawa fokus ke butang SUBMIT utama sahaja
            btn_submit.focus_set()

    # Mengikat gelung kekunci Return (Enter) untuk setiap slot input
    for i in range(4):
        entries_inner[i].bind("<Return>", lambda e, idx=i: alih_focus_ke_kotak_seterusnya(e, idx))

    # Fungsi Reset Isian Borang
    def cuci_isian():
        for ent in entries_inner:
            ent.delete(0, tk.END)
        entries_inner[0].focus_set()

    # ─── DEKLARASI BUTANG SUBMIT UTAMA ───
    btn_submit = tk.Button(win_outer, text="SUBMIT & GENERATE OUTER QR", 
                           command=lambda: logic.proses_submit_outer(win_outer, entry_date, entries_inner), 
                           bg="#007ACC", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2")
    btn_submit.pack(fill="x", padx=30, pady=(0, 4))

    # Barisan Butang Aksi Bawah
    frame_action_bar = tk.Frame(win_outer, bg="#F8F9FA")
    frame_action_bar.pack(fill="x", padx=30, pady=(0, 20))
    frame_action_bar.columnconfigure(0, weight=1)
    frame_action_bar.columnconfigure(1, weight=1)

    tk.Button(frame_action_bar, text="🔄 RESET", command=cuci_isian, bg="#6C757D", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").grid(row=0, column=0, padx=(0, 3), sticky="ew")
    tk.Button(frame_action_bar, text="◀ BACK", command=win_outer.destroy, bg="#212529", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", height=2, cursor="hand2").grid(row=0, column=1, padx=(3, 0), sticky="ew")

    entries_inner[0].focus_set()
