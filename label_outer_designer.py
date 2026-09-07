from PIL import Image, ImageDraw, ImageFont

# FUNGSI REKA BENTUK KAD GRAFIK OUTER PACKING (LANDSCAPE - UPDATED: PART NO INSTEAD OF SEQ NO)
def bina_imej_outer(img_qr, data_gabungan, seq_outer):
    # Format Landscape (Lebar x Tinggi): Ukuran memanjang mendatar
    w, h = 420, 200  
    imej_kanvas = Image.new("RGB", (w, h), "white")
    lukis = ImageDraw.Draw(imej_kanvas)
    
    try:
        font_data = ImageFont.truetype("arial.ttf", 10)
        font_bold = ImageFont.truetype("arialbd.ttf", 11)
        font_header = ImageFont.truetype("arialbd.ttf", 13)
    except (IOError, TypeError):
        font_data = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_header = ImageFont.load_default()
        
    # 1. BINGKAI OUTLINE HITAM LUAR
    lukis.rectangle([10, 10, w-10, h-10], outline="black", width=2)
    
    # 2. TULIS OUTER SEQUENCE NUMBER DI ATAS TENGAH
    lukis.text((145, 15), str(seq_outer), fill="black", font=font_header)
    
    # 3. LUKIS TAJUK LAJUR BARU (🌟 KEMASKINI: "Sequence No" diganti dengan "Part No" 🌟)
    start_y = 40
    lukis.text((25, start_y), "Part No", fill="black", font=font_bold)
    lukis.text((160, start_y), "Qty (Pcs )", fill="black", font=font_bold)
    lukis.text((320, start_y), "Box ID", fill="black", font=font_bold)
    
    # 4. MENYENARAIKAN KANDUNGAN DATA SECARA BERBARIS KE BAWAH
    pos_y = start_y + 22
    for idx, item in enumerate(data_gabungan):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            part_inner = str(item[0]).strip()  # 🌟 Membaca Part No
            qty_inner = str(item[1]).strip()   # Membaca Kuantiti
        else:
            part_inner = str(item).strip()
            qty_inner = ""
            
        if qty_inner:
            qty_inner = qty_inner.upper().replace("PCS", "").strip()
        
        if part_inner and part_inner != "--- PILIH DATA ---" and part_inner != "None" and part_inner != "":
            # Memaparkan nilai Part No asli (Contoh: 1. A09-XYZ)
            lukis.text((25, pos_y), f"{idx+1}. {part_inner}", fill="black", font=font_data)
            lukis.text((175, pos_y), qty_inner, fill="black", font=font_data)
        else:
            # Jika slot kosong, paparkan nombor baris sahaja
            lukis.text((25, pos_y), f"{idx+1}", fill="black", font=font_data)
            
        pos_y += 22
        
    # 5. TAMPAL GAMBAR QR CODE OUTER DI SEBELAH KANAN DI BAWAH BOX ID
    img_qr_resized = img_qr.resize((80, 80))  
    imej_kanvas.paste(img_qr_resized, (310, start_y + 25))
    
    return imej_kanvas

def bina_imej_gabungan_akses(img_qr, pilihan_data, seq_outer):
    pilihan_copy = list(pilihan_data)
    while len(pilihan_copy) < 4:
        pilihan_copy.append(("", ""))
    return bina_imej_outer(img_qr, pilihan_copy, seq_outer)
