# 🏥 Hospital Patient Management System

A modern desktop application for managing hospital/clinic patient records, built with **PySide6** and **SQLite**.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-6.6+-green?logo=qt)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Details |
|---|---|
| 👥 **Patient CRUD** | Add, view, edit, delete patient records |
| 🔍 **Search** | Real-time search by name, phone, or email |
| 📅 **Appointments** | Schedule & manage appointments per patient |
| 📊 **Statistics** | Blood-type chart, gender breakdown, appointment status |
| 🗄️ **SQLite** | Lightweight local database with demo data pre-loaded |
| 🎨 **Dark UI** | Polished dark-themed PySide6 interface |

---

## 🗂 Project Structure

```
hospital_pms/
├── main.py          # Entry point
├── ui_main.py       # All PySide6 widgets & dialogs
├── database.py      # SQLite data access layer
├── patient.py       # Patient & Appointment dataclasses
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/hospital-pms.git
cd hospital-pms
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python main.py
```

> **Note:** A `hospital.db` SQLite file will be created automatically on first run, pre-loaded with 8 demo patients and 5 appointments.

---

## 🖥 Screenshots

| Patients | Appointments | Statistics |
|---|---|---|
| Full CRUD table | Schedule & manage | Blood type bar chart |

---

## 🏗 Architecture

```
main.py
  └── MainWindow (ui_main.py)
        ├── Patients Tab   ──► PatientTableModel ──► Database.get_all_patients()
        ├── Appointments Tab ──────────────────────► Database.get_appointments()
        └── Statistics Tab ────────────────────────► Database.get_statistics()

database.py  ──  SQLite wrapper (CRUD + stats queries)
patient.py   ──  Patient & Appointment dataclasses
```

### OOP Design
- **`Patient` / `Appointment`** – `@dataclass` models with computed properties (`age`, `display_dob`) and serialisation helpers (`to_tuple`, `from_row`)
- **`Database`** – Single-responsibility class wrapping all SQLite operations; WAL mode, foreign keys enabled
- **`PatientTableModel`** – Custom `QAbstractTableModel` for efficient Qt table rendering
- **`MainWindow`** – Orchestrates tabs, signals, and calls into `Database`
- **`PatientDialog` / `AppointmentDialog`** – Reusable modal dialogs for Add/Edit

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `PySide6` | ≥ 6.6 | GUI framework (Qt 6 bindings) |
| `sqlite3` | stdlib | Database (no extra install needed) |

---

## 📝 License

MIT © 2025
