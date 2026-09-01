# Indian ANPR – Offline Real-Time Desktop Camera System

A real-time, fully offline ANPR system designed for Indian registration plates.

## Features
- Local vehicle detection using YOLO
- Plate detection with optional local trained model and OpenCV fallback
- OCR via PaddleOCR or EasyOCR locally
- Indian plate validation with state code checks and BH-series support
- Temporal voting and duplicate prevention
- SQLite database and CSV export
- PySide6 desktop dashboard

## Windows Quick Start

1. Install Python 3.11+
2. Create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Place trained model files in the `models/` directory:
   - `models/vehicle_yolo.pt` or `models/yolov8n.pt`
   - `models/indian_plate.pt`

4. Run the app:

```powershell
python app.py
```

### CLI usage

```powershell
python app.py --camera 0
python app.py --video test\videos\test.mp4
python test_image.py --image test\images\test.jpg
```

## Offline Guarantee

This project uses no API keys, no cloud OCR, no HTTP calls, and no external inference service.

## Build Windows Executable

```powershell
build_windows.bat
```
