#!/usr/bin/env python3
"""rebuild.py - Completely rewrite write_login.py with all 6 parts + __main__ guard."""

import sys


def main():
    """Write the complete write_login.py to disk."""
    content = generate_content()
    path = r"D:\hospital_pms\hospital_pms\write_login.py"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("write_login.py rewritten successfully.")


def generate_content() -> str:
    parts = []
    parts.append(_part1_header())
    parts.append(_part2_palette())
    parts.append(_part3_login_style())
    parts.append(_part4_fluid_background())
    parts.append(_part5_login_window())
    parts.append(_part6_unchanged())
    return "
".join(parts)


def _part1_header() -> str:
    return r'''"""
ui_login.py
-----------
Login screen + Doctor management panel for Hospital PMS.

Classes:
  LoginWindow          - modern frameless login dialog with animated fluid background
  ChangePasswordDialog - for logged-in doctor to change own password
  DoctorManagerDialog  - Admin-only: full CRUD for doctor accounts
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

