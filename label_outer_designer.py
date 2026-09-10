# label_outer_designer.py
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
    """
    # Matriks gandaan skala resolusi tinggi murni
    skala = 4.5
    w_base, h_base = 420, 200  
    w, h = int(w_base * skala), int(h_base * skala)
    
    imej_kanvas = Image.new("RGB", (w, h), "white")
    lukis = ImageDraw.Draw(imej_kanvas)
    
    # 📏 SAIZ FON DIOPTIMUMKAN KE 13PT (MAKSIMUM CLEAR & KALIS BERTINDIH)
    font_data = muatkan_fon_selamat("arial.ttf", int(13 * skala))      # Saiz tulisan data dinaikkan ke 13pt
    font_bold = muatkan_fon_selamat("arialbd.ttf", int(14 * skala))    # Saiz tulisan header dinaikkan ke 14pt
    font_header = muatkan_fon_selamat("arialbd.ttf", int(16 * skala))    # Sequence No Atas Tengah kekal 16pt
        
    # 1. BINGKAI OUTLINE HITAM LUAR
    lukis.rectangle([int(10 * skala), int(10 * skala), w - int(10 * skala), h - int(10 * skala)], outline="black", width=int(2 * skala))
    
    # 2. TULIS OUTER SEQUENCE NUMBER DI ATAS TENGAH (AUTO-CENTERING LOGIC)
    teks_seq = str(seq_outer)
    bbox_seq = lukis.textbbox((0, 0), teks_seq, font=font_header)
    lebar_seq = bbox_seq[2] - bbox_seq[0]
    pos_seq_x = (w - lebar_seq) // 2
    lukis.text((pos_seq_x, int(15 * skala)), teks_seq, fill="black", font=font_header)
    
    # 3. LUKIS TAJUK LAJUR (ANJAKAN KANAN SEJAJAR DENGAN SAID QR CODE)
    start_y = int(45 * skala)
    lukis.text((int(25 * skala), start_y), "Part No", fill="black", font=font_bold)
    lukis.text((int(215 * skala), start_y), "Qty (Pcs)", fill="black", font=font_bold) # Kedudukan rapat ke QR
    lukis.text((int(320 * skala), start_y), "Box ID", fill="black", font=font_bold)
    
    # 4. MENYENARAIKAN KANDUNGAN DATA SECARA BERBARIS KE BAWAH (JARAK AMAN VERTIKAL 26)
    pos_y = start_y + int(26 * skala) # Dinaikkan ke 26 sebagai padding keselamatan vertikal
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
            # Pengehad selamat teks 25 karakter maksimum (Safe String Guard)
            if len(part_inner) > 25:
                part_display = part_inner[:25]
            else:
                part_display = part_inner
                
            # Cetakan teks pada saiz 13pt tanpa risiko bertindih horizontal/vertikal
            lukis.text((int(25 * skala), pos_y), f"{idx+1}. {part_display}", fill="black", font=font_data)
            lukis.text((int(225 * skala), pos_y), qty_inner, fill="black", font=font_data) 
        else:
            # Jika slot kosong, paparkan nombor baris sahaja
            lukis.text((int(25 * skala), pos_y), f"{idx+1}", fill="black", font=font_data)
            
        pos_y += int(26 * skala) # Lonjakan baris bawah dianjak selamat mengikut skala fon 13pt
        
    # 5. TAMPAL GAMBAR QR CODE OUTER DI SEBELAH KANAN DI BAWAH BOX ID (KEKALKAN SAIZ ASAL QR)
    qr_saiz = int(80 * skala)
    img_qr_resized = img_qr.resize((qr_saiz, qr_saiz), Image.Resampling.NEAREST)  
    
    pos_qr_x = int(310 * skala)
    pos_qr_y = start_y + int(25 * skala)
    imej_kanvas.paste(img_qr_resized, (pos_qr_x, pos_qr_y))
    
    return imej_kanvas

def bina_imej_gabungan_akses(img_qr, pilihan_data, seq_outer):
    pilihan_copy = list(pilihan_data)
    while len(pilihan_copy) < 4:
        pilihan_copy.append(("", ""))
    return bina_imej_outer(img_qr, pilihan_copy, seq_outer)
