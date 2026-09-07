def preview_outer_terpilih(jadual, root):
    import qrcode
    import label_outer_designer as lod  # Memanggil fail pereka grafik landscape baru
    
    semua_item = jadual.get_children()
    item_ditanda = []
    for item in semua_item:
        nilai_baris = jadual.item(item)['values']
        if nilai_baris[0] == "☑":
            item_ditanda.append(nilai_baris)
            
    if not item_ditanda:
        messagebox.showwarning("REMINDER", "CLICK THE BOX [☐] FOR CHOOSING DATA!")
        return
        
    for n in item_ditanda:
        # PENTING: Mengambil indeks data yang tepat dari lajur grid database
        seq_outer = str(n[2])             # Lajur Outer Sequence No (Indeks 2)
        raw_inner_sequences = str(n[7])   # Lajur Linked Inner Sequences (Indeks 7)
        
        # Jana gambar QR Code Outer berdasarkan nilai siri
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(seq_outer)
        qr.make(fit=True)
        img_qr_mentah = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        
        # Hantar rentetan teks Linked Inner ke fail lukisan grafik kita
        img_gabung = lod.bina_imej_outer(img_qr_mentah, [raw_inner_sequences], seq_outer)
        
        # Paparkan ke dalam tetingkap popup pratonton yang baharu
        tingkap_popup = tk.Toplevel(root)
        tingkap_popup.title("OUTER PACKING LABEL PREVIEW")
        tingkap_popup.geometry("460x280")
        
        from PIL import ImageTk, Image
        frame_skrol = tk.Frame(tingkap_popup)
        frame_skrol.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        kanvas = tk.Canvas(frame_skrol, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(frame_skrol, orient=tk.VERTICAL, command=kanvas.yview)
        frame_imej = tk.Frame(kanvas)
        
        kanvas.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        kanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        kanvas.create_window((10, 0), window=frame_imej, anchor="nw")
        
        cache_file = "temp_cache_outer_db.png"
        img_gabung.save(cache_file)
        img_buka = Image.open(cache_file)
        img_tk = ImageTk.PhotoImage(img_buka)
        
        label_gambar = tk.Label(frame_imej, image=img_tk, bg="white")
        label_gambar.image = img_tk
        label_gambar.pack()
        
        frame_imej.update_idletasks()
        kanvas.config(scrollregion=kanvas.bbox("all"))
        
        # Sediakan butang Cetak dan Simpan yang merujuk terus ke fungsi form_outer_packing
        frame_btn = tk.Frame(tingkap_popup)
        frame_btn.pack(pady=10)
        
        import form_outer_packing as fop
        tk.Button(frame_btn, text="PRINT ", command=lambda ig=img_gabung: fop.cetak_qr(ig), bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=14).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn, text="SAVE ", command=lambda ig=img_gabung, so=seq_outer: fop.simpan_qr_manual(ig, so), bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=14).pack(side=tk.LEFT, padx=10)
