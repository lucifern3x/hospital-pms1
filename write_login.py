#!/usr/bin/env python3
"""
write_login.py
──────────────
Generates a fresh ui_login.py with:
  • A brand-new LoginWindow (FluidBackground, clean centered card, blue theme)
  • All unchanged classes (DoctorQRDialog, DoctorQRScanDialog,
    ChangePasswordDialog, DoctorManagerDialog, _DoctorFormDialog,
    _ResetPasswordDialog) preserved verbatim from the original.
"""


def main():
    """Write the generated ui_login.py to disk."""
    content = generate_ui_login()
    path = __file__.replace("write_login.py", "ui_login.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("ui_login.py generated successfully.")


def generate_ui_login() -> str:
    """Return the full text of the new ui_login.py."""
    parts = []
    parts.append(_part1_header())
    parts.append(_part2_palette())
    parts.append(_part3_login_style())
    parts.append(_part4_fluid_background())
    parts.append(_part5_login_window())
    parts.append(_part6_unchanged())
    return "\n".join(parts)


def _part1_header() -> str:
    return r'''"""
ui_login.py
───────────
Login screen + Doctor management panel for Hospital PMS.

Classes:
  LoginWindow          – modern frameless login dialog with animated fluid background
  ChangePasswordDialog – for logged-in doctor to change own password
  DoctorManagerDialog  – Admin-only: full CRUD for doctor accounts
"""
from __future__ import annotations

import math
import time
from typing import Optional

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QEvent, Signal
from PySide6.QtGui import (
    QFont, QColor, QPainter, QLinearGradient, QBrush, QPen, QPainterPath,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QAbstractItemView, QSizePolicy, QSpacerItem,
    QGroupBox, QTabWidget, QScrollArea, QGraphicsDropShadowEffect,
)

from database import Database
from i18n import load_language, get_language, set_language, tr, lang_label
from patient import Doctor

DOCTOR_QR_PREFIX = "HOSPITAL-PMS-DOCTOR:"
'''


def _part2_palette() -> str:
    return """\
# ── Shared palette ──────────────────────────────────────────────────────── #
P = {
    "bg":       "#0b1622",
    "surface":  "#111f2e",
    "surface2": "#182838",
    "accent":   "#00c9a7",
    "accent2":  "#0091ff",
    "danger":   "#ff4d6d",
    "warning":  "#ffd166",
    "text":     "#e8f0f7",
    "text_dim": "#6a8ba8",
    "border":   "#1e3448",
    "success":  "#06d6a0",
}

BASE_QSS = f\"\"\"
* {{
    font-family: 'Segoe UI', 'SF Pro Display', Arial;
    font-size: 13px;
    color: {P['text']};
}}
QDialog, QWidget {{ background: transparent; }}
QLineEdit {{
    background: {P['surface2']};
    border: 1.5px solid {P['border']};
    border-radius: 8px;
    padding: 9px 14px;
    color: {P['text']};
    font-size: 13px;
}}
QLineEdit:focus {{ border-color: {P['accent']}; }}
QLineEdit[echoMode=\"2\"] {{ letter-spacing: 3px; }}
QPushButton {{
    background: {P['surface2']};
    border: 1.5px solid {P['border']};
    border-radius: 8px;
    padding: 8px 20px;
    color: {P['text']};
    font-weight: 600;
}}
QPushButton:hover {{ border-color: {P['accent']}; color: {P['accent']}; }}
QPushButton#btn_primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007acc, stop:1 #00c9a7);
    border: none;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
    border-radius: 10px;
}}
QPushButton#btn_primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #006aab, stop:1 #00b390);
    color: #ffffff;
}}
QPushButton#btn_primary:pressed {{ opacity: 0.85; }}
QPushButton#btn_danger {{
    background: transparent;
    border-color: {P['danger']};
    color: {P['danger']};
}}
QPushButton#btn_danger:hover {{ background: {P['danger']}; color: #fff; }}
QPushButton#btn_accent2 {{
    background: transparent;
    border-color: {P['accent2']};
    color: {P['accent2']};
}}
QPushButton#btn_accent2:hover {{ background: {P['accent2']}; color: #fff; }}
QPushButton:disabled {{ opacity: 0.4; }}
QComboBox {{
    background: {P['surface2']};
    border: 1.5px solid {P['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {P['text']};
}}
QComboBox:focus {{ border-color: {P['accent']}; }}
QComboBox QAbstractItemView {{
    background: {P['surface2']};
    border: 1px solid {P['border']};
    selection-background-color: {P['accent']};
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1.5px solid {P['border']};
    border-radius: 4px;
    background: {P['surface2']};
}}
QCheckBox::indicator:checked {{
    background: {P['accent']};
    border-color: {P['accent']};
}}
QTableWidget {{
    background: {P['surface']};
    border: 1px solid {P['border']};
    border-radius: 8px;
    gridline-color: {P['border']};
    alternate-background-color: {P['surface2']};
}}
QTableWidget::item {{ padding: 6px 10px; }}
QTableWidget::item:selected {{ background: #00403a; color: {P['accent']}; }}
QHeaderView::section {{
    background: {P['surface2']};
    color: {P['accent']};
    font-weight: 700;
    font-size: 11px;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid {P['accent']};
    letter-spacing: 0.5px;
}}
QScrollBar:vertical {{
    background: {P['surface']};
    width: 7px;
}}
QScrollBar::handle:vertical {{
    background: {P['border']};
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{ background: {P['accent']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QTabWidget::pane {{
    border: 1px solid {P['border']};
    border-radius: 8px;
    background: {P['surface']};
}}
QTabBar::tab {{
    background: {P['surface2']};
    color: {P['text_dim']};
    padding: 9px 22px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background: {P['surface']};
    color: {P['accent']};
    border-bottom: 2px solid {P['accent']};
}}
QGroupBox {{
    border: 1px solid {P['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px; top: -6px;
    color: {P['accent']};
    background: {P['surface']};
    padding: 0 6px;
    font-weight: 700;
    font-size: 12px;
}}
\"\"\"""


def _part3_login_style() -> str:
    return """\
# ── LOGIN_STYLE: blue themed CSS for login form ───────────────────────── #
LOGIN_STYLE = f\"\"\"
QLineEdit#login_field {{
    background: rgba(10, 20, 40, 0.55);
    border: 1.5px solid rgba(70, 130, 220, 0.45);
    border-radius: 10px;
    padding: 10px 14px;
    color: #f0f6ff;
    font-size: 14px;
    selection-background-color: #007acc;
}}
QLineEdit#login_field:focus {{
    border: 2px solid #3b8be8;
    background: rgba(8, 18, 36, 0.65);
}}
QLineEdit#login_field::placeholder {{
    color: rgba(200, 220, 255, 0.4);
}}
QLineEdit#pw_field {{
    background: rgba(10, 20, 40, 0.55);
    border: 1.5px solid rgba(70, 130, 220, 0.45);
    border-radius: 10px;
    padding: 10px 14px;
    color: #f0f6ff;
    font-size: 14px;
    selection-background-color: #007acc;
}}
QLineEdit#pw_field:focus {{
    border: 2px solid #3b8be8;
    background: rgba(8, 18, 36, 0.65);
}}
QLineEdit#pw_field::placeholder {{
    color: rgba(200, 220, 255, 0.4);
}}
QPushButton#login_btn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0a5db8, stop:1 #1e90ff);
    border: none;
    border-radius: 10px;
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 12px 20px;
}}
QPushButton#login_btn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0e6ed0, stop:1 #3a9fff);
}}
QPushButton#login_btn:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #084d9e, stop:1 #1878e0);
}}
QPushButton#qr_btn {{
    background: rgba(255, 255, 255, 0.06);
    border: 1.5px solid rgba(70, 130, 220, 0.50);
    border-radius: 10px;
    color: #7abfff;
    font-size: 13px;
    font-weight: 600;
    padding: 10px 16px;
}}
QPushButton#qr_btn:hover {{
    background: rgba(30, 100, 200, 0.18);
    border-color: #3b8be8;
    color: #b0d4ff;
}}
QCheckBox#remember_cb {{
    color: rgba(200, 220, 255, 0.65);
    font-size: 12px;
    spacing: 8px;
}}
QCheckBox#remember_cb::indicator {{
    width: 16px; height: 16px;
    border: 1.5px solid rgba(70, 130, 220, 0.50);
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.25);
}}
QCheckBox#remember_cb::indicator:checked {{
    background: #1e90ff;
    border-color: #1e90ff;
}}
QPushButton#top_btn {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(200, 220, 255, 0.12);
    border-radius: 8px;
    color: rgba(200, 220, 255, 0.55);
    font-size: 13px;
    padding: 6px 12px;
}}
QPushButton#top_btn:hover {{
    background: rgba(200, 220, 255, 0.08);
    border-color: rgba(200, 220, 255, 0.25);
    color: #b0d4ff;
}}
QPushButton#close_btn {{
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(200, 220, 255, 0.12);
    border-radius: 8px;
    color: rgba(200, 220, 255, 0.55);
    font-size: 14px;
    padding: 4px 10px;
}}
QPushButton#close_btn:hover {{
    background: #e04050;
    border-color: #e04050;
    color: #ffffff;
}}
\"\"\""""


def _part4_fluid_background() -> str:
    return r"""# ══════════════════════════════════════════════════════════════════════════════
#  FLUID BACKGROUND  (animated blue blob background)
# ══════════════════════════════════════════════════════════════════════════════

class FluidBackground(QWidget):
    """Animated blue blob background using math.sin / cos."""
 