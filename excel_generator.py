import os
import sqlite3
from datetime import datetime, timedelta

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    # 🌟 IMPORT ENJIN CARTA EXCEL ASLI 🌟
    from openpyxl.chart import BarChart, PieChart, Reference
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    import csv

def jana_laporan_excel_tiga_tab(db_path, laluan_output_excel):
    """Membina fail Excel .xlsx premium dengan 1 Tab Visual Dashboard + 3 Tab Data Logs."""
    if not OPENPYXL_AVAILABLE:
        _jana_fallback_csv(db_path, laluan_output_excel.replace(".xlsx", "_REPORT_EXCEL.csv"))
        return

    try:
        wb = openpyxl.Workbook()
        if "Sheet" in wb.sheetnames:
            wb.remove(wb["Sheet"])
        
        # Penggayaan Struktur Font & Warna Korporat (Format aRGB Murni)
        font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        font_data = Font(name="Segoe UI", size=10)
        font_title = Font(name="Segoe UI", size=14, bold=True, color="1E3A8A")
        
        fill_inner = PatternFill(start_color="FF0284C7", fill_type="solid")   # Blue (Inner)
        fill_outer = PatternFill(start_color="FF2563EB", fill_type="solid")   # Dark Blue (Outer)
        fill_invoice = PatternFill(start_color="FF8B5CF6", fill_type="solid") # Purple (Invoice)
        fill_dash = PatternFill(start_color="FF0D9488", fill_type="solid")    # Teal (Dashboard)
        
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        border_nipis = Border(left=Side(style='thin', color='DDDDDD'), right=Side(style='thin', color='DDDDDD'), top=Side(style='thin', color='DDDDDD'), bottom=Side(style='thin', color='DDDDDD'))

        # CIPTA 4 TAB HELAIAN KERJA (DASHBOARD DI BARISAN PERTAMA)
        ws_dash = wb.create_sheet(title="📊 VISUAL DASHBOARD")
        ws_inner = wb.create_sheet(title="INNER PACKING LOGS")
        ws_outer = wb.create_sheet(title="OUTER PACKING LOGS")
        ws_invoice = wb.create_sheet(title="INVOICE SHIPPED LOGS")
        
        headers_inner = ["ID", "DATE", "CUSTOMER NAME", "DRAWING NO", "PART NO", "QUANTITY", "MANUFACTURED DATE", "MACHINE CODE", "LOT NO", "SEQUENCE NUMBER"]
        headers_outer = ["ID", "DATE", "CUSTOMER NAME", "DRAWING NO", "PART NO", "QUANTITY", "GENERATED TIME", "INNER BOX REF", "PAGING INDEX", "SEQUENCE NUMBER"]
        headers_invoice = ["ID", "DATE", "CUSTOMER NAME", "INVOICE NO", "SO NO", "QUANTITY", "GENERATED TIME", "OUTER BOX REF", "PAGING INDEX", "SEQUENCE NUMBER"]
        
        for ws, hd, fl in [(ws_inner, headers_inner, fill_inner), (ws_outer, headers_outer, fill_outer), (ws_invoice, headers_invoice, fill_invoice)]:
            ws.append(hd)
            ws.row_dimensions.height = 26
            for col_idx in range(1, len(hd) + 1):
                cell = ws.cell(row=1, column=col_idx)
                cell.font = font_header; cell.fill = fl; cell.alignment = align_center

        # EXTRAK DATA KESELURUHAN DARI SQLITE
        with sqlite3.connect(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no FROM rekod_qr ORDER BY id DESC")
            semua_baris = cursor.fetchall()
            
            for r in semua_baris:
                data_baris = list(r)
                seq_str = str(data_baris[9]).upper().strip() if (data_baris and len(data_baris) > 9) else ""
                
                # 🌟 KOREKSI JALUR INDEKS ASLI: Menyusun pembolehubah mengikut kedudukan kolum tegar database 🌟
                if seq_str.startswith("WP"):
                    ws_target = ws_inner
                    # database layout: 0:id, 1:tarikh, 2:customer, 3:drawing_no, 4:part_no, 5:quantity, 6:mfg_date, 7:machine, 8:lotcard_no, 9:sequence_no
                    data_bersih = [data_baris[0], data_baris[1], data_baris[2], data_baris[3], data_baris[4], data_baris[5], data_baris[6], data_baris[7], data_baris[8], data_baris[9]]
                elif seq_str.startswith("B"):
                    ws_target = ws_outer
                    data_bersih = [data_baris[0], data_baris[1], data_baris[2], data_baris[3], data_baris[4], data_baris[5], data_baris[6], data_baris[7], data_baris[8], data_baris[9]]
                elif seq_str.startswith("INV"):
                    ws_target = ws_invoice
                    drawing_clean = str(data_baris[3]).replace("INV:", "").strip()
                    part_clean = str(data_baris[4]).replace("SO:", "").strip()
                    data_bersih = [data_baris[0], data_baris[1], data_baris[2], drawing_clean, part_clean, data_baris[5], data_baris[6], data_baris[7], data_baris[8], data_baris[9]]
                else:
                    continue
                
                ws_target.append(data_bersih)
                cr = ws_target.max_row
                ws_target.row_dimensions[cr].height = 20
                for col_idx in range(1, len(data_bersih) + 1):
                    c = ws_target.cell(row=cr, column=col_idx)
                    c.font = font_data; c.border = border_nipis; c.alignment = align_center
        # 🌟 BINA STRUKTUR JADUAL RINGKASAN DI TAB DASHBOARD (VERSI UNIFIED GRIDLINES) 🌟
        try:
            ws_dash.sheet_view.showGridLines = True
        except Exception:
            try:
                ws_dash.views.sheetView.showGridLines = True
            except Exception:
                pass
                
        ws_dash.cell(row=2, column=2, value="OHTA PRECISION LOGISTICS MANAGEMENT DASHBOARD").font = font_title
        
        ws_dash.cell(row=4, column=2, value="OPERATION MODULE").font = font_header
        ws_dash.cell(row=4, column=2).fill = fill_dash; ws_dash.cell(row=4, column=2).alignment = align_center
        ws_dash.cell(row=4, column=3, value="TOTAL GENERATED").font = font_header
        ws_dash.cell(row=4, column=3).fill = fill_dash; ws_dash.cell(row=4, column=3).alignment = align_center
        
        modules = [
            ("Inner Packing Labels", "INNER PACKING LOGS"),
            ("Outer Packing Boxes", "OUTER PACKING LOGS"),
            ("Invoice Shipped Logs", "INVOICE SHIPPED LOGS")
        ]
        
        for idx, (nama_modul, nama_tab) in enumerate(modules, start=5):
            ws_dash.cell(row=idx, column=2, value=nama_modul).font = font_data
            ws_dash.cell(row=idx, column=2).border = border_nipis
            ws_dash.cell(row=idx, column=3, value=f"=COUNTA('{nama_tab}'!A:A)-1").font = font_data
            ws_dash.cell(row=idx, column=3).border = border_nipis; ws_dash.cell(row=idx, column=3).alignment = align_center

        # 🌟 JANA GRAFIK 1 - CARTA BAR (BAR CHART) COLUMNS 🌟
        carta_bar = BarChart()
        carta_bar.type = "col"; carta_bar.style = 10
        carta_bar.title = "Logistics Production Volumetric Analysis"
        carta_bar.y_axis.title = "Total Labels / Logs Created"
        carta_bar.x_axis.title = "Operation Department Modules"
        
        data_ref = Reference(ws_dash, min_col=3, min_row=4, max_row=7)
        cats_ref = Reference(ws_dash, min_col=2, min_row=5, max_row=7)
        carta_bar.add_data(data_ref, titles_from_data=True)
        carta_bar.set_categories(cats_ref)
        carta_bar.legend = None; carta_bar.width = 16; carta_bar.height = 11
        ws_dash.add_chart(carta_bar, "B10")

        # 🌟 JANA GRAFIK 2 - CARTA PAI (PIE CHART) BULAT 🌟
        carta_pai = PieChart()
        carta_pai.title = "Operational Share Distribution (%)"
        carta_pai.add_data(data_ref, titles_from_data=True)
        carta_pai.set_categories(cats_ref)
        carta_pai.width = 14; carta_pai.height = 11
        ws_dash.add_chart(carta_pai, "K10")

        # Tetapan Lebar Struktur Kolum Setiap Tab
        ws_dash.column_dimensions['B'].width = 25; ws_dash.column_dimensions['C'].width = 18
        ws_inner.column_dimensions['A'].width = 8; ws_inner.column_dimensions['B'].width = 14
        ws_inner.column_dimensions['C'].width = 34; ws_inner.column_dimensions['D'].width = 24
        ws_inner.column_dimensions['E'].width = 22; ws_inner.column_dimensions['F'].width = 14
        ws_inner.column_dimensions['G'].width = 22; ws_inner.column_dimensions['H'].width = 16
        ws_inner.column_dimensions['I'].width = 16; ws_inner.column_dimensions['J'].width = 24

        for ws in [ws_outer, ws_invoice]:
            ws.column_dimensions['A'].width = 8; ws.column_dimensions['B'].width = 14
            ws.column_dimensions['C'].width = 34; ws.column_dimensions['D'].width = 24
            ws.column_dimensions['E'].width = 22; ws.column_dimensions['F'].width = 14
            ws.column_dimensions['G'].width = 22; ws.column_dimensions['H'].width = 22
            ws.column_dimensions['I'].width = 14; ws.column_dimensions['J'].width = 24
                
        wb.save(laluan_output_excel)
        print("[EXCEL SYSTEM] Success! Multi-Tab English Report with Interactive Charts generated successfully.")
    except Exception as e:
        print(f"[EXCEL ERROR] Gagal membina carta: {e}")

def _jana_fallback_csv(db_path, laluan_output_csv):
    try:
        with sqlite3.connect(db_path, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no FROM rekod_qr ORDER BY id DESC")
            with open(laluan_output_csv, mode="w", newline="", encoding="utf-8") as f_csv:
                p = csv.writer(f_csv)
                p.writerow(["ID", "DATE", "CUSTOMER NAME", "INVOICE / DRAWING NO", "SO / PART NO", "QUANTITY", "GENERATED TIME", "OUTER REF", "PAGING INDEX", "SEQUENCE NUMBER"])
                for row in cursor.fetchall():
                    r_list = list(row)
                    if str(r_list[9]).upper().strip().startswith("INV"):
                        r_list[3] = str(r_list[3]).replace("INV:", "").strip()
                        r_list[4] = str(r_list[4]).replace("SO:", "").strip()
                    p.writerow(r_list)
    except: pass
