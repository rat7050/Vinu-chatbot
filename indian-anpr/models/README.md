# Offline YOLO Models Directory

Place your local trained weights files inside this folder:

1. `vehicle_yolo.pt` or `yolov8n.pt` / `yolo11n.pt` for vehicle detection.
2. `indian_plate.pt` for the dedicated Indian number plate detector.

If `indian_plate.pt` is not present, the system uses an experimental OpenCV fallback detector and logs a warning.
