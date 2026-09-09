import os
import sys
import sqlite3
import time
import shutil
from tkinter import messagebox, filedialog
from PIL import Image

def convert_to_crisp_monochrome(pil_img):
    """
    Menukar imej kepada 1-bit monochrome (hitam putih tulen) dengan pecahan threshold yang tajam.
    Ini membuang kesan kabur kelabu (anti-aliasing) pada sempadan tulisan dan petak kod QR.
    """
    try:
        gray_img = pil_img.convert("L")
        bw_img = gray_img.point(lambda x: 0 if x < 140 else 255, mode="1")
        return bw_img
    except Exception as e:
        print(f"Monochrome normalization fallback triggered: {e}")
        return pil_img.convert("1")

def cetak_a4_master(target_data):
    """
    PRINT ENGINE: SINGLE DEFAULT (600 DPI METADATA AUTO-SIZE INJECTED)
    """
    try:
        im = None
        if isinstance(target_data, tuple) and len(target_data) > 0:
            im = target_data
        elif isinstance(target_data, list) and len(target_data) > 0:
            item = target_data
            im = item if isinstance(item, tuple) else item
        else:
            im = target_data
            
        if im is None or not hasattr(im, "save"):
            print("Error: Failed to extract pure image object for Single Print.")
            return False

        crisp_image = convert_to_crisp_monochrome(im)
        temp_file = "temp_print_invoice_default.png"
        
        # PENTING: Menyuntik info ketumpatan 600 DPI supaya Windows Print Driver membaca saiz auto-scale
        crisp_image.save(temp_file, "PNG", dpi=(600, 600))
        
        if sys.platform == "win32":
            os.startfile(temp_file, "print")
            return True
        else:
            os.system(f"lp {temp_file}")
            return True
            
    except Exception as e:
        messagebox.showerror("ERROR", f"FAILED TO PRINT SINGLE: {str(e)}")
        return False

def cetak_a4_batch(senarai_imej_label):
    """
    PRINT ENGINE: MULTI-PAGE BATCH ISOLATION (600 DPI HARDWARE AUTO-SIZE SYNCHRONIZED)
    """
    if not senarai_imej_label:
        messagebox.showwarning("NO DATA", "NO INVOICE LABELS TO PRINT.")
        return False
        
    try:
        temp_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "OHTA_INVOICE_BATCH")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
            
        for idx, item in enumerate(senarai_imej_label):
            img_clean = item if isinstance(item, tuple) else item
            if isinstance(img_clean, Image.Image):
                crisp_page = convert_to_crisp_monochrome(img_clean)
                file_path = os.path.join(temp_dir, f"LABEL_PAGE_{idx+1:03d}.png")
                
                # Memaksa auto-scale 600 DPI pada setiap fail imej kumpulan
                crisp_page.save(file_path, "PNG", dpi=(600, 600))

        if sys.platform == "win32":
            import win32com.client
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.NameSpace(temp_dir)
            items = folder.Items()
            items.InvokeVerbEx("print")
            return True
        else:
            for f in sorted(os.listdir(temp_dir)):
                os.system(f"lp {os.path.join(temp_dir, f)}")
            return True
            
    except Exception as e:
        try:
            import win32api
            for idx, item in enumerate(senarai_imej_label):
                file_path = os.path.join(temp_dir, f"LABEL_PAGE_{idx+1:03d}.png")
                win32api.ShellExecute(0, "print", file_path, None, ".", 0)
                time.sleep(0.15)
            return True
        except:
            messagebox.showerror("BATCH PRINT ERROR", f"FAILED TO GENERATE BATCH PRINT:\n{str(e)}")
            return False

def simpan_a4_master(img_label, invoice_no):
    try:
        im = img_label if isinstance(img_label, tuple) else img_label
        fail_clean = str(invoice_no).replace("/", "-").replace(":", "-").strip()
        path_fail = filedialog.asksaveasfilename(
            initialfile=f"INVOICE_LABEL_{fail_clean}.png", 
            defaultextension=".png", 
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            title="SAVE LABEL GRAPHIC"
        )
        if path_fail:
            im.convert("RGB").save(path_fail, "PNG", quality=100)
            messagebox.showinfo("SUCCESS", "IMAGE SUCCESSFULLY SAVED!")
    except Exception as e:
        messagebox.showerror("ERROR SAVED", f"FAILED TO SAVE IMAGE:\n{str(e)}")

def dapatkan_qty_outer(seq_no):
    if not seq_no or seq_no == "--- PILIH DATA ---":
        return 0
    try:
        with sqlite3.connect("warehouse_data.db", timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM rekod_qr WHERE sequence_no = ?", (str(seq_no).strip(),))
            res = cursor.fetchone()
            if res:
                clean_val = str(res).upper().replace("PCS", "").strip()
                return int(float(clean_val))
            return 0
    except:
        return 0
