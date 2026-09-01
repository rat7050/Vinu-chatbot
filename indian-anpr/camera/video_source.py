import cv2

from utils.logger import app_logger


class VideoCaptureSource:
    def __init__(self, source, width: int = 1280, height: int = 720):
        self.source = source
        self.width = width
        self.height = height
        self.cap = None
        self.open()

    def open(self):
        if isinstance(self.source, bool):
            self.source = int(self.source)

        if isinstance(self.source, str) and self.source.isdigit():
            self.source = int(self.source)

        self.cap = cv2.VideoCapture(self.source)
        if isinstance(self.source, int):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        if not self.cap.isOpened():
            app_logger.error(f"Unable to open video source: {self.source}")
        else:
            app_logger.info(f"Video source {self.source} opened successfully.")

    def read(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            app_logger.info(f"Released video source {self.source}")
