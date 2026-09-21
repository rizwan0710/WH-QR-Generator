import os
import sqlite3
import shutil
import threading
import socket
from datetime import datetime

def laksanakan_backup_ke_nas_async():
    """Melancarkan enjin backup berkembar (Database + Excel) ke latar belakang secara Threaded."""
    t = threading.Thread(target=_proses_salinan_excel_dan_db_nas, daemon=True)
    t.start()

def _proses_salinan_excel_dan_db_nas():
    """Menguruskan kemas kini serentak bagi fail fizikal .db dan laporan formal Excel ke jajaran Z:\\."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    # 1. ATURAN LALUAN DISK NETWORK STORAGE OFFICE ANDA
    NAS_SERVER_ROOT = r"Z:\IT\IT\QR_SYS_Backup(DB)"
    db_asal = "warehouse_data.db"
    
    if not os.path.exists(db_asal):
        print("[NAS BACKUP ERROR] Fail pangkalan data 'warehouse_data.db' tidak dijumpai.")
        return
        
    try:
        # Mengesan nama pengenalan hos pc operator secara dinamik
        try:
            computer_name = socket.gethostname().upper().replace(" ", "_")
        except Exception:
            computer_name = "UNKNOWN_STATION"
            
        pc_specific_backup_dir = os.path.join(NAS_SERVER_ROOT, computer_name)
        os.makedirs(pc_specific_backup_dir, exist_ok=True)
            
        # Penetapan sebutan nama fail penjepala mengikut standard korporat
        tarikh_hari_ini = datetime.now().strftime("%Y-%m-%d")
        
        # 🌟 DIBAIKI: Nama fail diseragamkan dengan kod dashboard_logic asal anda! 🌟
        nama_fail_db_backup = f"QR System Backup DB_{tarikh_hari_ini}.db"
        nama_fail_excel_backup = f"LIVE_WAREHOUSE_REPORT_{computer_name}.xlsx"
        
        laluan_db_nas = os.path.join(pc_specific_backup_dir, nama_fail_db_backup)
        laluan_excel_nas = os.path.join(pc_specific_backup_dir, nama_fail_excel_backup)
        
        # =============================================================
        # 🌟 BAHAGIAN A: UPDATE LIVE PHYSICAL DATABASE FILE (.db) 🌟
        # =============================================================
        try:
            # 🌟 DIBAIKI: Menggunakan kaedah shutil.copy biasa untuk memastikan write permissions dikemas kini serentak! 🌟
            shutil.copy(db_asal, laluan_db_nas)
            print(f"[NAS DB SUCCESS] Database copied successfully to: {laluan_db_nas}")
        except Exception as e_db:
            print(f"[NAS DB ERROR] Failed to copy physical database file: {str(e_db)}")

        # =============================================================
        # 🌟 BAHAGIAN B: UPDATE LIVE CORPORATE EXCEL REPORT (.xlsx) 🌟
        # =============================================================
        wb = openpyxl.Workbook()
        if "Sheet" in wb.sheetnames:
            wb.remove(wb["Sheet"])
        
        # Executive Navy & Steel Gray Typography Theme
        font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        font_data = Font(name="Segoe UI", size=10, color="1A1A1A")
        
        fill_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")  # Corporate Navy Blue
        fill_alt_row = PatternFill(start_color="F2F6F9", end_color="F2F6F9", fill_type="solid") # Soft Ice Blue
        
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center")
        border_thin = Border(left=Side(style='thin', color='D9D9D9'), right=Side(style='thin', color='D9D9D9'), top=Side(style='thin', color='D9D9D9'), bottom=Side(style='thin', color='D9D9D9'))

        ws_inner = wb.create_sheet(title="INNER PACKING LOGS")
        ws_outer = wb.create_sheet(title="OUTER PACKING LOGS")
        ws_invoice = wb.create_sheet(title="INVOICE SHIPPED LOGS")
        
        headers_inner = ["ID", "DATE", "CUSTOMER NAME", "DRAWING NO", "PART NO", "QUANTITY", "MANUFACTURED DATE", "MACHINE CODE", "LOT NO", "SEQUENCE NUMBER"]
        headers_outer = ["ID", "DATE", "CUSTOMER NAME", "DRAWING NO", "PART NO", "QUANTITY", "GENERATED TIME", "INNER BOX REF", "PAGING INDEX", "SEQUENCE NUMBER"]
        headers_invoice = ["ID", "DATE", "CUSTOMER NAME", "INVOICE NO", "SO NO", "QUANTITY", "GENERATED TIME", "OUTER BOX REF", "PAGING INDEX", "SEQUENCE NUMBER"]
        
        for ws, hd in [(ws_inner, headers_inner), (ws_outer, headers_outer), (ws_invoice, headers_invoice)]:
            try:
                ws.sheet_view.showGridLines = True
            except:
                pass
            ws.append(hd)
            ws.row_dimensions.height = 28
            for col_idx in range(1, len(hd) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.font = font_header; cell.fill = fill_header; cell.alignment = align_center; cell.border = border_thin

        # Hubungkan ke pangkalan data untuk pengisian baris data excel
        with sqlite3.connect(db_asal, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no FROM rekod_qr ORDER BY id DESC")
            all_rows = cursor.fetchall()
            
            for row in all_rows:
                data_baris = list(row)
                seq_str = str(data_baris[9]).upper().strip() if (data_baris and len(data_baris) > 9) else ""
                
                # Memetik lajur mengikut pengelasan siri baris sistem asal
                id_db = data_baris[0]
                tarikh = data_baris[1]
                cust = data_baris[2]
                drw = data_baris[3]
                part = data_baris[4]
                qty = data_baris[5]
                mfg = data_baris[6]
                mach = data_baris[7]
                lot = data_baris[8]
                seq = data_baris[9]
                
                if seq_str.startswith("WP"):
                    ws_target = ws_inner
                    data_clean = [id_db, tarikh, cust, drw, part, qty, mfg, mach, lot, seq]
                elif seq_str.startswith("B"):
                    ws_target = ws_outer
                    data_clean = [id_db, tarikh, cust, drw, part, qty, mfg, mach, lot, seq]
                elif seq_str.startswith("INV"):
                    ws_target = ws_invoice
                    drw_clean = str(drw).replace("INV:", "").strip()
                    part_clean = str(part).replace("SO:", "").strip()
                    data_clean = [id_db, tarikh, cust, drw_clean, part_clean, qty, mfg, mach, lot, seq]
                else:
                    continue
                
                ws_target.append(data_clean)
                cr = ws_target.max_row
                ws_target.row_dimensions[cr].height = 22
                
                for col_idx in range(1, len(data_clean) + 1):
                    c = ws_target.cell(row=cr, column=col_idx)
                    c.font = font_data; c.border = border_thin
                    
                    if cr % 2 == 0:
                        c.fill = fill_alt_row
                        
                    if col_idx == 6:
                        try:
                            c.value = int(c.value)
                            c.number_format = '#,##0'
                            c.alignment = Alignment(horizontal="right", vertical="center")
                            continue
                        except:
                            pass
                            
                    if col_idx == 3:
                        c.alignment = align_left
                    else:
                        c.alignment = align_center

        # Auto-fit kelebaran kolum menggunakan kordinat koordinat huruf sel asli
        for ws in [ws_inner, ws_outer, ws_invoice]:
            for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
                for cell in row:
                    if cell.value is not None:
                        let_col = cell.column_letter
                        len_val = len(str(cell.value))
                        cur_width = ws.column_dimensions[let_col].width or 12
                        if len_val + 5 > cur_width:
                            ws.column_dimensions[let_col].width = len_val + 5

        wb.save(laluan_excel_nas)
        print(f"[NAS EXCEL SUCCESS] Live spreadsheet updated successfully layout at -> {laluan_excel_nas}")
        return True
    except Exception as e:
        print(f"[NAS BACKUP WARNING] Network transmission thread encountered exceptions: {str(e)}")
        return False
