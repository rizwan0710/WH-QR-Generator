# label_invoice_designer.py - FULL FIXED 600 DPI TEMPLATE ENGINE WITH SAFE TRUE-TYPE FALLBACK
from PIL import Image, ImageDraw, ImageFont
import os
import sys

def muatkan_fon_selamat(nama_fail_utama, saiz):
    """Memuatkan fon sistem secara dinamik dengan rujukan berbilang fon TrueType Windows untuk mengelakkan load_default bitmap crash."""
    senarai_fon_sistem = [
        nama_fail_utama,
        "arial.ttf" if "bd" not in nama_fail_utama else "arialbd.ttf",
        "segoeui.ttf" if "bd" not in nama_fail_utama else "segoeuib.ttf",
        "C:\\Windows\\Fonts\\arial.ttf" if "bd" not in nama_fail_utama else "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf" if "bd" not in nama_fail_utama else "C:\\Windows\\Fonts\\segoeuib.ttf"
    ]
    
    for nama_fon in senarai_fon_sistem:
        try:
            return ImageFont.truetype(nama_fon, saiz)
        except (IOError, TypeError):
            continue
            
    # Jika semua TrueType gagal, fallback terakhir baru guna default bitmap
    return ImageFont.load_default()

def bina_imej_invoice(img_qr, invoice_no, so_no, outer_seq, outer_qty, seq_inv_spesifik, text_paging, customer=""):
    """
    🌟 REKA BENTUK GRAFIK INVOICE (600 DPI HARDWARE OPTIMIZED TEMPLATE) 🌟
    Ukuran Fizikal  : 80 mm (Lebar) x 40 mm (Tinggi)
    Resolusi Kanvas : 1890 Piksel (Lebar) x 945 Piksel (Tinggi) - Nisbah Tepat 2:1
    Hardware Target : Xprinter XP-420B (Auto-Size & High Sharpness Enabled)
    """
    # 🌟 FORMULA PENGIRAAN MATRIKS SKALA PIKSEL 600 DPI 🌟
    skala = 5.5
    w_base, h_base = 340, 170 
    w, h = int(w_base * skala), int(h_base * skala)
    
    imej_kanvas = Image.new("RGB", (w, h), "white")
    lukis = ImageDraw.Draw(imej_kanvas)
    
    # Membesarkan saiz fon (Font Scaling Matrix) secara seimbang mengikut ketumpatan kanvas 600 DPI
    font_data = muatkan_fon_selamat("arial.ttf", int(14 * skala))
    font_bold = muatkan_fon_selamat("arialbd.ttf", int(14 * skala))
    font_page = muatkan_fon_selamat("arialbd.ttf", int(13 * skala))
    
    # 1. Bingkai Outline Hitam Luar
    lukis.rectangle([int(12 * skala), int(10 * skala), w - int(12 * skala), h - int(10 * skala)], outline="black", width=int(2.5 * skala))
    
    # 🟢 ENJIN SKALA DAN MULTILINE AUTO-WRAP INVOIS 600 DPI 🟢
    teks_pelanggan = str(customer).strip().upper() if str(customer).strip() != "NONE" and str(customer).strip() != "" else "INTERNAL/COMBINED"
    
    # Tetapkan saiz font yang optimum untuk paparan multiline alamat
    saiz_font_header = 11.5
    if len(teks_pelanggan) > 50:
        saiz_font_header = 8.5  
    elif len(teks_pelanggan) > 35:
        saiz_font_header = 10.0
        
    font_header = muatkan_fon_selamat("arialbd.ttf", int(saiz_font_header * skala))
    
    # Semak jika sistem terpaksa menggunakan Default Font bertabiat kaku
    adakah_fon_lalai = not hasattr(font_header, "getbbox") and not hasattr(font_header, "getsize")
    
    baris_alamat = []
    
    if adakah_fon_lalai:
        # 🌟 STRATEGI ANTI-FAIL EMERGENCY: Pecah rentetan teks secara paksa mengikut had karakter (Kalis Ralat Fon) 🌟
        had_karakter_baris = 30 if saiz_font_header > 10 else 40
        perkataan = teks_pelanggan.split()
        baris_semasa = ""
        for p in perkataan:
            if len(f"{baris_semasa} {p}".strip()) <= had_karakter_baris:
                baris_semasa = f"{baris_semasa} {p}".strip()
            else:
                if baris_semasa:
                    baris_alamat.append(baris_semasa)
                baris_semasa = p
        if baris_semasa:
            baris_alamat.append(baris_semasa)
    else:
        # Algoritma pembahagi baris pintarTrueType (Word Wrapping Engine Asal)
        lebar_maksimum_teks = int(210 * skala)
        perkataan = teks_pelanggan.split()
        baris_semasa = ""
        
        for p in perkataan:
            test_baris = f"{baris_semasa} {p}".strip()
            try:
                lebar_teks_cuba = lukis.textlength(test_baris, font=font_header)
            except AttributeError:
                if hasattr(lukis, 'textsize'):
                    lebar_teks_cuba = lukis.textsize(test_baris, font=font_header)[0]
                else:
                    lebar_teks_cuba = len(test_baris) * (saiz_font_header * skala * 0.55)
                
            if lebar_teks_cuba <= lebar_maksimum_teks:
                baris_semasa = test_baris
            else:
                if baris_semasa:
                    baris_alamat.append(baris_semasa)
                baris_semasa = p
        if baris_semasa:
            baris_alamat.append(baris_semasa)
        
    # Hadkan paparan maksimum 2 baris sahaja untuk mengelakkan pertindihan jadual bawah
    baris_alamat = baris_alamat[:2]
    
    # 2. Lukiskan Barisan Alamat Dinamik (Auto-Centered Y-axis tracking)
    mula_y_header = int(18 * skala)
    jarak_baris_y = int((saiz_font_header + 3) * skala)
    
    for idx_b, baris_teks in enumerate(baris_alamat):
        pos_y_b = mula_y_header + (idx_b * jarak_baris_y)
        lukis.text((int(22 * skala), pos_y_b), baris_teks, fill="black", font=font_header)
    
    # 3. Parameter Kedudukan Baris Data Kompak
    start_y = int(58 * skala)  
    row_gap = int(27 * skala)  
    label_x = int(22 * skala)
    data_x = int(125 * skala)  
    
    senarai_data = [
        ("Invoice No", f":  {str(invoice_no).replace('INV:', '').strip()}"),
        ("SO No", f":  {str(so_no).replace('SO:', '').strip()}"),
        ("Quantity", f":  {str(outer_qty).upper().replace('PCS', '').strip()} PCS")
    ]
    
    for idx, (label, nilai) in enumerate(senarai_data):
        current_y = start_y + (row_gap * idx)
        lukis.text((label_x, current_y), label, fill="black", font=font_data)
        lukis.text((data_x, current_y), nilai, fill="black", font=font_bold)
    
   
    # 4. 🌟 MEMUATKAN LOGO OHTA PNG LUTSINAR (FIXED FOR EXE BUNDLE)
    # Ambil laluan folder tempat fail .exe diletakkan secara dinamik
    if getattr(sys, 'frozen', False):
        folder_aplikasi = os.path.dirname(sys.executable)
    else:
        folder_aplikasi = os.path.dirname(os.path.abspath(__file__))
        
    logo_fail = os.path.join(folder_aplikasi, "logo_ohta.png")
    
    if os.path.exists(logo_fail):
        try:
            img_logo_raw = Image.open(logo_fail)
            logo_w, logo_h = int(60 * skala), int(42 * skala)
            img_logo_resized = img_logo_raw.resize((logo_w, logo_h), Image.Resampling.BILINEAR)
            
            pos_x, pos_y = int(250 * skala), int(15 * skala)
            
            if img_logo_resized.mode == 'RGBA':
                imej_kanvas.paste(img_logo_resized, (pos_x, pos_y), mask=img_logo_resized)
            elif 'transparency' in img_logo_resized.info:
                img_rgba = img_logo_resized.convert("RGBA")
                imej_kanvas.paste(img_rgba, (pos_x, pos_y), mask=img_rgba)
            else:
                imej_kanvas.paste(img_logo_resized, (pos_x, pos_y))
        except Exception:
            lukis.text((int(250 * skala), int(22 * skala)), "[ OHTA LOGO ]", fill="black", font=font_data)
    else:
        # Jika fail gambar tiada di sebelah .exe, paparkan teks backup yang kemas tanpa tanda kurung [ ]
        lukis.text((int(250 * skala), int(22 * skala)), "OHTA", fill="black", font=font_bold)


    # 5. 🌟 QR Code Adjustment
    qr_saiz = int(72 * skala)
    img_qr_resized = img_qr.resize((qr_saiz, qr_saiz), Image.Resampling.LANCZOS)  
    imej_kanvas.paste(img_qr_resized, (int(248 * skala), int(62 * skala)))
    
    # 6. Pemformatan Teks Paging Box (BOX 1/1, BOX 1/2)
    text_box_paging = str(text_paging).upper().replace("PAGE", "BOX")
    try:
        bbox = lukis.textbbox((0, 0), text_box_paging, font=font_page)
        lebar_teks = bbox[2] - bbox[0]
    except AttributeError:
        lebar_teks = lukis.textsize(text_box_paging, font=font_page)[0] if hasattr(lukis, 'textsize') else 150
        
    pos_x_tengah = (w - lebar_teks) // 2
    lukis.text((pos_x_tengah, int(142 * skala)), text_box_paging, fill="black", font=font_page)
    
    return imej_kanvas

def susun_ke_kertas_a4(senarai_had):
    """Menyusun kad pelekat ke dalam layout kertas A4."""
    a4_w, a4_h = 2480, 3508
    kertas_a4 = Image.new("RGB", (a4_w, a4_h), "white")
    
    skala_faktor = 5  
    kad_w_baru = 340 * skala_faktor 
    kad_h_baru = 220 * skala_faktor 
    
    margin_x = (a4_w - kad_w_baru) // 2  
    margin_y = 120  
    jarak_antara_kad = 80  
    
    for idx, kad in enumerate(senarai_had[:4]):
        kertas_a4.paste(kad.resize((kad_w_baru, kad_h_baru), Image.Resampling.LANCZOS), (margin_x, margin_y))
        margin_y += kad_h_baru + jarak_antara_kad
        
    return kertas_a4
