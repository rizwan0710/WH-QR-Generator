import sqlite3

def ambil_outer_tersedia():
    """
    FUNGSI BERASINGAN: Menarik siri Outer Box (B%) yang benar-benar bebas 
    dan mengecualikan (exclude) kod yang sudah didaftarkan pada Invoice (INV-%).
    """
    conn = None
    try:
        conn = sqlite3.connect("warehouse_data.db")
        cursor = conn.cursor()
        
        # 1. Ambil semua siri Outer Box (B%) yang wujud dalam sistem
        cursor.execute("SELECT sequence_no FROM rekod_qr WHERE sequence_no LIKE 'B%'")
        semua_outer = [r[0] for r in cursor.fetchall() if r and r[0]]
        
        # 2. Ambil siri Outer Box yang SUDAH DIGUNAKAN oleh rekod Invoice (INV-%) di lajur machine
        cursor.execute("SELECT machine FROM rekod_qr WHERE sequence_no LIKE 'INV-%'")
        outer_digunakan = [r[0] for r in cursor.fetchall() if r and r[0]]
        
        # 3. TAPISAN SILANG EXCLUDE: Hanya ambil nombor kotak yang belum pernah digunakan
        senarai_bebas = [box for box in semua_outer if box not in outer_digunakan]
        return senarai_bebas
    except Exception as e:
        print(f"Database filter system error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()
