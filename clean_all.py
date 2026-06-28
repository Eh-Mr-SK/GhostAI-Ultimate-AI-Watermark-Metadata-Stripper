"""
🚀 Ultimate AI Content Cleaner - Videos & Images
================================================
Removes visible watermarks (Gemini/Veo star, Runway logo) and strips ALL metadata
from both videos and images. Perfect for Instagram Reels, TikTok, and social media.

Features:
- Smart crop & scale watermark removal (100% clean, no artifacts)
- Complete metadata stripping (EXIF, XMP, IPTC, C2PA, GPS, camera info)
- Batch processing for folders with mixed content
- Supports: MP4, MOV, MKV, AVI, WEBM, JPG, JPEG, PNG, WEBP, HEIC, BMP, TIFF
"""
import os
import sys
import subprocess
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import piexif
from tqdm import tqdm
from colorama import init, Fore, Style
import argparse
from datetime import datetime
import random

init()

# Supported formats
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".tiff", ".tif"}


def strip_image_metadata(input_path, output_path):
    """
    Removes ALL metadata from an image while preserving quality.
    This includes: EXIF, XMP, IPTC, ICC profiles, comments, thumbnails, GPS data, etc.
    """
    try:
        # Open image
        img = Image.open(input_path)
        
        # Get the raw pixel data (strips all metadata)
        data = list(img.getdata())
        
        # Create a new image with the same mode and size (no metadata)
        img_clean = Image.new(img.mode, img.size)
        img_clean.putdata(data)
        
        # Handle different formats
        ext = Path(output_path).suffix.lower()
        
        if ext in ['.jpg', '.jpeg']:
            # Save JPEG with maximum quality, no EXIF
            img_clean.save(output_path, 'JPEG', quality=95, optimize=True)
        elif ext == '.png':
            # Save PNG with compression
            img_clean.save(output_path, 'PNG', optimize=True)
        elif ext == '.webp':
            # Save WebP with high quality
            img_clean.save(output_path, 'WEBP', quality=95)
        else:
            # Generic save
            img_clean.save(output_path)
        
        return True
    except Exception as e:
        raise Exception(f"Image processing error: {e}")


def remove_image_watermark(input_path, output_path, crop_right=280, crop_bottom=280):
    """
    Removes corner watermark from image by cropping and scaling back.
    Maintains original aspect ratio to prevent stretching.
    Also strips all metadata.
    """
    try:
        img = Image.open(input_path)
        original_size = img.size  # (width, height)
        w, h = original_size
        
        # Determine crop boundaries while preserving the exact aspect ratio
        target_ar = w / h
        max_w = w - crop_right
        max_h = h - crop_bottom
        
        new_w = max_w
        new_h = int(round(new_w / target_ar))
        
        if new_h > max_h:
            new_h = max_h
            new_w = int(round(new_h * target_ar))
            
        # Crop from top-left (removes right and bottom corners without aspect distortion)
        cropped = img.crop((0, 0, new_w, new_h))
        
        # Scale back to original dimensions using high-quality Lanczos resampling
        scaled = cropped.resize(original_size, Image.LANCZOS)
        
        # Save without any metadata
        data = list(scaled.getdata())
        img_clean = Image.new(scaled.mode, scaled.size)
        img_clean.putdata(data)
        
        ext = Path(output_path).suffix.lower()
        if ext in ['.jpg', '.jpeg']:
            img_clean.save(output_path, 'JPEG', quality=95, optimize=True)
        elif ext == '.png':
            img_clean.save(output_path, 'PNG', optimize=True)
        elif ext == '.webp':
            img_clean.save(output_path, 'WEBP', quality=95)
        else:
            img_clean.save(output_path)
        
        return True
    except Exception as e:
        raise Exception(f"Image watermark removal error: {e}")


def remove_video_watermark(input_path, output_path, crop_right=280, crop_bottom=280):
    """
    Removes corner watermark from video by cropping and scaling back.
    Maintains original aspect ratio to prevent stretching.
    Also strips all metadata.
    """
    input_path = str(input_path)
    output_path = str(output_path)
    
    # Get video dimensions
    probe_cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=s=x:p=0",
        input_path
    ]
    result = subprocess.run(probe_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Cannot read video dimensions")
    
    w, h = map(int, result.stdout.strip().split('x'))
    
    # Determine crop boundaries while preserving the exact aspect ratio
    target_ar = w / h
    max_w = w - crop_right
    max_h = h - crop_bottom
    
    new_w = max_w
    new_h = int(round(new_w / target_ar))
    
    if new_h > max_h:
        new_h = max_h
        new_w = int(round(new_h * target_ar))
        
    # Ensure they are even integers for FFmpeg (h264 restriction)
    new_w = (new_w // 2) * 2
    new_h = (new_h // 2) * 2
    
    # FFmpeg: crop, scale back, strip metadata
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"crop={new_w}:{new_h}:0:0,scale={w}:{h}:flags=lanczos",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map_metadata", "-1",
        "-fflags", "+bitexact",
        "-flags", "+bitexact",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr.decode()[-300:]}")
    
    return True


def strip_video_metadata_only(input_path, output_path):
    """
    Strips metadata from video without cropping (for videos without visible watermark).
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map_metadata", "-1",
        "-fflags", "+bitexact",
        "-flags", "+bitexact",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr.decode()[-300:]}")
    
    return True


def get_clean_output_filename(file_path, is_video=False):
    """
    Checks if the filename contains AI-related keywords or 'generated' tags.
    If so, renames it to a camera-style format (e.g., IMG_YYYYMMDD_HHMMSS or VID_YYYYMMDD_HHMMSS).
    Otherwise, returns the sanitized original filename.
    """
    name = file_path.stem
    ext = file_path.suffix.lower()
    
    # Common AI/Generated/Created keywords in filenames
    ai_keywords = [
        "gemini", "veo", "runway", "ai-generated", "ai_generated", "generated", 
        "midjourney", "sora", "luma", "kling", "pika", "flux", "dalle", "dall-e",
        "copilot", "bing", "stable_diffusion", "stablediffusion", "dreammachine",
        "synthesized", "creator", "photoshop", "firefly", "chatgpt", "openai", 
        "gpt", "dall_e", "created", "designed", "ai_", "synthetic", "render", 
        "stable-diffusion", "claude", "synthid", "watermarked"
    ]
    
    name_lower = name.lower()
    has_ai_keyword = any(keyword in name_lower for keyword in ai_keywords)
    
    if has_ai_keyword:
        # Get modification or creation time to generate realistic timestamp
        try:
            mtime = os.path.getmtime(file_path)
            dt = datetime.fromtimestamp(mtime)
        except Exception:
            dt = datetime.now()
            
        timestamp = dt.strftime("%Y%m%d_%H%M%S")
        prefix = "VID" if is_video else "IMG"
        
        # Add 3-digit random value to ensure unique filenames during batch processing
        rand_val = random.randint(100, 999)
        return f"{prefix}_{timestamp}_{rand_val}{ext}"
    
    return file_path.name


def run_gui():
    """
    Launches a beautiful, clean, light-themed premium application that is highly vibrant, spacious,
    and guarantees the initiate button is always fully visible on any screen size.
    """
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        import threading
    except ImportError:
        print("Error: Tkinter is not installed or available on this system.")
        return

    # Palette - Premium Modern Light Theme (Vibrant, high-contrast, beautiful)
    bg_color = "#f1f5f9"         # Slate-100 (Clean light workspace background)
    card_color = "#ffffff"       # Pure White (Crisp card containers)
    border_color = "#cbd5e1"     # Slate-300 (Subtle borders)
    accent_blue = "#2563eb"      # Royal Blue-600 (Primary actions)
    accent_hover = "#1d4ed8"     # Royal Blue-700 (Hover interactions)
    accent_green = "#059669"     # Emerald Green-600
    text_primary = "#0f172a"     # Slate-900 (High contrast readable text)
    text_secondary = "#475569"   # Slate-600 (Subtle secondary labels)
    console_bg = "#0f172a"       # Deep Dark Navy-900 (For high-contrast log screen)
    console_fg = "#f8fafc"       # Slate-50

    root = tk.Tk()
    root.title("Ultimate AI Content Cleaner")
    root.geometry("700x740")
    root.minsize(660, 680)
    root.configure(bg=bg_color)

    # Styles
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass

    # Custom styling overrides
    style.configure("TProgressbar", thickness=16, troughcolor="#e2e8f0", background=accent_blue, borderwidth=0)

    # Master structure: We pack the Bottom Action Bar FIRST to guarantee it is always visible and never cut off!
    bottom_frame = tk.Frame(root, bg=bg_color)
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(10, 15))

    # Main Scrollable / Spacious Container for the cards
    main_frame = tk.Frame(root, bg=bg_color)
    main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=15)

    # Custom Title Banner Card
    banner_card = tk.Frame(main_frame, bg=card_color, bd=0, relief=tk.FLAT, highlightbackground=border_color, highlightthickness=1)
    banner_card.pack(fill=tk.X, pady=(0, 12), ipady=6)
    
    title_label = tk.Label(
        banner_card, 
        text="🚀 Ultimate AI Content Cleaner", 
        font=("Segoe UI", 16, "bold"), 
        fg=accent_blue, 
        bg=card_color
    )
    title_label.pack(anchor="w", padx=15, pady=(8, 2))
    
    desc_label = tk.Label(
        banner_card, 
        text="Remove corner watermarks (Gemini, Runway, etc.) & completely strip metadata from videos/images.", 
        font=("Segoe UI", 9), 
        fg=text_secondary, 
        bg=card_color
    )
    desc_label.pack(anchor="w", padx=15, pady=(0, 8))

    # Helper function to create modern flat buttons
    def make_flat_button(parent, text, command, bg_col="#e2e8f0", fg_col=text_primary, hover_col="#cbd5e1"):
        btn = tk.Button(
            parent, text=text, command=command, font=("Segoe UI", 9, "bold"),
            bg=bg_col, fg=fg_col, activebackground=hover_col, activeforeground=fg_col,
            relief=tk.FLAT, bd=0, padx=12, pady=5, cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_col))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_col))
        return btn

    # Helper function to create stylish input fields
    def make_input_field(parent, textvariable):
        frame = tk.Frame(parent, bg=border_color, bd=1)
        inner = tk.Entry(
            frame, textvariable=textvariable, font=("Segoe UI", 10),
            bg="#f8fafc", fg=text_primary, insertbackground=accent_blue,
            relief=tk.FLAT, bd=6
        )
        inner.pack(fill=tk.X, expand=True)
        
        def on_focus_in(e):
            frame.config(bg=accent_blue)
        def on_focus_out(e):
            frame.config(bg=border_color)
            
        inner.bind("<FocusIn>", on_focus_in)
        inner.bind("<FocusOut>", on_focus_out)
        return frame, inner

    # Helper function to build custom titled container cards
    def make_card(parent, title):
        card = tk.Frame(parent, bg=card_color, bd=0, relief=tk.FLAT, highlightbackground=border_color, highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 10), ipady=6)
        lbl = tk.Label(card, text=title, font=("Segoe UI", 10, "bold"), fg=accent_blue, bg=card_color)
        lbl.pack(anchor="w", padx=15, pady=(8, 6))
        return card

    # 1. Input Section
    input_card = make_card(main_frame, "📁 1. SELECT INPUT SOURCE")
    input_row = tk.Frame(input_card, bg=card_color)
    input_row.pack(fill=tk.X, padx=15, pady=(0, 4))
    
    input_path_var = tk.StringVar()
    input_field, entry_input = make_input_field(input_row, input_path_var)
    input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[
                ("All Supported Files", "*.mp4;*.mov;*.mkv;*.avi;*.webm;*.jpg;*.jpeg;*.png;*.webp;*.heic;*.bmp;*.tiff;*.tif"),
                ("Videos", "*.mp4;*.mov;*.mkv;*.avi;*.webm"),
                ("Images", "*.jpg;*.jpeg;*.png;*.webp;*.heic;*.bmp;*.tiff;*.tif"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            input_path_var.set(file_path)
            if not output_path_var.get():
                output_path_var.set(str(Path(file_path).parent))

    def select_folder():
        folder_path = filedialog.askdirectory(title="Select Input Folder")
        if folder_path:
            input_path_var.set(folder_path)
            if not output_path_var.get():
                output_path_var.set(str(Path(folder_path) / "cleaned"))

    btn_file = make_flat_button(input_row, "Browse File...", select_file)
    btn_file.pack(side=tk.LEFT, padx=(0, 5))

    btn_folder = make_flat_button(input_row, "Browse Folder...", select_folder)
    btn_folder.pack(side=tk.LEFT)

    # 2. Output Section
    output_card = make_card(main_frame, "📂 2. SELECT OUTPUT FOLDER")
    output_row = tk.Frame(output_card, bg=card_color)
    output_row.pack(fill=tk.X, padx=15, pady=(0, 4))
    
    output_path_var = tk.StringVar()
    output_field, entry_output = make_input_field(output_row, output_path_var)
    output_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

    def select_output_folder():
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:
            output_path_var.set(folder_path)

    btn_out_folder = make_flat_button(output_row, "Browse...", select_output_folder)
    btn_out_folder.pack(side=tk.LEFT)

    # 3. Settings Section
    settings_card = make_card(main_frame, "⚙️ 3. CLEANING CONFIGURATION")
    settings_content = tk.Frame(settings_card, bg=card_color)
    settings_content.pack(fill=tk.X, padx=15)

    mode_var = tk.StringVar(value="crop")

    def on_mode_change():
        if mode_var.get() == "metadata_only":
            entry_right.config(state="disabled", bg="#e2e8f0", fg=text_secondary)
            entry_bottom.config(state="disabled", bg="#e2e8f0", fg=text_secondary)
        else:
            entry_right.config(state="normal", bg="#f8fafc", fg=text_primary)
            entry_bottom.config(state="normal", bg="#f8fafc", fg=text_primary)

    rb_crop = tk.Radiobutton(
        settings_content, 
        text="Watermark Removal + Strip Metadata (Auto Aspect-Ratio Crop & Scale)", 
        variable=mode_var, value="crop", command=on_mode_change,
        bg=card_color, fg=text_primary, selectcolor=bg_color, font=("Segoe UI", 9, "bold"),
        activebackground=card_color, activeforeground=text_primary, highlightthickness=0
    )
    rb_crop.pack(anchor="w", pady=(0, 4))

    rb_meta = tk.Radiobutton(
        settings_content, 
        text="Strip Metadata Only (Keeps full frame, removes invisible C2PA/AI metadata)", 
        variable=mode_var, value="metadata_only", command=on_mode_change,
        bg=card_color, fg=text_primary, selectcolor=bg_color, font=("Segoe UI", 9, "bold"),
        activebackground=card_color, activeforeground=text_primary, highlightthickness=0
    )
    rb_meta.pack(anchor="w", pady=(0, 10))

    crop_settings_frame = tk.Frame(settings_content, bg=card_color)
    crop_settings_frame.pack(anchor="w", padx=20)

    lbl_right = tk.Label(crop_settings_frame, text="Crop Right (px):", font=("Segoe UI", 9), fg=text_secondary, bg=card_color)
    lbl_right.pack(side=tk.LEFT, padx=(0, 5))
    crop_right_var = tk.StringVar(value="280")
    
    entry_right = tk.Entry(
        crop_settings_frame, textvariable=crop_right_var, width=6, font=("Segoe UI", 9, "bold"),
        bg="#f8fafc", fg=text_primary, insertbackground=accent_blue, relief=tk.FLAT, bd=3,
        highlightbackground=border_color, highlightthickness=1
    )
    entry_right.pack(side=tk.LEFT, padx=(0, 15))

    lbl_bottom = tk.Label(crop_settings_frame, text="Crop Bottom (px):", font=("Segoe UI", 9), fg=text_secondary, bg=card_color)
    lbl_bottom.pack(side=tk.LEFT, padx=(0, 5))
    crop_bottom_var = tk.StringVar(value="280")
    
    entry_bottom = tk.Entry(
        crop_settings_frame, textvariable=crop_bottom_var, width=6, font=("Segoe UI", 9, "bold"),
        bg="#f8fafc", fg=text_primary, insertbackground=accent_blue, relief=tk.FLAT, bd=3,
        highlightbackground=border_color, highlightthickness=1
    )
    entry_bottom.pack(side=tk.LEFT)

    # 4. Progress Card
    log_card = tk.Frame(main_frame, bg=card_color, bd=0, relief=tk.FLAT, highlightbackground=border_color, highlightthickness=1)
    log_card.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
    
    log_header = tk.Label(log_card, text="📝 PROCESSING LOG", font=("Segoe UI", 10, "bold"), fg=accent_blue, bg=card_color)
    log_header.pack(anchor="w", padx=15, pady=(8, 4))

    console_frame = tk.Frame(log_card, bg=console_bg, bd=0, highlightbackground=border_color, highlightthickness=1)
    console_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

    log_text = tk.Text(console_frame, wrap=tk.WORD, height=6, font=("Consolas", 9), bg=console_bg, fg=console_fg, relief=tk.FLAT, bd=6)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(console_frame, command=log_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=scrollbar.set)

    # Log text color coding
    log_text.tag_config("green", foreground="#34d399")  # Emerald Green
    log_text.tag_config("red", foreground="#f87171")    # Coral Red
    log_text.tag_config("cyan", foreground="#60a5fa")   # Soft Blue
    log_text.tag_config("yellow", foreground="#fbbf24") # Warm Amber

    def log(msg, color=None):
        log_text.config(state="normal")
        if color:
            log_text.insert(tk.END, msg + "\n", color)
        else:
            log_text.insert(tk.END, msg + "\n")
        log_text.config(state="disabled")
        log_text.see(tk.END)

    # Action panel widgets (packed inside bottom_frame so they are guaranteed visible)
    progress_bar = ttk.Progressbar(bottom_frame, mode="determinate", style="TProgressbar")
    progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))

    is_running = [False]

    def process_thread():
        try:
            input_val = input_path_var.get().strip()
            output_val = output_path_var.get().strip()

            if not input_val:
                messagebox.showerror("Error", "Please select an input file or folder.")
                return
            if not output_val:
                messagebox.showerror("Error", "Please select an output folder.")
                return

            input_path = Path(input_val)
            output_dir = Path(output_val)

            if not input_path.exists():
                messagebox.showerror("Error", f"Input path does not exist:\n{input_val}")
                return

            files_to_process = []
            if input_path.is_file():
                ext = input_path.suffix.lower()
                if ext in VIDEO_EXTENSIONS or ext in IMAGE_EXTENSIONS:
                    files_to_process.append(input_path)
            elif input_path.is_dir():
                for item in input_path.iterdir():
                    if item.is_file():
                        ext = item.suffix.lower()
                        if ext in VIDEO_EXTENSIONS or ext in IMAGE_EXTENSIONS:
                            files_to_process.append(item)

            if not files_to_process:
                log("❌ No supported video/image files found.", "red")
                return

            no_crop = (mode_var.get() == "metadata_only")
            try:
                crop_right = int(crop_right_var.get().strip())
                crop_bottom = int(crop_bottom_var.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Crop settings must be numbers.")
                return

            log("==================================================", "cyan")
            log("🚀 Starting processing...", "cyan")
            log(f"📁 Input: {input_path}", "cyan")
            log(f"📁 Output Folder: {output_dir}", "cyan")
            log(f"✨ Mode: {'Strip Metadata Only' if no_crop else 'Watermark Removal + Strip Metadata'}", "cyan")
            log("==================================================", "cyan")

            progress_bar["maximum"] = len(files_to_process)
            progress_bar["value"] = 0

            success_count = 0
            fail_count = 0

            for index, file_path in enumerate(files_to_process):
                ext = file_path.suffix.lower()
                is_vid = (ext in VIDEO_EXTENSIONS)
                
                clean_name = get_clean_output_filename(file_path, is_video=is_vid)
                
                if output_dir.resolve() == file_path.parent.resolve() and clean_name == file_path.name:
                    output_file = output_dir / f"{file_path.stem}_clean{file_path.suffix}"
                else:
                    output_file = output_dir / clean_name

                try:
                    if ext in VIDEO_EXTENSIONS:
                        log(f"🎬 Processing Video: {file_path.name}")
                        if no_crop:
                            strip_video_metadata_only(file_path, output_file)
                        else:
                            remove_video_watermark(file_path, output_file, crop_right, crop_bottom)
                    else:  # Image
                        log(f"🖼️ Processing Image: {file_path.name}")
                        if no_crop:
                            strip_image_metadata(file_path, output_file)
                        else:
                            remove_image_watermark(file_path, output_file, crop_right, crop_bottom)

                    log(f"   ✓ Saved as: {output_file.name}", "green")
                    success_count += 1
                except Exception as e:
                    log(f"   ✗ Failed: {e}", "red")
                    fail_count += 1

                progress_bar["value"] = index + 1
                root.update_idletasks()

            log("==================================================", "cyan")
            log("🎉 Processing Complete!", "green")
            log(f"   Successfully processed: {success_count}", "green")
            if fail_count > 0:
                log(f"   Failed: {fail_count}", "red")
            log(f"   Output folder: {output_dir}", "cyan")
            log("==================================================", "cyan")

            messagebox.showinfo("Processing Finished", f"Finished processing content!\n\nSuccessfully processed: {success_count}\nFailed: {fail_count}")

        except Exception as err:
            log(f"❌ Critical Error: {err}", "red")
            messagebox.showerror("Error", str(err))
        finally:
            is_running[0] = False
            btn_clean.config(state="normal", bg=accent_blue)
            btn_file.config(state="normal")
            btn_folder.config(state="normal")
            btn_out_folder.config(state="normal")

    def start_cleaning():
        if is_running[0]:
            return
        is_running[0] = True
        btn_clean.config(state="disabled", bg="#94a3b8")
        btn_file.config(state="disabled")
        btn_folder.config(state="disabled")
        btn_out_folder.config(state="disabled")

        log_text.config(state="normal")
        log_text.delete("1.0", tk.END)
        log_text.config(state="disabled")

        t = threading.Thread(target=process_thread, daemon=True)
        t.start()

    # Premium Vibrant Action Button
    btn_clean = tk.Button(
        bottom_frame, text="🚀 CLEAN CONTENT NOW", command=start_cleaning, font=("Segoe UI", 11, "bold"),
        bg=accent_blue, fg="#ffffff", activebackground=accent_hover, activeforeground="#ffffff",
        relief=tk.FLAT, bd=0, padx=25, pady=10, cursor="hand2"
    )
    btn_clean.bind("<Enter>", lambda e: btn_clean.config(bg=accent_hover) if not is_running[0] else None)
    btn_clean.bind("<Leave>", lambda e: btn_clean.config(bg=accent_blue) if not is_running[0] else None)
    btn_clean.pack(side=tk.RIGHT)

    log("Welcome to Ultimate AI Content Cleaner!", "green")
    log("Select a file or folder above to clean watermarks and metadata.")

    root.mainloop()


def main():
    # If no arguments are passed, launch the GUI!
    if len(sys.argv) == 1:
        run_gui()
        return

    print(f"""
{Fore.CYAN}================================================================================
   🚀 Ultimate AI Content Cleaner - Videos & Images 🚀
================================================================================
   ✓ Removes visible watermarks (Gemini/Veo, Runway, etc.)
   ✓ Strips ALL metadata (EXIF, XMP, IPTC, C2PA, GPS, AI tags)
   ✓ Supports: Videos (MP4, MOV, MKV, AVI) + Images (JPG, PNG, WEBP, HEIC)
   ✓ Batch processing for entire folders
================================================================================{Style.RESET_ALL}""")
    
    parser = argparse.ArgumentParser(description="Remove watermarks and metadata from videos and images.")
    parser.add_argument("-i", "--input", help="Input file or directory")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("--crop-right", type=int, default=280, help="Pixels to crop from right (default: 280)")
    parser.add_argument("--crop-bottom", type=int, default=280, help="Pixels to crop from bottom (default: 280)")
    parser.add_argument("--no-crop", action="store_true", help="Only strip metadata, don't remove watermark")
    
    args = parser.parse_args()
    
    if not args.input or not args.output:
        parser.print_help()
        sys.exit(1)
        
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Gather all files to process
    files_to_process = []
    
    if input_path.is_file():
        ext = input_path.suffix.lower()
        if ext in VIDEO_EXTENSIONS or ext in IMAGE_EXTENSIONS:
            files_to_process.append(input_path)
    elif input_path.is_dir():
        for item in input_path.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                if ext in VIDEO_EXTENSIONS or ext in IMAGE_EXTENSIONS:
                    files_to_process.append(item)
    
    if not files_to_process:
        print(f"{Fore.RED}[ERROR] No supported files found.{Style.RESET_ALL}")
        print(f"Supported formats:")
        print(f"  Videos: {', '.join(VIDEO_EXTENSIONS)}")
        print(f"  Images: {', '.join(IMAGE_EXTENSIONS)}")
        sys.exit(1)
    
    # Separate into videos and images
    videos = [f for f in files_to_process if f.suffix.lower() in VIDEO_EXTENSIONS]
    images = [f for f in files_to_process if f.suffix.lower() in IMAGE_EXTENSIONS]
    
    print(f"\n{Fore.GREEN}Found {len(files_to_process)} file(s) to process:{Style.RESET_ALL}")
    print(f"  • Videos: {len(videos)}")
    print(f"  • Images: {len(images)}")
    print(f"\nSettings:")
    print(f"  • Watermark removal: {Fore.GREEN if not args.no_crop else Fore.YELLOW}{'ENABLED (crop {0}x{1})'.format(args.crop_right, args.crop_bottom) if not args.no_crop else 'DISABLED'}{Style.RESET_ALL}")
    print(f"  • Metadata stripping: {Fore.GREEN}ENABLED{Style.RESET_ALL}")
    print(f"  • Output directory: {Fore.CYAN}{output_dir}{Style.RESET_ALL}\n")
    
    success_count = 0
    fail_count = 0
    
    # Process all files
    for file_path in tqdm(files_to_process, desc="Processing", unit="file"):
        ext = file_path.suffix.lower()
        is_vid = (ext in VIDEO_EXTENSIONS)
        
        # Determine the target output filename (with automatic camera genericizer)
        clean_name = get_clean_output_filename(file_path, is_video=is_vid)
        
        # Safeguard: if saving in the same folder and the name hasn't changed, append '_clean' to prevent overwriting
        if output_dir.resolve() == file_path.parent.resolve() and clean_name == file_path.name:
            output_file = output_dir / f"{file_path.stem}_clean{file_path.suffix}"
        else:
            output_file = output_dir / clean_name
        
        try:
            if ext in VIDEO_EXTENSIONS:
                tqdm.write(f" 🎬 {file_path.name}")
                if args.no_crop:
                    strip_video_metadata_only(file_path, output_file)
                else:
                    remove_video_watermark(file_path, output_file, args.crop_right, args.crop_bottom)
            else:  # Image
                tqdm.write(f" 🖼️  {file_path.name}")
                if args.no_crop:
                    strip_image_metadata(file_path, output_file)
                else:
                    remove_image_watermark(file_path, output_file, args.crop_right, args.crop_bottom)
            
            tqdm.write(f"    {Fore.GREEN}✓ Saved to {output_file.name}{Style.RESET_ALL}")
            success_count += 1
            
        except Exception as e:
            tqdm.write(f"    {Fore.RED}✗ Failed: {e}{Style.RESET_ALL}")
            fail_count += 1
    
    # Summary
    print(f"\n{Fore.CYAN}================================================================================{Style.RESET_ALL}")
    print(f"🎉 Processing complete!")
    print(f"   Successfully processed: {Fore.GREEN}{success_count}{Style.RESET_ALL}")
    if fail_count > 0:
        print(f"   Failed: {Fore.RED}{fail_count}{Style.RESET_ALL}")
    print(f"   Output location: {Fore.CYAN}{output_dir}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}================================================================================{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
