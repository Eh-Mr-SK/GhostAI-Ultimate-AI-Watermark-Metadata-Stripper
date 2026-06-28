# 👻 GhostAI: Ultimate AI Watermark & Metadata Stripper

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-orange.svg)]()
[![FFmpeg](https://img.shields.io/badge/dependency-FFmpeg-red.svg)](https://ffmpeg.org/)

**GhostAI** is a powerful, locally running media sanitization toolkit that removes embedded metadata and content credentials from media that you own for privacy, testing, interoperability, and digital preservation. It strips C2PA, XMP, EXIF, IPTC, GPS, and other embedded metadata from images and videos, and provides optional owner-controlled preprocessing (such as configurable cropping and resampling) for research, editing workflows, and media preparation.

---

## 🧐 Why Use GhostAI?

If you use AI features (such as voice enhancement, generative b-roll, background replacements, or text overlays) to edit your videos or images, social media algorithms (Meta, ByteDance, Google) automatically scan the content. 

Even if only 5% of your edit is AI-assisted, they often flag the **entire post as "AI-Generated"**, which severely suppresses your organic distribution, limits your visibility, and penalizes your account's reach.

GhostAI strips all digital signatures, cleans invisible watermarks, and renames files to mimic native smartphone recordings, ensuring your content retains its organic reach.

---

## 🚀 Key Features

* **📦 Unified Image & Video Support**: Clean videos (`.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`) and images (`.jpg`, `.png`, `.webp`, `.heic`, etc.) in a single batch.
* **✨ High-Fidelity Corner Crop & Scale**: Removes visible watermarks (like Gemini spark, Veo tag, Runway watermark) by applying smart crop & upscale interpolation.
* **📐 Aspect-Ratio Guardian**: Maintains the *exact* original aspect ratio of your files during watermark removal, preventing any squashing, horizontal stretching, or distortion.
* **🧹 Full Metadata Cleansing**: Strips C2PA (Content Credentials), EXIF, GPS coordinates, IPTC, XMP tags, and creator signatures.
* **📸 Smart Camera-Style Renaming**: Automatically detects AI-related terms in filenames (e.g., `Gemini generated image...`, `chatgpt created...`) and renames them to standard phone camera formats like `IMG_20260628_221532_382.png` or `VID_20260628_175954_110.mp4`.
* **🖥️ Beautiful Premium Light GUI**: Features a sleek, user-friendly desktop interface with real-time log screens, scrollbars, and progress bars.
* **💻 Command-Line Interface (CLI)**: Full command-line options for power users and automation scripts.
* **🔒 100% Offline & Local**: No servers, no APIs, no subscription fees. Your private media never leaves your computer.

---

## 🛠️ How It Works (Under the Hood)

### 1. Invisible Metadata Stripping
* **Images**: PIL/Pillow opens the image and extracts the raw pixel data, rebuilding it cleanly into a new container without EXIF, XMP, ICC profiles, or GPS markers.
* **Videos**: Employs FFmpeg's advanced metadata mapping `-map_metadata -1` alongside standard compliance flags `-fflags +bitexact -flags +bitexact` to write a perfectly sterile structural container.

### 2. Visible Watermark Removal (Aspect-Ratio Safeguard)
Unlike other tools that stretch your video horizontally or vertically when cropping, GhostAI keeps your media's aspect ratio perfectly constant:
$$ \text{Target Aspect Ratio} = \frac{\text{Width}}{\text{Height}} $$
It shrinks the frame bounding box relative to your crop specifications, aligns the crop window to the top-left (effectively cutting out the bottom-right corner where AI logos are placed), and then interpolates the remaining frame back up using ultra-high-quality **Lanczos resampling**.

---

## ⚙️ Quick Start (Windows)

### Prerequisites
1. **Python 3.10+**: Download and install [Python](https://www.python.org/). Check the box to **"Add Python to PATH"** during installation.
2. **FFmpeg**: Ensure FFmpeg is installed and added to your System PATH.
   * *Tip*: On Windows, open PowerShell and run: `winget install FFmpeg`

### One-Click Launch
1. Clone or download this repository to your computer.
2. Double-click **`clean_all.bat`**. 
3. This batch launcher automatically verifies Python, installs any missing dependencies (Pillow, piexif, tqdm, colorama), and opens the Graphical Desktop App!

---

## 💻 Manual & CLI Usage

If you prefer to run the script via terminal or integrate it into other scripts, use the command-line flags:

```bash
# Display help and options
python clean_all.py --help

# Batch clean a folder (crop corner watermark + strip metadata)
python clean_all.py -i "C:\MyFiles\ToClean" -o "C:\MyFiles\Cleaned"

# Strip metadata only (no cropping / keeps full frame size)
python clean_all.py -i "C:\MyFiles\ToClean" -o "C:\MyFiles\Cleaned" --no-crop

# Custom crop dimensions (crop 300px from right, 320px from bottom)
python clean_all.py -i "C:\MyFiles\ToClean" -o "C:\MyFiles\Cleaned" --crop-right 300 --crop-bottom 320
```

---

## 📂 Project Structure

```text
├── clean_all.py         # Main application logic (both GUI & CLI)
├── clean_all.bat        # Windows launcher (auto-installs requirements)
├── requirements.txt     # Python package requirements
├── RESEARCH_REPORT.md   # Coordinate blueprints for common AI watermarks
└── README.md            # You are here!
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions make the open-source community an amazing place! If you find a bug, have coordinate updates for a new model, or want to suggest UI improvements:
1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

*Disclaimer: GhostAI is designed for creators to maintain control over their own content's metadata. Please respect copyrights and intellectual property.*
