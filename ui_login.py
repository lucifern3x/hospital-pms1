"""
ui_login.py
───────────
Login screen + Doctor management panel for Hospital PMS.

Classes:
  LoginWindow          – full-screen styled login dialog
  ChangePasswordDialog – for logged-in doctor to change own password
  DoctorManagerDialog  – Admin-only: full CRUD for doctor accounts
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QEvent, Signal
from PySide6.QtGui import (
    QFont, QColor, QPainter, QLinearGradient, QBrush, QPen, QPainterPath,
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

BASE_QSS = f"""
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
QLineEdit[echoMode="2"] {{ letter-spacing: 3px; }}
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
"""

# Login screen only — liquid glass + framed inputs (not used in main app)
LOGIN_GLASS_QSS = f"""
QFrame#glass_login_panel {{
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(10, 22, 36, 0.56),
        stop:1 rgba(8, 18, 30, 0.70)
    );
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 0 18px 18px 0;
}}
QLabel#login_small {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    color: rgba(232, 240, 247, 0.58);
    background: transparent;
}}
QLineEdit#login_field {{
    background: rgba(5, 14, 24, 0.56);
    border: 1.5px solid rgba(255, 255, 255, 0.32);
    border-radius: 12px;
    padding: 10px 14px;
    color: #f5f9ff;
    font-size: 14px;
    selection-background-color: {P['accent']};
}}
QLineEdit#login_field:focus {{
    border: 2px solid rgba(0, 201, 167, 0.85);
    background: rgba(6, 16, 30, 0.72);
}}
QLineEdit#login_field::placeholder {{
    color: rgba(232, 240, 247, 0.45);
}}
QFrame#login_pw_frame {{
    background: rgba(5, 14, 24, 0.56);
    border: 1.5px solid rgba(255, 255, 255, 0.32);
    border-radius: 12px;
}}
QFrame#login_pw_frame[focusFrame="true"] {{
    border: 2px solid rgba(0, 201, 167, 0.85);
    background: rgba(6, 16, 30, 0.72);
}}
QLineEdit#login_field_inner {{
    background: transparent;
    border: none;
    padding: 10px 12px;
    color: #f5f9ff;
    font-size: 14px;
}}
QLineEdit#login_field_inner::placeholder {{
    color: rgba(232, 240, 247, 0.45);
}}
QPushButton#login_eye_btn {{
    background: transparent;
    border: none;
    border-left: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 0 11px 11px 0;
    color: rgba(232, 240, 247, 0.82);
    font-size: 15px;
    padding: 0 10px;
}}
QPushButton#login_eye_btn:hover {{
    background: rgba(255, 255, 255, 0.12);
    color: {P['accent']};
}}
QPushButton#login_btn_primary {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0, 122, 204, 0.95), stop:1 rgba(0, 201, 167, 0.95));
    border: 1.5px solid rgba(255, 255, 255, 0.52);
    border-radius: 12px;
    color: #ffffff;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.4px;
    padding: 12px 20px;
}}
QPushButton#login_btn_primary:hover {{
    border: 1.5px solid rgba(255, 255, 255, 0.75);
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0, 140, 220, 1), stop:1 rgba(0, 220, 185, 1));
}}
QPushButton#login_btn_primary:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0, 100, 180, 1), stop:1 rgba(0, 170, 150, 1));
}}
QPushButton#login_btn_secondary {{
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.24);
    border-radius: 11px;
    color: rgba(232, 240, 247, 0.92);
    font-size: 13px;
    font-weight: 600;
    padding: 10px 14px;
}}
QPushButton#login_btn_secondary:hover {{
    background: rgba(255, 255, 255, 0.16);
    border-color: rgba(0, 201, 167, 0.6);
    color: {P['accent']};
}}
QPushButton#login_btn_secondary:pressed {{
    background: rgba(255, 255, 255, 0.18);
}}
QPushButton#login_lang_btn {{
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 10px;
    color: {P['accent2']};
    font-weight: 600;
    padding: 8px 14px;
}}
QPushButton#login_lang_btn:hover {{
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(0, 145, 255, 0.55);
}}
QPushButton#login_link_btn {{
    background: transparent;
    border: none;
    color: rgba(128, 206, 255, 0.95);
    font-size: 12px;
    font-weight: 600;
    padding: 0;
    text-align: right;
}}
QPushButton#login_link_btn:hover {{
    color: {P['accent']};
    text-decoration: underline;
}}
QCheckBox#login_remember {{
    color: rgba(232, 240, 247, 0.72);
    font-size: 12px;
    spacing: 8px;
}}
QCheckBox#login_remember::indicator {{
    width: 16px; height: 16px;
    border: 1.5px solid rgba(255, 255, 255, 0.35);
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.2);
}}
QCheckBox#login_remember::indicator:checked {{
    background: {P['accent']};
    border-color: {P['accent']};
}}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  LIQUID GLASS PANEL (login form — iOS-style)
# ══════════════════════════════════════════════════════════════════════════════

class GlassLoginPanel(QFrame):
    """Frosted-glass panel painted behind the login form."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glass_login_panel")
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(0, 8, -8, -8)
        path = QPainterPath()
        path.addRoundedRect(float(rect.x()), float(rect.y()),
                            float(rect.width()), float(rect.height()), 18, 18)

        # Base glass tint
        grad = QLinearGradient(0, rect.top(), 0, rect.bottom())
        grad.setColorAt(0.0, QColor(255, 255, 255, 52))
        grad.setColorAt(0.35, QColor(255, 255, 255, 22))
        grad.setColorAt(1.0, QColor(255, 255, 255, 10))
        p.fillPath(path, QBrush(grad))

        # Soft inner glow (top-left highlight)
        shine = QLinearGradient(rect.topLeft(), rect.bottomRight())
        shine.setColorAt(0.0, QColor(255, 255, 255, 38))
        shine.setColorAt(0.45, QColor(255, 255, 255, 0))
        p.fillPath(path, QBrush(shine))

        # Outer border
        p.setPen(QPen(QColor(255, 255, 255, 72), 1.2))
        p.drawPath(path)

        # Top edge highlight (liquid glass rim)
        p.setPen(QPen(QColor(255, 255, 255, 110), 1))
        p.drawLine(rect.left() + 24, rect.top() + 1, rect.right() - 24, rect.top() + 1)


# ══════════════════════════════════════════════════════════════════════════════
#  ANIMATED BACKGROUND WIDGET
# ══════════════════════════════════════════════════════════════════════════════

class GradientBackground(QWidget):
    """Premium dark animated gradient background for the login screen."""
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Deep elegant background
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#0a0f18"))
        grad.setColorAt(0.5, QColor("#121b2b"))
        grad.setColorAt(1.0, QColor("#0f1724"))
        painter.fillRect(self.rect(), QBrush(grad))

        # Glowing orbs for a modern feel
        painter.setOpacity(0.4)
        
        # Top-right Teal Glow
        b1 = QBrush(QColor(0, 201, 167, 40)) # accent
        painter.setBrush(b1)
        painter.setPen(Qt.NoPen)
        r = self.height() * 1.2
        painter.drawEllipse(int(self.width() - r*0.5), int(-r*0.4), int(r), int(r))

        # Bottom-left Blue Glow
        b2 = QBrush(QColor(0, 145, 255, 30)) # accent2
        painter.setBrush(b2)
        r2 = self.height() * 1.1
        painter.drawEllipse(int(-r2*0.4), int(self.height() - r2*0.5), int(r2), int(r2))
        
        # Top-left subtle purple glow
        b3 = QBrush(QColor(138, 43, 226, 20))
        painter.setBrush(b3)
        r3 = self.height() * 0.8
        painter.drawEllipse(int(-r3*0.3), int(-r3*0.3), int(r3), int(r3))
        
        painter.end()


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class LoginWindow(QDialog):
    """
    Full-screen styled login window.
    On successful login, self.doctor holds the authenticated Doctor.
    """

    def __init__(self, db: Database) -> None:
        super().__init__()
        self._db = db
        self.doctor: Optional[Doctor] = None
        self._attempts = 0
        self._locked_until = 0
        self._lang = load_language()

        self.setFixedSize(900, 580)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(BASE_QSS + LOGIN_GLASS_QSS)
        self._build_ui()
        self._retranslate_ui()

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _toggle_language(self) -> None:
        self._lang = "en" if self._lang == "vi" else "vi"
        set_language(self._lang)
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        self.setWindowTitle(f"Hospital PMS – {self._t('login.title')}")
        self._login_title.setText(self._t("login.title"))
        self._login_sub.setText(self._t("login.subtitle"))
        self._u_lbl.setText(self._t("login.username_lbl"))
        self._p_lbl.setText(self._t("login.password_lbl"))
        self._inp_user.setPlaceholderText(
            "Nhập tên đăng nhập"
            if self._lang == "vi"
            else "Enter username"
        )
        self._inp_pass.setPlaceholderText(
            "Nhập mật khẩu"
            if self._lang == "vi"
            else "Enter password"
        )
        self._chk_remember.setText(self._t("login.remember"))
        self._btn_forgot.setText(
            "Quên mật khẩu?"
            if self._lang == "vi"
            else "Forgot password?"
        )
        self._btn_login.setText(f"{self._t('login.submit')}  →")
        self._btn_qr_login.setText(
            "📷  Đăng nhập bằng QR"
            if self._lang == "vi"
            else "📷  Sign in with QR"
        )
        self._login_hint.setText(self._t("login.hint"))
        self._left_sub.setText(
            "Hệ thống Quản lý\nBệnh nhân Phòng khám"
            if self._lang == "vi"
            else "Clinic Patient\nManagement System"
        )
        features = [
            ("👥", self._t("login.feature.patients")),
            ("📅", self._t("login.feature.appts")),
            ("📊", self._t("login.feature.stats")),
        ]
        for i, (icon, text) in enumerate(features):
            self._feature_labels[i].setText(text)
            self._feature_icons[i].setText(icon)
        self._btn_lang.setText(lang_label(self._lang))

    # ─── layout ──────────────────────────────────────────────────────────── #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Background
        self._bg = GradientBackground(self)
        self._bg.setGeometry(self.rect())

        # Main layout
        main_layout = QVBoxLayout(self._bg)
        main_layout.setAlignment(Qt.AlignCenter)

        # Floating Card Container
        card = QWidget()
        card.setFixedSize(780, 480)
        card.setStyleSheet("""
            QWidget#login_card {
                background: rgba(12, 22, 36, 0.72);
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 20px;
            }
        """)
        card.setObjectName("login_card")
        
        # Drop Shadow for the card
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 15)
        card.setGraphicsEffect(shadow)

        outer = QHBoxLayout(card)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # LEFT PANEL
        left = self._build_left_panel()
        left.setStyleSheet("background: transparent; border: none;")
        outer.addWidget(left, stretch=5)

        # Divider
        div = QFrame()
        div.setFixedWidth(1)
        div.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255,255,255,0), stop:0.5 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0)); border: none;")
        outer.addWidget(div)

        # RIGHT PANEL — liquid glass login form
        right = self._build_right_panel()
        outer.addWidget(right, stretch=4)
        
        main_layout.addWidget(card)

    def _build_left_panel(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent; border: none;")
        vl = QVBoxLayout(w)
        vl.setContentsMargins(40, 50, 30, 50)
        vl.setSpacing(0)

        # Logo
        logo = QLabel("🏥")
        logo.setStyleSheet("font-size: 52px;")
        vl.addWidget(logo)
        vl.addSpacing(16)

        title = QLabel("Hospital PMS")
        title.setStyleSheet(
            f"font-size: 30px; font-weight: 800; color: {P['accent']}; letter-spacing: -0.5px;")
        vl.addWidget(title)

        self._left_sub = QLabel("Hệ thống Quản lý\nBệnh nhân Phòng khám")
        self._left_sub.setStyleSheet(f"font-size: 15px; color: {P['text_dim']}; line-height: 1.6;")
        vl.addWidget(self._left_sub)
        vl.addSpacing(40)

        self._feature_icons: list[QLabel] = []
        self._feature_labels: list[QLabel] = []
        for icon, text in [("👥", ""), ("📅", ""), ("📊", "")]:
            row = QHBoxLayout(); row.setSpacing(10)
            ic = QLabel(icon); ic.setStyleSheet("font-size: 16px;")
            tx = QLabel(text)
            tx.setStyleSheet(f"font-size: 12px; color: {P['text_dim']};")
            self._feature_icons.append(ic)
            self._feature_labels.append(tx)
            row.addWidget(ic); row.addWidget(tx); row.addStretch()
            vl.addLayout(row)
            vl.addSpacing(8)

        vl.addStretch()

        version = QLabel("v1.0.0  •  © 2025 HealthTech")
        version.setStyleSheet(f"font-size: 10px; color: {P['border']};")
        vl.addWidget(version)
        return w

    def _build_right_panel(self) -> QWidget:
        glass = GlassLoginPanel()
        vl = QVBoxLayout(glass)
        vl.setContentsMargins(32, 28, 36, 34)
        vl.setSpacing(0)

        top_row = QHBoxLayout()
        self._btn_lang = QPushButton()
        self._btn_lang.setObjectName("login_lang_btn")
        self._btn_lang.setFixedHeight(34)
        self._btn_lang.setFixedWidth(128)
        self._btn_lang.setCursor(Qt.PointingHandCursor)
        self._btn_lang.clicked.connect(self._toggle_language)
        top_row.addWidget(self._btn_lang, alignment=Qt.AlignLeft)
        top_row.addStretch()

        self._btn_close = QPushButton("✕")
        self._btn_close.setFixedSize(32, 32)
        self._btn_close.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: {P['text_dim']}; font-size: 14px; border-radius: 8px;
            }}
            QPushButton:hover {{ background: {P['danger']}; color: #fff; border-color: {P['danger']}; }}
        """)
        self._btn_close.clicked.connect(self.reject)
        top_row.addWidget(self._btn_close)
        vl.addLayout(top_row)
        vl.addSpacing(14)

        self._login_title = QLabel("Đăng nhập")
        self._login_title.setStyleSheet(
            "font-size: 31px; font-weight: 800; color: #ffffff; letter-spacing: 0.4px; background: transparent;")
        vl.addWidget(self._login_title)
        vl.addSpacing(3)

        self._login_sub = QLabel("Nhập thông tin tài khoản của bạn")
        self._login_sub.setStyleSheet(
            f"font-size: 12px; color: rgba(232, 240, 247, 0.74); background: transparent;")
        vl.addWidget(self._login_sub)
        vl.addSpacing(22)

        self._u_lbl = QLabel("TÊN ĐĂNG NHẬP")
        self._u_lbl.setObjectName("login_small")
        vl.addWidget(self._u_lbl)
        vl.addSpacing(6)
        self._inp_user = QLineEdit()
        self._inp_user.setObjectName("login_field")
        self._inp_user.setClearButtonEnabled(True)
        self._inp_user.setFixedHeight(46)
        self._inp_user.returnPressed.connect(self._on_login)
        vl.addWidget(self._inp_user)
        vl.addSpacing(12)

        self._p_lbl = QLabel("MẬT KHẨU")
        self._p_lbl.setObjectName("login_small")
        vl.addWidget(self._p_lbl)
        vl.addSpacing(6)

        self._pw_frame = QFrame()
        self._pw_frame.setObjectName("login_pw_frame")
        self._pw_frame.setFixedHeight(46)
        pw_row = QHBoxLayout(self._pw_frame)
        pw_row.setContentsMargins(0, 0, 0, 0)
        pw_row.setSpacing(0)

        self._inp_pass = QLineEdit()
        self._inp_pass.setObjectName("login_field_inner")
        self._inp_pass.setEchoMode(QLineEdit.Password)
        self._inp_pass.returnPressed.connect(self._on_login)

        self._btn_eye = QPushButton("👁")
        self._btn_eye.setObjectName("login_eye_btn")
        self._btn_eye.setFixedSize(46, 46)
        self._btn_eye.setCheckable(True)
        self._btn_eye.toggled.connect(
            lambda on: self._inp_pass.setEchoMode(
                QLineEdit.Normal if on else QLineEdit.Password)
        )
        pw_row.addWidget(self._inp_pass, stretch=1)
        pw_row.addWidget(self._btn_eye)
        vl.addWidget(self._pw_frame)

        self._inp_pass.installEventFilter(self)
        self._pw_frame.installEventFilter(self)

        vl.addSpacing(12)
        options_row = QHBoxLayout()
        options_row.setContentsMargins(0, 0, 0, 0)
        options_row.setSpacing(8)
        self._chk_remember = QCheckBox()
        self._chk_remember.setObjectName("login_remember")
        options_row.addWidget(self._chk_remember)
        options_row.addStretch()
        self._btn_forgot = QPushButton()
        self._btn_forgot.setObjectName("login_link_btn")
        self._btn_forgot.setCursor(Qt.PointingHandCursor)
        self._btn_forgot.clicked.connect(self._on_forgot_password)
        options_row.addWidget(self._btn_forgot)
        vl.addLayout(options_row)
        vl.addSpacing(14)

        self._err_lbl = QLabel("")
        self._err_lbl.setStyleSheet(
            f"color: {P['danger']}; font-size: 12px; font-weight: 600;"
            f"background: rgba(255,77,109,0.14); border: 1px solid rgba(255,77,109,0.35);"
            f"border-radius: 8px; padding: 6px 10px;"
        )
        self._err_lbl.setWordWrap(True)
        self._err_lbl.setVisible(False)
        vl.addWidget(self._err_lbl)
        vl.addSpacing(6)

        self._btn_login = QPushButton()
        self._btn_login.setObjectName("login_btn_primary")
        self._btn_login.setFixedHeight(48)
        self._btn_login.setCursor(Qt.PointingHandCursor)
        self._btn_login.clicked.connect(self._on_login)
        vl.addWidget(self._btn_login)
        vl.addSpacing(10)

        self._btn_qr_login = QPushButton()
        self._btn_qr_login.setObjectName("login_btn_secondary")
        self._btn_qr_login.setFixedHeight(42)
        self._btn_qr_login.setCursor(Qt.PointingHandCursor)
        self._btn_qr_login.clicked.connect(self._on_qr_login)
        vl.addWidget(self._btn_qr_login)
        vl.addSpacing(12)

        self._login_hint = QLabel()
        self._login_hint.setStyleSheet(
            "font-size: 11px; color: rgba(232, 240, 247, 0.60); background: transparent;")
        self._login_hint.setAlignment(Qt.AlignCenter)
        self._login_hint.setWordWrap(True)
        vl.addWidget(self._login_hint)
        vl.addStretch()
        return glass

    def eventFilter(self, obj, event) -> bool:
        if hasattr(self, "_pw_frame") and obj in (self._inp_pass, self._pw_frame):
            if event.type() == QEvent.Type.FocusIn:
                self._pw_frame.setProperty("focusFrame", True)
                self._pw_frame.style().unpolish(self._pw_frame)
                self._pw_frame.style().polish(self._pw_frame)
            elif event.type() == QEvent.Type.FocusOut:
                if not self._inp_pass.hasFocus() and not self._pw_frame.hasFocus():
                    self._pw_frame.setProperty("focusFrame", False)
                    self._pw_frame.style().unpolish(self._pw_frame)
                    self._pw_frame.style().polish(self._pw_frame)
        return super().eventFilter(obj, event)

    # ─── drag to move ────────────────────────────────────────────────────── #
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton and hasattr(self, "_drag_pos"):
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def resizeEvent(self, e):
        self._bg.setGeometry(self.rect())

    # ─── login logic ─────────────────────────────────────────────────────── #
    def _on_login(self) -> None:
        import time
        if self._attempts >= 5:
            remaining = int(self._locked_until - time.time())
            if remaining > 0:
                self._show_error(f"⏳  Quá nhiều lần sai. Vui lòng đợi {remaining}s.")
                return
            else:
                self._attempts = 0

        username = self._inp_user.text().strip()
        password = self._inp_pass.text()

        if not username or not password:
            self._show_error("Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        self._btn_login.setEnabled(False)
        self._btn_login.setText(self._t("login.checking"))

        doctor = self._db.login(username, password)

        if doctor:
            self._err_lbl.setVisible(False)
            self._btn_login.setText(self._t("login.success"))
            self._btn_login.setStyleSheet(
                f"background: {P['success']}; border-color: {P['success']}; color: #0b1622;"
                "border-radius: 10px; font-size: 14px; font-weight: 700;"
            )
            self.doctor = doctor
            QTimer.singleShot(600, self.accept)
        else:
            self._attempts += 1
            if self._attempts >= 5:
                import time
                self._locked_until = time.time() + 30
                self._show_error("⛔  Tài khoản bị khoá tạm thời 30 giây do đăng nhập sai quá nhiều lần.")
            else:
                remaining = 5 - self._attempts
                self._show_error(
                    f"❌  Sai tên đăng nhập hoặc mật khẩu. "
                    f"Còn {remaining} lần thử."
                )
            self._btn_login.setEnabled(True)
            self._btn_login.setText(f"{self._t('login.submit')}  →")
            self._inp_pass.clear()
            self._inp_pass.setFocus()

    def _on_qr_login(self) -> None:
        dlg = DoctorQRScanDialog(self)
        dlg.scanned_username.connect(self._login_with_qr_username)
        dlg.exec()

    def _on_forgot_password(self) -> None:
        if self._lang == "vi":
            QMessageBox.information(
                self,
                "Quên mật khẩu",
                "Vui lòng liên hệ quản trị viên để đặt lại mật khẩu tài khoản bác sĩ.",
            )
        else:
            QMessageBox.information(
                self,
                "Forgot password",
                "Please contact your administrator to reset the doctor account password.",
            )

    def _login_with_qr_username(self, username: str) -> None:
        doctor = self._db.login_with_doctor_qr(username)
        if doctor:
            self._err_lbl.setVisible(False)
            self.doctor = doctor
            self._btn_login.setText(self._t("login.success"))
            QTimer.singleShot(350, self.accept)
        else:
            self._show_error("QR không hợp lệ hoặc tài khoản bác sĩ đã bị khóa.")

    def _show_error(self, msg: str) -> None:
        self._err_lbl.setText(msg)
        self._err_lbl.setVisible(True)


# ══════════════════════════════════════════════════════════════════════════════
#  DOCTOR QR LOGIN DIALOGS
# ══════════════════════════════════════════════════════════════════════════════
class DoctorQRDialog(QDialog):
    def __init__(self, doctor: Doctor, parent=None) -> None:
        super().__init__(parent)
        self._doctor = doctor
        self.setWindowTitle("QR đăng nhập bác sĩ")
        self.setFixedSize(380, 460)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['surface']}; }}")

        vl = QVBoxLayout(self)
        vl.setContentsMargins(24, 24, 24, 24)
        vl.setSpacing(14)

        title = QLabel("📱  QR đăng nhập bác sĩ")
        title.setStyleSheet(f"font-size: 17px; font-weight: 800; color: {P['accent']};")
        title.setAlignment(Qt.AlignCenter)
        vl.addWidget(title)

        name = QLabel(f"<b>{doctor.full_name}</b><br>{doctor.username} · {doctor.role}")
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet(f"font-size: 13px; color: {P['text']};")
        vl.addWidget(name)

        qr_lbl = QLabel()
        qr_lbl.setAlignment(Qt.AlignCenter)
        qr_lbl.setStyleSheet("background: #ffffff; border-radius: 8px; padding: 12px;")
        try:
            from ui_cccd import generate_qr_pixmap
            qr_lbl.setPixmap(generate_qr_pixmap(f"{DOCTOR_QR_PREFIX}{doctor.username}", 240))
        except Exception as exc:
            qr_lbl.setText(f"Không thể tạo QR:\n{exc}")
            qr_lbl.setStyleSheet(f"color: {P['danger']};")
        vl.addWidget(qr_lbl, alignment=Qt.AlignCenter)

        hint = QLabel("Quét mã này ở màn hình đăng nhập để vào hệ thống.")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        hint.setStyleSheet(f"font-size: 12px; color: {P['text_dim']};")
        vl.addWidget(hint)

        btn = QPushButton("Đóng")
        btn.setObjectName("btn_primary")
        btn.clicked.connect(self.accept)
        vl.addWidget(btn)


class DoctorQRScanDialog(QDialog):
    scanned_username = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Quét QR đăng nhập bác sĩ")
        self.setFixedSize(540, 480)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['bg']}; }}")
        self._cap = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)
        self._detected_username = ""
        self._ticks_after_detect = 0
        try:
            import cv2
            self._cv2 = cv2
            self._qr_detector = cv2.QRCodeDetector()
        except Exception:
            self._cv2 = None
            self._qr_detector = None
        self._build_ui()
        self._init_camera()

    def _build_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(16, 16, 16, 16)
        vl.setSpacing(12)
        title = QLabel("📷  Quét QR đăng nhập bác sĩ")
        title.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {P['accent']};")
        vl.addWidget(title)
        self.cam_view = QLabel("Đang kết nối webcam...")
        self.cam_view.setFixedSize(500, 340)
        self.cam_view.setAlignment(Qt.AlignCenter)
        self.cam_view.setStyleSheet(f"background: {P['surface']}; border: 2px solid {P['border']}; border-radius: 8px;")
        vl.addWidget(self.cam_view, alignment=Qt.AlignCenter)
        row = QHBoxLayout()
        row.addWidget(QLabel("Đưa QR bác sĩ vào khung camera."))
        row.addStretch()
        btn_cancel = QPushButton("Hủy")
        btn_cancel.clicked.connect(self.reject)
        row.addWidget(btn_cancel)
        vl.addLayout(row)

    def _init_camera(self) -> None:
        if not self._cv2:
            self.cam_view.setText("Không thể tải OpenCV để quét QR.")
            return
        self._cap = self._cv2.VideoCapture(0)
        if not self._cap.isOpened():
            self.cam_view.setText("Không tìm thấy webcam.")
            return
        self._timer.start(30)

    def _update_frame(self) -> None:
        if not self._cap or not self._cap.isOpened():
            return
        ok, frame = self._cap.read()
        if not ok:
            return
        if self._detected_username:
            self._ticks_after_detect += 1
            if self._ticks_after_detect > 8:
                self.scanned_username.emit(self._detected_username)
                self.accept()
                return
        try:
            data, bbox, _ = self._qr_detector.detectAndDecode(frame)
            if data.startswith(DOCTOR_QR_PREFIX):
                username = data.replace(DOCTOR_QR_PREFIX, "", 1).strip()
                if username:
                    self._detected_username = username
        except Exception:
            pass
        rgb = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        from PySide6.QtGui import QImage, QPixmap
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.cam_view.setPixmap(QPixmap.fromImage(img).scaled(
            self.cam_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def closeEvent(self, event) -> None:
        self._timer.stop()
        if self._cap:
            self._cap.release()
        super().closeEvent(event)

    def reject(self) -> None:
        self._timer.stop()
        if self._cap:
            self._cap.release()
        super().reject()


# ══════════════════════════════════════════════════════════════════════════════
#  CHANGE PASSWORD DIALOG
# ══════════════════════════════════════════════════════════════════════════════
class ChangePasswordDialog(QDialog):
    def __init__(self, db: Database, doctor: Doctor, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._doctor = doctor
        self.setWindowTitle("Đổi mật khẩu")
        self.setFixedWidth(400)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['surface']}; border-radius: 12px; }}")
        self._build_ui()

    def _build_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(28, 28, 28, 28)
        vl.setSpacing(14)

        ttl = QLabel("🔑  Đổi mật khẩu")
        ttl.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {P['accent']};")
        vl.addWidget(ttl)

        sub = QLabel(f"Tài khoản: <b>{self._doctor.username}</b>")
        sub.setStyleSheet(f"font-size: 12px; color: {P['text_dim']};")
        vl.addWidget(sub)

        form = QFormLayout(); form.setSpacing(10)
        lbl_s = f"color:{P['text_dim']}; font-weight:600; font-size:12px;"
        def lbl(t): l = QLabel(t); l.setStyleSheet(lbl_s); return l

        self._old  = QLineEdit(); self._old.setEchoMode(QLineEdit.Password)
        self._old.setPlaceholderText("Mật khẩu hiện tại")
        self._new1 = QLineEdit(); self._new1.setEchoMode(QLineEdit.Password)
        self._new1.setPlaceholderText("Mật khẩu mới (≥ 6 ký tự)")
        self._new2 = QLineEdit(); self._new2.setEchoMode(QLineEdit.Password)
        self._new2.setPlaceholderText("Nhập lại mật khẩu mới")

        form.addRow(lbl("Mật khẩu cũ"), self._old)
        form.addRow(lbl("Mật khẩu mới"), self._new1)
        form.addRow(lbl("Xác nhận"), self._new2)
        vl.addLayout(form)

        self._err = QLabel("")
        self._err.setStyleSheet(f"color:{P['danger']}; font-size:12px;")
        self._err.setWordWrap(True)
        self._err.setVisible(False)
        vl.addWidget(self._err)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Huỷ"); bc.setFixedWidth(90); bc.clicked.connect(self.reject)
        bs = QPushButton("💾  Lưu"); bs.setObjectName("btn_primary")
        bs.setFixedWidth(110); bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        vl.addLayout(btn_row)

    def _save(self) -> None:
        old = self._old.text()
        new1 = self._new1.text()
        new2 = self._new2.text()
        if not old or not new1:
            self._show_err("Vui lòng điền đầy đủ thông tin."); return
        if len(new1) < 6:
            self._show_err("Mật khẩu mới phải có ít nhất 6 ký tự."); return
        if new1 != new2:
            self._show_err("Mật khẩu mới không khớp."); return
        ok = self._db.change_own_password(self._doctor.id, old, new1)
        if ok:
            QMessageBox.information(self, "Thành công", "✅  Đã đổi mật khẩu thành công!")
            self.accept()
        else:
            self._show_err("❌  Mật khẩu cũ không đúng.")

    def _show_err(self, msg: str) -> None:
        self._err.setText(msg); self._err.setVisible(True)


# ══════════════════════════════════════════════════════════════════════════════
#  DOCTOR MANAGER DIALOG  (Admin only)
# ══════════════════════════════════════════════════════════════════════════════
class DoctorManagerDialog(QDialog):
    """Full CRUD for doctor accounts + login audit log."""

    def __init__(self, db: Database, current_doctor: Doctor, parent=None) -> None:
        super().__init__(parent)
        self._db = db
        self._current = current_doctor
        self.setWindowTitle("Quản lý tài khoản bác sĩ")
        self.setMinimumSize(820, 560)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['bg']}; }}")
        self._build_ui()
        self._load_doctors()

    def _build_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(20, 20, 20, 20)
        vl.setSpacing(14)

        # Header
        hdr = QHBoxLayout()
        ttl = QLabel("👨‍⚕️  Quản lý tài khoản bác sĩ")
        ttl.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {P['text']};")
        hdr.addWidget(ttl); hdr.addStretch()
        vl.addLayout(hdr)

        tabs = QTabWidget()
        tabs.addTab(self._build_accounts_tab(), "👥  Tài khoản")
        tabs.addTab(self._build_log_tab(),      "📋  Lịch sử đăng nhập")
        vl.addWidget(tabs)

    # ── Tab 1: accounts ────────────────────────────────────────────────── #
    def _build_accounts_tab(self) -> QWidget:
        w = QWidget(); w.setStyleSheet(f"background: {P['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(12, 12, 12, 12); vl.setSpacing(10)

        # Toolbar
        tb = QHBoxLayout()
        self._btn_add_doc  = QPushButton("➕  Thêm bác sĩ")
        self._btn_add_doc.setObjectName("btn_primary"); self._btn_add_doc.setFixedHeight(34)
        self._btn_edit_doc = QPushButton("✏️  Sửa")
        self._btn_edit_doc.setObjectName("btn_accent2"); self._btn_edit_doc.setFixedHeight(34)
        self._btn_reset_pw = QPushButton("🔑  Reset mật khẩu")
        self._btn_reset_pw.setFixedHeight(34)
        self._btn_qr_doc = QPushButton("📱  QR đăng nhập")
        self._btn_qr_doc.setObjectName("btn_accent2"); self._btn_qr_doc.setFixedHeight(34)
        self._btn_del_doc  = QPushButton("🗑  Xoá")
        self._btn_del_doc.setObjectName("btn_danger"); self._btn_del_doc.setFixedHeight(34)
        for b in (self._btn_edit_doc, self._btn_reset_pw, self._btn_qr_doc, self._btn_del_doc):
            b.setEnabled(False)
        tb.addWidget(self._btn_add_doc)
        tb.addWidget(self._btn_edit_doc)
        tb.addWidget(self._btn_reset_pw)
        tb.addWidget(self._btn_qr_doc)
        tb.addWidget(self._btn_del_doc)
        tb.addStretch()
        vl.addLayout(tb)

        # Table
        self._doc_table = QTableWidget()
        self._doc_table.setColumnCount(6)
        self._doc_table.setHorizontalHeaderLabels(
            ["ID", "Username", "Họ tên", "Chuyên khoa", "Vai trò", "Trạng thái"])
        self._doc_table.setAlternatingRowColors(True)
        self._doc_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._doc_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._doc_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._doc_table.verticalHeader().setVisible(False)
        self._doc_table.setShowGrid(False)
        self._doc_table.verticalHeader().setDefaultSectionSize(34)
        hh = self._doc_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Fixed); self._doc_table.setColumnWidth(0, 44)
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self._doc_table.itemSelectionChanged.connect(self._on_doc_select)
        self._doc_table.doubleClicked.connect(self._on_edit_doc)
        vl.addWidget(self._doc_table)

        # Signals
        self._btn_add_doc.clicked.connect(self._on_add_doc)
        self._btn_edit_doc.clicked.connect(self._on_edit_doc)
        self._btn_reset_pw.clicked.connect(self._on_reset_pw)
        self._btn_qr_doc.clicked.connect(self._on_show_doctor_qr)
        self._btn_del_doc.clicked.connect(self._on_del_doc)
        return w

    # ── Tab 2: log ────────────────────────────────────────────────────── #
    def _build_log_tab(self) -> QWidget:
        w = QWidget(); w.setStyleSheet(f"background: {P['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(12, 12, 12, 12); vl.setSpacing(10)

        tb = QHBoxLayout()
        btn_refresh = QPushButton("🔄  Làm mới"); btn_refresh.setFixedHeight(34)
        btn_refresh.clicked.connect(self._load_log)
        tb.addWidget(btn_refresh); tb.addStretch()
        vl.addLayout(tb)

        self._log_table = QTableWidget()
        self._log_table.setColumnCount(4)
        self._log_table.setHorizontalHeaderLabels(
            ["Thời gian", "Username", "Họ tên", "Kết quả"])
        self._log_table.setAlternatingRowColors(True)
        self._log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._log_table.verticalHeader().setVisible(False)
        self._log_table.setShowGrid(False)
        self._log_table.verticalHeader().setDefaultSectionSize(32)
        lhh = self._log_table.horizontalHeader()
        lhh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        lhh.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        lhh.setSectionResizeMode(2, QHeaderView.Stretch)
        lhh.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        vl.addWidget(self._log_table)
        self._load_log()
        return w

    # ── data ─────────────────────────────────────────────────────────── #
    def _load_doctors(self) -> None:
        self._doctors = self._db.get_all_doctors()
        self._doc_table.setRowCount(0)
        for doc in self._doctors:
            r = self._doc_table.rowCount()
            self._doc_table.insertRow(r)
            vals = [str(doc.id), doc.username, doc.full_name,
                    doc.specialty, doc.role,
                    "✅ Hoạt động" if doc.is_active else "⛔ Bị khoá"]
            colors = [None, None, None, None,
                      P["accent2"] if doc.role == "Admin" else P["accent"],
                      P["success"] if doc.is_active else P["danger"]]
            for col, (val, color) in enumerate(zip(vals, colors)):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if color:
                    item.setForeground(QColor(color))
                self._doc_table.setItem(r, col, item)

    def _load_log(self) -> None:
        rows = self._db.get_login_log(100)
        self._log_table.setRowCount(0)
        for logged_at, username, full_name, success in rows:
            r = self._log_table.rowCount()
            self._log_table.insertRow(r)
            result_text = "✅ Thành công" if success else "❌ Thất bại"
            result_color = P["success"] if success else P["danger"]
            items = [logged_at, username, full_name or "—", result_text]
            for col, val in enumerate(items):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col == 3:
                    item.setForeground(QColor(result_color))
                self._log_table.setItem(r, col, item)

    def _selected_doctor(self) -> Optional[Doctor]:
        row = self._doc_table.currentRow()
        if row < 0 or row >= len(self._doctors):
            return None
        return self._doctors[row]

    def _on_doc_select(self) -> None:
        has = self._doc_table.currentRow() >= 0
        self._btn_edit_doc.setEnabled(has)
        self._btn_reset_pw.setEnabled(has)
        self._btn_qr_doc.setEnabled(has)
        doc = self._selected_doctor()
        # prevent deleting yourself or last admin
        can_del = has and doc and doc.id != self._current.id
        self._btn_del_doc.setEnabled(can_del)

    # ── CRUD slots ────────────────────────────────────────────────────── #
    def _on_add_doc(self) -> None:
        dlg = _DoctorFormDialog(self)
        if dlg.exec() == QDialog.Accepted:
            doc, pw = dlg.get_data()
            self._db.add_doctor(doc, pw)
            self._load_doctors()

    def _on_edit_doc(self) -> None:
        doc = self._selected_doctor()
        if not doc:
            return
        dlg = _DoctorFormDialog(self, doctor=doc)
        if dlg.exec() == QDialog.Accepted:
            updated, _ = dlg.get_data()
            updated.id = doc.id
            self._db.update_doctor(updated)
            self._load_doctors()

    def _on_reset_pw(self) -> None:
        doc = self._selected_doctor()
        if not doc:
            return
        dlg = _ResetPasswordDialog(doc.full_name, self)
        if dlg.exec() == QDialog.Accepted:
            self._db.reset_doctor_password(doc.id, dlg.new_password)
            QMessageBox.information(self, "Thành công",
                f"✅  Đã reset mật khẩu cho <b>{doc.full_name}</b>.")

    def _on_show_doctor_qr(self) -> None:
        doc = self._selected_doctor()
        if not doc:
            return
        DoctorQRDialog(doc, self).exec()

    def _on_del_doc(self) -> None:
        doc = self._selected_doctor()
        if not doc:
            return
        reply = QMessageBox.question(
            self, "Xác nhận xoá",
            f"Xoá tài khoản <b>{doc.full_name}</b> ({doc.username})?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._db.delete_doctor(doc.id)
            self._load_doctors()


# ══════════════════════════════════════════════════════════════════════════════
#  INTERNAL: Doctor form dialog
# ══════════════════════════════════════════════════════════════════════════════
class _DoctorFormDialog(QDialog):
    def __init__(self, parent=None, doctor: Optional[Doctor] = None) -> None:
        super().__init__(parent)
        self._doctor = doctor
        self.setWindowTitle("Sửa tài khoản" if doctor else "Thêm bác sĩ mới")
        self.setFixedWidth(420)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['surface']}; }}")
        self._build_ui()
        if doctor:
            self._populate(doctor)

    def _build_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(24, 24, 24, 24); vl.setSpacing(14)

        mode = "✏️  Sửa tài khoản" if self._doctor else "➕  Thêm bác sĩ mới"
        ttl = QLabel(mode)
        ttl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {P['accent']};")
        vl.addWidget(ttl)

        form = QFormLayout(); form.setSpacing(10)
        ls = f"color:{P['text_dim']}; font-weight:600; font-size:12px;"
        def lbl(t): l = QLabel(t); l.setStyleSheet(ls); return l

        self._inp_user  = QLineEdit(); self._inp_user.setPlaceholderText("vd: drminh")
        self._inp_name  = QLineEdit(); self._inp_name.setPlaceholderText("Họ và tên đầy đủ")
        self._inp_spec  = QLineEdit(); self._inp_spec.setPlaceholderText("vd: Nội khoa")
        self._cmb_role  = QComboBox(); self._cmb_role.addItems(["Doctor", "Admin"])
        self._chk_active = QCheckBox("Tài khoản đang hoạt động")
        self._chk_active.setChecked(True)

        form.addRow(lbl("Username *"), self._inp_user)
        form.addRow(lbl("Họ tên *"),   self._inp_name)
        form.addRow(lbl("Chuyên khoa"), self._inp_spec)
        form.addRow(lbl("Vai trò"),    self._cmb_role)
        form.addRow(lbl(""),           self._chk_active)

        if not self._doctor:
            self._inp_pw  = QLineEdit(); self._inp_pw.setEchoMode(QLineEdit.Password)
            self._inp_pw.setPlaceholderText("Mật khẩu (≥ 6 ký tự)")
            self._inp_pw2 = QLineEdit(); self._inp_pw2.setEchoMode(QLineEdit.Password)
            self._inp_pw2.setPlaceholderText("Nhập lại mật khẩu")
            form.addRow(lbl("Mật khẩu *"),  self._inp_pw)
            form.addRow(lbl("Xác nhận *"),  self._inp_pw2)
        else:
            self._inp_user.setEnabled(False)

        vl.addLayout(form)

        self._err = QLabel(""); self._err.setStyleSheet(f"color:{P['danger']}; font-size:12px;")
        self._err.setWordWrap(True); self._err.setVisible(False)
        vl.addWidget(self._err)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Huỷ"); bc.setFixedWidth(90); bc.clicked.connect(self.reject)
        bs = QPushButton("💾  Lưu"); bs.setObjectName("btn_primary")
        bs.setFixedWidth(110); bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        vl.addLayout(btn_row)

    def _populate(self, doc: Doctor) -> None:
        self._inp_user.setText(doc.username)
        self._inp_name.setText(doc.full_name)
        self._inp_spec.setText(doc.specialty)
        self._cmb_role.setCurrentText(doc.role)
        self._chk_active.setChecked(doc.is_active)

    def _save(self) -> None:
        name = self._inp_name.text().strip()
        user = self._inp_user.text().strip()
        if not name or not user:
            self._err.setText("Vui lòng điền Username và Họ tên.")
            self._err.setVisible(True); return

        if not self._doctor:
            pw1 = self._inp_pw.text()
            pw2 = self._inp_pw2.text()
            if len(pw1) < 6:
                self._err.setText("Mật khẩu phải có ít nhất 6 ký tự.")
                self._err.setVisible(True); return
            if pw1 != pw2:
                self._err.setText("Mật khẩu không khớp.")
                self._err.setVisible(True); return
        self.accept()

    def get_data(self) -> tuple[Doctor, str]:
        pw = self._inp_pw.text() if not self._doctor else ""
        doc = Doctor(
            username=self._inp_user.text().strip(),
            full_name=self._inp_name.text().strip(),
            specialty=self._inp_spec.text().strip(),
            role=self._cmb_role.currentText(),
            is_active=self._chk_active.isChecked(),
        )
        return doc, pw


class _ResetPasswordDialog(QDialog):
    def __init__(self, doctor_name: str, parent=None) -> None:
        super().__init__(parent)
        self.new_password = ""
        self.setWindowTitle("Reset mật khẩu")
        self.setFixedWidth(360)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['surface']}; }}")
        vl = QVBoxLayout(self)
        vl.setContentsMargins(24, 24, 24, 24); vl.setSpacing(12)

        ttl = QLabel(f"🔑  Reset mật khẩu cho\n<b>{doctor_name}</b>")
        ttl.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {P['text']};")
        ttl.setWordWrap(True)
        vl.addWidget(ttl)

        ls = f"color:{P['text_dim']}; font-weight:600; font-size:12px;"
        vl.addWidget(QLabel("Mật khẩu mới (≥ 6 ký tự):").setStyleSheet(ls) or QLabel("Mật khẩu mới (≥ 6 ký tự):"))
        self._pw1 = QLineEdit(); self._pw1.setEchoMode(QLineEdit.Password)
        vl.addWidget(self._pw1)
        vl.addWidget(QLabel("Xác nhận:").setStyleSheet(ls) or QLabel("Xác nhận:"))
        self._pw2 = QLineEdit(); self._pw2.setEchoMode(QLineEdit.Password)
        vl.addWidget(self._pw2)

        self._err = QLabel(""); self._err.setStyleSheet(f"color:{P['danger']}; font-size:12px;")
        self._err.setVisible(False); vl.addWidget(self._err)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Huỷ"); bc.setFixedWidth(80); bc.clicked.connect(self.reject)
        bs = QPushButton("Lưu"); bs.setObjectName("btn_primary")
        bs.setFixedWidth(100); bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        vl.addLayout(btn_row)

    def _save(self) -> None:
        pw1 = self._pw1.text(); pw2 = self._pw2.text()
        if len(pw1) < 6:
            self._err.setText("Mật khẩu phải ≥ 6 ký tự."); self._err.setVisible(True); return
        if pw1 != pw2:
            self._err.setText("Mật khẩu không khớp."); self._err.setVisible(True); return
        self.new_password = pw1
        self.accept()
