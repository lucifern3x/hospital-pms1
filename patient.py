"""
patient.py - Patient data model
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Patient:
    """Represents a patient record."""
    full_name: str
    dob: str                        # ISO format: YYYY-MM-DD
    gender: str                     # "Male" | "Female" | "Other"
    phone: str
    email: str = ""
    address: str = ""
    blood_type: str = ""            # A+, B-, O+, AB+, etc.
    allergies: str = ""
    notes: str = ""
    id: Optional[int] = field(default=None, repr=False)

    # ------------------------------------------------------------------ #
    #  Computed helpers                                                     #
    # ------------------------------------------------------------------ #
    @property
    def age(self) -> int:
        try:
            born = date.fromisoformat(self.dob)
            today = date.today()
            return today.year - born.year - (
                (today.month, today.day) < (born.month, born.day)
            )
        except ValueError:
            return 0

    @property
    def display_dob(self) -> str:
        """Return DOB as DD/MM/YYYY for display."""
        try:
            d = date.fromisoformat(self.dob)
            return d.strftime("%d/%m/%Y")
        except ValueError:
            return self.dob

    @property
    def active_diagnosis(self) -> str:
        """Return diagnosis stored in patient notes, if present."""
        for line in (self.notes or "").splitlines():
            if line.startswith(("Diagnosis:", "Bệnh lý:", "Chẩn đoán:", "Benh ly:")):
                return line.split(":", 1)[1].strip()
        return ""

    @property
    def display_notes(self) -> str:
        """Return notes without the embedded diagnosis metadata line."""
        clean_notes = []
        for line in (self.notes or "").splitlines():
            if line.startswith(("Diagnosis:", "Bệnh lý:", "Chẩn đoán:", "Benh ly:")):
                continue
            clean_notes.append(line)
        return "\n".join(clean_notes).strip()

    # ------------------------------------------------------------------ #
    #  Serialisation helpers                                                #
    # ------------------------------------------------------------------ #
    def to_tuple(self) -> tuple:
        """Return fields in DB column order (excluding id)."""
        return (
            self.full_name,
            self.dob,
            self.gender,
            self.phone,
            self.email,
            self.address,
            self.blood_type,
            self.allergies,
            self.notes,
        )

    @classmethod
    def from_row(cls, row: tuple) -> "Patient":
        """Create a Patient from a DB row tuple."""
        (pid, full_name, dob, gender, phone,
         email, address, blood_type, allergies, notes) = row
        return cls(
            id=pid,
            full_name=full_name,
            dob=dob,
            gender=gender,
            phone=phone,
            email=email,
            address=address,
            blood_type=blood_type,
            allergies=allergies,
            notes=notes,
        )

    def __str__(self) -> str:
        return f"Patient({self.id}: {self.full_name}, {self.age}y)"


@dataclass
class Doctor:
    """Represents a doctor / staff account."""
    username: str
    full_name: str
    specialty: str = ""
    role: str = "Doctor"          # "Admin" | "Doctor"
    is_active: bool = True
    id: Optional[int] = field(default=None, repr=False)

    @classmethod
    def from_row(cls, row: tuple) -> "Doctor":
        did, username, full_name, specialty, role, is_active = row
        return cls(
            id=did,
            username=username,
            full_name=full_name,
            specialty=specialty,
            role=role,
            is_active=bool(is_active),
        )

    def __str__(self) -> str:
        return f"Doctor({self.id}: {self.full_name} [{self.role}])"


@dataclass
class Appointment:
    """Represents a scheduled appointment."""
    patient_id: int
    doctor: str
    appointment_date: str   # YYYY-MM-DD
    appointment_time: str   # HH:MM
    reason: str = ""
    status: str = "Scheduled"   # Scheduled | Completed | Cancelled
    id: Optional[int] = field(default=None, repr=False)

    @classmethod
    def from_row(cls, row: tuple) -> "Appointment":
        (aid, patient_id, doctor, appt_date,
         appt_time, reason, status) = row
        return cls(
            id=aid,
            patient_id=patient_id,
            doctor=doctor,
            appointment_date=appt_date,
            appointment_time=appt_time,
            reason=reason,
            status=status,
        )


@dataclass
class Medication:
    """Represents a medication or service in the system."""
    name: str
    price: float
    description: str = ""
    id: Optional[int] = field(default=None, repr=False)

    def to_tuple(self) -> tuple:
        return (self.name, self.price, self.description)

    @classmethod
    def from_row(cls, row: tuple) -> "Medication":
        mid, name, price, description = row
        return cls(id=mid, name=name, price=price, description=description)


@dataclass
class PrescriptionItem:
    """Represents an item within a prescription."""
    medication_id: int
    quantity: int
    price_at_time: float
    id: Optional[int] = field(default=None, repr=False)
    prescription_id: Optional[int] = field(default=None, repr=False)

    @classmethod
    def from_row(cls, row: tuple) -> "PrescriptionItem":
        iid, pid, mid, qty, price = row
        return cls(
            id=iid,
            prescription_id=pid,
            medication_id=mid,
            quantity=qty,
            price_at_time=price
        )


@dataclass
class Prescription:
    """Represents a bill/prescription for an appointment."""
    appointment_id: int
    notes: str = ""
    id: Optional[int] = field(default=None, repr=False)
    items: list[PrescriptionItem] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: tuple) -> "Prescription":
        pid, appt_id, notes = row
        return cls(id=pid, appointment_id=appt_id, notes=notes)


@dataclass
class MedicalRecord:
    """Structured clinical record for a single appointment visit."""
    appointment_id: int
    symptoms: str = ""
    diagnosis: str = ""
    lab_results: str = ""
    clinical_notes: str = ""
    id: Optional[int] = field(default=None, repr=False)
    created_at: str = ""

    @classmethod
    def from_row(cls, row: tuple) -> "MedicalRecord":
        rid, appt_id, symptoms, diagnosis, lab_results, clinical_notes, created_at = row
        return cls(
            id=rid,
            appointment_id=appt_id,
            symptoms=symptoms,
            diagnosis=diagnosis,
            lab_results=lab_results,
            clinical_notes=clinical_notes,
            created_at=created_at,
        )


@dataclass
class Payment:
    """Tracks payment for an appointment."""
    appointment_id: int
    amount: float
    method: str = "Cash"           # "Cash" | "Bank Transfer"
    status: str = "Pending"        # "Pending" | "Paid" | "Waived"
    reference_no: str = ""         # bank transfer reference
    paid_at: str = ""
    id: Optional[int] = field(default=None, repr=False)

    @classmethod
    def from_row(cls, row: tuple) -> "Payment":
        pid, appt_id, amount, method, status, reference_no, paid_at = row
        return cls(
            id=pid,
            appointment_id=appt_id,
            amount=amount,
            method=method,
            status=status,
            reference_no=reference_no,
            paid_at=paid_at,
        )


@dataclass
class LabTest:
    """Represents a laboratory test order."""
    appointment_id: int
    test_name: str
    price: float
    status: str = "Pending"        # "Pending" | "Processing" | "Completed"
    result_file: str = ""          # file path (PDF or Image)
    created_at: str = ""
    id: Optional[int] = field(default=None, repr=False)

    @classmethod
    def from_row(cls, row: tuple) -> "LabTest":
        lid, appt_id, name, price, status, file, created = row
        return cls(
            id=lid,
            appointment_id=appt_id,
            test_name=name,
            price=price,
            status=status,
            result_file=file,
            created_at=created
        )
