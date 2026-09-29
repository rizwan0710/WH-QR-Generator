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
    - CRASH FIX: Cleans multiline text anomalies to prevent draw.textlength() failure.
    """
    lebar_canvas = 420
    tinggi_canvas = 430
    canvas = Image.new("RGB", (lebar_canvas, tinggi_canvas), "white")
    draw = ImageDraw.Draw(canvas)
    
    # Maksimum ruang lebar teks (Lebar canvas - padding tepi kanan/kiri)
    lebar_maksimum_teks = lebar_canvas - 50 
    
    try:
        font_path_bold = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segoeuib.ttf")
        font_path_reg = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segoeui.ttf")
        
        # Saiz asal font tajuk/customer
        saiz_font_asal = 13
        font_title = ImageFont.truetype(font_path_bold, saiz_font_asal)
        font_sub_bold = ImageFont.truetype(font_path_bold, 11)
        font_sub_reg = ImageFont.truetype(font_path_reg, 11)
        
        font_rohs_large = ImageFont.truetype(font_path_reg, 13)       
        font_company_large = ImageFont.truetype(font_path_bold, 12)   
    except:
        font_title = font_sub_bold = font_sub_reg = font_rohs_large = font_company_large = ImageFont.load_default()
        font_path_bold = None

    # Meluaskan dimensi sempadan kotak luar mengikut saiz kanvas baharu
    draw.rectangle([(15, 15), (lebar_canvas - 15, tinggi_canvas - 15)], outline="black", width=2)
    
    # 🌟 SANITASI TEKS: Buang sebarang line breaks untuk elakkan crash textlength 🌟
    nama_cust = str(customer).replace("\r", " ").replace("\n", " ").upper().strip()
    # Buang ruang kosong berkembar (double spaces) jika ada
    nama_cust = " ".join(nama_cust.split())
    
    y_mula_jadual = 48
    
    # Fungsi pembantu selamat untuk mengira saiz piksel lebar teks
    def dapatkan_lebar_teks(teks, font_obj):
        # Pastikan string bersih dari newline break sebelum dikira
        teks_bersih = str(teks).replace("\n", " ").strip()
        try:
            return draw.textlength(teks_bersih, font=font_obj)
        except AttributeError:
            if hasattr(draw, 'textsize'):
                return draw.textsize(teks_bersih, font=font_obj)[0]
            return len(teks_bersih) * 7
        except Exception:
            # Fallback jika berlaku ralat luar jangkaan (menggunakan multiline bounding box)
            try:
                bbox = draw.multiline_textbbox((0, 0), teks_bersih, font=font_obj)
                return bbox[2] - bbox[0]
            except:
                return len(teks_bersih) * 7

    # Langkah 1: Semak jika font lalai digunakan (tiada kebolehan menukar font size)
    if font_path_bold is None:
        if len(nama_cust) > 28:
            baris1 = nama_cust[:28].strip()
            baris2 = nama_cust[28:].strip()
            draw.text((25, 20), baris1, fill="black", font=font_title)
            draw.text((25, 36), baris2, fill="black", font=font_title)
            y_mula_jadual = 60
        else:
            draw.text((25, 23), nama_cust, fill="black", font=font_title)
    else:
        # Langkah 2: Proses mengecilkan font secara dinamik (Dynamic Downscaling Loop)
        saiz_font_semasa = saiz_font_asal
        lebar_teks_semasa = dapatkan_lebar_teks(nama_cust, font_title)
        
        # Jika nama panjang, cuba turunkan saiz font sehingga muat dalam satu baris (Min saiz: 9)
        while lebar_teks_semasa > lebar_maksimum_teks and saiz_font_semasa > 9:
            saiz_font_semasa -= 1
            font_title = ImageFont.truetype(font_path_bold, saiz_font_semasa)
            lebar_teks_semasa = dapatkan_lebar_teks(nama_cust, font_title)
            
        # Langkah 3: Jika masih tidak muat pada saiz 9, pecahkan teks secara selamat kepada 2 baris
        if lebar_teks_semasa > lebar_maksimum_teks:
            # Menggunakan saiz font 10 untuk susunan dua baris yang kemas
            font_title = ImageFont.truetype(font_path_bold, 10)
            patah_perkataan = nama_cust.split()
            baris1, baris2 = "", ""
            
            for perkataan in patah_perkataan:
                test_baris1 = f"{baris1} {perkataan}".strip()
                if dapatkan_lebar_teks(test_baris1, font_title) <= lebar_maksimum_teks and not baris2:
                    baris1 = test_baris1
                else:
                    baris2 = f"{baris2} {perkataan}".strip()
            
            draw.text((25, 18), baris1, fill="black", font=font_title)
            draw.text((25, 32), baris2, fill="black", font=font_title)
            y_mula_jadual = 52
        else:
            # Muat dalam satu baris dengan pelarasan saiz font dinamik
            draw.text((25, 23), nama_cust, fill="black", font=font_title)

    # Garisan pembagi bawah nama customer
    draw.line([(15, y_mula_jadual), (lebar_canvas - 15, y_mula_jadual)], fill="black", width=2)
    
    def lukis_baris_jadual(y_atas, y_bawah, tajuk_lajur, nilai_lajur):
        draw.line([(15, y_bawah), (lebar_canvas - 15, y_bawah)], fill="black", width=1)
        draw.line([(135, y_atas), (135, y_bawah)], fill="black", width=1)
        draw.text((25, y_atas + 5), str(tajuk_lajur), fill="black", font=font_sub_bold)
        draw.text((145, y_atas + 5), str(nilai_lajur).strip(), fill="black", font=font_sub_reg)

    # Susun kedudukan dinamik mengikut pembolehubah y_mula_jadual yang baru
    h_baris = 28
    lukis_baris_jadual(y_mula_jadual, y_mula_jadual + h_baris, "Drawing No", drawing)
    lukis_baris_jadual(y_mula_jadual + h_baris, y_mula_jadual + (h_baris * 2), "Part Number", part)
    lukis_baris_jadual(y_mula_jadual + (h_baris * 2), y_mula_jadual + (h_baris * 3), "Quantity", f"{str(qty).upper().replace('PCS','').strip()} PCS")
    lukis_baris_jadual(y_mula_jadual + (h_baris * 3), y_mula_jadual + (h_baris * 4), "Machine", mac)
    lukis_baris_jadual(y_mula_jadual + (h_baris * 4), y_mula_jadual + (h_baris * 5), "Pack Date", tarikh)
    
    # Integrasi Grafik Kod QR Dinamik
    y_pos_qr = y_mula_jadual + (h_baris * 5) + 12
    if img_qr_mentah:
        img_qr_resized = img_qr_mentah.resize((120, 115), Image.Resampling.LANCZOS)
        canvas.paste(img_qr_resized, (25, y_pos_qr))
        
    # Penulisan Blok Serial No & Data Lot No (Sisi kanan Kod QR)
    draw.text((170, y_pos_qr + 10), "Serial No:", fill="black", font=font_sub_bold)
    draw.text((170, y_pos_qr + 25), str(seq_no).strip().upper(), fill="black", font=font_sub_reg)
    
    draw.text((170, y_pos_qr + 50), "Lot No:", fill="black", font=font_sub_bold)
    draw.text((170, y_pos_qr + 65), str(lot_no).strip().upper() if (lot_no and str(lot_no).strip().upper() != "NONE") else "N/A", fill="black", font=font_sub_reg)
    
    # =========================================================================
    # 🌟 BAHAGIAN FOOTER: DIBAIKI KEDUDUKAN DYNAMIC AUTO-CENTER 🌟
    # =========================================================================
    draw.line([(15, 340), (lebar_canvas - 15, 340)], fill="black", width=1)
    draw.text((25, 348), "Complied With ROHS", fill="black", font=font_rohs_large)
    
    draw.line([(15, 380), (lebar_canvas - 15, 380)], fill="black", width=2)
    
    teks_company = "OHTA PRECISION (M) SDN BHD"
    try:
        lebar_teks = draw.textlength(teks_company, font=font_company_large)
    except AttributeError:
        lebar_teks = draw.textsize(teks_company, font=font_company_large)[0] if hasattr(draw, 'textsize') else 200
        
    koordinat_x_center = int((lebar_canvas - lebar_teks) / 2)
    draw.text((koordinat_x_center, 393), teks_company, fill="black", font=font_company_large)
    
    return canvas
