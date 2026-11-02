import sqlite3
import os
import shutil
import threading
import socket
from datetime import datetime, timedelta
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess

# ─── ENJIN AUTO-INSTALL PREMIUM: KALIS PAPARAN TETINGKAP HITAM CMD ───
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    try:
        # Sediakan konfigurasi permulaan untuk menyorokkan tetingkap proses luar Windows
        si_startup = subprocess.STARTUPINFO()
        si_startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si_startup.wShowWindow = subprocess.SW_HIDE

        # Jalankan pemasangan openpyxl secara senyap (Silent Mode) tanpa mencetuskan CMD
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "openpyxl"],
            startupinfo=si_startup,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except Exception:
        pass


# Tambah baris ini di bahagian paling atas fail logik dashboard anda:
import database_manager as dbm

# ─── INTEGRASI ENJIN EXCEL DI DALAM LOGIK (MENGELAKKAN PYINSTALLER MISSING MODULE) ───
def jana_laporan_excel_tiga_tab(database_path, laluan_output_excel):
    """
    📊 ENJIN DATA INTEGRASI EMPAT TAB EXCEL RASMI .XLSX (OPENPYXL TUPLE FIX) 📊
    """
    if laluan_output_excel.lower().endswith('.xls'):
        laluan_output_excel = os.path.splitext(laluan_output_excel)[0] + ".xlsx"
    elif not laluan_output_excel.lower().endswith('.xlsx'):
        laluan_output_excel = laluan_output_excel + ".xlsx"

    try:
        with sqlite3.connect(database_path, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no FROM rekod_qr ORDER BY id DESC")
            semua_rekod = cursor.fetchall()

        log_inner_raw = [r for r in semua_rekod if r and str(r[-1]).startswith("WP")]
        log_outer_raw = [r for r in semua_rekod if r and str(r[-1]).startswith("B")]
        log_invoice_raw = [r for r in semua_rekod if r and str(r[-1]).startswith("INV")]

        header_inner = ["ID", "PACK DATE", "CUSTOMER NAME", "DRAWING NO", "PART NUMBER", "QUANTITY", "MNFD DATE", "MACHINE NO", "LOTCARD NO", "SEQUENCE NUMBER"]
        data_inner = [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]] for r in log_inner_raw]

        header_outer = ["ID", "DATE", "CUSTOMER NAME", "DRAWING NO", "PART NUMBER", "QUANTITY", "MNFD DATE", "INNER LINK", "SEQUENCE NUMBER"]
        data_outer = [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[9]] for r in log_outer_raw]

        header_invoice = ["ID", "PACK DATE", "CUSTOMER NAME", "INVOICE NO", "SO NO", "QUANTITY", "PACK TIME", "BOX LINK", "BOX INDEX", "SEQUENCE NUMBER"]
        data_invoice = []
        for r in log_invoice_raw:
            inv_no_clean = str(r[3]).replace("INV:", "").strip() if r[3] else ""
            so_no_clean = str(r[4]).replace("SO:", "").strip() if r[4] else ""
            data_invoice.append([r[0], r[1], r[2], inv_no_clean, so_no_clean, r[5], r[6], r[7], r[8], r[9]])

        header_history = ["PACK DATE", "CUSTOMER NAME", "PART NUMBER", "INNER SEQUENCE", "INNER QTY", "LINKED OUTER BOX", "LINKED INVOICE NO"]
        log_label_history = []
        for r_in in log_inner_raw:
            wp_code = str(r_in[-1]).strip()
            outer_box_code = "BELUM MASUK OUTER BOX"
            invoice_shipped_code = "BELUM DI-INVOICE"
            for r_out in log_outer_raw:
                if r_out and wp_code in str(r_out[7]).replace('\n', ','):
                    outer_box_code = str(r_out[-1]).strip()
                    break
            if outer_box_code != "BELUM MASUK OUTER BOX":
                for r_inv in log_invoice_raw:
                    if r_inv and outer_box_code in str(r_inv[7]).replace('\n', ','):
                        invoice_shipped_code = str(r_inv[-1]).strip()
                        break
            log_label_history.append([r_in[1], r_in[2], r_in[4], wp_code, r_in[5], outer_box_code, invoice_shipped_code])

        wb = openpyxl.Workbook()
        ws1 = wb.active; ws1.title = "INNER PACKING LOGS"
        ws2 = wb.create_sheet(title="OUTER PACKING LOGS")
        ws3 = wb.create_sheet(title="INVOICE SHIPPED LOGS")
        ws4 = wb.create_sheet(title="LABEL HISTORY")

        def suntik_data_excel(ws, header, rows):
            ws.append(header)
            for r in rows: ws.append(r)

        suntik_data_excel(ws1, header_inner, data_inner)
        suntik_data_excel(ws2, header_outer, data_outer)
        suntik_data_excel(ws3, header_invoice, data_invoice)
        suntik_data_excel(ws4, header_history, log_label_history)

        warna_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        font_data = Font(name="Segoe UI", size=10, bold=False, color="000000")
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center")
        sempadan_nipis = Border(left=Side(style='thin', color='CBD5E1'), right=Side(style='thin', color='CBD5E1'), top=Side(style='thin', color='CBD5E1'), bottom=Side(style='thin', color='CBD5E1'))

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            ws.sheet_view.showGridLines = True
            ws.row_dimensions[1].height = 28
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(row=1, column=col)
                cell.fill = warna_header; cell.font = font_header; cell.alignment = align_center

            for row in range(2, ws.max_row + 1):
                ws.row_dimensions[row].height = 20
                for col in range(1, ws.max_column + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.font = font_data; cell.border = sempadan_nipis
                    nama_hdr = str(ws.cell(row=1, column=col).value).upper()
                    cell.alignment = align_center if any(kwd in nama_hdr for kwd in ["ID", "DATE", "TIME", "SEQUENCE", "NUMBER", "BOX", "INDEX", "QTY", "LINK"]) else align_left

            # 🛠️ DIBAIKI: Membuang tanda '+' yang tergantung dan mengira dengan selamat
            for col_idx in range(1, ws.max_column + 1):
                senarai_panjang = [len(str(ws.cell(row=r, column=col_idx).value or '')) for r in range(1, ws.max_row + 1)]
                max_len = max(senarai_panjang) if senarai_panjang else 0
                ws.column_dimensions[get_column_letter(col_idx)].width = max(max_len + 4, 12)

        wb.save(laluan_output_excel)
        print(f"[SUCCESS EXCEL CLEANED] Fail Excel tunggal 4-Sheet berjaya disimpan ke: {laluan_output_excel}")
    except Exception as e:
        raise Exception(f"Gagal memproses kemas kini laporan 4-Sheet Excel: {str(e)}")


# ─── FUNGSI UTAMA DASHBOARD LOGIC ───
def dapatkan_statistik_dashboard_harian(tarikh_obj):
    """Kiraan total angka metrik kotak atas dengan padanan 3 format tarikh sekaligus (Sambungan Rangkaian NAS)."""
    tarikh_iso = tarikh_obj.strftime("%Y-%m-%d")
    tarikh_sempang = tarikh_obj.strftime("%d-%m-%Y")
    tarikh_condong = tarikh_obj.strftime("%d/%m/%Y")
    
    stats = {"inner_stickers": 0, "outer_boxes": 0, "invoice_logs": 0}
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
                
            cursor.execute(f"SELECT COUNT(*) FROM rekod_qr WHERE (tarikh LIKE ? OR tarikh = ? OR tarikh = ?) AND {lajur_seq} LIKE 'WP%'", (f"{tarikh_iso}%", tarikh_sempang, tarikh_condong))
            r_in = cursor.fetchone()
            stats["inner_stickers"] = r_in[0] if (r_in and r_in[0] is not None) else 0
            
            cursor.execute(f"SELECT COUNT(*) FROM rekod_qr WHERE (tarikh LIKE ? OR tarikh = ? OR tarikh = ?) AND {lajur_seq} LIKE 'B%'", (f"{tarikh_iso}%", tarikh_sempang, tarikh_condong))
            r_out = cursor.fetchone()
            stats["outer_boxes"] = r_out[0] if (r_out and r_out[0] is not None) else 0
            
            cursor.execute(f"SELECT COUNT(*) FROM rekod_qr WHERE (tarikh LIKE ? OR tarikh = ? OR tarikh = ?) AND {lajur_seq} LIKE 'INV%'", (f"{tarikh_iso}%", tarikh_sempang, tarikh_condong))
            r_inv = cursor.fetchone()
            stats["invoice_logs"] = r_inv[0] if (r_inv and r_inv[0] is not None) else 0
            
    except Exception as e: 
        print(f"Error central stats dashboard: {e}")
    return stats
def dapatkan_senarai_aktiviti_harian(tarikh_obj):
    """Memaparkan data ringkasan log summary bawah berdasarkan cap jam masa sebenar transaksi dari database pusat NAS."""
    tarikh_iso = tarikh_obj.strftime("%Y-%m-%d")
    tarikh_sempang = tarikh_obj.strftime("%d-%m-%Y")
    tarikh_condong = tarikh_obj.strftime("%d/%m/%Y")
    
    senarai_aktiviti = []
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
            
            query = f"""
                SELECT id, tarikh, customer, {lajur_seq}, mfg_date 
                FROM rekod_qr 
                WHERE (tarikh LIKE ? OR tarikh = ? OR tarikh = ?) 
                ORDER BY id DESC LIMIT 50
            """
            cursor.execute(query, (f"{tarikh_iso}%", tarikh_sempang, tarikh_condong))
            
            for r in cursor.fetchall():
                id_db, tarikh_raw, cust, seq, mfg_val = r
                seq_str = str(seq).upper().strip()
                modul = "INNER PACKING" if seq_str.startswith("WP") else "OUTER PACKING" if seq_str.startswith("B") else "INVOICE LOGS" if seq_str.startswith("INV") else "SYSTEM REC"
                
                waktu_clean = ""
                try:
                    if len(str(tarikh_raw)) > 10:
                        waktu_clean = str(tarikh_raw).split()[1].strip()
                    else:
                        waktu_clean = str(mfg_val).strip()
                except:
                    waktu_clean = datetime.now().strftime("%H:%M:%S")
                
                if not waktu_clean or ":" not in waktu_clean:
                    waktu_clean = datetime.now().strftime("%H:%M:%S")
                    
                senarai_aktiviti.append((waktu_clean, modul, seq_str, str(cust).upper().strip()))
                
    except Exception as e: 
        print(f"Error log central: {e}")
    return senarai_aktiviti

def laksanakan_manual_backup_PC(parent_win):
    pass

def laksanakan_auto_backup_NAS(parent_win=None, mod_manual=False):
    """Routes backup signal based on automatic startup execution or manual button click."""
    if mod_manual:
        _proses_generate_report_manual_save_as(parent_win)
    else:
        t = threading.Thread(target=_proses_salinan_fizikal_nas_silent, daemon=True)
        t.start()

def _proses_salinan_fizikal_nas_silent():
    LALUAN_NAS_SERVER_ROOT = r"Z:\IT\IT\QR_SYS_Backup(DB)"
    db_asal = "warehouse_data.db"
    if not os.path.exists(db_asal): return
    try:
        try:
            computer_name = socket.gethostname().upper().replace(" ", "_")
        except Exception:
            computer_name = "UNKNOWN_STATION"
            
        pc_specific_backup_dir = os.path.join(LALUAN_NAS_SERVER_ROOT, computer_name)
        if not os.path.exists(pc_specific_backup_dir): 
            os.makedirs(pc_specific_backup_dir, exist_ok=True)
            
        tarikh_hari_ini = datetime.now().strftime("%Y-%m-%d")
        
        nama_backup_nas = f"QR_System_Backup_DB_{computer_name}_{tarikh_hari_ini}.db"
        shutil.copy(db_asal, os.path.join(pc_specific_backup_dir, nama_backup_nas))
        
        nama_excel_nas = f"LIVE_WAREHOUSE_REPORT_{computer_name}.xlsx"
        # Memanggil enjin tempatan yang diintegrasikan secara langsung
        jana_laporan_excel_tiga_tab(db_asal, os.path.join(pc_specific_backup_dir, nama_excel_nas))
        
        _laksanakan_auto_clean_fail_lama_nas(pc_specific_backup_dir)
    except: 
        pass

def _proses_generate_report_manual_save_as(parent_win):
    """Launches the native Windows File Explorer to let users choose their custom export directory using central database path."""
    db_asal = getattr(dbm, 'DATABASE_PATH', 'warehouse_data.db')
    
    if not os.path.exists(db_asal):
        return messagebox.showerror("ERROR", f"Central Database file not found at location:\n{db_asal}", parent=parent_win)
        
    tarikh_hari_ini = datetime.now().strftime("%Y%m%d_%H%M%S")
    nama_fail_cadangan = f"COMPILATION_LOGISTICS_REPORT_{tarikh_hari_ini}.xlsx"
    
    path_pilihan_user = filedialog.asksaveasfilename(
        title="CHOOSE WHERE TO SAVE COMPILATION REPORT",
        initialfile=nama_fail_cadangan,
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")],
        parent=parent_win
    )
    
    if not path_pilihan_user:
        return

    try:
        # Memanggil enjin tempatan yang diintegrasikan secara langsung
        jana_laporan_excel_tiga_tab(db_asal, path_pilihan_user)
        messagebox.showinfo(
            "REPORT EXPORTED", 
            f"Excel Compilation Report successfully created and saved!\n\n"
            f"📂 Location: {path_pilihan_user}\n\n"
            f"Your 4-sheet premium logistics report is ready for viewing.", 
            parent=parent_win
        )
    except Exception as e:
        messagebox.showerror("SAVE FAILED", f"Failed to save Excel file at chosen location!\n\nError: {str(e)}", parent=parent_win)

def _laksanakan_auto_clean_fail_lama_nas(folder_nas):
    """Memadam fail sandaran database (.db) dan laporan lama pada NAS yang melebihi had umur 30 hari secara automatik."""
    if not folder_nas or not os.path.exists(folder_nas):
        return
    try:
        had_masa = datetime.now() - timedelta(days=30)
        for nama_fail in os.listdir(folder_nas):
            adalah_fail_backup = (
                nama_fail.startswith("QR_System_Backup_DB_") or 
                nama_fail.startswith("QR System Backup DB_") or 
                nama_fail.startswith("LIVE_WAREHOUSE_REPORT_")
            )
            adalah_format_sah = (
                nama_fail.endswith(".db") or 
                nama_fail.endswith(".xlsx") or 
                nama_fail.endswith(".csv")
            )
            if adalah_fail_backup and adalah_format_sah:
                laluan = os.path.join(folder_nas, nama_fail)
                if datetime.fromtimestamp(os.path.getmtime(laluan)) < had_masa: 
                    os.remove(laluan)
                    print(f"[NAS CLEANER] Fail lama berjaya dipadam: {nama_fail}")
    except Exception as e: 
        print(f"[NAS CLEANER ERROR] Gagal menjalankan pembersihan automatik NAS: {str(e)}")
