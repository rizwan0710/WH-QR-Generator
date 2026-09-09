from PIL import Image, ImageDraw, ImageFont

def muatkan_fon_selamat(nama_fail_utama, saiz):
    """Memuatkan fon sistem secara dinamik dengan perlindungan kalis error fallback."""
    for font_name in [nama_fail_utama, nama_fail_utama.lower(), "Arial.ttf", "arial.ttf", "Arialbd.ttf", "arialbd.ttf"]:
        try:
            return ImageFont.truetype(font_name, saiz)
        except IOError:
            continue
    return ImageFont.load_default()

# FUNGSI REKA BENTUK KAD GRAFIK OUTER PACKING (600 DPI HARDWARE OPTIMIZED)
def bina_imej_outer(img_qr, data_gabungan, seq_outer):
    """
    🎨 600 DPI HIGH-RESOLUTION OUTER BOX DESIGNER 🎨
    Physical Size     : 80 mm (Width) x 40 mm (Height)
    Canvas Resolution : 1890 Pixels (Width) x 900 Pixels (Height) - Exact 2.1:1 Ratio
    Kekalkan 100% kedudukan, koordinat, dan saiz asal abang tetapi dinaikkan resolusi imej ke 600 DPI.
    """
    # 🌟 MATRIKS GANDAAN SKALA RESOLUSI MURNI 🌟
    # Menggandakan resolusi layout asal (420x200) dengan faktor skala 4.5 
    # untuk mencapai kepadatan titik piksel tinggi kalis kabur pada Xprinter
    skala = 4.5
    w_base, h_base = 420, 200  
    w, h = int(w_base * skala), int(h_base * skala)
    
    imej_kanvas = Image.new("RGB", (w, h), "white")
    lukis = ImageDraw.Draw(imej_kanvas)
    
    # Membesarkan saiz fon asal abang secara presisi mengikut nisbah gandaan skala
    font_data = muatkan_fon_selamat("arial.ttf", int(10 * skala))
    font_bold = muatkan_fon_selamat("arialbd.ttf", int(11 * skala))
    font_header = muatkan_fon_selamat("arialbd.ttf", int(13 * skala))
        
    # 1. BINGKAI OUTLINE HITAM LUAR (Ketebalan mengikut nisbah skala gandaan)
    lukis.rectangle([int(10 * skala), int(10 * skala), w - int(10 * skala), h - int(10 * skala)], outline="black", width=int(2 * skala))
    
    # 2. TULIS OUTER SEQUENCE NUMBER DI ATAS TENGAH (Koordinat asal: 145, 15)
    lukis.text((int(145 * skala), int(15 * skala)), str(seq_outer), fill="black", font=font_header)
    
    # 3. LUKIS TAJUK LAJUR BARU (Koordinat asal: start_y = 40)
    start_y = int(40 * skala)
    lukis.text((int(25 * skala), start_y), "Part No", fill="black", font=font_bold)
    lukis.text((int(160 * skala), start_y), "Qty (Pcs )", fill="black", font=font_bold)
    lukis.text((int(320 * skala), start_y), "Box ID", fill="black", font=font_bold)
    
    # 4. MENYENARAIKAN KANDUNGAN DATA SECARA BERBARIS KE BAWAH (Koordinat asal: pos_y = start_y + 22)
    pos_y = start_y + int(22 * skala)
    for idx, item in enumerate(data_gabungan):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            part_inner = str(item[0]).strip()  # Membaca Part No
            qty_inner = str(item[1]).strip()   # Membaca Kuantiti
        else:
            part_inner = str(item).strip()
            qty_inner = ""
            
        if qty_inner:
            qty_inner = qty_inner.upper().replace("PCS", "").strip()
        
        if part_inner and part_inner != "--- PILIH DATA ---" and part_inner != "None" and part_inner != "":
            # Memaparkan nilai Part No asli mengikut koordinat asal abang
            lukis.text((int(25 * skala), pos_y), f"{idx+1}. {part_inner}", fill="black", font=font_data)
            lukis.text((int(175 * skala), pos_y), qty_inner, fill="black", font=font_data)
        else:
            # Jika slot kosong, paparkan nombor baris sahaja
            lukis.text((int(25 * skala), pos_y), f"{idx+1}", fill="black", font=font_data)
            
        pos_y += int(22 * skala)
        
    # 5. TAMPAL GAMBAR QR CODE OUTER DI SEBELAH KANAN DI BAWAH BOX ID (Koordinat asal: 310, start_y + 25)
    # Saiz dikembangkan mengikut skala gandaan, diproses menggunakan penapis NEAREST agar piksel kod QR tajam
    qr_saiz = int(80 * skala)
    img_qr_resized = img_qr.resize((qr_saiz, qr_saiz), Image.Resampling.NEAREST)  
    
    pos_qr_x = int(310 * skala)
    pos_qr_y = start_y + int(25 * skala)
    imej_kanvas.paste(img_qr_resized, (pos_qr_x, pos_qr_y))
    
    # 🌟 KOREKSI UTAMA AUTO-SIZE: Pulangkan imej beresolusi tinggi 1890 px secara terus 
    # tanpa perlu di-resize mengecil semula di bawah, membolehkan driver Xprinter melakukan auto-fit yang tajam!
    return imej_kanvas

def bina_imej_gabungan_akses(img_qr, pilihan_data, seq_outer):
    pilihan_copy = list(pilihan_data)
    while len(pilihan_copy) < 4:
        pilihan_copy.append(("", ""))
    return bina_imej_outer(img_qr, pilihan_copy, seq_outer)
