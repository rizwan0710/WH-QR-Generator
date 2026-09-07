from tkinter import messagebox

def semak_perbezaan_customer(sv_list, var_customer_auto, icd):
    """
    🌟 SISTEM ALARM SECURITY PINTAR (DIPERBAIKI) 🌟
    Memeriksa setiap dropdown secara langsung. Hanya mencetuskan alarm amaran jika 
    kotak benar-benar diisi dengan siri Outer Box 'B' yang sah milik customer lain.
    """
    customer_rujukan = ""
    
    for idx, sv_widget in enumerate(sv_list):
        val_semasa = sv_widget.get().strip()
        
        # PEMBERSIHAN PINTAR: Abaikan jika kotak masih kosong atau mengandungi teks penanda lalai (PILIH/CHOOSE/SELECT)
        if not val_semasa or "---" in val_semasa or val_semasa == "":
            continue
            
        # Hanya proses jika kotak benar-benar mengandungi kod siri Outer Box (Bermula huruf B)
        if val_semasa.startswith("B"):
            cust_semasa = icd.dapatkan_customer_dari_outer(val_semasa)
            
            # Tetapkan customer dari kotak pertama yang diisi sebagai rujukan utama Invoice
            if customer_rujukan == "":
                customer_rujukan = cust_semasa
                var_customer_auto.set(customer_rujukan)
            
            # 🚨 ALARM TERCETUS: Menghalang pencampuran jika customer kotak ini tidak sama dengan rujukan utama
            elif cust_semasa != customer_rujukan:
                messagebox.showerror(
                    "🚨 WARNING: DIFFERENT CUSTOMER!", 
                    f"CRITICAL WARNING!\n\n"
                    f"BOX AT 'Outer Box {idx+1}' IS FOR CUSTOMER:\n👉 [{cust_semasa}]\n\n"
                    f"NOT SAME AS CUSTOMER ON THIS INVOICE :\n👉 [{customer_rujukan}].\n\n"
                    f"SYSTEM RESSETING INPUT!",
                    parent=sv_widget.winfo_toplevel() # Dikurung rapi pada tetingkap borang sahaja
                )
                sv_widget.set("---CHOOSE DATA---")
                return False
                
    if customer_rujukan == "":
        var_customer_auto.set("- AUTO DETECT -")
    return True
