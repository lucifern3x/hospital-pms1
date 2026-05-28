"""
ui_face.py
──────────
PySide6 widgets for Face ID integration.

Provides:
  • CameraWidget        – live webcam feed rendered in a QLabel
  • RegisterFaceDialog  – capture + register a patient's face
  • IdentifyFaceDialog  – scan webcam and find matching patient
"""

from __future__ import annotations

import time
from typing import Optional, Callable

import numpy as np

from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject
from PySide6.QtGui import QImage, QPixmap, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QWidget, QSizePolicy, QMessageBox,
)

from face_recognition_engine import PatientFaceEngine, FaceMatch, FaceNotFoundError, FACE_LIBS_OK

# re-use palette from ui_main
PALETTE = {
    "bg":       "#0f1923",
    "surface":  "#16232e",
    "surface2": "#1c2f3d",
    "accent":   "#00c9a7",
    "accent2":  "#0091ff",
    "danger":   "#ff4d6d",
    "warning":  "#ffd166",
    "text":     "#e8f0f7",
    "text_dim": "#7a99b0",
    "border":   "#243647",
}

DIALOG_QSS = f"""
QDialog, QWidget {{
    background: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: 'Segoe UI', 'SF Pro Display', Arial;
    font-size: 13px;
}}
QLabel {{
    color: {PALETTE['text']};
}}
QPushButton {{
    background: {PALETTE['surface2']};
    border: 1.5px solid {PALETTE['border']};
    border-radius: 6px;
    padding: 7px 18px;
    color: {PALETTE['text']};
    font-weight: 600;
}}
QPushButton:hover {{
    background: {PALETTE['surface']};
    border-color: {PALETTE['accent']};
    color: {PALETTE['accent']};
}}
QPushButton#btn_primary {{
    background: {PALETTE['accent']};
    border-color: {PALETTE['accent']};
    color: #0f1923;
}}
QPushButton#btn_primary:hover {{
    background: #00b396;
    color: #0f1923;
}}
QPushButton#btn_danger {{
    border-color: {PALETTE['danger']};
    color: {PALETTE['danger']};
    background: transparent;
}}
QPushButton#btn_danger:hover {{
    background: {PALETTE['danger']};
    color: #fff;
}}
QPushButton:disabled {{
    opacity: 0.4;
}}
QProgressBar {{
    background: {PALETTE['surface2']};
    border: 1px solid {PALETTE['border']};
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: {PALETTE['accent']};
    border-radius: 4px;
}}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  CAMERA WORKER (runs in background thread)
# ══════════════════════════════════════════════════════════════════════════════
class CameraWorker(QObject):
    """Reads frames from webcam and emits them as QPixmap."""
    frame_ready  = Signal(object)   # np.ndarray
    error        = Signal(str)
    stopped      = Signal()

    def __init__(self, camera_index: int = 0) -> None:
        super().__init__()
        self._index   = camera_index
        self._running = False

    def start(self) -> None:
        if not FACE_LIBS_OK:
            self.error.emit("Thư viện face_recognition chưa được cài đặt.\n\nChạy:\n  pip install face_recognition opencv-python")
            return
        try:
            import cv2
            self._cap = PatientFaceEngine.open_camera(self._index)
        except RuntimeError as e:
            self.error.emit(str(e))
            return

        self._running = True
        while self._running:
            frame = PatientFaceEngine.capture_frame(self._cap)
            if frame is not None:
                self.frame_ready.emit(frame)
            QThread.msleep(33)   # ~30 fps

        self._cap.release()
        self.stopped.emit()

    def stop(self) -> None:
        self._running = False


# ══════════════════════════════════════════════════════════════════════════════
#  CAMERA WIDGET
# ══════════════════════════════════════════════════════════════════════════════
class CameraWidget(QLabel):
    """QLabel that displays live webcam frames."""

    def __init__(self, width: int = 480, height: int = 360, parent=None) -> None:
        super().__init__(parent)
        self._w = width
        self._h = height
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            background: {PALETTE['surface2']};
            border: 2px solid {PALETTE['border']};
            border-radius: 10px;
            color: {PALETTE['text_dim']};
            font-size: 13px;
        """)
        self.setText("📷  Đang khởi động camera…")

        self._thread = QThread()
        self._worker = CameraWorker()
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.start)
        self._worker.frame_ready.connect(self._on_frame)
        self._worker.error.connect(self._on_error)
        self._thread.start()

        self._last_frame: Optional[np.ndarray] = None

    # ─── slots ──────────────────────────────────────────────────────────── #
    def _on_frame(self, frame: np.ndarray) -> None:
        self._last_frame = frame
        self._display(frame)

    def _on_error(self, msg: str) -> None:
        self.setText(f"⚠️  {msg}")

    def _display(self, frame: np.ndarray) -> None:
        import cv2
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            self._w, self._h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.setPixmap(pix)

    # ─── public ─────────────────────────────────────────────────────────── #
    def current_frame(self) -> Optional[np.ndarray]:
        return self._last_frame

    def display_frame(self, frame: np.ndarray) -> None:
        """Display a specific (possibly annotated) frame."""
        self._display(frame)

    def stop(self) -> None:
        self._worker.stop()
        self._thread.quit()
        self._thread.wait(2000)


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTER FACE DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class RegisterFaceDialog(QDialog):
    """
    Opens webcam, lets user preview, then captures + registers
    a face encoding for the given patient.
    """

    def __init__(
        self,
        engine: PatientFaceEngine,
        patient_id: int,
        patient_name: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._engine       = engine
        self._patient_id   = patient_id
        self._patient_name = patient_name
        self.setWindowTitle(f"Đăng ký Face ID – {patient_name}")
        self.setStyleSheet(DIALOG_QSS)
        self.setModal(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Title
        ttl = QLabel(f"🫥  Đăng ký khuôn mặt")
        ttl.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {PALETTE['accent']};")
        layout.addWidget(ttl)

        sub = QLabel(f"Bệnh nhân: <b>{self._patient_name}</b><br>"
                     "Nhìn thẳng vào camera, rồi bấm <b>Chụp & Đăng ký</b>.")
        sub.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 12px; line-height: 1.6;")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        # Camera
        self._cam = CameraWidget(480, 340)
        layout.addWidget(self._cam, alignment=Qt.AlignCenter)

        # Status
        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignCenter)
        self._status.setStyleSheet(f"font-size: 12px; color: {PALETTE['text_dim']};")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

        # Buttons
        btn_row = QHBoxLayout()
        self._btn_capture = QPushButton("📸  Chụp & Đăng ký")
        self._btn_capture.setObjectName("btn_primary")
        self._btn_capture.setFixedHeight(38)
        self._btn_capture.clicked.connect(self._capture)
        btn_cancel = QPushButton("Huỷ")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self._btn_capture)
        layout.addLayout(btn_row)

    def _capture(self) -> None:
        frame = self._cam.current_frame()
        if frame is None:
            self._status.setText("⚠️  Chưa nhận được frame từ camera.")
            return

        self._btn_capture.setEnabled(False)
        self._status.setText("⏳  Đang phân tích khuôn mặt…")
        self.repaint()

        try:
            self._engine.register_face(self._patient_id, self._patient_name, frame)
            self._status.setStyleSheet(f"color: {PALETTE['accent']}; font-size: 13px; font-weight: 600;")
            self._status.setText("✅  Đăng ký thành công!")
            QTimer.singleShot(1200, self.accept)
        except FaceNotFoundError:
            self._status.setStyleSheet(f"color: {PALETTE['danger']}; font-size: 12px;")
            self._status.setText("❌  Không phát hiện khuôn mặt. Hãy đảm bảo mặt bạn nhìn thẳng vào camera và đủ sáng.")
            self._btn_capture.setEnabled(True)
        except Exception as e:
            self._status.setStyleSheet(f"color: {PALETTE['danger']}; font-size: 12px;")
            self._status.setText(f"❌  Lỗi: {e}")
            self._btn_capture.setEnabled(True)

    def closeEvent(self, event) -> None:
        self._cam.stop()
        event.accept()

    def reject(self) -> None:
        self._cam.stop()
        super().reject()

    def accept(self) -> None:
        self._cam.stop()
        super().accept()


# ══════════════════════════════════════════════════════════════════════════════
#  IDENTIFY FACE DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class IdentifyFaceDialog(QDialog):
    """
    Continuously scans webcam frames and tries to match a registered patient.
    Shows a live annotated feed. On match → emits patient_id via signal.
    """
    patient_identified = Signal(int, str, float)  # id, name, confidence

    SCAN_INTERVAL_MS = 500   # run recognition every 500 ms

    def __init__(self, engine: PatientFaceEngine, parent=None) -> None:
        super().__init__(parent)
        self._engine = engine
        self._last_match: Optional[FaceMatch] = None
        self.setWindowTitle("Nhận diện bệnh nhân – Face ID")
        self.setStyleSheet(DIALOG_QSS)
        self.setModal(True)
        self._build_ui()
        self._start_scan_timer()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        ttl = QLabel("🔍  Nhận diện khuôn mặt")
        ttl.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {PALETTE['accent2']};")
        layout.addWidget(ttl)

        count = self._engine.registered_count()
        sub = QLabel(
            f"Đang quét webcam để nhận diện bệnh nhân.<br>"
            f"Có <b>{count}</b> khuôn mặt đã đăng ký trong hệ thống."
        )
        sub.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 12px;")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        # Camera feed
        self._cam = CameraWidget(480, 340)
        layout.addWidget(self._cam, alignment=Qt.AlignCenter)

        # Match result card
        self._result_card = QFrame()
        self._result_card.setStyleSheet(f"""
            QFrame {{
                background: {PALETTE['surface2']};
                border: 1.5px solid {PALETTE['border']};
                border-radius: 10px;
                padding: 6px;
            }}
        """)
        card_layout = QHBoxLayout(self._result_card)
        card_layout.setSpacing(12)

        self._avatar = QLabel("👤")
        self._avatar.setStyleSheet("font-size: 28px;")
        card_layout.addWidget(self._avatar)

        info_col = QVBoxLayout()
        self._name_lbl = QLabel("Đang quét…")
        self._name_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {PALETTE['text']};")
        self._conf_lbl = QLabel("")
        self._conf_lbl.setStyleSheet(f"font-size: 12px; color: {PALETTE['text_dim']};")
        info_col.addWidget(self._name_lbl)
        info_col.addWidget(self._conf_lbl)
        card_layout.addLayout(info_col)
        card_layout.addStretch()

        self._conf_bar = QProgressBar()
        self._conf_bar.setRange(0, 100)
        self._conf_bar.setValue(0)
        self._conf_bar.setFixedWidth(100)
        self._conf_bar.setTextVisible(False)
        card_layout.addWidget(self._conf_bar)

        layout.addWidget(self._result_card)

        # Buttons
        btn_row = QHBoxLayout()
        self._btn_confirm = QPushButton("✅  Xác nhận bệnh nhân này")
        self._btn_confirm.setObjectName("btn_primary")
        self._btn_confirm.setFixedHeight(38)
        self._btn_confirm.setEnabled(False)
        self._btn_confirm.clicked.connect(self._confirm)

        btn_cancel = QPushButton("Đóng")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self._btn_confirm)
        layout.addLayout(btn_row)

    # ─── scanning ───────────────────────────────────────────────────────── #
    def _start_scan_timer(self) -> None:
        self._scan_timer = QTimer(self)
        self._scan_timer.setInterval(self.SCAN_INTERVAL_MS)
        self._scan_timer.timeout.connect(self._scan_once)
        self._scan_timer.start()

    def _scan_once(self) -> None:
        frame = self._cam.current_frame()
        if frame is None:
            return

        match = self._engine.identify_from_frame(frame)
        self._last_match = match

        if match:
            if match.frame is not None:
                self._cam.display_frame(match.frame)
            pct = int(match.confidence * 100)
            self._name_lbl.setText(match.patient_name)
            self._name_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {PALETTE['accent']};")
            self._conf_lbl.setText(f"Độ chính xác: {pct}%  •  ID #{match.patient_id}")
            self._conf_bar.setValue(pct)
            self._btn_confirm.setEnabled(True)
            self._result_card.setStyleSheet(f"""
                QFrame {{
                    background: {PALETTE['surface2']};
                    border: 1.5px solid {PALETTE['accent']};
                    border-radius: 10px; padding: 6px;
                }}
            """)
        else:
            self._name_lbl.setText("Đang tìm kiếm…")
            self._name_lbl.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {PALETTE['text']};")
            self._conf_lbl.setText("")
            self._conf_bar.setValue(0)
            self._btn_confirm.setEnabled(False)
            self._result_card.setStyleSheet(f"""
                QFrame {{
                    background: {PALETTE['surface2']};
                    border: 1.5px solid {PALETTE['border']};
                    border-radius: 10px; padding: 6px;
                }}
            """)

    def _confirm(self) -> None:
        if self._last_match:
            self.patient_identified.emit(
                self._last_match.patient_id,
                self._last_match.patient_name,
                self._last_match.confidence,
            )
            self.accept()

    # ─── cleanup ────────────────────────────────────────────────────────── #
    def _cleanup(self) -> None:
        self._scan_timer.stop()
        self._cam.stop()

    def closeEvent(self, event) -> None:
        self._cleanup(); event.accept()

    def reject(self) -> None:
        self._cleanup(); super().reject()

    def accept(self) -> None:
        self._cleanup(); super().accept()
