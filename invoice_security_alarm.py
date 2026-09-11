# invoice_security_alarm.py - HARD LOCK SECURITY ALARM ENGINE (3 COMBINED RULES)
import sqlite3
from tkinter import messagebox

def semak_perbezaan_customer(sv_list, var_customer_auto, icd):
    """
    🌟 ENGINE PENGGERA KESELAMATAN INVOIS (3 RULES STRICT COMPLIANCE) 🌟
    Rule 1: Jika input bukan nombor siri Outer Box yang sah -> ERROR
    Rule 2: Jika staf mengimbas kod kotak yang sama dalam satu borang -> ERROR
    Rule 3: Jika kod kotak tersebut sudah pernah digunakan/di-scan dalam invois sebelum ini -> ERROR
    """
    customer_rujukan = ""
    senarai_nilai_diisi = []
    
    # Sambung ke database untuk semakan kegunaan rekod lama (Rule 3)
    try:
        conn = sqlite3.connect("warehouse_data.db", timeout=10)
        cursor = conn.cursor()
    except Exception as e_db:
        print(f"Database lock error: {str(e_db)}")
        return False

    for idx, sv_widget in enumerate(sv_list):
        val_semasa = sv_widget.get().strip().upper()
        
        # Abaikan jika kotak masih kosong atau mengandungi teks penanda lalai
        if not val_semasa or "---" in val_semasa or val_semasa == "":
            continue

        # 🚨 RULE 1: IF BUKAN OUTERBOX SEQUENCE NUMBER -> ERROR
        # Sifat utama nombor siri Outer Box anda wajib bermula dengan huruf 'B' dan biasanya diikuti dengan angka siri (panjang > 5)
        if not val_semasa.startswith("B") or len(val_semasa) < 5:
            messagebox.showerror(
                "🚨 INVALID SEQUENCE NUMBER",
                f"GENERATE FAILED AT 'Outer Box {idx+1}'!\n\n"
                f"The value entered [{val_semasa}] is NOT a valid Outer Box Sequence Number!\n"
                f"Please ensure you are scanning the correct Outer Box label (starts with 'B').",
                parent=sv_widget.winfo_toplevel()
            )
            sv_widget.set("---CHOOSE DATA---")
            conn.close()
            return False

        # 🚨 RULE 2: IF OUTERBOX SAMA (DUPLICATE DALAM FORMBORANG AKTIF) -> ERROR
        if val_semasa in senarai_nilai_diisi:
            messagebox.showerror(
                "🚨 SAME BOX SCAN DETECTED", 
                f"GENERATE FAILED AT 'Outer Box {idx+1}'!\n\n"
                f"You have scanned the SAME Outer Box Sequence Number multiple times on this form:\n"
                f"👉 [{val_semasa}]\n\n"
                f"Every box entry must be unique. System resetting input!",
                parent=sv_widget.winfo_toplevel()
            )
            sv_widget.set("---CHOOSE DATA---")
            conn.close()
            return False
        else:
            senarai_nilai_diisi.append(val_semasa)

        # 🚨 RULE 3: IF OUTERBOX DAH PERNAH SCAN (SUDAH WUJUD DALAM DB) -> ERROR
        # Semak sama ada kod kotak 'B...' ini sudah pernah didaftarkan di dalam rekod data INVOIS ('INV%') sebelum ini
        try:
            cursor.execute("SELECT drawing_no FROM rekod_qr WHERE sequence_no LIKE 'INV%' AND machine = ?", (val_semasa,))
            if cursor.fetchone():
                messagebox.showerror(
                    "🚨 BOX ALREADY USED DETECTED",
                    f"GENERATE FAILED AT 'Outer Box {idx+1}'!\n\n"
                    f"The Outer Box [{val_semasa}] has ALREADY been scanned and linked to another invoice previously!\n"
                    f"You cannot reuse a box that has been shipped out.",
                    parent=sv_widget.winfo_toplevel()
                )
                sv_widget.set("---CHOOSE DATA---")
                conn.close()
                return False
        except Exception as e_sql:
            print(f"SQL checking error: {str(e_sql)}")

        # 🚨 LOGIK TAMBAHAN: SEMAKAN PERBEDAAN CUSTOMER (LOGIK ASAL BORANG)
        cust_semasa = icd.dapatkan_customer_dari_outer(val_semasa)
        if customer_rujukan == "":
            customer_rujukan = cust_semasa
            var_customer_auto.set(customer_rujukan)
        elif cust_semasa != customer_rujukan:
            messagebox.showerror(
                "🚨 WARNING: DIFFERENT CUSTOMER!", 
                f"CRITICAL WARNING AT 'Outer Box {idx+1}'!\n\n"
                f"This box belongs to Customer:\n👉 [{cust_semasa}]\n\n"
                f"Not matching with the Invoice reference Customer:\n👉 [{customer_rujukan}].",
                parent=sv_widget.winfo_toplevel()
            )
            sv_widget.set("---CHOOSE DATA---")
            conn.close()
            return False
            
    conn.close()
    if customer_rujukan == "":
        var_customer_auto.set("- AUTO DETECT -")
    return True
