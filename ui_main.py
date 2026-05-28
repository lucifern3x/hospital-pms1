"""
ui_main.py  –  All PySide6 widgets / dialogs for Hospital PMS
"""
from __future__ import annotations

import base64
import os
import sys
from typing import Optional

HOSPITAL_RECEIPT_ADDRESS = "470 Trần Đại Nghĩa, Ngũ Hành Sơn, Đà Nẵng, Việt Nam"


def _receipt_qr_image_html(width: int = 110) -> str:
    """Embed VietQR image as base64 for PDF/PNG receipt export."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for fname, mime in (
        ("qr_receipt_vietqr.png", "image/png"),
        ("qr_payment.png", "image/png"),
        ("qr_payment.jpg", "image/jpeg"),
    ):
        path = os.path.join(base_dir, fname)
        if not os.path.isfile(path):
            continue
        with open(path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        return (
            f'<img src="data:{mime};base64,{b64}" width="{width}" '
            f'style="display:inline-block;max-width:{width}px;height:auto;" alt="VietQR" />'
        )
    return ""
import qtawesome as qta

from PySide6.QtCore import (Qt, QDate, QTime, QTimer, QSortFilterProxyModel, QPropertyAnimation, QEasingCurve, QSize,
                             QAbstractTableModel, QModelIndex, Signal)
from PySide6.QtGui import (QColor, QFont, QIcon, QPalette, QPixmap, QMovie,
                            QPainter, QBrush, QLinearGradient)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QTimeEdit, QTextEdit,
    QTableView, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QFrame, QMessageBox,
    QSplitter, QScrollArea, QGroupBox, QStatusBar, QSizePolicy,
    QSpacerItem, QStyledItemDelegate, QAbstractItemView,
    QRadioButton, QButtonGroup, QCheckBox, QTextBrowser, QListWidget, QListWidgetItem,
)

from database import Database
from i18n import load_language, get_language, set_language, tr, lang_label
from patient import (Patient, Appointment, Medication, Prescription,
                     PrescriptionItem, MedicalRecord, Payment, LabTest)

PATIENT_HEADER_KEYS = [
    "th.id", "th.full_name", "th.dob", "th.age",
    "th.gender", "th.phone", "th.email", "th.blood_type",
]

DISEASE_CATALOG = [
    ("Nội khoa", [
        "Cảm cúm", "Sốt siêu vi", "Viêm họng", "Viêm phổi",
        "Cao huyết áp", "Tiểu đường", "Đau dạ dày", "Gan nhiễm mỡ",
    ]),
    ("Tim mạch", [
        "Tăng huyết áp", "Suy tim", "Rối loạn nhịp tim", "Đột quỵ",
    ]),
    ("Hô hấp", [
        "Hen suyễn", "Viêm phế quản", "COPD", "COVID-19",
    ]),
    ("Tiêu hóa", [
        "Viêm dạ dày", "Trào ngược dạ dày", "Táo bón", "Tiêu chảy",
    ]),
    ("Da liễu", [
        "Dị ứng da", "Nấm da", "Viêm da cơ địa", "Mụn trứng cá",
    ]),
    ("Cơ xương khớp", [
        "Thoái hóa khớp", "Gout", "Đau lưng", "Viêm khớp",
    ]),
    ("Nhi khoa", [
        "Sốt", "Tay chân miệng", "Sởi", "Viêm tai giữa",
    ]),
    ("Tai Mũi Họng", [
        "Viêm xoang", "Viêm amidan", "Viêm tai giữa",
    ]),
    ("Sản phụ khoa", [
        "Thai kỳ", "Viêm phụ khoa", "Rối loạn kinh nguyệt",
    ]),
    ("Thần kinh", [
        "Migraine", "Mất ngủ", "Parkinson", "Động kinh",
    ]),
]

MINI_AI_MAX_SUGGESTIONS = 30

MINI_AI_MED_RULES = [
    (("cảm cúm", "sốt siêu vi", "covid-19"), ["Paracetamol", "Vitamin C", "Cetirizine", "Oseltamivir"]),
    (("sốt",), ["Paracetamol", "Oral Rehydration Salts"]),
    (("viêm họng", "viêm amidan"), ["Paracetamol", "Cetirizine", "Amoxicillin", "Cefuroxime"]),
    (("viêm phổi",), ["Amoxicillin", "Azithromycin", "Cefuroxime", "Levofloxacin", "Ceftriaxone", "Ambroxol"]),
    (("viêm phế quản",), ["Ambroxol", "Dextromethorphan", "Guaifenesin", "Salbutamol", "Azithromycin"]),
    (("viêm xoang", "viêm tai giữa"), ["Amoxicillin", "Cefuroxime", "Cefixime", "Paracetamol"]),
    (("cao huyết áp", "tăng huyết áp", "hypertension"), ["Amlodipine", "Lisinopril", "Losartan"]),
    (("suy tim", "rối loạn nhịp tim", "heart failure", "arrhythmia"), ["Metoprolol", "ECG"]),
    (("đột quỵ", "stroke"), ["Aspirin", "Clopidogrel"]),
    (("tiểu đường", "diabetes"), ["Metformin", "Glucose Blood Test"]),
    (("đau dạ dày", "viêm dạ dày", "trào ngược dạ dày"), ["Omeprazole", "Pantoprazole", "Sucralfate", "Domperidone", "Simethicone"]),
    (("gan nhiễm mỡ",), ["Liver Function Test", "Lipid Panel Test"]),
    (("hen suyễn", "asthma", "copd"), ["Salbutamol", "Montelukast", "Budesonide", "Ipratropium"]),
    (("táo bón",), ["Lactulose", "Magnesium B6"]),
    (("tiêu chảy",), ["Oral Rehydration Salts", "Loperamide", "Simethicone"]),
    (("dị ứng da", "viêm da cơ địa"), ["Cetirizine", "Loratadine", "Hydrocortisone"]),
    (("nấm da",), ["Clotrimazole", "Miconazole", "Fluconazole"]),
    (("mụn trứng cá",), ["Benzoyl Peroxide", "Adapalene", "Doxycycline"]),
    (("thoái hóa khớp", "đau lưng", "chronic back pain", "back pain", "viêm khớp"), ["Ibuprofen", "Meloxicam", "Diclofenac gel", "Naproxen"]),
    (("gout",), ["Colchicine", "Allopurinol", "Naproxen"]),
    (("migraine",), ["Paracetamol", "Ibuprofen", "Naproxen"]),
    (("mất ngủ",), ["Melatonin", "Magnesium B6"]),
    (("động kinh",), ["Carbamazepine", "Specialist Consultation"]),
    (("thai kỳ",), ["Folic Acid", "Iron Supplements", "Calcium + D3"]),
    (("tay chân miệng", "sởi"), ["Paracetamol", "Oral Rehydration Salts", "Vitamin C"]),
    (("viêm phụ khoa", "rối loạn kinh nguyệt", "parkinson"), ["General Checkup", "Specialist Consultation"]),
]


# ══════════════════════════════════════════════════════════════════════════════
#  COLOUR PALETTE & STYLE
# ══════════════════════════════════════════════════════════════════════════════
PALETTE = {
    "bg":          "#121212",
    "surface":     "#1e1e1e",
    "surface2":    "#252526",
    "accent":      "#007acc",
    "accent2":     "#0098ff",
    "danger":      "#f14c4c",
    "warning":     "#cca700",
    "text":        "#cccccc",
    "text_dim":    "#858585",
    "border":      "#3c3c3c",
    "row_alt":     "#1e1e1e",
    "row_hover":   "#2a2d2e",
    "row_sel":     "#094771",
}

GLOBAL_QSS = f"""
QMainWindow, QDialog {{
    background: {PALETTE['bg']};
}}
QWidget {{
    background: transparent;
    color: {PALETTE['text']};
    font-family: 'Segoe UI', 'SF Pro Display', Arial;
    font-size: 13px;
}}
QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 4px;
    padding: 8px 12px;
    color: {PALETTE['text']};
    selection-background-color: {PALETTE['accent']};
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QTextEdit:focus {{
    border: 1px solid {PALETTE['accent']};
}}
QComboBox QAbstractItemView {{
    background: {PALETTE['surface2']};
    border: 1px solid {PALETTE['border']};
    selection-background-color: {PALETTE['accent']};
}}
QComboBox::drop-down {{ border: none; }}
QComboBox::down-arrow {{ image: none; width: 12px; height: 12px; }}
QPushButton {{
    background: {PALETTE['surface2']};
    border: 1px solid {PALETTE['border']};
    border-radius: 4px;
    padding: 8px 16px;
    color: {PALETTE['text']};
    font-weight: 600;
}}
QPushButton:hover {{
    background: {PALETTE['row_hover']};
    border-color: {PALETTE['text_dim']};
}}
QPushButton:pressed {{ opacity: 0.8; background: {PALETTE['surface']}; }}
QPushButton#btn_primary {{
    background: {PALETTE['accent']};
    border-color: {PALETTE['accent']};
    color: #ffffff;
}}
QPushButton#btn_primary:hover {{ background: #006bb3; }}
QPushButton#btn_danger {{ background: transparent; border-color: {PALETTE['danger']}; color: {PALETTE['danger']}; }}
QPushButton#btn_danger:hover {{ background: {PALETTE['danger']}; color: #ffffff; }}
QPushButton#btn_accent2 {{ background: transparent; border-color: {PALETTE['accent2']}; color: {PALETTE['accent2']}; }}
QPushButton#btn_accent2:hover {{ background: {PALETTE['accent2']}; color: #ffffff; }}
QPushButton#btn_ghost {{ background: transparent; border: none; }}
QPushButton#btn_ghost:hover {{ background: {PALETTE['surface2']}; }}

QTableView {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 6px;
    gridline-color: transparent;
    alternate-background-color: {PALETTE['row_alt']};
    selection-background-color: {PALETTE['row_sel']};
}}
QTableView::item {{ border-bottom: 1px solid {PALETTE['border']}; padding: 4px; }}
QHeaderView::section {{
    background: {PALETTE['bg']};
    color: {PALETTE['text_dim']};
    font-weight: 600;
    font-size: 11px;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {PALETTE['border']};
    text-transform: uppercase;
}}
QTabWidget::pane {{ border: none; background: {PALETTE['bg']}; }}
QScrollBar:vertical {{ background: {PALETTE['bg']}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {PALETTE['border']}; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {PALETTE['text_dim']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QGroupBox {{
    border: 1px solid {PALETTE['border']};
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 10px;
    color: {PALETTE['text_dim']};
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; top: -8px; color: {PALETTE['accent']}; background: {PALETTE['bg']}; padding: 0 4px; }}
QLabel#section_title {{ font-size: 11px; font-weight: 700; color: {PALETTE['text_dim']}; letter-spacing: 1.2px; text-transform: uppercase; }}
QStatusBar {{ background: {PALETTE['accent']}; color: #ffffff; font-weight: 600; }}
QFrame#divider {{ background: {PALETTE['border']}; max-height: 1px; }}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  TABLE MODEL
# ══════════════════════════════════════════════════════════════════════════════
class PatientTableModel(QAbstractTableModel):
    def __init__(self, patients: list[Patient] = None, lang: str | None = None):
        super().__init__()
        self._data: list[Patient] = patients or []
        self._lang = lang or get_language()
        self._headers = [tr(k, self._lang) for k in PATIENT_HEADER_KEYS]

    def set_language(self, lang: str) -> None:
        self._lang = lang
        self._headers = [tr(k, lang) for k in PATIENT_HEADER_KEYS]
        self.headerDataChanged.emit(Qt.Horizontal, 0, len(self._headers) - 1)

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        p = self._data[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            return [str(p.id), p.full_name, p.display_dob, str(p.age),
                    p.gender, p.phone, p.email, p.blood_type][col]
        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter | (Qt.AlignCenter if col in (0, 3, 4, 7)
                                      else Qt.AlignLeft)
        if role == Qt.ForegroundRole:
            if col == 4:   # gender
                return QColor(PALETTE["accent2"]) if p.gender == "Male" else QColor("#ff8fab")
            if col == 7:   # blood type
                return QColor(PALETTE["warning"])
        return None

    def patient_at(self, row: int) -> Optional[Patient]:
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def refresh(self, patients: list[Patient]) -> None:
        self.beginResetModel()
        self._data = patients
        self.endResetModel()


# ══════════════════════════════════════════════════════════════════════════════
#  STAT CARD WIDGET
# ══════════════════════════════════════════════════════════════════════════════
class StatCard(QFrame):
    def __init__(self, title: str, value: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['border']};
                border-left: 4px solid {color};
                border-radius: 10px;
                padding: 4px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 22px; color: {color};")
        top.addWidget(icon_lbl)
        top.addStretch()
        layout.addLayout(top)

        val_lbl = QLabel(value)
        val_lbl.setObjectName("val")
        val_lbl.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {color};")
        layout.addWidget(val_lbl)

        ttl_lbl = QLabel(title)
        ttl_lbl.setStyleSheet(f"font-size: 11px; color: {PALETTE['text_dim']}; font-weight: 600;")
        layout.addWidget(ttl_lbl)

        self._val_lbl = val_lbl
        self._ttl_lbl = ttl_lbl

    def update_value(self, value: str) -> None:
        self._val_lbl.setText(value)

    def set_title(self, title: str) -> None:
        self._ttl_lbl.setText(title)


# ══════════════════════════════════════════════════════════════════════════════
#  PATIENT DIALOG (Add / Edit)
# ══════════════════════════════════════════════════════════════════════════════
class PatientDialog(QDialog):
    def __init__(self, parent=None, patient: Optional[Patient] = None):
        super().__init__(parent)
        self._patient = patient
        self._lang = getattr(parent, "_lang", get_language()) if parent else get_language()
        self._initial_diagnosis = ""
        self.setWindowTitle(self._t("patient.dlg.edit_title") if patient else self._t("patient.dlg.add_title"))
        self.setMinimumWidth(680)
        self.setStyleSheet(f"background: {PALETTE['surface']}; border-radius: 12px;")
        self._build_ui()
        if patient:
            self._populate(patient)

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── title
        ttl = QLabel(self._t("patient.dlg.edit_header") if self._patient else self._t("patient.dlg.add_header"))
        ttl.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {PALETTE['accent']};")
        layout.addWidget(ttl)

        div = QFrame(); div.setObjectName("divider"); div.setFixedHeight(1)
        div.setStyleSheet(f"background: {PALETTE['border']};")
        layout.addWidget(div)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setMaximumHeight(460)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        form_host = QWidget()
        form_host.setStyleSheet("background: transparent;")

        form = QFormLayout(form_host)
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        lbl_style = f"color: {PALETTE['text_dim']}; font-weight: 600; font-size: 12px;"

        def lbl(text):
            l = QLabel(text)
            l.setStyleSheet(lbl_style)
            return l

        self.inp_name   = QLineEdit(); self.inp_name.setPlaceholderText(self._t("patient.dlg.name_ph"))
        self.inp_dob    = QDateEdit(QDate.currentDate()); self.inp_dob.setCalendarPopup(True)
        self.inp_dob.setDisplayFormat("dd/MM/yyyy")
        self.inp_gender = QComboBox()
        for code, key in [("Male", "gender.male"), ("Female", "gender.female"), ("Other", "gender.other")]:
            self.inp_gender.addItem(self._t(key), code)
        self.inp_phone  = QLineEdit(); self.inp_phone.setPlaceholderText(self._t("patient.dlg.phone_ph"))
        self.inp_email  = QLineEdit(); self.inp_email.setPlaceholderText(self._t("patient.dlg.email_ph"))
        self.inp_addr   = QLineEdit(); self.inp_addr.setPlaceholderText(self._t("patient.dlg.address_ph"))
        self.inp_blood  = QComboBox()
        self.inp_blood.addItems(["", "A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        self.inp_allerg = QLineEdit(); self.inp_allerg.setPlaceholderText(self._t("patient.dlg.allergies_ph"))
        self.disease_picker = self._build_disease_picker()
        self.inp_notes  = QTextEdit(); self.inp_notes.setFixedHeight(70)
        self.inp_notes.setPlaceholderText(self._t("patient.dlg.notes_ph"))

        form.addRow(lbl(self._t("patient.dlg.full_name")),  self.inp_name)
        form.addRow(lbl(self._t("patient.dlg.dob")), self.inp_dob)
        form.addRow(lbl(self._t("patient.dlg.gender")),     self.inp_gender)
        form.addRow(lbl(self._t("patient.dlg.phone")),      self.inp_phone)
        form.addRow(lbl(self._t("patient.dlg.email")),        self.inp_email)
        form.addRow(lbl(self._t("patient.dlg.address")),      self.inp_addr)
        form.addRow(lbl(self._t("patient.dlg.blood_type")),   self.inp_blood)
        form.addRow(lbl(self._t("patient.dlg.allergies")),    self.inp_allerg)
        form.addRow(lbl(self._t("patient.dlg.diagnosis")),    self.disease_picker)
        form.addRow(lbl(self._t("patient.dlg.notes")),        self.inp_notes)
        scroll.setWidget(form_host)
        layout.addWidget(scroll, stretch=1)

        # ── buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton(self._t("patient.dlg.cancel"))
        btn_cancel.setFixedWidth(100)
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton(self._t("patient.dlg.save"))
        btn_save.setObjectName("btn_primary")
        btn_save.setFixedWidth(120)
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _build_disease_picker(self) -> QWidget:
        picker = QWidget()
        picker.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(picker)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.cmb_specialty = QComboBox()
        for specialty, _ in DISEASE_CATALOG:
            self.cmb_specialty.addItem(specialty, specialty)
        self.cmb_specialty.currentIndexChanged.connect(self._populate_disease_table)
        layout.addWidget(self.cmb_specialty)

        self.tbl_disease = QTableWidget(0, 1)
        self.tbl_disease.setHorizontalHeaderLabels([self._t("patient.dlg.disease")])
        self.tbl_disease.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_disease.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tbl_disease.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_disease.setAlternatingRowColors(True)
        self.tbl_disease.verticalHeader().setVisible(False)
        self.tbl_disease.setShowGrid(False)
        self.tbl_disease.setFixedHeight(135)
        self.tbl_disease.setToolTip(self._t("patient.dlg.diagnosis_ph"))
        self.tbl_disease.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.tbl_disease)

        self._populate_disease_table()
        return picker

    def _populate_disease_table(self) -> None:
        if not hasattr(self, "tbl_disease"):
            return
        specialty = self.cmb_specialty.currentData()
        diseases = next((items for name, items in DISEASE_CATALOG if name == specialty), [])
        self.tbl_disease.setRowCount(0)
        for disease in diseases:
            row = self.tbl_disease.rowCount()
            self.tbl_disease.insertRow(row)
            item = QTableWidgetItem(disease)
            item.setData(Qt.UserRole, disease)
            self.tbl_disease.setItem(row, 0, item)
        if diseases:
            self.tbl_disease.selectRow(0)

    def _selected_diagnosis(self) -> str:
        row = self.tbl_disease.currentRow()
        if row < 0:
            return self._initial_diagnosis
        specialty = self.cmb_specialty.currentData()
        disease_item = self.tbl_disease.item(row, 0)
        if not specialty or not disease_item:
            return self._initial_diagnosis
        return f"{specialty} - {disease_item.text()}"

    def _select_diagnosis(self, diagnosis: str) -> None:
        self._initial_diagnosis = diagnosis
        normalized = diagnosis.strip().lower()
        if " - " in normalized:
            _, normalized_disease = normalized.split(" - ", 1)
        else:
            normalized_disease = normalized
        for spec_index, (specialty, diseases) in enumerate(DISEASE_CATALOG):
            specialty_l = specialty.strip().lower()
            for disease_index, disease in enumerate(diseases):
                disease_l = disease.strip().lower()
                combined = f"{specialty_l} - {disease_l}"
                if normalized in (combined, disease_l) or normalized_disease == disease_l:
                    self.cmb_specialty.setCurrentIndex(spec_index)
                    self.tbl_disease.selectRow(disease_index)
                    self.tbl_disease.scrollToItem(self.tbl_disease.item(disease_index, 0), QAbstractItemView.PositionAtCenter)
                    return

    def _populate(self, p: Patient) -> None:
        self.inp_name.setText(p.full_name)
        try:
            from datetime import date
            d = date.fromisoformat(p.dob)
            self.inp_dob.setDate(QDate(d.year, d.month, d.day))
        except Exception:
            pass
        idx = self.inp_gender.findData(p.gender)
        self.inp_gender.setCurrentIndex(idx if idx >= 0 else 0)
        self.inp_phone.setText(p.phone)
        self.inp_email.setText(p.email)
        self.inp_addr.setText(p.address)
        self.inp_blood.setCurrentText(p.blood_type)
        self.inp_allerg.setText(p.allergies)
        
        self._select_diagnosis(p.active_diagnosis)
        self.inp_notes.setPlainText(p.display_notes)

    def _on_save(self) -> None:
        name  = self.inp_name.text().strip()
        phone = self.inp_phone.text().strip()
        if not name or not phone:
            QMessageBox.warning(self, self._t("patient.dlg.validation_title"), self._t("patient.dlg.validation_required"))
            return
        self.accept()

    def get_patient(self) -> Patient:
        qd = self.inp_dob.date()
        dob = f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"
        pid = self._patient.id if self._patient else None
        
        diag = self._selected_diagnosis().strip()
        user_notes = self.inp_notes.toPlainText().strip()
        combined_notes = []
        if diag:
            combined_notes.append(f"Diagnosis: {diag}")
        if user_notes:
            combined_notes.append(user_notes)
        notes = "\n".join(combined_notes)

        return Patient(
            id=pid,
            full_name=self.inp_name.text().strip(),
            dob=dob,
            gender=self.inp_gender.currentData(),
            phone=self.inp_phone.text().strip(),
            email=self.inp_email.text().strip(),
            address=self.inp_addr.text().strip(),
            blood_type=self.inp_blood.currentText(),
            allergies=self.inp_allerg.text().strip(),
            notes=notes,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  APPOINTMENT DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class AppointmentDialog(QDialog):
    def __init__(self, parent=None, patient_list: list[tuple] = None, doctor_list: list[Doctor] = None, appt=None):
        super().__init__(parent)
        self._patient_list = patient_list or []
        self._doctor_list = doctor_list or []
        self._appt = appt
        self.setWindowTitle("Schedule Appointment")
        self.setMinimumWidth(460)
        self.setStyleSheet(f"background: {PALETTE['surface']};")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        ttl = QLabel("📅  Schedule Appointment")
        ttl.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {PALETTE['accent2']};")
        layout.addWidget(ttl)

        form = QFormLayout(); form.setSpacing(12)
        lbl_s = f"color: {PALETTE['text_dim']}; font-weight: 600; font-size: 12px;"
        def lbl(t): l = QLabel(t); l.setStyleSheet(lbl_s); return l

        self.cmb_patient = QComboBox()
        for pid, pname in self._patient_list:
            self.cmb_patient.addItem(pname, userData=pid)
            
        self.cmb_doctor = QComboBox()
        self.cmb_doctor.addItem("-- Chọn Bác sĩ / Select Doctor --", userData="")
        
        # Populate doctors from database (excluding Admin accounts)
        for d in self._doctor_list:
            if d.role == "Admin" or d.username == "admin":
                continue
            display_str = f"{d.full_name} ({d.specialty})" if d.specialty else d.full_name
            self.cmb_doctor.addItem(display_str, userData=d.full_name)
            
        self.inp_date    = QDateEdit(QDate.currentDate()); self.inp_date.setCalendarPopup(True)
        self.inp_date.setDisplayFormat("dd/MM/yyyy")
        self.inp_time    = QTimeEdit(QTime(9, 0))
        self.inp_time.setDisplayFormat("HH:mm")
        self.inp_reason  = QLineEdit(); self.inp_reason.setPlaceholderText("Reason for visit…")
        self.cmb_status  = QComboBox()
        self.cmb_status.addItems(["Scheduled", "Completed", "Cancelled"])

        form.addRow(lbl("Patient *"),  self.cmb_patient)
        form.addRow(lbl("Doctor *"),   self.cmb_doctor)
        form.addRow(lbl("Date *"),     self.inp_date)
        form.addRow(lbl("Time *"),     self.inp_time)
        form.addRow(lbl("Reason"),     self.inp_reason)
        form.addRow(lbl("Status"),     self.cmb_status)
        layout.addLayout(form)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Cancel"); bc.setFixedWidth(100); bc.clicked.connect(self.reject)
        bs = QPushButton("💾  Save"); bs.setObjectName("btn_primary")
        bs.setFixedWidth(120); bs.clicked.connect(self._on_save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        layout.addLayout(btn_row)
        
        if self._appt:
            self._populate()

    def _populate(self) -> None:
        idx = self.cmb_patient.findData(self._appt.patient_id)
        if idx >= 0: self.cmb_patient.setCurrentIndex(idx)
        self.cmb_patient.setEnabled(False) # Usually don't change patient for existing appt
        
        # Select the doctor
        idx_doc = self.cmb_doctor.findData(self._appt.doctor)
        if idx_doc >= 0:
            self.cmb_doctor.setCurrentIndex(idx_doc)
        else:
            idx_text = self.cmb_doctor.findText(self._appt.doctor)
            if idx_text >= 0:
                self.cmb_doctor.setCurrentIndex(idx_text)
                
        from PySide6.QtCore import QDate, QTime
        self.inp_date.setDate(QDate.fromString(self._appt.appointment_date, "yyyy-MM-dd"))
        self.inp_time.setTime(QTime.fromString(self._appt.appointment_time, "HH:mm"))
        self.inp_reason.setText(self._appt.reason)
        self.cmb_status.setCurrentText(self._appt.status)

    def _on_save(self) -> None:
        doc_name = self.cmb_doctor.currentData()
        if not doc_name:
            QMessageBox.warning(self, "Validation", "Doctor name is required.")
            return
        self.accept()

    def get_appointment(self) -> Appointment:
        qd = self.inp_date.date()
        qt = self.inp_time.time()
        aid = self._appt.id if self._appt else None
        doc_name = self.cmb_doctor.currentData() or ""
            
        return Appointment(
            id=aid,
            patient_id=self.cmb_patient.currentData(),
            doctor=doc_name,
            appointment_date=f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}",
            appointment_time=f"{qt.hour():02d}:{qt.minute():02d}",
            reason=self.inp_reason.text().strip(),
            status=self.cmb_status.currentText(),
        )


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR BUTTON
# ══════════════════════════════════════════════════════════════════════════════
class SidebarBtn(QPushButton):
    def __init__(self, icon_name: str, label: str, parent=None):
        super().__init__(f"  {label}", parent)
        self.setCheckable(True)
        self.setFixedHeight(44)
        
        # Load icon using qtawesome
        self.icon_active = qta.icon(icon_name, color=PALETTE['accent'])
        self.icon_inactive = qta.icon(icon_name, color=PALETTE['text_dim'])
        self.setIcon(self.icon_inactive)
        self.setIconSize(QSize(20, 20))
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding-left: 16px;
                color: {PALETTE['text_dim']};
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {PALETTE['surface2']};
                color: {PALETTE['text']};
            }}
            QPushButton:checked {{
                background: {PALETTE['surface']};
                border-left: 4px solid {PALETTE['accent']};
                color: {PALETTE['text']};
                font-weight: 700;
            }}
        """)

    def nextCheckState(self):
        super().nextCheckState()
        self.setIcon(self.icon_active if self.isChecked() else self.icon_inactive)

    def set_sidebar_label(self, label: str) -> None:
        self.setText(f"  {label}")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self, db: Database, doctor=None) -> None:
        super().__init__()
        self._db = db
        self._doctor = doctor   # logged-in Doctor dataclass
        self._lang = load_language()
        self.setMinimumSize(1180, 720)
        self.setStyleSheet(GLOBAL_QSS)
        self._selected_patient: Optional[Patient] = None
        self._lab_completion_timers: dict[int, QTimer] = {}
        self._payment_dashboard_timers: dict[int, list[QTimer]] = {}
        self._build_ui()
        self._retranslate_ui()
        self._load_patients()
        self._refresh_stats()

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _toggle_language(self) -> None:
        self._lang = "en" if self._lang == "vi" else "vi"
        set_language(self._lang)
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        self.setWindowTitle(self._t("app.title"))
        who = f"  👤 {self._doctor.full_name} ({self._doctor.role})" if self._doctor else ""
        self._status.showMessage(f"{self._t('app.status')}{who}")
        self._appname_lbl.setText(self._t("app.pms"))

        for btn, key in self._sidebar_i18n:
            btn.set_sidebar_label(self._t(key))

        self._lbl_patients_title.setText(self._t("patients.title"))
        self._btn_add.setText(self._t("patients.add"))
        self._btn_edit.setText(self._t("patients.edit"))
        self._btn_delete.setText(self._t("patients.delete"))
        self._btn_qr.setText(self._t("patients.qr"))
        self._btn_scan_qr.setText(self._t("patients.scan"))
        self._search_inp.setPlaceholderText(self._t("patients.search"))
        self._model.set_language(self._lang)

        self._lbl_appts_title.setText(self._t("appts.title"))
        self._btn_add_appt_hdr.setText(self._t("appts.schedule"))
        self._btn_queue.setText(self._t("appts.queue"))
        self._btn_prescribe.setText(self._t("appts.prescribe"))
        self._btn_payment.setText(self._t("appts.payment"))
        self._btn_del_appt.setText(self._t("appts.remove"))
        self._appt_model.setHorizontalHeaderLabels([
            self._t("appts.th.id"), self._t("appts.th.patient"), self._t("appts.th.doctor"),
            self._t("appts.th.date"), self._t("appts.th.time"),
            self._t("appts.th.reason"), self._t("appts.th.status"),
        ])

        self._lbl_meds_title.setText(self._t("meds.title"))
        self._btn_add_med.setText(self._t("meds.add"))
        self._btn_edit_med.setText(self._t("meds.edit"))
        self._btn_del_med.setText(self._t("meds.delete"))
        self._med_search_inp.setPlaceholderText(self._t("meds.search"))
        self._med_model.set_language(self._lang)

        self._lbl_stats_title.setText(self._t("stats.title"))
        self._card_total.set_title(self._t("stats.total_patients"))
        self._card_avg_age.set_title(self._t("stats.avg_age"))
        self._card_appts.set_title(self._t("stats.appointments"))
        self._card_male.set_title(self._t("stats.male"))
        self._card_female.set_title(self._t("stats.female"))
        if hasattr(self, "_grp_blood"):
            self._grp_blood.setTitle(self._t("stats.blood_dist"))
        if hasattr(self, "_grp_appt_status"):
            self._grp_appt_status.setTitle(self._t("stats.appt_status"))

        self._lbl_reports_title.setText(self._t("reports.title"))
        self._btn_reprint_bill.setText(self._t("reports.reprint"))
        self._lbl_journey_list.setText(self._t("reports.patient_list"))
        self._lbl_journey_profile.setText(self._t("reports.profile"))
        self._journey_search_inp.setPlaceholderText(self._t("reports.search_patient"))

        self._lbl_lab_title.setText(self._t("lab.title"))
        self.btn_add_lab.setText(self._t("lab.add"))
        self._lab_search_inp.setPlaceholderText(self._t("lab.search"))
        self.btn_update_lab.setText(self._t("lab.update"))
        self.btn_delete_lab.setText(self._t("lab.delete"))
        self._labs_model.set_language(self._lang)
        self._populate_lab_status_filter()

        if hasattr(self, "_btn_chpw"):
            self._btn_chpw.setText(self._t("btn.change_password"))
        self._btn_logout.setText(self._t("btn.logout"))
        self._btn_lang.setText(lang_label(self._lang))

        n = self._model.rowCount()
        self._row_count_lbl.setText(self._t("patients.showing", n=n))

        idx = self._tabs.currentIndex()
        if idx == 1:
            self._load_appointments()
        elif idx == 2:
            self._load_medications()
        elif idx == 3:
            self._refresh_stats()
        elif idx == 4:
            self._load_admin_reports()
        elif idx == 5:
            self._load_lab_tests()
        elif idx == 7:
            self._load_examined_dashboard()

    def _populate_lab_status_filter(self) -> None:
        cur = self._lab_status_filter.currentData()
        self._lab_status_filter.blockSignals(True)
        self._lab_status_filter.clear()
        for code, key in [
            ("", "lab.status.all"),
            ("Pending", "lab.status.pending"),
            ("Processing", "lab.status.processing"),
            ("Completed", "lab.status.completed"),
        ]:
            self._lab_status_filter.addItem(self._t(key), code)
        if cur is not None:
            for i in range(self._lab_status_filter.count()):
                if self._lab_status_filter.itemData(i) == cur:
                    self._lab_status_filter.setCurrentIndex(i)
                    break
        self._lab_status_filter.blockSignals(False)

    # ─────────────────────────── layout ────────────────────────────────── #
    def _build_ui(self) -> None:
        root = QWidget(); self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setSpacing(0); root_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        # Main area (stacked via QTabWidget hidden tabs)
        self._tabs = QTabWidget()
        self._tabs.tabBar().setVisible(False)
        self._tabs.setContentsMargins(0, 0, 0, 0)

        self._tabs.addTab(self._build_patients_tab(),     "patients")
        self._tabs.addTab(self._build_appointments_tab(), "appointments")
        self._tabs.addTab(self._build_medications_tab(),  "medications")
        self._tabs.addTab(self._build_stats_tab(),        "stats")
        self._tabs.addTab(self._build_admin_tab(),        "admin")
        self._tabs.addTab(self._build_labs_tab(),         "labs")
        self._tabs.addTab(self._build_payment_dashboard_tab(), "payment_dashboard")
        self._tabs.addTab(self._build_examined_dashboard_tab(), "examined")

        root_layout.addWidget(self._tabs, stretch=1)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)

    def _build_sidebar(self) -> QWidget:
        self._sb = QWidget()
        self._sb.setFixedWidth(220)
        self._sb.setStyleSheet(f"background: {PALETTE['bg']}; border-right: 1px solid {PALETTE['border']};")
        vl = QVBoxLayout(self._sb)
        vl.setContentsMargins(10, 20, 10, 20)
        vl.setSpacing(8)

        # Header area with Toggle Button
        hdr = QHBoxLayout()
        hdr.setContentsMargins(10, 0, 10, 0)
        
        self.btn_toggle = QPushButton()
        self.btn_toggle.setIcon(qta.icon('fa5s.bars', color=PALETTE['text']))
        self.btn_toggle.setIconSize(QSize(20, 20))
        self.btn_toggle.setFixedSize(36, 36)
        self.btn_toggle.setObjectName("btn_ghost")
        self.btn_toggle.clicked.connect(self._toggle_sidebar)
        
        appname = QLabel(" PMS")
        appname.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {PALETTE['text']}; letter-spacing: 1px;")
        
        hdr.addWidget(self.btn_toggle)
        hdr.addWidget(appname)
        hdr.addStretch()
        self._appname_lbl = appname
        
        vl.addLayout(hdr)
        vl.addSpacing(20)

        self._btn_patients = SidebarBtn("fa5s.user-injured", "Patients")
        self._btn_appts    = SidebarBtn("fa5s.calendar-alt", "Appointments")
        self._btn_meds     = SidebarBtn("fa5s.pills", "Medications")
        self._btn_labs     = SidebarBtn("fa5s.vials", "Laboratory")
        self._btn_stats    = SidebarBtn("fa5s.chart-pie", "Statistics")
        self._btn_examined = SidebarBtn("fa5s.clipboard-check", "Examined")
        self._sidebar_i18n = [
            (self._btn_patients, "nav.patients"),
            (self._btn_appts, "nav.appointments"),
            (self._btn_meds, "nav.medications"),
            (self._btn_labs, "nav.laboratory"),
            (self._btn_stats, "nav.statistics"),
            (self._btn_examined, "nav.examined"),
        ]
        self._btn_patients.setChecked(True)
        self._btn_patients.setIcon(self._btn_patients.icon_active)

        for btn, idx in [(self._btn_patients, 0), (self._btn_appts, 1), (self._btn_meds, 2),
                         (self._btn_labs, 5), (self._btn_stats, 3), (self._btn_examined, 7)]:
            vl.addWidget(btn)
            btn.clicked.connect(lambda checked, i=idx, b=btn: self._switch_tab(i, b))

        # Reports button (accessible to all doctors/users)
        self._btn_admin = SidebarBtn("fa5s.archive", "Reports & Journey")
        self._sidebar_i18n.append((self._btn_admin, "nav.reports"))
        self._btn_admin.clicked.connect(lambda checked, i=4, b=self._btn_admin: self._switch_tab(i, b))
        vl.addWidget(self._btn_admin)

        # Admin-only: Doctor Accounts button
        if self._doctor and self._doctor.role == "Admin":
            vl.addSpacing(16)
            btn_doctors = SidebarBtn("fa5s.user-md", "Doctor Accounts")
            btn_doctors.clicked.connect(self._open_doctor_manager)
            vl.addWidget(btn_doctors)

        vl.addStretch()

        # ── Doctor info card ─────────────────────────────────────────── #
        if self._doctor:
            info_card = QFrame()
            info_card.setStyleSheet(f"""
                QFrame {{
                    background: {PALETTE['surface']};
                    border: 1px solid {PALETTE['border']};
                    border-radius: 6px;
                }}
            """)
            ic_layout = QVBoxLayout(info_card)
            ic_layout.setContentsMargins(12, 12, 12, 12)
            
            name_lbl = QLabel(f"{self._doctor.full_name}")
            name_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {PALETTE['text']};")
            name_lbl.setWordWrap(True)
            ic_layout.addWidget(name_lbl)
            
            self._btn_chpw = QPushButton("Change Password")
            self._btn_chpw.setIcon(qta.icon('fa5s.key', color=PALETTE['text_dim']))
            self._btn_chpw.setObjectName("btn_ghost")
            self._btn_chpw.setStyleSheet("text-align: left; padding: 4px; color: #858585;")
            self._btn_chpw.clicked.connect(self._change_password)
            ic_layout.addWidget(self._btn_chpw)

            vl.addWidget(info_card)
            self._info_card = info_card

        # Logout button
        self._btn_logout = QPushButton(" Logout")
        self._btn_logout.setIcon(qta.icon('fa5s.sign-out-alt', color=PALETTE['danger']))
        self._btn_logout.setObjectName("btn_ghost")
        self._btn_logout.setStyleSheet(f"color: {PALETTE['danger']}; text-align: left;")
        self._btn_logout.clicked.connect(self._logout)
        vl.addWidget(self._btn_logout)

        # Language toggle (below logout)
        self._btn_lang = QPushButton()
        self._btn_lang.setObjectName("btn_ghost")
        self._btn_lang.setStyleSheet(f"color: {PALETTE['accent2']}; text-align: left; padding: 6px;")
        self._btn_lang.clicked.connect(self._toggle_language)
        vl.addWidget(self._btn_lang)

        return self._sb

    def _toggle_sidebar(self) -> None:
        is_expanded = self._sb.width() > 100
        target = 64 if is_expanded else 220
        
        self.anim = QPropertyAnimation(self._sb, b"minimumWidth")
        self.anim.setDuration(250)
        self.anim.setStartValue(self._sb.width())
        self.anim.setEndValue(target)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.anim2 = QPropertyAnimation(self._sb, b"maximumWidth")
        self.anim2.setDuration(250)
        self.anim2.setStartValue(self._sb.width())
        self.anim2.setEndValue(target)
        self.anim2.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.anim.start()
        self.anim2.start()
        
        # Hide text elements when collapsed
        show_text = not is_expanded
        self._appname_lbl.setVisible(show_text)
        if hasattr(self, '_info_card'):
            self._info_card.setVisible(show_text)
        
        for btn in self._sb.findChildren(QPushButton):
            if isinstance(btn, SidebarBtn) or btn == self.btn_toggle:
                pass # keep visible
            elif btn in (getattr(self, "_btn_logout", None), getattr(self, "_btn_lang", None)):
                if not show_text:
                    btn.setText("")
                elif btn is self._btn_logout:
                    btn.setText(self._t("btn.logout"))
                elif btn is self._btn_lang:
                    btn.setText(lang_label(self._lang))

    def _switch_tab(self, idx: int, active_btn: SidebarBtn) -> None:
        btns = [self._btn_patients, self._btn_appts, self._btn_meds, self._btn_stats]
        if hasattr(self, '_btn_admin'):
            btns.append(self._btn_admin)
        if hasattr(self, '_btn_labs'):
            btns.append(self._btn_labs)
        if hasattr(self, '_btn_examined'):
            btns.append(self._btn_examined)

        for btn in btns:
            btn.setChecked(btn is active_btn)
            btn.setIcon(btn.icon_active if btn.isChecked() else btn.icon_inactive)

        self._tabs.setCurrentIndex(idx)
        if idx == 2: self._load_medications()
        if idx == 3: self._refresh_stats()
        if idx == 1: self._load_appointments()
        if idx == 4: self._load_admin_reports()
        if idx == 5: self._load_lab_tests()
        if idx == 6: self._refresh_payment_dashboard()
        if idx == 7: self._load_examined_dashboard()
    # ──────────────────── PATIENTS TAB ─────────────────────────────────── #
    def _build_patients_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {PALETTE['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(20, 20, 20, 20); vl.setSpacing(12)

        # Header row
        header = QHBoxLayout()
        self._lbl_patients_title = QLabel("Patient Records")
        self._lbl_patients_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {PALETTE['text']};")
        header.addWidget(self._lbl_patients_title)
        header.addStretch()

        self._btn_add    = QPushButton(" Add Patient"); self._btn_add.setIcon(qta.icon("fa5s.plus", color="white"));  self._btn_add.setObjectName("btn_primary")
        self._btn_edit   = QPushButton(" Edit"); self._btn_edit.setIcon(qta.icon("fa5s.pen", color=PALETTE["accent2"]));         self._btn_edit.setObjectName("btn_accent2")
        self._btn_qr     = QPushButton(" QR Card"); self._btn_qr.setIcon(qta.icon("fa5s.qrcode", color=PALETTE["accent2"])); self._btn_qr.setObjectName("btn_accent2")
        self._btn_delete = QPushButton(" Delete"); self._btn_delete.setIcon(qta.icon("fa5s.trash", color=PALETTE["danger"]));       self._btn_delete.setObjectName("btn_danger")
        
        self._btn_edit.setEnabled(False)
        self._btn_qr.setEnabled(False)
        self._btn_delete.setEnabled(False)

        for btn in (self._btn_add, self._btn_edit, self._btn_qr, self._btn_delete):
            btn.setFixedHeight(36); header.addWidget(btn)
        vl.addLayout(header)

        # Search bar
        search_row = QHBoxLayout()
        self._search_inp = QLineEdit()
        self._search_inp.setPlaceholderText("Search by name, phone, or email…")
        self._search_inp.setFixedHeight(36)
        self._search_inp.textChanged.connect(self._on_search)
        
        btn_clr = QPushButton("✕")
        btn_clr.setFixedSize(36, 36)
        btn_clr.setToolTip("Clear search")
        btn_clr.clicked.connect(lambda: self._search_inp.clear())
        
        self._btn_scan_qr = QPushButton(" Scan QR")
        self._btn_scan_qr.setIcon(qta.icon("fa5s.camera", color="white"))
        self._btn_scan_qr.setObjectName("btn_primary")
        self._btn_scan_qr.setFixedHeight(36)
        self._btn_scan_qr.clicked.connect(self._on_scan_patient_qr)

        search_row.addWidget(self._search_inp)
        search_row.addWidget(btn_clr)
        search_row.addWidget(self._btn_scan_qr)
        vl.addLayout(search_row)

        # Table
        self._model = PatientTableModel(lang=self._lang)
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setDefaultSectionSize(36)

        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Fixed); self._table.setColumnWidth(0, 50)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        for col in (2, 3, 4, 5, 7):
            hh.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.Interactive); self._table.setColumnWidth(6, 180)

        self._table.selectionModel().selectionChanged.connect(self._on_selection)
        self._table.doubleClicked.connect(self._on_edit)
        vl.addWidget(self._table)

        # Row count label
        self._row_count_lbl = QLabel()
        self._row_count_lbl.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 12px;")
        vl.addWidget(self._row_count_lbl)

        # Signals
        self._btn_add.clicked.connect(self._on_add)
        self._btn_edit.clicked.connect(self._on_edit)
        self._btn_qr.clicked.connect(self._on_show_patient_qr_card)
        self._btn_delete.clicked.connect(self._on_delete)
        return w

    # ──────────────────── APPOINTMENTS TAB ─────────────────────────────── #
    def _build_appointments_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {PALETTE['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(20, 20, 20, 20); vl.setSpacing(12)

        header = QHBoxLayout()
        self._lbl_appts_title = QLabel("Appointments")
        self._lbl_appts_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {PALETTE['text']};")
        header.addWidget(self._lbl_appts_title); header.addStretch()
        self._btn_add_appt_hdr = QPushButton("➕  Schedule")
        self._btn_add_appt_hdr.setObjectName("btn_primary"); self._btn_add_appt_hdr.setFixedHeight(36)
        self._btn_add_appt_hdr.clicked.connect(self._on_add_appt)
        
        self._btn_queue = QPushButton("🎫  Get Ticket")
        self._btn_queue.setObjectName("btn_accent2"); self._btn_queue.setFixedHeight(36)
        self._btn_queue.setEnabled(False)
        self._btn_queue.clicked.connect(self._on_take_queue_number)
        
        self._btn_prescribe = QPushButton("📝  Prescription & Bill")
        self._btn_prescribe.setObjectName("btn_accent2"); self._btn_prescribe.setFixedHeight(36)
        self._btn_prescribe.setEnabled(False)
        self._btn_prescribe.clicked.connect(self._on_prescribe)
        self._btn_payment = QPushButton("💳  Payment")
        self._btn_payment.setObjectName("btn_accent2"); self._btn_payment.setFixedHeight(36)
        self._btn_payment.setEnabled(False)
        self._btn_payment.clicked.connect(self._on_payment)
        self._btn_del_appt = QPushButton("🗑  Remove")
        self._btn_del_appt.setObjectName("btn_danger"); self._btn_del_appt.setFixedHeight(36)
        self._btn_del_appt.setEnabled(False)
        self._btn_del_appt.clicked.connect(self._on_del_appt)
        header.addWidget(self._btn_add_appt_hdr); header.addWidget(self._btn_queue)
        header.addWidget(self._btn_prescribe)
        header.addWidget(self._btn_payment); header.addWidget(self._btn_del_appt)
        vl.addLayout(header)

        # Appointments table
        self._appt_table = QTableView()
        from PySide6.QtGui import QStandardItemModel, QStandardItem
        self._appt_model = QStandardItemModel()
        self._appt_model.setHorizontalHeaderLabels(
            ["ID", "Patient", "Doctor", "Date", "Time", "Reason", "Status"])
        self._appt_table.setModel(self._appt_model)
        self._appt_table.setAlternatingRowColors(True)
        self._appt_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._appt_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._appt_table.verticalHeader().setVisible(False)
        self._appt_table.setShowGrid(False)
        self._appt_table.verticalHeader().setDefaultSectionSize(36)
        hh2 = self._appt_table.horizontalHeader()
        hh2.setSectionResizeMode(0, QHeaderView.Fixed); self._appt_table.setColumnWidth(0, 44)
        hh2.setSectionResizeMode(1, QHeaderView.Stretch)
        hh2.setSectionResizeMode(5, QHeaderView.Stretch)
        self._appt_table.selectionModel().selectionChanged.connect(self._on_appt_selection)
        self._appt_table.doubleClicked.connect(self._on_edit_appt)
        vl.addWidget(self._appt_table)
        return w

    # ──────────────────── STATISTICS TAB ───────────────────────────────── #
    def _build_stats_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {PALETTE['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(20, 20, 20, 20); vl.setSpacing(16)

        self._lbl_stats_title = QLabel("Statistics & Overview")
        self._lbl_stats_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {PALETTE['text']};")
        vl.addWidget(self._lbl_stats_title)

        # Stat cards
        cards_row = QHBoxLayout(); cards_row.setSpacing(14)
        self._card_total   = StatCard("Total Patients",  "0", "👥", PALETTE["accent"])
        self._card_avg_age = StatCard("Average Age",     "0", "🎂", PALETTE["accent2"])
        self._card_appts   = StatCard("Appointments",    "0", "📅", PALETTE["warning"])
        self._card_male    = StatCard("Male Patients",   "0", "♂",  "#4cc9f0")
        self._card_female  = StatCard("Female Patients", "0", "♀",  "#ff8fab")
        for card in (self._card_total, self._card_avg_age, self._card_appts,
                     self._card_male, self._card_female):
            cards_row.addWidget(card)
        vl.addLayout(cards_row)

        # Blood type distribution
        self._grp_blood = QGroupBox("Blood Type Distribution")
        grp = self._grp_blood
        grp.setStyleSheet(f"""
            QGroupBox {{
                background: {PALETTE['surface']};
                border: 1px solid {PALETTE['border']};
                border-radius: 10px;
                margin-top: 14px; padding-top: 10px;
                font-weight: 700;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 14px; top: -7px;
                color: {PALETTE['accent']};
                background: {PALETTE['surface']};
                padding: 0 8px; font-size: 12px;
            }}
        """)
        grp_layout = QVBoxLayout(grp)
        self._blood_container = QHBoxLayout()
        self._blood_container.setSpacing(10)
        grp_layout.addLayout(self._blood_container)
        vl.addWidget(grp)

        # Appointment status
        self._grp_appt_status = QGroupBox("Appointment Status")
        grp2 = self._grp_appt_status
        grp2.setStyleSheet(grp.styleSheet())
        grp2_layout = QVBoxLayout(grp2)
        self._appt_status_container = QHBoxLayout()
        self._appt_status_container.setSpacing(10)
        grp2_layout.addLayout(self._appt_status_container)
        vl.addWidget(grp2)

        vl.addStretch()
        return w

    def _build_admin_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {PALETTE['bg']};")
        main_lay = QVBoxLayout(w)
        main_lay.setContentsMargins(24, 24, 24, 24)
        main_lay.setSpacing(20)

        # Header Title Area
        hdr_lay = QHBoxLayout()
        self._lbl_reports_title = QLabel("📊  REPORTS & CLINICAL JOURNEY")
        self._lbl_reports_title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {PALETTE['accent']}; letter-spacing: 0.5px;")
        hdr_lay.addWidget(self._lbl_reports_title)
        hdr_lay.addStretch()
        main_lay.addLayout(hdr_lay)

        # Sub-tab widget for 2 dashboards
        self._admin_tabs = QTabWidget()
        self._admin_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {PALETTE['border']};
                border-radius: 12px;
                background: {PALETTE['surface']};
                padding: 16px;
            }}
            QTabBar::tab {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 6px;
                font-weight: bold;
                color: {PALETTE['text_dim']};
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                background: {PALETTE['surface']};
                color: {PALETTE['accent2']};
                border-bottom: 2px solid {PALETTE['accent2']};
            }}
            QTabBar::tab:hover:!selected {{
                background: {PALETTE['row_hover']};
                color: {PALETTE['text']};
            }}
        """)

        # Add Tab 1: Billing & Financials Dashboard
        self._admin_tabs.addTab(self._build_billing_subtab(), "💳  Billing & Financials Dashboard")
        # Add Tab 2: Clinical Journey Dashboard
        self._admin_tabs.addTab(self._build_journey_subtab(), "🩺  Patient Clinical Journey")

        main_lay.addWidget(self._admin_tabs)
        return w

    def _build_billing_subtab(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(16)

        # 1. Financial KPI Cards Row
        cards_lay = QHBoxLayout()
        cards_lay.setSpacing(14)
        self._card_total_rev = StatCard("TOTAL REVENUE", "0 VNĐ", "💰", PALETTE["accent"])
        self._card_total_bills = StatCard("TOTAL PAID BILLS", "0", "📄", PALETTE["accent2"])
        self._card_cash_rev = StatCard("CASH REVENUE", "0 VNĐ", "💵", PALETTE["warning"])
        self._card_bank_rev = StatCard("BANK TRANSFER", "0 VNĐ", "🏦", "#4cc9f0")
        
        cards_lay.addWidget(self._card_total_rev)
        cards_lay.addWidget(self._card_total_bills)
        cards_lay.addWidget(self._card_cash_rev)
        cards_lay.addWidget(self._card_bank_rev)
        vl.addLayout(cards_lay)

        # 2. Search & Filters Row
        filter_lay = QHBoxLayout()
        filter_lay.setSpacing(10)
        
        self._bill_search_inp = QLineEdit()
        self._bill_search_inp.setPlaceholderText("Search by patient name...")
        self._bill_search_inp.setFixedHeight(36)
        self._bill_search_inp.textChanged.connect(self._load_bills)
        filter_lay.addWidget(self._bill_search_inp, stretch=3)
        
        self._bill_method_combo = QComboBox()
        self._bill_method_combo.addItems(["All Payment Methods", "Cash", "Bank Transfer"])
        self._bill_method_combo.setFixedHeight(36)
        self._bill_method_combo.currentIndexChanged.connect(self._load_bills)
        filter_lay.addWidget(self._bill_method_combo, stretch=1)
        
        self._bill_status_combo = QComboBox()
        self._bill_status_combo.addItems(["All Payment Statuses", "Paid", "Pending"])
        self._bill_status_combo.setFixedHeight(36)
        self._bill_status_combo.currentIndexChanged.connect(self._load_bills)
        filter_lay.addWidget(self._bill_status_combo, stretch=1)
        
        btn_clear = QPushButton("Reset Filters")
        btn_clear.setFixedHeight(36)
        btn_clear.clicked.connect(self._on_reset_bill_filters)
        filter_lay.addWidget(btn_clear)
        
        vl.addLayout(filter_lay)

        # 3. Bills Table
        self._bills_table = QTableView()
        self._bills_table.setStyleSheet("border: none; background: transparent;")
        from PySide6.QtGui import QStandardItemModel
        self._bills_model = QStandardItemModel()
        self._bills_model.setHorizontalHeaderLabels(["Bill ID", "Patient Name", "Amount", "Method", "Status", "Date", "Appt ID"])
        self._bills_table.setModel(self._bills_model)
        self._bills_table.setAlternatingRowColors(True)
        self._bills_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._bills_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._bills_table.verticalHeader().setVisible(False)
        self._bills_table.setShowGrid(False)
        self._bills_table.verticalHeader().setDefaultSectionSize(36)
        
        hh = self._bills_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Fixed); self._bills_table.setColumnWidth(0, 75)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.Stretch)
        hh.setSectionResizeMode(6, QHeaderView.Fixed); self._bills_table.setColumnWidth(6, 65)
        
        self._bills_table.selectionModel().selectionChanged.connect(self._on_bill_selection)
        vl.addWidget(self._bills_table)

        # 4. Reprint toolbar
        left_tools = QHBoxLayout()
        self._btn_reprint_bill = QPushButton("🖨️  Reprint Receipt / Bill")
        self._btn_reprint_bill.setObjectName("btn_accent2"); self._btn_reprint_bill.setFixedHeight(36)
        self._btn_reprint_bill.setMinimumWidth(180)
        self._btn_reprint_bill.setEnabled(False)
        self._btn_reprint_bill.clicked.connect(self._on_reprint_bill)
        left_tools.addWidget(self._btn_reprint_bill)
        left_tools.addStretch()
        vl.addLayout(left_tools)

        return w

    def _build_journey_subtab(self) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(16)

        # Main Split Content Area
        split_lay = QHBoxLayout()
        split_lay.setSpacing(16)

        # Column 1: Patient Search & List Sidebar
        self._journey_sidebar = QFrame()
        self._journey_sidebar.setFixedWidth(260)
        self._journey_sidebar.setStyleSheet(f"""
            QFrame {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['border']};
                border-radius: 10px;
            }}
            QLineEdit {{
                background: {PALETTE['surface']};
                border: 1px solid {PALETTE['border']};
                border-radius: 6px;
                color: #ffffff;
                padding: 8px 12px;
                font-size: 12px;
                border: 1px solid {PALETTE['border']};
            }}
            QLineEdit:focus {{
                border-color: {PALETTE['accent2']};
            }}
            QListWidget {{
                background: transparent;
                border: none;
                color: {PALETTE['text']};
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-radius: 6px;
                border-bottom: 1px solid {PALETTE['border']};
                color: {PALETTE['text']};
            }}
            QListWidget::item:hover {{
                background: {PALETTE['row_hover']};
            }}
            QListWidget::item:selected {{
                background: {PALETTE['accent2']};
                color: #ffffff;
                font-weight: bold;
            }}
        """)
        sidebar_lay = QVBoxLayout(self._journey_sidebar)
        sidebar_lay.setContentsMargins(12, 12, 12, 12)
        sidebar_lay.setSpacing(10)

        self._lbl_journey_list = QLabel("👥 DANH SÁCH BỆNH NHÂN")
        self._lbl_journey_list.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {PALETTE['accent']}; border: none;")
        sidebar_lay.addWidget(self._lbl_journey_list)

        self._journey_search_inp = QLineEdit()
        self._journey_search_inp.setPlaceholderText("🔍 Tìm tên bệnh nhân...")
        sidebar_lay.addWidget(self._journey_search_inp)

        from PySide6.QtWidgets import QListWidget
        self._journey_p_list = QListWidget()
        self._journey_p_list.itemSelectionChanged.connect(self._on_patient_journey_selected)
        sidebar_lay.addWidget(self._journey_p_list)

        split_lay.addWidget(self._journey_sidebar)

        # Column 2: Patient clinical profile card
        self._journey_profile_card = QFrame()
        self._journey_profile_card.setFixedWidth(260)
        self._journey_profile_card.setStyleSheet(f"""
            QFrame {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['border']};
                border-radius: 10px;
            }}
        """)
        prof_lay = QVBoxLayout(self._journey_profile_card)
        prof_lay.setContentsMargins(16, 16, 16, 16)
        prof_lay.setSpacing(12)

        self._lbl_journey_profile = QLabel("👤 HỒ SƠ BỆNH NHÂN")
        self._lbl_journey_profile.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {PALETTE['accent']}; border: none;")
        prof_lay.addWidget(self._lbl_journey_profile)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet(f"background-color: {PALETTE['border']}; max-height: 1px; border: none;")
        prof_lay.addWidget(divider)

        # Patient Info details as labels
        self._lbl_prof_name = QLabel("Họ tên: --")
        self._lbl_prof_dob = QLabel("Ngày sinh: --")
        self._lbl_prof_gender = QLabel("Giới tính: --")
        self._lbl_prof_phone = QLabel("Số điện thoại: --")
        self._lbl_prof_blood = QLabel("Nhóm máu: --")
        self._lbl_prof_allergies = QLabel("Dị ứng: --")
        
        for lbl in (self._lbl_prof_name, self._lbl_prof_dob, self._lbl_prof_gender, 
                     self._lbl_prof_phone, self._lbl_prof_blood, self._lbl_prof_allergies):
            lbl.setWordWrap(True)
            lbl.setStyleSheet("border: none; font-size: 12px; color: #cccccc;")
            prof_lay.addWidget(lbl)
            
        prof_lay.addStretch()
        split_lay.addWidget(self._journey_profile_card)

        # Column 3: Text Browser for Visual Timeline representation
        self._journey_timeline = QTextBrowser()
        self._journey_timeline.setStyleSheet(f"""
            QTextBrowser {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['border']};
                border-radius: 10px;
                padding: 18px;
                color: {PALETTE['text']};
                font-family: 'Segoe UI', Arial;
            }}
        """)
        self._journey_timeline.setOpenExternalLinks(False)
        split_lay.addWidget(self._journey_timeline, stretch=1)

        vl.addLayout(split_lay)
        return w

    def _on_reset_bill_filters(self) -> None:
        self._bill_search_inp.clear()
        self._bill_method_combo.setCurrentIndex(0)
        self._bill_status_combo.setCurrentIndex(0)

    def _load_admin_reports(self) -> None:
        self._load_bills()
        self._load_journey_patients()

    def _load_bills(self) -> None:
        # 1. Update overall financial KPI cards
        all_payments = self._db._conn.execute(
            "SELECT amount, method, status FROM payments"
        ).fetchall()
        
        total_rev = 0.0
        paid_count = 0
        cash_rev = 0.0
        bank_rev = 0.0
        
        for r in all_payments:
            amt, method, status = r
            if status == "Paid":
                total_rev += amt
                paid_count += 1
                if method == "Cash":
                    cash_rev += amt
                elif method == "Bank Transfer":
                    bank_rev += amt
                    
        self._card_total_rev.update_value(f"{total_rev:,.0f} VNĐ")
        self._card_total_bills.update_value(f"{paid_count} / {len(all_payments)}")
        self._card_cash_rev.update_value(f"{cash_rev:,.0f} VNĐ")
        self._card_bank_rev.update_value(f"{bank_rev:,.0f} VNĐ")

        # 2. Build filtered SQL query for bills table
        query = """
            SELECT p.id, pt.full_name, p.amount, p.method, p.status, p.paid_at, a.id
            FROM payments p
            JOIN appointments a ON a.id = p.appointment_id
            JOIN patients pt ON pt.id = a.patient_id
            WHERE 1=1
        """
        params = []
        
        # Apply patient name search filter
        if hasattr(self, "_bill_search_inp"):
            search_text = self._bill_search_inp.text().strip()
            if search_text:
                query += " AND pt.full_name LIKE ?"
                params.append(f"%{search_text}%")
            
        # Apply method filter
        if hasattr(self, "_bill_method_combo"):
            method_idx = self._bill_method_combo.currentIndex()
            if method_idx == 1:
                query += " AND p.method = 'Cash'"
            elif method_idx == 2:
                query += " AND p.method = 'Bank Transfer'"
            
        # Apply status filter
        if hasattr(self, "_bill_status_combo"):
            status_idx = self._bill_status_combo.currentIndex()
            if status_idx == 1:
                query += " AND p.status = 'Paid'"
            elif status_idx == 2:
                query += " AND p.status = 'Pending'"
            
        query += " ORDER BY p.paid_at DESC, p.id DESC"
        
        self._bills_model.removeRows(0, self._bills_model.rowCount())
        rows = self._db._conn.execute(query, params).fetchall()
        
        from PySide6.QtGui import QStandardItem
        for r in rows:
            amt_str = f"{r[2]:,.0f} VNĐ"
            paid_date = r[5] or "N/A"
            items = [
                QStandardItem(f"#{r[0]:05d}"),
                QStandardItem(r[1]),
                QStandardItem(amt_str),
                QStandardItem(r[3]),
                QStandardItem(r[4]),
                QStandardItem(paid_date),
                QStandardItem(str(r[6]))
            ]
            self._bills_model.appendRow(items)
            
        self._btn_reprint_bill.setEnabled(False)

    def _load_journey_patients(self) -> None:
        # Keep currently selected patient if any
        curr_id = None
        sel_items = self._journey_p_list.selectedItems()
        if sel_items:
            curr_id = sel_items[0].data(Qt.UserRole)
            
        self._journey_p_list.blockSignals(True)
        self._journey_p_list.clear()
        
        patients = self._db.get_all_patients()
        search_text = self._journey_search_inp.text().strip().lower()
        
        restore_idx = -1
        idx = 0
        from PySide6.QtWidgets import QListWidgetItem
        
        for p in patients:
            disp_text = f"{p.full_name} (ID: #{p.id:05d})"
            if search_text and (search_text not in p.full_name.lower() and search_text not in f"#{p.id:05d}"):
                continue
                
            item = QListWidgetItem(disp_text)
            item.setData(Qt.UserRole, p.id)
            self._journey_p_list.addItem(item)
            
            if curr_id == p.id:
                restore_idx = idx
            idx += 1
            
        # Try to restore selection or select the first item
        if restore_idx != -1:
            self._journey_p_list.setCurrentRow(restore_idx)
        elif self._journey_p_list.count() > 0:
            self._journey_p_list.setCurrentRow(0)
            
        self._journey_p_list.blockSignals(False)
        self._on_patient_journey_selected()

    def _on_bill_selection(self) -> None:
        has_sel = bool(self._bills_table.selectedIndexes())
        self._btn_reprint_bill.setEnabled(has_sel)

    def _on_reprint_bill(self) -> None:
        idx = self._bills_table.currentIndex()
        if not idx.isValid(): return
        appt_id = int(self._bills_model.item(idx.row(), 6).text())
        
        # Switch to Appointments tab and select the appt, then trigger payment
        self._switch_tab(1, self._btn_appts)
        for r in range(self._appt_model.rowCount()):
            item = self._appt_model.item(r, 0)
            if item and item.text().strip() == str(appt_id):
                self._appt_table.selectRow(r)
                self._on_appt_selection()
                self._on_payment()
                break

    def _on_patient_journey_selected(self) -> None:
        sel_items = self._journey_p_list.selectedItems()
        if not sel_items:
            self._journey_timeline.setHtml("<div style='color:#888888; font-style:italic;'>Chọn một bệnh nhân từ danh sách phía bên trái để xem lộ trình khám lịch sử chi tiết.</div>")
            self._lbl_prof_name.setText("Họ tên: --")
            self._lbl_prof_dob.setText("Ngày sinh: --")
            self._lbl_prof_gender.setText("Giới tính: --")
            self._lbl_prof_phone.setText("Số điện thoại: --")
            self._lbl_prof_blood.setText("Nhóm máu: --")
            self._lbl_prof_allergies.setText("Dị ứng: --")
            return
            
        pid = sel_items[0].data(Qt.UserRole)
        patient = self._db.get_patient_by_id(pid)
        if not patient:
            return
            
        # Update left profile card details
        self._lbl_prof_name.setText(f"<b>Họ tên:</b> {patient.full_name}")
        self._lbl_prof_dob.setText(f"<b>Ngày sinh:</b> {patient.display_dob} ({patient.age} tuổi)")
        self._lbl_prof_gender.setText(f"<b>Giới tính:</b> {patient.gender}")
        self._lbl_prof_phone.setText(f"<b>Số điện thoại:</b> {patient.phone}")
        self._lbl_prof_blood.setText(f"<b>Nhóm máu:</b> <span style='color: {PALETTE['warning']}; font-weight: bold;'>{patient.blood_type or 'Chưa xác định'}</span>")
        self._lbl_prof_allergies.setText(f"<b>Dị ứng:</b> <span style='color: {PALETTE['danger']}; font-weight: bold;'>{patient.allergies or 'Không'}</span>")
        
        # Fetch all appointments for this patient
        appt_rows = self._db._conn.execute(
            """SELECT id, doctor, appointment_date, appointment_time, reason, status
               FROM appointments WHERE patient_id=?
               ORDER BY appointment_date DESC, appointment_time DESC""",
            (pid,)
        ).fetchall()
        
        html = f"""
        <div style="font-family: 'Segoe UI', Arial; color: #e0e0e0;">
            <h2 style="color: #007acc; margin-bottom: 2px;">LỘ TRÌNH KHÁM BỆNH NHÂN</h2>
            <h4 style="color: #888888; margin-top: 0; margin-bottom: 20px;">Bệnh nhân: <b>{patient.full_name.upper()}</b> (Mã BN: #{patient.id:05d})</h4>
        """
        
        if not appt_rows:
            html += "<div style='color:#888888; font-style:italic; padding: 10px;'>Bệnh nhân chưa có lịch sử khám chữa bệnh nào được đăng ký trong hệ thống.</div>"
        else:
            for row in appt_rows:
                appt_id, doctor, appt_date, appt_time, reason, status = row
                
                # Fetch queue number deterministically
                seq_row = self._db._conn.execute(
                    "SELECT COUNT(*) FROM appointments WHERE appointment_date=? AND id <= ?",
                    (appt_date, appt_id)
                ).fetchone()
                queue_no = seq_row[0] if seq_row else 1
                
                # Fetch medical record
                med_rec = self._db.get_medical_record(appt_id)
                diagnosis_str = "<i>Chưa có chẩn đoán lâm sàng</i>"
                symptoms_str = "<i>Chưa ghi chép triệu chứng</i>"
                if med_rec:
                    if med_rec.diagnosis: diagnosis_str = f"<b>{med_rec.diagnosis}</b>"
                    if med_rec.symptoms: symptoms_str = f"<i>{med_rec.symptoms}</i>"
                    
                # Fetch prescription
                prescription = self._db.get_prescription_by_appointment(appt_id)
                prescription_items_html = ""
                total_cost = 150000.0  # Base cost
                if prescription and prescription.items:
                    prescription_items_html += "<ul style='margin: 4px 0; padding-left: 20px; font-size: 11px;'>"
                    for item in prescription.items:
                        med_name = "Thuốc / Dịch vụ"
                        m_row = self._db._conn.execute("SELECT name FROM medications WHERE id=?", (item.medication_id,)).fetchone()
                        if m_row: med_name = m_row[0]
                        prescription_items_html += f"<li>{med_name} (SL: {item.quantity}) - {item.price_at_time:,.0f} VNĐ</li>"
                        total_cost += item.quantity * item.price_at_time
                    prescription_items_html += "</ul>"
                else:
                    prescription_items_html = "<i>Không kê đơn thuốc hoặc dịch vụ ngoài khám.</i>"
                    
                # Fetch payment status
                payment = self._db.get_payment(appt_id)
                payment_str = f"<span style='color: #d9534f; font-weight: bold;'>Chưa thanh toán (Tạm tính: {total_cost:,.0f} VNĐ)</span>"
                if payment:
                    status_badge = "Đã thanh toán" if payment.status == "Paid" else "Chưa thanh toán"
                    badge_color = "#5cb85c" if payment.status == "Paid" else "#d9534f"
                    payment_str = f"<span style='color: {badge_color}; font-weight: bold;'>{status_badge} ({payment.amount:,.0f} VNĐ - {payment.method})</span>"
                
                html += f"""
                <div style="border-left: 3px solid #007acc; padding-left: 16px; margin-left: 8px; margin-bottom: 24px; position: relative;">
                    <div style="font-size: 14px; font-weight: bold; color: #007acc; margin-bottom: 4px;">
                        📌 LƯỢT KHÁM #{appt_id:05d} - Số thứ tự: [ {queue_no:02d} ]
                    </div>
                    <div style="font-size: 11px; color: #888888; margin-bottom: 6px;">
                        📅 Ngày khám: {appt_date} lúc {appt_time} | 🩺 Bác sĩ phụ trách: <b>{doctor}</b>
                    </div>
                    <div style="background: {PALETTE['surface']}; border: 1px solid {PALETTE['border']}; border-radius: 6px; padding: 10px; font-size: 12px; line-height: 1.5; color: #cccccc;">
                        <b>1. Lý do khám:</b> {reason or 'Không ghi chú'}<br>
                        <b>2. Triệu chứng lâm sàng:</b> {symptoms_str}<br>
                        <b>3. Chẩn đoán điều trị:</b> {diagnosis_str}<br>
                        <b>4. Đơn thuốc & Dịch vụ:</b> {prescription_items_html}<br>
                        <b>5. Trạng thái hóa đơn:</b> {payment_str}
                    </div>
                </div>
                """
                
        html += "</div>"
        self._journey_timeline.setHtml(html)

    # ──────────────────── DATA LOADING ─────────────────────────────────── #
    def _load_patients(self) -> None:
        q = self._search_inp.text().strip() if hasattr(self, "_search_inp") else ""
        if q:
            patients = self._db.search_patients(q)
        else:
            patients = self._db.get_all_patients()
        self._model.refresh(patients)
        n = len(patients)
        self._row_count_lbl.setText(self._t("patients.showing", n=n))
        self._status.showMessage(self._t("patients.loaded", n=n))

    def _load_appointments(self) -> None:
        from PySide6.QtGui import QStandardItem, QColor as QC
        self._appt_model.removeRows(0, self._appt_model.rowCount())
        rows = self._db.get_appointments()
        status_colors = {
            "Scheduled": PALETTE["accent2"],
            "Completed": PALETTE["accent"],
            "Cancelled": PALETTE["danger"],
        }
        for row in rows:
            items = []
            for val in row:
                item = QStandardItem(str(val))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                items.append(item)
            # colour status cell
            status = row[6]
            items[6].setForeground(QC(status_colors.get(status, PALETTE["text"])))
            self._appt_model.appendRow(items)

    def _refresh_stats(self) -> None:
        stats = self._db.get_statistics()
        self._card_total.update_value(str(stats["total"]))
        self._card_avg_age.update_value(str(stats["avg_age"]))
        total_appts = sum(stats["appt_status"].values())
        self._card_appts.update_value(str(total_appts))
        self._card_male.update_value(str(stats["gender"].get("Male", 0)))
        self._card_female.update_value(str(stats["gender"].get("Female", 0)))
        self._refresh_blood_bars(stats["blood_type"])
        self._refresh_appt_status(stats["appt_status"])

    def _refresh_blood_bars(self, blood_data: dict) -> None:
        # Clear
        while self._blood_container.count():
            item = self._blood_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not blood_data:
            self._blood_container.addWidget(
                QLabel(self._t("stats.no_data")))
            return

        max_val = max(blood_data.values(), default=1)
        colors  = ["#ef476f","#ffd166","#06d6a0","#118ab2",
                   "#073b4c","#4cc9f0","#f77f00","#4361ee"]
        for i, (bt, cnt) in enumerate(sorted(blood_data.items())):
            col_widget = QWidget()
            col_layout = QVBoxLayout(col_widget)
            col_layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
            col_layout.setSpacing(4)

            bar_h = max(10, int((cnt / max_val) * 120))
            bar = QFrame()
            bar.setFixedSize(44, bar_h)
            c = colors[i % len(colors)]
            bar.setStyleSheet(f"background: {c}; border-radius: 4px 4px 0 0;")
            col_layout.addStretch()
            col_layout.addWidget(bar, alignment=Qt.AlignHCenter)

            cnt_lbl = QLabel(str(cnt))
            cnt_lbl.setAlignment(Qt.AlignCenter)
            cnt_lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {c};")
            col_layout.addWidget(cnt_lbl)

            bt_lbl = QLabel(bt)
            bt_lbl.setAlignment(Qt.AlignCenter)
            bt_lbl.setStyleSheet(f"font-size: 12px; color: {PALETTE['text_dim']};")
            col_layout.addWidget(bt_lbl)

            self._blood_container.addWidget(col_widget)
        self._blood_container.addStretch()

    def _refresh_appt_status(self, appt_data: dict) -> None:
        while self._appt_status_container.count():
            item = self._appt_status_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        status_colors = {
            "Scheduled": PALETTE["accent2"],
            "Completed": PALETTE["accent"],
            "Cancelled": PALETTE["danger"],
        }
        total = sum(appt_data.values()) or 1
        for status, cnt in appt_data.items():
            c = status_colors.get(status, PALETTE["text"])
            pct = int((cnt / total) * 100)

            chip = QFrame()
            chip.setStyleSheet(f"""
                QFrame {{
                    background: {PALETTE['surface2']};
                    border: 1px solid {c};
                    border-radius: 8px;
                    padding: 8px;
                }}
            """)
            cl = QVBoxLayout(chip); cl.setSpacing(2)
            v = QLabel(str(cnt))
            v.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {c};")
            v.setAlignment(Qt.AlignCenter)
            s = QLabel(status)
            s.setStyleSheet(f"font-size: 12px; color: {PALETTE['text_dim']};")
            s.setAlignment(Qt.AlignCenter)
            p = QLabel(f"{pct}%")
            p.setStyleSheet(f"font-size: 11px; color: {c};")
            p.setAlignment(Qt.AlignCenter)
            for lbl in (v, s, p):
                cl.addWidget(lbl)
            chip.setFixedWidth(120)
            self._appt_status_container.addWidget(chip)
        self._appt_status_container.addStretch()

    # ──────────────────── SLOTS ─────────────────────────────────────────── #
    def _on_selection(self) -> None:
        has_sel = bool(self._table.selectedIndexes())
        self._btn_edit.setEnabled(has_sel)
        self._btn_qr.setEnabled(has_sel)
        self._btn_delete.setEnabled(has_sel)
        if has_sel:
            row = self._table.currentIndex().row()
            self._selected_patient = self._model.patient_at(row)

    def _on_search(self, text: str) -> None:
        self._load_patients()

    def _on_add(self) -> None:
        dlg = PatientDialog(self)
        dlg.setStyleSheet(GLOBAL_QSS)
        if dlg.exec() == QDialog.Accepted:
            patient = dlg.get_patient()
            pid = self._db.add_patient(patient)
            self._status.showMessage(f"✅  Patient added (ID {pid})")
            self._load_patients()
            
            # Capture photo prompt
            reply = QMessageBox.question(
                self, "Chụp ảnh bệnh nhân", 
                "Bệnh nhân đã được đăng ký thành công.\nBạn có muốn chụp ảnh bệnh nhân ngay bây giờ không?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._capture_patient_photo(pid, patient.full_name)

    def _capture_patient_photo(self, pid: int, name: str):
        class CapturePhotoDialog(QDialog):
            def __init__(self, patient_id, patient_name, parent=None):
                super().__init__(parent)
                self.patient_id = patient_id
                self.patient_name = patient_name
                self.setWindowTitle(f"Chụp ảnh - {patient_name}")
                self.setFixedSize(520, 480)
                self.setStyleSheet(GLOBAL_QSS)
                
                layout = QVBoxLayout(self)
                
                self.lbl = QLabel("Đang mở camera...")
                self.lbl.setAlignment(Qt.AlignCenter)
                self.lbl.setFixedSize(480, 360)
                self.lbl.setStyleSheet(f"background: {PALETTE['surface2']}; border: 1px solid {PALETTE['border']};")
                layout.addWidget(self.lbl)
                
                btn_capture = QPushButton("📸 Chụp & Lưu ảnh")
                btn_capture.setObjectName("btn_primary")
                btn_capture.setFixedHeight(40)
                btn_capture.clicked.connect(self._capture)
                layout.addWidget(btn_capture)
                
                import cv2
                self.cap = cv2.VideoCapture(0)
                
                from PySide6.QtCore import QTimer
                self.timer = QTimer(self)
                self.timer.timeout.connect(self._update_frame)
                self.timer.start(30)
                
                self.current_frame = None

            def _update_frame(self):
                ret, frame = self.cap.read()
                if ret:
                    import cv2
                    self.current_frame = frame
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame_rgb.shape
                    from PySide6.QtGui import QImage, QPixmap
                    img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
                    self.lbl.setPixmap(QPixmap.fromImage(img).scaled(480, 360, Qt.KeepAspectRatio))
                    
            def _capture(self):
                if self.current_frame is not None:
                    import os
                    import cv2
                    photo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patients_faces")
                    os.makedirs(photo_dir, exist_ok=True)
                    path = os.path.join(photo_dir, f"{self.patient_id}.jpg")
                    cv2.imwrite(path, self.current_frame)
                    QMessageBox.information(self, "Thành công", f"Đã lưu ảnh bệnh nhân vào:\n{path}")
                self.accept()
                
            def closeEvent(self, event):
                self.cap.release()
                self.timer.stop()
                super().closeEvent(event)
                
            def reject(self):
                self.cap.release()
                self.timer.stop()
                super().reject()
                
            def accept(self):
                self.cap.release()
                self.timer.stop()
                super().accept()
                
        dlg = CapturePhotoDialog(pid, name, self)
        dlg.exec()

    def _on_edit(self) -> None:
        if not self._selected_patient:
            return
        dlg = PatientDialog(self, patient=self._selected_patient)
        dlg.setStyleSheet(GLOBAL_QSS)
        if dlg.exec() == QDialog.Accepted:
            updated = dlg.get_patient()
            self._db.update_patient(updated)
            self._status.showMessage(f"✅  Patient '{updated.full_name}' updated")
            self._load_patients()

    def _on_show_patient_qr_card(self) -> None:
        if not self._selected_patient:
            return
        from ui_cccd import PatientQRDialog
        p = self._selected_patient
        dlg = PatientQRDialog(
            patient_id=p.id,
            name=p.full_name,
            dob=p.dob,
            gender=p.gender,
            phone=p.phone,
            parent=self
        )
        dlg.exec()

    def _on_scan_patient_qr(self) -> None:
        from ui_cccd import QRScanDialog
        dlg = QRScanDialog(self)
        dlg.scanned_patient_id.connect(self._on_patient_qr_identified)
        dlg.exec()

    def _on_patient_qr_identified(self, pid: int) -> None:
        # 1. Fetch patient details
        patient = self._db.get_patient_by_id(pid)
        if not patient:
            QMessageBox.warning(self, "Not Found", f"Patient ID #{pid} was identified via QR, but could not be found in database.")
            return

        # 2. Fetch latest appointment
        row = self._db._conn.execute(
            "SELECT id, doctor, appointment_date, appointment_time, reason, status "
            "FROM appointments WHERE patient_id=? "
            "ORDER BY appointment_date DESC, appointment_time DESC LIMIT 1",
            (pid,)
        ).fetchone()

        appt_info = None
        med_rec = None
        cost_info = {"amount": 150000.0, "status": "Chưa thanh toán", "method": ""}
        
        if row:
            appt_id, doctor, appt_date, appt_time, reason, status = row
            appt_info = {
                "id": appt_id,
                "doctor": doctor,
                "date": appt_date,
                "time": appt_time,
                "reason": reason,
                "status": status
            }
            # Fetch medical record
            med_rec_obj = self._db.get_medical_record(appt_id)
            if med_rec_obj:
                med_rec = {
                    "symptoms": med_rec_obj.symptoms,
                    "diagnosis": med_rec_obj.diagnosis,
                }
            # Fetch prescription cost
            prescription = self._db.get_prescription_by_appointment(appt_id)
            total_cost = 150000.0  # Base examination fee
            if prescription:
                for item in prescription.items:
                    total_cost += item.quantity * item.price_at_time

            # Fetch payment status
            payment_obj = self._db.get_payment(appt_id)
            if payment_obj:
                cost_info["amount"] = payment_obj.amount
                cost_info["status"] = "Đã thanh toán" if payment_obj.status == "Paid" else "Chưa thanh toán"
                cost_info["method"] = payment_obj.method
            else:
                cost_info["amount"] = total_cost
                cost_info["status"] = "Chưa thanh toán"

        patient_diagnosis = patient.active_diagnosis or patient.display_notes
        if not med_rec and patient_diagnosis:
            med_rec = {
                "symptoms": "",
                "diagnosis": patient_diagnosis,
            }
        elif med_rec and not med_rec.get("diagnosis") and patient_diagnosis:
            med_rec["diagnosis"] = patient_diagnosis

        # 3. Show Gorgeous Scanned Summary Dialog
        from ui_cccd import PatientScannedSummaryDialog
        dlg = PatientScannedSummaryDialog(patient, appt_info, med_rec, cost_info, self, lang=self._lang)
        res = dlg.exec()
        
        # 4. Select the patient in the main list
        row_found = -1
        for r in range(self._model.rowCount()):
            p = self._model.patient_at(r)
            if p and p.id == pid:
                row_found = r
                break
        
        if row_found == -1:
            self._search_inp.setText("")
            self._load_patients()
            for r in range(self._model.rowCount()):
                p = self._model.patient_at(r)
                if p and p.id == pid:
                    row_found = r
                    break
                    
        if row_found != -1:
            self._table.selectRow(row_found)
            self._table.scrollTo(self._model.index(row_found, 0))
            self._on_selection()
            self._status.showMessage(f"🎯 Patient identified via QR: {patient.full_name}")

        # 5. Handle action triggers from summary dialog
        if res == 100 and appt_info:  # Action to open payment directly!
            self._switch_tab(1, self._btn_appts)  # Switch to Appointments tab
            # Find the appointment row in the appt table
            for r in range(self._appt_model.rowCount()):
                item = self._appt_model.item(r, 0)
                if item and item.text().strip() == str(appt_info["id"]):
                    self._appt_table.selectRow(r)
                    self._on_appt_selection()
                    self._on_payment()
                    break

    def _on_delete(self) -> None:
        if not self._selected_patient:
            return
        p = self._selected_patient
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete patient <b>{p.full_name}</b>?<br>"
            "This will also remove all related appointments.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._db.delete_patient(p.id)
            self._selected_patient = None
            self._btn_edit.setEnabled(False)
            self._btn_qr.setEnabled(False)
            self._btn_delete.setEnabled(False)
            self._status.showMessage(f"🗑  Patient deleted")
            self._load_patients()

    def _on_add_appt(self) -> None:
        patients = self._db.get_patient_names()
        doctors = self._db.get_all_doctors()
        dlg = AppointmentDialog(self, patient_list=patients, doctor_list=doctors)
        dlg.setStyleSheet(GLOBAL_QSS)
        if dlg.exec() == QDialog.Accepted:
            appt = dlg.get_appointment()
            self._db.add_appointment(appt)
            self._status.showMessage("✅  Appointment scheduled")
            self._load_appointments()

    def _on_edit_appt(self) -> None:
        idx = self._appt_table.currentIndex()
        if not idx.isValid(): return
        appt_id = int(self._appt_model.item(idx.row(), 0).text())
        
        cursor = self._db._conn.execute("SELECT * FROM appointments WHERE id=?", (appt_id,))
        raw_appt = cursor.fetchone()
        if not raw_appt: return
        from patient import Appointment
        appt = Appointment.from_row(tuple(raw_appt))
        
        plist = [(p.id, p.full_name) for p in self._db.get_all_patients()]
        doctors = self._db.get_all_doctors()
        dlg = AppointmentDialog(self, patient_list=plist, doctor_list=doctors, appt=appt)
        if dlg.exec() == QDialog.Accepted:
            updated = dlg.get_appointment()
            self._db.update_appointment(updated)
            self._status.showMessage("✅ Appointment updated")
            self._load_appointments()

    def _on_del_appt(self) -> None:
        idx = self._appt_table.currentIndex()
        if not idx.isValid():
            return
        appt_id = int(self._appt_model.item(idx.row(), 0).text())
        reply = QMessageBox.question(
            self, "Confirm", "Remove this appointment?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._db.delete_appointment(appt_id)
            self._load_appointments()
            self._status.showMessage("🗑  Appointment removed")


    def _on_appt_selection(self) -> None:
        has_sel = bool(self._appt_table.selectedIndexes())
        if hasattr(self, '_btn_edit_appt'): self._btn_edit_appt.setEnabled(has_sel)
        self._btn_del_appt.setEnabled(has_sel)
        self._btn_prescribe.setEnabled(has_sel)
        self._btn_payment.setEnabled(has_sel)
        self._btn_queue.setEnabled(has_sel)

    def _on_take_queue_number(self) -> None:
        idx = self._appt_table.currentIndex()
        if not idx.isValid(): return
        appt_id = int(self._appt_model.item(idx.row(), 0).text())
        
        # 1. Fetch details of appointment from DB
        row = self._db._conn.execute(
            "SELECT a.appointment_date, a.appointment_time, p.full_name, a.doctor "
            "FROM appointments a "
            "JOIN patients p ON p.id = a.patient_id "
            "WHERE a.id=?",
            (appt_id,)
        ).fetchone()
        
        if not row:
            return
            
        appt_date, appt_time, p_name, doctor = row
        
        # 2. Count appointments on same date up to appt_id to get daily queue number
        seq_row = self._db._conn.execute(
            "SELECT COUNT(*) FROM appointments WHERE appointment_date=? AND id <= ?",
            (appt_date, appt_id)
        ).fetchone()
        
        queue_no = seq_row[0] if seq_row else 1
        
        # 3. Show Queue Ticket
        from ui_cccd import QueueTicketDialog
        dlg = QueueTicketDialog(queue_no, p_name, doctor, appt_date, appt_time, self)
        dlg.exec()

    def _on_prescribe(self) -> None:
        idx = self._appt_table.currentIndex()
        if not idx.isValid(): return
        appt_id = int(self._appt_model.item(idx.row(), 0).text())
        
        # Get patient name from appt list (col 1)
        # Actually need to fetch the patient from DB to be safe
        appt_row = next((r for r in self._db.get_appointments() if r[0] == appt_id), None)
        if not appt_row: return
        
        # We need the full appointment and patient object
        # Since get_appointments returns joined data, let's query raw appointment and patient
        p_name = appt_row[1]
        patients = self._db.get_all_patients()
        patient = next((p for p in patients if p.full_name == p_name), None)
        if not patient: return
        
        # Find raw appointment
        cursor = self._db._conn.execute("SELECT * FROM appointments WHERE id=?", (appt_id,))
        raw_appt = cursor.fetchone()
        appt = Appointment.from_row(tuple(raw_appt))
        
        dlg = PrescriptionDialog(self._db, appt, patient, self)
        dlg.exec()

    def _on_payment(self) -> None:
        idx = self._appt_table.currentIndex()
        if not idx.isValid(): return
        appt_id = int(self._appt_model.item(idx.row(), 0).text())
        
        appt_row = next((r for r in self._db.get_appointments() if r[0] == appt_id), None)
        if not appt_row: return
        
        p_name = appt_row[1]
        patients = self._db.get_all_patients()
        patient = next((p for p in patients if p.full_name == p_name), None)
        if not patient: return
        
        # Find raw appointment
        cursor = self._db._conn.execute("SELECT * FROM appointments WHERE id=?", (appt_id,))
        raw_appt = cursor.fetchone()
        appt = Appointment.from_row(tuple(raw_appt))

        self._open_payment_dashboard(appt, patient)

    # ──────────────────── PAYMENT DASHBOARD ────────────────────────────── #
    def _build_payment_dashboard_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {PALETTE['bg']};")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(20, 20, 20, 20)
        vl.setSpacing(12)

        header = QHBoxLayout()
        self._lbl_payment_dash_title = QLabel("Dashboard thanh toán lấy thuốc")
        self._lbl_payment_dash_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {PALETTE['text']};")
        header.addWidget(self._lbl_payment_dash_title)
        header.addStretch()
        self._btn_payment_dash_back = QPushButton("← Lịch hẹn")
        self._btn_payment_dash_back.setObjectName("btn_accent2")
        self._btn_payment_dash_back.setFixedHeight(36)
        self._btn_payment_dash_back.clicked.connect(lambda: self._switch_tab(1, self._btn_appts))
        self._btn_payment_dash_pay = QPushButton("💳 Thanh toán")
        self._btn_payment_dash_pay.setObjectName("btn_primary")
        self._btn_payment_dash_pay.setFixedHeight(36)
        self._btn_payment_dash_pay.clicked.connect(self._pay_selected_dashboard_row)
        header.addWidget(self._btn_payment_dash_pay)
        header.addWidget(self._btn_payment_dash_back)
        vl.addLayout(header)

        self._payment_dash_model = None
        from PySide6.QtGui import QStandardItemModel
        self._payment_dash_model = QStandardItemModel()
        self._payment_dash_model.setHorizontalHeaderLabels([
            "Mã lịch", "Tên bệnh nhân", "Ngày giờ lấy thuốc",
            "Loại bệnh", "Hình thức thanh toán", "Trạng thái thanh toán",
        ])

        self._payment_dash_table = QTableView()
        self._payment_dash_table.setModel(self._payment_dash_model)
        self._payment_dash_table.setAlternatingRowColors(True)
        self._payment_dash_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._payment_dash_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._payment_dash_table.verticalHeader().setVisible(False)
        self._payment_dash_table.setShowGrid(False)
        self._payment_dash_table.verticalHeader().setDefaultSectionSize(38)
        hh = self._payment_dash_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        vl.addWidget(self._payment_dash_table)

        self._payment_dash_hint = QLabel("Các chỉ định lấy thuốc sẽ tự chuyển Pending → Processing → Completed, rồi tự xóa khỏi dashboard.")
        self._payment_dash_hint.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 12px;")
        vl.addWidget(self._payment_dash_hint)
        return w

    def _payment_diagnosis_for(self, appt: Appointment, patient: Patient) -> str:
        med_rec = self._db.get_medical_record(appt.id)
        return (
            (med_rec.diagnosis if med_rec and med_rec.diagnosis else "")
            or patient.active_diagnosis
            or patient.display_notes
            or appt.reason
            or "Chưa ghi nhận"
        )

    def _payment_dashboard_row(self, appt_id: int) -> int:
        if not self._payment_dash_model:
            return -1
        for row in range(self._payment_dash_model.rowCount()):
            item = self._payment_dash_model.item(row, 0)
            if item and item.text() == str(appt_id):
                return row
        return -1

    def _set_payment_status_item(self, row: int, status: str) -> None:
        item = self._payment_dash_model.item(row, 5)
        if not item:
            return
        item.setText(status.upper())
        colors = {
            "Pending": "#ff9800",
            "Processing": PALETTE["accent2"],
            "Completed": "#2ecc71",
        }
        item.setForeground(QColor(colors.get(status, PALETTE["text"])))

    def _upsert_payment_dashboard_row(self, appt: Appointment, patient: Patient) -> None:
        from PySide6.QtGui import QStandardItem
        row = self._payment_dashboard_row(appt.id)
        pickup_time = QDate.currentDate().toString("dd/MM/yyyy") + " " + QTime.currentTime().toString("HH:mm:ss")
        values = [
            str(appt.id),
            patient.full_name,
            pickup_time,
            self._payment_diagnosis_for(appt, patient),
            "--",
            "PENDING",
        ]
        items = [QStandardItem(v) for v in values]
        for item in items:
            item.setEditable(False)
        if row < 0:
            self._payment_dash_model.appendRow(items)
            row = self._payment_dash_model.rowCount() - 1
        else:
            for col, item in enumerate(items):
                self._payment_dash_model.setItem(row, col, item)
        self._set_payment_status_item(row, "Pending")
        self._payment_dash_table.selectRow(row)
        self._payment_dash_table.scrollTo(self._payment_dash_model.index(row, 0))

    def _open_payment_dashboard(self, appt: Appointment, patient: Patient) -> None:
        self._tabs.setCurrentIndex(6)
        self._upsert_payment_dashboard_row(appt, patient)
        self._refresh_payment_dashboard()

    def _selected_dashboard_appt_id(self) -> Optional[int]:
        if not hasattr(self, "_payment_dash_table"):
            return None
        sel = self._payment_dash_table.selectionModel().selectedRows()
        if sel:
            row = sel[0].row()
        elif self._payment_dash_model and self._payment_dash_model.rowCount() == 1:
            row = 0
        else:
            return None
        item = self._payment_dash_model.item(row, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

    def _pay_selected_dashboard_row(self) -> None:
        appt_id = self._selected_dashboard_appt_id()
        if appt_id is None:
            QMessageBox.warning(self, "Thanh toán", "Vui lòng chọn một dòng trên dashboard thanh toán.")
            return
        appt, patient = self._resolve_appt_patient(appt_id)
        if not appt or not patient:
            QMessageBox.warning(self, "Thanh toán", "Không tìm thấy lịch hẹn hoặc bệnh nhân.")
            return
        self._show_payment_dialog_from_dashboard(appt, patient)

    def _show_payment_dialog_from_dashboard(self, appt: Appointment, patient: Patient) -> None:
        dlg = PaymentDialog(self._db, appt, patient, self)
        if dlg.exec() == QDialog.Accepted:
            payment = self._db.get_payment(appt.id)
            method = payment.method if payment else ("Bank Transfer" if dlg.rad_bank.isChecked() else "Cash")
            self._set_payment_dashboard_processing(appt.id, method)
            self._load_appointments()
            self._load_examined_dashboard()

    def _set_payment_dashboard_processing(self, appt_id: int, method: str) -> None:
        row = self._payment_dashboard_row(appt_id)
        if row < 0:
            return
        self._payment_dash_model.item(row, 4).setText(method)
        self._set_payment_status_item(row, "Processing")
        self._clear_payment_dashboard_timers(appt_id)

        done_timer = QTimer(self)
        done_timer.setSingleShot(True)
        done_timer.timeout.connect(lambda aid=appt_id: self._set_payment_dashboard_completed(aid))
        self._payment_dashboard_timers[appt_id] = [done_timer]
        done_timer.start(5000)

    def _set_payment_dashboard_completed(self, appt_id: int) -> None:
        row = self._payment_dashboard_row(appt_id)
        if row < 0:
            return
        self._set_payment_status_item(row, "Completed")
        remove_timer = QTimer(self)
        remove_timer.setSingleShot(True)
        remove_timer.timeout.connect(lambda aid=appt_id: self._remove_payment_dashboard_row(aid))
        self._payment_dashboard_timers.setdefault(appt_id, []).append(remove_timer)
        remove_timer.start(4000)

    def _remove_payment_dashboard_row(self, appt_id: int) -> None:
        self._clear_payment_dashboard_timers(appt_id)
        row = self._payment_dashboard_row(appt_id)
        if row >= 0:
            self._payment_dash_model.removeRow(row)
        self._status.showMessage("✅ Đã hoàn tất và xóa chỉ định lấy thuốc khỏi dashboard")

    def _clear_payment_dashboard_timers(self, appt_id: int) -> None:
        timers = self._payment_dashboard_timers.pop(appt_id, [])
        for timer in timers:
            timer.stop()
            timer.deleteLater()

    def _refresh_payment_dashboard(self) -> None:
        if hasattr(self, "_payment_dash_table"):
            self._payment_dash_table.viewport().update()

    # ──────────────────── EXAMINED DASHBOARD ───────────────────────────── #
    def _build_examined_dashboard_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {PALETTE['bg']};")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(20, 20, 20, 20)
        vl.setSpacing(12)

        header = QHBoxLayout()
        self._lbl_examined_title = QLabel("Dashboard đã khám")
        self._lbl_examined_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {PALETTE['text']};")
        header.addWidget(self._lbl_examined_title)
        header.addStretch()
        self._btn_examined_refresh = QPushButton("🔄 Làm mới")
        self._btn_examined_refresh.setObjectName("btn_accent2")
        self._btn_examined_refresh.setFixedHeight(36)
        self._btn_examined_refresh.clicked.connect(self._load_examined_dashboard)
        header.addWidget(self._btn_examined_refresh)
        vl.addLayout(header)

        body = QSplitter(Qt.Horizontal)
        self._examined_patient_list = QListWidget()
        self._examined_patient_list.setMinimumWidth(250)
        self._examined_patient_list.setStyleSheet(f"""
            QListWidget {{
                background: {PALETTE['surface']};
                border: 1px solid {PALETTE['border']};
                border-radius: 6px;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {PALETTE['border']};
            }}
            QListWidget::item:selected {{
                background: {PALETTE['row_sel']};
                color: #ffffff;
            }}
        """)
        self._examined_patient_list.currentItemChanged.connect(self._on_examined_patient_selected)

        from PySide6.QtGui import QStandardItemModel
        self._examined_visit_model = QStandardItemModel()
        self._examined_visit_model.setHorizontalHeaderLabels([
            "Mã lịch", "Tên bệnh nhân", "Ngày giờ đã khám",
            "Loại bệnh", "Hình thức thanh toán", "Trạng thái",
        ])

        self._examined_table = QTableView()
        self._examined_table.setModel(self._examined_visit_model)
        self._examined_table.setAlternatingRowColors(True)
        self._examined_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._examined_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._examined_table.verticalHeader().setVisible(False)
        self._examined_table.setShowGrid(False)
        self._examined_table.verticalHeader().setDefaultSectionSize(38)
        hh = self._examined_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        body.addWidget(self._examined_patient_list)
        body.addWidget(self._examined_table)
        body.setStretchFactor(0, 1)
        body.setStretchFactor(1, 3)
        vl.addWidget(body)

        hint = QLabel("Hồ sơ đã thanh toán sẽ rời danh sách chờ khám/lấy thuốc và nằm tại đây để theo dõi lại.")
        hint.setStyleSheet(f"color: {PALETTE['text_dim']}; font-size: 12px;")
        vl.addWidget(hint)
        return w

    def _load_examined_dashboard(self) -> None:
        if not hasattr(self, "_examined_patient_list"):
            return
        current_patient_id = None
        cur = self._examined_patient_list.currentItem()
        if cur:
            current_patient_id = cur.data(Qt.UserRole)

        rows = self._db._conn.execute(
            """SELECT p.id, p.full_name, COUNT(pay.id) AS visit_count,
                      MAX(COALESCE(pay.paid_at, '')) AS last_paid
               FROM payments pay
               JOIN appointments a ON a.id = pay.appointment_id
               JOIN patients p ON p.id = a.patient_id
               WHERE pay.status = 'Paid'
               GROUP BY p.id, p.full_name
               ORDER BY last_paid DESC, p.full_name"""
        ).fetchall()

        self._examined_patient_list.blockSignals(True)
        self._examined_patient_list.clear()
        selected_row = 0
        for i, (patient_id, full_name, visit_count, last_paid) in enumerate(rows):
            item = QListWidgetItem(f"{full_name}\n{visit_count} lần khám")
            item.setData(Qt.UserRole, patient_id)
            self._examined_patient_list.addItem(item)
            if current_patient_id == patient_id:
                selected_row = i
        self._examined_patient_list.blockSignals(False)
        if rows:
            self._examined_patient_list.setCurrentRow(selected_row)
            self._load_examined_visits_for_patient(self._examined_patient_list.currentItem().data(Qt.UserRole))
        else:
            self._examined_visit_model.removeRows(0, self._examined_visit_model.rowCount())

    def _on_examined_patient_selected(self, current: QListWidgetItem, previous: QListWidgetItem = None) -> None:
        if current:
            self._load_examined_visits_for_patient(current.data(Qt.UserRole))

    def _load_examined_visits_for_patient(self, patient_id: int) -> None:
        if not hasattr(self, "_examined_visit_model"):
            return
        from PySide6.QtGui import QStandardItem

        rows = self._db._conn.execute(
            """SELECT a.id, p.full_name, COALESCE(pay.paid_at, ''),
                      COALESCE(mr.diagnosis, ''), p.notes, a.reason,
                      pay.method, pay.status
               FROM payments pay
               JOIN appointments a ON a.id = pay.appointment_id
               JOIN patients p ON p.id = a.patient_id
               LEFT JOIN medical_records mr ON mr.appointment_id = a.id
               WHERE pay.status = 'Paid'
                 AND p.id = ?
               ORDER BY pay.paid_at DESC, a.id DESC"""
            ,
            (patient_id,),
        ).fetchall()

        self._examined_visit_model.removeRows(0, self._examined_visit_model.rowCount())
        for appt_id, patient_name, paid_at, med_diag, patient_notes, reason, method, status in rows:
            patient_diag = ""
            for line in (patient_notes or "").splitlines():
                if line.startswith(("Diagnosis:", "Bệnh lý:", "Chẩn đoán:", "Benh ly:")):
                    patient_diag = line.split(":", 1)[1].strip()
                    break
            diagnosis = med_diag or patient_diag or reason or "Chưa ghi nhận"
            values = [
                str(appt_id),
                patient_name,
                paid_at or "--",
                diagnosis,
                method or "--",
                "ĐÃ KHÁM",
            ]
            items = [QStandardItem(str(v)) for v in values]
            for item in items:
                item.setEditable(False)
            items[5].setForeground(QColor("#2ecc71"))
            self._examined_visit_model.appendRow(items)

    # ──────────────────── MEDICATIONS TAB ─────────────────────────────── #
    def _build_medications_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {PALETTE['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(20, 20, 20, 20); vl.setSpacing(12)

        header = QHBoxLayout()
        self._lbl_meds_title = QLabel("Medications & Services")
        self._lbl_meds_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {PALETTE['text']};")
        header.addWidget(self._lbl_meds_title); header.addStretch()

        self._btn_add_med = QPushButton("➕  Add")
        self._btn_add_med.setObjectName("btn_primary"); self._btn_add_med.setFixedHeight(36)
        self._btn_add_med.clicked.connect(self._on_add_med)
        
        self._btn_edit_med = QPushButton("✏️  Edit")
        self._btn_edit_med.setObjectName("btn_accent2"); self._btn_edit_med.setFixedHeight(36)
        self._btn_edit_med.setEnabled(False)
        self._btn_edit_med.clicked.connect(self._on_edit_med)
        
        self._btn_del_med = QPushButton("🗑  Delete")
        self._btn_del_med.setObjectName("btn_danger"); self._btn_del_med.setFixedHeight(36)
        self._btn_del_med.setEnabled(False)
        self._btn_del_med.clicked.connect(self._on_del_med)

        header.addWidget(self._btn_add_med)
        header.addWidget(self._btn_edit_med)
        header.addWidget(self._btn_del_med)
        vl.addLayout(header)

        # Search bar
        search_row = QHBoxLayout()
        self._med_search_inp = QLineEdit()
        self._med_search_inp.setPlaceholderText("🔍  Search medications...")
        self._med_search_inp.setFixedHeight(36)
        self._med_search_inp.textChanged.connect(self._load_medications)
        btn_clr = QPushButton("✕")
        btn_clr.setFixedSize(36, 36)
        btn_clr.clicked.connect(lambda: self._med_search_inp.clear())
        search_row.addWidget(self._med_search_inp)
        search_row.addWidget(btn_clr)
        vl.addLayout(search_row)

        self._med_model = MedicationTableModel(lang=self._lang)
        self._med_table = QTableView()
        self._med_table.setModel(self._med_model)
        self._med_table.setAlternatingRowColors(True)
        self._med_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._med_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._med_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._med_table.verticalHeader().setVisible(False)
        self._med_table.horizontalHeader().setStretchLastSection(True)
        self._med_table.setShowGrid(False)
        self._med_table.verticalHeader().setDefaultSectionSize(36)
        
        hh = self._med_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Fixed); self._med_table.setColumnWidth(0, 50)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.Fixed); self._med_table.setColumnWidth(2, 120)

        self._med_table.selectionModel().selectionChanged.connect(self._on_med_selection)
        self._med_table.doubleClicked.connect(self._on_edit_med)
        vl.addWidget(self._med_table)

        return w

    def _load_medications(self) -> None:
        q = self._med_search_inp.text().strip() if hasattr(self, "_med_search_inp") else ""
        if q:
            meds = self._db.search_medications(q)
        else:
            meds = self._db.get_all_medications()
        self._med_model.refresh(meds)

    def _on_med_selection(self) -> None:
        has_sel = bool(self._med_table.selectedIndexes())
        self._btn_edit_med.setEnabled(has_sel)
        self._btn_del_med.setEnabled(has_sel)

    def _on_add_med(self) -> None:
        dlg = MedicationDialog(self)
        if dlg.exec() == QDialog.Accepted:
            med = dlg.get_medication()
            self._db.add_medication(med)
            self._status.showMessage("✅ Medication added")
            self._load_medications()

    def _on_edit_med(self) -> None:
        idx = self._med_table.currentIndex()
        if not idx.isValid(): return
        med = self._med_model.med_at(idx.row())
        if not med: return
        dlg = MedicationDialog(self, med)
        if dlg.exec() == QDialog.Accepted:
            updated = dlg.get_medication()
            self._db.update_medication(updated)
            self._status.showMessage(f"✅ Medication '{updated.name}' updated")
            self._load_medications()

    def _on_del_med(self) -> None:
        idx = self._med_table.currentIndex()
        if not idx.isValid(): return
        med = self._med_model.med_at(idx.row())
        if not med: return
        reply = QMessageBox.question(self, "Confirm", f"Delete medication {med.name}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._db.delete_medication(med.id)
            self._status.showMessage("🗑 Medication deleted")
            self._load_medications()

    # ──────────────────── LABORATORY TAB ─────────────────────────────────── #
    def _build_labs_tab(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background: {PALETTE['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(20, 20, 20, 20); vl.setSpacing(12)

        header = QHBoxLayout()
        self._lbl_lab_title = QLabel("Clinical Laboratories")
        self._lbl_lab_title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {PALETTE['text']};")

        self.btn_add_lab = QPushButton("➕ Chỉ định Xét nghiệm (New)")
        self.btn_add_lab.setObjectName("btn_primary")
        self.btn_add_lab.setFixedHeight(36)
        self.btn_add_lab.clicked.connect(self._on_create_lab_test)

        header.addWidget(self._lbl_lab_title)
        header.addStretch()
        header.addWidget(self.btn_add_lab)
        vl.addLayout(header)

        div = QFrame(); div.setObjectName("divider"); div.setFixedHeight(1)
        div.setStyleSheet(f"background: {PALETTE['border']};")
        vl.addWidget(div)

        filter_lay = QHBoxLayout()
        filter_lay.setSpacing(10)

        self._lab_search_inp = QLineEdit()
        self._lab_search_inp.setPlaceholderText("Tìm kiếm theo tên bệnh nhân, bác sĩ hoặc tên xét nghiệm...")
        self._lab_search_inp.setFixedHeight(36)
        self._lab_search_inp.setStyleSheet(f"background: {PALETTE['surface2']}; color: #ffffff; padding: 6px; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        self._lab_search_inp.textChanged.connect(self._load_lab_tests)

        self._lab_status_filter = QComboBox()
        self._lab_status_filter.setFixedHeight(36)
        self._lab_status_filter.setStyleSheet(f"background: {PALETTE['surface2']}; color: #ffffff; padding: 6px; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        self._lab_status_filter.currentIndexChanged.connect(self._load_lab_tests)

        filter_lay.addWidget(self._lab_search_inp, stretch=3)
        filter_lay.addWidget(self._lab_status_filter, stretch=1)
        vl.addLayout(filter_lay)

        self._labs_table = QTableView()
        self._labs_table.setStyleSheet("border: none; background: transparent;")
        self._labs_model = LabTestTableModel(lang=self._lang)
        self._labs_table.setModel(self._labs_model)
        self._labs_table.setAlternatingRowColors(True)
        self._labs_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._labs_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._labs_table.verticalHeader().setVisible(False)
        self._labs_table.setShowGrid(False)
        self._labs_table.verticalHeader().setDefaultSectionSize(36)

        self._labs_table.doubleClicked.connect(self._on_update_lab_test)
        self._labs_table.selectionModel().selectionChanged.connect(self._on_lab_selection)

        hh = self._labs_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Fixed); self._labs_table.setColumnWidth(0, 85)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.Stretch)

        vl.addWidget(self._labs_table)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.btn_update_lab = QPushButton("✏️ Cập nhật & Tải lên Kết quả")
        self.btn_update_lab.setObjectName("btn_accent"); self.btn_update_lab.setFixedHeight(36)
        self.btn_update_lab.clicked.connect(self._on_update_lab_test)

        self.btn_delete_lab = QPushButton("🗑 Xóa chỉ định")
        self.btn_delete_lab.setStyleSheet(f"background: {PALETTE['warning']}; color: #ffffff; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_delete_lab.setFixedHeight(36)
        self.btn_delete_lab.clicked.connect(self._on_delete_lab_test)

        toolbar.addWidget(self.btn_update_lab)
        toolbar.addWidget(self.btn_delete_lab)
        toolbar.addStretch()
        vl.addLayout(toolbar)

        return w

    def _on_lab_selection(self) -> None:
        return

    def _resolve_appt_patient(self, appt_id: int) -> tuple[Optional[Appointment], Optional[Patient]]:
        row = self._db._conn.execute(
            "SELECT a.id, a.patient_id, a.doctor, a.appointment_date, a.appointment_time, a.reason, a.status "
            "FROM appointments a WHERE a.id=?",
            (appt_id,),
        ).fetchone()
        if not row:
            return None, None
        appt = Appointment.from_row(tuple(row))
        patient = self._db.get_patient_by_id(appt.patient_id)
        return appt, patient

    def _on_lab_payment(self) -> None:
        sel = self._labs_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, self._t("msg.error"), self._t("lab.err.select_payment"))
            return
        test_row = self._labs_model.row_at(sel[0].row())
        if not test_row:
            return
        test_id = test_row[0]
        appt_id = test_row[8]
        status = test_row[5]
        if status == "Processing":
            QMessageBox.information(self, self._t("msg.confirm"), self._t("lab.payment_done"))
            return
        labs = self._db.get_lab_tests_by_appointment(appt_id)
        lab_test = next((t for t in labs if t.id == test_id), None)
        if not lab_test:
            QMessageBox.warning(self, self._t("msg.error"), self._t("lab.err.no_orders"))
            return
        appt, patient = self._resolve_appt_patient(appt_id)
        if not appt or not patient:
            QMessageBox.warning(self, self._t("msg.error"), self._t("lab.err.select_appt"))
            return
            
        # If the appointment already has a prescription, force combined payment
        prescription = self._db.get_prescription_by_appointment(appt_id)
        if prescription and prescription.items:
            QMessageBox.warning(self, "Thông báo", "Lịch hẹn này đã có đơn thuốc. Vui lòng thanh toán gộp tại phần Lịch hẹn để xuất chung 1 hóa đơn.")
            return
            
        dlg = PaymentDialog(self._db, appt, patient, self, lab_only=True, lab_test=lab_test)
        if dlg.exec() == QDialog.Accepted:
            self._db.set_lab_test_status(test_id, "Processing")
            self._load_lab_tests()
            self._status.showMessage(self._t("lab.payment_done"))
            self._schedule_lab_test_completion(test_id)

    def _cancel_lab_timer(self, test_id: int) -> None:
        old = self._lab_completion_timers.pop(test_id, None)
        if old is not None:
            old.stop()
            old.deleteLater()

    def _get_lab_test_by_id(self, test_id: int) -> Optional[LabTest]:
        return next((t for t in self._db.get_all_lab_tests() if t.id == test_id), None)

    def _schedule_lab_test_completion(self, test_id: int) -> None:
        self._cancel_lab_timer(test_id)
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda tid=test_id: self._mark_lab_test_completed(tid))
        self._lab_completion_timers[test_id] = timer
        timer.start(5000)

    def _resume_processing_lab_tests(self, rows: list[tuple]) -> None:
        for row in rows:
            test_id = row[0]
            status = row[5]
            if status == "Processing" and test_id not in self._lab_completion_timers:
                self._schedule_lab_test_completion(test_id)

    def _mark_lab_test_completed(self, test_id: int) -> None:
        self._cancel_lab_timer(test_id)
        lab_test = self._get_lab_test_by_id(test_id)
        if not lab_test:
            self._load_lab_tests()
            return
        lab_test.status = "Completed"
        self._db.update_lab_test(lab_test)
        self._load_lab_tests()
        self._status.showMessage(self._t("lab.status_completed"))

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda tid=test_id: self._remove_lab_test(tid))
        self._lab_completion_timers[test_id] = timer
        timer.start(5000)

    def _remove_lab_test(self, test_id: int) -> None:
        self._cancel_lab_timer(test_id)
        if self._get_lab_test_by_id(test_id):
            self._db.delete_lab_test(test_id)
        self._load_lab_tests()
        self._status.showMessage(self._t("lab.processing_done"))

    def _load_lab_tests(self) -> None:
        rows = self._db.get_lab_tests_with_details()
        self._resume_processing_lab_tests(rows)
        search_query = self._lab_search_inp.text().strip().lower()
        status_filter = self._lab_status_filter.currentData()

        filtered = []
        for r in rows:
            p_name = r[1].lower()
            doc_name = r[2].lower()
            test_name = r[3].lower()
            status = r[5]

            if status_filter and status != status_filter:
                continue
            if search_query and not (search_query in p_name or search_query in doc_name or search_query in test_name):
                continue
            filtered.append(r)

        self._labs_model.refresh(filtered)

    def _on_create_lab_test(self) -> None:
        dlg = CreateLabTestDialog(self._db, self)
        if dlg.exec() == QDialog.Accepted:
            self._load_lab_tests()

    def _on_update_lab_test(self) -> None:
        sel = self._labs_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, self._t("msg.error"), self._t("lab.err.select_update"))
            return
        row_idx = sel[0].row()
        test_row = self._labs_model.row_at(row_idx)
        if not test_row: return

        dlg = UpdateLabTestDialog(self._db, test_row, self)
        if dlg.exec() == QDialog.Accepted:
            self._load_lab_tests()

    def _on_delete_lab_test(self) -> None:
        sel = self._labs_table.selectionModel().selectedRows()
        if not sel:
            QMessageBox.warning(self, self._t("msg.error"), self._t("lab.err.select_delete"))
            return
        row_idx = sel[0].row()
        test_row = self._labs_model.row_at(row_idx)
        if not test_row: return

        test_id = test_row[0]
        test_name = test_row[3]

        reply = QMessageBox.question(
            self,
            self._t("lab.confirm_delete_title"),
            self._t("lab.confirm_delete", name=test_name),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._db.delete_lab_test(test_id)
            self._load_lab_tests()

    def closeEvent(self, event) -> None:
        self._db.close()
        event.accept()

    def _logout(self) -> None:
        reply = QMessageBox.question(
            self, self._t("msg.logout_title"),
            self._t("msg.logout_body"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._db.close()
            # Re-launch login
            import subprocess, sys
            subprocess.Popen([sys.executable] + sys.argv)
            import PySide6.QtWidgets as _qw
            _qw.QApplication.quit()

    def _change_password(self) -> None:
        if not self._doctor:
            return
        from ui_login import ChangePasswordDialog
        dlg = ChangePasswordDialog(self._db, self._doctor, self)
        dlg.exec()

    def _open_doctor_manager(self) -> None:
        from ui_login import DoctorManagerDialog
        dlg = DoctorManagerDialog(self._db, self._doctor, self)
        dlg.exec()


# ══════════════════════════════════════════════════════════════════════════════
#  MEDICATIONS MODEL & DIALOG
# ══════════════════════════════════════════════════════════════════════════════
MED_HEADER_KEYS = ["meds.th.id", "meds.th.name", "meds.th.price", "meds.th.desc"]


class MedicationTableModel(QAbstractTableModel):
    def __init__(self, meds: list[Medication] = None, lang: str | None = None):
        super().__init__()
        self._data = meds or []
        self._lang = lang or get_language()
        self._headers = [tr(k, self._lang) for k in MED_HEADER_KEYS]

    def set_language(self, lang: str) -> None:
        self._lang = lang
        self._headers = [tr(k, lang) for k in MED_HEADER_KEYS]
        self.headerDataChanged.emit(Qt.Horizontal, 0, len(self._headers) - 1)

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid(): return None
        m = self._data[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return str(m.id)
            if col == 1: return m.name
            if col == 2: return f"{m.price:,.0f}"
            if col == 3: return m.description
        if role == Qt.TextAlignmentRole:
            if col in (0, 2): return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        if role == Qt.ForegroundRole and col == 2:
            return QColor(PALETTE["accent"])
        return None

    def med_at(self, row: int) -> Optional[Medication]:
        if 0 <= row < len(self._data): return self._data[row]
        return None

    def refresh(self, meds: list[Medication]) -> None:
        self.beginResetModel()
        self._data = meds
        self.endResetModel()


class MedicationDialog(QDialog):
    def __init__(self, parent=None, med: Optional[Medication] = None):
        super().__init__(parent)
        self._med = med
        self.setWindowTitle("Edit Medication" if med else "Add Medication")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"background: {PALETTE['surface']}; border-radius: 12px;")
        self._build_ui()
        if med:
            self._populate(med)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        ttl = QLabel(f"{'✏️' if self._med else '➕'}  {'Edit' if self._med else 'Add'} Medication")
        ttl.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {PALETTE['accent']};")
        layout.addWidget(ttl)

        form = QFormLayout()
        form.setSpacing(12)
        lbl_style = f"color: {PALETTE['text_dim']}; font-weight: 600; font-size: 12px;"
        def lbl(text):
            l = QLabel(text); l.setStyleSheet(lbl_style); return l

        self.inp_name = QLineEdit()
        self.inp_price = QLineEdit()
        from PySide6.QtGui import QDoubleValidator
        self.inp_price.setValidator(QDoubleValidator(0.0, 999999999.0, 2, self))
        self.inp_desc = QTextEdit()
        self.inp_desc.setFixedHeight(60)

        form.addRow(lbl("Name *"), self.inp_name)
        form.addRow(lbl("Price *"), self.inp_price)
        form.addRow(lbl("Description"), self.inp_desc)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("💾 Save")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

    def _populate(self, m: Medication) -> None:
        self.inp_name.setText(m.name)
        self.inp_price.setText(str(m.price))
        self.inp_desc.setPlainText(m.description)

    def _on_save(self) -> None:
        if not self.inp_name.text().strip() or not self.inp_price.text().strip():
            QMessageBox.warning(self, "Validation", "Name and Price are required.")
            return
        self.accept()

    def get_medication(self) -> Medication:
        try: p = float(self.inp_price.text())
        except: p = 0.0
        return Medication(
            id=self._med.id if self._med else None,
            name=self.inp_name.text().strip(),
            price=p,
            description=self.inp_desc.toPlainText().strip()
        )


# ══════════════════════════════════════════════════════════════════════════════
#  PRESCRIPTION / BILL DIALOG & EXPORT
# ══════════════════════════════════════════════════════════════════════════════
class PrescriptionDialog(QDialog):
    def __init__(self, db: Database, appt: Appointment, patient: Patient, parent=None):
        super().__init__(parent)
        self._db = db
        self._appt = appt
        self._patient = patient
        self._lang = getattr(parent, "_lang", get_language()) if parent else get_language()
        self._prescription = self._db.get_prescription_by_appointment(appt.id)
        if not self._prescription:
            self._prescription = Prescription(appointment_id=appt.id)
        
        self.setWindowTitle("Prescription & Bill")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(f"background: {PALETTE['surface']};")
        self._build_ui()
        self._load_data()

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Info
        info_layout = QGridLayout()
        lbl_s = f"color: {PALETTE['text_dim']}; font-weight: 600; font-size: 12px;"
        val_s = f"color: {PALETTE['text']}; font-weight: 700; font-size: 13px;"
        
        def add_info(row, col, label, value):
            l = QLabel(label); l.setStyleSheet(lbl_s)
            v = QLabel(value); v.setStyleSheet(val_s)
            info_layout.addWidget(l, row, col*2)
            info_layout.addWidget(v, row, col*2+1)

        add_info(0, 0, "Patient:", self._patient.full_name)
        add_info(0, 1, "Doctor:", self._appt.doctor)
        add_info(1, 0, "Date:", self._appt.appointment_date)
        add_info(1, 1, "Reason:", self._appt.reason)
        layout.addLayout(info_layout)
        
        div = QFrame(); div.setFixedHeight(1); div.setStyleSheet(f"background: {PALETTE['border']}; margin: 10px 0;")
        layout.addWidget(div)

        # Medication selection
        sel_layout = QHBoxLayout()
        self.cmb_meds = QComboBox()
        self.all_meds = self._db.get_all_medications()
        for m in self.all_meds:
            self.cmb_meds.addItem(f"{m.name} - {m.price:,.0f}", userData=m.id)
        
        self.inp_qty = QLineEdit("1")
        self.inp_qty.setFixedWidth(50)
        btn_add = QPushButton("➕ Add")
        btn_add.clicked.connect(self._add_item)
        btn_ai = QPushButton(self._t("rx.ai_suggest"))
        btn_ai.setObjectName("btn_accent2")
        btn_ai.clicked.connect(self._suggest_items)
        
        sel_layout.addWidget(QLabel("Item:"))
        sel_layout.addWidget(self.cmb_meds, stretch=1)
        sel_layout.addWidget(QLabel("Qty:"))
        sel_layout.addWidget(self.inp_qty)
        sel_layout.addWidget(btn_add)
        sel_layout.addWidget(btn_ai)
        layout.addLayout(sel_layout)

        # Items Table
        self.table = QTableView()
        from PySide6.QtGui import QStandardItemModel, QStandardItem
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["ID", "Name", "Qty", "Unit Price", "Total Price"])
        self.table.setModel(self.model)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        btn_del_item = QPushButton("🗑 Remove item")
        btn_del_item.clicked.connect(self._remove_item)
        layout.addWidget(btn_del_item, alignment=Qt.AlignRight)

        # Total Label
        self.lbl_total = QLabel("Total: 0 đ")
        self.lbl_total.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {PALETTE['accent']}; margin: 10px 0;")
        self.lbl_total.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lbl_total)

        # Actions
        btn_layout = QHBoxLayout()
        btn_export_png = QPushButton("🖼 Export PNG")
        btn_export_png.clicked.connect(self._export_png)
        btn_export_pdf = QPushButton("📄 Export PDF")
        btn_export_pdf.clicked.connect(self._export_pdf)
        
        btn_save = QPushButton("💾 Save Bill")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._save_bill)
        
        btn_layout.addWidget(btn_export_png)
        btn_layout.addWidget(btn_export_pdf)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def _load_data(self) -> None:
        from PySide6.QtGui import QStandardItem
        self.model.removeRows(0, self.model.rowCount())
        total = 0.0
        for item in self._prescription.items:
            m_name = "Unknown"
            for m in self.all_meds:
                if m.id == item.medication_id:
                    m_name = m.name
                    break
            
            line_total = item.quantity * item.price_at_time
            total += line_total
            
            row = [
                QStandardItem(str(item.medication_id)),
                QStandardItem(m_name),
                QStandardItem(str(item.quantity)),
                QStandardItem(f"{item.price_at_time:,.0f}"),
                QStandardItem(f"{line_total:,.0f}")
            ]
            self.model.appendRow(row)
        self.lbl_total.setText(f"Total: {total:,.0f} đ")

    def _add_item(self) -> None:
        med_id = self.cmb_meds.currentData()
        try:
            qty = int(self.inp_qty.text())
        except ValueError:
            return
        
        med = next((m for m in self.all_meds if m.id == med_id), None)
        if not med: return
        self._add_medication_item(med, qty)
        self._load_data()

    def _add_medication_item(self, med: Medication, qty: int = 1, increment_existing: bool = True) -> bool:
        # Check if already in items, update qty
        for it in self._prescription.items:
            if it.medication_id == med.id:
                if increment_existing:
                    it.quantity += qty
                return False
        self._prescription.items.append(
            PrescriptionItem(medication_id=med.id, quantity=qty, price_at_time=med.price)
        )
        return True

    def _diagnosis_context(self) -> str:
        med_rec = self._db.get_medical_record(self._appt.id)
        parts = [
            self._patient.active_diagnosis,
            med_rec.diagnosis if med_rec else "",
            self._appt.reason,
        ]
        return " ".join(p for p in parts if p).strip()

    def _suggest_items(self) -> None:
        diagnosis = self._diagnosis_context()
        if not diagnosis:
            QMessageBox.information(self, self._t("rx.ai_title"), self._t("rx.ai_no_diagnosis"))
            return

        normalized = diagnosis.lower()
        wanted_names: list[str] = []
        for disease_terms, med_names in MINI_AI_MED_RULES:
            if any(term in normalized for term in disease_terms):
                wanted_names.extend(med_names)

        suggestions: list[Medication] = []
        seen_ids = set()
        for wanted in wanted_names:
            wanted_l = wanted.lower()
            med = next((m for m in self.all_meds if wanted_l in m.name.lower()), None)
            if med and med.id not in seen_ids:
                suggestions.append(med)
                seen_ids.add(med.id)
            if len(suggestions) >= MINI_AI_MAX_SUGGESTIONS:
                break

        if not suggestions:
            QMessageBox.information(self, self._t("rx.ai_title"), self._t("rx.ai_no_match", diag=diagnosis))
            return

        added_count = 0
        for med in suggestions:
            if self._add_medication_item(med, 1, increment_existing=False):
                added_count += 1
        self._load_data()
        QMessageBox.information(self, self._t("rx.ai_title"), self._t("rx.ai_added", n=added_count))

    def _remove_item(self) -> None:
        idx = self.table.currentIndex()
        if not idx.isValid(): return
        row = idx.row()
        med_id = int(self.model.item(row, 0).text())
        self._prescription.items = [i for i in self._prescription.items if i.medication_id != med_id]
        self._load_data()

    def _save_bill(self) -> None:
        self._db.save_prescription(self._prescription)
        QMessageBox.information(self, "Success", "Bill saved successfully.")
        self.accept()

    def _get_html_content(self) -> str:
        html = f"""
        <html><head><style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            body {{ font-family: 'Roboto', 'Segoe UI', Arial, sans-serif; color: #2c3e50; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 30px; }}
            .header {{ text-align: center; border-bottom: 2px solid #00c9a7; padding-bottom: 20px; margin-bottom: 30px; }}
            .header h1 {{ color: #003d5c; font-size: 28px; margin: 0 0 10px 0; letter-spacing: 1px; }}
            .header p {{ margin: 5px 0; color: #7f8c8d; font-size: 14px; }}
            .title {{ text-align: center; color: #e74c3c; font-size: 22px; font-weight: 700; margin: 20px 0 30px 0; letter-spacing: 2px; }}
            .info-box {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 30px; border-left: 5px solid #00c9a7; }}
            .info-grid {{ display: table; width: 100%; }}
            .info-row {{ display: table-row; }}
            .info-cell {{ display: table-cell; padding: 5px 10px; font-size: 15px; }}
            .info-label {{ font-weight: 600; color: #34495e; width: 120px; }}
            table.items {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            table.items th {{ background-color: #00c9a7; color: white; padding: 12px; text-align: left; font-size: 14px; text-transform: uppercase; }}
            table.items td {{ border-bottom: 1px solid #ecf0f1; padding: 12px; font-size: 15px; }}
            table.items tr:last-child td {{ border-bottom: 2px solid #bdc3c7; }}
            .total-box {{ text-align: right; font-size: 20px; font-weight: 700; color: #2c3e50; padding: 15px; background: #e8f6f3; border-radius: 8px; margin-bottom: 40px; }}
            .total-amount {{ color: #e74c3c; font-size: 24px; }}
            .footer {{ text-align: center; color: #95a5a6; font-size: 13px; border-top: 1px solid #ecf0f1; padding-top: 20px; }}
            .signature-box {{ width: 100%; margin-top: 40px; display: table; }}
            .sig-col {{ display: table-cell; text-align: center; width: 50%; }}
            .sig-title {{ font-weight: bold; margin-bottom: 60px; color: #34495e; }}
        </style></head>
        <body>
            <div class='container'>
                <div class='header'>
                    <h1>HOSPITAL PMS</h1>
                    <p>{HOSPITAL_RECEIPT_ADDRESS}</p>
                    <p>Tel: (028) 1234-5678 | Email: contact@hospitalpms.com</p>
                </div>
                
                <div class='title'>PRESCRIPTION & INVOICE</div>
                
                <div class='info-box'>
                    <div class='info-grid'>
                        <div class='info-row'>
                            <div class='info-cell info-label'>Patient:</div>
                            <div class='info-cell'><b>{self._patient.full_name}</b></div>
                            <div class='info-cell info-label'>Date:</div>
                            <div class='info-cell'><b>{self._appt.appointment_date}</b></div>
                        </div>
                        <div class='info-row'>
                            <div class='info-cell info-label'>Doctor:</div>
                            <div class='info-cell'><b>{self._appt.doctor}</b></div>
                            <div class='info-cell info-label'>Bill ID:</div>
                            <div class='info-cell'><b>#INV-{self._appt.id:04d}</b></div>
                        </div>
                    </div>
                </div>

                <table class='items'>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 45%;">Item Name</th>
                        <th style="width: 10%; text-align: center;">Qty</th>
                        <th style="width: 20%; text-align: right;">Unit Price (VNĐ)</th>
                        <th style="width: 20%; text-align: right;">Total (VNĐ)</th>
                    </tr>
        """
        total = 0.0
        for i, item in enumerate(self._prescription.items, 1):
            m_name = next((m.name for m in self.all_meds if m.id == item.medication_id), "Unknown")
            t = item.quantity * item.price_at_time
            total += t
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{m_name}</td>
                    <td style="text-align: center;">{item.quantity}</td>
                    <td style="text-align: right;">{item.price_at_time:,.0f}</td>
                    <td style="text-align: right; font-weight: bold;">{t:,.0f}</td>
                </tr>
            """
        
        html += f"""
                </table>
                
                <div class='total-box'>
                    Total Amount: <span class='total-amount'>{total:,.0f} VNĐ</span>
                </div>
                
                <div class='signature-box'>
                    <div class='sig-col'>
                        <div class='sig-title'>Patient Signature</div>
                        <div>..................................</div>
                    </div>
                    <div class='sig-col'>
                        <div class='sig-title'>Doctor Signature</div>
                        <div><b>{self._appt.doctor}</b></div>
                    </div>
                </div>
                
                <div class='footer'>
                    Thank you for trusting Hospital PMS. Wishing you a speedy recovery!<br>
                    Generated on {self._appt.appointment_date}
                </div>
            </div>
        </body></html>
        """
        return html

    def _export_pdf(self) -> None:
        from PySide6.QtPrintSupport import QPrinter
        from PySide6.QtGui import QFont, QTextDocument
        from PySide6.QtWidgets import QMessageBox
        import os
        import uuid
        import datetime
        
        receipt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "receipt")
        os.makedirs(receipt_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_name = self._patient.full_name.replace(" ", "_")
        filename = f"Bill_{safe_name}_{timestamp}_{unique_id}.pdf"
        path = os.path.join(receipt_dir, filename)
        
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        
        doc = QTextDocument()
        doc.setDefaultFont(QFont("Arial", 10))
        doc.setHtml(self._get_html_content())
        doc.print_(printer)
        QMessageBox.information(self, "Exported", f"Saved PDF to {path}")

    def _export_png(self) -> None:
        from PySide6.QtGui import QFont, QTextDocument, QImage, QPainter
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import QSize, Qt
        import os
        import uuid
        import datetime
        
        receipt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "receipt")
        os.makedirs(receipt_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_name = self._patient.full_name.replace(" ", "_")
        filename = f"Bill_{safe_name}_{timestamp}_{unique_id}.png"
        path = os.path.join(receipt_dir, filename)
        
        doc = QTextDocument()
        doc.setDefaultFont(QFont("Arial", 10))
        doc.setHtml(self._get_html_content())
        
        width = 800
        min_height = int(width * 1.414) # A4 aspect ratio (vertical)
        doc.setTextWidth(width)
        
        content_size = doc.size().toSize()
        height = max(min_height, content_size.height() + 100) # Ensure vertical minimum
        
        img = QImage(QSize(width, height), QImage.Format_ARGB32)
        img.fill(Qt.white)
        
        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        doc.drawContents(painter)
        painter.end()
        
        img.save(path)
        QMessageBox.information(self, "Exported", f"Saved vertical PNG to {path}")


# ══════════════════════════════════════════════════════════════════════════════
#  PAYMENT DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class PaymentDialog(QDialog):
    def __init__(
        self,
        db: Database,
        appt: Appointment,
        patient: Patient,
        parent=None,
        lab_only: bool = False,
        lab_test: Optional[LabTest] = None,
    ):
        super().__init__(parent)
        self._db = db
        self._appt = appt
        self._patient = patient
        self._lab_only = lab_only
        self._single_lab_test = lab_test

        from PySide6.QtNetwork import QNetworkAccessManager
        self._nam = QNetworkAccessManager(self)
        self._nam.finished.connect(self._on_qr_downloaded)

        self._labs = self._db.get_lab_tests_by_appointment(appt.id)
        if lab_only and lab_test is not None:
            self._lab_fee = lab_test.price
            self._pending_labs = [lab_test]
        else:
            # Only charge for lab tests that haven't been paid separately
            self._pending_labs = [t for t in self._labs if t.status == "Pending"]
            self._lab_fee = sum(t.price for t in self._pending_labs)
            
        # Keep track of the tests to display in receipt
        self._receipt_labs = self._pending_labs

        if lab_only:
            self._appt_fee = 0.0
            self._med_fee = 0.0
            self._prescription = None
            self.all_meds = []
        else:
            self._appt_fee = 150000.0
            self._prescription = self._db.get_prescription_by_appointment(appt.id)
            self.all_meds = self._db.get_all_medications()
            self._med_fee = 0.0
            if self._prescription:
                for item in self._prescription.items:
                    self._med_fee += item.quantity * item.price_at_time

        self._subtotal = self._appt_fee + self._lab_fee + self._med_fee
        
        # Load existing payment to extract BHYT discount state
        self._existing_payment = self._db.get_payment(appt.id)
        self._has_bhyt = False
        if self._existing_payment:
            ref_str = self._existing_payment.reference_no or ""
            if "|BHYT:True" in ref_str:
                self._has_bhyt = True
                
        self._discount = self._subtotal * 0.8 if self._has_bhyt else 0.0
        self._total_amount = self._subtotal - self._discount
        
        title = "Lab Payment" if lab_only else "Payment Process"
        self.setWindowTitle(title)
        self.setMinimumSize(540, 680)
        self.setStyleSheet(f"background: {PALETTE['surface']}; border-radius: 12px;")
        
        self._build_ui()
        self._load_payment_state()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header Row: Title & Config Button
        self.title_widget = QWidget()
        title_layout = QHBoxLayout(self.title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        ttl = QLabel("💳  Payment Processing")
        ttl.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {PALETTE['accent2']};")
        
        self.btn_config = QPushButton()
        self.btn_config.setIcon(qta.icon('fa5s.cog', color=PALETTE['text_dim']))
        self.btn_config.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background: {PALETTE['surface2']};
            }}
        """)
        self.btn_config.setFixedSize(30, 30)
        self.btn_config.setToolTip("Configure Bank Account Settings")
        self.btn_config.clicked.connect(self._toggle_config_panel)
        
        title_layout.addWidget(ttl)
        title_layout.addStretch()
        title_layout.addWidget(self.btn_config)
        layout.addWidget(self.title_widget)
        self.title_widget.setVisible(False)
        
        self.divider = QFrame(); self.divider.setObjectName("divider"); self.divider.setFixedHeight(1)
        self.divider.setStyleSheet(f"background: {PALETTE['border']};")
        layout.addWidget(self.divider)
        self.divider.setVisible(False)
        
        # ⚙️ Bank Configuration Panel (Initially hidden)
        self.config_panel = QFrame()
        self.config_panel.setObjectName("config_panel")
        self.config_panel.setVisible(False)
        self.config_panel.setStyleSheet(f"""
            QFrame#config_panel {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['accent']};
                border-radius: 8px;
                padding: 12px;
            }}
            QLabel {{
                color: {PALETTE['text']};
                font-weight: 600;
                font-size: 12px;
            }}
            QLineEdit, QComboBox {{
                background: {PALETTE['surface']};
                border: 1px solid {PALETTE['border']};
                border-radius: 4px;
                color: #ffffff;
                padding: 6px;
                font-size: 12px;
            }}
        """)
        config_layout = QFormLayout(self.config_panel)
        config_layout.setSpacing(10)
        
        self.cmb_bank = QComboBox()
        self.cmb_bank.addItem("MBBank (Military Bank)", "MB")
        self.cmb_bank.addItem("Vietcombank", "VCB")
        self.cmb_bank.addItem("Techcombank", "TCB")
        self.cmb_bank.addItem("ACB", "ACB")
        self.cmb_bank.addItem("BIDV", "BIDV")
        self.cmb_bank.addItem("VietinBank", "ICB")
        self.cmb_bank.addItem("TPBank", "TPB")
        self.cmb_bank.addItem("VPBank", "VPB")
        self.cmb_bank.addItem("Agribank", "VBA")
        
        self.inp_bank_acc = QLineEdit()
        self.inp_bank_acc.setPlaceholderText("Enter account number...")
        self.inp_bank_name = QLineEdit()
        self.inp_bank_name.setPlaceholderText("Enter beneficiary name (capitalized)...")
        
        btn_save_config = QPushButton("💾 Apply & Save Settings")
        btn_save_config.setObjectName("btn_primary")
        btn_save_config.setStyleSheet(f"""
            QPushButton {{
                background: {PALETTE['accent']};
                color: #ffffff;
                font-weight: 700;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background: {PALETTE['accent2']};
            }}
        """)
        btn_save_config.clicked.connect(self._save_bank_config)
        
        config_layout.addRow(QLabel("Bank Name:"), self.cmb_bank)
        config_layout.addRow(QLabel("Account No:"), self.inp_bank_acc)
        config_layout.addRow(QLabel("Account Holder:"), self.inp_bank_name)
        config_layout.addRow(btn_save_config)
        
        layout.addWidget(self.config_panel)
        self.config_panel.setVisible(False)
        
        # Metadata Card
        self.info_card = QFrame()
        self.info_card.setObjectName("info_card")
        self.info_card.setStyleSheet(f"""
            QFrame#info_card {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        info_layout = QGridLayout(self.info_card)
        info_layout.setSpacing(8)
        
        lbl_s = f"color: {PALETTE['text_dim']}; font-weight: 600; font-size: 12px;"
        val_s = f"color: {PALETTE['text']}; font-weight: 700; font-size: 13px;"
        
        def add_meta(row, col, label, value):
            l = QLabel(label); l.setStyleSheet(lbl_s)
            v = QLabel(value); v.setStyleSheet(val_s)
            info_layout.addWidget(l, row, col*2)
            info_layout.addWidget(v, row, col*2+1)
            
        add_meta(0, 0, "Patient:", self._patient.full_name)
        add_meta(0, 1, "Doctor:", self._appt.doctor)
        add_meta(1, 0, "Date:", self._appt.appointment_date)
        add_meta(1, 1, "Bill ID:", f"#INV-{self._appt.id:04d}")
        
        layout.addWidget(self.info_card)
        
        # Detailed Billing Breakdown Panel
        self.amt_box = QFrame()
        self.amt_box.setObjectName("amt_box")
        self.amt_box.setStyleSheet(f"""
            QFrame#amt_box {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['border']};
                border-left: 5px solid {PALETTE['accent2']};
                border-radius: 8px;
                padding: 14px;
            }}
        """)
        
        breakdown_lay = QGridLayout(self.amt_box)
        breakdown_lay.setSpacing(10)
        
        def add_breakdown_row(r, label_txt, val_txt, is_bold=False, color_hex=None):
            l = QLabel(label_txt)
            v = QLabel(val_txt)
            if is_bold:
                l.setStyleSheet("font-weight: 800; font-size: 13px; color: #ffffff;")
                v.setStyleSheet(f"font-weight: 800; font-size: 15px; color: {color_hex or PALETTE['accent2']};")
            else:
                l.setStyleSheet(f"color: {PALETTE['text_dim']}; font-weight: bold; font-size: 12px;")
                v.setStyleSheet(f"color: {PALETTE['text']}; font-weight: bold; font-size: 12px;")
            breakdown_lay.addWidget(l, r, 0)
            breakdown_lay.addWidget(v, r, 1, Qt.AlignRight)
            return v
            
        row_idx = 0
        if not self._lab_only:
            add_breakdown_row(row_idx, "💵 Tiền khám lâm sàng:", f"{self._appt_fee:,.0f} VNĐ")
            row_idx += 1
        add_breakdown_row(row_idx, "🧪 Chi phí Xét nghiệm:", f"{self._lab_fee:,.0f} VNĐ")
        row_idx += 1
        if not self._lab_only:
            add_breakdown_row(row_idx, "💊 Tiền thuốc (Toa thuốc):", f"{self._med_fee:,.0f} VNĐ")
            row_idx += 1

        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background: {PALETTE['border']};")
        breakdown_lay.addWidget(sep, row_idx, 0, 1, 2)
        row_idx += 1

        subtotal_lbl = "Tổng chi phí XN:" if self._lab_only else "Tổng chi phí chưa giảm:"
        self.lbl_subtotal = add_breakdown_row(row_idx, subtotal_lbl, f"{self._subtotal:,.0f} VNĐ")
        row_idx += 1
        
        # BHYT Checkbox
        self.chk_bhyt = QCheckBox("Áp dụng Bảo hiểm y tế BHYT (Giảm 80% dịch vụ)")
        self.chk_bhyt.setStyleSheet(f"""
            QCheckBox {{
                color: {PALETTE['accent']};
                font-weight: bold;
                font-size: 12px;
                padding: 4px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
        """)
        self.chk_bhyt.setChecked(self._has_bhyt)
        self.chk_bhyt.stateChanged.connect(self._on_bhyt_changed)
        breakdown_lay.addWidget(self.chk_bhyt, row_idx, 0, 1, 2)
        row_idx += 1

        sep2 = QFrame(); sep2.setFixedHeight(1); sep2.setStyleSheet(f"background: {PALETTE['border']};")
        breakdown_lay.addWidget(sep2, row_idx, 0, 1, 2)
        row_idx += 1

        total_lbl = "Số tiền XN cần thanh toán:" if self._lab_only else "Số tiền Bệnh nhân cần thanh toán:"
        self.lbl_grand_total = add_breakdown_row(row_idx, total_lbl, f"{self._total_amount:,.0f} VNĐ", is_bold=True)
        
        layout.addWidget(self.amt_box)
        
        # Payment Method Radio Group
        self.method_grp = QGroupBox("Payment Method")
        method_layout = QHBoxLayout(self.method_grp)
        method_layout.setContentsMargins(16, 12, 16, 12)
        method_layout.setSpacing(20)
        
        self.rad_cash = QRadioButton("💵 Tiền mặt (Cash)")
        self.rad_bank = QRadioButton("🏦 Chuyển khoản (Bank Transfer)")
        self.rad_cash.setChecked(True)
        
        radio_style = f"""
            QRadioButton {{
                color: {PALETTE['text']};
                font-weight: 600;
                font-size: 13px;
                padding: 4px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {PALETTE['border']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {PALETTE['accent2']};
                border: 2px solid {PALETTE['accent2']};
            }}
        """
        self.rad_cash.setStyleSheet(radio_style)
        self.rad_bank.setStyleSheet(radio_style)
        
        method_layout.addWidget(self.rad_cash)
        method_layout.addWidget(self.rad_bank)
        layout.addWidget(self.method_grp)
        
        self.rad_cash.toggled.connect(self._on_method_changed)
        self.rad_bank.toggled.connect(self._on_method_changed)
        
        # Bank Transfer Widgets
        self.qr_widget = QFrame()
        self.qr_widget.setObjectName("qr_widget")
        self.qr_widget.setStyleSheet(f"""
            QFrame#qr_widget {{
                background: {PALETTE['surface2']};
                border: 1px solid {PALETTE['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        qr_layout = QVBoxLayout(self.qr_widget)
        qr_layout.setContentsMargins(14, 14, 14, 14)
        qr_layout.setSpacing(12)
        
        self.qr_img_label = QLabel("QR image unavailable.")
        self.qr_img_label.setFixedSize(500, 545)
        self.qr_img_label.setAlignment(Qt.AlignCenter)
        self.qr_img_label.setStyleSheet("background: #ffffff; color: #2c3e50; border-radius: 4px; padding: 4px;")
        qr_layout.addWidget(self.qr_img_label, alignment=Qt.AlignCenter)

        self.bank_owner_label = QLabel("Chủ TK: NGUYEN VO HAI DANG")
        self.bank_owner_label.setAlignment(Qt.AlignCenter)
        self.bank_owner_label.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 800;")
        qr_layout.addWidget(self.bank_owner_label)

        self.bank_account_label = QLabel("Số TK:0397745318")
        self.bank_account_label.setAlignment(Qt.AlignCenter)
        self.bank_account_label.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 800;")
        qr_layout.addWidget(self.bank_account_label)

        self.bank_loading_widget = QFrame()
        self.bank_loading_widget.setStyleSheet(f"""
            QFrame {{
                background: {PALETTE['surface']};
                border: none;
            }}
        """)
        bank_loading_lay = QVBoxLayout(self.bank_loading_widget)
        bank_loading_lay.setContentsMargins(0, 24, 0, 24)
        bank_loading_lay.setSpacing(18)

        self.bank_loading_gif = QLabel()
        self.bank_loading_gif.setAlignment(Qt.AlignCenter)
        self.bank_loading_movie = QMovie(os.path.join(os.path.dirname(os.path.abspath(__file__)), "loading_transfer.gif"))
        self.bank_loading_movie.setScaledSize(QSize(220, 220))
        self.bank_loading_gif.setMovie(self.bank_loading_movie)
        bank_loading_lay.addWidget(self.bank_loading_gif, alignment=Qt.AlignCenter)

        self.bank_loading_title = QLabel("VUI LÒNG CHỜ")
        self.bank_loading_title.setAlignment(Qt.AlignCenter)
        self.bank_loading_title.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: 900;")
        bank_loading_lay.addWidget(self.bank_loading_title)
        self.bank_loading_widget.setVisible(False)
        qr_layout.addWidget(self.bank_loading_widget)

        self.btn_confirm_bank = QPushButton("Xác nhận chuyển khoản")
        self.btn_confirm_bank.setObjectName("btn_primary")
        self.btn_confirm_bank.setFixedHeight(40)
        self.btn_confirm_bank.clicked.connect(self._on_confirm_bank_transfer)
        qr_layout.addWidget(self.btn_confirm_bank)
        layout.addWidget(self.qr_widget)
        
        # Reference Number Box
        self.ref_layout_widget = QWidget()
        self.ref_box = QHBoxLayout(self.ref_layout_widget)
        self.ref_box.setContentsMargins(0, 0, 0, 0)
        self.lbl_ref_no = QLabel("Reference No *:")
        self.lbl_ref_no.setStyleSheet(lbl_s)
        self.inp_ref_no = QLineEdit()
        self.inp_ref_no.setPlaceholderText("Enter transaction reference number...")
        self.ref_box.addWidget(self.lbl_ref_no)
        self.ref_box.addWidget(self.inp_ref_no, stretch=1)
        layout.addWidget(self.ref_layout_widget)
        self.ref_layout_widget.setVisible(False)  # Completely hidden from view as requested
        
        # Status Box
        self.status_widget = QWidget()
        self.status_box = QHBoxLayout(self.status_widget)
        self.status_box.setContentsMargins(0, 0, 0, 0)
        status_lbl = QLabel("Status:")
        status_lbl.setStyleSheet(lbl_s)
        self.status_badge = QLabel("UNPAID")
        self.status_badge.setStyleSheet("background: #f14c4c; color: #ffffff; font-weight: bold; padding: 4px 10px; border-radius: 10px; font-size: 11px;")
        self.status_box.addWidget(status_lbl)
        self.status_box.addWidget(self.status_badge)
        self.status_box.addStretch()
        layout.addWidget(self.status_widget)
        
        layout.addStretch()
        
        # Actions Row
        self.btn_row_widget = QWidget()
        self.btn_row = QHBoxLayout(self.btn_row_widget)
        self.btn_row.setContentsMargins(0, 0, 0, 0)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_confirm = QPushButton("💳  Confirm & Pay")
        self.btn_confirm.setObjectName("btn_primary")
        self.btn_confirm.clicked.connect(self._on_confirm_pay)
        
        self.btn_pdf = QPushButton("📄 Export PDF")
        self.btn_pdf.clicked.connect(self._on_export_pdf)
        
        self.btn_png = QPushButton("🖼 Export PNG")
        self.btn_png.clicked.connect(self._on_export_png)
        
        self.btn_row.addStretch()
        self.btn_row.addWidget(self.btn_cancel)
        self.btn_row.addWidget(self.btn_confirm)
        self.btn_row.addWidget(self.btn_pdf)
        self.btn_row.addWidget(self.btn_png)
        layout.addWidget(self.btn_row_widget)
 
    def _toggle_config_panel(self) -> None:
        self.config_panel.setVisible(not self.config_panel.isVisible())
 
    def _save_bank_config(self) -> None:
        from PySide6.QtCore import QSettings
        settings = QSettings("HospitalPMS", "PaymentSettings")
        settings.setValue("bank_id", self.cmb_bank.currentData())
        settings.setValue("account_no", self.inp_bank_acc.text().strip())
        settings.setValue("account_name", self.inp_bank_name.text().strip().upper())
        
        self.config_panel.setVisible(False)
        self._update_bank_labels()
        self._load_qr_code()
 
    def _update_bank_labels(self) -> None:
        return
 
    def _on_method_changed(self) -> None:
        is_bank = self.rad_bank.isChecked()
        self.qr_widget.setVisible(is_bank)
        self.lbl_ref_no.setVisible(False)
        self.inp_ref_no.setVisible(False)
        self.ref_layout_widget.setVisible(False)
        is_paid = self._existing_payment and self._existing_payment.status == "Paid"
        self.btn_config.setVisible(False)
        self.btn_confirm.setVisible(not is_bank and not is_paid)
        for widget in (
            self.info_card,
            self.amt_box,
            self.method_grp,
            self.status_widget,
        ):
            widget.setVisible(not is_bank)
        self.config_panel.setVisible(False)
        self.setMinimumSize(600 if is_bank else 540, 860 if is_bank else 680)
        if is_bank:
            self.qr_img_label.setVisible(True)
            self.bank_owner_label.setVisible(True)
            self.bank_account_label.setVisible(True)
            self.bank_loading_widget.setVisible(False)
            self.bank_loading_movie.stop()
            self.btn_confirm_bank.setVisible(not is_paid)
            self._load_qr_code()
 
    def _load_qr_code(self) -> None:
        local_qr_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr_payment.jpg")
        if not os.path.exists(local_qr_path):
            local_qr_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr_receipt_vietqr.png")
        if not os.path.exists(local_qr_path):
            self.qr_img_label.clear()
            self.qr_img_label.setText("QR image unavailable.")
            return

        pixmap = QPixmap(local_qr_path)
        if pixmap.isNull():
            self.qr_img_label.clear()
            self.qr_img_label.setText("QR image unavailable.")
            return
        self.qr_img_label.setScaledContents(False)
        self.qr_img_label.setPixmap(pixmap.scaled(
            self.qr_img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
 
    def _on_qr_downloaded(self, reply) -> None:
        from PySide6.QtNetwork import QNetworkReply
        from PySide6.QtGui import QPixmap
        
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(data):
                self.qr_img_label.setScaledContents(False)  # Keep online generator QR square & centered
                self.qr_img_label.setPixmap(pixmap.scaled(220, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.qr_img_label.setText("Error loading QR image.")
        else:
            self.qr_img_label.setText("Offline / QR generator unavailable.")
        reply.deleteLater()
 
    def _load_payment_state(self) -> None:
        # Load persisted settings into inputs
        from PySide6.QtCore import QSettings
        settings = QSettings("HospitalPMS", "PaymentSettings")
        bank_id = settings.value("bank_id", "MB")
        account_no = settings.value("account_no", "0397745318")
        account_name = settings.value("account_name", "NGUYEN HOANG PHUONG")
        
        # Override old hardcoded test defaults
        if account_no == "0901234567":
            account_no = "0397745318"
            bank_id = "MB"
            account_name = "NGUYEN HOANG PHUONG"
            settings.setValue("bank_id", bank_id)
            settings.setValue("account_no", account_no)
            settings.setValue("account_name", account_name)
            
        self.cmb_bank.setCurrentIndex(self.cmb_bank.findData(bank_id))
        self.inp_bank_acc.setText(account_no)
        self.inp_bank_name.setText(account_name)
        self._update_bank_labels()
        
        if self._existing_payment and self._existing_payment.status == "Paid":
            self.status_badge.setText("PAID")
            self.status_badge.setStyleSheet("background: #2ecc71; color: #ffffff; font-weight: bold; padding: 4px 10px; border-radius: 10px; font-size: 11px;")
            
            ref_str = self._existing_payment.reference_no or ""
            clean_ref = ref_str.split("|BHYT:")[0] if "|BHYT:" in ref_str else ref_str
            self._has_bhyt = "|BHYT:True" in ref_str
            
            if self._existing_payment.method == "Bank Transfer":
                self.rad_bank.setChecked(True)
                self.inp_ref_no.setText(clean_ref)
            else:
                self.rad_cash.setChecked(True)
                
            self.rad_cash.setEnabled(False)
            self.rad_bank.setEnabled(False)
            self.inp_ref_no.setEnabled(False)
            self.btn_config.setEnabled(False)
            
            self.chk_bhyt.setEnabled(False)
            self.chk_bhyt.setChecked(self._has_bhyt)
            
            self._on_method_changed()
            
            self.btn_confirm.setVisible(False)
            self.btn_confirm_bank.setVisible(False)
            self.btn_cancel.setText("Close")
            self.btn_pdf.setVisible(True)
            self.btn_png.setVisible(True)
        else:
            self.status_badge.setText("UNPAID")
            self.status_badge.setStyleSheet("background: #f14c4c; color: #ffffff; font-weight: bold; padding: 4px 10px; border-radius: 10px; font-size: 11px;")
            
            self.rad_cash.setEnabled(True)
            self.rad_bank.setEnabled(True)
            self.inp_ref_no.setEnabled(True)
            self.btn_config.setEnabled(True)
            self.btn_config.setVisible(False)
            self.chk_bhyt.setEnabled(True)
            
            self._on_method_changed()
            
            self.btn_confirm.setVisible(not self.rad_bank.isChecked())
            self.btn_confirm_bank.setVisible(self.rad_bank.isChecked())
            self.btn_cancel.setText("Cancel")
            self.btn_pdf.setVisible(False)
            self.btn_png.setVisible(False)

    def _on_bhyt_changed(self) -> None:
        self._has_bhyt = self.chk_bhyt.isChecked()
        self._discount = self._subtotal * 0.8 if self._has_bhyt else 0.0
        self._total_amount = self._subtotal - self._discount
        self.lbl_grand_total.setText(f"{self._total_amount:,.0f} VNĐ")
        if self.rad_bank.isChecked():
            self._load_qr_code()

    def _on_confirm_pay(self) -> None:
        self._complete_payment("Cash")

    def _on_confirm_bank_transfer(self) -> None:
        self.qr_img_label.setVisible(False)
        self.bank_owner_label.setVisible(False)
        self.bank_account_label.setVisible(False)
        self.btn_confirm_bank.setVisible(False)
        self.bank_loading_widget.setVisible(True)
        self.bank_loading_movie.start()
        self.rad_cash.setEnabled(False)
        self.rad_bank.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.btn_row_widget.setVisible(False)
        QTimer.singleShot(4000, lambda: self._complete_payment("Bank Transfer", ask_confirmation=False))

    def _complete_payment(self, method: str, ask_confirmation: bool = True) -> None:
        ref_no = self.inp_ref_no.text().strip()
        if not ref_no:
            ref_no = f"INV-{self._appt.id:04d}"
            
        ref_no_with_bhyt = f"{ref_no}|BHYT:{self._has_bhyt}"
        
        if ask_confirmation:
            reply = QMessageBox.question(
                self, "Confirm Payment",
                f"Are you sure you want to mark this bill of <b>{self._total_amount:,.0f} VNĐ</b> as Paid?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            
        if not self._lab_only:
            payment = Payment(
                appointment_id=self._appt.id,
                amount=self._total_amount,
                method=method,
                status="Paid",
                reference_no=ref_no_with_bhyt,
            )
            self._db.save_payment(payment)
            
            # Also mark all pending lab tests as paid (Processing)
            for test in self._pending_labs:
                self._db.set_lab_test_status(test.id, "Processing")

            parent = self.parent()
            if parent and hasattr(parent, "_schedule_lab_test_completion"):
                for test in self._pending_labs:
                    parent._schedule_lab_test_completion(test.id)
                
            self._existing_payment = self._db.get_payment(self._appt.id)
            if ask_confirmation:
                self._load_payment_state()
        
        exp_reply = QMessageBox.question(
            self, "Payment Successful",
            "Payment processed successfully!\nWould you like to export the receipt as PDF now?",
            QMessageBox.Yes | QMessageBox.No
        )
        if exp_reply == QMessageBox.Yes:
            self._on_export_pdf()
            
        self.accept()

    def _on_export_pdf(self) -> None:
        from PySide6.QtPrintSupport import QPrinter
        from PySide6.QtGui import QFont, QTextDocument
        from PySide6.QtWidgets import QMessageBox
        import os
        import uuid
        import datetime
        
        payment = self._existing_payment or Payment(
            appointment_id=self._appt.id,
            amount=self._total_amount,
            method="Bank Transfer" if self.rad_bank.isChecked() else "Cash",
            status="Paid",
            reference_no=self.inp_ref_no.text().strip()
        )
        
        receipt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "receipt")
        os.makedirs(receipt_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_name = self._patient.full_name.replace(" ", "_")
        filename = f"Receipt_{safe_name}_{timestamp}_{unique_id}.pdf"
        path = os.path.join(receipt_dir, filename)
        
        printer = QPrinter(QPrinter.ScreenResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        
        doc = QTextDocument()
        doc.setDefaultFont(QFont("Arial", 10))
        doc.setHtml(self._get_receipt_html(payment))
        doc.print_(printer)
        QMessageBox.information(self, "Exported", f"Saved receipt PDF to {path}")

    def _on_export_png(self) -> None:
        from PySide6.QtGui import QFont, QTextDocument, QImage, QPainter
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import QSize, Qt
        import os
        import uuid
        import datetime
        
        payment = self._existing_payment or Payment(
            appointment_id=self._appt.id,
            amount=self._total_amount,
            method="Bank Transfer" if self.rad_bank.isChecked() else "Cash",
            status="Paid",
            reference_no=self.inp_ref_no.text().strip()
        )
        
        receipt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "receipt")
        os.makedirs(receipt_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_name = self._patient.full_name.replace(" ", "_")
        filename = f"Receipt_{safe_name}_{timestamp}_{unique_id}.png"
        path = os.path.join(receipt_dir, filename)
        
        doc = QTextDocument()
        doc.setDefaultFont(QFont("Arial", 10))
        doc.setHtml(self._get_receipt_html(payment))
        
        width = 800
        min_height = int(width * 1.414)
        doc.setTextWidth(width)
        
        content_size = doc.size().toSize()
        height = max(min_height, content_size.height() + 100)
        
        img = QImage(QSize(width, height), QImage.Format_ARGB32)
        img.fill(Qt.white)
        
        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        doc.drawContents(painter)
        painter.end()
        
        img.save(path)
        QMessageBox.information(self, "Exported", f"Saved vertical receipt PNG to {path}")

    def _number_to_vietnamese_words(self, n: float) -> str:
        n = int(n)
        if n == 0:
            return "Không đồng"
            
        units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
        
        def read_hundred(num: int, show_zero_hundred=False) -> str:
            hundred = num // 100
            ten = (num % 100) // 10
            unit = num % 10
            
            res = []
            if hundred > 0 or show_zero_hundred:
                res.append(units[hundred] + " trăm")
                
            if ten > 0:
                if ten == 1:
                    res.append("mười")
                else:
                    res.append(units[ten] + " mươi")
            elif (hundred > 0 or show_zero_hundred) and unit > 0:
                res.append("lẻ")
                
            if unit > 0:
                if unit == 1 and ten > 1:
                    res.append("mốt")
                elif unit == 5 and ten > 0:
                    res.append("lăm")
                else:
                    res.append(units[unit])
            return " ".join(res)

        groups = []
        temp = n
        while temp > 0:
            groups.append(temp % 1000)
            temp //= 1000
            
        group_names = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"]
        words = []
        
        for i in range(len(groups) - 1, -1, -1):
            g = groups[i]
            if g == 0:
                continue
            show_zero = (i < len(groups) - 1)
            g_words = read_hundred(g, show_zero)
            if g_words:
                words.append(g_words)
                if group_names[i]:
                    words.append(group_names[i])
                    
        words_str = " ".join(words) + " đồng"
        return words_str.capitalize()

    def _get_receipt_html(self, payment: Payment) -> str:
        import datetime
        now = datetime.datetime.now()
        formatted_date_time = f"Ngày {now.day:02d} tháng {now.month:02d} năm {now.year} {now.strftime('%H:%M:%S')}"
        
        is_male = self._patient.gender.lower() in ["male", "nam"]
        gender_html = f"""
        Giới tính / Sex: 
        <span style="border: 1px solid #000; padding: 1px 4px; font-weight: bold;">{'X' if is_male else '&nbsp;&nbsp;'}</span> Nam/Male
        <span style="border: 1px solid #000; padding: 1px 4px; font-weight: bold; margin-left: 6px;">{'X' if not is_male else '&nbsp;&nbsp;'}</span> Nữ/Female
        """

        items_rows_html = ""
        total_amount = 0.0
        total_qty = 0
        
        row_idx = 1
        
        if not self._lab_only:
            items_rows_html += f"""
            <tr>
                <td style="border: 1px solid #000; padding: 5px; text-align: center;">{row_idx}</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: left;">Khám bệnh tổng quát / General Clinical Consultation</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: center;">1</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right;">{self._appt_fee:,.0f}</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right;">{self._appt_fee:,.0f}</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right; font-weight: bold;">{self._appt_fee:,.0f}</td>
            </tr>
            """
            row_idx += 1
            total_qty += 1
            total_amount += self._appt_fee
            
        if self._receipt_labs:
            for test in self._receipt_labs:
                items_rows_html += f"""
                <tr>
                    <td style="border: 1px solid #000; padding: 5px; text-align: center;">{row_idx}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: left;">Xét nghiệm / Lab Test: {test.test_name}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: center;">1</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">{test.price:,.0f}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">{test.price:,.0f}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right; font-weight: bold;">{test.price:,.0f}</td>
                </tr>
                """
                row_idx += 1
                total_qty += 1
                total_amount += test.price

        if not self._lab_only and self._prescription and self._prescription.items:
            for item in self._prescription.items:
                m_name = next((m.name for m in self.all_meds if m.id == item.medication_id), "Unknown")
                line_total = item.quantity * item.price_at_time
                total_amount += line_total
                items_rows_html += f"""
                <tr>
                    <td style="border: 1px solid #000; padding: 5px; text-align: center;">{row_idx}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: left;">Thuốc / Med: {m_name}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: center;">{item.quantity}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">{item.price_at_time:,.0f}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">{line_total:,.0f}</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                    <td style="border: 1px solid #000; padding: 5px; text-align: right; font-weight: bold;">{line_total:,.0f}</td>
                </tr>
                """
                row_idx += 1
                total_qty += item.quantity
                
        if self._has_bhyt:
            items_rows_html += f"""
            <tr>
                <td colspan="4" style="border: 1px solid #000; padding: 5px; text-align: right; font-weight: bold;">BHYT chi trả / Health Insurance (80%)</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right;"></td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right; color: #d9534f; font-weight: bold;">-{self._discount:,.0f}</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right;">0</td>
                <td style="border: 1px solid #000; padding: 5px; text-align: right; font-weight: bold; color: #d9534f;">-{self._discount:,.0f}</td>
            </tr>
            """
            
        total_amount = payment.amount

        method_display = payment.method
        if payment.method == "Bank Transfer":
            from PySide6.QtCore import QSettings
            settings = QSettings("HospitalPMS", "PaymentSettings")
            bank_id = settings.value("bank_id", "MB")
            account_no = settings.value("account_no", "0901234567")
            account_name = settings.value("account_name", "HOSPITAL PMS")
            method_display = f"Chuyển khoản / Bank Transfer<br><span style='font-size: 9px; font-weight: normal; color: #555;'>({bank_id} - {account_no} - {account_name})<br>Ref: {payment.reference_no if payment.reference_no else 'N/A'}</span>"
        else:
            method_display = "Tiền mặt / Cash"

        amount_in_words = self._number_to_vietnamese_words(total_amount)
        qr_footer_html = _receipt_qr_image_html(85)

        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #000000;
                    margin: 0;
                    padding: 10px;
                    background-color: #ffffff;
                }}
                .container {{
                    width: 100%;
                    max-width: 780px;
                    margin: 0 auto;
                }}
                .header-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 10px;
                }}
                .header-logo-cell {{
                    width: 70%;
                    text-align: left;
                    vertical-align: top;
                }}
                .header-qr-cell {{
                    width: 30%;
                    text-align: right;
                    vertical-align: top;
                }}
                .hospital-title {{
                    font-size: 13px;
                    font-weight: bold;
                    color: #003366;
                    text-transform: uppercase;
                }}
                .hospital-sub {{
                    font-size: 11px;
                    color: #333333;
                    margin-top: 2px;
                }}
                .hospital-info {{
                    font-size: 9px;
                    color: #666666;
                    line-height: 1.3;
                    margin-top: 4px;
                }}
                .qr-receipt-img {{
                    text-align: right;
                    display: inline-block;
                }}
                .receipt-title-box {{
                    text-align: center;
                    margin-top: 15px;
                    margin-bottom: 15px;
                }}
                .receipt-title {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #003366;
                    letter-spacing: 0.5px;
                }}
                .receipt-no {{
                    font-size: 12px;
                    color: #333333;
                    margin-top: 4px;
                }}
                .receipt-subtitle {{
                    font-size: 10px;
                    font-style: italic;
                    color: #666666;
                }}
                .section-header {{
                    background-color: #f2f2f2;
                    border: 1px solid #000000;
                    padding: 4px;
                    font-weight: bold;
                    font-size: 12px;
                    text-align: center;
                    text-transform: uppercase;
                    margin-bottom: 0px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <!-- HEADER AREA -->
                <table class="header-table">
                    <tr>
                        <td class="header-logo-cell" colspan="2">
                            <div class="hospital-title">BỆNH VIỆN ĐA KHOA HOSPITAL PMS</div>
                            <div class="hospital-sub">PHÒNG KHÁM BỆNH VIỆN ĐA KHOA HOSPITAL PMS 1</div>
                            <div class="hospital-info">
                                📞 1900 6423 | 🌐 www.hospitalpms.com<br>
                                📍 {HOSPITAL_RECEIPT_ADDRESS}
                            </div>
                        </td>
                    </tr>
                </table>

                <!-- RECEIPT TITLE -->
                <div class="receipt-title-box">
                    <div class="receipt-title">BIÊN LAI THU TIỀN / RECEIPT</div>
                    <div class="receipt-no">Số phiếu / Receipt No.: <b>#REC-{self._appt.id:04d}-{payment.appointment_id:04d}</b></div>
                    <div class="receipt-subtitle">(Bản chính)</div>
                </div>

                <!-- PATIENT INFORMATION -->
                <div class="section-header">Thông tin hành chính / Patient Information</div>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 12px; border: 1px solid #000000;">
                    <tr>
                        <td style="border: 1px solid #000000; padding: 6px; width: 45%;">Họ và tên / Name: <b>{self._patient.full_name.upper()}</b></td>
                        <td style="border: 1px solid #000000; padding: 6px; width: 30%;">{gender_html}</td>
                        <td style="border: 1px solid #000000; padding: 6px; width: 25%;">Năm / DOB: <b>{self._patient.dob}</b></td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000000; padding: 6px;">Khoa / Dept: <b>Khám bệnh</b></td>
                        <td style="border: 1px solid #000000; padding: 6px;">Phòng / Room: <b>Khám nội 1 - Tầng 2 STT: {self._appt.id}</b></td>
                        <td style="border: 1px solid #000000; padding: 6px;">Giường / Bed: <b>N/A</b></td>
                    </tr>
                    <tr>
                        <td colspan="3" style="border: 1px solid #000000; padding: 6px;">Địa chỉ / Address: <b>{HOSPITAL_RECEIPT_ADDRESS}</b></td>
                    </tr>
                </table>

                <!-- ITEMS TABLE -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 11px; border: 1px solid #000000;">
                    <thead>
                        <tr style="background-color: #f2f2f2; font-weight: bold; text-align: center;">
                            <th style="border: 1px solid #000000; padding: 6px; width: 4%;">No.</th>
                            <th style="border: 1px solid #000000; padding: 6px; text-align: left; width: 36%;">Tên dịch vụ / Services Name</th>
                            <th style="border: 1px solid #000000; padding: 6px; width: 6%;">SL / Qty</th>
                            <th style="border: 1px solid #000000; padding: 6px; text-align: right; width: 12%;">Đơn giá / Price</th>
                            <th style="border: 1px solid #000000; padding: 6px; text-align: right; width: 12%;">Thành tiền / Charges</th>
                            <th style="border: 1px solid #000000; padding: 6px; text-align: right; width: 10%;">Bảo hiểm</th>
                            <th style="border: 1px solid #000000; padding: 6px; text-align: right; width: 6%;">Khác</th>
                            <th style="border: 1px solid #000000; padding: 6px; text-align: right; width: 10%;">Số tiền giảm</th>
                            <th style="border: 1px solid #000000; padding: 6px; text-align: right; width: 12%;">BN trả / Patient</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_rows_html}
                        <tr style="font-weight: bold; background-color: #fafafa;">
                            <td colspan="2" style="border: 1px solid #000000; padding: 6px; text-align: right;">Tổng tạm / Subtotal:</td>
                            <td style="border: 1px solid #000000; padding: 6px; text-align: center;">{total_qty}</td>
                            <td style="border: 1px solid #000000; padding: 6px; text-align: right;">-</td>
                            <td style="border: 1px solid #000000; padding: 6px; text-align: right;">{total_amount:,.0f}</td>
                            <td style="border: 1px solid #000000; padding: 6px; text-align: right;">0</td>
                            <td style="border: 1px solid #000000; padding: 6px; text-align: right;">0</td>
                            <td style="border: 1px solid #000000; padding: 6px; text-align: right;">0</td>
                            <td style="border: 1px solid #000000; padding: 6px; text-align: right;">{total_amount:,.0f}</td>
                        </tr>
                    </tbody>
                </table>

                <!-- TOTALS SECTION -->
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 12px; border: 1px solid #000000;">
                    <tr>
                        <td style="border: 1px solid #000000; padding: 8px; width: 70%; vertical-align: top;">
                            Số tiền viết bằng chữ / Total amount by words:<br>
                            <b style="font-style: italic; color: #003366; font-size: 12px; margin-top: 4px; display: block;">{amount_in_words}</b>
                        </td>
                        <td style="border: 1px solid #000000; padding: 8px; width: 30%; text-align: right; vertical-align: middle; background-color: #fafafa;">
                            <span style="font-size: 10px; font-weight: bold; color: #555555; text-transform: uppercase;">Total Amount:</span><br>
                            <b style="font-size: 16px; color: #d9534f; display: block; margin-top: 2px;">{total_amount:,.0f} VNĐ</b>
                        </td>
                    </tr>
                </table>

                <!-- PAYMENT METHOD -->
                <table style="width: 50%; border-collapse: collapse; margin-bottom: 20px; font-size: 11px; border: 1px solid #000000;">
                    <tr style="background-color: #f2f2f2; font-weight: bold; text-align: center;">
                        <td style="border: 1px solid #000000; padding: 6px; width: 50%;">Phương thức / Method</td>
                        <td style="border: 1px solid #000000; padding: 6px; width: 50%;">Tổng tiền / Amount</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000000; padding: 6px; text-align: center; font-weight: bold;">{method_display}</td>
                        <td style="border: 1px solid #000000; padding: 6px; text-align: right; font-weight: bold; color: #003366;">{total_amount:,.0f} VNĐ</td>
                    </tr>
                </table>

                <!-- DATE AND SIGNATURES -->
                <table style="width: 100%; margin-bottom: 40px; font-size: 11px; text-align: center; border-collapse: collapse;">
                    <tr>
                        <td colspan="3" style="text-align: right; padding-bottom: 12px; font-style: italic; color: #333333;">
                            {formatted_date_time}
                        </td>
                    </tr>
                    <tr style="font-weight: bold; color: #003366;">
                        <td style="width: 33%;">Người nộp tiền<br><span style="font-size: 9px; font-weight: normal; font-style: italic; color: #666666;">(Ký, ghi rõ họ tên)</span></td>
                        <td style="width: 33%;">Đề nghị của bác sĩ<br><span style="font-size: 9px; font-weight: normal; font-style: italic; color: #666666;">(Ký, ghi rõ họ tên)</span></td>
                        <td style="width: 34%;">Người thu / Cashier<br><span style="font-size: 9px; font-weight: normal; font-style: italic; color: #666666;">(Ký, đóng dấu)</span></td>
                    </tr>
                    <tr>
                        <td style="height: 60px; vertical-align: bottom; color: #888888;">..................................</td>
                        <td style="height: 60px; vertical-align: bottom; color: #888888;">
                            <span style="color: #000000; font-weight: bold;">{self._appt.doctor}</span><br>
                            <span style="color: #888888;">..................................</span>
                        </td>
                        <td style="height: 60px; vertical-align: bottom; color: #888888;">
                            <span style="color: #000000; font-weight: bold;">Phòng Tài Vụ</span><br>
                            <span style="color: #888888;">..................................</span>
                        </td>
                    </tr>
                </table>

                <!-- INVOICE WARNING FOOTER -->
                <hr style="border: 0; border-top: 1px dashed #cccccc; margin-bottom: 12px;">
                <table style="width: 100%; font-size: 10px; color: #555555; line-height: 1.4; border-collapse: collapse;">
                    <tr>
                        <td style="width: 15%; text-align: center; vertical-align: middle; padding-right: 10px;">
                            <div class="qr-receipt-img">
                                {qr_footer_html}
                            </div>
                        </td>
                        <td style="width: 85%; vertical-align: middle; text-align: left;">
                            * <b>Quý khách hàng vui lòng kiểm tra kỹ thông tin trên biên lai.</b> Phòng khám không có chính sách đổi trả các dịch vụ sau khi hoàn tất thanh toán.<br>
                            * Quét mã QR bên cạnh để xuất Hóa đơn điện tử (HĐĐT).<br>
                            * <b>Lưu ý:</b> Thực hiện cập nhật thông tin xuất HĐĐT chỉ áp dụng trong ngày (Trước 22h00). Quý khách vui lòng giữ biên lai này để tra cứu HĐĐT.
                        </td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        return html


# ─────────────────────────────────────────────────────────────────── #
#  Laboratory Management Classes & Tab                               #
# ─────────────────────────────────────────────────────────────────── #

LAB_HEADER_KEYS = [
    "lab.th.id", "lab.th.patient", "lab.th.doctor", "lab.th.test",
    "lab.th.cost", "lab.th.status", "lab.th.date",
]


class LabTestTableModel(QAbstractTableModel):
    def __init__(self, tests: list[tuple] = None, lang: str | None = None):
        super().__init__()
        self._data = tests or []
        self._lang = lang or get_language()
        self._headers = [tr(k, self._lang) for k in LAB_HEADER_KEYS]

    def set_language(self, lang: str) -> None:
        self._lang = lang
        self._headers = [tr(k, lang) for k in LAB_HEADER_KEYS]
        self.headerDataChanged.emit(Qt.Horizontal, 0, len(self._headers) - 1)

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid(): return None
        row = self._data[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            if col == 0: return f"LAB-{row[0]:04d}"
            if col == 1: return str(row[1])
            if col == 2: return str(row[2])
            if col == 3: return str(row[3])
            if col == 4: return f"{row[4]:,.0f}"
            if col == 5: return str(row[5])
            if col == 6: return str(row[7]) # created_at
        if role == Qt.TextAlignmentRole:
            if col in (0, 4, 5, 6): return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter
        if role == Qt.ForegroundRole:
            if col == 4: return QColor(PALETTE["accent"])
            if col == 5:
                status = row[5]
                if status == "Pending": return QColor("#ff9800")
                if status == "Processing": return QColor("#00bcd4")
                if status == "Completed": return QColor("#4caf50")
        return None

    def row_at(self, row: int) -> Optional[tuple]:
        if 0 <= row < len(self._data): return self._data[row]
        return None

    def refresh(self, tests: list[tuple]) -> None:
        self.beginResetModel()
        self._data = tests
        self.endResetModel()


def _dlg_lang(parent) -> str:
    return getattr(parent, "_lang", get_language()) if parent else get_language()


class CreateLabTestDialog(QDialog):
    def __init__(self, db: Database, parent=None, appointment_id: Optional[int] = None):
        super().__init__(parent)
        self._db = db
        self._lang = _dlg_lang(parent)
        self._preselect_appt_id = appointment_id
        self.setMinimumWidth(480)
        self.setStyleSheet(f"background: {PALETTE['surface']}; border-radius: 10px;")

        self._build_ui()
        self._retranslate()
        self._load_appointments()

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _retranslate(self) -> None:
        self.setWindowTitle(self._t("lab.dlg.create_title"))
        self._ttl.setText(self._t("lab.dlg.create_hdr"))
        self._lbl_appt.setText(self._t("lab.dlg.appt"))
        self._lbl_preset.setText(self._t("lab.dlg.preset"))
        self._lbl_name.setText(self._t("lab.dlg.name"))
        self._lbl_price.setText(self._t("lab.dlg.price"))
        self.inp_name.setPlaceholderText(self._t("lab.dlg.name_ph"))
        self.btn_cancel.setText(self._t("lab.dlg.cancel"))
        self.btn_save.setText(self._t("lab.dlg.save"))
        presets = [
            self._t("lab.dlg.preset_placeholder"),
            self._t("lab.preset.blood_panel"),
            self._t("lab.preset.blood"),
            self._t("lab.preset.xray"),
            self._t("lab.preset.mri"),
            self._t("lab.preset.ultrasound"),
            self._t("lab.preset.urine"),
            self._t("lab.preset.custom"),
        ]
        cur = self.cmb_presets.currentIndex()
        self.cmb_presets.blockSignals(True)
        self.cmb_presets.clear()
        self.cmb_presets.addItems(presets)
        if 0 <= cur < self.cmb_presets.count():
            self.cmb_presets.setCurrentIndex(cur)
        self.cmb_presets.blockSignals(False)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self._ttl = QLabel()
        self._ttl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {PALETTE['accent2']};")
        layout.addWidget(self._ttl)
        
        div = QFrame(); div.setFixedHeight(1); div.setStyleSheet(f"background: {PALETTE['border']};")
        layout.addWidget(div)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)
        
        lbl_s = f"color: {PALETTE['text']}; font-weight: bold; font-size: 12px;"
        
        self.cmb_appt = QComboBox()
        self.cmb_appt.setStyleSheet(f"background: {PALETTE['surface2']}; color: #ffffff; padding: 6px; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        
        self.cmb_presets = QComboBox()
        self.cmb_presets.setStyleSheet(f"background: {PALETTE['surface2']}; color: #ffffff; padding: 6px; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        self.cmb_presets.currentIndexChanged.connect(self._on_preset_changed)
        
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Nhập tên xét nghiệm...")
        self.inp_name.setStyleSheet(f"background: {PALETTE['surface2']}; color: #ffffff; padding: 6px; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        
        self.inp_price = QLineEdit()
        self.inp_price.setPlaceholderText("0")
        self.inp_price.setStyleSheet(f"background: {PALETTE['surface2']}; color: #ffffff; padding: 6px; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        
        def add_row(lbl_widget, w):
            form.addRow(lbl_widget, w)

        self._lbl_appt = QLabel(); self._lbl_appt.setStyleSheet(lbl_s)
        self._lbl_preset = QLabel(); self._lbl_preset.setStyleSheet(lbl_s)
        self._lbl_name = QLabel(); self._lbl_name.setStyleSheet(lbl_s)
        self._lbl_price = QLabel(); self._lbl_price.setStyleSheet(lbl_s)
        add_row(self._lbl_appt, self.cmb_appt)
        add_row(self._lbl_preset, self.cmb_presets)
        add_row(self._lbl_name, self.inp_name)
        add_row(self._lbl_price, self.inp_price)
        
        layout.addLayout(form)
        
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(10)
        
        self.btn_cancel = QPushButton()
        self.btn_cancel.setStyleSheet(f"background: {PALETTE['surface2']}; color: {PALETTE['text']}; padding: 8px 16px; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton()
        self.btn_save.setStyleSheet(f"background: {PALETTE['accent']}; color: #ffffff; padding: 8px 16px; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_save.clicked.connect(self._on_save)
        
        btn_lay.addStretch()
        btn_lay.addWidget(self.btn_cancel)
        btn_lay.addWidget(self.btn_save)
        layout.addLayout(btn_lay)
        
    def _load_appointments(self):
        self.cmb_appt.clear()
        rows = self._db.get_appointments_for_lab_orders()
        if not rows:
            self.cmb_appt.addItem(self._t("lab.dlg.no_appt"), None)
            self.btn_save.setEnabled(False)
            return

        for row in rows:
            appt_id, p_name, doctor, appt_date, appt_time, _reason, status = row
            label = f"{p_name} — {appt_date} {appt_time} ({doctor}) [{status}]"
            self.cmb_appt.addItem(label, appt_id)

        if self._preselect_appt_id is not None:
            for i in range(self.cmb_appt.count()):
                if self.cmb_appt.itemData(i) == self._preselect_appt_id:
                    self.cmb_appt.setCurrentIndex(i)
                    break
            
    def _on_preset_changed(self, idx):
        if idx == 0:
            self.inp_name.clear()
            self.inp_price.clear()
        elif idx == 1:
            self.inp_name.setText(self._t("lab.name.blood_panel"))
            self.inp_price.setText("200000")
        elif idx == 2:
            self.inp_name.setText(self._t("lab.name.blood"))
            self.inp_price.setText("200000")
        elif idx == 3:
            self.inp_name.setText(self._t("lab.name.xray"))
            self.inp_price.setText("350000")
        elif idx == 4:
            self.inp_name.setText(self._t("lab.name.mri"))
            self.inp_price.setText("1500000")
        elif idx == 5:
            self.inp_name.setText(self._t("lab.name.ultrasound"))
            self.inp_price.setText("300000")
        elif idx == 6:
            self.inp_name.setText(self._t("lab.name.urine"))
            self.inp_price.setText("150000")
        elif idx == 7:
            self.inp_name.clear()
            self.inp_price.setText("0")
            self.inp_name.setFocus()
            
    def _on_save(self):
        appt_id = self.cmb_appt.currentData()
        name = self.inp_name.text().strip()
        price_str = self.inp_price.text().strip()
        
        if not appt_id:
            QMessageBox.warning(self, self._t("msg.error"), self._t("lab.err.select_appt"))
            return
        if not name:
            QMessageBox.warning(self, self._t("msg.error"), self._t("lab.err.name"))
            return

        try:
            price = float(price_str) if price_str else 0.0
        except ValueError:
            QMessageBox.warning(self, self._t("msg.error"), self._t("lab.err.price"))
            return

        test = LabTest(appointment_id=appt_id, test_name=name, price=price, status="Pending", result_file="")
        self._db.add_lab_test(test)
        QMessageBox.information(self, self._t("msg.success"), self._t("lab.success.created", name=name))
        self.accept()


class UpdateLabTestDialog(QDialog):
    def __init__(self, db: Database, test_row: tuple, parent=None):
        super().__init__(parent)
        self._db = db
        self._test_id = test_row[0]
        self._patient_name = test_row[1]
        self._doctor_name = test_row[2]
        self._test_name = test_row[3]
        self._price = test_row[4]
        self._status = test_row[5]
        self._result_file = test_row[6]
        self._appt_id = test_row[8]
        
        self.setWindowTitle(f"Cập nhật Kết quả Xét nghiệm - LAB-{self._test_id:04d}")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background: {PALETTE['surface']}; border-radius: 10px;")
        
        self._build_ui()
        self._load_data()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)
        
        ttl = QLabel(f"🧪  Kết quả Xét nghiệm: LAB-{self._test_id:04d}")
        ttl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {PALETTE['accent2']};")
        layout.addWidget(ttl)
        
        div = QFrame(); div.setFixedHeight(1); div.setStyleSheet(f"background: {PALETTE['border']};")
        layout.addWidget(div)
        
        card = QFrame()
        card.setStyleSheet(f"background: {PALETTE['surface2']}; border-radius: 6px; padding: 12px;")
        card_lay = QGridLayout(card)
        card_lay.setSpacing(8)
        
        lbl_s = f"color: {PALETTE['text_dim']}; font-size: 12px; font-weight: bold;"
        val_s = f"color: {PALETTE['text']}; font-size: 12px; font-weight: bold;"
        
        def add_meta(r, col, l_txt, v_txt):
            l = QLabel(l_txt); l.setStyleSheet(lbl_s)
            v = QLabel(v_txt); v.setStyleSheet(val_s)
            card_lay.addWidget(l, r, col*2)
            card_lay.addWidget(v, r, col*2+1)
            
        add_meta(0, 0, "Bệnh nhân:", self._patient_name)
        add_meta(0, 1, "Bác sĩ chỉ định:", self._doctor_name)
        add_meta(1, 0, "Tên xét nghiệm:", self._test_name)
        add_meta(1, 1, "Chi phí:", f"{self._price:,.0f} VNĐ")
        
        layout.addWidget(card)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Pending", "Processing", "Completed"])
        self.cmb_status.setStyleSheet(f"background: {PALETTE['surface2']}; color: #ffffff; padding: 6px; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        
        file_widget = QWidget()
        file_lay = QHBoxLayout(file_widget)
        file_lay.setContentsMargins(0, 0, 0, 0)
        file_lay.setSpacing(6)
        
        self.inp_file = QLineEdit()
        self.inp_file.setReadOnly(True)
        self.inp_file.setPlaceholderText("Chưa tải file kết quả lên...")
        self.inp_file.setStyleSheet(f"background: {PALETTE['surface2']}; color: {PALETTE['text_dim']}; padding: 6px; border: 1px solid {PALETTE['border']}; border-radius: 4px;")
        
        self.btn_browse = QPushButton("📁 Upload File")
        self.btn_browse.setStyleSheet(f"background: {PALETTE['accent']}; color: #ffffff; padding: 6px 12px; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_browse.clicked.connect(self._on_browse)
        
        file_lay.addWidget(self.inp_file, stretch=3)
        file_lay.addWidget(self.btn_browse, stretch=1)
        
        self.btn_view = QPushButton("👀 Xem kết quả đính kèm")
        self.btn_view.setStyleSheet(f"background: {PALETTE['accent2']}; color: #ffffff; padding: 8px; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_view.clicked.connect(self._on_view_result)
        
        form_lbl_s = f"color: {PALETTE['text']}; font-weight: bold; font-size: 12px;"
        lbl_status = QLabel("Trạng thái:"); lbl_status.setStyleSheet(form_lbl_s)
        lbl_file = QLabel("Tài liệu kết quả (PDF/Ảnh):"); lbl_file.setStyleSheet(form_lbl_s)
        
        form.addRow(lbl_status, self.cmb_status)
        form.addRow(lbl_file, file_widget)
        
        layout.addLayout(form)
        layout.addWidget(self.btn_view)
        
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(10)
        
        self.btn_cancel = QPushButton("Hủy bỏ")
        self.btn_cancel.setStyleSheet(f"background: {PALETTE['surface2']}; color: {PALETTE['text']}; padding: 8px 16px; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("💾 Cập nhật")
        self.btn_save.setStyleSheet(f"background: {PALETTE['accent']}; color: #ffffff; padding: 8px 16px; border: none; border-radius: 4px; font-weight: bold;")
        self.btn_save.clicked.connect(self._on_save)
        
        btn_lay.addStretch()
        btn_lay.addWidget(self.btn_cancel)
        btn_lay.addWidget(self.btn_save)
        layout.addLayout(btn_lay)
        
    def _load_data(self):
        self.cmb_status.setCurrentText(self._status)
        self.inp_file.setText(self._result_file)
        self.btn_view.setVisible(bool(self._result_file))
        
    def _on_browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Chọn file kết quả (PDF, X-Ray Image, Blood test)", 
            "", 
            "Medical Files (*.pdf *.png *.jpg *.jpeg)"
        )
        if not path: return
        
        import shutil
        os.makedirs("uploads", exist_ok=True)
        dest_filename = f"lab_{self._test_id}_{os.path.basename(path)}"
        dest_path = os.path.join("uploads", dest_filename)
        try:
            shutil.copy2(path, dest_path)
            self._result_file = dest_path
            self.inp_file.setText(self._result_file)
            self.btn_view.setVisible(True)
            self.cmb_status.setCurrentText("Completed")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể copy file: {str(e)}")
            
    def _on_view_result(self):
        if not self._result_file or not os.path.exists(self._result_file):
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file kết quả!")
            return
            
        ext = os.path.splitext(self._result_file.lower())[1]
        if ext in (".png", ".jpg", ".jpeg"):
            dlg = QDialog(self)
            dlg.setWindowTitle(f"Kết quả hình ảnh - LAB-{self._test_id:04d}")
            dlg.setMinimumSize(600, 600)
            v_lay = QVBoxLayout(dlg)
            
            lbl_img = QLabel()
            from PySide6.QtGui import QPixmap
            pix = QPixmap(self._result_file)
            lbl_img.setPixmap(pix.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            lbl_img.setAlignment(Qt.AlignCenter)
            v_lay.addWidget(lbl_img)
            
            dlg.exec()
        else:
            import os
            try:
                os.startfile(os.path.abspath(self._result_file))
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể mở file bằng chương trình mặc định: {str(e)}")
                
    def _on_save(self):
        status = self.cmb_status.currentText()
        test = LabTest(
            appointment_id=self._appt_id,
            test_name=self._test_name,
            price=self._price,
            status=status,
            result_file=self._result_file,
            id=self._test_id
        )
        self._db.update_lab_test(test)
        QMessageBox.information(self, "Thành công", "Đã cập nhật trạng thái xét nghiệm thành công!")
        self.accept()

