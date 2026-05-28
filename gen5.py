import sys

# Read the file
with open('D:\\hospital_pms\\hospital_pms\\write_login.py', 'r', encoding='utf-8') as f:
    content = f.read()
lines = content.split('\n')

# Keep only first 404 lines
base = '\n'.join(lines[:404])

# Now add _part5_login_window
# We use regular (non-raw) triple-single-quoted string
# Inside it we embed triple-double-quotes for QSS f-strings

part5 = '''

def _part5_login_window() -> str:
    """Return the LoginWindow class code (triple-single-quote delimited)."""
    return \'\'\'
# LOGIN WINDOW

class LoginWindow(QDialog):
    """Modern frameless login dialog with animated fluid background. Resizable via edge-drag."""

    _MARGIN = 6

    def __init__(self, db: Database) -> None:
        super().__init__()
        self._db = db
        self.doctor: Optional[Doctor] = None
        self._attempts = 0
        self._locked_until = 0.0
        self._lang = load_language()
        self._resizing = False
        self._resize_edge = 0
        self._drag_pos = None

        self.setMinimumSize(560, 520)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(BASE_QSS + LOGIN_STYLE)
        self.setMouseTracking(True)
        self._build_ui()
        self._retranslate_ui()

    def _t(self, key: str, **fmt) -> str:
        return tr(key, self._lang, **fmt)

    def _toggle_language(self) -> None:
        self._lang = "en" if self._lang == "vi" else "vi"
        set_language(self._lang)
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        self.setWindowTitle(f"Hospital PMS - {self._t(\'login.title\')}")
        self._lbl_title.setText(self._t("login.title"))
        self._lbl_subtitle.setText(self._t("login.subtitle"))
        self._login_field.setPlaceholderText(self._t("login.username_lbl"))
        self._pw_field.setPlaceholderText(self._t("login.password_lbl"))
        self._login_btn.setText(self._t("login.submit"))
        self._qr_btn.setText(self._t("login.qr_login"))
        self._hint_label.setText(self._t("login.hint"))
        self._remember_cb.setText(self._t("login.remember"))
        self._top_btn.setText(lang_label(self._lang))
\'\'\'

'''

print(f'Length of base: {len(base)}')
print(f'Length of part5: {len(part5)}')

# Write base + part5
with open('D:\\hospital_pms\\hospital_pms\\write_login.py', 'w', encoding='utf-8') as f:
    f.write(base + part5)
print('Wrote successfully')
