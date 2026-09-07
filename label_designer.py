from PIL import Image, ImageDraw, ImageFont

def bina_imej_gabungan(img_qr, tarikh, drawing, part, qty, mfg, mac, sequence_no, customer):
    """ENGINE PEREKA GRAFIK INNER BOX (PERFECT SYMMETRIC EDITION)"""
    lebar_kad, tinggi_kad = 380, 385  
    imej_kanvas = Image.new("RGB", (lebar_kad, tinggi_kad), "white")
    lukis = ImageDraw.Draw(imej_kanvas)
    
    try:
        font_regular = ImageFont.truetype("arial.ttf", 12)
        font_bold    = ImageFont.truetype("arialbd.ttf", 12)
        font_header  = ImageFont.truetype("arialbd.ttf", 15)
        font_footer  = ImageFont.truetype("arialbd.ttf", 11)
        font_serial  = ImageFont.truetype("arialbd.ttf", 11)
    except (IOError, TypeError):
        font_regular = ImageFont.load_default()
        font_bold    = ImageFont.load_default()
        font_header  = ImageFont.load_default()
        font_footer  = ImageFont.load_default()
        font_serial  = ImageFont.load_default()

    lukis.rectangle([15, 15, lebar_kad-15, tinggi_kad-15], outline="black", width=2)
    
    lukis.text((25, 23), str(customer).upper().strip(), fill="black", font=font_header)
    lukis.line([15, 45, lebar_kad-15, 45], fill="black", width=2)
    
    lajur_pembahagi_x = 125
    senarai_data = [
        ("Date", str(tarikh)),
        ("Drawing No", str(drawing)),
        ("Part Number", str(part)),
        ("Quantity", str(qty)),
        ("Machine", str(mac))
    ]
    
    y_semasa = 45
    for tajuk, nilai in senarai_data:
        lukis.line([15, y_semasa+28, lebar_kad-15, y_semasa+28], fill="black", width=1)
        lukis.text((25, y_semasa+7), tajuk, fill="black", font=font_bold)
        lukis.line([lajur_pembahagi_x, y_semasa, lajur_pembahagi_x, y_semasa+28], fill="black", width=1)
        lukis.text((lajur_pembahagi_x+10, y_semasa+7), nilai.upper().strip(), fill="black", font=font_regular)
        y_semasa += 28

    lukis.line([15, y_semasa, lebar_kad-15, y_semasa], fill="black", width=2)

    gap_atas_bawah = 15
    pos_qr_y = y_semasa + gap_atas_bawah
    
    img_qr_resized = img_qr.resize((105, 105))
    imej_kanvas.paste(img_qr_resized, (25, pos_qr_y))
    
    pos_teks_qr_y = pos_qr_y + 35
    lukis.text((145, pos_teks_qr_y), "Serial No:", fill="black", font=font_regular)
    lukis.text((145, pos_teks_qr_y+16), str(sequence_no).upper().strip(), fill="black", font=font_serial)

    y_rohs_start = pos_qr_y + 105 + gap_atas_bawah
    
    lukis.line([15, y_rohs_start, lebar_kad-15, y_rohs_start], fill="black", width=1)
    lukis.text((25, y_rohs_start+6), "Complied With ROHS", fill="black", font=font_regular)
    
    y_company_start = y_rohs_start + 26
    lukis.line([15, y_company_start, lebar_kad-15, y_company_start], fill="black", width=1)
    
    teks_kilang = "OHTA PRECISION (M) SDN BHD"
    try:
        lebar_teks_kilang = lukis.textlength(teks_kilang, font=font_footer)
    except AttributeError:
        lebar_teks_kilang = lukis.textsize(teks_kilang, font=font_footer)[0] if hasattr(lukis, 'textsize') else 180
        
    pos_x_center = (lebar_kad - lebar_teks_kilang) // 2
    lukis.text((pos_x_center, y_company_start+6), teks_kilang, fill="black", font=font_footer)
    
    return imej_kanvas
