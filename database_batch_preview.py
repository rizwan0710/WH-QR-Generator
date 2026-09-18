import os
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk

# Rekabentuk gaya butang rata terstandarisasi mengikut rujukan gambar
BTN_STYLE = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

def laksanakan_windows_photo_wizard_tunggal(image_list):
    """
    🖨️ MUTTAMAD WINDOWS PHOTO WIZARD ENJIN SINGLE WINDOW 🖨️
    Menyimpan semua imej ke folder sementara dan melancarkan HANYA SATU tetingkap
    cetakan 'Print Pictures' asli Windows dengan butang Next/Prev bersiri (1 of 8 pages).
    """
    if not image_list:
        return False
        
    try:
        # Menetapkan direktori cetakan sementara khusus
        temp_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "OHTA_GLOBAL_BATCH_PRINT")
        
        # Wajib bersihkan folder setiap kali print pukal ditekan supaya fail lama tidak bertindih
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                try: os.remove(os.path.join(temp_dir, f))
                except: pass
        else:
            os.makedirs(temp_dir)

        # Simpan fail gambar PNG dengan susunan nama berindeks yang kemas
        for idx, img_obj in enumerate(image_list):
            actual_img = img_obj
            while isinstance(actual_img, (list, tuple)) and len(actual_img) > 0:
                actual_img = actual_img[0]
                
            if hasattr(actual_img, "save"):
                file_path = os.path.join(temp_dir, f"STIKER_PAGE_{idx+1:03d}.png")
                actual_img.convert("RGB").save(file_path, "PNG")

        # 🌟 TEKNIK MUTTAMAD: Memaksa Windows membuka 1 Window sahaja mengikut cara asal anda 🌟
        if sys.platform == "win32" and os.path.exists(temp_dir) and len(os.listdir(temp_dir)) > 0:
            import win32com.client
            import pythoncom
            
            # Mulakan sambungan thread COM dengan selamat untuk mengelakkan ralat 'Access is denied'
            pythoncom.CoInitialize()
            
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.NameSpace(temp_dir)
            
            # Mengambil keseluruhan fail di dalam folder sebagai satu koleksi item berpusat
            items = folder.Items()
            
            # Menggunakan VerbEx 'Print' pada tahap koleksi item untuk mengunci 1 Window dialog sahaja
            items.InvokeVerbEx("Print")
            return True
        else:
            return False
            
    except Exception as e_wizard:
        print(f"Windows Photo Wizard error: {str(e_wizard)}")
        
        # Pilihan keselamatan kedua secara berturutan jika kaedah utama disekat sistem operasi
        try:
            import win32api
            if os.path.exists(temp_dir):
                win32api.ShellExecute(0, "print", temp_dir, None, ".", 0)
                return True
        except Exception as e_alt:
            print(f"Alternative print system failed: {str(e_alt)}")
            return False

def buka_popup_database_pukal_seragam(parent_window, img_list_raw, is_outer=False, is_invoice=False):
    """
    🌟 STANDARDIZED GLOBAL BATCH SLIDER INTERFACE - FULL FIXED 🌟
    Digunakan secara kongsi oleh Inner, Outer, dan Invoice apabila melihat pelbagai data dari pangkalan data.
    Mengunci aspek nisbah asal label supaya tidak melebar atau penyek pada mod multiple.
    """
    if not img_list_raw:
        messagebox.showwarning("WARNING", "No printable labels found in the selection scope!", parent=parent_window)
        return

    # Normalisasi data imej untuk membongkar sebarang struktur tuple bertingkat dari database
    normalized_images = []
    for item in img_list_raw:
        actual_img = item
        while isinstance(actual_img, (list, tuple)) and len(actual_img) > 0:
            actual_img = actual_img[0]
        
        if hasattr(actual_img, "resize"):
            normalized_images.append(actual_img)

    total_labels = len(normalized_images)
    current_index = 0

    if total_labels == 0:
        messagebox.showerror("RENDER ERROR", "Gagal mengekstrak objek imej grafik daripada data database!", parent=parent_window)
        return

    popup_window = tk.Toplevel(parent_window)
    popup_window.title("BATCH PREVIEW PANEL")
    popup_window.geometry("560x630+420+40")  # Ketinggian dikekalkan 630 potret untuk kekemasan saiz menegak
    popup_window.configure(bg="#F8F9FA")
    popup_window.grab_set()

    # Tajuk header mengikut warna standard
    lbl_header = tk.Label(popup_window, text="", font=("Segoe UI", 10, "bold"), fg="#10B981", bg="#F8F9FA")
    lbl_header.pack(pady=12)

    # Mengunci saiz kotak putih previu supaya kekal petak potret tegak
    frame_canvas_container = tk.Frame(popup_window, bg="white", bd=1, relief="groove")
    frame_canvas_container.pack(fill=tk.NONE, expand=False, padx=30, pady=5)
    
    label_image_viewport = tk.Label(frame_canvas_container, bg="white")
    label_image_viewport.pack(padx=10, pady=10, expand=False, fill=tk.NONE)

    def refresh_wizard_viewport():
        nonlocal current_index
        idx = current_index
        
        lbl_header.config(text=f"BATCH PREVIEW PANEL  |  LABEL COUNTER: {idx + 1}/{total_labels}")
        img_target = normalized_images[idx]
        
        # Pengecilan dimensi mengikut jenis kotak secara tepat potret asli
        if is_outer or is_invoice:
            resized_w, resized_h = 420, 240
        else:
            resized_w, resized_h = 340, 350
            
        try:
            img_scaled = img_target.resize((resized_w, resized_h), Image.Resampling.LANCZOS)
            img_scaled_tk = ImageTk.PhotoImage(img_scaled)
            label_image_viewport.config(image=img_scaled_tk, text="")
            label_image_viewport.image = img_scaled_tk 
        except Exception as e_render:
            print(f"Render fail context: {e_render}")
            label_image_viewport.config(text="[ IMAGE RENDER ERROR ]", fg="red")
        
        btn_prev.config(state="normal" if idx > 0 else "disabled")
        btn_next.config(state="normal" if idx < total_labels - 1 else "disabled")

    def slide_previous_page():
        nonlocal current_index
        if current_index > 0:
            current_index -= 1
            refresh_wizard_viewport()

    def slide_next_page():
        nonlocal current_index
        if current_index < total_labels - 1:
            current_index += 1
            refresh_wizard_viewport()

    def trigger_single_print():
        """Cetak stiker tunggal aktif yang sedang dipaparkan di skrin"""
        img_aktif = normalized_images[current_index]
        laksanakan_windows_photo_wizard_tunggal([img_aktif])

    def trigger_unified_batch_print():
        """Melancarkan dialog cetakan Windows tunggal untuk kesemua imej kelompok asli PNG"""
        if messagebox.askyesno("CONFIRMATION MESSAGE", f"PROCEED WITH PRINT ALL {total_labels} LABELS IN ONE WINDOW?", parent=popup_window):
            laksanakan_windows_photo_wizard_tunggal(normalized_images)

    def trigger_batch_save():
        target_dir = filedialog.askdirectory(title="CHOOSE FOLDER TO SAVE BATCH IMAGES", parent=popup_window)
        if target_dir:
            try:
                for idx, img_item in enumerate(normalized_images):
                    file_output_path = os.path.join(target_dir, f"BATCH_LABEL_EXPORT_{idx+1}.png")
                    img_item.convert("RGB").save(file_output_path, "PNG")
                messagebox.showinfo("COMPLETE", f"All {total_labels} label assets successfully saved!", parent=popup_window)
            except Exception as e_save:
                messagebox.showerror("STORAGE ERROR", str(e_save), parent=popup_window)

    # ─── 1. BAR NAVIGASI ATAS ───
    frame_navigation_bar = tk.Frame(popup_window, bg="#F8F9FA")
    frame_navigation_bar.pack(pady=5)
    
    btn_prev = tk.Button(frame_navigation_bar, text="◀ PREV", command=slide_previous_page, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_prev.pack(side=tk.LEFT, padx=8)
    
    btn_next = tk.Button(frame_navigation_bar, text="NEXT ▶", command=slide_next_page, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_next.pack(side=tk.LEFT, padx=8)

    # ─── 2. BARIS BUTANG KAWALAN UTAMA ───
    frame_action_footer = tk.Frame(popup_window, bg="#F8F9FA")
    frame_action_footer.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    
    tk.Button(frame_action_footer, text="🖨️ PRINT CURRENT", command=trigger_single_print, bg="#2ECC71", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_action_footer, text="🖨️ PRINT ALL", command=trigger_unified_batch_print, bg="#10B981", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_action_footer, text="💾 SAVE ALL", command=trigger_batch_save, bg="#E65100", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_action_footer, text="❌ CLOSE", command=popup_window.destroy, bg="#34495E", **BTN_STYLE).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)

    refresh_wizard_viewport()
