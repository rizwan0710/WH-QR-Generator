import tkinter as tk
from tkinter import ttk
import database_edit_manager as dem  
import central_tab_inner_logic as logic  

def bina_tab_inner(tab_inner_frame, frame_top1, root, pratonton_fn, padam_fn):
    tab_inner_frame.configure(bg="white")
    frame_top1.configure(bg="white")
    
    tk.Label(frame_top1, text="Search Inner:", font=("Segoe UI", 10, "bold"), fg="#495057", bg="white").pack(side=tk.LEFT, padx=5)
    entry_search1 = tk.Entry(frame_top1, width=22, font=("Segoe UI", 10), relief="groove")
    entry_search1.pack(side=tk.LEFT, padx=5, ipady=2)
    
    entry_search1.bind("<Button-3>", lambda e: logic.bina_menu_paste_search_global(e, entry_search1, root))
    
    lajur_inner = ("Select", "ID", "Date", "Customer", "Drawing No", "Part No", "Quantity", "Mfg Date", "Machine", "Lotcard No", "Sequence No")
    frame_table1 = tk.Frame(tab_inner_frame, bg="white")
    frame_table1.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    gaya = ttk.Style()
    gaya.configure("CentralInner.Treeview", rowheight=32, font=("Segoe UI", 9), background="white", fieldbackground="white")
    gaya.configure("CentralInner.Treeview.Heading", font=("Segoe UI", 9, "bold"), cursor="hand2")
    
    jadual_inner = ttk.Treeview(frame_table1, columns=lajur_inner, show="headings", selectmode="browse", style="CentralInner.Treeview")
    
    # 🌟 KONFIGURASI TAG WARNA BARIS GRED PREMIUM 🌟
    jadual_inner.tag_configure('normal', background='white', foreground='black')
    jadual_inner.tag_configure('hover', background='#E8F0FE', foreground='black') # Biru Lembut
    jadual_inner.tag_configure('checked', background='#E8F5E9', foreground='#1B5E20') # Hijau Lembut Korporat
    
    entry_search1.bind("<Return>", lambda e: logic.carian_inner(jadual_inner, entry_search1))
    
    # ─── BARISAN BUTANG KAWALAN KIRI ───
    tk.Button(frame_top1, text="SEARCH", command=lambda: logic.carian_inner(jadual_inner, entry_search1), bg="#0D6EFD", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(frame_top1, text="RESET", command=lambda: [entry_search1.delete(0, tk.END), logic.carian_inner(jadual_inner, entry_search1)], bg="#6C757D", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(frame_top1, text="PREVIEW SELECTED", command=lambda: pratonton_fn(jadual_inner, root, is_outer=False), bg="#198754", fg="white", font=("Segoe UI", 9, "bold"), width=18, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    tk.Button(frame_top1, text="EDIT SELECTED", command=lambda: dem.buka_popup_edit(root, jadual_inner, entry_search1, 1), bg="#FD7E14", fg="white", font=("Segoe UI", 9, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(frame_top1, text="DELETE SELECTED", command=lambda: padam_fn(jadual_inner, entry_search1, is_outer=False), bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold"), width=15, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(frame_top1, text="📥 EXPORT CSV", command=logic.eksport_inner_excel, bg="#212529", fg="white", font=("Segoe UI", 9, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    
    # ─── 🌟 KANAN SEKALI: REFRESH DI SEBELAH LEFT BUTTON BACK TO MAIN 🌟 ───
    tk.Button(frame_top1, text="◀ BACK TO MAIN", command=root.destroy, bg="#6C757D", fg="white", font=("Segoe UI", 9, "bold"), width=16, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=5)
    tk.Button(frame_top1, text="🔄 REFRESH", command=lambda: logic.carian_inner(jadual_inner, entry_search1), bg="#0D9488", fg="white", font=("Segoe UI", 9, "bold"), width=11, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=2)
    
    jadual_inner.bind("<Button-1>", lambda e: logic.on_inner_click(e, jadual_inner))
    jadual_inner.bind("<Button-3>", lambda e: logic.bina_menu_klik_kanan_global(e, jadual_inner, root))
    jadual_inner.bind("<Motion>", lambda e: logic.on_mouse_hover(e, jadual_inner))
    jadual_inner.bind("<Leave>", lambda e: logic.on_mouse_leave(e, jadual_inner))
    
    for col in lajur_inner:
        jadual_inner.heading(col, text=col, command=lambda c=col: logic.susun_lajur_treeview(jadual_inner, c, True))
        jadual_inner.column(col, width=95, anchor="center")
        
    jadual_inner.column("Select", width=50); jadual_inner.column("ID", width=40); jadual_inner.column("Customer", width=140, anchor="w"); jadual_inner.column("Sequence No", width=130)
    
    sb1 = ttk.Scrollbar(frame_table1, orient=tk.VERTICAL, command=jadual_inner.yview)
    jadual_inner.configure(yscrollcommand=sb1.set)
    jadual_inner.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb1.pack(side=tk.RIGHT, fill=tk.Y)
    
    logic.carian_inner(jadual_inner, entry_search1)
