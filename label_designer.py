import os
import sys
from PIL import Image, ImageDraw, ImageFont

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def bina_imej_gabungan(img_qr_mentah, tarikh, drawing, part, qty, mfg, mac, seq_no, customer, lot_no=""):
    """
    🖼️ EXECUTIVE LABEL DESIGNER ENGINE (DYNAMIC AUTO-CENTER FOOTER FIX) 🖼️
    - Enlarges canvas height to 430px for maximum structural padding.
    - Centers the factory signature label dynamically using draw.textlength().
    """
    lebar_canvas = 420
    tinggi_canvas = 430
    canvas = Image.new("RGB", (lebar_canvas, tinggi_canvas), "white")
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_path_bold = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segoeuib.ttf")
        font_path_reg = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segoeui.ttf")
        
        font_title = ImageFont.truetype(font_path_bold, 14)
        font_sub_bold = ImageFont.truetype(font_path_bold, 11)
        font_sub_reg = ImageFont.truetype(font_path_reg, 11)
        
        font_rohs_large = ImageFont.truetype(font_path_reg, 13)       
        font_company_large = ImageFont.truetype(font_path_bold, 12)   
    except:
        font_title = font_sub_bold = font_sub_reg = font_rohs_large = font_company_large = ImageFont.load_default()

    # Meluaskan dimensi sempadan kotak luar mengikut saiz kanvas baharu
    draw.rectangle([(15, 15), (lebar_canvas - 15, tinggi_canvas - 15)], outline="black", width=2)
    
    # Tajuk Utama Pendaftaran Syarikat Customer
    draw.text((25, 23), str(customer).upper().strip(), fill="black", font=font_title)
    draw.line([(15, 45), (lebar_canvas - 15, 45)], fill="black", width=2)
    
    def lukis_baris_jadual(y_atas, y_bawah, tajuk_lajur, nilai_lajur):
        draw.line([(15, y_bawah), (lebar_canvas - 15, y_bawah)], fill="black", width=1)
        draw.line([(135, y_atas), (135, y_bawah)], fill="black", width=1)
        draw.text((25, y_atas + 5), str(tajuk_lajur), fill="black", font=font_sub_bold)
        draw.text((145, y_atas + 5), str(nilai_lajur).strip(), fill="black", font=font_sub_reg)

    lukis_baris_jadual(45, 73, "Pack Date", tarikh)
    lukis_baris_jadual(73, 101, "Drawing No", drawing)
    lukis_baris_jadual(101, 129, "Part Number", part)
    lukis_baris_jadual(129, 157, "Quantity", f"{str(qty).upper().replace('PCS','').strip()} PCS")
    lukis_baris_jadual(157, 185, "Machine", mac)
    
    # Integrasi Grafik Kod QR Dinamik
    if img_qr_mentah:
        img_qr_resized = img_qr_mentah.resize((125, 120), Image.Resampling.LANCZOS)
        canvas.paste(img_qr_resized, (25, 200))
        
    # Penulisan Blok Serial No & Data Lot No (Sisi kanan Kod QR)
    draw.text((170, 215), "Serial No:", fill="black", font=font_sub_bold)
    draw.text((170, 230), str(seq_no).strip().upper(), fill="black", font=font_sub_reg)
    
    draw.text((170, 255), "Lot No:", fill="black", font=font_sub_bold)
    draw.text((170, 270), str(lot_no).strip().upper() if (lot_no and str(lot_no).strip().upper() != "NONE") else "N/A", fill="black", font=font_sub_reg)
    
    # =========================================================================
    # 🌟 BAHAGIAN FOOTER: DIBAIKI KEDUDUKAN DYNAMIC AUTO-CENTER 🌟
    # =========================================================================
    # Garisan ROHS diletakkan pada Y: 340
    draw.line([(15, 340), (lebar_canvas - 15, 340)], fill="black", width=1)
    draw.text((25, 348), "Complied With ROHS", fill="black", font=font_rohs_large)
    
    # Garisan penutup bawah ditolak ke Y: 380 (Memberikan ruang tinggi baris sebanyak 40px!)
    draw.line([(15, 380), (lebar_canvas - 15, 380)], fill="black", width=2)
    
    # 🌟 KOREKSI UTAMA: Kira kelebaran tulisan teks secara dinamik untuk center murni 🌟
    teks_company = "OHTA PRECISION (M) SDN BHD"
    
    try:
        # Gunakan textlength() jika disokong oleh Pillow versi baru anda
        lebar_teks = draw.textlength(teks_company, font=font_company_large)
    except AttributeError:
        # Fallback sekiranya menggunakan Pillow versi lama
        lebar_teks = draw.textsize(teks_company, font=font_company_large)[0] if hasattr(draw, 'textsize') else 200
        
    # Formula tengah: (Jumlah lebar canvas - lebar teks tulisan) dibahagi 2
    koordinat_x_center = int((lebar_canvas - lebar_teks) / 2)
    
    # Cetak nama syarikat tepat di posisi tengah-tengah kotak (Y: 393) secara seimbang!
    draw.text((koordinat_x_center, 393), teks_company, fill="black", font=font_company_large)
    
    return canvas
