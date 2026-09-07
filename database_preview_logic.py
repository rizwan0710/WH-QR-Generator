import tkinter as tk
from tkinter import messagebox

def pratonton_terpilih(jadual, root, is_outer=False, is_invoice=False):
    """Menguruskan fungsi agihan butang pratinjau tunggal (single) dan pukal (bulk) - 100% FIX TOTAL."""
    semua_item = jadual.get_children()
    item_ditanda = []
    
    # Membaca data baris berdasarkan rekod yang ditanda rait [☑]
    for i in semua_item:
        nilai = jadual.item(i)['values']
        if nilai and len(nilai) > 0 and "☑" in str(nilai):
            item_ditanda.append(nilai)
            
    if not item_ditanda:
        messagebox.showwarning("REMINDER", "PLEASE CHECK BOX [☐] FOR CHOOSING DATA!", parent=root)
        return
        
    # ─── SECTION A: BATCH MULTI-PREVIEW (PILIHAN > 1 DATA) ───
    if len(item_ditanda) > 1:
        if is_invoice:
            import central_tab_invoice_wizard as ctiv_wiz
            ctiv_wiz.buka_popup_pukal_invoice_1by1(item_ditanda, root)
        elif is_outer:
            import central_tab_outer_wizard as ctow
            ctow.buka_popup_pukal_outer_1by1(item_ditanda, root)
        else:
            import central_tab_inner_wizard as ctiw
            ctiw.buka_popup_pukal_inner_1by1(item_ditanda, root)
        return

    # ─── SECTION B: SINGLE PREVIEW (PILIHAN == 1 DATA SAHAJA) ───
    # 🌟 KOREKSI TOTAL: Menggunakan item_ditanda[0] untuk mengubah nested list [[...]] menjadi flat list [...] 🌟
    baris_pilihan = item_ditanda[0]
    
    # Menembak terus data flat list yang telah dibersihkan ke enjin pelakar RAM (database_preview_render.py)
    import database_preview_render as dpr
    if is_invoice:
        dpr.bina_single_invoice_preview(baris_pilihan, root)
    elif is_outer:
        dpr.bina_single_outer_preview(baris_pilihan, root)
    else:
        dpr.bina_single_inner_preview(baris_pilihan, root)
