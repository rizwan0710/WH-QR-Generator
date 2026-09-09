import os
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import invoice_print_manager  # Pautan enjin cetak pukal Windows Photo Wizard

# Rekabentuk gaya butang rata terstandarisasi mengikut rujukan gambar
BTN_STYLE = {"font": ("Segoe UI", 9, "bold"), "fg": "white", "relief": "flat", "height": 2, "cursor": "hand2"}

def laksanakan_windows_photo_wizard_tunggal(image_list):
    """
    🖨️ WINDOWS PHOTO PRINTING WIZARD INTERFACE 🖨️
    Menyimpan semua imej ke folder sementara dan melancarkan tetingkap
    'Print Pictures' terbina dalam Windows secara pukal dengan butang Next/Prev.
    """
    if not image_list:
        return False
        
    try:
        temp_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "OHTA_GLOBAL_BATCH_PRINT")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        else:
            for f in os.listdir(temp_dir):
                try: os.remove(os.path.join(temp_dir, f))
                except: pass

        for idx, img_obj in enumerate(image_list):
            # Pengendalian kalis error sekiranya data dihantar dalam struktur tuple
            actual_img = img_obj[0] if isinstance(img_obj, (list, tuple)) else img_obj
                
            file_path = os.path.join(temp_dir, f"STIKER_PAGE_{idx+1:03d}.png")
            actual_img.convert("RGB").save(file_path, "PNG")

        if sys.platform == "win32" and os.path.exists(temp_dir):
            import win32com.client
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.NameSpace(temp_dir)
            items = folder.Items()
            items.InvokeVerbEx("Print")
            return True
        else:
            return False
            
    except Exception as e_wizard:
        print(f"Windows Photo Wizard error: {str(e_wizard)}")
        try:
            import win32api
            for idx, img_obj in enumerate(image_list):
                actual_img = img_obj[0] if isinstance(img_obj, (list, tuple)) else img_obj
                file_path = os.path.join(temp_dir, f"STIKER_PAGE_{idx+1:03d}.png")
                win32api.ShellExecute(0, "print", file_path, None, ".", 0)
                time.sleep(0.15)
            return True
        except:
            return False

def buka_popup_database_pukal_seragam(parent_window, img_list_raw, is_outer=False, is_invoice=False):
    """
    🌟 STANDARDIZED GLOBAL BATCH SLIDER INTERFACE 🌟
    Digunakan secara kongsi oleh Inner, Outer, dan Invoice apabila melihat pelbagai data dari pangkalan data.
    Menyelaraskan rupa bentuk 4 butang dan warna eksak 100% sebijik mengikut gambar rujukan.
    """
    if not img_list_raw:
        messagebox.showwarning("WARNING", "No printable labels found in the selection scope!", parent=parent_window)
        return

    # Normalisasi data imej bagi mengelakkan AttributeError semasa proses resize
    normalized_images = []
    for item in img_list_raw:
        if isinstance(item, (list, tuple)) and len(item) > 0:
            normalized_images.append(item[0])
        else:
            normalized_images.append(item)

    total_labels = len(normalized_images)
    current_index = 0

    popup_window = tk.Toplevel(parent_window)
    popup_window.title("BATCH PREVIEW PANEL")
    popup_window.geometry("560x540+420+120")
    popup_window.configure(bg="#F8F9FA")
    popup_window.grab_set()

    # Tajuk header mengikut warna standard
    lbl_header = tk.Label(popup_window, text="", font=("Segoe UI", 10, "bold"), fg="#10B981", bg="#F8F9FA")
    lbl_header.pack(pady=12)

    frame_canvas_container = tk.Frame(popup_window, bg="white", bd=1, relief="groove")
    frame_canvas_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=5)
    
    label_image_viewport = tk.Label(frame_canvas_container, bg="white")
    label_image_viewport.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    def refresh_wizard_viewport():
        nonlocal current_index
        idx = current_index
        
        lbl_header.config(text=f"BATCH PREVIEW PANEL  |  LABEL COUNTER: {idx + 1}/{total_labels}")
        img_target = normalized_images[idx]
        
        # Penyelarasan dimensi saiz mengikut jenis entiti kotak
        if is_outer or is_invoice:
            resized_w, resized_h = 420, 240
        else:
            resized_w, resized_h = 360, 260
            
        try:
            img_scaled = img_target.resize((resized_w, resized_h), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_scaled)
            label_image_viewport.config(image=img_tk, text="")
            label_image_viewport.image = img_tk 
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
        """Cetak stiker tunggal aktif yang sedang dipaparkan di skrin menggunakan print master"""
        img_aktif = normalized_images[current_index]
        invoice_print_manager.cetak_a4_master(img_aktif)

    def trigger_unified_batch_print():
        """Melancarkan wizard cetakan Windows Photo untuk kesemua imej kelompok sekaligus"""
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

    # ─── 1. BAR NAVIGASI ATAS (PREV & NEXT SEBIJIK KOD WARNA SLATE SLIDER) ───
    frame_navigation_bar = tk.Frame(popup_window, bg="#F8F9FA")
    frame_navigation_bar.pack(pady=5)
    
    btn_prev = tk.Button(frame_navigation_bar, text="◀ PREV", command=slide_previous_page, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_prev.pack(side=tk.LEFT, padx=8)
    
    btn_next = tk.Button(frame_navigation_bar, text="NEXT ▶", command=slide_next_page, bg="#34495E", fg="white", font=("Segoe UI", 9, "bold"), width=13, relief="flat", cursor="hand2")
    btn_next.pack(side=tk.LEFT, padx=8)

    # ─── 2. BARIS BUTANG KAWALAN UTAMA (EXACT MATCH WARNA & EMOJI 100% CUN) ───
    frame_action_footer = tk.Frame(popup_window, bg="#F8F9FA")
    frame_action_footer.pack(pady=15, side=tk.BOTTOM, fill=tk.X, padx=20)
    
    # Penerapan kod hex warna tepat dari gambar rujukan: #2ECC71, #10B981, #E65100, #34495E
    tk.Button(frame_action_footer, text="🖨️ PRINT CURRENT", command=trigger_single_print, bg="#2ECC71", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_action_footer, text="🖨️ PRINT ALL", command=trigger_unified_batch_print, bg="#10B981", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_action_footer, text="💾 SAVE ALL", command=trigger_batch_save, bg="#E65100", **BTN_STYLE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    tk.Button(frame_action_footer, text="❌ CLOSE", command=popup_window.destroy, bg="#34495E", **BTN_STYLE).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=4)

    refresh_wizard_viewport()
