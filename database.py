"""
database.py - SQLite database access layer
"""
import hashlib
import os
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from patient import Patient, Appointment, Doctor, Medication, Prescription, PrescriptionItem, MedicalRecord, Payment, LabTest


DB_PATH = Path(__file__).parent / "hospital.db"


class Database:
    """Thread-safe SQLite wrapper for the Hospital PMS."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self._path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self.connect()
        self._create_tables()
        self._seed_demo_data()
        self._ensure_mini_ai_medications()

    # ------------------------------------------------------------------ #
    #  Connection management                                                #
    # ------------------------------------------------------------------ #
    def connect(self) -> None:
        self._conn = sqlite3.connect(
            self._path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("PRAGMA foreign_keys=ON;")

    def close(self) -> None:
        if self._conn:
            self._conn.close()

    @property
    def cursor(self) -> sqlite3.Cursor:
        return self._conn.cursor()

    # ------------------------------------------------------------------ #
    #  Schema                                                               #
    # ------------------------------------------------------------------ #
    # ------------------------------------------------------------------ #
    #  Auth helpers                                                         #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _hash_password(password: str, salt: str = "") -> str:
        if not salt:
            salt = os.urandom(16).hex()
        hashed = hashlib.sha256((salt + password).encode()).hexdigest()
        return f"{salt}:{hashed}"

    @staticmethod
    def _verify_password(password: str, stored: str) -> bool:
        try:
            salt, _ = stored.split(":", 1)
            return stored == Database._hash_password(password, salt)
        except ValueError:
            return False

    def _create_tables(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS doctors (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                full_name   TEXT    NOT NULL,
                specialty   TEXT    DEFAULT '',
                role        TEXT    DEFAULT 'Doctor',
                is_active   INTEGER DEFAULT 1,
                password_hash TEXT  NOT NULL
            );

            CREATE TABLE IF NOT EXISTS login_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id   INTEGER REFERENCES doctors(id),
                username    TEXT NOT NULL,
                success     INTEGER NOT NULL,
                logged_at   TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS patients (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name   TEXT    NOT NULL,
                dob         TEXT    NOT NULL,
                gender      TEXT    NOT NULL,
                phone       TEXT    NOT NULL,
                email       TEXT    DEFAULT '',
                address     TEXT    DEFAULT '',
                blood_type  TEXT    DEFAULT '',
                allergies   TEXT    DEFAULT '',
                notes       TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id       INTEGER NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
                doctor           TEXT    NOT NULL,
                appointment_date TEXT    NOT NULL,
                appointment_time TEXT    NOT NULL,
                reason           TEXT    DEFAULT '',
                status           TEXT    DEFAULT 'Scheduled'
            );

            CREATE TABLE IF NOT EXISTS medications (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                price       REAL    NOT NULL,
                description TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS prescriptions (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
                notes          TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS prescription_items (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id INTEGER NOT NULL REFERENCES prescriptions(id) ON DELETE CASCADE,
                medication_id   INTEGER NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
                quantity        INTEGER NOT NULL,
                price           REAL    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS medical_records (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id  INTEGER NOT NULL UNIQUE REFERENCES appointments(id) ON DELETE CASCADE,
                symptoms        TEXT    DEFAULT '',
                diagnosis       TEXT    DEFAULT '',
                lab_results     TEXT    DEFAULT '',
                clinical_notes  TEXT    DEFAULT '',
                created_at      TEXT    DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS payments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id  INTEGER NOT NULL UNIQUE REFERENCES appointments(id) ON DELETE CASCADE,
                amount          REAL    NOT NULL DEFAULT 0,
                method          TEXT    DEFAULT 'Cash',
                status          TEXT    DEFAULT 'Pending',
                reference_no    TEXT    DEFAULT '',
                paid_at         TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS lab_tests (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id  INTEGER NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
                test_name       TEXT    NOT NULL,
                price           REAL    NOT NULL DEFAULT 0.0,
                status          TEXT    DEFAULT 'Pending',
                result_file     TEXT    DEFAULT '',
                created_at      TEXT    DEFAULT (datetime('now','localtime'))
            );
        """)
        self._conn.commit()

    def _seed_demo_data(self) -> None:
        """Insert sample records only when the DB is empty."""
        # Seed medications
        med_count = self._conn.execute("SELECT COUNT(*) FROM medications").fetchone()[0]
        if med_count == 0:
            demo_meds = [
                ("General Checkup", 150000.0, "General consultation fee"),
                ("Specialist Consultation", 250000.0, "Specialist consultation fee"),
                ("Complete Blood Count", 120000.0, "CBC Blood Test"),
                ("Abdominal Ultrasound", 200000.0, "Full abdominal ultrasound"),
                ("Chest X-Ray", 180000.0, "Standard chest radiography"),
                ("ECG", 150000.0, "Electrocardiogram"),
                ("Paracetamol 500mg", 5000.0, "Pain reliever / Fever reducer (box of 100)"),
                ("Amoxicillin 500mg", 15000.0, "Antibiotic"),
                ("Omeprazole 20mg", 12000.0, "Proton pump inhibitor for GERD"),
                ("Ibuprofen 400mg", 8000.0, "NSAID pain reliever"),
                ("Metformin 500mg", 10000.0, "Anti-diabetic medication"),
                ("Lisinopril 10mg", 14000.0, "ACE inhibitor for high blood pressure"),
                ("Amlodipine 5mg", 11000.0, "Calcium channel blocker"),
                ("Atorvastatin 20mg", 18000.0, "Cholesterol lowering medication"),
                ("Azithromycin 250mg", 22000.0, "Macrolide antibiotic"),
                ("Salbutamol Inhaler", 25000.0, "Bronchodilator for asthma"),
                ("Cetirizine 10mg", 6000.0, "Antihistamine for allergies"),
                ("Loratadine 10mg", 7000.0, "Non-drowsy antihistamine"),
                ("Ciprofloxacin 500mg", 16000.0, "Fluoroquinolone antibiotic"),
                ("Doxycycline 100mg", 12000.0, "Tetracycline antibiotic"),
                ("Fluconazole 150mg", 9000.0, "Antifungal medication"),
                ("Levothyroxine 50mcg", 15000.0, "Thyroid hormone replacement"),
                ("Losartan 50mg", 14000.0, "Angiotensin II receptor blocker"),
                ("Metoprolol 50mg", 11000.0, "Beta blocker"),
                ("Pantoprazole 40mg", 13000.0, "Proton pump inhibitor"),
                ("Prednisone 5mg", 8000.0, "Corticosteroid"),
                ("Simvastatin 20mg", 10000.0, "Cholesterol lowering medication"),
                ("Tramadol 50mg", 18000.0, "Opioid pain medication"),
                ("Aspirin 81mg", 4000.0, "Low-dose aspirin"),
                ("Clopidogrel 75mg", 20000.0, "Antiplatelet medication"),
                ("Gabapentin 300mg", 16000.0, "Nerve pain medication"),
                ("Hydrochlorothiazide 25mg", 7000.0, "Diuretic / water pill"),
                ("Meloxicam 15mg", 12000.0, "NSAID"),
                ("Montelukast 10mg", 19000.0, "Asthma and allergy medication"),
                ("Sertraline 50mg", 15000.0, "SSRI antidepressant"),
                ("Escitalopram 10mg", 18000.0, "SSRI antidepressant"),
                ("Tamsulosin 0.4mg", 22000.0, "Prostate medication"),
                ("Ranitidine 150mg", 9000.0, "H2 blocker for stomach acid"),
                ("Vitamin C 1000mg", 5000.0, "Immune support supplement"),
                ("Vitamin D3 1000 IU", 6000.0, "Bone health supplement"),
                ("Multivitamin Tablets", 15000.0, "Daily multivitamin"),
                ("Iron Supplements 65mg", 10000.0, "Iron deficiency treatment"),
                ("Calcium + D3", 12000.0, "Bone health supplement"),
                ("Glucose Blood Test", 40000.0, "Fasting blood sugar test"),
                ("Lipid Panel Test", 60000.0, "Cholesterol test"),
                ("Liver Function Test", 70000.0, "Hepatic panel"),
                ("Kidney Function Test", 65000.0, "Renal panel"),
                ("Urine Analysis", 25000.0, "Standard urinalysis"),
                ("MRI Scan", 1200000.0, "Magnetic Resonance Imaging"),
                ("CT Scan", 800000.0, "Computed Tomography scan")
            ]
            self._conn.executemany(
                """INSERT INTO medications (name, price, description)
                   VALUES (?,?,?)""",
                demo_meds,
            )
            self._conn.commit()

        # Seed doctors first
        doc_count = self._conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
        if doc_count == 0:
            demo_doctors = [
                ("admin",    "Administrator",  "",              "Admin",  1, self._hash_password("admin123")),
                ("drminh",   "BS. Nguyễn Minh","Nội khoa",     "Doctor", 1, self._hash_password("doctor123")),
                ("drlan",    "BS. Trần Thị Lan","Nhi khoa",    "Doctor", 1, self._hash_password("doctor123")),
                ("drtuan",   "BS. Lê Văn Tuấn","Ngoại khoa",  "Doctor", 1, self._hash_password("doctor123")),
            ]
            self._conn.executemany(
                """INSERT INTO doctors (username, full_name, specialty, role, is_active, password_hash)
                   VALUES (?,?,?,?,?,?)""",
                demo_doctors,
            )
            self._conn.commit()

        count = self._conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        if count > 0:
            return

        demo_patients = [
            ("Alice Nguyen",    "1990-04-15", "Female", "0901234567", "alice@email.com",    "12 Lê Lợi, Đà Nẵng",    "A+",  "Penicillin",  "Hypertension"),
            ("Bob Trần",        "1985-08-22", "Male",   "0912345678", "bob@email.com",      "45 Hùng Vương, TP.HCM",  "B+",  "",            "Diabetes Type 2"),
            ("Carol Lê",        "2000-01-30", "Female", "0923456789", "carol@email.com",    "7 Trần Phú, Hà Nội",     "O-",  "Aspirin",     "Asthma"),
            ("David Phạm",      "1978-11-05", "Male",   "0934567890", "david@email.com",    "88 Nguyễn Huệ, Cần Thơ", "AB+", "",            ""),
            ("Emma Võ",         "1995-06-18", "Female", "0945678901", "emma@email.com",     "23 Bạch Đằng, Đà Nẵng",  "A-",  "Shellfish",   ""),
            ("Frank Đỗ",        "1960-03-12", "Male",   "0956789012", "frank@email.com",    "1 Điện Biên Phủ, Huế",   "O+",  "",            "Chronic back pain"),
            ("Grace Bùi",       "2005-09-25", "Female", "0967890123", "",                   "34 Hai Bà Trưng, Hải Phòng", "B-", "Latex",   ""),
            ("Henry Hoàng",     "1970-07-08", "Male",   "0978901234", "henry@email.com",    "56 Lý Thường Kiệt, HN",  "AB-", "",            "High cholesterol"),
        ]

        self._conn.executemany(
            """INSERT INTO patients
               (full_name, dob, gender, phone, email, address, blood_type, allergies, notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            demo_patients,
        )

        # seed a few appointments
        demo_appts = [
            (1, "Dr. Minh",  "2025-06-10", "09:00", "Annual check-up",       "Scheduled"),
            (2, "Dr. Lan",   "2025-06-11", "10:30", "Diabetes follow-up",    "Scheduled"),
            (3, "Dr. Tuấn",  "2025-06-09", "14:00", "Asthma review",         "Completed"),
            (4, "Dr. Minh",  "2025-06-12", "11:00", "General consultation",  "Scheduled"),
            (5, "Dr. Lan",   "2025-06-08", "08:30", "Blood test review",     "Completed"),
        ]
        self._conn.executemany(
            """INSERT INTO appointments
               (patient_id, doctor, appointment_date, appointment_time, reason, status)
               VALUES (?,?,?,?,?,?)""",
            demo_appts,
        )
        self._conn.commit()

    def _ensure_mini_ai_medications(self) -> None:
        """Add commonly used medications for the offline suggestion helper."""
        meds = [
            ("Oseltamivir 75mg", 32000.0, "Antiviral for influenza"),
            ("Cefuroxime 500mg", 18000.0, "Cephalosporin antibiotic"),
            ("Cefixime 200mg", 17000.0, "Cephalosporin antibiotic"),
            ("Levofloxacin 500mg", 22000.0, "Fluoroquinolone antibiotic"),
            ("Ceftriaxone 1g injection", 45000.0, "Injectable cephalosporin antibiotic"),
            ("Ambroxol 30mg", 7000.0, "Mucolytic for productive cough"),
            ("Dextromethorphan syrup", 25000.0, "Cough suppressant"),
            ("Guaifenesin syrup", 22000.0, "Expectorant"),
            ("Budesonide inhaler", 160000.0, "Inhaled corticosteroid"),
            ("Ipratropium inhaler", 145000.0, "Bronchodilator"),
            ("Oral Rehydration Salts", 5000.0, "Rehydration for diarrhea"),
            ("Loperamide 2mg", 6000.0, "Antidiarrheal"),
            ("Lactulose syrup", 35000.0, "Osmotic laxative"),
            ("Domperidone 10mg", 8000.0, "Antiemetic / prokinetic"),
            ("Simethicone 80mg", 6000.0, "Anti-gas medication"),
            ("Sucralfate 1g", 9000.0, "Gastric mucosal protectant"),
            ("Clotrimazole cream", 28000.0, "Topical antifungal"),
            ("Miconazole cream", 30000.0, "Topical antifungal"),
            ("Hydrocortisone cream 1%", 25000.0, "Topical corticosteroid"),
            ("Benzoyl Peroxide gel", 45000.0, "Acne treatment"),
            ("Adapalene gel", 90000.0, "Topical retinoid for acne"),
            ("Allopurinol 300mg", 12000.0, "Urate-lowering gout medication"),
            ("Colchicine 0.6mg", 15000.0, "Gout flare treatment"),
            ("Diclofenac gel", 35000.0, "Topical NSAID"),
            ("Naproxen 500mg", 10000.0, "NSAID pain reliever"),
            ("Folic Acid 5mg", 5000.0, "Pregnancy / anemia supplement"),
            ("Magnesium B6", 12000.0, "Supplement for cramps and fatigue"),
            ("Melatonin 3mg", 18000.0, "Sleep support"),
            ("Betahistine 16mg", 14000.0, "Vertigo medication"),
            ("Carbamazepine 200mg", 16000.0, "Anticonvulsant"),
        ]
        for name, price, desc in meds:
            exists = self._conn.execute(
                "SELECT 1 FROM medications WHERE lower(name)=lower(?) LIMIT 1",
                (name,),
            ).fetchone()
            if not exists:
                self._conn.execute(
                    "INSERT INTO medications (name, price, description) VALUES (?, ?, ?)",
                    (name, price, desc),
                )
        self._conn.commit()

    # ------------------------------------------------------------------ #
    #  Authentication                                                       #
    # ------------------------------------------------------------------ #
    def login(self, username: str, password: str) -> Optional[Doctor]:
        """Return Doctor on success, None on failure. Logs every attempt."""
        row = self._conn.execute(
            "SELECT id, username, full_name, specialty, role, is_active, password_hash "
            "FROM doctors WHERE username=?", (username.strip(),)
        ).fetchone()

        success = False
        doctor_id = None

        if row:
            doctor_id = row[0]
            is_active = bool(row[5])
            stored_hash = row[6]
            if is_active and self._verify_password(password, stored_hash):
                success = True

        # Log attempt
        self._conn.execute(
            "INSERT INTO login_log (doctor_id, username, success) VALUES (?,?,?)",
            (doctor_id, username.strip(), int(success)),
        )
        self._conn.commit()

        if success:
            return Doctor.from_row(tuple(row[:6]))
        return None

    def login_with_doctor_qr(self, username: str) -> Optional[Doctor]:
        """Return active Doctor for a QR login token and log the attempt."""
        clean_username = username.strip()
        row = self._conn.execute(
            "SELECT id, username, full_name, specialty, role, is_active "
            "FROM doctors WHERE username=?",
            (clean_username,),
        ).fetchone()
        success = bool(row and row[5])
        doctor_id = row[0] if row else None
        self._conn.execute(
            "INSERT INTO login_log (doctor_id, username, success) VALUES (?,?,?)",
            (doctor_id, clean_username, int(success)),
        )
        self._conn.commit()
        return Doctor.from_row(tuple(row)) if success else None

    def get_login_log(self, limit: int = 50) -> List[tuple]:
        rows = self._conn.execute(
            """SELECT ll.logged_at, ll.username, d.full_name,
                      ll.success
               FROM login_log ll
               LEFT JOIN doctors d ON d.id = ll.doctor_id
               ORDER BY ll.id DESC LIMIT ?""", (limit,)
        ).fetchall()
        return [tuple(r) for r in rows]

    # ------------------------------------------------------------------ #
    #  Doctor CRUD                                                          #
    # ------------------------------------------------------------------ #
    def get_all_doctors(self) -> List[Doctor]:
        rows = self._conn.execute(
            "SELECT id, username, full_name, specialty, role, is_active FROM doctors ORDER BY full_name"
        ).fetchall()
        return [Doctor.from_row(tuple(r)) for r in rows]

    def add_doctor(self, doctor: Doctor, password: str) -> int:
        cur = self._conn.execute(
            """INSERT INTO doctors (username, full_name, specialty, role, is_active, password_hash)
               VALUES (?,?,?,?,?,?)""",
            (doctor.username, doctor.full_name, doctor.specialty,
             doctor.role, int(doctor.is_active), self._hash_password(password)),
        )
        self._conn.commit()
        return cur.lastrowid

    def update_doctor(self, doctor: Doctor) -> None:
        self._conn.execute(
            """UPDATE doctors SET full_name=?, specialty=?, role=?, is_active=?
               WHERE id=?""",
            (doctor.full_name, doctor.specialty, doctor.role,
             int(doctor.is_active), doctor.id),
        )
        self._conn.commit()

    def reset_doctor_password(self, doctor_id: int, new_password: str) -> None:
        self._conn.execute(
            "UPDATE doctors SET password_hash=? WHERE id=?",
            (self._hash_password(new_password), doctor_id),
        )
        self._conn.commit()

    def delete_doctor(self, doctor_id: int) -> None:
        self._conn.execute("DELETE FROM doctors WHERE id=?", (doctor_id,))
        self._conn.commit()

    def change_own_password(self, doctor_id: int, old_pw: str, new_pw: str) -> bool:
        row = self._conn.execute(
            "SELECT password_hash FROM doctors WHERE id=?", (doctor_id,)
        ).fetchone()
        if not row or not self._verify_password(old_pw, row[0]):
            return False
        self._conn.execute(
            "UPDATE doctors SET password_hash=? WHERE id=?",
            (self._hash_password(new_pw), doctor_id),
        )
        self._conn.commit()
        return True

    # ------------------------------------------------------------------ #
    #  Patient CRUD                                                         #
    # ------------------------------------------------------------------ #
    def get_all_patients(self) -> List[Patient]:
        rows = self._conn.execute(
            "SELECT * FROM patients ORDER BY full_name"
        ).fetchall()
        return [Patient.from_row(tuple(r)) for r in rows]

    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        row = self._conn.execute(
            "SELECT * FROM patients WHERE id=?", (patient_id,)
        ).fetchone()
        return Patient.from_row(tuple(row)) if row else None

    def search_patients(self, query: str) -> List[Patient]:
        like = f"%{query}%"
        rows = self._conn.execute(
            """SELECT * FROM patients
               WHERE full_name LIKE ? OR phone LIKE ? OR email LIKE ?
               ORDER BY full_name""",
            (like, like, like),
        ).fetchall()
        return [Patient.from_row(tuple(r)) for r in rows]

    def add_patient(self, patient: Patient) -> int:
        cur = self._conn.execute(
            """INSERT INTO patients
               (full_name, dob, gender, phone, email, address, blood_type, allergies, notes)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            patient.to_tuple(),
        )
        self._conn.commit()
        return cur.lastrowid

    def update_patient(self, patient: Patient) -> bool:
        self._conn.execute(
            """UPDATE patients SET
               full_name=?, dob=?, gender=?, phone=?, email=?,
               address=?, blood_type=?, allergies=?, notes=?
               WHERE id=?""",
            (*patient.to_tuple(), patient.id),
        )
        self._conn.commit()
        return True

    def delete_patient(self, patient_id: int) -> bool:
        self._conn.execute("DELETE FROM patients WHERE id=?", (patient_id,))
        self._conn.commit()
        return True

    # ------------------------------------------------------------------ #
    #  Statistics                                                           #
    # ------------------------------------------------------------------ #
    def get_statistics(self) -> Dict[str, Any]:
        total = self._conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
        gender_rows = self._conn.execute(
            "SELECT gender, COUNT(*) FROM patients GROUP BY gender"
        ).fetchall()
        blood_rows = self._conn.execute(
            """SELECT blood_type, COUNT(*) FROM patients
               WHERE blood_type != '' GROUP BY blood_type ORDER BY COUNT(*) DESC"""
        ).fetchall()
        appt_status = self._conn.execute(
            "SELECT status, COUNT(*) FROM appointments GROUP BY status"
        ).fetchall()
        avg_age_row = self._conn.execute(
            """SELECT AVG(
                 (strftime('%Y','now') - strftime('%Y', dob)) -
                 (strftime('%m-%d','now') < strftime('%m-%d', dob))
               ) FROM patients"""
        ).fetchone()
        return {
            "total": total,
            "gender": dict(gender_rows),
            "blood_type": dict(blood_rows),
            "appt_status": dict(appt_status),
            "avg_age": round(avg_age_row[0] or 0, 1),
        }

    # ------------------------------------------------------------------ #
    #  Appointments                                                         #
    # ------------------------------------------------------------------ #
    def update_appointment(self, appt: Appointment) -> None:
        self._conn.execute(
            '''UPDATE appointments 
               SET patient_id=?, doctor=?, appointment_date=?, appointment_time=?, reason=?, status=?
               WHERE id=?''',
            (appt.patient_id, appt.doctor, appt.appointment_date, appt.appointment_time, appt.reason, appt.status, appt.id)
        )
        self._conn.commit()

    def get_appointments(self) -> List[tuple]:
        """Return appointments joined with patient names, excluding paid ones."""
        rows = self._conn.execute(
            """SELECT a.id, p.full_name, a.doctor,
                      a.appointment_date, a.appointment_time,
                      a.reason, a.status
               FROM appointments a
               JOIN patients p ON p.id = a.patient_id
               WHERE a.id NOT IN (SELECT appointment_id FROM payments WHERE status = 'Paid')
               ORDER BY a.appointment_date DESC, a.appointment_time"""
        ).fetchall()
        return [tuple(r) for r in rows]

    def get_appointments_for_lab_orders(self) -> List[tuple]:
        """Return non-cancelled, unpaid appointments for lab order assignment."""
        rows = self._conn.execute(
            """SELECT a.id, p.full_name, a.doctor,
                      a.appointment_date, a.appointment_time,
                      a.reason, a.status
               FROM appointments a
               JOIN patients p ON p.id = a.patient_id
               WHERE a.status != 'Cancelled'
                 AND a.id NOT IN (
                     SELECT appointment_id FROM payments WHERE status = 'Paid'
                 )
               ORDER BY a.appointment_date DESC, a.appointment_time DESC"""
        ).fetchall()
        return [tuple(r) for r in rows]

    def add_appointment(self, appt: Appointment) -> int:
        cur = self._conn.execute(
            """INSERT INTO appointments
               (patient_id, doctor, appointment_date, appointment_time, reason, status)
               VALUES (?,?,?,?,?,?)""",
            (appt.patient_id, appt.doctor, appt.appointment_date,
             appt.appointment_time, appt.reason, appt.status),
        )
        self._conn.commit()
        return cur.lastrowid

    def delete_appointment(self, appt_id: int) -> None:
        self._conn.execute("DELETE FROM appointments WHERE id=?", (appt_id,))
        self._conn.commit()

    def get_patient_names(self) -> List[tuple]:
        """Return [(id, name), ...] for combo-boxes."""
        rows = self._conn.execute(
            "SELECT id, full_name FROM patients ORDER BY full_name"
        ).fetchall()
        return [tuple(r) for r in rows]

    # ------------------------------------------------------------------ #
    #  Medications                                                          #
    # ------------------------------------------------------------------ #
    def get_all_medications(self) -> List[Medication]:
        rows = self._conn.execute("SELECT id, name, price, description FROM medications ORDER BY name").fetchall()
        return [Medication.from_row(tuple(r)) for r in rows]

    def search_medications(self, query: str) -> List[Medication]:
        like = f"%{query}%"
        rows = self._conn.execute(
            "SELECT id, name, price, description FROM medications WHERE name LIKE ? ORDER BY name", (like,)
        ).fetchall()
        return [Medication.from_row(tuple(r)) for r in rows]

    def add_medication(self, med: Medication) -> int:
        cur = self._conn.execute(
            "INSERT INTO medications (name, price, description) VALUES (?, ?, ?)",
            med.to_tuple()
        )
        self._conn.commit()
        return cur.lastrowid

    def update_medication(self, med: Medication) -> None:
        self._conn.execute(
            "UPDATE medications SET name=?, price=?, description=? WHERE id=?",
            (*med.to_tuple(), med.id)
        )
        self._conn.commit()

    def delete_medication(self, med_id: int) -> None:
        self._conn.execute("DELETE FROM medications WHERE id=?", (med_id,))
        self._conn.commit()

    # ------------------------------------------------------------------ #
    #  Prescriptions / Bills                                                #
    # ------------------------------------------------------------------ #
    def get_prescription_by_appointment(self, appt_id: int) -> Optional[Prescription]:
        p_row = self._conn.execute(
            "SELECT id, appointment_id, notes FROM prescriptions WHERE appointment_id=?", (appt_id,)
        ).fetchone()
        
        if not p_row:
            return None
        
        prescription = Prescription.from_row(tuple(p_row))
        
        i_rows = self._conn.execute(
            "SELECT id, prescription_id, medication_id, quantity, price FROM prescription_items WHERE prescription_id=?", 
            (prescription.id,)
        ).fetchall()
        
        prescription.items = [PrescriptionItem.from_row(tuple(r)) for r in i_rows]
        return prescription

    def save_prescription(self, prescription: Prescription) -> int:
        # Delete existing prescription for this appointment if any
        self._conn.execute("DELETE FROM prescriptions WHERE appointment_id=?", (prescription.appointment_id,))
        
        cur = self._conn.execute(
            "INSERT INTO prescriptions (appointment_id, notes) VALUES (?, ?)",
            (prescription.appointment_id, prescription.notes)
        )
        p_id = cur.lastrowid
        
        items_data = [
            (p_id, item.medication_id, item.quantity, item.price_at_time)
            for item in prescription.items
        ]
        self._conn.executemany(
            "INSERT INTO prescription_items (prescription_id, medication_id, quantity, price) VALUES (?, ?, ?, ?)",
            items_data
        )
        self._conn.commit()
        return p_id

    # ------------------------------------------------------------------ #
    #  Medical Records                                                      #
    # ------------------------------------------------------------------ #
    def save_medical_record(self, record: MedicalRecord) -> None:
        self._conn.execute("""
            INSERT INTO medical_records
                (appointment_id, symptoms, diagnosis, lab_results, clinical_notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(appointment_id) DO UPDATE SET
                symptoms       = excluded.symptoms,
                diagnosis      = excluded.diagnosis,
                lab_results    = excluded.lab_results,
                clinical_notes = excluded.clinical_notes,
                created_at     = datetime('now','localtime')
        """, (record.appointment_id, record.symptoms, record.diagnosis,
              record.lab_results, record.clinical_notes))
        self._conn.commit()

    def get_medical_record(self, appointment_id: int) -> Optional[MedicalRecord]:
        row = self._conn.execute(
            "SELECT id, appointment_id, symptoms, diagnosis, lab_results, clinical_notes, created_at "
            "FROM medical_records WHERE appointment_id=?",
            (appointment_id,)
        ).fetchone()
        return MedicalRecord.from_row(tuple(row)) if row else None

    # ------------------------------------------------------------------ #
    #  Payments                                                             #
    # ------------------------------------------------------------------ #
    def save_payment(self, payment: Payment) -> None:
        from datetime import datetime
        paid_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if payment.status == "Paid" else ""
        self._conn.execute("""
            INSERT INTO payments
                (appointment_id, amount, method, status, reference_no, paid_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(appointment_id) DO UPDATE SET
                amount       = excluded.amount,
                method       = excluded.method,
                status       = excluded.status,
                reference_no = excluded.reference_no,
                paid_at      = excluded.paid_at
        """, (payment.appointment_id, payment.amount, payment.method,
              payment.status, payment.reference_no, paid_at))
        self._conn.commit()

    def get_payment(self, appointment_id: int) -> Optional[Payment]:
        row = self._conn.execute(
            "SELECT id, appointment_id, amount, method, status, reference_no, paid_at "
            "FROM payments WHERE appointment_id=?",
            (appointment_id,)
        ).fetchone()
        return Payment.from_row(tuple(row)) if row else None

    # ------------------------------------------------------------------ #
    #  Laboratory Tests                                                  #
    # ------------------------------------------------------------------ #
    def add_lab_test(self, test: LabTest) -> int:
        cur = self._conn.execute(
            """INSERT INTO lab_tests
               (appointment_id, test_name, price, status, result_file)
               VALUES (?, ?, ?, ?, ?)""",
            (test.appointment_id, test.test_name, test.price, test.status, test.result_file)
        )
        self._conn.commit()
        return cur.lastrowid

    def update_lab_test(self, test: LabTest) -> None:
        self._conn.execute(
            """UPDATE lab_tests
               SET test_name=?, price=?, status=?, result_file=?
               WHERE id=?""",
            (test.test_name, test.price, test.status, test.result_file, test.id)
        )
        self._conn.commit()

    def get_lab_tests_by_appointment(self, appt_id: int) -> List[LabTest]:
        rows = self._conn.execute(
            "SELECT id, appointment_id, test_name, price, status, result_file, created_at "
            "FROM lab_tests WHERE appointment_id=?",
            (appt_id,)
        ).fetchall()
        return [LabTest.from_row(tuple(r)) for r in rows]

    def get_all_lab_tests(self) -> List[LabTest]:
        rows = self._conn.execute(
            "SELECT id, appointment_id, test_name, price, status, result_file, created_at "
            "FROM lab_tests ORDER BY id DESC"
        ).fetchall()
        return [LabTest.from_row(tuple(r)) for r in rows]

    def delete_lab_test(self, test_id: int) -> None:
        self._conn.execute("DELETE FROM lab_tests WHERE id=?", (test_id,))
        self._conn.commit()

    def set_lab_test_status(self, test_id: int, status: str) -> None:
        self._conn.execute(
            "UPDATE lab_tests SET status=? WHERE id=?",
            (status, test_id),
        )
        self._conn.commit()

    def get_lab_tests_with_details(self) -> List[tuple]:
        """Return lab tests joined with patient names and doctor names."""
        rows = self._conn.execute(
            """SELECT l.id, pt.full_name, a.doctor, l.test_name, l.price, l.status, l.result_file, l.created_at, l.appointment_id
               FROM lab_tests l
               JOIN appointments a ON a.id = l.appointment_id
               JOIN patients pt ON pt.id = a.patient_id
               ORDER BY l.id DESC"""
        ).fetchall()
        return [tuple(r) for r in rows]

