"""
Populates the database with dummy data so HospFlow is demoable out of the box.
Run with: python seed.py
Replace this with real data collection (hospital onboarding forms, CSV import,
admin dashboard entries, etc.) when moving to production.
"""
import random
from faker import Faker
from app import app
from models import db, Hospital, Bed, Doctor, Appointment, LabTest, TestBooking, Report, OxygenCylinder

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

INDIAN_CITIES = [
    "Jammu", "Srinagar", "Delhi", "Mumbai", "Bengaluru", "Chennai",
    "Hyderabad", "Pune", "Kolkata", "Ahmedabad", "Lucknow", "Chandigarh",
    "Jaipur", "Amritsar", "Ludhiana",
]

BED_TYPES = ["ICU", "Oxygen", "General", "Emergency"]
SPECIALIZATIONS = [
    "General Physician", "Cardiologist", "Orthopedic", "Pediatrician",
    "Neurologist", "Gynecologist", "Dermatologist", "ENT Specialist",
]
LAB_TESTS = [
    ("Complete Blood Count (CBC)", 300),
    ("Blood Sugar (Fasting)", 150),
    ("Lipid Profile", 600),
    ("Liver Function Test", 700),
    ("Kidney Function Test", 650),
    ("Thyroid Profile (T3 T4 TSH)", 550),
    ("COVID-19 RT-PCR", 800),
    ("X-Ray Chest", 400),
    ("MRI Scan", 4500),
    ("ECG", 250),
]
TIME_SLOTS = ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM"]
STATUSES = ["Pending", "Confirmed", "Cancelled"]


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Lab tests (shared catalog)
        tests = []
        for name, price in LAB_TESTS:
            t = LabTest(name=name, price=price)
            db.session.add(t)
            tests.append(t)
        db.session.commit()

        hospitals = []
        used_cities = random.sample(INDIAN_CITIES, k=8)
        for city in used_cities:
            h = Hospital(
                name=f"{city} {random.choice(['General Hospital', 'Multispeciality Hospital', 'Medical Center', 'City Hospital'])}",
                location=city,
                contact="9" + str(random.randint(100000000, 999999999)),
            )
            db.session.add(h)
            hospitals.append(h)
        db.session.commit()

        doctors = []
        for h in hospitals:
            # Beds
            for bed_type in BED_TYPES:
                total = random.randint(10, 60)
                available = random.randint(0, total)
                db.session.add(Bed(hospital_id=h.id, bed_type=bed_type, total=total, available=available))

            # Oxygen cylinders
            o_total = random.randint(20, 100)
            db.session.add(OxygenCylinder(hospital_id=h.id, total=o_total, available=random.randint(0, o_total)))

            # Doctors
            for _ in range(random.randint(3, 6)):
                d = Doctor(name=f"Dr. {fake.name()}", specialization=random.choice(SPECIALIZATIONS), hospital_id=h.id)
                db.session.add(d)
                doctors.append(d)
        db.session.commit()

        # Appointments
        for _ in range(25):
            d = random.choice(doctors)
            db.session.add(Appointment(
                patient_name=fake.name(),
                patient_contact="9" + str(random.randint(100000000, 999999999)),
                doctor_id=d.id,
                date=fake.date_between(start_date="-10d", end_date="+20d").isoformat(),
                time_slot=random.choice(TIME_SLOTS),
                status=random.choice(STATUSES),
            ))

        # Test bookings
        for _ in range(15):
            t = random.choice(tests)
            h = random.choice(hospitals)
            db.session.add(TestBooking(
                patient_name=fake.name(),
                test_id=t.id,
                hospital_id=h.id,
                date=fake.date_between(start_date="-5d", end_date="+15d").isoformat(),
                prescription_filename=None,
                status=random.choice(["Booked", "Completed", "Cancelled"]),
            ))

        # Reports
        for _ in range(10):
            db.session.add(Report(
                patient_name=fake.name(),
                filename=f"{fake.word()}_report.pdf",
                shared_with_doctor=random.choice([None, f"Dr. {fake.last_name()}"]),
            ))

        db.session.commit()
        print("Dummy data seeded successfully.")
        print(f"Hospitals: {len(hospitals)}, Doctors: {len(doctors)}, Tests: {len(tests)}")


if __name__ == "__main__":
    seed()
