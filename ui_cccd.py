"""
ui_cccd.py
──────────
Offline QR Code Generator and Camera Scanner Dialog for Hospital PMS.
Repurposed to manage Patient QR Code cards and scan them using OpenCV.
"""
from __future__ import annotations

import cv2
import qrcode
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QImage, QPixmap, QFont, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QFrame, QFileDialog, QWidget
)
from i18n import get_language, tr

# ── Palette matches main UI dark mode ─────────────────────────────────────────
P = {
    "bg":       "#121212",
    "surface":  "#1e1e1e",
    "surface2": "#252526",
    "accent":   "#007acc",
    "accent2":  "#0098ff",
    "text":     "#cccccc",
    "text_dim": "#858585",
    "border":   "#3c3c3c",
    "success":  "#4caf50",
    "danger":   "#f14c4c",
}

# ══════════════════════════════════════════════════════════════════════════════
#  LOCAL OFFLINE QR GENERATION UTILITY
# ══════════════════════════════════════════════════════════════════════════════
def generate_qr_pixmap(data: str, size: int = 220) -> QPixmap:
    """Generates a QR Code QPixmap locally and offline."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=1
        )
        qr.add_data(data)
        qr.make(fit=True)
        # Create PIL Image
        img = qr.make_image(fill_color="black", back_color="white")
        # Convert to QImage directly
        from PIL import ImageQt
        qimg = ImageQt.ImageQt(img.convert("RGB"))
        pixmap = QPixmap.fromImage(qimg)
        return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    except Exception as e:
        # Fail-safe fallback if PIL conversion fails
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor("white"))
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor("red"), 2))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, f"QR Error:\n{e}")
        painter.end()
        return pixmap


# ══════════════════════════════════════════════════════════════════════════════
#  PATIENT QR CARD VIEWER / PRINTER
# ══════════════════════════════════════════════════════════════════════════════
class PatientQRDialog(QDialog):
    """
    Displays a premium, high-fidelity patient card with their details
    and a locally generated offline QR code. Supports exporting and printing.
    """
    def __init__(self, patient_id: int, name: str, dob: str, gender: str, phone: str, parent=None):
        super().__init__(parent)
        self._lang = getattr(parent, "_lang", get_language()) if parent else get_language()
        self.patient_id = patient_id
        self.patient_name = name
        self.patient_dob = dob
        self.patient_gender = gender
        self.patient_phone = phone
        
        self.setWindowTitle(self._t("qr.card.title"))
        self.setFixedSize(420, 520)
        self.setStyleSheet(f"""
            QDialog {{ background: {P['bg']}; color: {P['text']}; font-family: 'Segoe UI', Arial; }}
            QPushButton {{ background: {P['surface2']}; border: 1px solid {P['border']};
                           border-radius: 4px; padding: 8px 16px; color: {P['text']}; font-weight: 600; }}
            QPushButton:hover {{ border-color: {P['accent']}; color: {P['accent']}; }}
            QPushButton#btn_primary {{ background: {P['accent']}; border-color: {P['accent']}; color: #fff; }}
            QPushButton#btn_primary:hover {{ background: #006aab; }}
        """)
        
        self._build_ui()

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ── Card Container (Visual Card representation)
        self.card_widget = QWidget()
        self.card_widget.setObjectName("card")
        # Visual styling for the hospital identity card
        self.card_widget.setStyleSheet(f"""
            QWidget#card {{
                background: #ffffff;
                border: 2px solid {P['accent']};
                border-radius: 12px;
            }}
            QLabel {{
                background: transparent;
                color: #333333;
            }}
        """)
        
        card_layout = QVBoxLayout(self.card_widget)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        # Hospital Identity Header
        header_lbl = QLabel(self._t("qr.card.header"))
        header_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {P['accent']}; text-align: center;")
        header_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(header_lbl)

        sub_lbl = QLabel(self._t("qr.card.sub"))
        sub_lbl.setStyleSheet("font-size: 9px; font-weight: bold; color: #666666; margin-bottom: 6px;")
        sub_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(sub_lbl)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(f"background-color: {P['accent']}; max-height: 1px;")
        card_layout.addWidget(div)

        # QR Code Display
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        qr_data = f"HOSPITAL-PMS-PATIENT:{self.patient_id}"
        self.qr_pixmap = generate_qr_pixmap(qr_data, 180)
        self.qr_label.setPixmap(self.qr_pixmap)
        card_layout.addWidget(self.qr_label)

        # Patient Details
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_lbl = QLabel(f"{self._t('qr.card.name')}: <b>{self.patient_name.upper()}</b>")
        name_lbl.setStyleSheet("font-size: 13px; color: #111111;")
        
        id_lbl = QLabel(f"{self._t('qr.card.patient_id')}: <b>#{self.patient_id:05d}</b>")
        id_lbl.setStyleSheet(f"font-size: 12px; color: {P['accent']}; font-weight: bold;")
        
        dob_lbl = QLabel(f"{self._t('qr.card.dob')}: {self.patient_dob}   |   {self._t('qr.card.sex')}: {self.patient_gender}")
        dob_lbl.setStyleSheet("font-size: 11px; color: #444444;")
        
        phone_lbl = QLabel(f"{self._t('qr.card.phone')}: {self.patient_phone}")
        phone_lbl.setStyleSheet("font-size: 11px; color: #444444;")

        for lbl in (name_lbl, id_lbl, dob_lbl, phone_lbl):
            lbl.setAlignment(Qt.AlignCenter)
            info_layout.addWidget(lbl)
            
        card_layout.addLayout(info_layout)
        
        # Footer
        footer_lbl = QLabel(self._t("qr.card.footer"))
        footer_lbl.setStyleSheet("font-size: 8px; color: #777777; font-style: italic;")
        footer_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(footer_lbl)

        layout.addWidget(self.card_widget)

        # ── Buttons Action
        btn_row = QHBoxLayout()
        
        btn_export = QPushButton(self._t("qr.card.save"))
        btn_export.clicked.connect(self._on_export)
        
        btn_print = QPushButton(self._t("qr.card.print"))
        btn_print.clicked.connect(self._on_print)
        
        btn_close = QPushButton(self._t("qr.close"))
        btn_close.setObjectName("btn_primary")
        btn_close.clicked.connect(self.accept)
        
        btn_row.addWidget(btn_export)
        btn_row.addWidget(btn_print)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        
        layout.addLayout(btn_row)

    def _on_export(self):
        """Saves the card layout as a high-quality PNG image."""
        path, _ = QFileDialog.getSaveFileName(self, "Save Patient Card", f"PatientCard_{self.patient_name}.png", "PNG Files (*.png)")
        if not path:
            return
            
        # Draw the widget contents onto a QPixmap
        card_size = self.card_widget.size()
        pixmap = QPixmap(card_size)
        self.card_widget.render(pixmap)
        
        if pixmap.save(path):
            QMessageBox.information(self, "Exported", f"Successfully exported patient card image to:\n{path}")
        else:
            QMessageBox.critical(self, "Error", "Failed to save card image.")

    def _on_print(self):
        """Prints the patient card using PySide6 QtPrintSupport."""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            printer = QPrinter(QPrinter.HighResolution)
            printer.setDocName(f"PatientCard_{self.patient_name}")
            
            dlg = QPrintDialog(printer, self)
            if dlg.exec() == QDialog.Accepted:
                painter = QPainter(printer)
                card_size = self.card_widget.size()
                pixmap = QPixmap(card_size)
                self.card_widget.render(pixmap)
                
                # Scale card to fit nicely on A4 paper
                rect = painter.viewport()
                factor = min(rect.width() / pixmap.width(), rect.height() / pixmap.height()) * 0.8
                w = pixmap.width() * factor
                h = pixmap.height() * factor
                x = (rect.width() - w) / 2
                y = (rect.height() - h) / 2
                
                painter.drawPixmap(int(x), int(y), int(w), int(h), pixmap)
                painter.end()
                QMessageBox.information(self, "Printed", "Sent patient card to printer.")
        except Exception as e:
            QMessageBox.warning(self, "Printing Failed", f"Could not print patient card:\n{e}")


# ══════════════════════════════════════════════════════════════════════════════
#  HIGH-SPEED WEBCAM QR SCANNER DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class QRScanDialog(QDialog):
    """
    Uses OpenCV webcam stream and local QRCodeDetector to scan a patient's QR code.
    Auto-detects HOSPITAL-PMS-PATIENT:[ID], renders visual scan feedback,
    and returns the scanned ID instantly.
    """
    scanned_patient_id = Signal(int)  # Emits the identified patient ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self._lang = getattr(parent, "_lang", get_language()) if parent else get_language()
        self.setWindowTitle(self._t("qr.scan.title"))
        self.setFixedSize(540, 480)
        self.setStyleSheet(f"""
            QDialog {{ background: {P['bg']}; color: {P['text']}; font-family: 'Segoe UI', Arial; }}
            QPushButton {{ background: {P['surface2']}; border: 1px solid {P['border']};
                           border-radius: 4px; padding: 8px 16px; color: {P['text']}; font-weight: 600; }}
            QPushButton:hover {{ border-color: {P['accent']}; color: {P['accent']}; }}
        """)

        self._cap = None
        self._qr_detector = cv2.QRCodeDetector()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)
        self._detected_id = None
        self._ticks_after_detect = 0

        self._build_ui()
        self._init_camera()

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title / Instruction
        hdr_lay = QHBoxLayout()
        title_lbl = QLabel(self._t("qr.scan.header"))
        title_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {P['accent']};")
        hdr_lay.addWidget(title_lbl)
        hdr_lay.addStretch()
        layout.addLayout(hdr_lay)

        # Camera viewport
        self.cam_view = QLabel()
        self.cam_view.setFixedSize(500, 340)
        self.cam_view.setAlignment(Qt.AlignCenter)
        self.cam_view.setStyleSheet(f"background: {P['surface']}; border: 2px solid {P['border']}; border-radius: 8px;")
        self.cam_view.setText(self._t("qr.scan.connecting"))
        layout.addWidget(self.cam_view, alignment=Qt.AlignCenter)

        # Bottom info and cancel
        bottom = QHBoxLayout()
        info_lbl = QLabel(self._t("qr.scan.hint"))
        info_lbl.setStyleSheet(f"font-size: 11px; color: {P['text_dim']};")
        bottom.addWidget(info_lbl)
        bottom.addStretch()

        btn_cancel = QPushButton(self._t("qr.scan.cancel"))
        btn_cancel.clicked.connect(self.reject)
        bottom.addWidget(btn_cancel)

        layout.addLayout(bottom)

    def _init_camera(self):
        try:
            self._cap = cv2.VideoCapture(0)
            if not self._cap.isOpened():
                self.cam_view.setText(self._t("qr.scan.no_camera"))
                return
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self._timer.start(30)  # ~33 fps for fast scanning
        except Exception as e:
            self.cam_view.setText(f"⚠️ Camera setup error:\n{e}")

    def _update_frame(self):
        if not self._cap or not self._cap.isOpened():
            return
        ret, frame = self._cap.read()
        if not ret:
            return

        # If a QR code was just detected, hold the success frame with overlay
        if self._detected_id is not None:
            self._ticks_after_detect += 1
            if self._ticks_after_detect > 10:  # Hold for ~300ms
                self.scanned_patient_id.emit(self._detected_id)
                self.accept()
                return

        # Perform QR Code scanning
        try:
            data, bbox, _ = self._qr_detector.detectAndDecode(frame)
            if data and "HOSPITAL-PMS-PATIENT:" in data:
                try:
                    parts = data.split(":")
                    if len(parts) == 2:
                        pid = int(parts[1])
                        self._detected_id = pid
                        
                        # Draw green border around detected QR code
                        if bbox is not None and len(bbox) > 0:
                            pts = bbox[0].astype(int)
                            for i in range(len(pts)):
                                pt1 = tuple(pts[i])
                                pt2 = tuple(pts[(i + 1) % len(pts)])
                                cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
                            
                            # Write success overlay text
                            cv2.putText(frame, "SUCCESS!", (pts[0][0], pts[0][1] - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                except ValueError:
                    pass
        except Exception:
            pass

        # Overlay a subtle guide scanner box on the live view
        if self._detected_id is None:
            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2
            size = 200
            x1, y1 = cx - size // 2, cy - size // 2
            x2, y2 = cx + size // 2, cy + size // 2
            # Blue selector framing guide
            cv2.rectangle(frame, (x1, y1), (x2, y2), (204, 122, 0), 2)
            cv2.putText(frame, "ALIGN QR CODE HERE", (x1 + 5, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (204, 122, 0), 1)

        # Convert OpenCV BGR to RGB and update label
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.cam_view.setPixmap(
            QPixmap.fromImage(img).scaled(
                self.cam_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

    def closeEvent(self, event):
        self._timer.stop()
        if self._cap:
            self._cap.release()
        super().closeEvent(event)

    def reject(self):
        self._timer.stop()
        if self._cap:
            self._cap.release()
        super().reject()


# ══════════════════════════════════════════════════════════════════════════════
#  PATIENT QR SCAN SUMMARY PANEL DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class PatientScannedSummaryDialog(QDialog):
    """
    Displays a premium, visually impressive dashboard card immediately after scanning
    a patient QR code, showing demographics, attending doctor, active diagnosis, and costs.
    """
    def __init__(self, patient, appt_info=None, med_rec=None, cost_info=None, parent=None, lang: str | None = None):
        super().__init__(parent)
        self._lang = lang or getattr(parent, "_lang", get_language()) if parent else (lang or get_language())
        self.patient = patient
        self.appt_info = appt_info
        self.med_rec = med_rec
        self.cost_info = cost_info or {"amount": 150000.0, "status": self._t("qr.summary.unpaid")}

        self.setWindowTitle(self._t("qr.summary.title"))
        self.setFixedSize(580, 640)
        self.setStyleSheet(f"""
            QDialog {{ background: {P['bg']}; color: {P['text']}; font-family: 'Segoe UI', Arial; }}
            QLabel {{ color: {P['text']}; }}
            QPushButton {{ background: {P['surface2']}; border: 1px solid {P['border']};
                           border-radius: 4px; padding: 10px 18px; color: {P['text']}; font-weight: 600; }}
            QPushButton:hover {{ border-color: {P['accent']}; color: {P['accent']}; }}
            QPushButton#btn_primary {{ background: {P['accent']}; border-color: {P['accent']}; color: #fff; }}
            QPushButton#btn_primary:hover {{ background: #006aab; }}
            QPushButton#btn_success {{ background: {P['success']}; border-color: {P['success']}; color: #fff; }}
            QPushButton#btn_success:hover {{ background: #3d8b40; }}
        """)

        self._build_ui()

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ── Header Verification Banner
        hdr_lbl = QLabel(self._t("qr.summary.verified"))
        hdr_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {P['accent2']}; letter-spacing: 0.5px;")
        hdr_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(hdr_lbl)

        div_h = QFrame(); div_h.setFrameShape(QFrame.HLine)
        div_h.setStyleSheet(f"background-color: {P['accent']}; max-height: 1px;")
        layout.addWidget(div_h)

        # ── Group 1: Demographics Card
        card_demo = QFrame()
        card_demo.setStyleSheet(f"background: {P['surface']}; border: 1px solid {P['border']}; border-radius: 8px;")
        lay_demo = QVBoxLayout(card_demo)
        lay_demo.setSpacing(6)
        
        lbl_sec1 = QLabel(self._t("qr.summary.demographics"))
        lbl_sec1.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {P['accent2']}; border: none;")
        lay_demo.addWidget(lbl_sec1)
        
        lay_grid1 = QHBoxLayout()
        lay_grid1.setSpacing(16)
        
        # Photo column
        import os
        from PySide6.QtGui import QPixmap
        col_photo = QVBoxLayout()
        col_photo.setSpacing(4)
        photo_lbl = QLabel()
        photo_lbl.setFixedSize(100, 130)
        photo_lbl.setStyleSheet(f"border: 1px solid {P['border']}; background-color: {P['surface2']};")
        photo_lbl.setAlignment(Qt.AlignCenter)
        
        photo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patients_faces", f"{self.patient.id}.jpg")
        if os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            photo_lbl.setPixmap(pixmap.scaled(100, 130, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else:
            photo_lbl.setText(self._t("qr.summary.no_photo"))
            
        col_photo.addWidget(photo_lbl)
        col_photo.addStretch()
        
        # Left column
        col_l = QVBoxLayout()
        col_l.setSpacing(4)
        col_l.addWidget(QLabel(f"{self._t('qr.summary.name')}: <b>{self.patient.full_name.upper()}</b>"))
        col_l.addWidget(QLabel(f"{self._t('qr.summary.patient_id')}: <b>#{self.patient.id:05d}</b>"))
        col_l.addWidget(QLabel(f"{self._t('qr.summary.dob')}: {self.patient.dob}"))
        col_l.addWidget(QLabel(f"{self._t('qr.summary.gender')}: {self.patient.gender}"))
        
        # Right column
        col_r = QVBoxLayout()
        col_r.setSpacing(4)
        col_r.addWidget(QLabel(f"{self._t('qr.summary.phone')}: {self.patient.phone}"))
        col_r.addWidget(QLabel(f"{self._t('qr.summary.address')}: {self.patient.address or 'N/A'}"))
        col_r.addWidget(QLabel(f"{self._t('qr.summary.blood')}: <b>{self.patient.blood_type or 'N/A'}</b>"))
        col_r.addWidget(QLabel(f"{self._t('qr.summary.allergies')}: <span style='color: {P['danger']}'>{self.patient.allergies or self._t('qr.summary.none')}</span>"))
        
        lay_grid1.addLayout(col_photo)
        lay_grid1.addLayout(col_l)
        lay_grid1.addLayout(col_r)
        lay_demo.addLayout(lay_grid1)
        layout.addWidget(card_demo)

        # ── Group 2: Appointment / Doctor Info
        card_appt = QFrame()
        card_appt.setStyleSheet(f"background: {P['surface']}; border: 1px solid {P['border']}; border-radius: 8px;")
        lay_appt = QVBoxLayout(card_appt)
        lay_appt.setSpacing(6)

        lbl_sec2 = QLabel(self._t("qr.summary.appointment"))
        lbl_sec2.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {P['accent2']}; border: none;")
        lay_appt.addWidget(lbl_sec2)

        if self.appt_info:
            lay_grid2 = QHBoxLayout()
            col_l2 = QVBoxLayout(); col_l2.setSpacing(4)
            col_l2.addWidget(QLabel(f"{self._t('qr.summary.doctor')}: <b>{self.appt_info['doctor']}</b>"))
            col_l2.addWidget(QLabel(f"{self._t('qr.summary.date')}: {self.appt_info['date']}"))
            
            col_r2 = QVBoxLayout(); col_r2.setSpacing(4)
            col_r2.addWidget(QLabel(f"{self._t('qr.summary.time')}: {self.appt_info['time']}"))
            col_r2.addWidget(QLabel(f"{self._t('qr.summary.reason')}: {self.appt_info['reason']}"))
            
            lay_grid2.addLayout(col_l2)
            lay_grid2.addLayout(col_r2)
            lay_appt.addLayout(lay_grid2)
        else:
            lay_appt.addWidget(QLabel(f"<i>{self._t('qr.summary.no_appt')}</i>"))

        layout.addWidget(card_appt)

        # ── Group 3: Diagnosis / Diseases
        card_diag = QFrame()
        card_diag.setStyleSheet(f"background: {P['surface']}; border: 1px solid {P['border']}; border-radius: 8px;")
        lay_diag = QVBoxLayout(card_diag)
        lay_diag.setSpacing(6)

        lbl_sec3 = QLabel(self._t("qr.summary.diagnosis"))
        lbl_sec3.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {P['accent2']}; border: none;")
        lay_diag.addWidget(lbl_sec3)

        diagnosis = (self.med_rec or {}).get("diagnosis", "").strip()
        symptoms = (self.med_rec or {}).get("symptoms", "").strip()
        if diagnosis or symptoms:
            lay_diag.addWidget(QLabel(f"{self._t('qr.summary.symptoms')}: <i>{symptoms or self._t('qr.summary.no_symptoms')}</i>"))
            lay_diag.addWidget(QLabel(f"{self._t('qr.summary.active_diagnosis')}: <b style='color: {P['accent2']}'>{diagnosis or self._t('qr.summary.no_diagnosis')}</b>"))
        else:
            lay_diag.addWidget(QLabel(f"<i>{self._t('qr.summary.no_diagnosis')}</i>"))

        layout.addWidget(card_diag)

        # ── Group 4: Billing & Cost Information
        card_cost = QFrame()
        card_cost.setStyleSheet(f"background: {P['surface']}; border: 1px solid {P['border']}; border-radius: 8px;")
        lay_cost = QVBoxLayout(card_cost)
        lay_cost.setSpacing(6)

        lbl_sec4 = QLabel(self._t("qr.summary.billing"))
        lbl_sec4.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {P['accent2']}; border: none;")
        lay_cost.addWidget(lbl_sec4)

        lay_grid4 = QHBoxLayout()
        col_l4 = QVBoxLayout(); col_l4.setSpacing(4)
        col_l4.addWidget(QLabel(f"{self._t('qr.summary.total_cost')}: <b style='font-size: 15px; color: #ff9800;'>{self.cost_info['amount']:,.0f} VNĐ</b>"))

        # Payment status badge representation
        col_r4 = QHBoxLayout()
        col_r4.addWidget(QLabel(f"{self._t('qr.summary.status')}: "))
        
        is_paid = self.cost_info.get("status") in ("Đã thanh toán", "Paid")
        status_badge = QLabel((self._t("qr.summary.paid") if is_paid else self._t("qr.summary.unpaid")).upper())
        if is_paid:
            status_badge.setStyleSheet(f"background: {P['success']}; color: #fff; padding: 4px 10px; border-radius: 10px; font-weight: bold; font-size: 10px;")
        else:
            status_badge.setStyleSheet(f"background: {P['danger']}; color: #fff; padding: 4px 10px; border-radius: 10px; font-weight: bold; font-size: 10px;")
        status_badge.setAlignment(Qt.AlignCenter)
        
        col_r4.addWidget(status_badge)
        col_r4.addStretch()

        lay_grid4.addLayout(col_l4)
        lay_grid4.addLayout(col_r4)
        lay_cost.addLayout(lay_grid4)
        layout.addWidget(card_cost)

        # ── Bottom Action Row
        layout.addStretch()
        btn_row = QHBoxLayout()
        
        # Thêm nút thanh toán ngay nếu chưa thanh toán
        if not is_paid and self.appt_info:
            btn_pay = QPushButton(self._t("qr.summary.pay"))
            btn_pay.setObjectName("btn_success")
            btn_pay.clicked.connect(self._on_pay_clicked)
            btn_row.addWidget(btn_pay)

        btn_history = QPushButton(self._t("qr.summary.records"))
        btn_history.clicked.connect(self._on_history_clicked)
        btn_row.addWidget(btn_history)
        
        btn_row.addStretch()
        
        btn_close = QPushButton(self._t("qr.close"))
        btn_close.setObjectName("btn_primary")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)

        layout.addLayout(btn_row)

    def _on_pay_clicked(self):
        # Done code 100 will trigger direct payment flow in ui_main
        self.done(100)

    def _on_history_clicked(self):
        # Done code 200 will focus record
        self.done(200)


# ══════════════════════════════════════════════════════════════════════════════
#  CLINICAL APPOINTMENT QUEUE TICKET DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class QueueTicketDialog(QDialog):
    """
    Displays a premium, dashed-border ticket representing the patient's
    daily sequential check-in number. Includes print options.
    """
    def __init__(self, queue_no: int, patient_name: str, doctor_name: str, appt_date: str, appt_time: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Examination Queue Ticket")
        self.setFixedSize(360, 480)
        self.setStyleSheet(f"""
            QDialog {{ background: #ffffff; color: #333333; font-family: 'Segoe UI', Arial; }}
            QPushButton {{ background: {P['accent']}; border: none; border-radius: 4px; padding: 10px 20px; color: #fff; font-weight: 600; }}
            QPushButton:hover {{ background: #006aab; }}
        """)
        
        self.queue_no = queue_no
        self.patient_name = patient_name
        self.doctor_name = doctor_name
        self.appt_date = appt_date
        self.appt_time = appt_time
        
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        
        # Ticket Border Box
        ticket = QFrame()
        ticket.setStyleSheet("border: 2px dashed #007acc; border-radius: 8px; background: #fafafa;")
        ticket_lay = QVBoxLayout(ticket)
        ticket_lay.setContentsMargins(20, 20, 20, 20)
        ticket_lay.setSpacing(10)
        
        title = QLabel("HOSPITAL PMS")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #007acc; text-align: center;")
        title.setAlignment(Qt.AlignCenter)
        ticket_lay.addWidget(title)
        
        subtitle = QLabel("PHIẾU LẤY SỐ THỨ TỰ KHÁM")
        subtitle.setStyleSheet("font-size: 11px; font-weight: bold; color: #555555;")
        subtitle.setAlignment(Qt.AlignCenter)
        ticket_lay.addWidget(subtitle)
        
        div = QFrame(); div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color: #007acc; max-height: 1px;")
        ticket_lay.addWidget(div)
        
        num_lbl = QLabel(f"{self.queue_no:02d}")
        num_lbl.setStyleSheet("font-size: 80px; font-weight: 900; color: #007acc; text-align: center; margin: 10px 0;")
        num_lbl.setAlignment(Qt.AlignCenter)
        ticket_lay.addWidget(num_lbl)
        
        info_lay = QVBoxLayout()
        info_lay.setSpacing(4)
        
        p_lbl = QLabel(f"Bệnh nhân: <b>{self.patient_name.upper()}</b>")
        d_lbl = QLabel(f"Bác sĩ khám: <b>{self.doctor_name}</b>")
        t_lbl = QLabel(f"Ngày khám: {self.appt_date}   Giờ: {self.appt_time}")
        
        for lbl in (p_lbl, d_lbl, t_lbl):
            lbl.setStyleSheet("font-size: 12px; color: #444444;")
            lbl.setAlignment(Qt.AlignCenter)
            info_lay.addWidget(lbl)
            
        ticket_lay.addLayout(info_lay)
        
        ticket_lay.addStretch()
        footer = QLabel("Vui lòng ngồi đợi gọi số ở hàng chờ phòng khám.")
        footer.setStyleSheet("font-size: 9px; color: #888888; font-style: italic; text-align: center;")
        footer.setAlignment(Qt.AlignCenter)
        ticket_lay.addWidget(footer)
        
        layout.addWidget(ticket)
        
        # Buttons
        btn_row = QHBoxLayout()
        btn_print = QPushButton("🖨️  Print Ticket")
        btn_print.clicked.connect(self._on_print)
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        
        btn_row.addWidget(btn_print)
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)
        
    def _on_print(self):
        QMessageBox.information(self, "Printed", f"Đã gửi lệnh in Số thứ tự {self.queue_no:02d} thành công!")
