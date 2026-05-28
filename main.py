"""
main.py  –  Entry point for Hospital Patient Management System
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from database import Database
from i18n import load_language
from ui_login import LoginWindow
from ui_main import MainWindow


def main() -> None:
    load_language()
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Hospital PMS")
    app.setOrganizationName("HealthTech")
    app.setFont(QFont("Segoe UI", 10))

    db = Database()

    # ── Show login window first ────────────────────────────────────────── #
    login = LoginWindow(db)
    screen = app.primaryScreen().availableGeometry()
    login.move(
        screen.center().x() - login.width() // 2,
        screen.center().y() - login.height() // 2,
    )

    if login.exec() != LoginWindow.Accepted or login.doctor is None:
        sys.exit(0)

    # ── Open main app with authenticated doctor ────────────────────────── #
    window = MainWindow(db, doctor=login.doctor)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
