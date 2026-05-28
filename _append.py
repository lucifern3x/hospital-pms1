import sys
sys.stdout.reconfigure(encoding='utf-8')
path = r"D:\hospital_pms\hospital_pms\rebuild.py"

# Part 6 remaining content (DoctorQRScanDialog, ChangePasswordDialog, DoctorManagerDialog, etc.)
# and __main__ guard

part6_rest = r"""
class DoctorQRScanDialog(QDialog):
    scanned_username = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quet QR dang nhap bac si")
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
    def _build_ui(self):
        vl = QVBoxLayout(self)
        vl.setContentsMargins(16, 16, 16, 16)
        vl.setSpacing(12)
        title = QLabel("\U0001f4f7  Quet QR dang nhap bac si")
        title.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {P['accent']};")
        vl.addWidget(title)
        self.cam_view = QLabel("Dang ket noi webcam...")
        self.cam_view.setFixedSize(500, 340)
        self.cam_view.setAlignment(Qt.AlignCenter)
        self.cam_view.setStyleSheet(f"background: {P['surface']}; border: 2px solid {P['border']}; border-radius: 8px;")
        vl.addWidget(self.cam_view, alignment=Qt.AlignCenter)
        row = QHBoxLayout()
        row.addWidget(QLabel("Dua QR bac si vao khung camera."))
        row.addStretch()
        btn_cancel = QPushButton("Huy")
        btn_cancel.clicked.connect(self.reject)
        row.addWidget(btn_cancel)
        vl.addLayout(row)
    def _init_camera(self):
        if not self._cv2:
            self.cam_view.setText("Khong the tai OpenCV de quet QR.")
            return
        self._cap = self._cv2.VideoCapture(0)
        if not self._cap.isOpened():
            self.cam_view.setText("Khong tim thay webcam.")
            return
        self._timer.start(30)
    def _update_frame(self):
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

class ChangePasswordDialog(QDialog):
    def __init__(self, db, doctor, parent=None):
        super().__init__(parent)
        self._db = db
        self._doctor = doctor
        self.setWindowTitle("Doi mat khau")
        self.setFixedWidth(400)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['surface']}; border-radius: 12px; }}")
        self._build_ui()
    def _build_ui(self):
        vl = QVBoxLayout(self)
        vl.setContentsMargins(28, 28, 28, 28)
        vl.setSpacing(14)
        ttl = QLabel("\U0001f511  Doi mat khau")
        ttl.setStyleSheet(f"font-size: 17px; font-weight: 700; color: {P['accent']};")
        vl.addWidget(ttl)
        sub = QLabel(f"Tai khoan: <b>{self._doctor.username}</b>")
        sub.setStyleSheet(f"font-size: 12px; color: {P['text_dim']};")
        vl.addWidget(sub)
        form = QFormLayout(); form.setSpacing(10)
        lbl_s = f"color:{P['text_dim']}; font-weight:600; font-size:12px;"
        def lbl(t): l = QLabel(t); l.setStyleSheet(lbl_s); return l
        self._old  = QLineEdit(); self._old.setEchoMode(QLineEdit.Password)
        self._old.setPlaceholderText("Mat khau hien tai")
        self._new1 = QLineEdit(); self._new1.setEchoMode(QLineEdit.Password)
        self._new1.setPlaceholderText("Mat khau moi (>= 6 ky tu)")
        self._new2 = QLineEdit(); self._new2.setEchoMode(QLineEdit.Password)
        self._new2.setPlaceholderText("Nhap lai mat khau moi")
        form.addRow(lbl("Mat khau cu"), self._old)
        form.addRow(lbl("Mat khau moi"), self._new1)
        form.addRow(lbl("Xac nhan"), self._new2)
        vl.addLayout(form)
        self._err = QLabel("")
        self._err.setStyleSheet(f"color:{P['danger']}; font-size:12px;")
        self._err.setWordWrap(True)
        self._err.setVisible(False)
        vl.addWidget(self._err)
        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Huy"); bc.setFixedWidth(90); bc.clicked.connect(self.reject)
        bs = QPushButton("\U0001f4be  Luu"); bs.setObjectName("btn_primary")
        bs.setFixedWidth(110); bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        vl.addLayout(btn_row)
    def _save(self):
        old = self._old.text()
        new1 = self._new1.text()
        new2 = self._new2.text()
        if not old or not new1:
            self._show_err("Vui long dien day du thong tin."); return
        if len(new1) < 6:
            self._show_err("Mat khau moi phai co it nhat 6 ky tu."); return
        if new1 != new2:
            self._show_err("Mat khau moi khong khop."); return
        ok = self._db.change_own_password(self._doctor.id, old, new1)
        if ok:
            QMessageBox.information(self, "Thanh cong", "\U00002705  Da doi mat khau thanh cong!")
            self.accept()
        else:
            self._show_err("\U0000274c  Mat khau cu khong dung.")
    def _show_err(self, msg):
        self._err.setText(msg); self._err.setVisible(True)

class DoctorManagerDialog(QDialog):
    def __init__(self, db, current_doctor, parent=None):
        super().__init__(parent)
        self._db = db
        self._current = current_doctor
        self.setWindowTitle("Quan ly tai khoan bac si")
        self.setMinimumSize(820, 560)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['bg']}; }}")
        self._build_ui()
        self._load_doctors()
    def _build_ui(self):
        vl = QVBoxLayout(self)
        vl.setContentsMargins(20, 20, 20, 20)
        vl.setSpacing(14)
        hdr = QHBoxLayout()
        ttl = QLabel("\U0001f468\u200d\u2695\ufe0f  Quan ly tai khoan bac si")
        ttl.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {P['text']};")
        hdr.addWidget(ttl); hdr.addStretch()
        vl.addLayout(hdr)
        tabs = QTabWidget()
        tabs.addTab(self._build_accounts_tab(), "\U0001f465  Tai khoan")
        tabs.addTab(self._build_log_tab(),      "\U0001f4cb  Lich su dang nhap")
        vl.addWidget(tabs)
    def _build_accounts_tab(self):
        w = QWidget(); w.setStyleSheet(f"background: {P['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(12, 12, 12, 12); vl.setSpacing(10)
        tb = QHBoxLayout()
        self._btn_add_doc  = QPushButton("\U00002795  Them bac si")
        self._btn_add_doc.setObjectName("btn_primary"); self._btn_add_doc.setFixedHeight(34)
        self._btn_edit_doc = QPushButton("\U0000270f\ufe0f  Sua")
        self._btn_edit_doc.setObjectName("btn_accent2"); self._btn_edit_doc.setFixedHeight(34)
        self._btn_reset_pw = QPushButton("\U0001f511  Reset mat khau")
        self._btn_reset_pw.setFixedHeight(34)
        self._btn_qr_doc = QPushButton("\U0001f4f1  QR dang nhap")
        self._btn_qr_doc.setObjectName("btn_accent2"); self._btn_qr_doc.setFixedHeight(34)
        self._btn_del_doc  = QPushButton("\U0001f5d1  Xoa")
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
        self._doc_table = QTableWidget()
        self._doc_table.setColumnCount(6)
        self._doc_table.setHorizontalHeaderLabels(["ID", "Username", "Ho ten", "Chuyen khoa", "Vai tro", "Trang thai"])
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
        self._btn_add_doc.clicked.connect(self._on_add_doc)
        self._btn_edit_doc.clicked.connect(self._on_edit_doc)
        self._btn_reset_pw.clicked.connect(self._on_reset_pw)
        self._btn_qr_doc.clicked.connect(self._on_show_doctor_qr)
        self._btn_del_doc.clicked.connect(self._on_del_doc)
        return w
    def _build_log_tab(self):
        w = QWidget(); w.setStyleSheet(f"background: {P['bg']};")
        vl = QVBoxLayout(w); vl.setContentsMargins(12, 12, 12, 12); vl.setSpacing(10)
        tb = QHBoxLayout()
        btn_refresh = QPushButton("\U0001f504  Lam moi"); btn_refresh.setFixedHeight(34)
        btn_refresh.clicked.connect(self._load_log)
        tb.addWidget(btn_refresh); tb.addStretch()
        vl.addLayout(tb)
        self._log_table = QTableWidget()
        self._log_table.setColumnCount(4)
        self._log_table.setHorizontalHeaderLabels(["Thoi gian", "Username", "Ho ten", "Ket qua"])
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
    def _load_doctors(self):
        self._doctors = self._db.get_all_doctors()
        self._doc_table.setRowCount(0)
        for doc in self._doctors:
            r = self._doc_table.rowCount()
            self._doc_table.insertRow(r)
            vals = [str(doc.id), doc.username, doc.full_name, doc.specialty, doc.role, "\U00002705 Hoat dong" if doc.is_active else "\U000026d4 Bi khoa"]
            colors = [None, None, None, None, P["accent2"] if doc.role == "Admin" else P["accent"], P["success"] if doc.is_active else P["danger"]]
            for col, (val, color) in enumerate(zip(vals, colors)):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if color:
                    item.setForeground(QColor(color))
                self._doc_table.setItem(r, col, item)
    def _load_log(self):
        rows = self._db.get_login_log(100)
        self._log_table.setRowCount(0)
        for logged_at, username, full_name, success in rows:
            r = self._log_table.rowCount()
            self._log_table.insertRow(r)
            result_text = "\U00002705 Thanh cong" if success else "\U0000274c That bai"
            result_color = P["success"] if success else P["danger"]
            items = [logged_at, username, full_name or "—", result_text]
            for col, val in enumerate(items):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col == 3:
                    item.setForeground(QColor(result_color))
                self._log_table.setItem(r, col, item)
    def _selected_doctor(self):
        row = self._doc_table.currentRow()
        if row < 0 or row >= len(self._doctors):
            return None
        return self._doctors[row]
    def _on_doc_select(self):
        has = self._doc_table.currentRow() >= 0
        self._btn_edit_doc.setEnabled(has)
        self._btn_reset_pw.setEnabled(has)
        self._btn_qr_doc.setEnabled(has)
        doc = self._selected_doctor()
        can_del = has and doc and doc.id != self._current.id
        self._btn_del_doc.setEnabled(can_del)
    def _on_add_doc(self):
        dlg = _DoctorFormDialog(self)
        if dlg.exec() == QDialog.Accepted:
            doc, pw = dlg.get_data()
            self._db.add_doctor(doc, pw)
            self._load_doctors()
    def _on_edit_doc(self):
        doc = self._selected_doctor()
        if not doc: return
        dlg = _DoctorFormDialog(self, doctor=doc)
        if dlg.exec() == QDialog.Accepted:
            updated, _ = dlg.get_data()
            updated.id = doc.id
            self._db.update_doctor(updated)
            self._load_doctors()
    def _on_reset_pw(self):
        doc = self._selected_doctor()
        if not doc: return
        dlg = _ResetPasswordDialog(doc.full_name, self)
        if dlg.exec() == QDialog.Accepted:
            self._db.reset_doctor_password(doc.id, dlg.new_password)
            QMessageBox.information(self, "Thanh cong", f"\U00002705  Da reset mat khau cho <b>{doc.full_name}</b>.")
    def _on_show_doctor_qr(self):
        doc = self._selected_doctor()
        if not doc: return
        DoctorQRDialog(doc, self).exec()
    def _on_del_doc(self):
        doc = self._selected_doctor()
        if not doc: return
        reply = QMessageBox.question(self, "Xac nhan xoa", f"Xoa tai khoan <b>{doc.full_name}</b> ({doc.username})?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._db.delete_doctor(doc.id)
            self._load_doctors()

class _DoctorFormDialog(QDialog):
    def __init__(self, parent=None, doctor=None):
        super().__init__(parent)
        self._doctor = doctor
        self.setWindowTitle("Sua tai khoan" if doctor else "Them bac si moi")
        self.setFixedWidth(420)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['surface']}; }}")
        self._build_ui()
        if doctor:
            self._populate(doctor)
    def _build_ui(self):
        vl = QVBoxLayout(self)
        vl.setContentsMargins(24, 24, 24, 24); vl.setSpacing(14)
        mode = "\U0000270f\ufe0f  Sua tai khoan" if self._doctor else "\U00002795  Them bac si moi"
        ttl = QLabel(mode)
        ttl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {P['accent']};")
        vl.addWidget(ttl)
        form = QFormLayout(); form.setSpacing(10)
        ls = f"color:{P['text_dim']}; font-weight:600; font-size:12px;"
        def lbl(t): l = QLabel(t); l.setStyleSheet(ls); return l
        self._inp_user  = QLineEdit(); self._inp_user.setPlaceholderText("vd: drminh")
        self._inp_name  = QLineEdit(); self._inp_name.setPlaceholderText("Ho va ten day du")
        self._inp_spec  = QLineEdit(); self._inp_spec.setPlaceholderText("vd: Noi khoa")
        self._cmb_role  = QComboBox(); self._cmb_role.addItems(["Doctor", "Admin"])
        self._chk_active = QCheckBox("Tai khoan dang hoat dong")
        self._chk_active.setChecked(True)
        form.addRow(lbl("Username *"), self._inp_user)
        form.addRow(lbl("Ho ten *"),   self._inp_name)
        form.addRow(lbl("Chuyen khoa"), self._inp_spec)
        form.addRow(lbl("Vai tro"),    self._cmb_role)
        form.addRow(lbl(""),           self._chk_active)
        if not self._doctor:
            self._inp_pw  = QLineEdit(); self._inp_pw.setEchoMode(QLineEdit.Password)
            self._inp_pw.setPlaceholderText("Mat khau (>= 6 ky tu)")
            self._inp_pw2 = QLineEdit(); self._inp_pw2.setEchoMode(QLineEdit.Password)
            self._inp_pw2.setPlaceholderText("Nhap lai mat khau")
            form.addRow(lbl("Mat khau *"),  self._inp_pw)
            form.addRow(lbl("Xac nhan *"),  self._inp_pw2)
        else:
            self._inp_user.setEnabled(False)
        vl.addLayout(form)
        self._err = QLabel(""); self._err.setStyleSheet(f"color:{P['danger']}; font-size:12px;")
        self._err.setWordWrap(True); self._err.setVisible(False)
        vl.addWidget(self._err)
        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Huy"); bc.setFixedWidth(90); bc.clicked.connect(self.reject)
        bs = QPushButton("\U0001f4be  Luu"); bs.setObjectName("btn_primary")
        bs.setFixedWidth(110); bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        vl.addLayout(btn_row)
    def _populate(self, doc):
        self._inp_user.setText(doc.username)
        self._inp_name.setText(doc.full_name)
        self._inp_spec.setText(doc.specialty)
        self._cmb_role.setCurrentText(doc.role)
        self._chk_active.setChecked(doc.is_active)
    def _save(self):
        name = self._inp_name.text().strip()
        user = self._inp_user.text().strip()
        if not name or not user:
            self._err.setText("Vui long dien Username va Ho ten.")
            self._err.setVisible(True); return
        if not self._doctor:
            pw1 = self._inp_pw.text()
            pw2 = self._inp_pw2.text()
            if len(pw1) < 6:
                self._err.setText("Mat khau phai co it nhat 6 ky tu.")
                self._err.setVisible(True); return
            if pw1 != pw2:
                self._err.setText("Mat khau khong khop.")
                self._err.setVisible(True); return
        self.accept()
    def get_data(self):
        pw = self._inp_pw.text() if not self._doctor else ""
        doc = Doctor(username=self._inp_user.text().strip(), full_name=self._inp_name.text().strip(), specialty=self._inp_spec.text().strip(), role=self._cmb_role.currentText(), is_active=self._chk_active.isChecked())
        return doc, pw

class _ResetPasswordDialog(QDialog):
    def __init__(self, doctor_name, parent=None):
        super().__init__(parent)
        self.new_password = ""
        self.setWindowTitle("Reset mat khau")
        self.setFixedWidth(360)
        self.setStyleSheet(BASE_QSS + f"QDialog {{ background: {P['surface']}; }}")
        vl = QVBoxLayout(self)
        vl.setContentsMargins(24, 24, 24, 24); vl.setSpacing(12)
        ttl = QLabel(f"\U0001f511  Reset mat khau cho\n<b>{doctor_name}</b>")
        ttl.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {P['text']};")
        ttl.setWordWrap(True)
        vl.addWidget(ttl)
        ls = f"color:{P['text_dim']}; font-weight:600; font-size:12px;"
        vl.addWidget(QLabel("Mat khau moi (>= 6 ky tu):"))
        self._pw1 = QLineEdit(); self._pw1.setEchoMode(QLineEdit.Password)
        vl.addWidget(self._pw1)
        vl.addWidget(QLabel("Xac nhan:"))
        self._pw2 = QLineEdit(); self._pw2.setEchoMode(QLineEdit.Password)
        vl.addWidget(self._pw2)
        self._err = QLabel(""); self._err.setStyleSheet(f"color:{P['danger']}; font-size:12px;")
        self._err.setVisible(False); vl.addWidget(self._err)
        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Huy"); bc.setFixedWidth(80); bc.clicked.connect(self.reject)
        bs = QPushButton("Luu"); bs.setObjectName("btn_primary")
        bs.setFixedWidth(100); bs.clicked.connect(self._save)
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        vl.addLayout(btn_row)
    def _save(self):
        pw1 = self._pw1.text(); pw2 = self._pw2.text()
        if len(pw1) < 6:
            self._err.setText("Mat khau phai >= 6 ky tu."); self._err.setVisible(True); return
        if pw1 != pw2:
            self._err.setText("Mat khau khong khop."); self._err.setVisible(True); return
        self.new_password = pw1
        self.accept()
'''

if __name__ == "__main__":
    main()
"""

with open(path, 'a', encoding='utf-8') as f:
    f.write(part6_rest)
    f.write('\n')
print(f'Appended part6 rest + __main__')
