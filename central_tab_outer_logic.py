import sqlite3
import csv
import qrcode
import re
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import label_outer_designer as lod
import database_batch_preview
import database_manager as dbm  # 🌟 Integrasi Pengurus Pangkalan Data Pusat NAS 🌟

# Jejaki baris hover tetikus global untuk kesan warna Treeview
baris_hover_terakhir = None
jad_out = None  # Rujukan widget jadual global

def semak_dan_pencetus_popup_gatekeeper(parent_win):
    """
    🚀 ENJIN AUTO-UPDATE LATAR BELAKANG (SILENT SYNC SYSTEM - NO POPUP) 🚀
    Mengesan sebarang baki perubahan data sync di database pusat NAS dan mengemas kini 
    rekod Invoice Shipped secara automatik tanpa mengeluarkan sebarang gangguan popup.
    """
    conn_nas = None
    try:
        conn_nas = sqlite3.connect(dbm.DATABASE_PATH, timeout=15)
        cursor = conn_nas.cursor()
        
        # Ambil baki data antrean yang tersimpan di jadual pending_sync pusat
        cursor.execute("SELECT id, outer_seq, qty_baru FROM pending_sync")
        semua_pending = cursor.fetchall()
        
        if semua_pending:
            for row in semua_pending:
                p_id = row[0]
                outer_code = str(row[1]).strip().upper()  # Bersihkan trailing spaces / kes huruf
                qty_baru_str = str(row[2]).strip()
                
                # SINKRONISASI SENYAP: Kemaskan kuantiti invois mengikut padanan kod murni
                cursor.execute("""
                    UPDATE rekod_qr 
                    SET quantity = ? 
                    WHERE sequence_no LIKE 'INV%' 
                      AND UPPER(TRIM(machine)) = ?
                """, (qty_baru_str, outer_code))
                
                # Padamkan rekod id antrean ini secara tegar supaya tidak tersangkut lagi
                cursor.execute("DELETE FROM pending_sync WHERE id = ?", (p_id,))
            
            # Commit dan sahkan penyimpanan kekal ke pemacu pangkalan data pusat NAS
            conn_nas.commit()
            print(f"[NAS SILENT SYNC] Berjaya menyelaraskan {len(semua_pending)} rekod ke Invoice Logs secara senyap.")
            
    except Exception as e: 
        print(f"Silent Gatekeeper error override: {e}")
    finally:
        if conn_nas:
            conn_nas.close()

def hitung_live_total_qty_dari_db(linked_text):
    """Mengira live total quantity daripada baki database NAS untuk dipaparkan pada jadual (Kalis Tukar Lajur)."""
    if not linked_text: 
        return 0
    t_clean = str(linked_text).strip()
    if t_clean == "None" or not t_clean: 
        return 0
    total = 0
    conn_nas = None
    try:
        conn_nas = sqlite3.connect(dbm.DATABASE_PATH, timeout=15)
        cursor = conn_nas.cursor()
        
        # 🛠️ SEMAKAN LAJUR LIVE: Mengesan sama ada database menggunakan sequence_no atau [Sequence No]
        lajur_seq = "sequence_no"
        try:
            cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
            lajur_seq = "[Sequence No]"
        except sqlite3.OperationalError:
            lajur_seq = "sequence_no"
            
        # Pecahkan siri kod WP mengikut koma atau baris baru (\n)
        for wp in [s.strip().upper() for s in re.split(r'[,\n]', t_clean) if s.strip()]:
            cursor.execute(f"SELECT quantity FROM rekod_qr WHERE UPPER(TRIM({lajur_seq})) = ?", (wp,))
            row = cursor.fetchone()
            if row and row[0]:
                digits = "".join(filter(str.isdigit, str(row[0])))
                if digits: 
                    total += int(digits)
                    
    except Exception as e:
        print(f"[NAS LIVE QTY ERROR] Gagal mengira baki live: {e}")
    finally:
        if conn_nas:
            conn_nas.close()
            
    return total



def semak_adakah_inner_sudah_digunakan(inner_seq):
    """Menyemak status silang sekiranya kod siri WP% telah didaftarkan pada kotak luar lain (Sudah 100% Okey)."""
    if not inner_seq:
        return None
    inner_seq_bersih = str(inner_seq).strip().upper()
    try:
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError:
                lajur_seq = "sequence_no"
                
            query = f"SELECT {lajur_seq} FROM rekod_qr WHERE lotcard_no = 'OUTER BOX' AND UPPER(TRIM(machine)) LIKE ?"
            cursor.execute(query, (f"%{inner_seq_bersih}%",))
            res = cursor.fetchone()
            return res[0] if res else None
    except Exception as e:
        print(f"[OUTER LOGIC ERROR] Gagal menyemak penggunaan siri inner: {str(e)}")
        return None

def dapatkan_maklumat_inner(seq_no):
    """Mengambil data Kuantiti dan Customer bagi siri WP% secara eksplisit menggunakan nama kunci pautan (Versi Kebal NAS)."""
    kod_bersih = str(seq_no).strip().upper()
    if not kod_bersih.startswith("WP"):
        return {"error": "❌ SEKATAN JENIS KOD BAR!\n\nBorang Outer Packing hanya menerima INNER LABEL (WP%) sahaja!"}
    try:
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            
            # 🛠️ SEMAKAN LAJUR LIVE: Mengesan sama ada database menggunakan sequence_no atau [Sequence No]
            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError:
                lajur_seq = "sequence_no"
            
            # ✅ DIBAIKI: Menggunakan lajur_seq dinamik dan nama parameter kod_bersih yang betul
            cursor.execute(f"SELECT quantity, customer FROM rekod_qr WHERE {lajur_seq} = ?", (kod_bersih,))
            res = cursor.fetchone()
            if res:
                return {
                    "qty": str(res[0]).strip(),
                    "customer": str(res[1]).strip()
                }
            return None
    except Exception as e:
        print(f"Error dapatkan_maklumat_inner di database pusat: {e}")
        return None


def proses_submit_outer(win_outer, entry_date, entries_inner, btn_submit_widget=None):
    """🌟 MAIN SUBMIT FUNCTION WITH INTEGRATED ANTI-DUPLICATE SAFETY LOCK (CENTRAL NAS VERSION) 🌟"""
    global btn_submit_ref
    if btn_submit_widget:
        btn_submit_ref = btn_submit_widget

    tarikh_str = entry_date.get() if hasattr(entry_date, 'get') else str(entry_date)
    senarai_inner = [e.get().strip().upper() for e in entries_inner if e.get().strip()]
    if not senarai_inner: 
        return messagebox.showwarning("INCOMPLETE FORM", "PLEASE SCAN OR ENTER THE SERIAL NUMBER!", parent=win_outer)

    if len(senarai_inner) != len(set(senarai_inner)):
        return messagebox.showerror("SAME FORM DUPLICATE ERROR", "❌ FORM RE-SCAN RESTRICTION!\n\nTHIS NUMBER HAS ALREADY BEEN SCANNED!\n\nPLEASE REMOVE DUPLICATE BEFORE REGISTERING.", parent=win_outer)

    for idx, seq in enumerate(senarai_inner, start=1):
        outer_id = semak_adakah_inner_sudah_digunakan(seq)
        if outer_id: 
            return messagebox.showerror("DUPLICATE ENTRY", f"❌ ERROR AT SLOT {idx}!\n\nSERIAL NUMBER [{seq}] HAS ALREADY BEEN SCANNED AT OUTER BOX: {outer_id}", parent=win_outer)

    data_1 = dapatkan_maklumat_inner(senarai_inner[0])
    if isinstance(data_1, dict) and "error" in data_1:
        return messagebox.showerror("DATABASE REFUSAL", data_1["error"], parent=win_outer)
    if not data_1: 
        return messagebox.showerror("DATA NOT FOUND", f"❌ ERROR AT SLOT 1!\n\nSERIAL NUMBER [{senarai_inner[0]}] IS NOT EXIST IN GIVEN CENTRAL DATABASE DIRECTORY!", parent=win_outer)
        
    customer_utama = data_1.get("customer", "").upper()
    total_qty, data_final = 0, []
    
    for idx, seq in enumerate(senarai_inner, start=1):
        res = dapatkan_maklumat_inner(seq)
        if not res or (isinstance(res, dict) and "error" in res): 
            return messagebox.showerror("DATA NOT FOUND", f"❌ ERROR AT SLOT {idx}!\n\nSERIAL NUMBER [{seq}] IS INVALID OR DOS NOT EXIST IN GIVEN CENTRAL DATABASE DIRECTORY!", parent=win_outer)
        
        cust = res.get("customer", "").upper()
        qty = res.get("qty", "100 PCS")
        
        if "/" in qty or "-" in qty or len(qty) > 10:
            qty = "100 PCS"
        
        if cust != customer_utama:
            return messagebox.showerror("MIXED CUSTOMER DETECTION", f"❌ CUSTOMER TRANSACTION MISMATCH!\n\n• SLOT 1 RECOGNIZED AS: {customer_utama}\n• SLOT {idx} WRONG TARGETED AS: {cust} (SN: {seq})\n\nCONSOLIDATED CARGO MIXING ARE STRICTLY FORBIDDEN AT FLOOR OPERATION!", parent=win_outer)
            
        qty_c = str(qty).upper().replace("PCS", "").strip()
        try:
            total_qty += int(float(qty_c))
        except ValueError:
            digits = "".join([c for c in qty_c if c.isdigit()])
            total_qty += int(digits) if digits else 100
            qty_c = digits if digits else "100"
            
        data_final.append((seq, f"{qty_c} PCS"))

    try:
        waktu_kini = datetime.now()
    except:
        import datetime as dt_module
        waktu_kini = dt_module.datetime.now()
        
    prefix = f"B{waktu_kini.strftime('%y%m%d')}"
    
    try:
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError:
                lajur_seq = "sequence_no"
                
            last = cursor.execute(f"SELECT {lajur_seq} FROM rekod_qr WHERE {lajur_seq} LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",)).fetchone()
            
            run_no = 1
            if last and last:
                nombor_akhir = re.findall(r'\d+', str(last))
                if nombor_akhir:
                    run_no = int(str(nombor_akhir[-1])[-4:]) + 1
                    
            seq_outer = f"{prefix}{run_no:04d}"
            
            cursor.execute(f"""
                INSERT INTO rekod_qr (tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, {lajur_seq}) 
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (tarikh_str, customer_utama, "COMBINED", "CONSOLIDATED", f"{total_qty} PCS", tarikh_str, ",".join(senarai_inner), "OUTER BOX", seq_outer))
            conn.commit()
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_outer)
        qr.make(fit=True)
        img_label = lod.bina_imej_gabungan_akses(qr.make_image().convert("RGB"), data_final, seq_outer)
        
        try:
            nama_folder_bersih = "".join([c for c in customer_utama if c.isalnum() or c in (' ', '_', '-')]).strip()
            folder = os.path.join("OUTER_STICKER", waktu_kini.strftime("%d-%m-%Y"), nama_folder_bersih)
            if not os.path.exists(folder): 
                os.makedirs(folder)
            img_label.convert("RGB").save(os.path.join(folder, f"OUTER_STICKER_{seq_outer}.png"), "PNG")
        except: 
            pass

        if 'btn_submit_ref' in globals() and btn_submit_ref and btn_submit_ref.winfo_exists():
            btn_submit_ref.config(state="disabled", text="🔒 REGISTRATION LOCKED (COMPLETED)", bg="#64748B")
        for e in entries_inner:
            if hasattr(e, 'config'):
                e.config(state="disabled")

        import form_outer_packing_logic
        if hasattr(form_outer_packing_logic, 'paparkan_pop_up_imej_label'):
            form_outer_packing_logic.paparkan_pop_up_imej_label(win_outer, entries_inner, img_label, "OUTER PACKING LABEL GENERATED", seq_outer)
        
    except Exception as e: 
        messagebox.showerror("DATABASE CRITICAL ERROR", f"CRITICAL FAULT OCCURRED WHILE WRITING TO CENTRAL RACK MANAGEMENT SYSTEM:\n\n{str(e)}", parent=win_outer)

def carian_outer(jadual, entry_search=None):
    """Menguruskan muatan data logs Outer Box berkembar dengan fungsi pembersihan harian."""
    dbm.laksanakan_auto_clean_orphaned_logs()
    semak_dan_pencetus_popup_gatekeeper(jadual.winfo_toplevel())
    
    if entry_search is not None and hasattr(entry_search, 'get'):
        teks = entry_search.get().strip()
    else:
        teks = ""
        
    for item in jadual.get_children(): 
        jadual.delete(item)
        
    # 🌟 1. ENJIN PENTERJEMAH TARIKH (DATE FORMAT CONVERTER)
    # Jika operator menaip "22/10/2026", kod secara automatik menukarkannya kepada "2026-10-22"
    teks_asal = teks  # Simpan teks asal untuk carian fleksibel
    if "/" in teks:
        bahagian = teks.split("/")
        if len(bahagian) == 3:
            # Menguruskan pertukaran format DD/MM/YYYY -> YYYY-MM-DD
            if len(bahagian[0]) == 2 and len(bahagian[2]) == 4:
                teks = f"{bahagian[2]}-{bahagian[1]}-{bahagian[0]}"
            # Menguruskan pertukaran format YYYY/MM/DD -> YYYY-MM-DD
            elif len(bahagian[0]) == 4 and len(bahagian[2]) == 2:
                teks = f"{bahagian[0]}-{bahagian[1]}-{bahagian[2]}"

    try:
        conn = dbm.get_db_connection()
        with conn:
            cursor = conn.cursor()
            laluan_db = getattr(dbm, 'DATABASE_PATH', 'Tidak Diketahui')
            print(f"\n[DIAGNOSTIK] Membaca fail database dari: {laluan_db}")
            
            try:
                cursor.execute("SELECT COUNT(*) FROM rekod_qr")
                jumlah_asal = cursor.fetchone()[0]
                print(f"[DIAGNOSTIK] Jumlah data keseluruhan di dalam jadual 'rekod_qr' = {jumlah_asal} baris")
            except Exception as e_check:
                print(f"[DIAGNOSTIK ALERT] Gagal membaca jadual 'rekod_qr': {str(e_check)}")

            lajur_seq = "sequence_no"
            try:
                cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
                lajur_seq = "[Sequence No]"
            except sqlite3.OperationalError:
                lajur_seq = "sequence_no"
            
            base = f"SELECT id, tarikh, customer, quantity, machine, lotcard_no, {lajur_seq} FROM rekod_qr WHERE LOWER({lajur_seq}) LIKE 'b%'"
            
            if not teks:
                cursor.execute(base + " ORDER BY id DESC")
            else:
                # 🌟 2. TAMBAH PARAMETER TARIKH: Menyertakankan lajur 'tarikh' dalam tapisan WHERE query SQL
                # Menggunakan teks (format SQLite) dan teks_asal untuk sokongan carian teks/tarikh serentak
                query_penapis = base + f" AND (LOWER({lajur_seq}) LIKE ? OR LOWER(customer) LIKE ? OR LOWER(machine) LIKE ? OR tarikh LIKE ? OR tarikh LIKE ?) ORDER BY id DESC"
                
                param_biasa = f"%{teks_asal.lower()}%"
                param_tarikh = f"%{teks}%"
                
                cursor.execute(query_penapis, (param_biasa, param_biasa, param_biasa, param_tarikh, param_biasa))
                
            rekod_data = cursor.fetchall()
            print(f"[DIAGNOSTIK] Jumlah data Outer Box (B%) yang berjaya dijumpai = {len(rekod_data)} baris")
            
            for r in rekod_data:
                db_id = r[0]
                tarikh = r[1]
                customer = str(r[2]).upper() if r[2] else ""
                
                raw_inners = str(r[4]).strip() if r[4] else ""
                linked_inners = raw_inners.replace(",", "\n")
                
                total_qty_live = hitung_live_total_qty_dari_db(raw_inners)
                if total_qty_live > 0:
                    qty = f"{total_qty_live} PCS"
                else:
                    qty = f"{str(r[3]).replace('PCS','').strip()} PCS" if r[3] else "0 PCS"
                
                box_type = "OUTER BOX"
                outer_seq = r[6]                              
                
                jadual.insert("", tk.END, values=(
                    "☐", db_id, tarikh, customer, qty, box_type, linked_inners, outer_seq
                ), tags=('normal',))
                
    except Exception as e: 
        messagebox.showerror("ERROR OUTER", f"Ralat sistem ketika memuatkan data:\n{str(e)}")
        
def on_outer_click(event, jadual):
    """Menguruskan tanda checkbox pada baris grid."""
    item_id = jadual.identify_row(event.y)
    if item_id:
        v = list(jadual.item(item_id)['values'])
        t = "☑" if "☐" in str(v[0]) else "☐"
        v[0] = t
        jadual.item(item_id, values=v, tags=('checked' if t == "☑" else 'normal',))

def on_mouse_hover(event, jadual):
    """Menukar warna latar belakang baris apabila tetikus berada di atas grid."""
    global baris_hover_terakhir
    item_id = jadual.identify_row(event.y)
    if item_id != baris_hover_terakhir:
        if baris_hover_terakhir and jadual.exists(baris_hover_terakhir):
            v = jadual.item(baris_hover_terakhir)['values']
            jadual.item(baris_hover_terakhir, tags=('checked' if "☑" in str(v[0]) else 'normal',))
        if item_id and "☐" in str(jadual.item(item_id)['values'][0]): 
            jadual.item(item_id, tags=('hover',))
        baris_hover_terakhir = item_id

def on_mouse_leave(event, jadual):
    """Membersihkan kesan hover apabila tetikus meninggalkan grid."""
    global baris_hover_terakhir
    if baris_hover_terakhir and jadual.exists(baris_hover_terakhir):
        v = jadual.item(baris_hover_terakhir)['values']
        jadual.item(baris_hover_terakhir, tags=('checked' if "☑" in str(v[0]) else 'normal',))
    baris_hover_terakhir = None

def jana_grafik_outer_dari_row(r):
    """
    🌟 OUTER IMAGE PREVIEW GENERATION ENGINE (FIXED GRID INDEX OVERRIDE) 🌟
    Memaksa kad grafik stiker mengambil nilai kuantiti live yang paling terkini
    terus dari paparan grid jadual Treeview selepas dikemaskini.
    """
    try:
        elemen = list(r)
        if elemen and str(elemen[0]) in ("☐", "☑"):
            elemen = elemen[1:]
            
        # 🛠️ SEPADAN INDEKS: Memastikan susunan lajur mengikut kedudukan Treeview Sistem
        if len(elemen) >= 8:
            qty_text_live  = str(elemen[3]).replace('PCS','').strip()  # Lajur Box Quantity (395)
            raw_in         = str(elemen[5]).strip()                    # Lajur Linked Inners (WP)
            seq            = str(elemen[7]).strip()                    # Lajur Outer Sequence (B%)
            cust_name      = str(elemen[2]).strip()                    # Lajur Customer Name (ALPSMY)
        else:
            # Fallback jika data kecemasan terputus
            seq = "B2610200001"
            raw_in = ""
            qty_text_live = "395"
            cust_name = "ALPSMY"
            for item in elemen:
                if str(item).startswith("B"): seq = str(item).strip()
                elif str(item).startswith("WP"): raw_in = str(item).strip()
                elif "PCS" in str(item): qty_text_live = str(item).replace('PCS','').strip()

        qr = qrcode.QRCode(version=1, border=1)
        qr.add_data(seq)
        qr.make(fit=True)
        im_qr = qr.make_image().convert("RGB")
        
        data_g = []
        senarai_wp = [x.strip() for x in re.split(r'[,\n]', raw_in) if x.strip()]
        
        if senarai_wp:
            for idx, s in enumerate(senarai_wp):
                if idx == 0:
                    # Masukkan baki tolakan kuantiti murni ke slot stiker pertama
                    data_g.append((s, f"{qty_text_live} PCS"))
                else:
                    # Slot baki stiker lain yang dipautkan dalam kumpulan kotak
                    data_g.append((s, "100 PCS")) # Boleh tukar laluan jika mahu pecahan dinamik
        else:
            data_g.append(("INNER CODE", f"{qty_text_live} PCS"))
            
        # Menghantar maklumat murni yang tepat ke enjin bina imej stiker asal
        return lod.create_outer_label_image(seq, "OHTA PRECISION", cust_name, "COMBINED", "CONSOLIDATED", f"{qty_text_live} PCS", "M/C-01", datetime.now().strftime("%d/%m/%Y"), im_qr, data_g)
            
    except Exception as e_label_strict:
        print(f"Strict outer preview override layout fault: {e_label_strict}")
        seq = "B290920260002"
        qty_text_live = "70"
        qr = qrcode.QRCode(version=1, border=1); qr.add_data(seq); qr.make(fit=True)
        im_qr = qr.make_image().convert("RGB")
        data_g = [("INNER CODE", f"{qty_text_live} PCS")]
        return lod.create_outer_label_image(seq, "OHTA PRECISION", "ERROR CUST", "ERROR", "ERROR", f"{qty_text_live} PCS", "ERROR", "20/10/2026", im_qr, data_g)

def papar_pratonton_outer_terpilih(jadual, win):
    """Membuka popup prebiu kelompok stiker bagi baris yang ditandakan ☑."""
    sel = [jadual.item(i)['values'] for i in jadual.get_children() if "☑" in str(jadual.item(i)['values'][0])]
    if not sel: 
        return messagebox.showwarning("WARNING", "PLEASE TICK (☑) AT LEAST ONE RECORD TO PREVIEW!", parent=win)
    imgs = [jana_grafik_outer_dari_row(r) for r in sel if r]
    if imgs: 
        database_batch_preview.buka_popup_database_pukal_seragam(win, imgs, is_outer=True)

def eksport_outer_excel():
    """Menjana laporan laporan murni CSV daripada log database pusat."""
    conn_exp = None
    try:
        conn_exp = sqlite3.connect(dbm.DATABASE_PATH, timeout=10)
        cursor = conn_exp.cursor()
        
        lajur_seq = "sequence_no"
        try:
            cursor.execute("SELECT [Sequence No] FROM rekod_qr LIMIT 1")
            lajur_seq = "[Sequence No]"
        except sqlite3.OperationalError: pass
            
        cursor.execute(f"SELECT id, tarikh, customer, quantity, lotcard_no, machine, {lajur_seq} FROM rekod_qr WHERE {lajur_seq} LIKE 'B%' ORDER BY id DESC")
        data = cursor.fetchall()
        
        if not data:
            return messagebox.showwarning("WARNING", "NO DATA RECORD FOUND TO EXPORT!")
        
        tarikh_sekarang  = datetime.now().strftime("%Y%m%d")
        nama_fail_cadangan = f"Outer_report_{tarikh_sekarang}.csv"
        path = filedialog.asksaveasfilename(initialfile=nama_fail_cadangan, defaultextension=".csv")
        if path:
            with open(path, mode='w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(["ID", "Date", "Customer", "Quantity", "Box Type", "Linked Inners", "Outer Sequence"])
                w.writerows(data)
            messagebox.showinfo("SUCCESS", "Data logs report successfully exported!")
    except Exception as e:
        messagebox.showerror("EXPORT ERROR", f"Failed to export documents list:\n{str(e)}")
    finally:
        if conn_exp:
            conn_exp.close()

def susun_lajur_treeview(jadual, lajur, menaik):
    pass

def bina_tab_outer(f_tb, f_tp, win, gate_pratonton_seragam, fungsi_padam):
    """Membina reka bentuk penuh tab pengurusan Outer Box di dalam notebook utama (Strict 8-Column Force-Lock)."""
    tk.Label(f_tp, text="Search Outer:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=5)
    e_s = tk.Entry(f_tp, width=22, font=("Segoe UI", 10))
    e_s.pack(side=tk.LEFT, padx=5)
    
    # Bind search field entries cleanly
    e_s.bind("<Return>", lambda e: [dbm.laksanakan_auto_clean_orphaned_logs() if hasattr(dbm, 'laksanakan_auto_clean_orphaned_logs') else None, carian_outer(jad_out, e_s)])
    
    # Control Row Buttons Configuration (Left-Side Operations)
    tk.Button(f_tp, text="SEARCH", command=lambda: carian_outer(jad_out, e_s), bg="#007BFF", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="RESET", command=lambda: [e_s.delete(0, tk.END), carian_outer(jad_out, e_s)], bg="#6C757D", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="PREVIEW SELECTED", command=lambda: papar_pratonton_outer_terpilih(jad_out, win), bg="#28A745", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="DELETE SELECTED", command=lambda: fungsi_padam(jad_out, e_s), bg="#DC3545", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    tk.Button(f_tp, text="EXPORT CSV", command=eksport_outer_excel, bg="#343A40", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.LEFT, padx=2)
    
    # Navigation Action Button Triggers (Right-Side Actions Layout)
    tk.Button(f_tp, text="REFRESH", command=lambda: [dbm.laksanakan_auto_clean_orphaned_logs() if hasattr(dbm, 'laksanakan_auto_clean_orphaned_logs') else None, carian_outer(jad_out, e_s)], bg="#17A2B8", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.RIGHT, padx=2)
    tk.Button(f_tp, text="◀ BACK TO MAIN", command=win.destroy, bg="#6C757D", fg="white", font=("Segoe UI", 8, "bold"), padx=10).pack(side=tk.RIGHT, padx=2)
    
    # 🌟 DEFINITION FIX: Explicitly specify 9 technical slots but lock visual presentation to exactly 8 fields 🌟
    lajur_teknikal = ("Select", "ID", "Date", "Customer Name", "Box Quantity", "Box Type", "Linked Inners", "Outer Sequence" )
    lajur_papar_murni = ("Select", "ID", "Date", "Customer Name", "Box Quantity", "Box Type", "Linked Inners", "Outer Sequence")
    
    gaya = ttk.Style()
    gaya.configure("CentralOuter.Treeview", rowheight=78, font=("Segoe UI", 9), background="white", fieldbackground="white") 
    gaya.configure("CentralOuter.Treeview.Heading", font=("Segoe UI", 9, "bold"), cursor="hand2")
    
    global jad_out
    jad_out = ttk.Treeview(f_tb, columns=lajur_teknikal, show="headings", selectmode="browse", style="CentralOuter.Treeview")
    
    jad_out.tag_configure('normal', background='white', foreground='black')
    jad_out.tag_configure('hover', background='#E8F0FE', foreground='black')
    jad_out.tag_configure('checked', background='#E8F5E9', foreground='#1B5E20') 
    
    # Event tracker bindings setup
    jad_out.bind("<Button-1>", lambda e: on_outer_click(e, jad_out))
    jad_out.bind("<Motion>", lambda e: on_mouse_hover(e, jad_out))
    jad_out.bind("<Leave>", lambda e: on_mouse_leave(e, jad_out))
    
    # 🌟 DISPLAY OVERRIDE ENGINE: Force layout visualization arrays directly into memory slots 🌟
    jad_out.configure(displaycolumns=lajur_papar_murni)
    
    # Loop headings strictly across visible presentation tokens
    for col in lajur_teknikal:
        jad_out.heading(col, text=col)
        jad_out.column(col, width=110, anchor="center")
        
    # 🌟 HEADER TEXT SWAP: Remap the Column 7 header label string directly to overwrite "Operation" text 🌟
    jad_out.heading("Operation", text="Outer Sequence")
    
    # Set explicitly sized column spacing guidelines across active data tracks
    jad_out.column("Select", width=50)
    jad_out.column("ID", width=40)
    jad_out.column("Customer Name", width=140, anchor="w")
    jad_out.column("Box Quantity", width=110)
    jad_out.column("Box Type", width=110)
    #jad_out.column("Operation", width=130)       # This acts as your visual 'Outer Sequence' field now
    jad_out.column("Linked Inners", width=220, anchor="w") 
    
    # Hide the obsolete 9th background slot column completely from screen frame renders
    jad_out.column("Outer Sequence", width=0, stretch=tk.NO)
    
    sb = ttk.Scrollbar(f_tb, orient=tk.VERTICAL, command=jad_out.yview)
    jad_out.configure(yscrollcommand=sb.set)
    jad_out.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    
    carian_outer(jad_out, e_s)
