import os
import sqlite3
from datetime import datetime
from tkinter import filedialog, messagebox

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    import csv

def jana_laporan_excel_tiga_tab(db_path, laluan_output_excel):
    """
    Generates an executive-level formal Excel report with 3 dedicated tracking sheets.
    Applies a clean Classic Corporate Navy theme and auto-fits data grids perfectly.
    """
    if not OPENPYXL_AVAILABLE:
        _jana_fallback_csv(db_path, laluan_output_excel.replace(".xlsx", "_REPORT_EXCEL.csv"))
        return

    try:
        wb = openpyxl.Workbook()
        if "Sheet" in wb.sheetnames:
            wb.remove(wb["Sheet"])
        
        # --- Executive Typography & Styling Definitions ---
        font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        font_data = Font(name="Segoe UI", size=10, color="1A1A1A")
        
        # Professional Navy & Muted Accent Theme
        fill_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")  # Classic Corporate Navy Blue
        fill_alt_row = PatternFill(start_color="F2F6F9", end_color="F2F6F9", fill_type="solid") # Soft Ice Blue tint
        
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center")
        
        # Clean Corporate Borders
        border_thin = Border(
            left=Side(style='thin', color='D9D9D9'), 
            right=Side(style='thin', color='D9D9D9'), 
            top=Side(style='thin', color='D9D9D9'), 
            bottom=Side(style='thin', color='D9D9D9')
        )

        # Initialize the 3 Data Sheets
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
            ws.row_dimensions[1].height = 28  # Generous header row room
            for col_idx in range(1, len(hd) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.font = font_header
                cell.fill = fill_header
                cell.alignment = align_center
                cell.border = border_thin

        # Extract data from the local database source
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no FROM rekod_qr ORDER BY id DESC")
            all_rows = cursor.fetchall()
            
            for row in all_rows:
                no_siri = str(row[9]).upper().strip() if row[9] else ""
                
                # Rigid mapping parameters array references
                id_db, tarikh, cust, drw, part, qty, mfg, mach, lot, seq = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]
                
                if no_siri.startswith("WP"):
                    ws_target = ws_inner
                    data_clean = [id_db, tarikh, cust, drw, part, qty, mfg, mach, lot, seq]
                elif no_siri.startswith("B"):
                    ws_target = ws_outer
                    data_clean = [id_db, tarikh, cust, drw, part, qty, mfg, mach, lot, seq]
                elif no_siri.startswith("INV"):
                    ws_target = ws_invoice
                    drw_clean = str(drw).replace("INV:", "").strip()
                    part_clean = str(part).replace("SO:", "").strip()
                    data_clean = [id_db, tarikh, cust, drw_clean, part_clean, qty, mfg, mach, lot, seq]
                else:
                    continue
                
                ws_target.append(data_clean)
                cr = ws_target.max_row
                ws_target.row_dimensions[cr].height = 22  # Balanced spacing row height
                
                for col_idx in range(1, len(data_clean) + 1):
                    c = ws_target.cell(row=cr, column=col_idx)
                    c.font = font_data
                    c.border = border_thin
                    
                    # Zebra striped row formatting assignment
                    if cr % 2 == 0:
                        c.fill = fill_alt_row
                    
                    # Clean number formatting for accounting reports
                    if col_idx == 6:
                        try:
                            c.value = int(c.value)
                            c.number_format = '#,##0'
                            c.alignment = Alignment(horizontal="right", vertical="center")
                            continue
                        except:
                            pass
                            
                    # Left align long company name texts, center others
                    if col_idx == 3:
                        c.alignment = align_left
                    else:
                        c.alignment = align_center

        # Dynamic safety column auto-fitting strategy
        for ws in [ws_inner, ws_outer, ws_invoice]:
            for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
                for cell in row:
                    if cell.value is not None:
                        let_col = cell.column_letter
                        len_val = len(str(cell.value))
                        cur_width = ws.column_dimensions[let_col].width or 12
                        if len_val + 5 > cur_width:
                            ws.column_dimensions[let_col].width = len_val + 5

        wb.save(laluan_output_excel)
        
    except Exception as e:
        raise e

def _jana_fallback_csv(db_path, fallback_path):
    try:
        with sqlite3.connect("warehouse_data.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no FROM rekod_qr ORDER BY id DESC")
            rows = cursor.fetchall()
            with open(fallback_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "DATE", "CUSTOMER", "DRAWING_NO/INV_NO", "PART_NO/SO_NO", "QTY", "MFG/GEN_TIME", "MACHINE/REF", "LOT/INDEX", "SEQUENCE"])
                writer.writerows(rows)
    except Exception as e:
        print(f"Fallback CSV error: {str(e)}")
