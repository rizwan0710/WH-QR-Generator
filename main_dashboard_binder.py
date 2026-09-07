import tkinter as tk
from datetime import datetime, timedelta
import sqlite3
import dashboard_logic as dl

# Pemegang tarikh global RAM
tarikh_semasa_dashboard = datetime.now()

# Pemegang rujukan komponen widget UI
v_tarikh, v_inner, v_outer, v_invoice, v_table = None, None, None, None, None

def siapkan_rujukan_visual_dashboard(lbl_t, lbl_i, lbl_o, lbl_inv, table_log):
    """Menyimpan alamat memori komponen widget utama."""
    global v_tarikh, v_inner, v_outer, v_invoice, v_table
    v_tarikh, v_inner, v_outer, v_invoice, v_table = lbl_t, lbl_i, lbl_o, lbl_inv, table_log
    
    # Konfigurasi gaya baris dan logik sorotan hover tetikus di sini
    v_table.tag_configure('baris_normal', background='white', foreground='#1E293B')
    v_table.tag_configure('baris_selang', background='#F1F5F9', foreground='#1E293B')
    v_table.tag_configure('hover', background='#FEF08A', foreground='black')
    v_table.bind("<Motion>", pada_tetikus_melintas)

def pada_tetikus_melintas(event):
    """Kesan sorotan warna kuning sutera lembut apabila tetikus melintas data (Hover Highlight Effect)."""
    if v_table:
        item_id = v_table.identify_row(event.y)
        v_table.tk.call(v_table, "tag", "remove", "hover")
        if item_id:
            # 🌟 FIX MUTTAMAD: Mengasingkan pembacaan tag sebagai tuple dan menggabungkannya dengan cara yang betul 🌟
            tag_sedia_ada = v_table.item(item_id, "tags")
            
            # Pastikan tag_sedia_ada adalah tuple, jika string tukar kepada tuple
            if isinstance(tag_sedia_ada, str):
                tag_sedia_ada = (tag_sedia_ada,) if tag_sedia_ada else ()
            elif not tag_sedia_ada:
                tag_sedia_ada = ()
                
            # Gabungkan kedua-dua tuple dengan selamat tanpa ralat string concatenation
            tag_baru = tuple(tag_sedia_ada) + ("hover",)
            v_table.item(item_id, tags=tag_baru)

def kemaskini_angka_dashboard_live():
    """Mengemaskini teks angka kuantiti sticker dan memuat jadual log skrol harian."""
    global tarikh_semasa_dashboard
    if not v_tarikh: return
    
    # 🌟 FIXED ENGLISH LABELLING: Menukarkan dari "TARIKH:" kepada "DATE:" untuk fungsi live refresh loop 🌟
    v_tarikh.config(text=f"DATE: {tarikh_semasa_dashboard.strftime('%d/%m/%Y')}")
    data_stats = dl.dapatkan_statistik_dashboard_harian(tarikh_semasa_dashboard)
    
    v_inner.config(text=f"{data_stats['inner_stickers']} Stickers", fg="#1E293B")
    v_outer.config(text=f"{data_stats['outer_boxes']} Boxes", fg="#1E293B")
    v_invoice.config(text=f"{data_stats['invoice_logs']} Logs", fg="#1E293B")
    
    for item in v_table.get_children():
        v_table.delete(item)
        
    rekod_aktiviti_hari_ini = dl.dapatkan_senarai_aktiviti_harian(tarikh_semasa_dashboard)
    if not rekod_aktiviti_hari_ini:
        v_table.insert("", tk.END, values=("---", "No transaction recorded for this specific date.", "---", "---"))
    else:
        for idx, log in enumerate(rekod_aktiviti_hari_ini):
            tag_warna = 'baris_normal' if idx % 2 == 0 else 'baris_selang'
            v_table.insert("", tk.END, values=(log[0], log[1], log[2], log[3]), tags=(tag_warna,))

def aksi_butang_prev_day():
    global tarikh_semasa_dashboard
    tarikh_semasa_dashboard -= timedelta(days=1)
    kemaskini_angka_dashboard_live()

def aksi_butang_next_day():
    """🌟 FIX MUTTAMAD ISU NAMEERROR: Mengeluarkan kemaskini_arcade_live() yang tiada 🌟"""
    global tarikh_semasa_dashboard
    tarikh_semasa_dashboard += timedelta(days=1)
    kemaskini_angka_dashboard_live()

def aksi_butang_today():
    global tarikh_semasa_dashboard
    tarikh_semasa_dashboard = datetime.now()
    kemaskini_angka_dashboard_live()

def suntik_masa_asli_ke_mfg_date(sequence_no):
    try:
        waktu_sekarang_str = datetime.now().strftime("%I:%M:%S %p")
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE rekod_qr SET mfg_date = ? WHERE sequence_no = ?", (waktu_sekarang_str, sequence_no))
            conn.commit()
    except Exception: pass
