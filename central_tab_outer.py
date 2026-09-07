import tkinter as tk
from tkinter import ttk
import database_edit_manager as dem
import central_tab_outer_logic as logic
import central_tab_inner_logic as inner_logic

def bina_tab_outer(tab_outer_frame, frame_top2, root, pratonton_fn, padam_fn):
    """🌟 RE-LAYOUT: Butang REFRESH disuntik di sebelah kiri butang BACK (Kanan Sekali) 🌟"""
    tab_outer_frame.configure(bg="white")
    frame_top2.configure(bg="white")
    
    tk.Label(frame_top2, text="Cari Outer:", font=("Segoe UI", 10, "bold"), fg="#495057", bg="white").pack(side=tk.LEFT, padx=5)
    entry_search2 = tk.Entry(frame_top2, width=22, font=("Segoe UI", 10), relief="groove")
    entry_search2.pack(side=tk.LEFT, padx=5, ipady=2)
    
    entry_search2.bind("<Button-3>", lambda e: inner_logic.bina_menu_paste_search_global(e, entry_search2, root))
    
    lajur_outer = ("Select", "ID", "Date", "Customer", "Quantity", "Mfg Date", "Linked Inner Sequences", "Box Type", "Outer Sequence No")
    frame_table2 = tk.Frame(tab_outer_frame, bg="white")
    frame_table2.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    gaya = ttk.Style()
    gaya.configure("CentralOuter.Treeview", rowheight=78, font=("Segoe UI", 9), background="white", fieldbackground="white") 
    gaya.configure("CentralOuter.Treeview.Heading", font=("Segoe UI", 9, "bold"), cursor="hand2")
    
    jadual_outer = ttk.Treeview(frame_table2, columns=lajur_outer, show="headings", selectmode="browse", style="CentralOuter.Treeview")
    
    jadual_outer.tag_configure('normal', background='white', foreground='black')
    jadual_outer.tag_configure('hover', background='#E8F0FE', foreground='black')
    jadual_outer.tag_configure('checked', background='#E8F5E9', foreground='#1B5E20') 
    
    entry_search2.bind("<Return>", lambda e: logic.carian_outer(jadual_outer, entry_search2))
    
    # Kiri: Butang Kawalan Carian & Aksi
    tk.Button(frame_top2, text="SEARCH", command=lambda: logic.carian_outer(jadual_outer, entry_search2), bg="#0D6EFD", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    tk.Button(frame_top2, text="RESET", command=lambda: [entry_search2.delete(0, tk.END), logic.carian_outer(jadual_outer, entry_search2)], bg="#6C757D", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    tk.Button(frame_top2, text="PREVIEW SELECTED", command=lambda: pratonton_fn(jadual_outer, root, is_outer=True), bg="#198754", fg="white", font=("Segoe UI", 9, "bold"), width=18, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=10)
    tk.Button(frame_top2, text="EDIT SELECTED", command=lambda: dem.buka_popup_edit(root, jadual_outer, entry_search2, 2), bg="#FD7E14", fg="white", font=("Segoe UI", 9, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    tk.Button(frame_top2, text="DELETE SELECTED", command=lambda: padam_fn(jadual_outer, entry_search2, is_outer=True), bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold"), width=15, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    tk.Button(frame_top2, text="📥 EXPORT CSV", command=logic.eksport_outer_excel, bg="#212529", fg="white", font=("Segoe UI", 9, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=2)
    
    # 🌟 KANAN SEKALI: Susunan Bersifat Rapat ke Kanan (Refresh di sebelah Kiri Back) 🌟
    tk.Button(frame_top2, text="◀ BACK TO MAIN", command=root.destroy, bg="#475569", fg="white", font=("Segoe UI", 9, "bold"), width=16, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=5)
    tk.Button(frame_top2, text="🔄 REFRESH", command=lambda: logic.carian_outer(jadual_outer, entry_search2), bg="#0D9488", fg="white", font=("Segoe UI", 9, "bold"), width=11, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=2)
    
    jadual_outer.bind("<Button-1>", lambda e: logic.on_outer_click(e, jadual_outer))
    jadual_outer.bind("<Button-3>", lambda e: inner_logic.bina_menu_klik_kanan_global(e, jadual_outer, root))
    jadual_outer.bind("<Motion>", lambda e: logic.on_mouse_hover(e, jadual_outer))
    jadual_outer.bind("<Leave>", lambda e: logic.on_mouse_leave(e, jadual_outer))
    
    for col in lajur_outer:
        jadual_outer.heading(col, text=col, command=lambda c=col: logic.susun_lajur_treeview(jadual_outer, c, True))
        jadual_outer.column(col, width=110, anchor="center")
    
    jadual_outer.column("Select", width=50)
    jadual_outer.column("ID", width=40)
    jadual_outer.column("Customer", width=140, anchor="w")
    jadual_outer.column("Outer Sequence No", width=130)
    jadual_outer.column("Linked Inner Sequences", width=220, anchor="w") 
    
    sb2 = ttk.Scrollbar(frame_table2, orient=tk.VERTICAL, command=jadual_outer.yview)
    jadual_outer.configure(yscrollcommand=sb2.set)
    jadual_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb2.pack(side=tk.RIGHT, fill=tk.Y)
    
    logic.carian_outer(jadual_outer, entry_search2)
