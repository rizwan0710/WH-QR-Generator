from PIL import Image, ImageDraw, ImageFont
import os

def muatkan_fon_selamat(nama_fail_utama, saiz):
    """Memuatkan fon sistem secara dinamik dengan perlindungan kalis error fallback."""
    try:
        return ImageFont.truetype(nama_fail_utama, saiz)
    except IOError:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", saiz)
        except TypeError:
            return ImageFont.load_default()

def bina_imej_invoice(img_qr, invoice_no, so_no, outer_seq, outer_qty, seq_inv_spesifik, text_paging, customer=""):
    """
    🌟 REKA BENTUK GRAFIK INVOICE (600 DPI HARDWARE OPTIMIZED TEMPLATE) 🌟
    Ukuran Fizikal  : 80 mm (Lebar) x 40 mm (Tinggi)
    Resolusi Kanvas : 1890 Piksel (Lebar) x 945 Piksel (Tinggi) - Nisbah Tepat 2:1
    Hardware Target : Xprinter XP-420B (Auto-Size & High Sharpness Enabled)
    """
    # 🌟 FORMULA PENGIRAAN MATRIKS SKALA PIKSEL 600 DPI 🌟
    # Kod asal menggunakan w_base=340, h_base=220. Untuk mencapai resolusi sekitar 1890 piksel,
    # kita tingkatkan skala penggandaan dalaman dari '2' kepada faktor ketumpatan tinggi '5.5'
    skala = 5.5
    w_base, h_base = 340, 170 # Nisbah dilaraskan kepada 2:1 (80mm x 40mm) untuk ketepatan fizikal label
    w, h = int(w_base * skala), int(h_base * skala)
    
    imej_kanvas = Image.new("RGB", (w, h), "white")
    lukis = ImageDraw.Draw(imej_kanvas)
    
    # Membesarkan saiz fon (Font Scaling Matrix) secara seimbang mengikut ketumpatan kanvas 600 DPI
    font_data = muatkan_fon_selamat("arial.ttf", int(14 * skala))
    font_bold = muatkan_fon_selamat("arialbd.ttf", int(14 * skala))
    font_header = muatkan_fon_selamat("arialbd.ttf", int(17 * skala))
    font_page = muatkan_fon_selamat("arialbd.ttf", int(13 * skala))
        
    # 1. Bingkai Outline Hitam Luar (Mengekalkan ketebalan mengikut nisbah skala)
    lukis.rectangle([int(12 * skala), int(10 * skala), w - int(12 * skala), h - int(10 * skala)], outline="black", width=int(2.5 * skala))
    
    # 2. Paparan Nama Pelanggan (Customer Corporate Header)
    teks_pelanggan = str(customer).strip().upper() if str(customer).strip() != "NONE" and str(customer).strip() != "" else "INTERNAL/COMBINED"
    lukis.text((int(22 * skala), int(20 * skala)), teks_pelanggan, fill="black", font=font_header)
    
    # 3. Parameter Kedudukan Baris Data Kompak (Asal Susunan Struktur Reka Bentuk Abang)
    start_y = int(52 * skala)  
    row_gap = int(28 * skala)  
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
    
    # 4. 🌟 MEMUATKAN LOGO OHTA PNG LUTSINAR (Mengekalkan Logik Alpha Masking Abang)
    logo_fail = "logo_ohta.png"
    if os.path.exists(logo_fail):
        try:
            img_logo_raw = Image.open(logo_fail)
            logo_w, logo_h = int(60 * skala), int(42 * skala)
            # Menggunakan penapis NEAREST/BILINEAR untuk mengelakkan garisan tepi logo termal kabur pecah
            img_logo_resized = img_logo_raw.resize((logo_w, logo_h), Image.Resampling.BILINEAR)
            
            pos_x, pos_y = int(250 * skala), int(15 * skala)
            
            # Tampal imej logo mengikut format saluran perlindungan Alpha Channel Masking
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
        lukis.text((int(250 * skala), int(22 * skala)), "[ OHTA ]", fill="black", font=font_data)

    # 5. Tampal Gambar QR Code Pasangan Data Bersih (Penapis NEAREST untuk High Density Barcode)
    qr_saiz = int(72 * skala)
    img_qr_resized = img_qr.resize((qr_saiz, qr_saiz), Image.Resampling.NEAREST)  
    imej_kanvas.paste(img_qr_resized, (int(248 * skala), int(62 * skala)))
    
    # 6. Pemformatan Teks Paging Box (BOX 1/1, BOX 1/2) - Sentiasa Di Tengah Bawah Pelekat
    text_box_paging = str(text_paging).upper().replace("PAGE", "BOX")
    bbox = lukis.textbbox((0, 0), text_box_paging, font=font_page)
    lebar_teks = bbox[2] - bbox[0]
    pos_x_tengah = (w - lebar_teks) // 2
    
    lukis.text((pos_x_tengah, int(142 * skala)), text_box_paging, fill="black", font=font_page)
    
    # 🌟 KOREKSI UTAMA UNTUK AUTO-SIZE KEPADATAN PIKSEL TINGGI 🌟
    # Jangan kecilkan balik imej (Hapus imej_kanvas.resize bawah) untuk membiarkan imej kekal 
    # dalam saiz resolusi penuh 600 DPI berskala tinggi, membolehkan Xprinter buat auto-fit yang sangat tajam!
    return imej_kanvas

def susun_ke_kertas_a4(senarai_had):
    """Menyusun kad pelekat ke dalam layout kertas A4 untuk fungsi sekunder cetakan biasa."""
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
