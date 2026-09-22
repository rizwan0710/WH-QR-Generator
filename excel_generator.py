import sqlite3
import os
import sys

# ─── ENJIN AUTO-INSTALL: Memastikan modul 'openpyxl' sentiasa tersedia ───
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except Exception:
        pass

def jana_laporan_excel_tiga_tab(database_path, laluan_output_excel):
    """
    📊 ENJIN DATA INTEGRASI EMPAT TAB EXCEL RASMI .XLSX (OPENPYXL TUPLE FIX) 📊
    Menjana fail Excel (.xlsx) murni tunggal dengan penukaran lajur dan pembersihan teks data:
    1. INNER PACKING LOGS (Date -> Pack Date)
    2. OUTER PACKING LOGS (Machine No -> Inner Link, Buang Lotcard No)
    3. INVOICE SHIPPED LOGS (Pembersihan Teks "INV:" dan "SO:", Penukaran 6 Nama Lajur)
    4. LABEL HISTORY (Kompilasi Rujukan Silang Rantai Bekalan Gudang)
    """
    if laluan_output_excel.lower().endswith('.xls'):
        laluan_output_excel = os.path.splitext(laluan_output_excel) + ".xlsx"
    elif not laluan_output_excel.lower().endswith('.xlsx'):
        laluan_output_excel = laluan_output_excel + ".xlsx"

    try:
        # 1. TARIK DATA MURNI DARI PANGKALAN DATA GUDANG KILANG
        db_aktif = "warehouse_data.db"
        if os.path.exists("data/warehouse_data.db"):
            try:
                with sqlite3.connect("data/warehouse_data.db") as c_test:
                    if c_test.execute("SELECT COUNT(*) FROM rekod_qr").fetchone() > 0:
                        db_aktif = "data/warehouse_data.db"
            except Exception: pass

        with sqlite3.connect(db_aktif, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, tarikh, customer, drawing_no, part_no, quantity, mfg_date, machine, lotcard_no, sequence_no FROM rekod_qr ORDER BY id DESC")
            semua_rekod = cursor.fetchall()

        # 2. SELEKSI PENGASINGAN DATA ASAL REKOD KILANG
        log_inner_raw = [r for r in semua_rekod if r and str(r[-1]).startswith("WP")]
        log_outer_raw = [r for r in semua_rekod if r and str(r[-1]).startswith("B")]
        log_invoice_raw = [r for r in semua_rekod if r and str(r[-1]).startswith("INV")]

        # ─── 📦 FORMAT LENGKAP TAB 1: INNER PACKING LOGS ───
        header_inner = ["ID", "PACK DATE", "CUSTOMER NAME", "DRAWING NO", "PART NUMBER", "QUANTITY", "MNFD DATE", "MACHINE NO", "LOTCARD NO", "SEQUENCE NUMBER"]
        data_inner = []
        for r in log_inner_raw:
            data_inner.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]])

        # ─── 🏢 FORMAT LENGKAP TAB 2: OUTER PACKING LOGS ───
        header_outer = ["ID", "DATE", "CUSTOMER NAME", "DRAWING NO", "PART NUMBER", "QUANTITY", "MNFD DATE", "INNER LINK", "SEQUENCE NUMBER"]
        data_outer = []
        for r in log_outer_raw:
            # Mengeluarkan r[8] (Lotcard No) daripada susunan baris excel sepenuhnya
            data_outer.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[9]])

        # ─── 📄 FORMAT LENGKAP TAB 3: INVOICE SHIPPED LOGS ───
        header_invoice = ["ID", "PACK DATE", "CUSTOMER NAME", "INVOICE NO", "SO NO", "QUANTITY", "PACK TIME", "BOX LINK", "BOX INDEX", "SEQUENCE NUMBER"]
        data_invoice = []
        for r in log_invoice_raw:
            inv_no_clean = str(r[3]).replace("INV:", "").strip() if r[3] else ""
            so_no_clean = str(r[4]).replace("SO:", "").strip() if r[4] else ""
            
            data_invoice.append([
                r[0],          # ID
                r[1],          # PACK DATE (Asal: Date)
                r[2],          # CUSTOMER NAME
                inv_no_clean,  # INVOICE NO (Asal: Drawing No - Teks "INV:" dibuang)
                so_no_clean,   # SO NO (Asal: Part Number - Teks "SO:" dibuang)
                r[5],          # QUANTITY
                r[6],          # PACK TIME (Asal: MNFD DATE)
                r[7],          # BOX LINK (Asal: Machine No)
                r[8],          # BOX INDEX (Asal: Lotcard No)
                r[9]           # SEQUENCE NUMBER
            ])

        # ─── 🔍 FORMAT LENGKAP TAB 4: LABEL HISTORY (RUJUKAN SILANG RANTAI) ───
        header_history = ["PACK DATE", "CUSTOMER NAME", "PART NUMBER", "INNER SEQUENCE", "INNER QTY", "LINKED OUTER BOX", "LINKED INVOICE NO"]
        log_label_history = []

        for r_in in log_inner_raw:
            wp_code = str(r_in[-1]).strip()
            tarikh_in = r_in[1]
            customer_in = r_in[2]
            part_in = r_in[4]
            qty_in = r_in[5]
            
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
                        
            log_label_history.append([tarikh_in, customer_in, part_in, wp_code, qty_in, outer_box_code, invoice_shipped_code])

        # ─── 3. PROSES PENULISAN STRUKTUR WORKBOOK OPENPYXL ───
        wb = openpyxl.Workbook()
        
        ws1 = wb.active; ws1.title = "INNER PACKING LOGS"
        ws2 = wb.create_sheet(title="OUTER PACKING LOGS")
        ws3 = wb.create_sheet(title="INVOICE SHIPPED LOGS")
        ws4 = wb.create_sheet(title="LABEL HISTORY")

        def suntik_data_excel(ws, header, rows):
            ws.append(header)
            for r in rows:
                ws.append(r)

        suntik_data_excel(ws1, header_inner, data_inner)
        suntik_data_excel(ws2, header_outer, data_outer)
        suntik_data_excel(ws3, header_invoice, data_invoice)
        suntik_data_excel(ws4, header_history, log_label_history)

        # ─── 4. FORMAT REKA BENTUK TEMA KORPORAT PREMIUM OHTA ───
        warna_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Navy Blue
        font_header = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
        font_data = Font(name="Segoe UI", size=10, bold=False, color="000000")
        
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center")
        sempadan_nipis = Border(left=Side(style='thin', color='CBD5E1'), right=Side(style='thin', color='CBD5E1'), top=Side(style='thin', color='CBD5E1'), bottom=Side(style='thin', color='CBD5E1'))

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            ws.sheet_view.showGridLines = True # Kekalkan garisan kekotak grid murni
            
            # Format baris tajuk pertama (Header - Row 1)
            ws.row_dimensions[1].height = 28
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(row=1, column=col)
                cell.fill = warna_header
                cell.font = font_header
                cell.alignment = align_center

            # Format baris data logistik (Row 2+)
            for row in range(2, ws.max_row + 1):
                ws.row_dimensions[row].height = 20
                for col in range(1, ws.max_column + 1):
                    cell = ws.cell(row=row, column=col)
                    cell.font = font_data
                    cell.border = sempadan_nipis
                    
                    nama_hdr = str(ws.cell(row=1, column=col).value).upper()
                    if any(kwd in nama_hdr for kwd in ["ID", "DATE", "TIME", "SEQUENCE", "NUMBER", "BOX", "INDEX", "QTY", "LINK"]):
                        cell.alignment = align_center
                    else:
                        cell.alignment = align_left

            # 🌟 PEMBETULAN MUKTAMAD KALIS RALAT TUPLE COLUMN FIT 🌟
            # Menggunakan indeks integer lajur untuk mengelakkan isu perbezaan jenis struktur openpyxl
            for col_idx in range(1, ws.max_column + 1):
                max_len = 0
                for row_idx in range(1, ws.max_row + 1):
                    cell_val = str(ws.cell(row=row_idx, column=col_idx).value or '')
                    if len(cell_val) > max_len:
                        max_len = len(cell_val)
                col_letter = get_column_letter(col_idx)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        # Simpan fail spreadsheet .xlsx murni
        wb.save(laluan_output_excel)
        print(f"[SUCCESS EXCEL CLEANED] Fail Excel tunggal 4-Sheet berjaya disimpan ke: {laluan_output_excel}")

    except Exception as e:
        raise Exception(f"Gagal memproses kemas kini laporan 4-Sheet Excel: {str(e)}")
