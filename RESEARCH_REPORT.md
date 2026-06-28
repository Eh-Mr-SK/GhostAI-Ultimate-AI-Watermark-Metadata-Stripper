# Gemini/Veo Watermark Removal - Complete Research Report

## 1. EXACT Watermark Coordinates & Geometry

Based on analysis of multiple open-source tools (allenk/VeoWatermarkRemover, Paxsenix0/veo3-watermark-remover, dearabhin/gemini-watermark-remover, allenk/GeminiWatermarkTool):

### For IMAGES (Static Gemini Sparkle ✦):

| Image Dimensions | Logo Size | Margin from Corner | Position (x, y) |
|---|---|---|---|
| W ≤ 1024 OR H ≤ 1024 | **48×48 px** | 32px from right & bottom | `(W - 32 - 48, H - 32 - 48)` |
| W > 1024 AND H > 1024 | **96×96 px** | 64px from right & bottom | `(W - 64 - 96, H - 64 - 96)` |

**For V2 (Gemini 3.5+ / current profile):**
| Image Dimensions | Logo Size | Margin | Notes |
|---|---|---|---|
| Large (>1024 both) | 96×96 | 192px margin | V2 has wider margins |
| Small (≤1024 either) | 36×36 | ~proportional | Scales with aspect ratio |

### For VIDEOS (Veo/Gemini Video Watermark):

The `Paxsenix0/veo3-watermark-remover` `logo_data.py` reveals these exact coordinates:

| Video Format | Resolution | Position (x, y) | Region Size (w × h) |
|---|---|---|---|
| Horizontal 720p | 1280×720 | **(1150, 650)** | 130×70 |
| Horizontal 1080p | 1920×1080 | **(1700, 970)** | 220×110 |
| Vertical 720p | 720×1280 | **(590, 1200)** | 130×80 |
| **Vertical 1080p** | **1080×1920** | **(880, 1800)** | **200×120** |
| Gemini Diamond 720p | 1280×720 | **(1150, 650)** | 130×70 |

### For YOUR specific case (1080×1920 PORTRAIT Video):

```
Watermark position: x=880, y=1800, width=200, height=120
```

This means the star is centered around approximately:
- **Center X ≈ 980** (880 + 200/2)
- **Center Y ≈ 1860** (1800 + 120/2)
- Covers from x=880 to x=1080, y=1800 to y=1920

**THIS IS WHY YOUR PREVIOUS CROP FAILED!** You were cropping 100px from the RIGHT edge (x=980→1080) and 120px from the BOTTOM (y=1800→1920). But the watermark starts at **x=880**, which is 200px from the right edge, not just 100px! The watermark extends across a 200px-wide region.

### Alternate Video Geometry Formula (dearabhin/gemini-watermark-remover):

For Veo videos specifically:
```
base = min(width, height)   // = 1080 for 1080x1920
size = round(base / 15)     // = 72 px (logo square dimension)
margin = round(base / 10)   // = 108 px from corner

x = width - margin - size   // = 1080 - 108 - 72 = 900
y = height - margin - size  // = 1920 - 108 - 72 = 1740
```

With default offsets applied: `offsetX = -24, offsetY = -24`
```
Final x = 900 + (-24) = 876
Final y = 1740 + (-24) = 1716
```

**Note:** There are TWO watermark formats:
1. The **older "Veo" text** watermark (pre-Gemini 3.5) — larger text logo
2. The **newer "Gemini diamond/sparkle" ✦** — 4-pointed star (Gemini 3.5+)

The VeoWatermarkRemover README confirms:
- **720p standard diamond**: 48×48 at margin (72, 72)
- **720p compact diamond**: 44×44 at margin (29, 40)  
- **1080p diamond**: Auto-detected, ~96px area with 192px margin from edges

---

## 2. How the Watermark is Applied (Critical for Removal)

Gemini applies the watermark using **alpha compositing**:

```
displayed_pixel = alpha × white(255) + (1 - alpha) × original_pixel
```

Where `alpha` is a pre-computed alpha map (the sparkle shape) with values 0.0-1.0.

### Mathematically Exact Removal (Reverse Alpha Blending):

```
original_pixel = (displayed_pixel - alpha × 255) / (1 - alpha)
```

This is NOT inpainting or guessing — it's **exact mathematical restoration** of the original pixels!

---

## 3. Relevant GitHub Repositories

### Tier 1 (Best Quality, Most Stars):

| Repo | Stars | Language | Method |
|---|---|---|---|
| [allenk/VeoWatermarkRemover](https://github.com/allenk/VeoWatermarkRemover) | **183** | C++ (binary) | Reverse alpha blend + AI denoise + auto-detect |
| [dearabhin/gemini-watermark-remover](https://github.com/dearabhin/gemini-watermark-remover) | **196** | JS (browser) | Reverse alpha blend (client-side Vue app) |
| [allenk/GeminiWatermarkTool](https://github.com/allenk/GeminiWatermarkTool) | N/A | C++/OpenCV | GUI + CLI, 3-stage NCC detection + reverse alpha |

### Tier 2 (Python-based, Good for Integration):

| Repo | Stars | Language | Method |
|---|---|---|---|
| [Paxsenix0/veo3-watermark-remover](https://github.com/Paxsenix0/veo3-watermark-remover) | 1 | Python | FastAPI, reverse alpha blend, multi-worker |
| [harindujayakody/flow-veo-watermark-remover](https://github.com/harindujayakody/flow-veo-watermark-remover) | 2 | Python | Zoom + crop approach |
| [husnain381a/gemini-veo-video-watermark-remover](https://github.com/husnain381a/gemini-veo-video-watermark-remover) | 5 | JavaScript | Reverse alpha blending |
| [froggeric/gemini-watermark-and-synthid-remover](https://github.com/froggeric/gemini-watermark-and-synthid-remover) | 3 | C++ | CLI, cross-platform |

---

## 4. Best Approach: Reverse Alpha Blending (NOT Inpainting)

The **unanimously best method** used by ALL successful tools is **Reverse Alpha Blending**, not OpenCV inpainting or template matching. Here's why:

- **Inpainting** = guessing pixels → artifacts, blur, quality loss
- **Reverse Alpha Blending** = mathematical restoration → PERFECT pixel recovery

### Requirements:
1. The **alpha map** (the sparkle shape template as a grayscale image)
2. Knowledge that the logo color is **pure white (255)**
3. The **exact position** of the watermark in the frame

### The Alpha Map:
The alpha map is a grayscale image (48×48 or 96×96) that defines the watermark shape. It's extracted by:
- Generating images with a pure-color background through Gemini
- Subtracting the known background from the watermarked output
- The difference reveals the exact alpha transparency at each pixel

These alpha maps are available as embedded PNGs in both GeminiWatermarkTool and the web-based tools (stored as `bg_48.png` and `bg_96.png`).

---

## 5. Complete Working Python Implementation

See `gemini_watermark_remover.py` in this project — a fully automated solution that:

1. Auto-detects video resolution and orientation
2. Determines correct watermark position using known geometry
3. Applies **Reverse Alpha Blending** per-frame using NumPy
4. Optional: Falls back to OpenCV inpainting if no alpha map available
5. Supports bulk processing
6. Preserves audio via FFmpeg stream copy

---

## 6. Why Previous Approaches Failed

| Approach | Why it Failed |
|---|---|
| Crop 100px right + 120px bottom | Watermark is 200px wide starting at x=880 — need to crop ≥200px from right |
| FFmpeg `delogo` filter | Wrong coordinates; also delogo is just a blur, not precise |
| Spatial cloning patches | Doesn't match the exact alpha shape |
| Simple blur region | Introduces visible blur artifacts |

### The CORRECT crop (if you want the simple approach):
For 1080×1920 portrait video, you need to crop at MINIMUM:
- **200px from right edge** (watermark spans x=880 to x=1080)
- **120px from bottom edge** (watermark spans y=1800 to y=1920)

But the **reverse alpha blending** approach is vastly superior because it has ZERO quality loss and preserves all pixels.
