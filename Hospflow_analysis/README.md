# HospFlow

Smart healthcare management platform — live hospital bed tracking, doctor
appointment booking, medical test booking, report uploads, hospital
dashboards, and oxygen cylinder availability tracking.

## Tech Stack
- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite (file-based, zero setup — swap for PostgreSQL/MySQL later by changing `SQLALCHEMY_DATABASE_URI` in `app.py`)
- **Frontend:** Jinja2 templates + plain CSS (no build step needed)
- **Dummy data:** generated with `Faker`

## Project Structure
```
hospflow/
├── app.py              # Flask app & all routes
├── models.py            # Database models (SQLAlchemy)
├── seed.py               # Populates dummy data — RUN THIS FIRST
├── requirements.txt
├── static/style.css
├── templates/            # All HTML pages
├── uploads/               # Uploaded reports & prescriptions land here
└── instance/hospflow.db  # SQLite DB (auto-created)
```

## Setup

```bash
cd hospflow
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                # creates tables + fills dummy data
python app.py
```

Open **http://127.0.0.1:5000**

## Where to plug in your real dataset

Right now `seed.py` fills the database with realistic-looking fake data
(hospitals, doctors, beds, appointments, tests, reports) using `Faker`, so
the whole app is demoable immediately. To move to real data:

1. **Hospitals & beds** — replace the loop in `seed.py` that creates
   `Hospital`/`Bed`/`OxygenCylinder` rows with a CSV/JSON import of your
   actual hospital list (name, location, contact, bed counts per type).
2. **Doctors** — same pattern: import a real doctor roster instead of the
   `fake.name()` calls.
3. **Lab tests** — `LAB_TESTS` in `seed.py` is a plain list of
   `(name, price)` tuples — swap in your real test catalog.
4. Once you have a real source, either:
   - write a one-off `import_csv.py` that reads your file and calls
     `db.session.add(...)` the same way `seed.py` does, or
   - build an admin form (the `hospital_dashboard.html` page is a good
     starting point) so hospitals can self-register instead of seeding.

Uploaded reports/prescriptions go to `uploads/` — filenames are stored in
the `Report` and `TestBooking` tables.

## Feature → Route Map
| Feature | Route |
|---|---|
| Live bed tracking | `/beds` |
| Hospital dashboard (update beds/oxygen) | `/hospitals/<id>` |
| Doctor search & booking | `/doctors`, `/appointments/book/<doctor_id>` |
| Appointments list | `/appointments` |
| Medical test booking | `/tests`, `/tests/book/<test_id>` |
| Report upload | `/reports` |
| Oxygen tracking | `/oxygen` |
| Hospital directory | `/hospitals` |

## Next steps for production
- Add authentication (patients vs hospital-admin roles)
- Move file uploads to cloud storage (S3 etc.) instead of local `uploads/`
- Switch SQLite → PostgreSQL for concurrent writes
- Add form validation + CSRF protection (Flask-WTF)
