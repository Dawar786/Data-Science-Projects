from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    beds = db.relationship("Bed", backref="hospital", cascade="all, delete-orphan")
    doctors = db.relationship("Doctor", backref="hospital", cascade="all, delete-orphan")
    oxygen = db.relationship("OxygenCylinder", backref="hospital", uselist=False, cascade="all, delete-orphan")


class Bed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    bed_type = db.Column(db.String(20), nullable=False)  # ICU, Oxygen, General, Emergency
    total = db.Column(db.Integer, nullable=False, default=0)
    available = db.Column(db.Integer, nullable=False, default=0)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(80), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    appointments = db.relationship("Appointment", backref="doctor", cascade="all, delete-orphan")


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(120), nullable=False)
    patient_contact = db.Column(db.String(20))
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="Pending")  # Pending, Confirmed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LabTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    bookings = db.relationship("TestBooking", backref="test", cascade="all, delete-orphan")


class TestBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(120), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey("lab_test.id"), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    prescription_filename = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Booked")
    hospital = db.relationship("Hospital")


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(120), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    shared_with_doctor = db.Column(db.String(120))


class OxygenCylinder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospital.id"), nullable=False)
    total = db.Column(db.Integer, nullable=False, default=0)
    available = db.Column(db.Integer, nullable=False, default=0)
