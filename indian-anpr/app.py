import argparse
import sys

from PySide6.QtWidgets import QApplication

from gui.main_window import ANPRMainWindow


def main():
    parser = argparse.ArgumentParser(description="Indian ANPR - Offline Real-Time Desktop Camera System")
    parser.add_argument("--camera", type=int, default=None, help="Camera device index")
    parser.add_argument("--video", type=str, default=None, help="Path to video file")
    parser.add_argument("--rtsp", type=str, default=None, help="RTSP stream URL")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = ANPRMainWindow()
    window.show()

    if args.camera is not None:
        window.start_camera(source_override=args.camera)
    elif args.video is not None:
        window.start_camera(source_override=args.video)
    elif args.rtsp is not None:
        window.start_camera(source_override=args.rtsp)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
