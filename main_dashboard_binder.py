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
    
    # 🌟 PERLINDUNGAN BATCH REPRINT: Pintasan klik dua kali pada jadual log dashboard 🌟
    v_table.bind("<Double-1>", laksanakan_reprint_pintasan_dashboard)

def laksanakan_reprint_pintasan_dashboard(event):
    """
    🖨️ ENJIN REPRINT DASHBOARD (SAFE TUPLE GUARD) 🖨️
    Mengeluarkan data baris yang diklik secara selamat, mengesan nombor siri log,
    dan menghalang sebarang ralat .save objek tuple semasa pencetakan semula stiker.
    """
    if not v_table: 
        return
        
    item_terpilih = v_table.selection()
    if not item_terpilih: 
        return
        
    nilai_baris = v_table.item(item_terpilih[0], "values")
    if not nilai_baris or nilai_baris[0] == "---": 
        return
        
    # Ambil nombor siri sequence_no dari baris jadual (Indeks ke-2)
    no_siri_seq = str(nilai_baris[2]).strip()
    print(f"⚡ Memicu reprint selamat dari Dashboard untuk No Siri: {no_siri_seq}")
    
    # 🚀 Hubungkan dengan fungsi cetak dari print manager secara default tanpa paksaan tuple
    import form_invoice_packing_logic as f_logic
    import invoice_print_manager as p_mgr
    
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            res = cursor.execute("SELECT customer, drawing_no, part_no, quantity, lotcard_no FROM rekod_qr WHERE sequence_no = ?", (no_siri_seq,)).fetchone()
            
            if res:
                cust, dwg, part, qty, lot = res
                import qrcode
                import label_invoice_designer as lid
                
                qr = qrcode.QRCode(version=1, border=1)
                qr.add_data(no_siri_seq)
                qr.make(fit=True)
                im_qr = qr.make_image()
                
                # Bina objek grafik PIL Image tulen (Bukan tuple)
                stk_img = lid.bina_imej_invoice(
                    img_qr=im_qr, 
                    invoice_no=dwg.replace("INV:", ""), 
                    so_no=part.replace("SO:", ""), 
                    outer_seq=no_siri_seq, 
                    outer_qty=qty, 
                    seq_inv_spesifik=no_siri_seq, 
                    text_paging=lot, 
                    customer=cust
                )
                
                if stk_img:
                    # Hantar objek imej bersih ke enjin cetakan default
                    p_mgr.cetak_a4_master(stk_img)
    except Exception as e:
        print(f"Dashboard reprint guard error: {str(e)}")

def pada_tetikus_melintas(event):
    """Kesan sorotan warna kuning sutera lembut apabila tetikus melintas data (Hover Highlight Effect)."""
    if v_table:
        item_id = v_table.identify_row(event.y)
        v_table.tk.call(v_table, "tag", "remove", "hover")
        if item_id:
            tag_sedia_ada = v_table.item(item_id, "tags")
            
            if isinstance(tag_sedia_ada, str):
                tag_sedia_ada = (tag_sedia_ada,) if tag_sedia_ada else ()
            elif not tag_sedia_ada:
                tag_sedia_ada = ()
                
            tag_baru = tuple(tag_sedia_ada) + ("hover",)
            v_table.item(item_id, tags=tag_baru)

def kemaskini_angka_dashboard_live():
    """Mengemaskini teks angka kuantiti sticker dan memuat jadual log skrol harian."""
    global tarikh_semasa_dashboard
    if not v_tarikh: return
    
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
    except Exception: 
        pass
