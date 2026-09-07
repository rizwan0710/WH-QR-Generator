import tkinter as tk
from tkinter import ttk
from PIL import ImageTk

def bina_popup_preview_standalone(parent, img_gabung, seq_outer, cetak_cb, simpan_cb):
    """Membina tetingkap modal pop-up pratinjau imej gred industri (RAM Based)."""
    tingkap = tk.Toplevel(parent)
    tingkap.title(f"PREVIEW - {seq_outer}")
    tingkap.geometry("460x390")
    tingkap.configure(bg="#F8F9FA")
    tingkap.grab_set()
    
    tk.Label(tingkap, text="OUTERBOX LABEL PREVIEW", font=("Segoe UI", 11, "bold"), fg="#0078D7", bg="#F8F9FA").pack(pady=10)
    
    frame_skrol = tk.Frame(tingkap, bg="white", bd=1, relief="groove")
    frame_skrol.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    
    kanvas = tk.Canvas(frame_skrol, highlightthickness=0, bg="white")
    scrollbar_y = ttk.Scrollbar(frame_skrol, orient=tk.VERTICAL, command=kanvas.yview)
    frame_imej = tk.Frame(kanvas, bg="white")
    
    kanvas.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y); kanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    id_tingkap = kanvas.create_window((0, 0), window=frame_imej, anchor="nw")
    
    img_tk = ImageTk.PhotoImage(img_gabung)
    label_gambar = tk.Label(frame_imej, image=img_tk, bg="white")
    label_gambar.image = img_tk  
    label_gambar.pack(padx=10, pady=10)
    
    frame_imej.bind("<Configure>", lambda e: [kanvas.configure(scrollregion=kanvas.bbox("all")), kanvas.itemconfig(id_tingkap, width=kanvas.winfo_width()) if kanvas.winfo_width() > frame_imej.winfo_width() else None])
    
    frame_btn = tk.Frame(tingkap, bg="#F8F9FA")
    frame_btn.pack(pady=15, side=tk.BOTTOM)
    
    tk.Button(frame_btn, text="PRINT", command=cetak_cb, bg="#198754", fg="white", font=("Segoe UI", 10, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=8)
    tk.Button(frame_btn, text="SAVE", command=simpan_cb, bg="#FF9800", fg="white", font=("Segoe UI", 10, "bold"), width=14, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=8)
