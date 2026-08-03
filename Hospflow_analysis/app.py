import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import db, Hospital, Bed, Doctor, Appointment, LabTest, TestBooking, Report, OxygenCylinder

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'hospflow.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-this-in-production")

db.init_app(app)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- Home ----------
@app.route("/")
def home():
    hospitals = Hospital.query.all()
    total_beds_available = sum(b.available for h in hospitals for b in h.beds)
    total_oxygen_available = sum(h.oxygen.available for h in hospitals if h.oxygen)
    return render_template(
        "index.html",
        hospitals=hospitals,
        total_hospitals=len(hospitals),
        total_beds_available=total_beds_available,
        total_oxygen_available=total_oxygen_available,
    )


# ---------- Live Bed Tracking ----------
@app.route("/beds")
def beds():
    hospitals = Hospital.query.all()
    filter_type = request.args.get("type", "")
    return render_template("beds.html", hospitals=hospitals, filter_type=filter_type)


@app.route("/beds/update/<int:bed_id>", methods=["POST"])
def update_bed(bed_id):
    bed = Bed.query.get_or_404(bed_id)
    available = request.form.get("available", type=int)
    if available is not None and 0 <= available <= bed.total:
        bed.available = available
        db.session.commit()
        flash(f"{bed.bed_type} bed availability updated.", "success")
    return redirect(url_for("hospital_dashboard", hospital_id=bed.hospital_id))


# ---------- Oxygen Tracking ----------
@app.route("/oxygen")
def oxygen():
    hospitals = Hospital.query.all()
    return render_template("oxygen.html", hospitals=hospitals)


@app.route("/oxygen/update/<int:hospital_id>", methods=["POST"])
def update_oxygen(hospital_id):
    o = OxygenCylinder.query.filter_by(hospital_id=hospital_id).first_or_404()
    available = request.form.get("available", type=int)
    if available is not None and 0 <= available <= o.total:
        o.available = available
        db.session.commit()
        flash("Oxygen cylinder availability updated.", "success")
    return redirect(url_for("hospital_dashboard", hospital_id=hospital_id))


# ---------- Doctors & Appointments ----------
@app.route("/doctors")
def doctors():
    specialization = request.args.get("specialization", "")
    hospital_id = request.args.get("hospital_id", type=int)
    query = Doctor.query
    if specialization:
        query = query.filter(Doctor.specialization == specialization)
    if hospital_id:
        query = query.filter(Doctor.hospital_id == hospital_id)
    all_specializations = sorted({d.specialization for d in Doctor.query.all()})
    return render_template(
        "doctors.html",
        doctors=query.all(),
        hospitals=Hospital.query.all(),
        specializations=all_specializations,
        selected_specialization=specialization,
        selected_hospital=hospital_id,
    )


@app.route("/appointments/book/<int:doctor_id>", methods=["GET", "POST"])
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    if request.method == "POST":
        appt = Appointment(
            patient_name=request.form["patient_name"],
            patient_contact=request.form.get("patient_contact"),
            doctor_id=doctor.id,
            date=request.form["date"],
            time_slot=request.form["time_slot"],
            status="Pending",
        )
        db.session.add(appt)
        db.session.commit()
        flash(f"Appointment requested with {doctor.name} on {appt.date} at {appt.time_slot}.", "success")
        return redirect(url_for("my_appointments"))
    time_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
    return render_template("book_appointment.html", doctor=doctor, time_slots=time_slots)


@app.route("/appointments")
def my_appointments():
    appointments = Appointment.query.order_by(Appointment.created_at.desc()).all()
    return render_template("appointments.html", appointments=appointments)


@app.route("/appointments/status/<int:appt_id>", methods=["POST"])
def update_appointment_status(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    status = request.form.get("status")
    if status in ("Pending", "Confirmed", "Cancelled"):
        appt.status = status
        db.session.commit()
        flash("Appointment status updated.", "success")
    return redirect(url_for("my_appointments"))


# ---------- Medical Tests ----------
@app.route("/tests")
def tests():
    lab_tests = LabTest.query.all()
    return render_template("tests.html", tests=lab_tests, hospitals=Hospital.query.all())


@app.route("/tests/book/<int:test_id>", methods=["GET", "POST"])
def book_test(test_id):
    test = LabTest.query.get_or_404(test_id)
    hospitals = Hospital.query.all()
    if request.method == "POST":
        filename = None
        file = request.files.get("prescription")
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"{request.form['patient_name']}_{file.filename}")
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        booking = TestBooking(
            patient_name=request.form["patient_name"],
            test_id=test.id,
            hospital_id=request.form["hospital_id"],
            date=request.form["date"],
            prescription_filename=filename,
            status="Booked",
        )
        db.session.add(booking)
        db.session.commit()
        flash(f"{test.name} booked successfully.", "success")
        return redirect(url_for("tests"))
    return render_template("book_test.html", test=test, hospitals=hospitals)


# ---------- Reports ----------
@app.route("/reports", methods=["GET", "POST"])
def reports():
    if request.method == "POST":
        file = request.files.get("report_file")
        filename = None
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(f"{request.form['patient_name']}_{file.filename}")
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            flash("Please upload a valid PDF/PNG/JPG file.", "error")
            return redirect(url_for("reports"))
        report = Report(
            patient_name=request.form["patient_name"],
            filename=filename,
            shared_with_doctor=request.form.get("shared_with_doctor") or None,
        )
        db.session.add(report)
        db.session.commit()
        flash("Report uploaded successfully.", "success")
        return redirect(url_for("reports"))
    all_reports = Report.query.order_by(Report.upload_date.desc()).all()
    return render_template("reports.html", reports=all_reports)


# ---------- Hospital Info / Dashboard ----------
@app.route("/hospitals")
def hospitals():
    return render_template("hospitals.html", hospitals=Hospital.query.all())


@app.route("/hospitals/<int:hospital_id>")
def hospital_dashboard(hospital_id):
    hospital = Hospital.query.get_or_404(hospital_id)
    return render_template("hospital_dashboard.html", hospital=hospital)


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
