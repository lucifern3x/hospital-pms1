"""
i18n.py — Vietnamese / English UI strings for Hospital PMS.
"""
from __future__ import annotations

from PySide6.QtCore import QSettings

ORG = "HealthTech"
APP = "Hospital PMS"
SUPPORTED = ("vi", "en")

_lang: str = "vi"

TEXTS: dict[str, dict[str, str]] = {
    # App
    "app.title": {"vi": "🏥  Hệ thống Quản lý Bệnh viện", "en": "🏥  Hospital Patient Management System"},
    "app.status": {"vi": "Hospital PMS v1.0", "en": "Hospital PMS v1.0"},
    "app.pms": {"vi": " PMS", "en": " PMS"},

    # Navigation
    "nav.patients": {"vi": "Bệnh nhân", "en": "Patients"},
    "nav.appointments": {"vi": "Lịch hẹn", "en": "Appointments"},
    "nav.medications": {"vi": "Thuốc & Dịch vụ", "en": "Medications"},
    "nav.laboratory": {"vi": "Phòng Xét nghiệm", "en": "Laboratory"},
    "nav.statistics": {"vi": "Thống kê", "en": "Statistics"},
    "nav.reports": {"vi": "Báo cáo & Hành trình", "en": "Reports & Journey"},
    "nav.examined": {"vi": "Đã khám", "en": "Examined"},
    "nav.doctor_accounts": {"vi": "Tài khoản Bác sĩ", "en": "Doctor Accounts"},
    "btn.change_password": {"vi": "Đổi mật khẩu", "en": "Change Password"},
    "btn.logout": {"vi": " Đăng xuất", "en": " Logout"},
    "btn.language_vi": {"vi": "🌐 Tiếng Việt", "en": "🌐 Vietnamese"},
    "btn.language_en": {"vi": "🌐 English", "en": "🌐 English"},

    # Patients tab
    "patients.title": {"vi": "Hồ sơ Bệnh nhân", "en": "Patient Records"},
    "patients.add": {"vi": "➕  Thêm", "en": "➕  Add"},
    "patients.edit": {"vi": "✏️  Sửa", "en": "✏️  Edit"},
    "patients.delete": {"vi": "🗑  Xóa", "en": "🗑  Delete"},
    "patients.qr": {"vi": "📱  Mã QR", "en": "📱  QR Code"},
    "patients.scan": {"vi": "📷  Quét QR", "en": "📷  Scan QR"},
    "patients.search": {"vi": "🔍  Tìm bệnh nhân...", "en": "🔍  Search patients..."},
    "patients.showing": {"vi": "Hiển thị {n} bệnh nhân", "en": "Showing {n} patient(s)"},
    "patients.loaded": {"vi": "Đã tải {n} bệnh nhân", "en": "Loaded {n} patients"},

    # Patient dialog
    "patient.dlg.add_title": {"vi": "Thêm bệnh nhân mới", "en": "Add New Patient"},
    "patient.dlg.edit_title": {"vi": "Sửa thông tin bệnh nhân", "en": "Edit Patient"},
    "patient.dlg.add_header": {"vi": "➕  Thêm bệnh nhân mới", "en": "➕  Add New Patient"},
    "patient.dlg.edit_header": {"vi": "✏️  Sửa thông tin bệnh nhân", "en": "✏️  Edit Patient"},
    "patient.dlg.full_name": {"vi": "Họ tên *", "en": "Full Name *"},
    "patient.dlg.dob": {"vi": "Ngày sinh *", "en": "Date of Birth *"},
    "patient.dlg.gender": {"vi": "Giới tính *", "en": "Gender *"},
    "patient.dlg.phone": {"vi": "Điện thoại *", "en": "Phone *"},
    "patient.dlg.email": {"vi": "Email", "en": "Email"},
    "patient.dlg.address": {"vi": "Địa chỉ", "en": "Address"},
    "patient.dlg.blood_type": {"vi": "Nhóm máu", "en": "Blood Type"},
    "patient.dlg.allergies": {"vi": "Dị ứng", "en": "Allergies"},
    "patient.dlg.diagnosis": {"vi": "Bệnh / Chẩn đoán", "en": "Disease / Diagnosis"},
    "patient.dlg.specialty": {"vi": "Chuyên khoa", "en": "Specialty"},
    "patient.dlg.disease": {"vi": "Bệnh", "en": "Disease"},
    "patient.dlg.notes": {"vi": "Ghi chú", "en": "Notes"},
    "patient.dlg.name_ph": {"vi": "Nhập họ tên...", "en": "Full name..."},
    "patient.dlg.phone_ph": {"vi": "Nhập số điện thoại...", "en": "Phone number..."},
    "patient.dlg.email_ph": {"vi": "Nhập email...", "en": "Email address..."},
    "patient.dlg.address_ph": {"vi": "Nhập địa chỉ...", "en": "Street address..."},
    "patient.dlg.allergies_ph": {"vi": "Dị ứng đã biết...", "en": "Known allergies..."},
    "patient.dlg.diagnosis_ph": {"vi": "Chọn bệnh đang điều trị / chẩn đoán trong bảng.", "en": "Select the active disease / diagnosis from the table."},
    "patient.dlg.notes_ph": {"vi": "Ghi chú bổ sung...", "en": "Additional notes..."},
    "patient.dlg.cancel": {"vi": "Hủy", "en": "Cancel"},
    "patient.dlg.save": {"vi": "💾  Lưu", "en": "💾  Save"},
    "patient.dlg.validation_title": {"vi": "Thiếu thông tin", "en": "Validation"},
    "patient.dlg.validation_required": {"vi": "Vui lòng nhập Họ tên và Điện thoại.", "en": "Full Name and Phone are required."},
    "gender.male": {"vi": "Nam", "en": "Male"},
    "gender.female": {"vi": "Nữ", "en": "Female"},
    "gender.other": {"vi": "Khác", "en": "Other"},

    # Patient QR / scanner dialogs
    "qr.card.title": {"vi": "Thẻ QR nhận diện bệnh nhân", "en": "Patient QR Identification Card"},
    "qr.card.header": {"vi": "BỆNH VIỆN ĐA KHOA HOSPITAL PMS", "en": "HOSPITAL PMS GENERAL HOSPITAL"},
    "qr.card.sub": {"vi": "THẺ NHẬN DIỆN BỆNH NHÂN", "en": "PATIENT IDENTIFICATION CARD"},
    "qr.card.name": {"vi": "Bệnh nhân", "en": "Name"},
    "qr.card.patient_id": {"vi": "Mã BN", "en": "Patient ID"},
    "qr.card.dob": {"vi": "Ngày sinh", "en": "DOB"},
    "qr.card.sex": {"vi": "Giới tính", "en": "Sex"},
    "qr.card.phone": {"vi": "Điện thoại", "en": "Phone"},
    "qr.card.footer": {"vi": "Vui lòng xuất trình thẻ này khi đến phòng khám.", "en": "Please present this card at registration."},
    "qr.card.save": {"vi": "💾  Lưu thẻ", "en": "💾  Save Card"},
    "qr.card.print": {"vi": "🖨️  In thẻ", "en": "🖨️  Print Card"},
    "qr.close": {"vi": "Đóng", "en": "Close"},
    "qr.scan.title": {"vi": "Quét mã QR bệnh nhân", "en": "Scan Patient QR Code"},
    "qr.scan.header": {"vi": "📷  Quét mã QR bệnh nhân", "en": "📷  Scan Patient QR Code"},
    "qr.scan.connecting": {"vi": "Đang kết nối webcam...", "en": "Connecting to webcam..."},
    "qr.scan.hint": {"vi": "Đưa thẻ QR bệnh nhân vào trước camera.", "en": "Hold the patient's QR card in front of the camera."},
    "qr.scan.cancel": {"vi": "Hủy", "en": "Cancel"},
    "qr.scan.no_camera": {"vi": "⚠️ Không tìm thấy webcam.\nVui lòng kết nối camera.", "en": "⚠️ Webcam not found.\nPlease connect a camera."},
    "qr.summary.title": {"vi": "🎯 Tóm tắt xác thực QR bệnh nhân", "en": "🎯 Patient QR Scan Verification Summary"},
    "qr.summary.verified": {"vi": "🎯  BỆNH NHÂN ĐÃ ĐƯỢC XÁC THỰC THÀNH CÔNG", "en": "🎯  PATIENT VERIFIED SUCCESSFULLY"},
    "qr.summary.demographics": {"vi": "👤  THÔNG TIN HÀNH CHÍNH", "en": "👤  DEMOGRAPHICS"},
    "qr.summary.appointment": {"vi": "📅  CUỘC HẸN & BÁC SĨ PHỤ TRÁCH", "en": "📅  APPOINTMENT & DOCTOR"},
    "qr.summary.diagnosis": {"vi": "🩺  BỆNH ĐANG ĐIỀU TRỊ & CHẨN ĐOÁN", "en": "🩺  ACTIVE DISEASE & DIAGNOSIS"},
    "qr.summary.billing": {"vi": "💳  CHI PHÍ KHÁM & THANH TOÁN", "en": "💳  BILLING & PAYMENT"},
    "qr.summary.no_photo": {"vi": "CHƯA CÓ\nẢNH", "en": "NO\nPHOTO"},
    "qr.summary.name": {"vi": "Họ tên", "en": "Name"},
    "qr.summary.patient_id": {"vi": "Mã BN", "en": "Patient ID"},
    "qr.summary.dob": {"vi": "Ngày sinh", "en": "DOB"},
    "qr.summary.gender": {"vi": "Giới tính", "en": "Gender"},
    "qr.summary.phone": {"vi": "Điện thoại", "en": "Phone"},
    "qr.summary.address": {"vi": "Địa chỉ", "en": "Address"},
    "qr.summary.blood": {"vi": "Nhóm máu", "en": "Blood Type"},
    "qr.summary.allergies": {"vi": "Dị ứng", "en": "Allergies"},
    "qr.summary.none": {"vi": "Không", "en": "None"},
    "qr.summary.doctor": {"vi": "Bác sĩ khám", "en": "Doctor"},
    "qr.summary.date": {"vi": "Ngày hẹn", "en": "Date"},
    "qr.summary.time": {"vi": "Giờ khám", "en": "Time"},
    "qr.summary.reason": {"vi": "Lý do khám", "en": "Reason"},
    "qr.summary.no_appt": {"vi": "Bệnh nhân chưa có lịch hẹn khám nào được ghi nhận.", "en": "No appointments have been recorded for this patient."},
    "qr.summary.symptoms": {"vi": "Triệu chứng", "en": "Symptoms"},
    "qr.summary.active_diagnosis": {"vi": "Bệnh đang chữa / Chẩn đoán", "en": "Active disease / Diagnosis"},
    "qr.summary.no_symptoms": {"vi": "Chưa ghi nhận", "en": "Not recorded"},
    "qr.summary.no_diagnosis": {"vi": "Chưa có chẩn đoán hoặc bệnh đang điều trị.", "en": "No diagnosis or active disease has been recorded."},
    "qr.summary.total_cost": {"vi": "Tổng chi phí khám & thuốc", "en": "Total consultation & medication cost"},
    "qr.summary.status": {"vi": "Trạng thái", "en": "Status"},
    "qr.summary.paid": {"vi": "Đã thanh toán", "en": "Paid"},
    "qr.summary.unpaid": {"vi": "Chưa thanh toán", "en": "Unpaid"},
    "qr.summary.pay": {"vi": "💳  Thanh toán", "en": "💳  Process Payment"},
    "qr.summary.records": {"vi": "📅  Xem hồ sơ", "en": "📅  Go to Records"},

    # Patient table headers
    "th.id": {"vi": "Mã", "en": "ID"},
    "th.full_name": {"vi": "Họ tên", "en": "Full Name"},
    "th.dob": {"vi": "Ngày sinh", "en": "Date of Birth"},
    "th.age": {"vi": "Tuổi", "en": "Age"},
    "th.gender": {"vi": "Giới tính", "en": "Gender"},
    "th.phone": {"vi": "Điện thoại", "en": "Phone"},
    "th.email": {"vi": "Email", "en": "Email"},
    "th.blood_type": {"vi": "Nhóm máu", "en": "Blood Type"},

    # Appointments tab
    "appts.title": {"vi": "Lịch hẹn", "en": "Appointments"},
    "appts.schedule": {"vi": "➕  Đặt lịch", "en": "➕  Schedule"},
    "appts.queue": {"vi": "🎫  Lấy số", "en": "🎫  Get Ticket"},
    "appts.lab_order": {"vi": "🧪  Chỉ định XN", "en": "🧪  Lab Order"},
    "appts.prescribe": {"vi": "📝  Đơn thuốc & Hóa đơn", "en": "📝  Prescription & Bill"},
    "appts.payment": {"vi": "💳  Thanh toán", "en": "💳  Payment"},
    "appts.remove": {"vi": "🗑  Xóa", "en": "🗑  Remove"},
    "appts.th.id": {"vi": "Mã", "en": "ID"},
    "appts.th.patient": {"vi": "Bệnh nhân", "en": "Patient"},
    "appts.th.doctor": {"vi": "Bác sĩ", "en": "Doctor"},
    "appts.th.date": {"vi": "Ngày", "en": "Date"},
    "appts.th.time": {"vi": "Giờ", "en": "Time"},
    "appts.th.reason": {"vi": "Lý do", "en": "Reason"},
    "appts.th.status": {"vi": "Trạng thái", "en": "Status"},
    "appts.lab_ordered": {"vi": "✅ Đã chỉ định xét nghiệm", "en": "✅ Lab test ordered"},

    # Medications tab
    "meds.title": {"vi": "Thuốc & Dịch vụ", "en": "Medications & Services"},
    "meds.add": {"vi": "➕  Thêm", "en": "➕  Add"},
    "meds.edit": {"vi": "✏️  Sửa", "en": "✏️  Edit"},
    "meds.delete": {"vi": "🗑  Xóa", "en": "🗑  Delete"},
    "meds.search": {"vi": "🔍  Tìm thuốc/dịch vụ...", "en": "🔍  Search medications..."},
    "meds.th.id": {"vi": "Mã", "en": "ID"},
    "meds.th.name": {"vi": "Tên", "en": "Item Name"},
    "meds.th.price": {"vi": "Giá", "en": "Price"},
    "meds.th.desc": {"vi": "Mô tả", "en": "Description"},
    "meds.added": {"vi": "✅ Đã thêm thuốc/dịch vụ", "en": "✅ Medication added"},
    "meds.updated": {"vi": "✅ Đã cập nhật '{name}'", "en": "✅ Medication '{name}' updated"},
    "meds.deleted": {"vi": "🗑 Đã xóa thuốc/dịch vụ", "en": "🗑 Medication deleted"},
    "meds.confirm_delete": {"vi": "Xóa thuốc/dịch vụ {name}?", "en": "Delete medication {name}?"},
    "rx.ai_suggest": {"vi": "🤖 Gợi ý thuốc", "en": "🤖 Suggest meds"},
    "rx.ai_title": {"vi": "AI mini gợi ý thuốc", "en": "Mini AI Medication Suggestion"},
    "rx.ai_no_diagnosis": {"vi": "Chưa có bệnh/chẩn đoán để gợi ý thuốc.", "en": "No disease/diagnosis is available for medication suggestions."},
    "rx.ai_no_match": {"vi": "Chưa có thuốc phù hợp trong kho cho bệnh: {diag}", "en": "No matching stock medication was found for: {diag}"},
    "rx.ai_added": {"vi": "Đã gợi ý và thêm {n} thuốc/dịch vụ.\nBác sĩ cần kiểm tra lại trước khi lưu hóa đơn.", "en": "Added {n} suggested medication/service item(s).\nThe doctor must review before saving the bill."},

    # Statistics tab
    "stats.title": {"vi": "Thống kê & Tổng quan", "en": "Statistics & Overview"},
    "stats.total_patients": {"vi": "Tổng bệnh nhân", "en": "Total Patients"},
    "stats.avg_age": {"vi": "Tuổi trung bình", "en": "Average Age"},
    "stats.appointments": {"vi": "Lịch hẹn", "en": "Appointments"},
    "stats.male": {"vi": "Nam", "en": "Male Patients"},
    "stats.female": {"vi": "Nữ", "en": "Female Patients"},
    "stats.blood_dist": {"vi": "Phân bố nhóm máu", "en": "Blood Type Distribution"},
    "stats.appt_status": {"vi": "Trạng thái lịch hẹn", "en": "Appointment Status"},
    "stats.no_data": {"vi": "Chưa có dữ liệu", "en": "No data yet"},

    # Reports / admin tab
    "reports.title": {"vi": "📊  BÁO CÁO & HÀNH TRÌNH KHÁM", "en": "📊  REPORTS & CLINICAL JOURNEY"},
    "reports.bills": {"vi": "Hóa đơn đã thanh toán", "en": "Paid Bills"},
    "reports.reprint": {"vi": "🖨 In lại hóa đơn", "en": "🖨 Reprint Bill"},
    "reports.patient_list": {"vi": "👥 DANH SÁCH BỆNH NHÂN", "en": "👥 PATIENT LIST"},
    "reports.profile": {"vi": "👤 HỒ SƠ BỆNH NHÂN", "en": "👤 PATIENT PROFILE"},
    "reports.search_patient": {"vi": "🔍 Tìm bệnh nhân...", "en": "🔍 Search patients..."},
    "reports.select_hint": {
        "vi": "Chọn một bệnh nhân từ danh sách bên trái để xem lộ trình khám.",
        "en": "Select a patient from the list on the left to view their clinical journey.",
    },
    "prof.name": {"vi": "Họ tên: --", "en": "Full name: --"},
    "prof.dob": {"vi": "Ngày sinh: --", "en": "Date of birth: --"},
    "prof.gender": {"vi": "Giới tính: --", "en": "Gender: --"},
    "prof.phone": {"vi": "Số điện thoại: --", "en": "Phone: --"},
    "prof.blood": {"vi": "Nhóm máu: --", "en": "Blood type: --"},
    "prof.allergies": {"vi": "Dị ứng: --", "en": "Allergies: --"},
    "prof.name_val": {"vi": "<b>Họ tên:</b> {name}", "en": "<b>Full name:</b> {name}"},
    "prof.dob_val": {"vi": "<b>Ngày sinh:</b> {dob} ({age} tuổi)", "en": "<b>Date of birth:</b> {dob} ({age} yrs)"},
    "prof.gender_val": {"vi": "<b>Giới tính:</b> {gender}", "en": "<b>Gender:</b> {gender}"},
    "prof.phone_val": {"vi": "<b>Số điện thoại:</b> {phone}", "en": "<b>Phone:</b> {phone}"},
    "prof.blood_val": {"vi": "<b>Nhóm máu:</b> <span style='color: {c}; font-weight: bold;'>{bt}</span>", "en": "<b>Blood type:</b> <span style='color: {c}; font-weight: bold;'>{bt}</span>"},
    "prof.blood_unknown": {"vi": "Chưa xác định", "en": "Unknown"},
    "prof.allergies_val": {"vi": "<b>Dị ứng:</b> <span style='color: {c}; font-weight: bold;'>{a}</span>", "en": "<b>Allergies:</b> <span style='color: {c}; font-weight: bold;'>{a}</span>"},
    "prof.allergies_none": {"vi": "Không", "en": "None"},

    # Laboratory tab
    "lab.title": {"vi": "Phòng Xét nghiệm", "en": "Clinical Laboratory"},
    "lab.add": {"vi": "➕ Chỉ định Xét nghiệm", "en": "➕ New Lab Order"},
    "lab.search": {"vi": "Tìm theo bệnh nhân, bác sĩ hoặc tên xét nghiệm...", "en": "Search by patient, doctor or test name..."},
    "lab.update": {"vi": "✏️ Cập nhật & Tải kết quả", "en": "✏️ Update & Upload Result"},
    "lab.delete": {"vi": "🗑 Xóa chỉ định", "en": "🗑 Delete Order"},
    "lab.th.id": {"vi": "Mã XN", "en": "ID"},
    "lab.th.patient": {"vi": "Bệnh nhân", "en": "Patient"},
    "lab.th.doctor": {"vi": "Bác sĩ", "en": "Doctor"},
    "lab.th.test": {"vi": "Tên XN", "en": "Test Name"},
    "lab.th.cost": {"vi": "Chi phí (VNĐ)", "en": "Cost (VND)"},
    "lab.th.status": {"vi": "Trạng thái", "en": "Status"},
    "lab.th.date": {"vi": "Ngày", "en": "Date"},
    "lab.status.all": {"vi": "Tất cả trạng thái", "en": "All Statuses"},
    "lab.status.pending": {"vi": "Chờ xử lý", "en": "Pending"},
    "lab.status.processing": {"vi": "Đang xử lý", "en": "Processing"},
    "lab.status.completed": {"vi": "Hoàn thành", "en": "Completed"},
    "lab.err.select_update": {"vi": "Vui lòng chọn một hàng để cập nhật.", "en": "Please select a row to update."},
    "lab.err.select_delete": {"vi": "Vui lòng chọn chỉ định để xóa.", "en": "Please select an order to delete."},
    "lab.confirm_delete": {"vi": "Xóa chỉ định xét nghiệm '{name}'?", "en": "Delete lab order '{name}'?"},
    "lab.confirm_delete_title": {"vi": "Xác nhận xóa", "en": "Confirm Delete"},
    "lab.payment": {"vi": "💳 Thanh toán XN", "en": "💳 Lab Payment"},
    "lab.err.select_payment": {"vi": "Vui lòng chọn một chỉ định để thanh toán.", "en": "Please select a lab order to pay."},
    "lab.err.no_orders": {"vi": "Lịch hẹn này chưa có chỉ định xét nghiệm.", "en": "This appointment has no lab orders."},
    "lab.err.already_paid": {"vi": "Lịch hẹn này đã thanh toán.", "en": "This appointment is already paid."},
    "lab.payment_done": {"vi": "✅ Đã thanh toán — đang xử lý mẫu", "en": "✅ Paid — sample processing"},
    "lab.status_completed": {"vi": "✅ Hoàn thành xét nghiệm", "en": "✅ Lab test completed"},
    "lab.processing_done": {"vi": "✅ Đã xóa chỉ định khỏi danh sách", "en": "✅ Lab order removed from list"},

    # Lab dialogs
    "lab.dlg.create_title": {"vi": "Chỉ định Xét nghiệm", "en": "New Lab Order"},
    "lab.dlg.create_hdr": {"vi": "➕  Chỉ định phiếu xét nghiệm mới", "en": "➕  New Lab Test Order"},
    "lab.dlg.appt": {"vi": "Bệnh nhân & Lịch hẹn:", "en": "Patient & Appointment:"},
    "lab.dlg.preset": {"vi": "Mẫu xét nghiệm:", "en": "Test preset:"},
    "lab.dlg.name": {"vi": "Tên xét nghiệm:", "en": "Test name:"},
    "lab.dlg.price": {"vi": "Chi phí (VNĐ):", "en": "Cost (VND):"},
    "lab.dlg.name_ph": {"vi": "Nhập tên xét nghiệm...", "en": "Enter test name..."},
    "lab.dlg.cancel": {"vi": "Hủy bỏ", "en": "Cancel"},
    "lab.dlg.save": {"vi": "💾 Chỉ định", "en": "💾 Order"},
    "lab.dlg.no_appt": {"vi": "(Chưa có lịch hẹn — tạo lịch hẹn trước)", "en": "(No appointments — schedule one first)"},
    "lab.dlg.preset_placeholder": {"vi": "--- Chọn dịch vụ xét nghiệm ---", "en": "--- Select a test service ---"},
    "lab.preset.blood_panel": {"vi": "Xét nghiệm máu tổng quát - 200,000 VNĐ", "en": "Blood Panel - 200,000 VND"},
    "lab.preset.blood": {"vi": "Xét nghiệm máu - 200,000 VNĐ", "en": "Blood Test - 200,000 VND"},
    "lab.preset.xray": {"vi": "Chụp X-quang - 350,000 VNĐ", "en": "X-Ray Scan - 350,000 VND"},
    "lab.preset.mri": {"vi": "MRI - 1,500,000 VNĐ", "en": "MRI Scan - 1,500,000 VND"},
    "lab.preset.ultrasound": {"vi": "Siêu âm tổng quát - 300,000 VNĐ", "en": "Ultrasound - 300,000 VND"},
    "lab.preset.urine": {"vi": "Xét nghiệm nước tiểu - 150,000 VNĐ", "en": "Urine Test - 150,000 VND"},
    "lab.preset.custom": {"vi": "Dịch vụ khác (tùy chỉnh)...", "en": "Other (custom)..."},
    "lab.name.blood_panel": {"vi": "Xét nghiệm máu tổng quát (Blood Panel)", "en": "Blood Panel"},
    "lab.name.blood": {"vi": "Xét nghiệm máu (Blood Test)", "en": "Blood Test"},
    "lab.name.xray": {"vi": "Chụp X-quang (X-Ray Scan)", "en": "X-Ray Scan"},
    "lab.name.mri": {"vi": "Chụp Cộng hưởng từ (MRI Scan)", "en": "MRI Scan"},
    "lab.name.ultrasound": {"vi": "Siêu âm tổng quát (Ultrasound)", "en": "Ultrasound"},
    "lab.name.urine": {"vi": "Xét nghiệm nước tiểu (Urine Test)", "en": "Urine Test"},
    "lab.err.select_appt": {"vi": "Vui lòng chọn bệnh nhân / lịch hẹn.", "en": "Please select a patient / appointment."},
    "lab.err.name": {"vi": "Tên xét nghiệm không được để trống.", "en": "Test name is required."},
    "lab.err.price": {"vi": "Chi phí phải là số hợp lệ.", "en": "Cost must be a valid number."},
    "lab.success.created": {"vi": "Đã thêm chỉ định '{name}' thành công!", "en": "Lab order '{name}' created successfully!"},
    "lab.dlg.update_title": {"vi": "Cập nhật kết quả XN - LAB-{id:04d}", "en": "Update Lab Result - LAB-{id:04d}"},
    "lab.dlg.update_hdr": {"vi": "🧪  Kết quả XN: LAB-{id:04d}", "en": "🧪  Lab Result: LAB-{id:04d}"},
    "lab.dlg.patient": {"vi": "Bệnh nhân:", "en": "Patient:"},
    "lab.dlg.doctor": {"vi": "Bác sĩ:", "en": "Doctor:"},
    "lab.dlg.status_lbl": {"vi": "Trạng thái:", "en": "Status:"},
    "lab.dlg.file": {"vi": "Tài liệu kết quả (PDF/Ảnh):", "en": "Result file (PDF/Image):"},
    "lab.dlg.browse": {"vi": "📂 Chọn tệp", "en": "📂 Browse"},
    "lab.dlg.view": {"vi": "👁 Xem kết quả", "en": "👁 View Result"},
    "lab.dlg.save_result": {"vi": "💾 Lưu", "en": "💾 Save"},
    "lab.success.updated": {"vi": "Đã cập nhật trạng thái xét nghiệm!", "en": "Lab test updated successfully!"},

    # Common messages
    "msg.error": {"vi": "Lỗi", "en": "Error"},
    "msg.success": {"vi": "Thành công", "en": "Success"},
    "msg.confirm": {"vi": "Xác nhận", "en": "Confirm"},
    "msg.logout_title": {"vi": "Đăng xuất", "en": "Log Out"},
    "msg.logout_body": {"vi": "Bạn có muốn đăng xuất không?", "en": "Do you want to log out?"},
    "msg.confirm_delete": {"vi": "Xác nhận xóa", "en": "Confirm Delete"},
    "msg.delete_patient": {
        "vi": "Xóa bệnh nhân <b>{name}</b>?<br>Điều này cũng xóa tất cả lịch hẹn liên quan.",
        "en": "Delete patient <b>{name}</b>?<br>This will also remove all related appointments.",
    },
    "msg.patient_deleted": {"vi": "🗑  Đã xóa bệnh nhân", "en": "🗑  Patient deleted"},
    "msg.no_prescription": {
        "vi": "Chưa có đơn thuốc. Vui lòng tạo Đơn thuốc & Hóa đơn trước!",
        "en": "No prescription found. Please create a Prescription & Bill first!",
    },
    "msg.no_prescription_title": {"vi": "Chưa có đơn thuốc", "en": "No Prescription Found"},

    # Login (shared)
    "login.title": {"vi": "Đăng nhập", "en": "Sign In"},
    "login.subtitle": {"vi": "Hệ thống Quản lý Bệnh viện", "en": "Hospital Management System"},
    "login.username": {"vi": "Tên đăng nhập", "en": "Username"},
    "login.password": {"vi": "Mật khẩu", "en": "Password"},
    "login.remember": {"vi": "Ghi nhớ đăng nhập", "en": "Remember me"},
    "login.submit": {"vi": "Đăng nhập", "en": "Sign In"},
    "login.invalid": {"vi": "Sai tên đăng nhập hoặc mật khẩu.", "en": "Invalid username or password."},
    "login.username_lbl": {"vi": "TÊN ĐĂNG NHẬP", "en": "USERNAME"},
    "login.password_lbl": {"vi": "MẬT KHẨU", "en": "PASSWORD"},
    "login.hint": {
        "vi": "Tài khoản mặc định: <b>admin</b> / <b>admin123</b>",
        "en": "Default account: <b>admin</b> / <b>admin123</b>",
    },
    "login.checking": {"vi": "Đang kiểm tra…", "en": "Checking…"},
    "login.success": {"vi": "✅  Thành công!", "en": "✅  Success!"},
    "login.feature.patients": {"vi": "Quản lý hồ sơ bệnh nhân", "en": "Patient record management"},
    "login.feature.appts": {"vi": "Lịch hẹn & Thanh toán", "en": "Appointments & billing"},
    "login.feature.stats": {"vi": "Thống kê & Báo cáo", "en": "Statistics & reports"},
}


def load_language() -> str:
    global _lang
    raw = QSettings(ORG, APP).value("language", "vi")
    _lang = raw if raw in SUPPORTED else "vi"
    return _lang


def get_language() -> str:
    return _lang


def set_language(lang: str) -> None:
    global _lang
    _lang = lang if lang in SUPPORTED else "vi"
    QSettings(ORG, APP).setValue("language", _lang)


def tr(key: str, lang: str | None = None, **fmt) -> str:
    lang = lang or _lang
    entry = TEXTS.get(key, {})
    text = entry.get(lang) or entry.get("en") or key
    if fmt:
        try:
            return text.format(**fmt)
        except (KeyError, ValueError):
            return text
    return text


def lang_label(lang: str | None = None) -> str:
    """Button label for switching to the other language."""
    lang = lang or _lang
    return tr("btn.language_en" if lang == "vi" else "btn.language_vi", lang)
