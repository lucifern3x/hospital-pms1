"""
test_hospital.py
────────────────
Unit tests for Hospital PMS core logic.
Tests cover: Patient, Doctor, Appointment, Medication, Prescription models and
all Database CRUD operations using an in-memory SQLite database.
"""

import unittest
import tempfile
import os

from patient import Patient, Doctor, Appointment, Medication, PrescriptionItem, Prescription
from database import Database


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def make_temp_db() -> Database:
    """Create a Database backed by a temporary file (auto-cleaned)."""
    tmp = tempfile.mktemp(suffix=".db")
    db = Database(tmp)
    return db, tmp


# ═══════════════════════════════════════════════════════════════════════════════
#  PATIENT MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestPatientModel(unittest.TestCase):

    def test_age_calculation(self):
        p = Patient(full_name="John Doe", dob="1990-01-01", gender="Male", phone="0900000000")
        self.assertGreater(p.age, 30)

    def test_display_dob(self):
        p = Patient(full_name="Jane Doe", dob="2000-06-15", gender="Female", phone="0911111111")
        self.assertEqual(p.display_dob, "15/06/2000")

    def test_display_dob_invalid(self):
        p = Patient(full_name="Bad DOB", dob="not-a-date", gender="Male", phone="0")
        self.assertEqual(p.display_dob, "not-a-date")

    def test_to_tuple(self):
        p = Patient(full_name="Alice", dob="1995-03-20", gender="Female", phone="0912345678",
                    email="alice@test.com", blood_type="A+")
        t = p.to_tuple()
        # to_tuple order: full_name, dob, gender, phone, email, address, blood_type, allergies, notes
        self.assertEqual(t[0], "Alice")
        self.assertEqual(t[2], "Female")
        self.assertEqual(t[6], "A+")

    def test_from_row(self):
        row = (1, "Bob", "1985-07-04", "Male", "0900000001",
               "bob@test.com", "10 St", "O+", "None", "Healthy")
        p = Patient.from_row(row)
        self.assertEqual(p.id, 1)
        self.assertEqual(p.full_name, "Bob")
        self.assertEqual(p.blood_type, "O+")


# ═══════════════════════════════════════════════════════════════════════════════
#  APPOINTMENT MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestAppointmentModel(unittest.TestCase):

    def test_from_row(self):
        row = (5, 2, "Dr. Smith", "2025-10-01", "09:30", "Checkup", "Scheduled")
        a = Appointment.from_row(row)
        self.assertEqual(a.id, 5)
        self.assertEqual(a.doctor, "Dr. Smith")
        self.assertEqual(a.status, "Scheduled")


# ═══════════════════════════════════════════════════════════════════════════════
#  MEDICATION MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestMedicationModel(unittest.TestCase):

    def test_from_row(self):
        row = (3, "Paracetamol 500mg", 5000.0, "Pain reliever")
        m = Medication.from_row(row)
        self.assertEqual(m.id, 3)
        self.assertEqual(m.price, 5000.0)

    def test_to_tuple(self):
        m = Medication(name="Amoxicillin", price=15000.0, description="Antibiotic")
        self.assertEqual(m.to_tuple(), ("Amoxicillin", 15000.0, "Antibiotic"))


# ═══════════════════════════════════════════════════════════════════════════════
#  DATABASE – PATIENT CRUD
# ═══════════════════════════════════════════════════════════════════════════════
class TestDatabasePatient(unittest.TestCase):

    def setUp(self):
        self.db, self.tmp = make_temp_db()

    def tearDown(self):
        self.db._conn.close()
        os.unlink(self.tmp)

    def _make_patient(self, name="Test Patient", phone="0900000001"):
        return Patient(full_name=name, dob="1990-01-01", gender="Male",
                       phone=phone, email="test@test.com")

    def test_add_and_get_patient(self):
        p = self._make_patient("Alice Test")
        self.db.add_patient(p)
        patients = self.db.get_all_patients()
        names = [pt.full_name for pt in patients]
        self.assertIn("Alice Test", names)

    def test_update_patient(self):
        p = self._make_patient("Before Update")
        self.db.add_patient(p)
        patients = self.db.get_all_patients()
        target = next(pt for pt in patients if pt.full_name == "Before Update")
        target.full_name = "After Update"
        self.db.update_patient(target)
        patients = self.db.get_all_patients()
        names = [pt.full_name for pt in patients]
        self.assertIn("After Update", names)
        self.assertNotIn("Before Update", names)

    def test_delete_patient(self):
        p = self._make_patient("Delete Me")
        self.db.add_patient(p)
        patients = self.db.get_all_patients()
        target = next(pt for pt in patients if pt.full_name == "Delete Me")
        self.db.delete_patient(target.id)
        patients = self.db.get_all_patients()
        names = [pt.full_name for pt in patients]
        self.assertNotIn("Delete Me", names)

    def test_search_patients(self):
        self.db.add_patient(self._make_patient("Nguyen Van An", "0901111111"))
        self.db.add_patient(self._make_patient("Tran Thi Bao", "0902222222"))
        # Search by unique name (seeded data does not contain 'Nguyen Van An')
        results = self.db.search_patients("Nguyen Van An")
        names = [p.full_name for p in results]
        self.assertIn("Nguyen Van An", names)
        # 'Tran Thi Bao' should not appear
        self.assertNotIn("Tran Thi Bao", names)


# ═══════════════════════════════════════════════════════════════════════════════
#  DATABASE – APPOINTMENT CRUD
# ═══════════════════════════════════════════════════════════════════════════════
class TestDatabaseAppointment(unittest.TestCase):

    def setUp(self):
        self.db, self.tmp = make_temp_db()
        # Add a patient to use
        p = Patient(full_name="Appt Patient", dob="1990-01-01",
                    gender="Male", phone="0900000099")
        self.db.add_patient(p)
        self.patient_id = self.db.get_all_patients()[0].id

    def tearDown(self):
        self.db._conn.close()
        os.unlink(self.tmp)

    def _make_appt(self, date="2025-12-01", status="Scheduled"):
        return Appointment(patient_id=self.patient_id, doctor="Dr. Test",
                           appointment_date=date, appointment_time="10:00",
                           reason="Checkup", status=status)

    def test_add_appointment(self):
        self.db.add_appointment(self._make_appt())
        rows = self.db.get_appointments()
        self.assertGreater(len(rows), 0)
        self.assertEqual(rows[0][2], "Dr. Test")  # doctor column

    def test_update_appointment(self):
        self.db.add_appointment(self._make_appt())
        raw = self.db._conn.execute("SELECT * FROM appointments").fetchone()
        appt = Appointment.from_row(tuple(raw))
        appt.status = "Completed"
        appt.reason = "Follow-up"
        self.db.update_appointment(appt)
        raw2 = self.db._conn.execute("SELECT * FROM appointments WHERE id=?", (appt.id,)).fetchone()
        self.assertEqual(raw2[6], "Completed")
        self.assertEqual(raw2[5], "Follow-up")

    def test_delete_appointment(self):
        self.db.add_appointment(self._make_appt())
        before_count = self.db._conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
        # Get the last inserted appointment
        raw = self.db._conn.execute("SELECT id FROM appointments ORDER BY id DESC LIMIT 1").fetchone()
        self.db.delete_appointment(raw[0])
        after_count = self.db._conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
        self.assertEqual(after_count, before_count - 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  DATABASE – MEDICATION CRUD
# ═══════════════════════════════════════════════════════════════════════════════
class TestDatabaseMedication(unittest.TestCase):

    def setUp(self):
        self.db, self.tmp = make_temp_db()

    def tearDown(self):
        self.db._conn.close()
        os.unlink(self.tmp)

    def _make_med(self, name="TestMed", price=10000.0):
        return Medication(name=name, price=price, description="Test description")

    def test_add_and_get_medication(self):
        self.db.add_medication(self._make_med("Paracetamol", 5000.0))
        meds = self.db.get_all_medications()
        # Skip demo data inserted by _seed_demo_data, find ours
        names = [m.name for m in meds]
        self.assertIn("Paracetamol", names)

    def test_update_medication(self):
        self.db.add_medication(self._make_med("OldName", 1000.0))
        meds = self.db.get_all_medications()
        target = next(m for m in meds if m.name == "OldName")
        target.name = "NewName"
        target.price = 9999.0
        self.db.update_medication(target)
        meds = self.db.get_all_medications()
        names = [m.name for m in meds]
        self.assertIn("NewName", names)
        self.assertNotIn("OldName", names)

    def test_delete_medication(self):
        self.db.add_medication(self._make_med("DeleteMe", 500.0))
        meds = self.db.get_all_medications()
        target = next(m for m in meds if m.name == "DeleteMe")
        self.db.delete_medication(target.id)
        meds = self.db.get_all_medications()
        names = [m.name for m in meds]
        self.assertNotIn("DeleteMe", names)

    def test_search_medications(self):
        self.db.add_medication(self._make_med("Amoxicillin 500mg"))
        self.db.add_medication(self._make_med("Ibuprofen 400mg"))
        results = self.db.search_medications("Amoxicillin")
        names = [m.name for m in results]
        self.assertIn("Amoxicillin 500mg", names)
        self.assertNotIn("Ibuprofen 400mg", names)


# ═══════════════════════════════════════════════════════════════════════════════
#  DATABASE – AUTH
# ═══════════════════════════════════════════════════════════════════════════════
class TestDatabaseAuth(unittest.TestCase):

    def setUp(self):
        self.db, self.tmp = make_temp_db()

    def tearDown(self):
        self.db._conn.close()
        os.unlink(self.tmp)

    def test_login_success(self):
        doctor = self.db.login("admin", "admin123")
        self.assertIsNotNone(doctor)
        self.assertEqual(doctor.role, "Admin")

    def test_login_wrong_password(self):
        doctor = self.db.login("admin", "wrongpassword")
        self.assertIsNone(doctor)

    def test_login_unknown_user(self):
        doctor = self.db.login("nobody", "pass")
        self.assertIsNone(doctor)

    def test_doctor_crud(self):
        new_doc = Doctor(username="dr_new", full_name="Dr. Newbie",
                         specialty="Cardiology", role="Doctor")
        self.db.add_doctor(new_doc, "newpass123")
        doctors = self.db.get_all_doctors()
        usernames = [d.username for d in doctors]
        self.assertIn("dr_new", usernames)

        # Login with the new doctor
        logged = self.db.login("dr_new", "newpass123")
        self.assertIsNotNone(logged)
        self.assertEqual(logged.full_name, "Dr. Newbie")


# ═══════════════════════════════════════════════════════════════════════════════
#  DATABASE – PRESCRIPTION
# ═══════════════════════════════════════════════════════════════════════════════
class TestDatabasePrescription(unittest.TestCase):

    def setUp(self):
        self.db, self.tmp = make_temp_db()
        # Ensure a patient and appointment exist
        p = Patient(full_name="Rx Patient", dob="1990-01-01", gender="Female", phone="0900099000")
        self.db.add_patient(p)
        pid = self.db.get_all_patients()[0].id
        a = Appointment(patient_id=pid, doctor="Dr. Rx", appointment_date="2025-01-01",
                        appointment_time="08:00", reason="Test")
        self.db.add_appointment(a)
        raw = self.db._conn.execute("SELECT id FROM appointments").fetchone()
        self.appt_id = raw[0]

        meds = self.db.get_all_medications()
        self.med_id = meds[0].id
        self.med_price = meds[0].price

    def tearDown(self):
        self.db._conn.close()
        os.unlink(self.tmp)

    def test_save_and_load_prescription(self):
        items = [PrescriptionItem(medication_id=self.med_id, quantity=2,
                                  price_at_time=self.med_price)]
        rx = Prescription(appointment_id=self.appt_id, notes="Take after meals", items=items)
        self.db.save_prescription(rx)

        loaded = self.db.get_prescription_by_appointment(self.appt_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.notes, "Take after meals")
        self.assertEqual(len(loaded.items), 1)
        self.assertEqual(loaded.items[0].quantity, 2)


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    unittest.main(verbosity=2)
