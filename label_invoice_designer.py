from PIL import Image, ImageDraw, ImageFont
import os

def muatkan_fon_selamat(nama_fail_utama, saiz):
    try:
        return ImageFont.truetype(nama_fail_utama, saiz)
    except IOError:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", saiz)
        except TypeError:
            return ImageFont.load_default()

def bina_imej_invoice(img_qr, invoice_no, so_no, outer_seq, outer_qty, seq_inv_spesifik, text_paging, customer=""):
    """
    🌟 REKA BENTUK GRAFIK INVOICE (KOD 6 UPDATED) 🌟
    Menyelesaikan Isu 1: Membuang latar belakang hitam pada logo PNG lutsinar.
    """
    skala = 2
    w_base, h_base = 340, 220
    w, h = w_base * skala, h_base * skala
    
    imej_kanvas = Image.new("RGB", (w, h), "white")
    lukis = ImageDraw.Draw(imej_kanvas)
    
    font_data = muatkan_fon_selamat("arial.ttf", 13 * skala)
    font_bold = muatkan_fon_selamat("arialbd.ttf", 13 * skala)
    font_header = muatkan_fon_selamat("arialbd.ttf", 15 * skala)
    font_page = muatkan_fon_selamat("arialbd.ttf", 12 * skala)
        
    # 1. Bingkai Outline Hitam Luar
    lukis.rectangle([12 * skala, 10 * skala, w - (12 * skala), h - (10 * skala)], outline="black", width=2 * skala)
    
    # 2. Paparan Nama Pelanggan (Customer Corporate Header)
    teks_pelanggan = str(customer).strip().upper() if str(customer).strip() != "NONE" and str(customer).strip() != "" else "INTERNAL/COMBINED"
    lukis.text((22 * skala, 20 * skala), teks_pelanggan, fill="black", font=font_header)
    
    # 3. Parameter Kedudukan Baris Data Kompak
    start_y = 55 * skala  
    row_gap = 30 * skala  
    label_x = 22 * skala
    data_x = 135 * skala  
    
    senarai_data = [
        ("Invoice No", f":  {str(invoice_no).replace('INV:', '').strip()}"),
        ("SO No", f":  {str(so_no).replace('SO:', '').strip()}"),
        ("Quantity", f":  {str(outer_qty).upper().replace('PCS', '').strip()} PCS")
    ]
    
    for idx, (label, nilai) in enumerate(senarai_data):
        current_y = start_y + (row_gap * idx)
        lukis.text((label_x, current_y), label, fill="black", font=font_data)
        lukis.text((data_x, current_y), nilai, fill="black", font=font_bold)
    
    # 4. 🌟 FIX MUTTAMAD ISU 1: Tampal logo PNG lutsinar dengan Alpha Channel Masking
    logo_fail = "logo_ohta.png"
    if os.path.exists(logo_fail):
        try:
            img_logo_raw = Image.open(logo_fail)
            logo_w, logo_h = 55 * skala, 40 * skala
            img_logo_resized = img_logo_raw.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            
            pos_x, pos_y = 245 * skala, 48 * skala
            
            # Jika imej mempunyai alpha transparency channel (RGBA), gunakannya sebagai MASK
            if img_logo_resized.mode == 'RGBA':
                imej_kanvas.paste(img_logo_resized, (pos_x, pos_y), mask=img_logo_resized)
            elif 'transparency' in img_logo_resized.info:
                img_rgba = img_logo_resized.convert("RGBA")
                imej_kanvas.paste(img_rgba, (pos_x, pos_y), mask=img_rgba)
            else:
                imej_kanvas.paste(img_logo_resized, (pos_x, pos_y))
        except Exception:
            lukis.text((245 * skala, 55 * skala), "[ OHTA LOGO ]", fill="#0033aa", font=font_data)
    else:
        lukis.text((245 * skala, 55 * skala), "[ OHTA ]", fill="gray", font=font_data)

    # 5. Tampal Gambar QR Code Pasangan Data Bersih
    qr_saiz = 85 * skala
    img_qr_resized = img_qr.resize((qr_saiz, qr_saiz), Image.Resampling.LANCZOS)  
    imej_kanvas.paste(img_qr_resized, (235 * skala, 98 * skala))
    
    # 6. Pemformatan Teks Paging Box (BOX 1/1, BOX 1/2) - Sentiasa Di Tengah Bawah Pelekat
    text_box_paging = str(text_paging).upper().replace("PAGE", "BOX")
    bbox = lukis.textbbox((0, 0), text_box_paging, font=font_page)
    lebar_teks = bbox[2] - bbox[0]
    pos_x_tengah = (w - lebar_teks) // 2
    
    lukis.text((pos_x_tengah, 192 * skala), text_box_paging, fill="black", font=font_page)
    
    return imej_kanvas.resize((w_base, h_base), Image.Resampling.LANCZOS)

def susun_ke_kertas_a4(senarai_had):
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
