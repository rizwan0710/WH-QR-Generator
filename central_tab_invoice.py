import tkinter as tk
from tkinter import ttk
import database_edit_manager as dem
import invoice_tab_logic as logic
import central_tab_inner_logic as inner_logic

def bina_tab_invoice(tab_invoice_frame, frame_top3, root, pratonton_fn, padam_fn):
    tab_invoice_frame.configure(bg="white")
    frame_top3.configure(bg="white")
    
    tk.Label(frame_top3, text="Search Invoice:", font=("Segoe UI", 10, "bold"), fg="#495057", bg="white").pack(side=tk.LEFT, padx=5)
    entry_search3 = tk.Entry(frame_top3, width=22, font=("Segoe UI", 10), relief="groove")
    entry_search3.pack(side=tk.LEFT, padx=5, ipady=2)
    
    entry_search3.bind("<Button-3>", lambda e: inner_logic.bina_menu_paste_search_global(e, entry_search3, root))
    
    lajur_invoice = ("Select", "ID", "Date", "Customer", "Invoice No", "SO No", "Quantity", "Page Status", "Linked Outer Box", "Box Type", "Invoice Sequence No")
    frame_table3 = tk.Frame(tab_invoice_frame, bg="white")
    frame_table3.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    gaya = ttk.Style()
    gaya.configure("CentralInvoice.Treeview", rowheight=78, font=("Segoe UI", 9), background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#212529")
    gaya.configure("CentralInvoice.Treeview.Heading", font=("Segoe UI", 9, "bold"), cursor="hand2")
    
    jadual_invoice = ttk.Treeview(frame_table3, columns=lajur_invoice, show="headings", selectmode="browse", style="CentralInvoice.Treeview")
    
    # 🌟 TREEVIEW ROW TAG CONFIGURATIONS
    jadual_invoice.tag_configure('normal', background='white', foreground='black')
    jadual_invoice.tag_configure('hover', background='#E8F0FE', foreground='black')
    jadual_invoice.tag_configure('checked', background='#E8F5E9', foreground='#1B5E20') # Soft Corporate Green
    
    entry_search3.bind("<Return>", lambda e: logic.carian_invoice(jadual_invoice, entry_search3))
    
    # ─── LEFT SIDE WORKFLOW BUTTONS ───
    tk.Button(frame_top3, text="SEARCH", command=lambda: logic.carian_invoice(jadual_invoice, entry_search3), bg="#0D6EFD", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(frame_top3, text="RESET", command=lambda: [entry_search3.delete(0, tk.END), logic.carian_invoice(jadual_invoice, entry_search3)], bg="#6C757D", fg="white", font=("Segoe UI", 9, "bold"), width=9, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    
    # Standardized green matching production inner layout
    tk.Button(frame_top3, text="PREVIEW SELECTED", command=lambda: pratonton_fn(jadual_invoice, root, is_invoice=True), bg="#198754", fg="white", font=("Segoe UI", 9, "bold"), width=18, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    # Standardized orange matching production inner layout
    tk.Button(frame_top3, text="EDIT SELECTED", command=lambda: dem.buka_popup_edit(root, jadual_invoice, entry_search3, 3), bg="#FD7E14", fg="white", font=("Segoe UI", 9, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    tk.Button(frame_top3, text="DELETE SELECTED", command=lambda: padam_fn(jadual_invoice, entry_search3, is_invoice=True), bg="#DC3545", fg="white", font=("Segoe UI", 9, "bold"), width=15, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    
    # Standardized charcoal black for structural/export tasks
    tk.Button(frame_top3, text="EXPORT CSV", command=logic.eksport_invoice_excel, bg="#212529", fg="white", font=("Segoe UI", 9, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=3)
    
    # ─── RIGHT SIDE NAVIGATION CONTROL BUTTONS ───
    tk.Button(frame_top3, text="BACK TO MAIN", command=root.destroy, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=16, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=5)
    tk.Button(frame_top3, text="REFRESH", command=lambda: logic.carian_invoice(jadual_invoice, entry_search3), bg="#0D9488", fg="white", font=("Segoe UI", 9, "bold"), width=11, relief="flat", cursor="hand2").pack(side=tk.RIGHT, padx=2)
    
    jadual_invoice.bind("<Button-1>", lambda e: logic.on_invoice_click(e, jadual_invoice))
    jadual_invoice.bind("<Button-3>", lambda e: inner_logic.bina_menu_klik_kanan_global(e, jadual_invoice, root))
    jadual_invoice.bind("<Motion>", lambda e: logic.on_mouse_hover(e, jadual_invoice))
    jadual_invoice.bind("<Leave>", lambda e: logic.on_mouse_leave(e, jadual_invoice))
    
    for col in lajur_invoice:
        jadual_invoice.heading(col, text=col, command=lambda c=col: logic.susun_lajur_treeview(jadual_invoice, c, True))
        jadual_invoice.column(col, width=95, anchor="center")
        
    jadual_invoice.column("Select", width=50); jadual_invoice.column("ID", width=40); jadual_invoice.column("Customer", width=140, anchor="w"); jadual_invoice.column("Invoice Sequence No", width=130); jadual_invoice.column("Linked Outer Box", width=220, anchor="w") 
    sb3 = ttk.Scrollbar(frame_table3, orient=tk.VERTICAL, command=jadual_invoice.yview)
    jadual_invoice.configure(yscrollcommand=sb3.set)
    jadual_invoice.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb3.pack(side=tk.RIGHT, fill=tk.Y)
    logic.carian_invoice(jadual_invoice, entry_search3)
